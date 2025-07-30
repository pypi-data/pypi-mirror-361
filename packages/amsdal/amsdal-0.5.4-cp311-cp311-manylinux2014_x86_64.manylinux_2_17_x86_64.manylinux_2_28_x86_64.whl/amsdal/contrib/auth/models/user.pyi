from amsdal.contrib.auth.models.permission import *
from amsdal_models.classes.model import Model
from amsdal_utils.models.enums import ModuleType
from typing import Any, ClassVar

class User(Model):
    __module_type__: ClassVar[ModuleType] = ...
    email: str = ...
    password: bytes = ...
    permissions: list['Permission'] | None = ...
    def __repr__(self) -> str: ...
    def __str__(self) -> str: ...
    async def apre_update(self) -> None: ...
    @property
    def display_name(self) -> str:
        """
        Returns the display name of the user.

        This method returns the email of the user as their display name.

        Returns:
            str: The email of the user.
        """
    _object_id = ...
    def post_init(self, *, is_new_object: bool, kwargs: dict[str, Any]) -> None:
        """
        Post-initializes a user object by validating email and password, and hashing the password.

        This method checks if the email and password are provided and valid. If the object is new,
        it hashes the password and sets the object ID to the lowercased email.

        Args:
            is_new_object (bool): Indicates if the object is new.
            kwargs (dict[str, Any]): The keyword arguments containing user details.

        Raises:
            UserCreationError: If the email or password is invalid.
        """
    def pre_create(self) -> None:
        """
        Pre-creates a user object.

        This method is a placeholder for any pre-creation logic that needs to be executed
        before a user object is created.
        """
    def pre_update(self) -> None: ...
