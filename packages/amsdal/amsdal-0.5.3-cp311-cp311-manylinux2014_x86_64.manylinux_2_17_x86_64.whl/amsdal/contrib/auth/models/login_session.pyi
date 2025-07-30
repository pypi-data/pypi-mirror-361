from amsdal_models.classes.model import Model
from amsdal_utils.models.enums import ModuleType
from typing import Any, ClassVar

class LoginSession(Model):
    __module_type__: ClassVar[ModuleType] = ...
    email: str = ...
    password: str = ...
    token: str | None = ...
    @property
    def display_name(self) -> str:
        """
        Returns the display name of the user.

        This method returns the email of the user as their display name.

        Returns:
            str: The email of the user.
        """
    def pre_init(self, *, is_new_object: bool, kwargs: dict[str, Any]) -> None:
        """
        Pre-initializes a user object by validating email and password, and generating a JWT token.

        This method checks if the object is new and validates the provided email and password.
        If the email and password are valid, it generates a JWT token and adds it to the kwargs.

        Args:
            is_new_object (bool): Indicates if the object is new.
            kwargs (dict[str, Any]): The keyword arguments containing user details.

        Raises:
            AuthenticationError: If the email or password is invalid.
        """
    def pre_create(self) -> None: ...
    def pre_update(self) -> None: ...
    async def apre_create(self) -> None: ...
    async def apre_update(self) -> None: ...
