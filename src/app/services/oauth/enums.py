from enum import Enum


class YandexOAuthEndpointEnum(str, Enum):
    authorization_endpoint = "https://oauth.yandex.ru/authorize"
    token_endpoint = "https://oauth.yandex.ru/token"
    token_revoke = "https://oauth.yandex.ru/revoke_token"
    user_info = "https://login.yandex.ru/info"


class VKOAuthEndpointEnum(str, Enum):
    authorization_endpoint = "https://oauth.vk.com/authorize"
    token_endpoint = "https://oauth.vk.com/access_token"
    user_info = "https://api.vk.com/method/users.get"
    # token_revoke = "https://oauth.yandex.ru/revoke_token"


class GoogleOAuthEndpointEnum(str, Enum):
    authorization_endpoint = "https://accounts.google.com/o/oauth2/v2/auth"
    token_endpoint = "https://oauth2.googleapis.com/token"
