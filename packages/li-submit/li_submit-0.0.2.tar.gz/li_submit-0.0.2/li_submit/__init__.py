"""
li-submit: LiveInternet.ru site registration module.

A Python library for registering websites on liveinternet.ru with automatic captcha solving.
"""

from .li_submit import (
    LiveInternetRegistration,
    register_site,
    RegistrationResult,
    RegistrationResponse,
)
from .exceptions import (
    LiveInternetError,
    CaptchaError,
    RegistrationError,
    AntiCaptchaError,
)

__version__ = "0.0.1"
__author__ = "webii"
__email__ = "webii@pm.me"
__description__ = "LiveInternet.ru site registration with automatic captcha solving"

__all__ = [
    "LiveInternetRegistration",
    "register_site",
    "RegistrationResult",
    "RegistrationResponse",
    "LiveInternetError",
    "CaptchaError",
    "RegistrationError",
    "AntiCaptchaError",
]
