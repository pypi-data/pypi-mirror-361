from typing import *

from pydantic import BaseModel, Field

from .ObjectError import ObjectError


class CouldNotRegisterErrorResponse(BaseModel):
    """
    CouldNotRegisterErrorResponse model

    """

    model_config = {"populate_by_name": True, "validate_assignment": True}

    error: str = Field(validation_alias="error")

    objects: Optional[List[Optional[ObjectError]]] = Field(
        validation_alias="objects", default=None
    )
