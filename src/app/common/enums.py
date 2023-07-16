from enum import Enum


class RateLimitPeriodEnum(str, Enum):
    seconds = "s"
    hours = "h"
    minutes = "m"
    days = "d"

    @classmethod
    def _missing_(cls, value):
        return cls.hours


class SocialNameEnum(str, Enum):
    GOOGLE = "google"
    VK = "vk"
    YANDEX = "yandex"
