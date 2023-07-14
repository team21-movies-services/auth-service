from pydantic import BaseModel


class OAuthRequestBaseSchema(BaseModel):
    client_id: str
    client_secret: str


class OAuthRequestTokenSchema(OAuthRequestBaseSchema):
    code: int
    grant_type: str
