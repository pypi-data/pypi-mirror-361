from typing import *

from pydantic import BaseModel, Field


class ObjectError(BaseModel):
    """
    ObjectError model

    """

    model_config = {"populate_by_name": True, "validate_assignment": True}

    error: str = Field(validation_alias="error")

    name: str = Field(validation_alias="name")
