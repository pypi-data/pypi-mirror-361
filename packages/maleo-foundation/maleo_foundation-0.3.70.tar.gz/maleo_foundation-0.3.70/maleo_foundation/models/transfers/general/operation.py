from pydantic import BaseModel, Field
from typing import Optional
from .request import RequestContext
from maleo_foundation.authentication import Authentication
from maleo_foundation.authorization import Authorization
from maleo_foundation.models.schemas.general import BaseGeneralSchemas


class Operation(BaseModel):
    request_context: RequestContext = Field(..., description="Request context")
    authentication: Authentication = Field(..., description="Authentication")
    authorization: Optional[Authorization] = Field(None, description="Authorization")
    service: BaseGeneralSchemas.OperationServiceContext = Field(
        ..., description="Service's context"
    )
    timestamps: BaseGeneralSchemas.OperationTimestamps = Field(
        ..., description="Operation's timestamps"
    )
    context: BaseGeneralSchemas.OperationContext = Field(
        ..., description="Operation's context"
    )
    metadata: BaseGeneralSchemas.OperationMetadata = Field(
        ..., description="Operation's metadata"
    )
    arguments: BaseGeneralSchemas.OperationArguments = Field(
        ..., description="Operation's arguments"
    )
    result: BaseGeneralSchemas.OperationResult = Field(
        ..., description="Database operation's result"
    )


class DatabaseOperation(BaseModel):
    request_context: RequestContext = Field(..., description="Request context")
    authentication: Authentication = Field(..., description="Authentication")
    authorization: Optional[Authorization] = Field(None, description="Authorization")
    service: BaseGeneralSchemas.OperationServiceContext = Field(
        ..., description="Service's context"
    )
    timestamps: BaseGeneralSchemas.OperationTimestamps = Field(
        ..., description="Operation's timestamps"
    )
    context: BaseGeneralSchemas.DatabaseOperationContext = Field(
        ..., description="Database operation's context"
    )
    metadata: BaseGeneralSchemas.OperationMetadata = Field(
        ..., description="Operation's metadata"
    )
    result: BaseGeneralSchemas.DatabaseOperationResult = Field(
        ..., description="Database operation's result"
    )
