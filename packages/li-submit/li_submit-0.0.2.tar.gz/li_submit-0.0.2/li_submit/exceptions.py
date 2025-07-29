"""Custom exceptions for li-submit module."""


class LiveInternetError(Exception):
    """Base exception for LiveInternet registration errors."""

    pass


class CaptchaError(LiveInternetError):
    """Exception raised when captcha solving fails."""

    pass


class RegistrationError(LiveInternetError):
    """Exception raised when registration fails."""

    pass


class AntiCaptchaError(LiveInternetError):
    """Exception raised when AntiCaptcha API fails."""

    pass
