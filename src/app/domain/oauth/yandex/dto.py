from typing import Optional, Literal
from uuid import UUID

from dataclasses import dataclass
from domain.base.dto import BaseDTO


@dataclass
class AuthorizationUrlDto(BaseDTO):
    redirect_uri: str
    device_id: UUID
    client_id: Optional[str] = None
    response_type: Optional[str] = None  # FIXME: check from enum


@dataclass
class OAuthRequestTokenDto(BaseDTO):
    code: int
    state: Optional[str] = None  # FIXME: check from enum


@dataclass
class CacheTokensDto(BaseDTO):
    user_id: UUID
    access_token: str
    refresh_token: str
    expired: int


@dataclass
class RefreshTokenDto(BaseDTO):
    client_id: str
    client_secret: str
    refresh_token: str
    grant_type: Literal["refresh_token"]


@dataclass
class RevokeTokenDto(BaseDTO):
    client_id: str
    client_secret: str
    access_token: str
