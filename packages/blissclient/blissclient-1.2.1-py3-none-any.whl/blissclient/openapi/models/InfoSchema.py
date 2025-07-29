from typing import *

from pydantic import BaseModel, Field


class InfoSchema(BaseModel):
    """
        InfoSchema model
            Information related to this session.

    This could contain extra keys.

    """

    model_config = {"populate_by_name": True, "validate_assignment": True}

    beamline: str = Field(validation_alias="beamline")

    bliss_version: str = Field(validation_alias="bliss_version")

    blissdata_version: str = Field(validation_alias="blissdata_version")

    blisstomo_version: str = Field(validation_alias="blisstomo_version")

    blisswebui_version: str = Field(validation_alias="blisswebui_version")

    flint_version: str = Field(validation_alias="flint_version")

    fscan_version: str = Field(validation_alias="fscan_version")

    instrument: str = Field(validation_alias="instrument")

    session: str = Field(validation_alias="session")

    synchrotron: str = Field(validation_alias="synchrotron")
