from amsdal_models.classes.model import Model
from amsdal_utils.models.enums import ModuleType
from typing import ClassVar

class Permission(Model):
    __module_type__: ClassVar[ModuleType] = ...
    model: str = ...
    action: str = ...
    @property
    def display_name(self) -> str:
        """
        Returns the display name of the user.

        This method returns a formatted string combining the model and action of the user.

        Returns:
            str: The formatted display name in the format 'model:action'.
        """
