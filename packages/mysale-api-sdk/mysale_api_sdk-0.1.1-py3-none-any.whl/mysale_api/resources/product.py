# resources/product.py

from typing import Dict, Any, List, Optional, Union, TYPE_CHECKING

from .base import MySaleResource
from ..models.product import ProductRead, ProductWrite, ProductCreateWrite, ProductImages
from ..utils import validate_identifier

if TYPE_CHECKING:
    from ..client import MySaleClient, MySaleAsyncClient


class Product(MySaleResource):
    """
    Product resource for MySale API.
    
    Products group related SKUs together in MySale marketplace.
    """
    
    endpoint = "merchant-products"
    model_class = ProductRead
    
    # Instance methods (work when this represents a specific product)
    
    def update(self, data: Union[Dict[str, Any], ProductWrite]) -> "Product":
        """Update this product."""
        merchant_product_id = self._require_instance()
        return self.update_by_merchant_id(merchant_product_id, data)
    
    def get_images(self) -> ProductImages:
        """Get images for this product."""
        merchant_product_id = self._require_instance()
        return self.get_images_for_product(merchant_product_id)
    
    # Async instance methods
    
    async def update_async(self, data: Union[Dict[str, Any], ProductWrite]) -> "Product":
        """Update this product asynchronously."""
        merchant_product_id = self._require_instance()
        return await self.update_by_merchant_id_async(merchant_product_id, data)
    
    async def get_images_async(self) -> ProductImages:
        """Get images for this product asynchronously."""
        merchant_product_id = self._require_instance()
        return await self.get_images_for_product_async(merchant_product_id)
    
    # Collection management methods (work when this is a collection manager)
    
    def get_by_merchant_id(self, merchant_product_id: str) -> "Product":
        """Get a product by its merchant product ID."""
        merchant_product_id = validate_identifier(merchant_product_id, "merchant_product_id")
        return self.get(merchant_product_id)
    
    def create_product(self, data: Union[Dict[str, Any], ProductCreateWrite]) -> "Product":
        """Create a new product."""
        if not hasattr(self._client, '_make_request_sync'):
            raise TypeError("This method requires a synchronous client")
        
        # For product creation, we use PUT with merchant_product_id in the URL
        if hasattr(data, 'model_dump'):
            prepared_data = data.model_dump(by_alias=True, exclude_none=True)
        else:
            prepared_data = data
        
        merchant_product_id = prepared_data.get('merchant_product_id')
        if not merchant_product_id:
            raise ValueError("merchant_product_id is required for product creation")
        
        merchant_product_id = validate_identifier(merchant_product_id, "merchant_product_id")
        
        url = self._build_url(merchant_product_id)
        response = self._client._make_request_sync("PUT", url, json_data=prepared_data)
        
        return self._create_instance(response)
    
    def update_by_merchant_id(self, merchant_product_id: str, data: Union[Dict[str, Any], ProductWrite]) -> "Product":
        """Update a product by merchant product ID."""
        merchant_product_id = validate_identifier(merchant_product_id, "merchant_product_id")
        
        if not hasattr(self._client, '_make_request_sync'):
            raise TypeError("This method requires a synchronous client")
        
        url = self._build_url(merchant_product_id)
        prepared_data = self._prepare_request_data(data)
        response = self._client._make_request_sync("PUT", url, json_data=prepared_data)
        
        return self._create_instance(response)
    
    def get_images_for_product(self, merchant_product_id: str) -> ProductImages:
        """Get images for a product."""
        merchant_product_id = validate_identifier(merchant_product_id, "merchant_product_id")
        
        if not hasattr(self._client, '_make_request_sync'):
            raise TypeError("This method requires a synchronous client")
        
        url = self._build_url(merchant_product_id, "images")
        response = self._client._make_request_sync("GET", url)
        
        return ProductImages(**response)
    
    def list_products(self, offset: int = 0, limit: int = 50, 
                     paginated: bool = False) -> Union[List["Product"], "PaginatedResponse[Product]"]:
        """List all products with pagination."""
        params = {
            'offset': offset,
            'limit': limit
        }
        
        return self.list(paginated=paginated, **params)
    
    # Asynchronous collection methods
    
    async def get_by_merchant_id_async(self, merchant_product_id: str) -> "Product":
        """Get a product by its merchant product ID asynchronously."""
        merchant_product_id = validate_identifier(merchant_product_id, "merchant_product_id")
        return await self.get_async(merchant_product_id)
    
    async def create_product_async(self, data: Union[Dict[str, Any], ProductCreateWrite]) -> "Product":
        """Create a new product asynchronously."""
        if not hasattr(self._client, '_make_request_async'):
            raise TypeError("This method requires an asynchronous client")
        
        if hasattr(data, 'model_dump'):
            prepared_data = data.model_dump(by_alias=True, exclude_none=True)
        else:
            prepared_data = data
        
        merchant_product_id = prepared_data.get('merchant_product_id')
        if not merchant_product_id:
            raise ValueError("merchant_product_id is required for product creation")
        
        merchant_product_id = validate_identifier(merchant_product_id, "merchant_product_id")
        
        url = self._build_url(merchant_product_id)
        response = await self._client._make_request_async("PUT", url, json_data=prepared_data)
        
        return self._create_instance(response)
    
    async def update_by_merchant_id_async(self, merchant_product_id: str, data: Union[Dict[str, Any], ProductWrite]) -> "Product":
        """Update a product by merchant product ID asynchronously."""
        merchant_product_id = validate_identifier(merchant_product_id, "merchant_product_id")
        
        if not hasattr(self._client, '_make_request_async'):
            raise TypeError("This method requires an asynchronous client")
        
        url = self._build_url(merchant_product_id)
        prepared_data = self._prepare_request_data(data)
        response = await self._client._make_request_async("PUT", url, json_data=prepared_data)
        
        return self._create_instance(response)
    
    async def get_images_for_product_async(self, merchant_product_id: str) -> ProductImages:
        """Get images for a product asynchronously."""
        merchant_product_id = validate_identifier(merchant_product_id, "merchant_product_id")
        
        if not hasattr(self._client, '_make_request_async'):
            raise TypeError("This method requires an asynchronous client")
        
        url = self._build_url(merchant_product_id, "images")
        response = await self._client._make_request_async("GET", url)
        
        return ProductImages(**response)
    
    async def list_products_async(self, offset: int = 0, limit: int = 50,
                                 paginated: bool = False) -> Union[List["Product"], "PaginatedResponse[Product]"]:
        """List all products with pagination asynchronously."""
        params = {
            'offset': offset,
            'limit': limit
        }
        
        return await self.list_async(paginated=paginated, **params)
