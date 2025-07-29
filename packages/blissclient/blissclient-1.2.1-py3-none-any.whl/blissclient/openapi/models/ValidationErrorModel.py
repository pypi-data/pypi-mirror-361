from typing import *

from pydantic import BaseModel, Field


class ValidationErrorModel(BaseModel):
    """
    ValidationErrorModel model

    """

    model_config = {"populate_by_name": True, "validate_assignment": True}

    ctx: Optional[Union[Dict[str, Any], None]] = Field(
        validation_alias="ctx", default=None
    )

    loc: Optional[Union[List[str], None]] = Field(validation_alias="loc", default=None)

    msg: Optional[Union[str, None]] = Field(validation_alias="msg", default=None)

    type_: Optional[Union[str, None]] = Field(validation_alias="type_", default=None)
