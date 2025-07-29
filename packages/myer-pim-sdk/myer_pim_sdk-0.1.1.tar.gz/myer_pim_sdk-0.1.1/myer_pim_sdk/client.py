import httpx
import asyncio
import time
import base64
import logging
from typing import Optional, Any, Dict, Union
from urllib.parse import urlparse

from .exceptions import (
    AkeneoAPIError, 
    AuthenticationError, 
    create_exception_from_response
)
from . import utils
from .resources import (
    Product,
    ProductModel,
    Family,
    FamilyVariant,
    Attribute,
    AttributeOption,
    AttributeGroup,
    AssociationType,
    Category,
    MediaFile,
    System
)
from .throttler import throttler, async_throttler

logger = logging.getLogger(__name__)

DEFAULT_TOKEN_BUFFER_SECONDS = 300  # Refresh token 5 minutes before expiry
DEFAULT_BASE_URL = "https://your-pim.akeneo.com"  # Default, should be overridden


class BaseAkeneoClient:
    def __init__(
        self,
        *,
        client_id: str,
        client_secret: str,
        username: str,
        password: str,
        base_url: str = DEFAULT_BASE_URL,
        timeout: float = 60.0,
        token_buffer_seconds: int = DEFAULT_TOKEN_BUFFER_SECONDS,
        max_retries: int = 5,
    ):
        if not all([client_id, client_secret, base_url]):
            raise ValueError("client_id, client_secret, and base_url are required.")

        self.client_id = client_id
        self.client_secret = client_secret
        self.username = username
        self.password = password
        self.base_url = base_url.rstrip('/')
        
        self.token_url = f"{self.base_url}/api/oauth/v1/token"
        
        self.timeout = timeout
        self.token_buffer_seconds = token_buffer_seconds
        self.max_retries = max_retries
        self.utils = utils  # Make utils accessible

        self._access_token: Optional[str] = None
        self._token_expires_at: float = 0.0

        self._client: Optional[Union[httpx.Client, httpx.AsyncClient]] = None  # To be defined in subclasses

        # Initialize resource classes
        self._initialize_resources()

    def _initialize_resources(self):
        """Initialize resource classes."""
        self.products = Product(client=self)
        self.product_models = ProductModel(client=self)
        self.families = Family(client=self)
        self.family_variants = FamilyVariant(client=self)
        self.attributes = Attribute(client=self)
        self.attribute_options = AttributeOption(client=self)
        self.attribute_groups = AttributeGroup(client=self)
        self.association_types = AssociationType(client=self)
        self.categories = Category(client=self)
        self.media_files = MediaFile(client=self)
        self.system = System(client=self)

    def _get_basic_auth_header(self) -> str:
        """Generate Basic Auth header for OAuth2 token request."""
        auth_str = f"{self.client_id}:{self.client_secret}"
        return "Basic " + base64.b64encode(auth_str.encode("utf-8")).decode("utf-8")

    def _is_token_expired(self) -> bool:
        """Check if the current token is expired or about to expire."""
        return not self._access_token or time.time() >= (self._token_expires_at - self.token_buffer_seconds)

    def _handle_error_response(self, response: httpx.Response, method: str, url: str, **kwargs):
        """Centralized error handling."""
        logger.error(
            f"Akeneo API Error: {response.status_code} on {method} {url}. "
            f"Response: {response.content[:500] if response.content else 'No content'}"
        )
        
        # When tokens expire, force a refresh
        if response.status_code == 401:
            self._access_token = None  # Force token refresh on next attempt
            
        # Use our generic exception creation helper
        raise create_exception_from_response(response, method, url, **kwargs)


class AkeneoClient(BaseAkeneoClient):
    """Synchronous Akeneo API client."""
    
    def __init__(self, *args, **kwargs):
        self._client = None  # Initialize to avoid type checking errors before super().__init__
        super().__init__(*args, **kwargs)
        self._client = httpx.Client(base_url=self.base_url, timeout=self.timeout)

    def _fetch_new_token_sync(self) -> None:
        """Fetch a new OAuth2 access token."""
        headers = {"Authorization": self._get_basic_auth_header()}
        
        # Really struggling to understand why tf these guys have set up auth like this.....
        data = {
            "grant_type": "password",
            "username": self.username,
            "password": self.password,
        }
        
        logger.info(f"Fetching new OAuth2 token from {self.token_url}")
        try:
            # Use a separate client for token fetching to avoid circular dependencies
            with httpx.Client(timeout=self.timeout) as token_client:
                response = token_client.post(self.token_url, headers=headers, data=data)
            response.raise_for_status()
            token_data = response.json()
            self._access_token = token_data["access_token"]
            self._token_expires_at = time.time() + token_data["expires_in"]
            logger.info("Successfully fetched new OAuth2 token.")
        except httpx.HTTPStatusError as e:
            logger.error(f"Failed to fetch OAuth2 token: {e.response.status_code} - {e.response.text}")
            self._access_token = None  # Ensure token is cleared on failure
            raise AuthenticationError(
                message=f"Failed to fetch OAuth2 token: {e.response.text}",
                response=e.response
            )
        except Exception as e:
            logger.error(f"An unexpected error occurred while fetching OAuth2 token: {e}")
            self._access_token = None
            # Create a dummy response for error creation
            dummy_response = httpx.Response(500, request=httpx.Request("POST", self.token_url))
            raise AuthenticationError(
                message=f"Unexpected error fetching token: {str(e)}",
                response=dummy_response
            )

    def _ensure_token_valid_sync(self) -> None:
        """Ensure we have a valid access token."""
        if self._is_token_expired():
            self._fetch_new_token_sync()

    @throttler.throttle()
    def _make_request_sync(
        self,
        method: str,
        path: str,
        params: Optional[Dict[str, Any]] = None,
        json_data: Optional[Dict[str, Any]] = None,
        form_data: Optional[Dict[str, Any]] = None,
        files: Optional[Dict[str, Any]] = None,
    ) -> Any:
        """Make a synchronous HTTP request to the Akeneo API."""
        
        if not isinstance(self._client, httpx.Client):
            raise TypeError("HTTP client must be an instance of httpx.Client")
        
        self._ensure_token_valid_sync()
        
        headers = {
            "Authorization": f"Bearer {self._access_token}",
            "Accept": "application/json",
        }
        
        params = utils.clean_params(params) if params else {}
        
        # Ensure path starts with /
        if not path.startswith('/'):
            path = '/' + path
        
        retries = self.max_retries
        while True:
            try:
                response = self._client.request(
                    method,
                    path,
                    params=params,
                    json=json_data,
                    data=form_data,
                    files=files,
                    headers=headers,
                )
            
                if 200 <= response.status_code < 300:
                    if response.content:
                        try:
                            return response.json()
                        except ValueError:
                            # Response is not JSON, return text
                            return response.text
                    return {}  # For 204 No Content
                
                retry_after_header = response.headers.get("Retry-After")
                should_retry_rate_limit = response.status_code == 429 and retry_after_header and retry_after_header.isdigit()
                should_retry_maintenance = response.status_code == 503 and retry_after_header and retry_after_header.isdigit()
                
                if (should_retry_rate_limit or should_retry_maintenance) and retries > 0:
                    wait_time = int(retry_after_header)  # type: ignore
                    logger.warning(f"Status {response.status_code}, retrying after {wait_time}s. Retries left: {retries-1}")
                    time.sleep(wait_time)
                    retries -= 1
                    self._ensure_token_valid_sync()  # Re-check token before retry
                    headers["Authorization"] = f"Bearer {self._access_token}"  # Re-apply token
                    continue

                self._handle_error_response(response, method, path, params=params, json=json_data, data=form_data)
                return {}  # Should not be reached due to raise in _handle_error_response

            except AkeneoAPIError as e:
                if hasattr(e, 'retry_after') and getattr(e, 'retry_after') and isinstance(e.retry_after, (int, float)) and retries > 0:
                    logger.warning(f"Caught {type(e).__name__}, retrying after {e.retry_after}s. Retries left: {retries-1}")
                    time.sleep(e.retry_after)
                    retries -= 1
                    self._ensure_token_valid_sync()
                    headers["Authorization"] = f"Bearer {self._access_token}"
                    continue
                raise  # Reraise if no retry_after or no retries left
            except httpx.RequestError as e:  # Network errors
                if retries > 0:
                    logger.warning(f"Network error: {e}. Retrying in 3s. Retries left: {retries-1}")
                    time.sleep(3)
                    retries -= 1
                    continue
                # Create a dummy response for network errors
                dummy_response = httpx.Response(500, request=httpx.Request(method, self.base_url + path))
                raise AkeneoAPIError(
                    message=f"Network request failed: {str(e)}",
                    response=dummy_response
                )

    def close(self):
        """Close the HTTP client."""
        if self._client and isinstance(self._client, httpx.Client):
            self._client.close()


class AkeneoAsyncClient(BaseAkeneoClient):
    """Asynchronous Akeneo API client."""
    
    def __init__(self, *args, **kwargs):
        self._client = None  # Initialize to avoid type checking errors before super().__init__
        super().__init__(*args, **kwargs)
        self._client = httpx.AsyncClient(base_url=self.base_url, timeout=self.timeout)

    async def _fetch_new_token_async(self) -> None:
        """Fetch a new OAuth2 access token asynchronously."""
        headers = {"Authorization": self._get_basic_auth_header()}
        
        # Really struggling to understand why tf these guys have set up auth like this.....
        data = {
            "grant_type": "password",
            "username": self.username,
            "password": self.password,
        }

        logger.info(f"Fetching new OAuth2 token asynchronously from {self.token_url}")
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as token_client:
                response = await token_client.post(self.token_url, headers=headers, data=data)
            response.raise_for_status()
            token_data = response.json()
            self._access_token = token_data["access_token"]
            self._token_expires_at = time.time() + token_data["expires_in"]
            logger.info("Successfully fetched new OAuth2 token asynchronously.")
        except httpx.HTTPStatusError as e:
            logger.error(f"Failed to fetch OAuth2 token asynchronously: {e.response.status_code} - {e.response.text}")
            self._access_token = None
            raise AuthenticationError(
                message=f"Failed to fetch OAuth2 token: {e.response.text}",
                response=e.response
            )
        except Exception as e:
            logger.error(f"An unexpected error occurred while fetching OAuth2 token asynchronously: {e}")
            self._access_token = None
            # Create a dummy response for error creation
            dummy_response = httpx.Response(500, request=httpx.Request("POST", self.token_url))
            raise AuthenticationError(
                message=f"Unexpected error fetching token: {str(e)}",
                response=dummy_response
            )

    async def _ensure_token_valid_async(self) -> None:
        """Ensure we have a valid access token asynchronously."""
        if self._is_token_expired():
            await self._fetch_new_token_async()

    @async_throttler.throttle()
    async def _make_request_async(
        self,
        method: str,
        path: str,
        params: Optional[Dict[str, Any]] = None,
        json_data: Optional[Dict[str, Any]] = None,
        form_data: Optional[Dict[str, Any]] = None,
        files: Optional[Dict[str, Any]] = None,
    ) -> Any:
        """Make an asynchronous HTTP request to the Akeneo API."""
        
        if not isinstance(self._client, httpx.AsyncClient):
            raise TypeError("HTTP client must be an instance of httpx.AsyncClient")
        
        await self._ensure_token_valid_async()
        
        params = utils.clean_params(params) if params else {}
        
        headers = {
            "Authorization": f"Bearer {self._access_token}",
            "Accept": "application/json",
        }
        
        # Ensure path starts with /
        if not path.startswith('/'):
            path = '/' + path

        retries = self.max_retries
        while True:
            try:
                response = await self._client.request(
                    method,
                    path,
                    params=params,
                    json=json_data,
                    data=form_data,
                    files=files,
                    headers=headers,
                )
                
                if 200 <= response.status_code < 300:
                    if response.content:
                        try:
                            return response.json()
                        except ValueError:
                            # Response is not JSON, return text
                            return response.text
                    return {}

                retry_after_header = response.headers.get("Retry-After")
                should_retry_rate_limit = response.status_code == 429 and retry_after_header and retry_after_header.isdigit()
                should_retry_maintenance = response.status_code == 503 and retry_after_header and retry_after_header.isdigit()

                if (should_retry_rate_limit or should_retry_maintenance) and retries > 0:
                    wait_time = int(retry_after_header)  # type: ignore
                    logger.warning(f"Status {response.status_code}, retrying after {wait_time}s. Retries left: {retries-1}")
                    await asyncio.sleep(wait_time)
                    retries -= 1
                    await self._ensure_token_valid_async()
                    headers["Authorization"] = f"Bearer {self._access_token}"
                    continue
                
                self._handle_error_response(response, method, path, params=params, json=json_data, data=form_data)
                return {}  # Should not be reached

            except AkeneoAPIError as e:
                if hasattr(e, 'retry_after') and getattr(e, 'retry_after') and isinstance(e.retry_after, (int, float)) and retries > 0:
                    logger.warning(f"Caught {type(e).__name__}, retrying after {e.retry_after}s. Retries left: {retries-1}")
                    await asyncio.sleep(e.retry_after)
                    retries -= 1
                    await self._ensure_token_valid_async()
                    headers["Authorization"] = f"Bearer {self._access_token}"
                    continue
                raise
            except httpx.RequestError as e:
                if retries > 0:
                    logger.warning(f"Network error: {e}. Retrying in 3s. Retries left: {retries-1}")
                    await asyncio.sleep(3)
                    retries -= 1
                    continue
                # Create a dummy response for network errors
                dummy_response = httpx.Response(500, request=httpx.Request(method, self.base_url + path))
                raise AkeneoAPIError(
                    message=f"Network request failed: {str(e)}",
                    response=dummy_response
                )
                
    async def close(self):
        """Close the HTTP client asynchronously."""
        if self._client and isinstance(self._client, httpx.AsyncClient):
            await self._client.aclose()
