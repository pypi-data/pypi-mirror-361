from pydantic import BaseModel, ConfigDict, Field
from typing import Optional


class TopicConfigurations(BaseModel):
    id: str = Field(..., description="Topic's id")


DEFAULT_DATABASE_OPERATION_TOPIC_CONFIGURATIONS = TopicConfigurations(
    id="database-operation"
)

DEFAULT_OPERATION_TOPIC_CONFIGURATIONS = TopicConfigurations(id="operation")


class SingleTopicsConfigurations(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)


class MandatoryTopicsConfigurations(SingleTopicsConfigurations):
    database_operation: TopicConfigurations = Field(
        default=DEFAULT_DATABASE_OPERATION_TOPIC_CONFIGURATIONS,
        description="Database operation topic configurations",
    )
    operation: TopicConfigurations = Field(
        default=DEFAULT_OPERATION_TOPIC_CONFIGURATIONS,
        description="Operation topic configurations",
    )


class AdditionalTopicsConfigurations(SingleTopicsConfigurations):
    pass


class TopicsConfigurations(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    mandatory: MandatoryTopicsConfigurations = Field(
        default_factory=MandatoryTopicsConfigurations,
        description="Mandatory topics configurations",
    )
    additional: Optional[AdditionalTopicsConfigurations] = Field(
        default=None, description="Additional topics configurations"
    )


class PublisherConfigurations(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    topics: TopicsConfigurations = Field(
        default_factory=TopicsConfigurations, description="Topics configurations"
    )
