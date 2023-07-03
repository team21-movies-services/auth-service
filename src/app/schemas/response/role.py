import uuid

from pydantic.main import BaseModel


class RoleResponse(BaseModel):
    id: uuid.UUID
    name: str
    description: str

    class Config:
        orm_mode = True
