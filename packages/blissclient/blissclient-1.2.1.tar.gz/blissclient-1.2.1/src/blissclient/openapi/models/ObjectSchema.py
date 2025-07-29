from typing import *

from pydantic import BaseModel, Field

from .LockedDict import LockedDict


class ObjectSchema(BaseModel):
    """
    ObjectSchema model

    """

    model_config = {"populate_by_name": True, "validate_assignment": True}

    alias: Optional[Union[str, None]] = Field(validation_alias="alias", default=None)

    errors: List[Dict[str, Any]] = Field(validation_alias="errors")

    locked: Union[LockedDict, None] = Field(validation_alias="locked")

    name: str = Field(validation_alias="name")

    online: bool = Field(validation_alias="online")

    properties: Dict[str, Any] = Field(validation_alias="properties")

    type: str = Field(validation_alias="type")

    user_tags: List[str] = Field(validation_alias="user_tags")
