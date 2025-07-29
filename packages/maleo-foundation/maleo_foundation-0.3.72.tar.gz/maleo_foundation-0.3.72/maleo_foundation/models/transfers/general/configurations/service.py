from pydantic import BaseModel, Field
from maleo_foundation.enums import BaseEnums


class ServiceConfigurations(BaseModel):
    key: BaseEnums.Service = Field(..., description="Service's key")
    name: str = Field(..., description="Service's name")
    host: str = Field(..., description="Service's host")
    port: int = Field(..., description="Service's port")
