from typing import Literal

from dataclasses import dataclass
from domain.base.dto import BaseDTO


@dataclass
class AuthorizationUrlDto(BaseDTO):
    response_type: Literal["code"]
    client_id: str
    redirect_uri: str
    scope: Literal["openid email"]
    access_type: Literal["offline", "online"]


@dataclass
class AccessTokenUrlDto(BaseDTO):
    client_id: str
    client_secret: str
    redirect_uri: str
    code: str
    grant_type: Literal["authorization_code"]


@dataclass
class UserInfoUrlDto(BaseDTO):
    access_token: str
    user_ids: int
    v: str = "5.131"
