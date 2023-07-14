from pydantic.env_settings import BaseSettings
from pydantic.fields import Field


class YandexOAuthConfig(BaseSettings):
    valid_keys: set = {
        "device_id",
        "device_name",
        "redirect_uri",
        "login_hint",
        "scope",
        "optional_scope",
        "force_confirm",
        "state",
    }

    client_id: str = Field(default='', env="YANDEX_CLIENT_ID")
    client_secret: str = Field(default='', env="YANDEX_CLIENT_SECRET")


class VKOAuthConfig(BaseSettings):
    client_id: str = Field(default='', env="VK_CLIENT_ID")
    client_secret: str = Field(default='', env="VK_CLIENT_SECRET")


class OAuthConfig(BaseSettings):
    yandex: YandexOAuthConfig = YandexOAuthConfig()
    vk: VKOAuthConfig = VKOAuthConfig()
