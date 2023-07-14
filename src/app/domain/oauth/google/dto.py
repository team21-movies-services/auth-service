from typing import Literal

from dataclasses import dataclass
from domain.base.dto import BaseDTO


@dataclass
class AuthorizationUrlDto(BaseDTO):
    response_type: Literal["code"]
    client_id: str
    redirect_uri: str
    scope: Literal["openid email profile"]
    access_type: Literal["offline", "online"]


@dataclass
class AccessTokenDto(BaseDTO):
    client_id: str
    client_secret: str
    redirect_uri: str
    code: str
    grant_type: Literal["authorization_code"]


@dataclass
class RefreshTokenDto(BaseDTO):
    client_id: str
    client_secret: str
    refresh_token: str
    grant_type: Literal["refresh_token"]


@dataclass
class RevokeTokenUrlDto(BaseDTO):
    token: str
