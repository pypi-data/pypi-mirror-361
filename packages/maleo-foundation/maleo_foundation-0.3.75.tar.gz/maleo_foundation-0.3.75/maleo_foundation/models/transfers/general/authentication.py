from pydantic import BaseModel, Field
from typing import Optional, Sequence
from maleo_foundation.enums import BaseEnums
from .token import (
    MaleoFoundationTokenGeneralTransfers,
)


class Token(BaseModel):
    type: BaseEnums.TokenType = Field(..., description="Token's type")
    payload: MaleoFoundationTokenGeneralTransfers.DecodePayload = Field(
        ..., description="Token's payload"
    )


class Credentials(BaseModel):
    token: Optional[Token] = Field(None, description="Token")
    scopes: Optional[Sequence[str]] = Field(None, description="Scopes")


class User(BaseModel):
    is_authenticated: bool = Field(False, description="Authenticated")
    display_name: str = Field("", description="Username")
    identity: str = Field("", description="Email")


class Authentication(BaseModel):
    credentials: Credentials = Field(
        default_factory=Credentials,  # type: ignore
        description="Credential",
    )
    user: User = Field(
        default_factory=User,  # type: ignore
        description="User",
    )
