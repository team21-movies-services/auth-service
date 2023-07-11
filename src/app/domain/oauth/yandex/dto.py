from uuid import UUID

from dataclasses import dataclass
from domain.base.dto import BaseDTO


@dataclass
class AuthorizationUrlDto(BaseDTO):
    response_type: str  # FIXME: check from enum
    client_id: str
    redirect_uri: str
    device_id: UUID
