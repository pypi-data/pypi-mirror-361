from pydantic import BaseModel, Field


class Authorization(BaseModel):
    scheme: str = Field(..., description="Authorization's scheme")
    credentials: str = Field(..., description="Authorization's credentials")
