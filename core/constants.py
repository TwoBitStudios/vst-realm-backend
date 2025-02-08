from enum import Enum

from core.settings import settings


class Provider(str, Enum):
    LOCAL = settings.LOCAL_PROVIDER_NAME
    GOOGLE = 'google'
