from amsdal_models.classes.model import TypeModel
from amsdal_utils.models.enums import ModuleType
from typing import Any, ClassVar

class FrontendConfigSkipNoneBase(TypeModel):
    __module_type__: ClassVar[ModuleType]
    def model_dump(self, **kwargs: Any) -> dict[str, Any]: ...
    def model_dump_json(self, **kwargs: Any) -> str: ...
