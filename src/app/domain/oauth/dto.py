from dataclasses import dataclass
from domain.base.dto import BaseDTO
from domain.oauth.yandex.response import OAuthUserInfoSchema, OAuthResponseTokenSchema


@dataclass
class OAuthUserInfoDto(BaseDTO):
    email: str
    first_name: str
    last_name: str

    @classmethod
    def from_yandex_response(
        cls,
        response: OAuthUserInfoSchema
    ) -> "OAuthUserInfoDto":
        return OAuthUserInfoDto(
            email=response.emails[0],
            first_name=response.first_name,
            last_name=response.last_name,
        )


@dataclass
class OAuthTokenDto(BaseDTO):
    access_token: str
    refresh_token: str
    expires_in: int

    @classmethod
    def from_yandex_response(
        cls,
        response: OAuthResponseTokenSchema,
    ) -> "OAuthTokenDto":
        return OAuthTokenDto(
            access_token=response.access_token,
            refresh_token=response.refresh_token,
            expires_in=response.expires_in,
        )
