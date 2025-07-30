from pydantic import BaseModel, Field
from maleo_foundation.enums import BaseEnums


class ServiceContext(BaseModel):
    key: BaseEnums.Service = Field(..., description="Service's key")
    environment: BaseEnums.EnvironmentType = Field(
        ..., description="Service's environment"
    )
