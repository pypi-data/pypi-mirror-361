from google.cloud.pubsub_v1.subscriber.message import Message
from typing import Awaitable, Callable, Optional, Union
from maleo_foundation.models.transfers.results.service.controllers.rest import (
    BaseServiceRESTControllerResults,
)


class ControllerTypes:
    # * REST controller types
    SyncRESTController = Callable[..., BaseServiceRESTControllerResults]
    OptionalSyncRESTController = Optional[
        Callable[..., BaseServiceRESTControllerResults]
    ]
    AsyncRESTController = Callable[..., Awaitable[BaseServiceRESTControllerResults]]
    OptionalAsyncRESTController = Optional[
        Callable[..., Awaitable[BaseServiceRESTControllerResults]]
    ]
    RESTController = Union[SyncRESTController, AsyncRESTController]
    OptionalRESTController = Optional[RESTController]

    # * Message controller types
    SyncMessageController = Callable[[str, Message], bool]
    AsyncMessageController = Callable[[str, Message], Awaitable[bool]]
    MessageController = Union[SyncMessageController, AsyncMessageController]
    OptionalMessageController = Optional[MessageController]
