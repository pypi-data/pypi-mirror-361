from datetime import datetime
from typing import Optional

from pydantic import BaseModel, model_validator


class MessageCreate(BaseModel):
    topic: str
    message: str
    aggregate_type: Optional[str] = None
    aggregate_id: Optional[int] = None

    @model_validator(mode="after")
    def validate_aggregate_fields(self):
        if self.aggregate_id is not None and self.aggregate_type is None:
            raise ValueError("aggregate_type is required when aggregate_id is provided")
        return self


class Message(MessageCreate):
    id: str

    connection_id: str
    session_id: str

    timestamp: datetime
    created_at: datetime
