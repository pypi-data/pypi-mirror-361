from typing import *

from pydantic import BaseModel, Field

from .ObjectTypeSchema import ObjectTypeSchema


class Paginated_ObjectTypeSchema_(BaseModel):
    """
    Paginated&lt;ObjectTypeSchema&gt; model

    """

    model_config = {"populate_by_name": True, "validate_assignment": True}

    limit: Optional[Union[int, None]] = Field(validation_alias="limit", default=None)

    results: List[ObjectTypeSchema] = Field(validation_alias="results")

    skip: Optional[Union[int, None]] = Field(validation_alias="skip", default=None)

    total: int = Field(validation_alias="total")
