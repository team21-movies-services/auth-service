from enum import Enum


class YandexOAuthEndpointEnum(str, Enum):
    authorization_endpoint = "https://oauth.yandex.ru/authorize"
    token_endpoint = "https://oauth.yandex.ru/token"
    token_revoke = "https://oauth.yandex.ru/revoke_token"
    user_info = "https://login.yandex.ru/info"
