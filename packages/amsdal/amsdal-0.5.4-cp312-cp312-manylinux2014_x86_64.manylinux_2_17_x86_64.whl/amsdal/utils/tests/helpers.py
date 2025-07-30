import contextlib
import os
import random
import string
import tempfile
from collections.abc import AsyncGenerator
from collections.abc import AsyncIterator
from collections.abc import Generator
from collections.abc import Iterator
from contextlib import asynccontextmanager
from contextlib import contextmanager
from contextlib import suppress
from pathlib import Path
from typing import Any

import yaml
from amsdal_data.application import AsyncDataApplication
from amsdal_data.connections.historical.schema_version_manager import AsyncHistoricalSchemaVersionManager
from amsdal_data.connections.historical.schema_version_manager import HistoricalSchemaVersionManager
from amsdal_models.migration import migrations
from amsdal_models.migration.executors.default_executor import DefaultAsyncMigrationExecutor
from amsdal_models.migration.executors.default_executor import DefaultMigrationExecutor
from amsdal_models.migration.file_migration_executor import SimpleFileMigrationExecutorManager
from amsdal_models.migration.file_migration_generator import SimpleFileMigrationGenerator
from amsdal_models.migration.file_migration_writer import FileMigrationWriter
from amsdal_models.migration.migrations import MigrateData
from amsdal_models.migration.migrations import MigrationSchemas
from amsdal_models.migration.migrations_loader import MigrationsLoader
from amsdal_models.migration.utils import contrib_to_module_root_path
from amsdal_models.schemas.class_schema_loader import ClassSchemaLoader
from amsdal_utils.config.manager import AmsdalConfigManager
from amsdal_utils.models.enums import ModuleType

from amsdal.configs.constants import CORE_MIGRATIONS_PATH
from amsdal.configs.main import settings
from amsdal.manager import AmsdalManager
from amsdal.manager import AsyncAmsdalManager
from amsdal.utils.tests.enums import DbExecutionType
from amsdal.utils.tests.enums import LakehouseOption
from amsdal.utils.tests.enums import StateOption

TESTS_DIR = Path(os.getcwd())


def create_postgres_database(database: str) -> tuple[str, str, str, str]:
    import psycopg

    db_host = os.getenv('POSTGRES_HOST', 'localhost')
    db_port = os.getenv('POSTGRES_PORT', '5432')
    db_user = os.getenv('POSTGRES_USER', 'postgres')
    db_password = os.getenv('POSTGRES_PASSWORD', 'example')

    conn = psycopg.connect(
        host=db_host,
        port=db_port,
        user=db_user,
        password=db_password,
        autocommit=True,
    )
    cur = conn.cursor()

    with suppress(psycopg.errors.DuplicateDatabase):
        cur.execute(f'CREATE DATABASE "{database}"')

    cur.close()
    conn.close()

    return (
        db_host,
        db_port,
        db_user,
        db_password,
    )


@contextmanager
def override_settings(**kwargs: Any) -> Iterator[None]:
    """
    A context manager that temporarily overrides settings.

    This is a copy of django.test.utils.override_settings, but with the
    ability to override settings with None.
    """
    from amsdal.configs.main import settings

    original_settings = settings.model_dump()

    settings.override(**kwargs)

    try:
        yield
    finally:
        settings.override(**original_settings)


def _get_config_template(
    db_execution_type: DbExecutionType,
    lakehouse_option: LakehouseOption,
    state_option: StateOption,
    *,
    is_async: bool = False,
) -> str:
    config_object: dict[str, Any] = {
        'application_name': 'test_client_app',
        'async_mode': is_async,
        'connections': [
            {
                'name': 'lock',
                'backend': 'amsdal_data.lock.implementations.thread_lock.ThreadLock',
            },
        ],
        'resources_config': {
            'lakehouse': 'lakehouse',
            'lock': 'lock',
            'repository': {'default': 'state'},
        },
    }
    if lakehouse_option in [
        LakehouseOption.postgres,
        LakehouseOption.postgres_immutable,
    ]:
        config_object['connections'].append(
            {
                'name': 'lakehouse',
                'backend': 'postgres-historical-async' if is_async else 'postgres-historical',
                'credentials': [
                    {
                        'db_host': '{{ db_host }}',
                        'db_port': '{{ db_port }}',
                        'db_user': '{{ db_user }}',
                        'db_password': '{{ db_password }}',
                        'db_name': '{{ lakehouse_postgres_db }}',
                    }
                ],
            }
        )
    elif lakehouse_option in [LakehouseOption.sqlite, LakehouseOption.sqlite_immutable]:
        config_object['connections'].append(
            {
                'name': 'lakehouse',
                'backend': 'sqlite-historical-async' if is_async else 'sqlite-historical',
                'credentials': [{'db_path': '{{ db_dir }}/sqlite_lakehouse.sqlite3'}],
            }
        )

    if db_execution_type == DbExecutionType.lakehouse_only:
        config_object['resources_config']['repository']['default'] = 'lakehouse'

        return yaml.dump(config_object)

    if state_option == StateOption.postgres:
        config_object['connections'].append(
            {
                'name': 'state',
                'backend': 'postgres-async' if is_async else 'postgres',
                'credentials': [
                    {
                        'db_host': '{{ db_host }}',
                        'db_port': '{{ db_port }}',
                        'db_user': '{{ db_user }}',
                        'db_password': '{{ db_password }}',
                        'db_name': '{{ state_postgres_db }}',
                    }
                ],
            }
        )

    elif state_option == StateOption.sqlite:
        config_object['connections'].append(
            {
                'name': 'state',
                'backend': 'sqlite-async' if is_async else 'sqlite',
                'credentials': [{'db_path': '{{ db_dir }}/sqlite_state.sqlite3'}],
            }
        )

    return yaml.dump(config_object)


@contextmanager
def _init_manager(
    db_execution_type: DbExecutionType,
    lakehouse_option: LakehouseOption,
    state_option: StateOption,
    *,
    is_async: bool = False,
) -> Generator[tuple[Path, Path], Any, None]:
    Path('.tmp').mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory(dir='.tmp') as temp_dir:
        db_dir = Path(temp_dir) / 'db_dir'
        (db_dir / 'warehouse').mkdir(exist_ok=True, parents=True)

        lakehouse_database = ''.join(random.sample(string.ascii_letters, 16))
        state_database = ''.join(random.sample(string.ascii_letters, 16))
        config_text = _get_config_template(db_execution_type, lakehouse_option, state_option, is_async=is_async)

        if lakehouse_option in [
            LakehouseOption.postgres,
            LakehouseOption.postgres_immutable,
        ]:
            (
                db_host,
                db_port,
                db_user,
                db_password,
            ) = create_postgres_database(lakehouse_database)

            config_text = (
                config_text.replace('{{ db_host }}', db_host)
                .replace('{{ db_port }}', db_port)
                .replace('{{ db_user }}', db_user)
                .replace('{{ db_password }}', db_password)
                .replace('{{ lakehouse_postgres_db }}', lakehouse_database)
            )
        elif lakehouse_option in [
            LakehouseOption.sqlite,
            LakehouseOption.sqlite_immutable,
        ]:
            config_text = config_text.replace('{{ db_dir }}', db_dir.absolute().as_posix())

        if state_option == StateOption.postgres:
            create_postgres_database(state_database)
            config_text = (
                config_text.replace('{{ db_host }}', db_host)
                .replace('{{ db_port }}', db_port)
                .replace('{{ db_user }}', db_user)
                .replace('{{ db_password }}', db_password)
                .replace('{{ state_postgres_db }}', state_database)
            )
        elif state_option == StateOption.sqlite:
            config_text = config_text.replace('{{ db_dir }}', db_dir.absolute().as_posix())

        config_path = Path(temp_dir) / 'config.yml'
        config_path.write_text(config_text)

        yield db_dir, config_path


@contextmanager
def init_manager(
    src_dir_path: Path,
    db_execution_type: DbExecutionType,
    lakehouse_option: LakehouseOption,
    state_option: StateOption,
) -> Generator[AmsdalManager, Any, None]:
    with _init_manager(db_execution_type, lakehouse_option, state_option) as (
        db_dir,
        config_path,
    ):
        with override_settings(
            APP_PATH=db_dir,
            CONFIG_PATH=config_path,
            USER_MODELS_MODULE_PATH=src_dir_path / 'models',
            TRANSACTIONS_MODULE_PATH=src_dir_path / 'transactions',
            FIXTURES_MODULE_PATH=src_dir_path / 'fixtures',
        ):
            config_manager = AmsdalConfigManager()
            config_manager.load_config(config_path)
            manager = AmsdalManager()
            manager.setup()
            manager.post_setup()  # type: ignore[call-arg]

            try:
                yield manager
            finally:
                manager.teardown()
                AmsdalManager.invalidate()
                AmsdalConfigManager.invalidate()


@asynccontextmanager
async def async_init_manager(
    src_dir_path: Path,
    db_execution_type: DbExecutionType,
    lakehouse_option: LakehouseOption,
    state_option: StateOption,
) -> AsyncIterator[AsyncAmsdalManager]:
    with _init_manager(db_execution_type, lakehouse_option, state_option, is_async=True) as (db_dir, config_path):
        with override_settings(
            APP_PATH=db_dir,
            CONFIG_PATH=config_path,
            USER_MODELS_MODULE_PATH=src_dir_path / 'models',
            TRANSACTIONS_MODULE_PATH=src_dir_path / 'transactions',
            FIXTURES_MODULE_PATH=src_dir_path / 'fixtures',
        ):
            config_manager = AmsdalConfigManager()
            config_manager.load_config(config_path)
            manager = AsyncAmsdalManager()
            await manager.setup()
            await manager.post_setup()  # type: ignore[call-arg,misc]

            try:
                yield manager
            finally:
                await manager.teardown()
                await AsyncDataApplication().teardown()
                AsyncAmsdalManager.invalidate()
                AmsdalConfigManager.invalidate()
                AsyncDataApplication.invalidate()


def migrate() -> None:
    schemas = MigrationSchemas()
    executor = DefaultMigrationExecutor(schemas, use_foreign_keys=True)

    with contextlib.suppress(Exception):
        HistoricalSchemaVersionManager().object_classes  # noqa: B018

    _migrate_per_loader(
        executor,
        MigrationsLoader(
            migrations_dir=CORE_MIGRATIONS_PATH,
            module_type=ModuleType.CORE,
        ),
    )

    for contrib in settings.CONTRIBS:
        contrib_root_path = contrib_to_module_root_path(contrib)
        _migrate_per_loader(
            executor,
            MigrationsLoader(
                migrations_dir=contrib_root_path / settings.MIGRATIONS_DIRECTORY_NAME,
                module_type=ModuleType.CONTRIB,
                module_name=contrib,
            ),
        )

    user_schema_loader = ClassSchemaLoader(
        settings.USER_MODELS_MODULE,
        class_filter=lambda cls: cls.__module_type__ == ModuleType.USER,
    )
    _schemas, _cycle_schemas = user_schema_loader.load_sorted()
    _schemas_map = {_schema.title: _schema for _schema in _schemas}

    for object_schema in _schemas:
        for _operation_data in SimpleFileMigrationGenerator.build_operations(
            ModuleType.USER,
            object_schema,
            None,
        ):
            _operation_name = FileMigrationWriter.operation_name_map[_operation_data.type]
            _operation = getattr(migrations, _operation_name)(
                module_type=ModuleType.USER,
                class_name=_operation_data.class_name,
                new_schema=_operation_data.new_schema.model_dump(),
            )

            _operation.forward(executor)

    for object_schema in _cycle_schemas:
        for _operation_data in SimpleFileMigrationGenerator.build_operations(
            ModuleType.USER,
            object_schema,
            _schemas_map[object_schema.title],
        ):
            _operation_name = FileMigrationWriter.operation_name_map[_operation_data.type]
            _operation = getattr(migrations, _operation_name)(
                module_type=ModuleType.USER,
                class_name=_operation_data.class_name,
                new_schema=_operation_data.new_schema.model_dump(),
            )

            _operation.forward(executor)

    executor.flush_buffer()


def _migrate_per_loader(executor: DefaultMigrationExecutor, loader: MigrationsLoader) -> None:
    for _migration in loader:
        migration_class = SimpleFileMigrationExecutorManager.get_migration_class(_migration)
        migration_class_instance = migration_class()

        for _operation in migration_class_instance.operations:
            if isinstance(_operation, MigrateData):
                executor.flush_buffer()

            _operation.forward(executor)

        executor.flush_buffer()


async def async_migrate() -> None:
    schemas = MigrationSchemas()
    executor = DefaultAsyncMigrationExecutor(schemas)

    with contextlib.suppress(Exception):
        await AsyncHistoricalSchemaVersionManager().object_classes

    await _async_migrate_per_loader(
        executor,
        MigrationsLoader(
            migrations_dir=CORE_MIGRATIONS_PATH,
            module_type=ModuleType.CORE,
        ),
    )

    for contrib in settings.CONTRIBS:
        contrib_root_path = contrib_to_module_root_path(contrib)
        await _async_migrate_per_loader(
            executor,
            MigrationsLoader(
                migrations_dir=contrib_root_path / settings.MIGRATIONS_DIRECTORY_NAME,
                module_type=ModuleType.CONTRIB,
                module_name=contrib,
            ),
        )

    user_schema_loader = ClassSchemaLoader(
        settings.USER_MODELS_MODULE,
        class_filter=lambda cls: cls.__module_type__ == ModuleType.USER,
    )
    _schemas, _cycle_schemas = user_schema_loader.load_sorted()
    _schemas_map = {_schema.title: _schema for _schema in _schemas}

    for object_schema in _schemas:
        for _operation_data in SimpleFileMigrationGenerator.build_operations(
            ModuleType.USER,
            object_schema,
            None,
        ):
            _operation_name = FileMigrationWriter.operation_name_map[_operation_data.type]
            _operation = getattr(migrations, _operation_name)(
                module_type=ModuleType.USER,
                class_name=_operation_data.class_name,
                new_schema=_operation_data.new_schema.model_dump(),
            )

            _operation.forward(executor)

    for object_schema in _cycle_schemas:
        for _operation_data in SimpleFileMigrationGenerator.build_operations(
            ModuleType.USER,
            object_schema,
            _schemas_map[object_schema.title],
        ):
            _operation_name = FileMigrationWriter.operation_name_map[_operation_data.type]
            _operation = getattr(migrations, _operation_name)(
                module_type=ModuleType.USER,
                class_name=_operation_data.class_name,
                new_schema=_operation_data.new_schema.model_dump(),
            )

            _operation.forward(executor)

    await executor.flush_buffer()


async def _async_migrate_per_loader(executor: DefaultAsyncMigrationExecutor, loader: MigrationsLoader) -> None:
    for _migration in loader:
        migration_class = SimpleFileMigrationExecutorManager.get_migration_class(_migration)
        migration_class_instance = migration_class()

        for _operation in migration_class_instance.operations:
            if isinstance(_operation, MigrateData):
                await executor.flush_buffer()

            _operation.forward(executor)

        await executor.flush_buffer()


@contextmanager
def init_manager_and_migrate(
    src_dir_path: Path,
    db_execution_type: DbExecutionType,
    lakehouse_option: LakehouseOption,
    state_option: StateOption,
) -> Generator[AmsdalManager, Any, None]:
    with init_manager(
        src_dir_path=src_dir_path,
        db_execution_type=db_execution_type,
        lakehouse_option=lakehouse_option,
        state_option=state_option,
    ) as manager:
        migrate()
        manager.authenticate()
        manager.init_classes()

        yield manager


@asynccontextmanager
async def async_init_manager_and_migrate(
    src_dir_path: Path,
    db_execution_type: DbExecutionType,
    lakehouse_option: LakehouseOption,
    state_option: StateOption,
) -> AsyncGenerator[AsyncAmsdalManager, Any]:
    async with async_init_manager(
        src_dir_path=src_dir_path,
        db_execution_type=db_execution_type,
        lakehouse_option=lakehouse_option,
        state_option=state_option,
    ) as manager:
        await async_migrate()
        manager.authenticate()
        manager.init_classes()

        yield manager
