from __future__ import annotations
from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field
from typing import List, Optional, Tuple
from uuid import UUID
from maleo_foundation.types import BaseTypes
from .user_agent import UserAgent


class RequestContext(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    request_id: UUID = Field(..., description="Request's ID")
    requested_at: datetime = Field(..., description="Request timestamp")
    method: str = Field(..., description="Request's method")
    url: str = Field(..., description="Request's URL")
    ip_address: str = Field("unknown", description="Client's IP address")
    is_internal: BaseTypes.OptionalBoolean = Field(
        None, description="True if IP is internal"
    )
    headers: Optional[List[Tuple[str, str]]] = Field(
        None, description="Request's headers"
    )
    path_params: BaseTypes.OptionalStringToStringDict = Field(
        None, description="Request's path parameters"
    )
    query_params: BaseTypes.OptionalString = Field(
        None, description="Request's query parameters"
    )
    user_agent: UserAgent = Field(..., description="User agent")
    referer: BaseTypes.OptionalString = Field(None, description="Referrer URL")
    origin: BaseTypes.OptionalString = Field(None, description="Origin of the request")
    host: BaseTypes.OptionalString = Field(None, description="Host header from request")
    forwarded_proto: BaseTypes.OptionalString = Field(
        None, description="Forwarded protocol (http/https)"
    )
    language: BaseTypes.OptionalString = Field(
        None, description="Accepted languages from client"
    )
