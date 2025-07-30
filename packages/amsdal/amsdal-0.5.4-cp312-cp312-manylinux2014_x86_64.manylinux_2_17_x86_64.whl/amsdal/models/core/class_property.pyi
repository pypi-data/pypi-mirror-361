from amsdal.models.core.option import *
from amsdal_models.classes.model import TypeModel
from amsdal_utils.models.enums import ModuleType
from typing import Any, ClassVar

class ClassProperty(TypeModel):
    __module_type__: ClassVar[ModuleType]
    title: str | None
    type: str
    default: Any | None
    options: list['Option'] | None
    items: dict[str, Any | None] | None
    discriminator: str | None
    @classmethod
    def _non_empty_keys_items(cls, value: Any) -> Any: ...
