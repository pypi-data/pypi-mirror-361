from typing import *

from pydantic import BaseModel, Field


class YamlContentSchema(BaseModel):
    """
    YamlContentSchema model

    """

    model_config = {"populate_by_name": True, "validate_assignment": True}

    content: Any = Field(validation_alias="content")
