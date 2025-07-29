"""Trimergo API client for interacting with the Trimergo HR system.

This module provides a client for making authenticated requests to the Trimergo API,
handling authentication, retries, and session management.
"""

# Standard library imports
import base64
from typing import Optional, Tuple, Any

# Third-party imports
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# Local imports
from brynq_sdk_brynq import BrynQ
from .timesheet import Timesheet

class Trimergo(BrynQ):
    """Client for interacting with the Trimergo HR system API.

    Handles authentication, session management, and provides methods for
    accessing various Trimergo API services like Timesheet.

    Attributes:
        trimergo_host (str): The base URL for the Trimergo API.
        trimergo_session (requests.Session): The authenticated session for API requests.
        openapi_json (dict): The OpenAPI specification for the Trimergo API.
        timesheet (Timesheet): An instance of the Timesheet service client.
        OPENAPI_VERSION (str): Expected OpenAPI version.
        TRIMERGO_T2_WEBSERVICES_VERSION (str): Expected Trimergo T2 WebServices version.
    """

    OPENAPI_VERSION: str = "3.0.1"
    TRIMERGO_T2_WEBSERVICES_VERSION: str = "1.1.0"

    def __init__(
        self,
        interface_id: str,
        test_environment: bool,
        system_type: str
    ) -> None:
        """Initializes the Trimergo API client.

        Retrieves credentials, initializes an authenticated session, and
        sets up service-specific clients.

        Args:
            interface_id (str): ID of the interface to get credentials for.
            test_environment (bool): True if using the test environment, False otherwise.
            system_type (str): Specifies 'source' or 'target' system.
        """
        super().__init__()
        # Retrieve trimergo's host (base url) and credentials
        self.trimergo_host: str
        trimergo_username: str
        trimergo_password: str
        self.trimergo_host, trimergo_username, trimergo_password = (
            self._get_trimergo_credentials(
                interface_id, test_environment, system_type
            )
        )
        # Init trimergo session and retrieve openapi json
        self.trimergo_session: requests.Session
        self.openapi_json: dict
        self.trimergo_session, self.openapi_json = self._init_trimergo_session(
            trimergo_username, trimergo_password
        )
        # Init service classes
        self.timesheet: Timesheet = Timesheet(self)

    def _get_trimergo_credentials(
        self,
        interface_id: str = "1",
        test_environment: bool = False,
        system_type: Optional[str] = None,
    ) -> Tuple[str, str, str]:
        """Retrieves Trimergo API credentials from BrynQ's interface system.

        Args:
            interface_id (str): ID of the interface.
            test_environment (bool): True if using the test environment.
            system_type (Optional[str]): 'source' or 'target'.

        Returns:
            Tuple[str, str, str]: host, username, password.

        Raises:
            ValueError: If any required credentials (host, username, password) are missing.
            Exception: If credential retrieval fails for other reasons.
        """
        try:
            creds =  self.interfaces.credentials.get(
                system="trimergo",
                system_type=system_type,
            )

            if not creds or not creds.get("data"):
                raise Exception(
                    f"Failed to retrieve credentials for interface_id {interface_id}. "
                    f"Response: {creds}"
                )

            data = creds["data"]
            host = data.get("host")
            username = data.get("username")
            password = data.get("password")

            missing_fields = []
            if not host or not host.strip():
                missing_fields.append("host")
            if not username or not username.strip():
                missing_fields.append("username")
            if not password or not password.strip():
                missing_fields.append("password")

            if missing_fields:
                error_message = f"Missing Trimergo credentials: {', '.join(missing_fields)}."
                raise ValueError(error_message)

            return str(host), str(username), str(password)
        except ValueError:
            raise
        except Exception as e:
            error_message = (
                f"An unexpected error occurred while retrieving Trimergo credentials "
                f"for interface_id {interface_id}: {e}"
            )
            raise Exception(error_message) from e

    def _init_trimergo_session(
        self, trimergo_username: str, trimergo_password: str
    ) -> Tuple[requests.Session, dict]:
        """Initializes and returns an authenticated Trimergo API session and OpenAPI spec.

        Args:
            trimergo_username (str): Username for Trimergo API.
            trimergo_password (str): Password for Trimergo API.

        Returns:
            Tuple[requests.Session, dict]: Authenticated session and OpenAPI JSON.

        Raises:
            Exception: If session initialization or version check fails.
        """
        try:
            retry_strategy = Retry(
                total=3,
                backoff_factor=1,
                status_forcelist=[500, 502, 503, 504, 400, 401, 403, 404],
                allowed_methods=["HEAD", "GET", "PUT", "DELETE", "OPTIONS", "TRACE", "POST"],
            )
            trimergo_session = requests.Session()
            adapter = HTTPAdapter(max_retries=retry_strategy)
            trimergo_session.mount("http://", adapter)
            trimergo_session.mount("https://", adapter)
            auth_string = f"{trimergo_username}:{trimergo_password}"
            auth_b64 = self._encode_string(auth_string)
            trimergo_session.headers.update({
                "Authorization": f"Basic {auth_b64}",
                "Content-Type": "application/json",
            })

            openapi_url = f"{self.trimergo_host}/tri-server-gateway-ws/api/rest/openapi.json"
            response = trimergo_session.get(openapi_url)
            response.raise_for_status()

            openapi_json: dict = response.json()

            api_openapi_version = openapi_json.get("openapi")
            api_info_version = openapi_json.get("info", {}).get("version")

            if api_openapi_version != self.OPENAPI_VERSION or \
               api_info_version != self.TRIMERGO_T2_WEBSERVICES_VERSION:
                warning_msg = (
                    f"Version mismatch detected for Trimergo API. "
                    f"Expected OpenAPI: {self.OPENAPI_VERSION} (Got: {api_openapi_version}), "
                    f"Expected T2 WebServices: {self.TRIMERGO_T2_WEBSERVICES_VERSION} "
                    f"(Got: {api_info_version}). API might not be compatible."
                )
                print(f"WARNING: {warning_msg}")

            return trimergo_session, openapi_json
        except requests.exceptions.HTTPError as http_err:
            err_msg = (
                f"HTTP error during Trimergo session initialization for {openapi_url}: "
                f"{http_err.response.status_code} - {http_err.response.text}"
            )
            raise Exception(err_msg) from http_err
        except requests.exceptions.RequestException as req_err:
            err_msg = f"Request error initializing Trimergo session for {openapi_url}: {req_err}"
            raise Exception(err_msg) from req_err
        except Exception as e:
            err_msg = (
                f"Unexpected error during Trimergo session initialization for {openapi_url}: {e}"
            )
            raise Exception(err_msg) from e

    def _encode_string(self, string_to_encode: str) -> str:
        """Encodes a string to Base64 for Trimergo API authentication headers.

        Args:
            string_to_encode (str): The string to be Base64 encoded.

        Returns:
            str: The Base64 encoded string.
        """
        string_bytes = string_to_encode.encode('utf-8')
        string_b64_bytes = base64.b64encode(string_bytes)
        return string_b64_bytes.decode('utf-8')
