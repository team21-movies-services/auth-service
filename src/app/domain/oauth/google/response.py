from pydantic import BaseModel, EmailStr


class GoogleOAuthResponseTokenSchema(BaseModel):
    access_token: str
    refresh_token: str
    expires_in: int
    id_token: str
    scope: str
    token_type: str


class GoogleOAuthResponseUserInfoSchema(BaseModel):
    email: EmailStr
    given_name: str | None
    family_name: str | None
    name: str | None
