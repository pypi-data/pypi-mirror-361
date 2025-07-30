from __future__ import annotations
from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field
from typing import List, Optional, Tuple


class ResponseContext(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    responded_at: datetime = Field(..., description="Respond timestamp")
    process_time: float = Field(..., description="Process time")
    headers: Optional[List[Tuple[str, str]]] = Field(
        None, description="Response's headers"
    )
