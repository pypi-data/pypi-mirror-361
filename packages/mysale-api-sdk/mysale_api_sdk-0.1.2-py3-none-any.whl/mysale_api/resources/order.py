# resources/order.py

from typing import Dict, Any, List, Optional, Union, Generator, AsyncGenerator, TYPE_CHECKING
from uuid import UUID

from .base import MySaleResource, PaginatedResponse
from ..models.order import (
    OrderRead, OrderListItem, OrderAcknowledgement,
    Shipment, ShipmentCreate, ShipmentList,
    Cancellation, CancellationCreate, CancellationList
)
from ..utils import validate_identifier

if TYPE_CHECKING:
    from ..client import MySaleClient, MySaleAsyncClient


class Order(MySaleResource):
    """
    Order resource for MySale API.
    
    Provides access to order management functionality including
    retrieving orders, acknowledgements, shipments, and cancellations.
    """
    
    endpoint = "orders"
    model_class = OrderRead
    
    # Instance methods (work when this represents a specific order)
    
    def acknowledge(self, acknowledgement: Union[Dict[str, Any], OrderAcknowledgement]) -> None:
        """Acknowledge this order."""
        order_id = self._require_instance()
        self.acknowledge_order(order_id, acknowledgement)
    
    def create_shipment(self, shipment: Union[Dict[str, Any], ShipmentCreate]) -> str:
        """Create a new shipment for this order. Returns the shipment ID."""
        order_id = self._require_instance()
        return self.create_shipment_for_order(order_id, shipment)
    
    def get_shipments(self) -> ShipmentList:
        """Get all shipments for this order."""
        order_id = self._require_instance()
        return self.get_shipments_for_order(order_id)
    
    def get_shipment(self, shipment_id: str) -> Shipment:
        """Get a specific shipment for this order."""
        order_id = self._require_instance()
        return self.get_shipment_for_order(order_id, shipment_id)
    
    def update_shipment(self, shipment_id: str, shipment: Union[Dict[str, Any], ShipmentCreate]) -> None:
        """Update an existing shipment for this order."""
        order_id = self._require_instance()
        self.update_shipment_for_order(order_id, shipment_id, shipment)
    
    def create_cancellation(self, cancellation: Union[Dict[str, Any], CancellationCreate]) -> str:
        """Create a new cancellation for this order. Returns the cancellation ID."""
        order_id = self._require_instance()
        return self.create_cancellation_for_order(order_id, cancellation)
    
    def get_cancellations(self) -> CancellationList:
        """Get all cancellations for this order."""
        order_id = self._require_instance()
        return self.get_cancellations_for_order(order_id)
    
    def get_cancellation(self, cancellation_id: str) -> Cancellation:
        """Get a specific cancellation for this order."""
        order_id = self._require_instance()
        return self.get_cancellation_for_order(order_id, cancellation_id)
    
    # Async instance methods
    
    async def acknowledge_async(self, acknowledgement: Union[Dict[str, Any], OrderAcknowledgement]) -> None:
        """Acknowledge this order asynchronously."""
        order_id = self._require_instance()
        await self.acknowledge_order_async(order_id, acknowledgement)
    
    async def create_shipment_async(self, shipment: Union[Dict[str, Any], ShipmentCreate]) -> str:
        """Create a new shipment for this order asynchronously."""
        order_id = self._require_instance()
        return await self.create_shipment_for_order_async(order_id, shipment)
    
    async def get_shipments_async(self) -> ShipmentList:
        """Get all shipments for this order asynchronously."""
        order_id = self._require_instance()
        return await self.get_shipments_for_order_async(order_id)
    
    async def create_cancellation_async(self, cancellation: Union[Dict[str, Any], CancellationCreate]) -> str:
        """Create a new cancellation for this order asynchronously."""
        order_id = self._require_instance()
        return await self.create_cancellation_for_order_async(order_id, cancellation)
    
    # Collection management methods (work when this is a collection manager)
    
    def get_order(self, order_id: str) -> "Order":
        """Get a specific order by ID."""
        order_id = validate_identifier(order_id, "order_id")
        return self.get(order_id)
    
    def paginate_orders_by_status(self, status: str, offset: int = 0, limit: int = 50) -> Generator["Order", None, None]:
        """Paginate through orders by status."""
        for order_list_item in self.paginate(url=self._build_url(status), offset=offset, limit=limit):
            yield self.get_order(order_list_item.order_id)

    def list_new_orders(self, offset: int = 0, limit: int = 50, 
                       paginated: bool = False) -> Union[List[OrderListItem], "PaginatedResponse[OrderListItem]"]:
        """List orders with 'new' status."""
        return self._list_orders_by_status("new", offset, limit, paginated)
    
    def list_acknowledged_orders(self, offset: int = 0, limit: int = 50,
                               paginated: bool = False) -> Union[List[OrderListItem], "PaginatedResponse[OrderListItem]"]:
        """List orders with 'acknowledged' status."""
        return self._list_orders_by_status("acknowledged", offset, limit, paginated)
    
    def list_inprogress_orders(self, offset: int = 0, limit: int = 50,
                              paginated: bool = False) -> Union[List[OrderListItem], "PaginatedResponse[OrderListItem]"]:
        """List orders with 'inprogress' status."""
        return self._list_orders_by_status("inprogress", offset, limit, paginated)
    
    def list_completed_orders(self, offset: int = 0, limit: int = 50,
                             paginated: bool = False) -> Union[List[OrderListItem], "PaginatedResponse[OrderListItem]"]:
        """List orders with 'completed' status."""
        return self._list_orders_by_status("completed", offset, limit, paginated)
    
    def list_incomplete_orders(self, offset: int = 0, limit: int = 50,
                              paginated: bool = False) -> Union[List[OrderListItem], "PaginatedResponse[OrderListItem]"]:
        """List orders with 'incomplete' status (new, acknowledged, or inprogress)."""
        return self._list_orders_by_status("incomplete", offset, limit, paginated)
    
    def _list_orders_by_status(self, status: str, offset: int, limit: int, 
                              paginated: bool) -> Union[List[OrderListItem], "PaginatedResponse[OrderListItem]"]:
        """Helper method to list orders by status."""
        if not hasattr(self._client, '_make_request_sync'):
            raise TypeError("This method requires a synchronous client")
        
        params = {
            'offset': offset,
            'limit': limit
        }
        
        url = self._build_url(status)
        prepared_params = self._prepare_request_params(params)
        response = self._client._make_request_sync("GET", url, params=prepared_params)
        
        # MySale returns orders as a direct array
        if isinstance(response, list):
            orders_data = response
        else:
            orders_data = response.get('orders', response)
        
        # Convert to OrderListItem instances
        order_items = [OrderListItem(**order_data) for order_data in orders_data]
        
        if paginated:
            # Create pagination info
            from .base import PaginatedResponse
            pagination_data = self._extract_pagination_data(response, prepared_params)
            return PaginatedResponse(
                items=order_items,
                offset=pagination_data.get('offset', offset),
                limit=pagination_data.get('limit', limit),
                total_count=pagination_data.get('total_count'),
                has_more=len(order_items) >= limit
            )
        
        return order_items
    
    def acknowledge_order(self, order_id: str, acknowledgement: Union[Dict[str, Any], OrderAcknowledgement]) -> None:
        """Acknowledge an order."""
        order_id = validate_identifier(order_id, "order_id")
        
        if not hasattr(self._client, '_make_request_sync'):
            raise TypeError("This method requires a synchronous client")
        
        url = self._build_url(order_id, "acknowledge")
        prepared_data = self._prepare_request_data(acknowledgement)
        self._client._make_request_sync("PUT", url, json_data=prepared_data)
    
    # Shipment methods
    
    def create_shipment_for_order(self, order_id: str, shipment: Union[Dict[str, Any], ShipmentCreate]) -> str:
        """Create a new shipment for an order. Returns the shipment ID."""
        order_id = validate_identifier(order_id, "order_id")
        
        if not hasattr(self._client, '_make_request_sync'):
            raise TypeError("This method requires a synchronous client")
        
        url = self._build_url(order_id, "shipments")
        prepared_data = self._prepare_request_data(shipment)
        response = self._client._make_request_sync("POST", url, json_data=prepared_data)
        
        # MySale returns the shipment ID as a string
        return response if isinstance(response, str) else str(response)
    
    def update_shipment_for_order(self, order_id: str, shipment_id: str, 
                       shipment: Union[Dict[str, Any], ShipmentCreate]) -> None:
        """Update an existing shipment."""
        order_id = validate_identifier(order_id, "order_id")
        shipment_id = validate_identifier(shipment_id, "shipment_id")
        
        if not hasattr(self._client, '_make_request_sync'):
            raise TypeError("This method requires a synchronous client")
        
        url = self._build_url(order_id, f"shipments/{shipment_id}")
        prepared_data = self._prepare_request_data(shipment)
        self._client._make_request_sync("PUT", url, json_data=prepared_data)
    
    def get_shipments_for_order(self, order_id: str) -> ShipmentList:
        """Get all shipments for an order."""
        order_id = validate_identifier(order_id, "order_id")
        
        if not hasattr(self._client, '_make_request_sync'):
            raise TypeError("This method requires a synchronous client")
        
        url = self._build_url(order_id, "shipments")
        response = self._client._make_request_sync("GET", url)
        
        return ShipmentList(**response)
    
    def get_shipment_for_order(self, order_id: str, shipment_id: str) -> Shipment:
        """Get a specific shipment."""
        order_id = validate_identifier(order_id, "order_id")
        shipment_id = validate_identifier(shipment_id, "shipment_id")
        
        if not hasattr(self._client, '_make_request_sync'):
            raise TypeError("This method requires a synchronous client")
        
        url = self._build_url(order_id, f"shipments/{shipment_id}")
        response = self._client._make_request_sync("GET", url)
        
        return Shipment(**response)
    
    # Cancellation methods
    
    def create_cancellation_for_order(self, order_id: str, cancellation: Union[Dict[str, Any], CancellationCreate]) -> str:
        """Create a new cancellation for an order. Returns the cancellation ID."""
        order_id = validate_identifier(order_id, "order_id")
        
        if not hasattr(self._client, '_make_request_sync'):
            raise TypeError("This method requires a synchronous client")
        
        url = self._build_url(order_id, "cancellations")
        prepared_data = self._prepare_request_data(cancellation)
        response = self._client._make_request_sync("POST", url, json_data=prepared_data)
        
        # MySale returns the cancellation ID as a string
        return response if isinstance(response, str) else str(response)
    
    def get_cancellations_for_order(self, order_id: str) -> CancellationList:
        """Get all cancellations for an order."""
        order_id = validate_identifier(order_id, "order_id")
        
        if not hasattr(self._client, '_make_request_sync'):
            raise TypeError("This method requires a synchronous client")
        
        url = self._build_url(order_id, "cancellations")
        response = self._client._make_request_sync("GET", url)
        
        return CancellationList(**response)
    
    def get_cancellation_for_order(self, order_id: str, cancellation_id: str) -> Cancellation:
        """Get a specific cancellation."""
        order_id = validate_identifier(order_id, "order_id")
        cancellation_id = validate_identifier(cancellation_id, "cancellation_id")
        
        if not hasattr(self._client, '_make_request_sync'):
            raise TypeError("This method requires a synchronous client")
        
        url = self._build_url(order_id, f"cancellations/{cancellation_id}")
        response = self._client._make_request_sync("GET", url)
        
        return Cancellation(**response)
    
    # Asynchronous collection methods
    
    async def get_order_async(self, order_id: str) -> "Order":
        """Get a specific order by ID asynchronously."""
        order_id = validate_identifier(order_id, "order_id")
        return await self.get_async(order_id)
    
    async def paginate_orders_by_status_async(self, status: str, offset: int = 0, limit: int = 50) -> AsyncGenerator["Order", None]:
        """Paginate through orders by status asynchronously."""
        url = self._build_url(status)
        async for order_list_item in self.paginate_async(url=url, offset=offset, limit=limit):
            yield await self.get_order_async(order_list_item.order_id)
    
    async def list_new_orders_async(self, offset: int = 0, limit: int = 50,
                                   paginated: bool = False) -> Union[List[OrderListItem], "PaginatedResponse[OrderListItem]"]:
        """List orders with 'new' status asynchronously."""
        return await self._list_orders_by_status_async("new", offset, limit, paginated)
    
    async def list_acknowledged_orders_async(self, offset: int = 0, limit: int = 50,
                                           paginated: bool = False) -> Union[List[OrderListItem], "PaginatedResponse[OrderListItem]"]:
        """List orders with 'acknowledged' status asynchronously."""
        return await self._list_orders_by_status_async("acknowledged", offset, limit, paginated)
    
    async def list_inprogress_orders_async(self, offset: int = 0, limit: int = 50,
                                          paginated: bool = False) -> Union[List[OrderListItem], "PaginatedResponse[OrderListItem]"]:
        """List orders with 'inprogress' status asynchronously."""
        return await self._list_orders_by_status_async("inprogress", offset, limit, paginated)
    
    async def list_completed_orders_async(self, offset: int = 0, limit: int = 50,
                                         paginated: bool = False) -> Union[List[OrderListItem], "PaginatedResponse[OrderListItem]"]:
        """List orders with 'completed' status asynchronously."""
        return await self._list_orders_by_status_async("completed", offset, limit, paginated)
    
    async def list_incomplete_orders_async(self, offset: int = 0, limit: int = 50,
                                          paginated: bool = False) -> Union[List[OrderListItem], "PaginatedResponse[OrderListItem]"]:
        """List orders with 'incomplete' status asynchronously."""
        return await self._list_orders_by_status_async("incomplete", offset, limit, paginated)
    
    async def _list_orders_by_status_async(self, status: str, offset: int, limit: int,
                                          paginated: bool) -> Union[List[OrderListItem], "PaginatedResponse[OrderListItem]"]:
        """Helper method to list orders by status asynchronously."""
        if not hasattr(self._client, '_make_request_async'):
            raise TypeError("This method requires an asynchronous client")
        
        params = {
            'offset': offset,
            'limit': limit
        }
        
        url = self._build_url(status)
        prepared_params = self._prepare_request_params(params)
        response = await self._client._make_request_async("GET", url, params=prepared_params)
        
        # MySale returns orders as a direct array
        if isinstance(response, list):
            orders_data = response
        else:
            orders_data = response.get('orders', response)
        
        # Convert to OrderListItem instances
        order_items = [OrderListItem(**order_data) for order_data in orders_data]
        
        if paginated:
            # Create pagination info
            from .base import PaginatedResponse
            pagination_data = self._extract_pagination_data(response, prepared_params)
            return PaginatedResponse(
                items=order_items,
                offset=pagination_data.get('offset', offset),
                limit=pagination_data.get('limit', limit),
                total_count=pagination_data.get('total_count'),
                has_more=len(order_items) >= limit
            )
        
        return order_items
    
    async def acknowledge_order_async(self, order_id: str, acknowledgement: Union[Dict[str, Any], OrderAcknowledgement]) -> None:
        """Acknowledge an order asynchronously."""
        order_id = validate_identifier(order_id, "order_id")
        
        if not hasattr(self._client, '_make_request_async'):
            raise TypeError("This method requires an asynchronous client")
        
        url = self._build_url(order_id, "acknowledge")
        prepared_data = self._prepare_request_data(acknowledgement)
        await self._client._make_request_async("PUT", url, json_data=prepared_data)
    
    # Async shipment methods
    
    async def create_shipment_for_order_async(self, order_id: str, shipment: Union[Dict[str, Any], ShipmentCreate]) -> str:
        """Create a new shipment for an order asynchronously."""
        order_id = validate_identifier(order_id, "order_id")
        
        if not hasattr(self._client, '_make_request_async'):
            raise TypeError("This method requires an asynchronous client")
        
        url = self._build_url(order_id, "shipments")
        prepared_data = self._prepare_request_data(shipment)
        response = await self._client._make_request_async("POST", url, json_data=prepared_data)
        
        return response if isinstance(response, str) else str(response)
    
    async def update_shipment_for_order_async(self, order_id: str, shipment_id: str,
                                   shipment: Union[Dict[str, Any], ShipmentCreate]) -> None:
        """Update an existing shipment asynchronously."""
        order_id = validate_identifier(order_id, "order_id")
        shipment_id = validate_identifier(shipment_id, "shipment_id")
        
        if not hasattr(self._client, '_make_request_async'):
            raise TypeError("This method requires an asynchronous client")
        
        url = self._build_url(order_id, f"shipments/{shipment_id}")
        prepared_data = self._prepare_request_data(shipment)
        await self._client._make_request_async("PUT", url, json_data=prepared_data)
    
    async def get_shipments_for_order_async(self, order_id: str) -> ShipmentList:
        """Get all shipments for an order asynchronously."""
        order_id = validate_identifier(order_id, "order_id")
        
        if not hasattr(self._client, '_make_request_async'):
            raise TypeError("This method requires an asynchronous client")
        
        url = self._build_url(order_id, "shipments")
        response = await self._client._make_request_async("GET", url)
        
        return ShipmentList(**response)
    
    async def get_shipment_for_order_async(self, order_id: str, shipment_id: str) -> Shipment:
        """Get a specific shipment asynchronously."""
        order_id = validate_identifier(order_id, "order_id")
        shipment_id = validate_identifier(shipment_id, "shipment_id")
        
        if not hasattr(self._client, '_make_request_async'):
            raise TypeError("This method requires an asynchronous client")
        
        url = self._build_url(order_id, f"shipments/{shipment_id}")
        response = await self._client._make_request_async("GET", url)
        
        return Shipment(**response)
    
    # Async cancellation methods
    
    async def create_cancellation_for_order_async(self, order_id: str, cancellation: Union[Dict[str, Any], CancellationCreate]) -> str:
        """Create a new cancellation for an order asynchronously."""
        order_id = validate_identifier(order_id, "order_id")
        
        if not hasattr(self._client, '_make_request_async'):
            raise TypeError("This method requires an asynchronous client")
        
        url = self._build_url(order_id, "cancellations")
        prepared_data = self._prepare_request_data(cancellation)
        response = await self._client._make_request_async("POST", url, json_data=prepared_data)
        
        return response if isinstance(response, str) else str(response)
    
    async def get_cancellations_for_order_async(self, order_id: str) -> CancellationList:
        """Get all cancellations for an order asynchronously."""
        order_id = validate_identifier(order_id, "order_id")
        
        if not hasattr(self._client, '_make_request_async'):
            raise TypeError("This method requires an asynchronous client")
        
        url = self._build_url(order_id, "cancellations")
        response = await self._client._make_request_async("GET", url)
        
        return CancellationList(**response)
    
    async def get_cancellation_for_order_async(self, order_id: str, cancellation_id: str) -> Cancellation:
        """Get a specific cancellation asynchronously."""
        order_id = validate_identifier(order_id, "order_id")
        cancellation_id = validate_identifier(cancellation_id, "cancellation_id")
        
        if not hasattr(self._client, '_make_request_async'):
            raise TypeError("This method requires an asynchronous client")
        
        url = self._build_url(order_id, f"cancellations/{cancellation_id}")
        response = await self._client._make_request_async("GET", url)
        
        return Cancellation(**response)
