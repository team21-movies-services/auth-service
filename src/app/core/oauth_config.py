from pydantic.env_settings import BaseSettings
from pydantic.fields import Field


class YandexOAuth(BaseSettings):
    valid_keys: set = {'device_id', 'device_name', 'redirect_uri',
                       'login_hint', 'scope', 'optional_scope', 'force_confirm',
                       'state'}

    client_id: str = Field(env='YANDEX_CLIENT_ID')
    client_secret: str = Field(env='YANDEX_CLIENT_SECRET')


class OAuthConfig(BaseSettings):
    yandex: YandexOAuth = YandexOAuth()
