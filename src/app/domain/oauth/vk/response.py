from pydantic import BaseModel, EmailStr


class VKOAuthResponseTokenSchema(BaseModel):
    access_token: str
    expires_in: int
    user_id: int
    email: EmailStr


class VKOAuthResponseUserInfoSchema(BaseModel):
    email: EmailStr
    first_name: str
    last_name: str
    id: str
