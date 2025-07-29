from pydantic import BaseModel, ConfigDict, Field
from maleo_foundation.types import BaseTypes
from .publisher import PublisherConfigurations


class PubSubConfigurations(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    publisher: PublisherConfigurations = Field(
        default_factory=PublisherConfigurations,
        description="Publisher's configurations",
    )
    subscriptions: BaseTypes.OptionalListOfStrings = Field(
        None, description="Subscriptions"
    )
