from amsdal.contrib.frontend_configs.models.frontend_config_skip_none_base import *
from amsdal_utils.models.enums import ModuleType
from typing import Any, ClassVar

class FrontendConfigGroupValidator(FrontendConfigSkipNoneBase):
    __module_type__: ClassVar[ModuleType]
    mainControl: str | None
    dependentControls: list[str] | None
    condition: str | None
    @classmethod
    def validate_value_in_options_condition(cls, value: Any) -> Any: ...
