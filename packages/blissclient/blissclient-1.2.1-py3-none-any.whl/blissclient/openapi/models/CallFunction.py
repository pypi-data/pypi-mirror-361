from typing import *

from pydantic import BaseModel, Field


class CallFunction(BaseModel):
    """
    CallFunction model

    """

    model_config = {"populate_by_name": True, "validate_assignment": True}

    args: Optional[Union[List[Any], None]] = Field(
        validation_alias="args", default=None
    )

    emit_stdout: Optional[Union[bool, None]] = Field(
        validation_alias="emit_stdout", default=None
    )

    env_object: Optional[Union[str, None]] = Field(
        validation_alias="env_object", default=None
    )

    function: str = Field(validation_alias="function")

    has_scan_factory: Optional[Union[bool, None]] = Field(
        validation_alias="has_scan_factory", default=None
    )

    in_terminal: Optional[Union[bool, None]] = Field(
        validation_alias="in_terminal", default=None
    )

    kwargs: Optional[Union[Dict[str, Any], None]] = Field(
        validation_alias="kwargs", default=None
    )

    object: Optional[Union[str, None]] = Field(validation_alias="object", default=None)
