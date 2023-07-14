from dataclasses import dataclass

from domain.base.dto import BaseDTO
from domain.oauth.google.response import GoogleOAuthResponseUserInfoSchema
from domain.oauth.vk.response import VKOAuthResponseUserInfoSchema
from domain.oauth.yandex.response import OAuthResponseTokenSchema, OAuthUserInfoSchema


@dataclass
class OAuthUserInfoDto(BaseDTO):
    email: str
    first_name: str
    last_name: str

    @classmethod
    def from_yandex_response(
        cls,
        response: OAuthUserInfoSchema,
    ) -> "OAuthUserInfoDto":
        return OAuthUserInfoDto(
            email=response.emails[0],
            first_name=response.first_name,
            last_name=response.last_name,
        )

    @classmethod
    def from_vk_response(
        cls,
        response: VKOAuthResponseUserInfoSchema,
    ) -> "OAuthUserInfoDto":
        if not response.first_name:
            response.first_name = ""
        if not response.last_name:
            response.last_name = ""

        return OAuthUserInfoDto(
            email=response.email,
            first_name=response.first_name,
            last_name=response.last_name,
        )

    @classmethod
    def from_google_response(
        cls,
        response: GoogleOAuthResponseUserInfoSchema,
    ) -> "OAuthUserInfoDto":
        return OAuthUserInfoDto(
            email=response.email,
            first_name=response.given_name,
            last_name=response.family_name,
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
