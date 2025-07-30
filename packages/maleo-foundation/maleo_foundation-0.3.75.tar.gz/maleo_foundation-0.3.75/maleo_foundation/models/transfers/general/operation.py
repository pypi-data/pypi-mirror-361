import json
from pydantic import BaseModel, Field, model_validator
from typing import Any, Optional, Self
from uuid import UUID, uuid4
from .request import RequestContext
from .response import ResponseContext
from .service import ServiceContext
from maleo_foundation.enums import BaseEnums
from maleo_foundation.models.transfers.general.authentication import Authentication
from maleo_foundation.models.transfers.general.authorization import Authorization
from maleo_foundation.types import BaseTypes


class OperationId(BaseModel):
    operation_id: UUID = Field(uuid4(), description="Operation's ID")


class OperationArguments(BaseModel):
    positional: BaseTypes.ListOfAny = Field([], description="Positional arguments")
    keyword: BaseTypes.StringToAnyDict = Field({}, description="Keyword arguments")


class OperationOrigin(BaseModel):
    type: BaseEnums.OperationOrigin = Field(
        ..., description="Operation's origin's type"
    )
    properties: BaseTypes.OptionalStringToStringDict = Field(
        None, description="Operation's origin's properties"
    )


class OperationLayer(BaseModel):
    type: BaseEnums.OperationLayer = Field(..., description="Operation's layer's type")
    properties: BaseTypes.OptionalStringToStringDict = Field(
        None, description="Operation's layer's properties"
    )


class OperationTarget(BaseModel):
    type: BaseEnums.OperationTarget = Field(
        ..., description="Operation's target's type"
    )
    properties: BaseTypes.OptionalStringToStringDict = Field(
        None, description="Operation's target's properties"
    )


class OperationContext(BaseModel):
    origin: OperationOrigin = Field(..., description="Operation's origin")
    layer: OperationLayer = Field(..., description="Operation's layer")
    target: Optional[OperationTarget] = Field(
        None, description="Operation's target (optional)"
    )


class OperationMetadata(BaseModel):
    type: BaseEnums.OperationType = Field(..., description="Operation's type")
    create_type: Optional[BaseEnums.CreateType] = Field(
        None, description="Create type (optional)"
    )
    update_type: Optional[BaseEnums.UpdateType] = Field(
        None, description="Update type (optional)"
    )
    status_update_type: Optional[BaseEnums.StatusUpdateType] = Field(
        None, description="Status update type (optional)"
    )

    # @model_validator(mode="after")
    # def validate_operation_types(self) -> Self:
    #     # Validate create operation type
    #     if self.type is BaseEnums.OperationType.CREATE:
    #         if self.create_type is None:
    #             raise ValueError(
    #                 "'create_type' must have value if 'type' is 'create'"
    #             )
    #         if self.create_type not in BaseEnums.CreateType:
    #             raise ValueError(
    #                 f"'create_type' must be one of {[e.value for e in BaseEnums.CreateType]}"
    #             )

    #     # Validate update operation type
    #     if self.type is BaseEnums.OperationType.UPDATE:
    #         if self.update_type is None:
    #             raise ValueError(
    #                 "'update_type' must have value if 'type' is 'update'"
    #             )
    #         if self.update_type not in BaseEnums.UpdateType:
    #             raise ValueError(
    #                 f"'update_type' must be one of {[e.value for e in BaseEnums.UpdateType]}"
    #             )
    #         if self.update_type is BaseEnums.UpdateType.STATUS:
    #             if self.status_update_type is None:
    #                 raise ValueError(
    #                     "'status_update_type' must have value if 'update_type' is 'status'"
    #                 )
    #             if self.status_update_type not in BaseEnums.StatusUpdateType:
    #                 raise ValueError(
    #                     f"'status_update_type' must be one of {[e.value for e in BaseEnums.StatusUpdateType]}"
    #                 )

    #     return self


class OperationException(BaseModel):
    type: BaseEnums.ExceptionType = Field(
        BaseEnums.ExceptionType.INTERNAL, description="Exception type"
    )
    raw: str = Field(..., description="Raw exception")
    traceback: BaseTypes.ListOfStrings = Field(..., description="Traceback")


class OperationTimestamps(BaseModel):
    started_at: BaseTypes.OptionalDatetime = Field(
        None, description="Started at timestamp (Optional)"
    )
    finished_at: BaseTypes.OptionalDatetime = Field(
        None, description="Finished at timestamp (Optional)"
    )
    duration: float = Field(0, description="Operation duration")

    @model_validator(mode="after")
    def calculate_duration(self) -> Self:
        if self.started_at is not None and self.finished_at is not None:
            self.duration = (self.finished_at - self.started_at).total_seconds()

        return self


class OperationResult(BaseModel):
    success: bool = Field(..., description="Success status")
    code: BaseTypes.OptionalString = Field(None, description="Optional result code")
    message: BaseTypes.OptionalString = Field(None, description="Optional message")
    description: BaseTypes.OptionalString = Field(
        None, description="Optional description"
    )
    data: Any = Field(..., description="Data")
    metadata: BaseTypes.OptionalAny = Field(None, description="Optional metadata")
    other: BaseTypes.OptionalAny = Field(None, description="Optional other information")


class Operation(BaseModel):
    operation_id: UUID = Field(..., description="Operation's ID")
    summary: str = Field(..., description="Operation's summary")
    request_context: RequestContext = Field(..., description="Request context")
    authentication: Authentication = Field(..., description="Authentication")
    authorization: Optional[Authorization] = Field(None, description="Authorization")
    service: ServiceContext = Field(..., description="Service's context")
    timestamps: OperationTimestamps = Field(..., description="Operation's timestamps")
    context: OperationContext = Field(..., description="Operation's context")
    metadata: OperationMetadata = Field(..., description="Operation's metadata")
    exception: Optional[OperationException] = Field(
        None, description="Operation's exception"
    )
    arguments: Optional[OperationArguments] = Field(
        None, description="Operation's arguments"
    )
    result: Optional[OperationResult] = Field(None, description="Operation's result")
    response_context: Optional[ResponseContext] = Field(
        None, description="Response's context"
    )

    def to_log_string(self, multiline: bool = True, indent: int = 2) -> str:
        if not self.authentication.user.is_authenticated:
            authentication = "Unauthenticated"
        else:
            authentication = (
                "Authenticated | "
                f"Username: {self.authentication.user.display_name} | "
                f"Email: {self.authentication.user.identity}"
            )
        summary = f"Operation {self.operation_id} - {authentication} - {self.summary}"
        payload = self.model_dump(mode="json")
        if multiline:
            details = f"\n{json.dumps(payload, indent=indent)}"
        else:
            details = f" - Details: {json.dumps(payload)}"
        return f"{summary}{details}"


class DatabaseOperationContext(BaseModel):
    database: str = Field(..., description="Database name")
    environment: BaseEnums.EnvironmentType = Field(
        ..., description="Database environment"
    )
    table: str = Field(..., description="Table name")


class DatabaseOperationResult(BaseModel):
    data_id: int = Field(..., ge=1, description="Data's ID")
    old_data: BaseTypes.OptionalAny = Field(None, description="Old data")
    new_data: BaseTypes.OptionalAny = Field(None, description="New data")

    @model_validator(mode="after")
    def validate_data(self) -> Self:
        if self.old_data is None and self.new_data is None:
            raise ValueError("Either 'old_data' or 'new_data' must have value")
        return self


class DatabaseOperation(BaseModel):
    operation_id: UUID = Field(uuid4(), description="Operation's ID")
    request_context: RequestContext = Field(..., description="Request context")
    authentication: Authentication = Field(..., description="Authentication")
    authorization: Optional[Authorization] = Field(None, description="Authorization")
    service: ServiceContext = Field(..., description="Service's context")
    timestamps: OperationTimestamps = Field(..., description="Operation's timestamps")
    context: DatabaseOperationContext = Field(
        ..., description="Database operation's context"
    )
    metadata: OperationMetadata = Field(..., description="Operation's metadata")
    result: DatabaseOperationResult = Field(
        ..., description="Database operation's result"
    )
