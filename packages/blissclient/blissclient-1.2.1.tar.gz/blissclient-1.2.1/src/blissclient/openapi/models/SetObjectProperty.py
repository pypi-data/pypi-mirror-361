from typing import *

from pydantic import BaseModel, Field


class SetObjectProperty(BaseModel):
    """
    SetObjectProperty model

    """

    model_config = {"populate_by_name": True, "validate_assignment": True}

    property: str = Field(validation_alias="property")

    value: Any = Field(validation_alias="value")
