from amsdal.contrib.frontend_configs.models.frontend_config_skip_none_base import *
from amsdal_utils.models.enums import ModuleType
from typing import ClassVar

class FrontendConfigOption(FrontendConfigSkipNoneBase):
    __module_type__: ClassVar[ModuleType]
    label: str | None
    value: str | None
