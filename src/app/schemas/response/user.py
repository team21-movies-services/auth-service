from uuid import UUID
from typing import Optional

from pydantic import BaseModel
from datetime import datetime

from schemas.response.token import TokensResponse


class UserResponse(BaseModel):
    id: UUID
    email: str
    first_name: Optional[str]
    last_name: Optional[str]
    is_superuser: bool
    is_active: bool
    created_at: datetime
    updated_at: datetime

    tokens: Optional[TokensResponse] = None

    class Config:
        orm_mode = True
