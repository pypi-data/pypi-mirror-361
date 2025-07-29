from typing import *

from pydantic import BaseModel, Field

from .ObjectSchema import ObjectSchema


class Paginated_ObjectSchema_(BaseModel):
    """
    Paginated&lt;ObjectSchema&gt; model

    """

    model_config = {"populate_by_name": True, "validate_assignment": True}

    limit: Optional[Union[int, None]] = Field(validation_alias="limit", default=None)

    results: List[ObjectSchema] = Field(validation_alias="results")

    skip: Optional[Union[int, None]] = Field(validation_alias="skip", default=None)

    total: int = Field(validation_alias="total")
