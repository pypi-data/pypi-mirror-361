from amsdal.contrib.frontend_configs.models.frontend_config_skip_none_base import *
from amsdal_utils.models.enums import ModuleType
from typing import ClassVar

class FrontendConfigSliderOption(FrontendConfigSkipNoneBase):
    __module_type__: ClassVar[ModuleType]
    min: float | None
    max: float | None
    range: bool | None
