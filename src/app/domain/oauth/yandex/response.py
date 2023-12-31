from pydantic import BaseModel


class OAuthResponseTokenSchema(BaseModel):
    token_type: str
    access_token: str
    expires_in: int
    refresh_token: str


class OAuthUserInfoSchema(BaseModel):
    id: int
    first_name: str
    last_name: str
    emails: list[str]


class OAuthResponseRefreshSchema(BaseModel):
    access_token: str
    expires_in: int
    token_type: str
    refresh_token: str
