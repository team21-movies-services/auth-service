from common.exceptions.base import AppException


class AuthException(AppException):
    """Base Token Exception"""


class OAuthException(AuthException):
    """Base OAuthToken Exception"""


class TokenException(AuthException):
    """Base Token Exception"""


class TokenEncodeException(TokenException):
    """Token Encode Exception"""


class TokenDecodeException(TokenException):
    """Token Decode Exception"""


class TokenExpiredException(AuthException):
    """Token Expired Exception"""
