import uuid

from pydantic.main import BaseModel


class SocialAccountResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    user_social_id: str
    social_name: str

    class Config:
        orm_mode = True
