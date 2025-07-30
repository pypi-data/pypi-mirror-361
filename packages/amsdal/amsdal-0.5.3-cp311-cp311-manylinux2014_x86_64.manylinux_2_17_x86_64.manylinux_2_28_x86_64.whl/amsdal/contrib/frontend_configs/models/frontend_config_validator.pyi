from amsdal.contrib.frontend_configs.models.frontend_config_group_validator import *
from amsdal_utils.models.enums import ModuleType
from typing import Any, ClassVar

class FrontendConfigValidator(FrontendConfigGroupValidator):
    __module_type__: ClassVar[ModuleType]
    mainControl: str | None
    dependentControls: list[str] | None
    condition: str | None
    function: str | None
    value: str | None
    @classmethod
    def validate_value_in_options_condition(cls, value: Any) -> Any: ...
    @classmethod
    def validate_value_in_options_function(cls, value: Any) -> Any: ...
