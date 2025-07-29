from typing import *

from pydantic import BaseModel, Field


class ObjectTypeSchema(BaseModel):
    """
    ObjectTypeSchema model

    """

    model_config = {"populate_by_name": True, "validate_assignment": True}

    callables: Optional[Dict[str, Any]] = Field(
        validation_alias="callables", default=None
    )

    properties: Any = Field(validation_alias="properties")

    state_ok: List[str] = Field(validation_alias="state_ok")

    type: str = Field(validation_alias="type")
