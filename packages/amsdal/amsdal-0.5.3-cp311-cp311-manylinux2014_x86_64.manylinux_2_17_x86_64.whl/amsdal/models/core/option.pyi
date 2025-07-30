from amsdal_models.classes.model import TypeModel
from amsdal_utils.models.enums import ModuleType
from typing import ClassVar

class Option(TypeModel):
    __module_type__: ClassVar[ModuleType]
    key: str
    value: str
