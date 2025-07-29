from pydantic import BaseModel, ConfigDict, Field
from typing import Optional


class TopicConfigurations(BaseModel):
    id: str = Field(..., description="Topic's id")


DEFAULT_DATABASE_ACCESS_TOPIC_CONFIGURATIONS = TopicConfigurations(id="database-access")

DEFAULT_DATABASE_AUDIT_TOPIC_CONFIGURATIONS = TopicConfigurations(id="database-audit")

DEFAULT_OPERATION_TOPIC_CONFIGURATIONS = TopicConfigurations(id="operation")


class TopicsConfigurations(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    database_access: Optional[TopicConfigurations] = Field(
        default=DEFAULT_DATABASE_ACCESS_TOPIC_CONFIGURATIONS,
        description="Database access topic configurations",
    )
    database_audit: Optional[TopicConfigurations] = Field(
        default=DEFAULT_DATABASE_AUDIT_TOPIC_CONFIGURATIONS,
        description="Database audit topic configurations",
    )
    operation: Optional[TopicConfigurations] = Field(
        default=DEFAULT_OPERATION_TOPIC_CONFIGURATIONS,
        description="Operation topic configurations",
    )


class PublisherConfigurations(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    topics: TopicsConfigurations = Field(
        default_factory=TopicsConfigurations, description="Topics configurations"
    )
