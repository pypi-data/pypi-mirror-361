from amsdal.contrib.frontend_configs.models.frontend_activator_config import *
from amsdal.contrib.frontend_configs.models.frontend_config_async_validator import *
from amsdal.contrib.frontend_configs.models.frontend_config_control_action import *
from amsdal.contrib.frontend_configs.models.frontend_config_option import *
from amsdal.contrib.frontend_configs.models.frontend_config_skip_none_base import *
from amsdal.contrib.frontend_configs.models.frontend_config_slider_option import *
from amsdal.contrib.frontend_configs.models.frontend_config_text_mask import *
from amsdal.contrib.frontend_configs.models.frontend_config_validator import *
from amsdal_utils.models.enums import ModuleType
from typing import Any, ClassVar

class FrontendControlConfig(FrontendConfigSkipNoneBase):
    __module_type__: ClassVar[ModuleType]
    type: str
    name: str
    label: str | None
    required: bool | None
    hideLabel: bool | None
    actions: list['FrontendConfigControlAction'] | None
    validators: list['FrontendConfigValidator'] | None
    asyncValidators: list['FrontendConfigAsyncValidator'] | None
    activators: list['FrontendActivatorConfig'] | None
    additionalText: str | None
    value: Any | None
    placeholder: str | None
    options: list['FrontendConfigOption'] | None
    mask: FrontendConfigTextMask | None
    controls: list['FrontendControlConfig'] | None
    showSearch: bool | None
    sliderOptions: FrontendConfigSliderOption | None
    customLabel: list[str] | None
    control: FrontendControlConfig | None
    entityType: str | None
    @classmethod
    def validate_value_in_options_type(cls, value: Any) -> Any: ...
