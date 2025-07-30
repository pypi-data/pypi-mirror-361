from amsdal.contrib.frontend_configs.models.frontend_config_group_validator import *
from amsdal_utils.models.enums import ModuleType
from typing import Any, ClassVar

class FrontendActivatorConfig(FrontendConfigGroupValidator):
    __module_type__: ClassVar[ModuleType]
    mainControl: str | None
    dependentControls: list[str] | None
    condition: str | None
    value: Any | None
    @classmethod
    def validate_value_in_options_condition(cls, value: Any) -> Any: ...
