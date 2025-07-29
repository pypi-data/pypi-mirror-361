from typing import *

from pydantic import BaseModel, Field


class ErrorResponse(BaseModel):
    """
    ErrorResponse model

    """

    model_config = {"populate_by_name": True, "validate_assignment": True}

    error: str = Field(validation_alias="error")
