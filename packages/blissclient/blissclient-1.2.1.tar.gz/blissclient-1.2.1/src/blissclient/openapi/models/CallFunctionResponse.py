from typing import *

from pydantic import BaseModel, Field


class CallFunctionResponse(BaseModel):
    """
    CallFunctionResponse model

    """

    model_config = {"populate_by_name": True, "validate_assignment": True}

    call_id: str = Field(validation_alias="call_id")
