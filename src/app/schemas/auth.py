from uuid import UUID

from pydantic.main import BaseModel


class AuthData(BaseModel):
    user_id: UUID
    is_superuser: bool
    roles: list[str]


class RefreshData(BaseModel):
    user_id: UUID
    is_superuser: bool
    refresh_token: str
    roles: list[str]
