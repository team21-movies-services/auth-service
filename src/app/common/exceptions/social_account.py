from common.exceptions.base import AppException


class SocialAccountException(AppException):
    """Base Social Account Exception"""


class SocialAccountAlreadyExists(SocialAccountException):
    """Social Account Already Exists"""
