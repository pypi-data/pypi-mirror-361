from typing import *

from pydantic import BaseModel, Field


class CallFunctionAsyncState(BaseModel):
    """
    CallFunctionAsyncState model

    """

    model_config = {"populate_by_name": True, "validate_assignment": True}

    progress: Optional[Union[Dict[str, Any], None]] = Field(
        validation_alias="progress", default=None
    )

    return_value: Optional[Union[Any, None]] = Field(
        validation_alias="return_value", default=None
    )

    state: str = Field(validation_alias="state")
