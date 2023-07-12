from enum import Enum
from typing import Literal

from dataclasses import dataclass
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
