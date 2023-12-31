import uuid
from datetime import datetime

from pydantic.main import BaseModel

from models.history import ActionType


class DeviceResponse(BaseModel):
    id: uuid.UUID
    user_agent: str

    class Config:
        orm_mode = True


class HistoryResponse(BaseModel):
    user_id: uuid.UUID
    device: DeviceResponse
    action_type: ActionType
    created_at: datetime

    class Config:
        orm_mode = True
