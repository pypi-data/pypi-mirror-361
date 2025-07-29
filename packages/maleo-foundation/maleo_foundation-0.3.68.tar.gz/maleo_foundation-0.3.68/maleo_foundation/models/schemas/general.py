from __future__ import annotations
from datetime import datetime, timezone
from pydantic import BaseModel, Field, model_validator
from typing import Any, Optional, Self
from uuid import UUID
from maleo_foundation.enums import BaseEnums
from maleo_foundation.types import BaseTypes


class BaseGeneralSchemas:
    class DateFilter(BaseModel):
        name: str = Field(..., description="Column name.")
        from_date: BaseTypes.OptionalDatetime = Field(None, description="From date.")
        to_date: BaseTypes.OptionalDatetime = Field(None, description="To date.")

    class SortColumn(BaseModel):
        name: str = Field(..., description="Column name.")
        order: BaseEnums.SortOrder = Field(..., description="Sort order.")

    class SimplePagination(BaseModel):
        page: int = Field(1, ge=1, description="Page number, must be >= 1.")
        limit: int = Field(
            10, ge=1, le=100, description="Page size, must be 1 <= limit <= 100."
        )

    # * ----- ----- ----- Operation ----- ----- ----- *#
    class OperationArguments(BaseModel):
        positional: BaseTypes.ListOfAny = Field([], description="Positional arguments")
        keyword: BaseTypes.StringToAnyDict = Field({}, description="Keyword arguments")

    class OperationContext(BaseModel):
        origin: BaseEnums.OperationOrigin = Field(..., description="Operation's origin")
        client_key: BaseTypes.OptionalString = Field(None, description="Client's key")
        layer: BaseEnums.OperationLayer = Field(..., description="Operation's layer")
        target: Optional[BaseEnums.OperationTarget] = Field(
            None, description="Operation's target (optional)"
        )
        environment: Optional[BaseEnums.EnvironmentType] = Field(
            None, description="Operation's target's environment (optional)"
        )
        target_name: BaseTypes.OptionalString = Field(
            None, description="Operation's target's name (optional)"
        )
        target_resource: BaseTypes.OptionalString = Field(
            None, description="Operation's target's resource (optional)"
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
        summary: BaseTypes.OptionalString = Field(
            None, description="Summary (optional)"
        )

        @model_validator(mode="after")
        def validate_operation_types(self) -> Self:
            # Validate create operation type
            if self.type is BaseEnums.OperationType.CREATE:
                if self.create_type is None:
                    raise ValueError(
                        "'create_type' must have value if 'type' is 'create'"
                    )
                if self.create_type not in BaseEnums.CreateType:
                    raise ValueError(
                        f"'create_type' must be one of {[e.value for e in BaseEnums.CreateType]}"
                    )

            # Validate update operation type
            if self.type is BaseEnums.OperationType.UPDATE:
                if self.update_type is None:
                    raise ValueError(
                        "'update_type' must have value if 'type' is 'update'"
                    )
                if self.update_type not in BaseEnums.UpdateType:
                    raise ValueError(
                        f"'update_type' must be one of {[e.value for e in BaseEnums.UpdateType]}"
                    )
                if self.update_type is BaseEnums.UpdateType.STATUS:
                    if self.status_update_type is None:
                        raise ValueError(
                            "'status_update_type' must have value if 'update_type' is 'status'"
                        )
                    if self.status_update_type not in BaseEnums.StatusUpdateType:
                        raise ValueError(
                            f"'status_update_type' must be one of {[e.value for e in BaseEnums.StatusUpdateType]}"
                        )

            return self

    class OperationServiceContext(BaseModel):
        key: BaseEnums.Service = Field(..., description="Service's key")
        environment: BaseEnums.EnvironmentType = Field(
            ..., description="Service's environment"
        )

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
        other: BaseTypes.OptionalAny = Field(
            None, description="Optional other information"
        )

    class DatabaseOperationContext(BaseModel):
        database: str = Field(..., description="Database name")
        environment: BaseEnums.EnvironmentType = Field(
            ..., description="Database environment"
        )
        table: str = Field(..., description="Table name")

    class DatabaseOperationResult(BaseModel):
        data_id: int = Field(..., ge=1, description="Data's ID")
        old_data: BaseTypes.OptionalStringToAnyDict = Field(
            None, description="Old data"
        )
        new_data: BaseTypes.OptionalStringToAnyDict = Field(
            None, description="New data"
        )

        @model_validator(mode="after")
        def validate_data(self) -> Self:
            if self.old_data is None and self.new_data is None:
                raise ValueError("Either 'old_data' or 'new_data' must have value")
            return self

    # * ----- ----- ----- Data ----- ----- ----- *#
    class Identifiers(BaseModel):
        id: int = Field(..., ge=1, description="Data's ID, must be >= 1.")
        uuid: UUID = Field(..., description="Data's UUID.")

    class EssentialTimestamps(BaseModel):
        created_at: datetime = Field(..., description="Data's created_at timestamp")
        updated_at: datetime = Field(..., description="Data's updated_at timestamp")

    class StatusTimestamps(BaseModel):
        deleted_at: BaseTypes.OptionalDatetime = Field(
            ..., description="Data's deleted_at timestamp"
        )
        restored_at: BaseTypes.OptionalDatetime = Field(
            ..., description="Data's restored_at timestamp"
        )
        deactivated_at: BaseTypes.OptionalDatetime = Field(
            ..., description="Data's deactivated_at timestamp"
        )
        activated_at: datetime = Field(..., description="Data's activated_at timestamp")

    class Timestamps(StatusTimestamps, EssentialTimestamps):
        pass

    class Status(BaseModel):
        status: BaseEnums.StatusType = Field(..., description="Data's status")

    class DataMixin(Status, Timestamps, Identifiers):
        pass

    class IsDefault(BaseModel):
        is_default: BaseTypes.OptionalBoolean = Field(
            None, description="Whether data is default"
        )

    class IsRoot(BaseModel):
        is_root: BaseTypes.OptionalBoolean = Field(
            None, description="Whether data is root"
        )

    class IsParent(BaseModel):
        is_parent: BaseTypes.OptionalBoolean = Field(
            None, description="Whether data is parent"
        )

    class IsChild(BaseModel):
        is_child: BaseTypes.OptionalBoolean = Field(
            None, description="Whether data is child"
        )

    class IsLeaf(BaseModel):
        is_leaf: BaseTypes.OptionalBoolean = Field(
            None, description="Whether data is leaf"
        )

    class Order(BaseModel):
        order: BaseTypes.OptionalInteger = Field(..., description="Data's order")

    class Code(BaseModel):
        code: str = Field(..., description="Data's code")

    class Key(BaseModel):
        key: str = Field(..., description="Data's key")

    class Name(BaseModel):
        name: str = Field(..., description="Data's name")

    class Secret(BaseModel):
        secret: UUID = Field(..., description="Data's secret")

    # * ----- ----- ----- RSA Key ----- ----- ----- *#
    class PrivateKey(BaseModel):
        private_key: str = Field(..., description="Private key in str format.")

    class PublicKey(BaseModel):
        public_key: str = Field(..., description="Public key in str format.")

    class KeyPair(PublicKey, PrivateKey):
        pass

    class RSAKeys(BaseModel):
        password: str = Field(..., description="Key's password")
        private: str = Field(..., description="Private key")
        public: str = Field(..., description="Public key")

    class AccessedAt(BaseModel):
        accessed_at: datetime = Field(
            datetime.now(tz=timezone.utc), description="Accessed at"
        )

    class AccessedBy(BaseModel):
        accessed_by: int = Field(0, ge=0, description="Accessed by")
