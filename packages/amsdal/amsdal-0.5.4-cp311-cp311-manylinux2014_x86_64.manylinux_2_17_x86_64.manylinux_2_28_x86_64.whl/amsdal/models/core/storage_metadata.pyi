from amsdal_models.classes.model import TypeModel
from amsdal_utils.models.enums import ModuleType
from typing import ClassVar

class StorageMetadata(TypeModel):
    __module_type__: ClassVar[ModuleType]
    table_name: str | None
    db_fields: dict[str, list[str]] | None
    primary_key: list[str] | None
    indexed: list[list[str]] | None
    unique: list[list[str]] | None
