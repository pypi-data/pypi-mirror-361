from pydantic import BaseModel, ConfigDict, Field
from maleo_foundation.controller_types import ControllerTypes


class SubscriptionConfigurations(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    id: str = Field(..., description="Subscription's ID")
    max_messages: int = Field(10, description="Subscription's Max messages")
    ack_deadline: int = Field(10, description="Subscription's ACK deadline")


class ExtendedSubscriptionConfigurations(SubscriptionConfigurations):
    controller: ControllerTypes.OptionalMessageController = Field(
        None, description="Optional message controller"
    )
