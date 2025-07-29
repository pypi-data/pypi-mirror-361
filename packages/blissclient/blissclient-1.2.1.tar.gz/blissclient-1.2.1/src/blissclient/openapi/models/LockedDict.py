from typing import *

from pydantic import BaseModel, Field


class LockedDict(BaseModel):
    """
    LockedDict model

    """

    model_config = {"populate_by_name": True, "validate_assignment": True}

    reason: str = Field(validation_alias="reason")
