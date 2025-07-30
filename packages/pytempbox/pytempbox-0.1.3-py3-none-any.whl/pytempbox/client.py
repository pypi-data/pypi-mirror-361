import requests
import time
from typing import List, Dict, Optional
from .exceptions import PyTempBoxException

class PyTempBox:
    """
    A Python client for temporary email services.

    Provides functionality to generate temporary email addresses and retrieve messages.

    Example:
        >>> from pytempbox import PyTempBox
        >>> client = PyTempBox()
        >>> email = client.generate_email()
        >>> messages = client.get_messages(email)
    """

    BASE_URL = "https://api.internal.temp-mail.io/api/v3"
    DEFAULT_TIMEOUT = 30  # seconds

    def __init__(self, request_timeout: int = DEFAULT_TIMEOUT):
        """
        Initialize the PyTempBox client.

        Args:
            request_timeout: Timeout in seconds for API requests. Defaults to 30.
        """
        self.session = requests.Session()
        self.timeout = request_timeout

    def get_available_domains(self) -> List[str]:
        """Retrieve list of available email domains.

        Returns:
            List of available domain strings.

        Raises:
            PyTempBoxException: If the request fails.
        """
        try:
            response = self.session.get(
                f"{self.BASE_URL}/domains",
                timeout=self.timeout
            )
            response.raise_for_status()
            return [domain["name"] for domain in response.json()["domains"]]
        except Exception as e:
            raise PyTempBoxException(f"Failed to get domains: {str(e)}")

    def generate_email(self, min_length: int = 10, max_length: int = 15, domain: Optional[str] = None) -> str:
        """Generate a new temporary email address.

        Args:
            min_length: Minimum length for the email name part. Defaults to 10.
            max_length: Maximum length for the email name part. Defaults to 15.
            domain: Optional specific domain to use. Defaults to random available domain.

        Returns:
            Generated email address string.

        Raises:
            PyTempBoxException: If email generation fails.
        """
        try:
            payload = {
                "min_name_length": min_length,
                "max_name_length": max_length
            }
            if domain:
                payload["domain"] = domain

            response = self.session.post(
                f"{self.BASE_URL}/email/new",
                json=payload,
                timeout=self.timeout
            )
            response.raise_for_status()
            return response.json()["email"]
        except Exception as e:
            raise PyTempBoxException(f"Failed to generate email: {str(e)}")

    def get_messages(self, email: str, timeout: int = 300, interval: int = 10) -> List[Dict]:
        """Retrieve messages for the given email address.

        Args:
            email: Email address to check for messages.
            timeout: Maximum time to wait for messages in seconds. Defaults to 300.
            interval: Interval between checks in seconds. Defaults to 10.

        Returns:
            List of message dictionaries.

        Raises:
            PyTempBoxException: If message retrieval fails.
        """
        start_time = time.time()

        while (time.time() - start_time) < timeout:
            try:
                response = self.session.get(
                    f"{self.BASE_URL}/email/{email}/messages",
                    timeout=self.timeout
                )
                response.raise_for_status()

                messages = response.json()
                if messages:
                    return messages

                time.sleep(interval)
            except Exception as e:
                raise PyTempBoxException(f"Failed to get messages: {str(e)}")
        return []

    def get_message_content(self, email: str, message_id: str) -> Dict:
        """Retrieve full content of a specific message.

        Args:
            email: Email address the message was sent to.
            message_id: ID of the message to retrieve.

        Returns:
            Dictionary containing full message content.

        Raises:
            PyTempBoxException: If message content retrieval fails.
        """
        try:
            response = self.session.get(
                f"{self.BASE_URL}/email/{email}/messages/{message_id}",
                timeout=self.timeout
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            raise PyTempBoxException(f"Failed to get message content: {str(e)}")
