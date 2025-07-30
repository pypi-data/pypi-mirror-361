from amsdal_models.classes.model import Model
from amsdal_utils.models.enums import ModuleType
from pathlib import Path
from typing import BinaryIO, ClassVar

class File(Model):
    __module_type__: ClassVar[ModuleType] = ...
    filename: str = ...
    data: bytes = ...
    size: float | None = ...
    def __repr__(self) -> str: ...
    def __str__(self) -> str: ...
    async def apre_create(self) -> None:
        """
        Prepares the object for creation by setting its size attribute.

        This method calculates the size of the object's data and assigns it to the size attribute.
        If the data is None, it defaults to an empty byte string.

        Args:
            None
        """
    async def apre_update(self) -> None:
        """
        Prepares the object for update by setting its size attribute.

        This method calculates the size of the object's data and assigns it to the size attribute.
        If the data is None, it defaults to an empty byte string.

        Args:
            None
        """
    @classmethod
    def data_base64_decode(cls, v: bytes) -> bytes:
        """
        Decodes a base64-encoded byte string if it is base64-encoded.

        This method checks if the provided byte string is base64-encoded and decodes it if true.
        If the byte string is not base64-encoded, it returns the original byte string.

        Args:
            cls: The class this method belongs to.
            v (bytes): The byte string to be checked and potentially decoded.

        Returns:
            bytes: The decoded byte string if it was base64-encoded, otherwise the original byte string.
        """
    @classmethod
    def from_file(cls, file_or_path: Path | BinaryIO) -> File:
        """
        Creates a `File` object from a file path or a binary file object.

        Args:
            file_or_path (Path | BinaryIO): The file path or binary file object.

        Returns:
            File: The created `File` object.

        Raises:
            ValueError: If the provided path is a directory.
        """
    @property
    def mimetype(self) -> str | None:
        """
        Returns the MIME type of the file based on its filename.

        This method uses the `mimetypes` module to guess the MIME type of the file.

        Returns:
            str | None: The guessed MIME type of the file, or None if it cannot be determined.
        """
    def pre_create(self) -> None:
        """
        Prepares the object for creation by setting its size attribute.

        This method calculates the size of the object's data and assigns it to the size attribute.
        If the data is None, it defaults to an empty byte string.

        Args:
            None
        """
    def pre_update(self) -> None:
        """
        Prepares the object for update by setting its size attribute.

        This method calculates the size of the object's data and assigns it to the size attribute.
        If the data is None, it defaults to an empty byte string.

        Args:
            None
        """
    def to_file(self, file_or_path: Path | BinaryIO) -> None:
        """
        Writes the object's data to a file path or a binary file object.

        Args:
            file_or_path (Path | BinaryIO): The file path or binary file object where the data will be written.

        Returns:
            None

        Raises:
            ValueError: If the provided path is a directory.
        """
