from pydantic import BaseModel, EmailStr


class GoogleOAuthResponseTokenSchema(BaseModel):
    access_token: str
    refresh_token: str
    expires_in: int
    id_token: str
    scope: str
    token_type: str


class GoogleOAuthResponseRefreshSchema(BaseModel):
    access_token: str
    expires_in: int
    scope: str
    token_type: str
    refresh_token: str | None


class GoogleOAuthResponseUserInfoSchema(BaseModel):
    email: EmailStr
    given_name: str | None
    family_name: str | None
    name: str | None


class GoogleOAuthPairTokensResponseSchema(BaseModel):
    access_token: str
    refresh_token: str
