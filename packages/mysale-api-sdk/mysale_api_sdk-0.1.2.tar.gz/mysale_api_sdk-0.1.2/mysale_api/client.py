import httpx
import asyncio
import time
import logging
from typing import Optional, Any, Dict, Union

from .exceptions import (
    MySaleAPIError, 
    AuthenticationError, 
    create_exception_from_response
)
from . import utils
from .resources import (
    SKU,
    Product,
    Taxonomy,
    Shipping,
    Order,
    Returns
)
from .throttler import throttler, async_throttler

logger = logging.getLogger(__name__)

DEFAULT_BASE_URL = "https://api.mysale.com"  # Placeholder - should be replaced with actual MySale API URL
DEFAULT_TIMEOUT = 60.0


class BaseMySaleClient:
    def __init__(
        self,
        *,
        api_token: str,
        base_url: str = DEFAULT_BASE_URL,
        timeout: float = DEFAULT_TIMEOUT,
        max_retries: int = 5,
    ):
        if not api_token:
            raise ValueError("api_token is required.")

        self.api_token = api_token
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.max_retries = max_retries
        self.utils = utils  # Make utils accessible

        self._client: Optional[Union[httpx.Client, httpx.AsyncClient]] = None  # To be defined in subclasses

        # Initialize resource classes
        self._initialize_resources()

    def _initialize_resources(self):
        """Initialize resource classes."""
        self.skus = SKU(client=self)
        self.products = Product(client=self)
        self.taxonomy = Taxonomy(client=self)
        self.shipping = Shipping(client=self)
        self.orders = Order(client=self)
        self.returns = Returns(client=self)

    def _get_auth_headers(self) -> Dict[str, str]:
        """Generate authorization headers for MySale API."""
        return {
            "Authorization": f"Bearer {self.api_token}",
            "Accept": "application/json",
            "Content-Type": "application/json"
        }

    def _handle_error_response(self, response: httpx.Response, method: str, url: str, **kwargs):
        """Centralized error handling."""
        logger.error(
            f"MySale API Error: {response.status_code} on {method} {url}. "
            f"Response: {response.content[:500] if response.content else 'No content'}"
        )
        
        # Use our generic exception creation helper
        raise create_exception_from_response(response, method, url, **kwargs)


class MySaleClient(BaseMySaleClient):
    """Synchronous MySale API client."""
    
    def __init__(self, *args, **kwargs):
        self._client = None  # Initialize to avoid type checking errors before super().__init__
        super().__init__(*args, **kwargs)
        self._client = httpx.Client(base_url=self.base_url, timeout=self.timeout)

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
        """Make a synchronous HTTP request to the MySale API."""
        
        if not isinstance(self._client, httpx.Client):
            raise TypeError("HTTP client must be an instance of httpx.Client")
        
        headers = self._get_auth_headers()
        
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
                    continue

                self._handle_error_response(response, method, path, params=params, json=json_data, data=form_data)
                return {}  # Should not be reached due to raise in _handle_error_response

            except MySaleAPIError as e:
                if hasattr(e, 'retry_after') and getattr(e, 'retry_after') and isinstance(e.retry_after, (int, float)) and retries > 0:
                    logger.warning(f"Caught {type(e).__name__}, retrying after {e.retry_after}s. Retries left: {retries-1}")
                    time.sleep(e.retry_after)
                    retries -= 1
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
                raise MySaleAPIError(
                    message=f"Network request failed: {str(e)}",
                    response=dummy_response
                )

    def close(self):
        """Close the HTTP client."""
        if self._client and isinstance(self._client, httpx.Client):
            self._client.close()


class MySaleAsyncClient(BaseMySaleClient):
    """Asynchronous MySale API client."""
    
    def __init__(self, *args, **kwargs):
        self._client = None  # Initialize to avoid type checking errors before super().__init__
        super().__init__(*args, **kwargs)
        self._client = httpx.AsyncClient(base_url=self.base_url, timeout=self.timeout)

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
        """Make an asynchronous HTTP request to the MySale API."""
        
        if not isinstance(self._client, httpx.AsyncClient):
            raise TypeError("HTTP client must be an instance of httpx.AsyncClient")
        
        params = utils.clean_params(params) if params else {}
        
        headers = self._get_auth_headers()
        
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
                    continue
                
                self._handle_error_response(response, method, path, params=params, json=json_data, data=form_data)
                return {}  # Should not be reached

            except MySaleAPIError as e:
                if hasattr(e, 'retry_after') and getattr(e, 'retry_after') and isinstance(e.retry_after, (int, float)) and retries > 0:
                    logger.warning(f"Caught {type(e).__name__}, retrying after {e.retry_after}s. Retries left: {retries-1}")
                    await asyncio.sleep(e.retry_after)
                    retries -= 1
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
                raise MySaleAPIError(
                    message=f"Network request failed: {str(e)}",
                    response=dummy_response
                )
                
    async def close(self):
        """Close the HTTP client asynchronously."""
        if self._client and isinstance(self._client, httpx.AsyncClient):
            await self._client.aclose()
