from amsdal_models.classes.model import TypeModel
from amsdal_utils.models.enums import ModuleType
from typing import Any, ClassVar

class Validator(TypeModel):
    __module_type__: ClassVar[ModuleType]
    name: str
    data: Any
