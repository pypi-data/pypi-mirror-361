from amsdal.contrib.frontend_configs.models.frontend_config_skip_none_base import *
from amsdal_utils.models.enums import ModuleType
from typing import Any, ClassVar

class FrontendConfigControlAction(FrontendConfigSkipNoneBase):
    __module_type__: ClassVar[ModuleType]
    action: str
    text: str
    type: str
    dataLayerEvent: str | None
    activator: str | None
    icon: str | None
    @classmethod
    def validate_value_in_options_type(cls, value: Any) -> Any: ...
    @classmethod
    def validate_action(cls, v: str) -> str:
        """
        Validates the action string to ensure it is one of the allowed values.

        This method checks if the action string starts with 'navigate::' or is one of the predefined
        actions. If the action string is invalid, it raises a ValueError.

        Args:
            cls: The class this method is attached to.
            v (str): The action string to validate.

        Returns:
            str: The validated action string.

        Raises:
            ValueError: If the action string is not valid.
        """
