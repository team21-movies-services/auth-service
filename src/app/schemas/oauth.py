from typing import List, Optional

from pydantic.class_validators import validator
from pydantic.main import BaseModel


class OAuthTokens(BaseModel):
    token_type: str
    access_token: str
    expires_in: int
    refresh_token: str
    scope: Optional[List[str]]

    @validator('scope')
    def scope_validator(cls, val):
        if isinstance(val, str):
            return val.split()
        return val


class ResponseStatus(BaseModel):
    status: str


class OAuthTokensError(BaseModel):
    error_description: str
    error: str

    def log_error(self):
        return f'{self.error} - {self.error_description}'


class OAuthCodeRequestSchema(BaseModel):
    code: Optional[int]
    state: Optional[str]
    error: Optional[str]
    error_description: Optional[str]


class OAuthUserInfoSchema(BaseModel):
    email: str
    first_name: str
    last_name: str

    @classmethod
    def from_yandex(cls, data: dict):
        return cls(
            email=data.get('default_email', ''),
            first_name=data.get('first_name', ''),
            last_name=data.get('last_name', ''),
        )


class VKOAuthCodeRequestSchema(BaseModel):
    code: str
    error: Optional[str]
    error_description: Optional[str]
