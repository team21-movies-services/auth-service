from pydantic.env_settings import BaseSettings
from pydantic.fields import Field


class YandexOAuthConfig(BaseSettings):
    client_id: str = Field(default='', env="YANDEX_CLIENT_ID")
    client_secret: str = Field(default='', env="YANDEX_CLIENT_SECRET")
    access_token_cache_key: str = "oauth-yandex-access-token-{user_id}"
    refresh_token_cache_key: str = "oauth-yandex-refresh-token-{user_id}"


class VKOAuthConfig(BaseSettings):
    client_id: str = Field(default='', env="VK_CLIENT_ID")
    client_secret: str = Field(default='', env="VK_CLIENT_SECRET")


class GoogleOAuthConfig(BaseSettings):
    client_id: str = Field(default='', env="GOOGLE_CLIENT_ID")
    client_secret: str = Field(default='', env="GOOGLE_CLIENT_SECRET")
    access_token_cache_key: str = "oauth-google-access-token-{user_id}"
    refresh_token_cache_key: str = "oauth-google-refresh-token-{user_id}"


class OAuthConfig(BaseSettings):
    yandex: YandexOAuthConfig = YandexOAuthConfig()
    vk: VKOAuthConfig = VKOAuthConfig()
    google: GoogleOAuthConfig = GoogleOAuthConfig()
