"""
LiveInternet.ru site registration module.

This module provides functionality to register websites on liveinternet.ru
with automatic captcha solving using AntiCaptcha service.
"""

import sys
import time
import requests
from enum import Enum
from typing import Tuple, NamedTuple, Optional
from urllib.parse import urlparse
from tempfile import NamedTemporaryFile
from pyquery import PyQuery as pq
from anticaptchaofficial.imagecaptcha import imagecaptcha


class RegistrationResult(Enum):
    """Enumeration of possible registration results."""

    SUCCESS = 1
    ALREADY_REGISTERED = 2
    CAPTCHA_ERROR = 3
    REGISTRATION_ERROR = 4
    EXCEPTION_ERROR = 5


class RegistrationResponse(NamedTuple):
    """Structured response from registration attempt."""

    success: bool
    result: RegistrationResult
    message: str
    text: str


class LiveInternetRegistration:
    """Class for handling LiveInternet.ru site registration."""

    def __init__(self, anticaptcha_key: str, verbose: bool = False):
        """
        Initialize the registration client.

        Args:
            anticaptcha_key: API key for AntiCaptcha service
            verbose: Enable verbose output
        """
        self.anticaptcha_key = anticaptcha_key
        self.verbose = verbose
        self.session = self._get_session()

    def _get_session(self) -> requests.Session:
        """Create and configure requests session."""
        session = requests.Session()
        session.headers.update(
            {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
            }
        )
        return session

    def _vprint(self, message: str) -> None:
        """Print message if verbose mode is enabled."""
        if self.verbose:
            print(message)

    def _get_random_value(self) -> str:
        """Get random value from liveinternet.ru."""
        self._vprint("🔍 Getting random value...")

        try:
            response = self.session.get("https://www.liveinternet.ru/add")
            response.raise_for_status()

            doc = pq(response.text)
            random_value = doc('input[name="random"]').attr("value")

            if random_value:
                self._vprint(f"📊 Random value: {random_value}")
                return random_value
            else:
                # print(response.text)
                raise ValueError("Could not find random value in response")

        except requests.RequestException as e:
            raise ValueError(f"Failed to get random value: {e}")

    def _solve_captcha(self, captcha_url: str) -> str:
        """Solve the CAPTCHA from the provided URL.

        Args:
            captcha_url: URL of the CAPTCHA image

        Returns:
            Captcha text solution

        Raises:
            ValueError: If captcha solving fails
            requests.RequestException: If captcha image download fails
        """
        anticaptcha_key = self.anticaptcha_key

        self._vprint("📥 Downloading captcha image...")
        try:
            image_response = self.session.get(captcha_url, verify=False)
            image_response.raise_for_status()
        except requests.RequestException as e:
            raise requests.RequestException(f"Failed to download captcha image: {e}")

        # Use a temporary file for the solver
        with NamedTemporaryFile(mode="w+b", delete=False) as temp_file:
            temp_file.write(image_response.content)
            temp_file.flush()

            # Set up the captcha solver
            solver = imagecaptcha()
            solver.set_verbose(0)  # Disable anticaptcha verbose output
            solver.set_key(anticaptcha_key)

            self._vprint("🧩 Solving captcha...")

            captcha_text = solver.solve_and_return_solution(temp_file.name)

            if captcha_text == 0:
                raise ValueError(f"Failed to solve captcha: {solver.error_code}")

        self._vprint(f"🎯 Captcha solved: {captcha_text}")
        return captcha_text

    def register_site(
        self,
        url: str,
        email: str,
        password: str = "123123",
        retry_attempts: int = 1,
        debug: bool = False,
    ) -> RegistrationResponse:
        """
        Register a site on liveinternet.ru.

        Args:
            url: Website URL to register
            email: Email address
            password: Password (default: "123123")
            retry_attempts: Number of retry attempts for captcha errors (default: 1)
            debug: Whether to print debug information

        Returns:
            RegistrationResponse containing success status, result code, and message
        """
        # Normalize URL
        if not url.startswith("http"):
            url = f"https://{url}"

        parsed_url = urlparse(url)
        site_name = parsed_url.netloc

        self._vprint(f"🚀 Registering site: {url}")
        self._vprint(f"📝 Site name: {site_name}, email: {email}")

        # Retry logic for captcha errors
        for attempt in range(retry_attempts + 1):
            if attempt > 0:
                self._vprint(f"🔄 Retry attempt {attempt}...")
                time.sleep(2)  # Brief delay between attempts

            try:
                # Get random value
                random_value = self._get_random_value()

                # Solve captcha
                captcha_url = f"http://captcha.li.ru/image?id={random_value}&lang=dig"
                captcha_value = self._solve_captcha(captcha_url)

                # Prepare registration data
                data = {
                    "url": url,
                    "email": email,
                    "password": password,
                    "check": password,
                    "rules": "agreed",
                    "www": "",
                    "type": "site",
                    "random": random_value,
                    "captcha_id": random_value,
                    "captcha": captcha_value,
                    "aliases": "",
                    "name": site_name,
                    "lang": "ru",
                    "group": "",
                    "private": "",
                }

                self._vprint("📤 Submitting registration...")

                response = self.session.post(
                    "https://www.liveinternet.ru/add", data=data
                )
                response.raise_for_status()

                self._vprint(
                    f"📬 Registration request sent. Status code: {response.status_code}"
                )

                # Check response content for different outcomes
                response_text = response.text.lower()

                if "успешно зарегистрирован" in response_text:
                    self._vprint("✅ Site registered successfully!")
                    return RegistrationResponse(
                        success=True,
                        result=RegistrationResult.SUCCESS,
                        message="Site registered successfully",
                        text="",
                    )
                elif "сайт с таким адресом уже зарегистрирован" in response_text:
                    return RegistrationResponse(
                        success=False,
                        result=RegistrationResult.ALREADY_REGISTERED,
                        message="Site with this URL is already registered",
                        text="",
                    )
                elif "ошибка: неверный код с картинки" in response_text:
                    if attempt < retry_attempts:
                        self._vprint("🔄 Captcha error, retrying...")
                        continue
                    return RegistrationResponse(
                        success=False,
                        result=RegistrationResult.CAPTCHA_ERROR,
                        message="Invalid captcha code",
                        text="",
                    )
                else:
                    self._vprint("Some error occured")
                    if debug:
                        print("📋 Response content:")
                        print(response.text)
                    return RegistrationResponse(
                        success=False,
                        result=RegistrationResult.REGISTRATION_ERROR,
                        message="Registration failed - unknown error",
                    )

            except (ValueError, requests.RequestException) as e:
                error_msg = f"Error during registration: {e}"
                if debug:
                    print(f"💥 {error_msg}", file=sys.stderr)
                return RegistrationResponse(
                    success=False,
                    result=RegistrationResult.EXCEPTION_ERROR,
                    message=error_msg,
                )

        try:
            text = response.text
        except AttributeError:
            text = ""
        return RegistrationResponse(
            success=False,
            result=RegistrationResult.CAPTCHA_ERROR,
            message="All retry attempts failed",
            text=text,
        )


# Convenience function for simple usage
def register_site(
    url: str,
    email: str,
    anticaptcha_key: str,
    password: str = "123123",
    retry_attempts: int = 1,
    verbose: bool = False,
    debug: bool = False,
) -> RegistrationResponse:
    """
    Register a site on liveinternet.ru.

    This is a convenience function that creates a LiveInternetRegistration instance
    and calls the register_site method.

    Args:
        url: Website URL to register
        email: Email address
        anticaptcha_key: API key for AntiCaptcha service
        password: Password (default: "123123")
        retry_attempts: Number of retry attempts for captcha errors (default: 1)
        verbose: Enable verbose output
        debug: Whether to print debug information

    Returns:
        RegistrationResponse containing success status, result code, and message

    Example:
        >>> from liveinternet_registration import register_site
        >>> result = register_site("example.com", "user@example.com", "your_anticaptcha_key")
        >>> if result.success:
        ...     print("Registration successful!")
        ... else:
        ...     print(f"Registration failed: {result.message}")
    """
    client = LiveInternetRegistration(anticaptcha_key, verbose)
    return client.register_site(url, email, password, retry_attempts, debug)


# Example usage
if __name__ == "__main__":
    # Example of how to use the module
    import argparse

    parser = argparse.ArgumentParser(
        description="Register a website on liveinternet.ru"
    )
    parser.add_argument("url", help="Website URL to register")
    parser.add_argument("email", help="Email address for registration")
    parser.add_argument("anticaptcha_key", help="AntiCaptcha API key")
    parser.add_argument(
        "--password", default="123123", help="Password for registration"
    )
    parser.add_argument("--retry", type=int, default=1, help="Number of retry attempts")
    parser.add_argument(
        "--verbose", "-v", action="store_true", help="Enable verbose output"
    )
    parser.add_argument("--debug", action="store_true", help="Enable debug output")

    args = parser.parse_args()

    result = register_site(
        url=args.url,
        email=args.email,
        anticaptcha_key=args.anticaptcha_key,
        password=args.password,
        retry_attempts=args.retry,
        verbose=args.verbose,
        debug=args.debug,
    )

    if result.success:
        print("🎉 Registration completed successfully!")
        sys.exit(0)
    elif result.result == RegistrationResult.ALREADY_REGISTERED:
        print("ℹ️  Site is already registered")
        sys.exit(0)
    else:
        print(f"😞 Registration failed: {result.message}")
        sys.exit(1)
