# resources/sku.py

from typing import Dict, Any, List, Optional, Union, TYPE_CHECKING
import json
import asyncio

from .base import MySaleResource
from ..models.sku import (
    SKURead, SKUWrite, SKUCreateWrite, 
    SKUImages, SKUPrices, SKUInventory, SKUAttributes, SKUStatistics
)
from ..utils import validate_merchant_sku_id

if TYPE_CHECKING:
    from ..client import MySaleClient, MySaleAsyncClient


class SKU(MySaleResource):
    """
    SKU resource for MySale API.
    
    SKUs are the core product entities in MySale marketplace.
    """
    
    endpoint = "merchant-skus"
    model_class = SKURead
    
    # Instance methods (work when this represents a specific SKU)
    
    def update(self, data: Union[Dict[str, Any], SKUWrite]) -> "SKU":
        """Update this SKU instance."""
        merchant_sku_id = self._require_instance()
        return self.update_by_merchant_id(merchant_sku_id, data)
    
    def enable_sku(self) -> None:
        """Enable this SKU for sale."""
        merchant_sku_id = self._require_instance()
        self.enable(merchant_sku_id)
    
    def disable_sku(self) -> None:
        """Disable this SKU for sale."""
        merchant_sku_id = self._require_instance()
        self.disable(merchant_sku_id)
    
    def unarchive_sku(self) -> None:
        """Unarchive this SKU for sale."""
        merchant_sku_id = self._require_instance()
        self.unarchive(merchant_sku_id)
    
    def upload_images(self, images: Union[Dict[str, Any], SKUImages]) -> SKUImages:
        """Upload images for this SKU."""
        merchant_sku_id = self._require_instance()
        return self.upload_images_for_sku(merchant_sku_id, images)
    
    def get_images(self) -> SKUImages:
        """Get images for this SKU."""
        merchant_sku_id = self._require_instance()
        return self.get_images_for_sku(merchant_sku_id)
    
    def upload_prices(self, prices: Union[Dict[str, Any], SKUPrices]) -> SKUPrices:
        """Upload prices for this SKU."""
        merchant_sku_id = self._require_instance()
        return self.upload_prices_for_sku(merchant_sku_id, prices)
    
    def get_prices(self) -> SKUPrices:
        """Get prices for this SKU."""
        merchant_sku_id = self._require_instance()
        return self.get_prices_for_sku(merchant_sku_id)
    
    def upload_inventory(self, inventory: Union[Dict[str, Any], SKUInventory]) -> SKUInventory:
        """Upload inventory for this SKU."""
        merchant_sku_id = self._require_instance()
        return self.upload_inventory_for_sku(merchant_sku_id, inventory)
    
    def get_inventory(self) -> SKUInventory:
        """Get inventory for this SKU."""
        merchant_sku_id = self._require_instance()
        return self.get_inventory_for_sku(merchant_sku_id)
    
    def upload_attributes(self, attributes: Union[Dict[str, Any], SKUAttributes]) -> SKUAttributes:
        """Upload attributes for this SKU."""
        merchant_sku_id = self._require_instance()
        return self.upload_attributes_for_sku(merchant_sku_id, attributes)
    
    # Async instance methods
    
    async def update_async(self, data: Union[Dict[str, Any], SKUWrite]) -> "SKU":
        """Update this SKU instance asynchronously."""
        merchant_sku_id = self._require_instance()
        return await self.update_by_merchant_id_async(merchant_sku_id, data)
    
    async def enable_sku_async(self) -> None:
        """Enable this SKU for sale asynchronously."""
        merchant_sku_id = self._require_instance()
        await self.enable_async(merchant_sku_id)
    
    async def disable_sku_async(self) -> None:
        """Disable this SKU for sale asynchronously."""
        merchant_sku_id = self._require_instance()
        await self.disable_async(merchant_sku_id)
    
    async def upload_prices_async(self, prices: Union[Dict[str, Any], SKUPrices]) -> SKUPrices:
        """Upload prices for this SKU asynchronously."""
        merchant_sku_id = self._require_instance()
        return await self.upload_prices_for_sku_async(merchant_sku_id, prices)
    
    async def upload_inventory_async(self, inventory: Union[Dict[str, Any], SKUInventory]) -> SKUInventory:
        """Upload inventory for this SKU asynchronously."""
        merchant_sku_id = self._require_instance()
        return await self.upload_inventory_for_sku_async(merchant_sku_id, inventory)
    
    # Collection management methods (work when this is a collection manager)
    
    def get_by_merchant_id(self, merchant_sku_id: str) -> "SKU":
        """Get a SKU by its merchant SKU ID."""
        merchant_sku_id = validate_merchant_sku_id(merchant_sku_id)
        return self.get(merchant_sku_id)
    
    def create_sku(self, data: Union[Dict[str, Any], SKUCreateWrite]) -> "SKU":
        """Create a new SKU."""
        if not hasattr(self._client, '_make_request_sync'):
            raise TypeError("This method requires a synchronous client")
        
        # For SKU creation, we use PUT with merchant_sku_id in the URL
        if hasattr(data, 'model_dump'):
            prepared_data = data.model_dump(by_alias=True, exclude_none=True)
        else:
            prepared_data = data
        
        merchant_sku_id = prepared_data.get('merchant_sku_id')
        if not merchant_sku_id:
            raise ValueError("merchant_sku_id is required for SKU creation")
        
        merchant_sku_id = validate_merchant_sku_id(merchant_sku_id)
        
        url = self._build_url(merchant_sku_id)
        response = self._client._make_request_sync("PUT", url, json_data=prepared_data)
        
        return self._create_instance(response)
    
    def update_by_merchant_id(self, merchant_sku_id: str, data: Union[Dict[str, Any], SKUWrite]) -> "SKU":
        """Update a SKU by merchant SKU ID."""
        merchant_sku_id = validate_merchant_sku_id(merchant_sku_id)
        
        if not hasattr(self._client, '_make_request_sync'):
            raise TypeError("This method requires a synchronous client")
        
        url = self._build_url(merchant_sku_id)
        prepared_data = self._prepare_request_data(data)
        response = self._client._make_request_sync("PUT", url, json_data=prepared_data)
        
        return self._create_instance(response)
    
    def enable(self, merchant_sku_id: str) -> None:
        """Enable SKU for sale."""
        merchant_sku_id = validate_merchant_sku_id(merchant_sku_id)
        
        if not hasattr(self._client, '_make_request_sync'):
            raise TypeError("This method requires a synchronous client")
        
        url = self._build_url(merchant_sku_id, "enable")
        self._client._make_request_sync("POST", url)
    
    def disable(self, merchant_sku_id: str) -> None:
        """Disable SKU for sale."""
        merchant_sku_id = validate_merchant_sku_id(merchant_sku_id)
        
        if not hasattr(self._client, '_make_request_sync'):
            raise TypeError("This method requires a synchronous client")
        
        url = self._build_url(merchant_sku_id, "disable")
        self._client._make_request_sync("POST", url)
    
    def unarchive(self, merchant_sku_id: str) -> None:
        """Unarchive SKU for sale."""
        merchant_sku_id = validate_merchant_sku_id(merchant_sku_id)
        
        if not hasattr(self._client, '_make_request_sync'):
            raise TypeError("This method requires a synchronous client")
        
        url = self._build_url(merchant_sku_id, "unarchive")
        self._client._make_request_sync("POST", url)
    
    # Image management
    
    def upload_images_for_sku(self, merchant_sku_id: str, images: Union[Dict[str, Any], SKUImages]) -> SKUImages:
        """Upload images for a SKU."""
        merchant_sku_id = validate_merchant_sku_id(merchant_sku_id)
        
        if not hasattr(self._client, '_make_request_sync'):
            raise TypeError("This method requires a synchronous client")
        
        url = self._build_url(merchant_sku_id, "images")
        prepared_data = self._prepare_request_data(images)
        response = self._client._make_request_sync("PUT", url, json_data=prepared_data)
        
        return SKUImages(**response)
    
    def get_images_for_sku(self, merchant_sku_id: str) -> SKUImages:
        """Get images for a SKU."""
        merchant_sku_id = validate_merchant_sku_id(merchant_sku_id)
        
        if not hasattr(self._client, '_make_request_sync'):
            raise TypeError("This method requires a synchronous client")
        
        url = self._build_url(merchant_sku_id, "images")
        response = self._client._make_request_sync("GET", url)
        
        return SKUImages(**response)
    
    # Price management
    
    def upload_prices_for_sku(self, merchant_sku_id: str, prices: Union[Dict[str, Any], SKUPrices]) -> SKUPrices:
        """Upload prices for a SKU."""
        merchant_sku_id = validate_merchant_sku_id(merchant_sku_id)
        
        if not hasattr(self._client, '_make_request_sync'):
            raise TypeError("This method requires a synchronous client")
        
        url = self._build_url(merchant_sku_id, "prices")
        prepared_data = self._prepare_request_data(prices)
        response = self._client._make_request_sync("PUT", url, json_data=prepared_data)
        
        return SKUPrices(**response)
    
    def get_prices_for_sku(self, merchant_sku_id: str) -> SKUPrices:
        """Get prices for a SKU."""
        merchant_sku_id = validate_merchant_sku_id(merchant_sku_id)
        
        if not hasattr(self._client, '_make_request_sync'):
            raise TypeError("This method requires a synchronous client")
        
        url = self._build_url(merchant_sku_id, "prices")
        response = self._client._make_request_sync("GET", url)
        
        return SKUPrices(**response)
    
    # Inventory management
    
    def upload_inventory_for_sku(self, merchant_sku_id: str, inventory: Union[Dict[str, Any], SKUInventory]) -> SKUInventory:
        """Upload inventory for a SKU."""
        merchant_sku_id = validate_merchant_sku_id(merchant_sku_id)
        
        if not hasattr(self._client, '_make_request_sync'):
            raise TypeError("This method requires a synchronous client")
        
        url = self._build_url(merchant_sku_id, "inventory")
        prepared_data = self._prepare_request_data(inventory)
        response = self._client._make_request_sync("PUT", url, json_data=prepared_data)
        
        return SKUInventory(**response)
    
    def get_inventory_for_sku(self, merchant_sku_id: str) -> SKUInventory:
        """Get inventory for a SKU."""
        merchant_sku_id = validate_merchant_sku_id(merchant_sku_id)
        
        if not hasattr(self._client, '_make_request_sync'):
            raise TypeError("This method requires a synchronous client")
        
        url = self._build_url(merchant_sku_id, "inventory")
        response = self._client._make_request_sync("GET", url)
        
        return SKUInventory(**response)
    
    # Bulk inventory operations
    
    def bulk_update_inventory(self, inventory_updates: Dict[str, Union[Dict[str, Any], SKUInventory]]) -> Dict[str, Union[SKUInventory, Exception]]:
        """
        Bulk update inventory for multiple SKUs synchronously.
        
        Args:
            inventory_updates: Dict mapping merchant_sku_id to inventory data
            
        Returns:
            Dict mapping merchant_sku_id to either SKUInventory (success) or Exception (failure)
        """
        if not hasattr(self._client, '_make_request_sync'):
            raise TypeError("This method requires a synchronous client")
        
        results = {}
        
        for merchant_sku_id, inventory_data in inventory_updates.items():
            try:
                result = self.upload_inventory_for_sku(merchant_sku_id, inventory_data)
                results[merchant_sku_id] = result
            except Exception as e:
                results[merchant_sku_id] = e
                
        return results
    
    async def bulk_update_inventory_async(
        self, 
        inventory_updates: Dict[str, Union[Dict[str, Any], SKUInventory]],
        max_concurrent: int = 10
    ) -> Dict[str, Union[SKUInventory, Exception]]:
        """
        Bulk update inventory for multiple SKUs asynchronously.
        
        Args:
            inventory_updates: Dict mapping merchant_sku_id to inventory data
            max_concurrent: Maximum number of concurrent requests
            
        Returns:
            Dict mapping merchant_sku_id to either SKUInventory (success) or Exception (failure)
        """
        if not hasattr(self._client, '_make_request_async'):
            raise TypeError("This method requires an asynchronous client")
        
        semaphore = asyncio.Semaphore(max_concurrent)
        
        async def update_single_inventory(merchant_sku_id: str, inventory_data):
            async with semaphore:
                try:
                    result = await self.upload_inventory_for_sku_async(merchant_sku_id, inventory_data)
                    return merchant_sku_id, result
                except Exception as e:
                    return merchant_sku_id, e
        
        tasks = [
            update_single_inventory(merchant_sku_id, inventory_data)
            for merchant_sku_id, inventory_data in inventory_updates.items()
        ]
        
        results = await asyncio.gather(*tasks)
        return dict(results)
    
    # Attributes management
    
    def upload_attributes_for_sku(self, merchant_sku_id: str, attributes: Union[Dict[str, Any], SKUAttributes]) -> SKUAttributes:
        """Upload attributes for a SKU."""
        merchant_sku_id = validate_merchant_sku_id(merchant_sku_id)
        
        if not hasattr(self._client, '_make_request_sync'):
            raise TypeError("This method requires a synchronous client")
        
        url = self._build_url(merchant_sku_id, "attributes")
        prepared_data = self._prepare_request_data(attributes)
        response = self._client._make_request_sync("PUT", url, json_data=prepared_data)
        
        return SKUAttributes(**response)
    
    # Statistics
    
    def get_statistics(self, fields: Optional[List[str]] = None) -> SKUStatistics:
        """Get SKU statistics."""
        if not hasattr(self._client, '_make_request_sync'):
            raise TypeError("This method requires a synchronous client")
        
        url = "/v1/merchant-skus/statistics"
        params = {}
        
        if fields:
            params['fields'] = ','.join(fields)
        
        response = self._client._make_request_sync("GET", url, params=params)
        
        return SKUStatistics(**response)
    
    def list_skus(self, offset: int = 0, limit: int = 50, exclude_archived: bool = False, 
                  paginated: bool = False) -> Union[List["SKU"], "PaginatedResponse[SKU]"]:
        """List all SKUs with optional filters."""
        params = {
            'offset': offset,
            'limit': limit,
            'exclude_archived': exclude_archived
        }
        
        return self.list(paginated=paginated, **params)
    
    # Asynchronous collection methods
    
    async def get_by_merchant_id_async(self, merchant_sku_id: str) -> "SKU":
        """Get a SKU by its merchant SKU ID asynchronously."""
        merchant_sku_id = validate_merchant_sku_id(merchant_sku_id)
        return await self.get_async(merchant_sku_id)
    
    async def create_sku_async(self, data: Union[Dict[str, Any], SKUCreateWrite]) -> "SKU":
        """Create a new SKU asynchronously."""
        if not hasattr(self._client, '_make_request_async'):
            raise TypeError("This method requires an asynchronous client")
        
        if hasattr(data, 'model_dump'):
            prepared_data = data.model_dump(by_alias=True, exclude_none=True)
        else:
            prepared_data = data
        
        merchant_sku_id = prepared_data.get('merchant_sku_id')
        if not merchant_sku_id:
            raise ValueError("merchant_sku_id is required for SKU creation")
        
        merchant_sku_id = validate_merchant_sku_id(merchant_sku_id)
        
        url = self._build_url(merchant_sku_id)
        response = await self._client._make_request_async("PUT", url, json_data=prepared_data)
        
        return self._create_instance(response)
    
    async def update_by_merchant_id_async(self, merchant_sku_id: str, data: Union[Dict[str, Any], SKUWrite]) -> "SKU":
        """Update a SKU by merchant SKU ID asynchronously."""
        merchant_sku_id = validate_merchant_sku_id(merchant_sku_id)
        
        if not hasattr(self._client, '_make_request_async'):
            raise TypeError("This method requires an asynchronous client")
        
        url = self._build_url(merchant_sku_id)
        prepared_data = self._prepare_request_data(data)
        response = await self._client._make_request_async("PUT", url, json_data=prepared_data)
        
        return self._create_instance(response)
    
    async def enable_async(self, merchant_sku_id: str) -> None:
        """Enable SKU for sale asynchronously."""
        merchant_sku_id = validate_merchant_sku_id(merchant_sku_id)
        
        if not hasattr(self._client, '_make_request_async'):
            raise TypeError("This method requires an asynchronous client")
        
        url = self._build_url(merchant_sku_id, "enable")
        await self._client._make_request_async("POST", url)
    
    async def disable_async(self, merchant_sku_id: str) -> None:
        """Disable SKU for sale asynchronously."""
        merchant_sku_id = validate_merchant_sku_id(merchant_sku_id)
        
        if not hasattr(self._client, '_make_request_async'):
            raise TypeError("This method requires an asynchronous client")
        
        url = self._build_url(merchant_sku_id, "disable")
        await self._client._make_request_async("POST", url)
    
    async def unarchive_async(self, merchant_sku_id: str) -> None:
        """Unarchive SKU for sale asynchronously."""
        merchant_sku_id = validate_merchant_sku_id(merchant_sku_id)
        
        if not hasattr(self._client, '_make_request_async'):
            raise TypeError("This method requires an asynchronous client")
        
        url = self._build_url(merchant_sku_id, "unarchive")
        await self._client._make_request_async("POST", url)
    
    # Async image management
    
    async def upload_images_for_sku_async(self, merchant_sku_id: str, images: Union[Dict[str, Any], SKUImages]) -> SKUImages:
        """Upload images for a SKU asynchronously."""
        merchant_sku_id = validate_merchant_sku_id(merchant_sku_id)
        
        if not hasattr(self._client, '_make_request_async'):
            raise TypeError("This method requires an asynchronous client")
        
        url = self._build_url(merchant_sku_id, "images")
        prepared_data = self._prepare_request_data(images)
        response = await self._client._make_request_async("PUT", url, json_data=prepared_data)
        
        return SKUImages(**response)
    
    async def get_images_for_sku_async(self, merchant_sku_id: str) -> SKUImages:
        """Get images for a SKU asynchronously."""
        merchant_sku_id = validate_merchant_sku_id(merchant_sku_id)
        
        if not hasattr(self._client, '_make_request_async'):
            raise TypeError("This method requires an asynchronous client")
        
        url = self._build_url(merchant_sku_id, "images")
        response = await self._client._make_request_async("GET", url)
        
        return SKUImages(**response)
    
    # Async price management
    
    async def upload_prices_for_sku_async(self, merchant_sku_id: str, prices: Union[Dict[str, Any], SKUPrices]) -> SKUPrices:
        """Upload prices for a SKU asynchronously."""
        merchant_sku_id = validate_merchant_sku_id(merchant_sku_id)
        
        if not hasattr(self._client, '_make_request_async'):
            raise TypeError("This method requires an asynchronous client")
        
        url = self._build_url(merchant_sku_id, "prices")
        prepared_data = self._prepare_request_data(prices)
        response = await self._client._make_request_async("PUT", url, json_data=prepared_data)
        
        return SKUPrices(**response)
    
    async def get_prices_for_sku_async(self, merchant_sku_id: str) -> SKUPrices:
        """Get prices for a SKU asynchronously."""
        merchant_sku_id = validate_merchant_sku_id(merchant_sku_id)
        
        if not hasattr(self._client, '_make_request_async'):
            raise TypeError("This method requires an asynchronous client")
        
        url = self._build_url(merchant_sku_id, "prices")
        response = await self._client._make_request_async("GET", url)
        
        return SKUPrices(**response)
    
    # Async inventory management
    
    async def upload_inventory_for_sku_async(self, merchant_sku_id: str, inventory: Union[Dict[str, Any], SKUInventory]) -> SKUInventory:
        """Upload inventory for a SKU asynchronously."""
        merchant_sku_id = validate_merchant_sku_id(merchant_sku_id)
        
        if not hasattr(self._client, '_make_request_async'):
            raise TypeError("This method requires an asynchronous client")
        
        url = self._build_url(merchant_sku_id, "inventory")
        prepared_data = self._prepare_request_data(inventory)
        response = await self._client._make_request_async("PUT", url, json_data=prepared_data)
        
        return SKUInventory(**response)
    
    async def get_inventory_for_sku_async(self, merchant_sku_id: str) -> SKUInventory:
        """Get inventory for a SKU asynchronously."""
        merchant_sku_id = validate_merchant_sku_id(merchant_sku_id)
        
        if not hasattr(self._client, '_make_request_async'):
            raise TypeError("This method requires an asynchronous client")
        
        url = self._build_url(merchant_sku_id, "inventory")
        response = await self._client._make_request_async("GET", url)
        
        return SKUInventory(**response)
    
    # Async attributes management
    
    async def upload_attributes_for_sku_async(self, merchant_sku_id: str, attributes: Union[Dict[str, Any], SKUAttributes]) -> SKUAttributes:
        """Upload attributes for a SKU asynchronously."""
        merchant_sku_id = validate_merchant_sku_id(merchant_sku_id)
        
        if not hasattr(self._client, '_make_request_async'):
            raise TypeError("This method requires an asynchronous client")
        
        url = self._build_url(merchant_sku_id, "attributes")
        prepared_data = self._prepare_request_data(attributes)
        response = await self._client._make_request_async("PUT", url, json_data=prepared_data)
        
        return SKUAttributes(**response)
    
    # Async statistics
    
    async def get_statistics_async(self, fields: Optional[List[str]] = None) -> SKUStatistics:
        """Get SKU statistics asynchronously."""
        if not hasattr(self._client, '_make_request_async'):
            raise TypeError("This method requires an asynchronous client")
        
        url = "/v1/merchant-skus/statistics"
        params = {}
        
        if fields:
            params['fields'] = ','.join(fields)
        
        response = await self._client._make_request_async("GET", url, params=params)
        
        return SKUStatistics(**response)
    
    async def list_skus_async(self, offset: int = 0, limit: int = 50, exclude_archived: bool = False,
                             paginated: bool = False) -> Union[List["SKU"], "PaginatedResponse[SKU]"]:
        """List all SKUs with optional filters asynchronously."""
        params = {
            'offset': offset,
            'limit': limit,
            'exclude_archived': exclude_archived
        }
        
        return await self.list_async(paginated=paginated, **params)
