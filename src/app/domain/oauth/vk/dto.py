from dataclasses import dataclass
from typing import Literal

from domain.base.dto import BaseDTO


@dataclass
class AuthorizationUrlDto(BaseDTO):
    response_type: Literal["code"]
    client_id: str
    redirect_uri: str
    display: Literal["page", "popup", "mobile"]
    scope: Literal["email"]


@dataclass
class AccessTokenUrlDto(BaseDTO):
    client_id: str
    client_secret: str
    redirect_uri: str
    code: str


@dataclass
class UserInfoUrlDto(BaseDTO):
    access_token: str
    user_ids: int
    v: str = "5.131"
