from pydantic import BaseModel, EmailStr


class OAuthResponseTokenSchema(BaseModel):
    access_token: str
    expires_in: int
    user_id: int
    email: EmailStr
