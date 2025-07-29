from typing import *

from pydantic import BaseModel, Field


class RegisterHardwareSchema(BaseModel):
    """
    RegisterHardwareSchema model

    """

    model_config = {"populate_by_name": True, "validate_assignment": True}

    names: List[str] = Field(validation_alias="names")
