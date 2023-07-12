from typing import Optional
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
