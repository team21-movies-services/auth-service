from typing import Optional

from pydantic.main import BaseModel


class RoleRequest(BaseModel):
    name: str
    description: Optional[str]
