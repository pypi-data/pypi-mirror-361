# resources/returns.py

from typing import Dict, Any, List, Optional, Union, TYPE_CHECKING

from .base import MySaleResource, PaginatedResponse
from ..models.returns import (
    ReturnRead, ReturnListItem, ReturnUpdate, PartialRefund,
    TicketRead, TicketListItem, TicketCreate
)
from ..utils import validate_identifier

if TYPE_CHECKING:
    from ..client import MySaleClient, MySaleAsyncClient


class Returns(MySaleResource):
    """
    Returns resource for MySale API.
    
    Provides access to returns management functionality including
    retrieving returns, updating status, and managing tickets.
    """
    
    endpoint = "returns"
    model_class = ReturnRead
    
    # Instance methods (work when this represents a specific return)
    
    def update_return(self, update_data: Union[Dict[str, Any], ReturnUpdate]) -> "Returns":
        """Update this return."""
        return_id = self._require_instance()
        return self.update_return_by_id(return_id, update_data)
    
    def approve(self) -> "Returns":
        """Approve this return."""
        return_id = self._require_instance()
        return self.approve_return(return_id)
    
    def decline(self) -> "Returns":
        """Decline this return."""
        return_id = self._require_instance()
        return self.decline_return(return_id)
    
    def receive(self) -> "Returns":
        """Mark this return as received."""
        return_id = self._require_instance()
        return self.receive_return(return_id)
    
    def reopen(self) -> "Returns":
        """Reopen this return."""
        return_id = self._require_instance()
        return self.reopen_return(return_id)
    
    def full_refund(self) -> "Returns":
        """Fully refund this return."""
        return_id = self._require_instance()
        return self.full_refund_return(return_id)
    
    def partial_refund(self, refund_data: Union[Dict[str, Any], PartialRefund]) -> "Returns":
        """Partially refund this return."""
        return_id = self._require_instance()
        return self.partial_refund_return(return_id, refund_data)
    
    def get_tickets(self) -> List[TicketListItem]:
        """Get all tickets for this return."""
        return_id = self._require_instance()
        return self.get_return_tickets(return_id)
    
    def create_ticket(self, ticket_data: Union[Dict[str, Any], TicketCreate]) -> TicketRead:
        """Create a ticket for this return."""
        return_id = self._require_instance()
        return self.create_ticket_from_return(return_id, ticket_data)
    
    # Async instance methods
    
    async def update_return_async(self, update_data: Union[Dict[str, Any], ReturnUpdate]) -> "Returns":
        """Update this return asynchronously."""
        return_id = self._require_instance()
        return await self.update_return_by_id_async(return_id, update_data)
    
    async def approve_async(self) -> "Returns":
        """Approve this return asynchronously."""
        return_id = self._require_instance()
        return await self.approve_return_async(return_id)
    
    async def decline_async(self) -> "Returns":
        """Decline this return asynchronously."""
        return_id = self._require_instance()
        return await self.decline_return_async(return_id)
    
    async def full_refund_async(self) -> "Returns":
        """Fully refund this return asynchronously."""
        return_id = self._require_instance()
        return await self.full_refund_return_async(return_id)
    
    async def partial_refund_async(self, refund_data: Union[Dict[str, Any], PartialRefund]) -> "Returns":
        """Partially refund this return asynchronously."""
        return_id = self._require_instance()
        return await self.partial_refund_return_async(return_id, refund_data)
    
    # Collection management methods (work when this is a collection manager)
    
    def get_return(self, return_id: str) -> "Returns":
        """Get a specific return by ID."""
        return_id = validate_identifier(return_id, "return_id")
        return self.get(return_id)
    
    def list_pending_returns(self, offset: int = 0, limit: int = 50,
                           paginated: bool = False) -> Union[List[ReturnListItem], "PaginatedResponse[ReturnListItem]"]:
        """List returns with 'pending' status."""
        return self._list_returns_by_status("pending", offset, limit, paginated)
    
    def list_awaiting_returns(self, offset: int = 0, limit: int = 50,
                            paginated: bool = False) -> Union[List[ReturnListItem], "PaginatedResponse[ReturnListItem]"]:
        """List returns with 'approved' status (awaiting processing)."""
        return self._list_returns_by_status("awaiting", offset, limit, paginated)
    
    def list_received_returns(self, offset: int = 0, limit: int = 50,
                            paginated: bool = False) -> Union[List[ReturnListItem], "PaginatedResponse[ReturnListItem]"]:
        """List returns with 'received' status."""
        return self._list_returns_by_status("received", offset, limit, paginated)
    
    def list_closed_returns(self, offset: int = 0, limit: int = 50,
                          paginated: bool = False) -> Union[List[ReturnListItem], "PaginatedResponse[ReturnListItem]"]:
        """List returns with 'closed' status."""
        return self._list_returns_by_status("closed", offset, limit, paginated)
    
    def list_declined_returns(self, offset: int = 0, limit: int = 50,
                            paginated: bool = False) -> Union[List[ReturnListItem], "PaginatedResponse[ReturnListItem]"]:
        """List returns with 'declined' status."""
        return self._list_returns_by_status("declined", offset, limit, paginated)
    
    def _list_returns_by_status(self, status: str, offset: int, limit: int,
                               paginated: bool) -> Union[List[ReturnListItem], "PaginatedResponse[ReturnListItem]"]:
        """Helper method to list returns by status."""
        if not hasattr(self._client, '_make_request_sync'):
            raise TypeError("This method requires a synchronous client")
        
        params = {
            'offset': offset,
            'limit': limit
        }
        
        url = self._build_url(status)
        prepared_params = self._prepare_request_params(params)
        response = self._client._make_request_sync("GET", url, params=prepared_params)
        
        # MySale returns returns as a direct array
        if isinstance(response, list):
            returns_data = response
        else:
            returns_data = response.get('returns', response)
        
        # Convert to ReturnListItem instances
        return_items = [ReturnListItem(**return_data) for return_data in returns_data]
        
        if paginated:
            from .base import PaginatedResponse
            pagination_data = self._extract_pagination_data(response, prepared_params)
            return PaginatedResponse(
                items=return_items,
                offset=pagination_data.get('offset', offset),
                limit=pagination_data.get('limit', limit),
                total_count=pagination_data.get('total_count'),
                has_more=len(return_items) >= limit
            )
        
        return return_items
    
    def update_return_by_id(self, return_id: str, update_data: Union[Dict[str, Any], ReturnUpdate]) -> "Returns":
        """Update a return."""
        return_id = validate_identifier(return_id, "return_id")
        
        if not hasattr(self._client, '_make_request_sync'):
            raise TypeError("This method requires a synchronous client")
        
        url = self._build_url(return_id)
        prepared_data = self._prepare_request_data(update_data)
        response = self._client._make_request_sync("PUT", url, json_data=prepared_data)
        
        return self._create_instance(response)
    
    def approve_return(self, return_id: str) -> "Returns":
        """Approve a return."""
        return self._update_return_status(return_id, "approve")
    
    def decline_return(self, return_id: str) -> "Returns":
        """Decline a return."""
        return self._update_return_status(return_id, "decline")
    
    def receive_return(self, return_id: str) -> "Returns":
        """Mark a return as received."""
        return self._update_return_status(return_id, "receive")
    
    def reopen_return(self, return_id: str) -> "Returns":
        """Reopen a return."""
        return self._update_return_status(return_id, "reopen")
    
    def full_refund_return(self, return_id: str) -> "Returns":
        """Fully refund a return."""
        return self._update_return_status(return_id, "fullRefund")
    
    def partial_refund_return(self, return_id: str, refund_data: Union[Dict[str, Any], PartialRefund]) -> "Returns":
        """Partially refund a return."""
        return_id = validate_identifier(return_id, "return_id")
        
        if not hasattr(self._client, '_make_request_sync'):
            raise TypeError("This method requires a synchronous client")
        
        url = self._build_url(return_id + ":partialRefund")
        prepared_data = self._prepare_request_data(refund_data)
        response = self._client._make_request_sync("POST", url, json_data=prepared_data)
        
        return self._create_instance(response)
    
    def _update_return_status(self, return_id: str, status_command: str) -> "Returns":
        """Helper method to update return status."""
        return_id = validate_identifier(return_id, "return_id")
        
        if not hasattr(self._client, '_make_request_sync'):
            raise TypeError("This method requires a synchronous client")
        
        url = self._build_url(return_id + ":" + status_command)
        response = self._client._make_request_sync("POST", url)
        
        return self._create_instance(response)
    
    # Ticket methods
    
    def get_return_tickets(self, return_id: str) -> List[TicketListItem]:
        """Get all tickets for a return."""
        return_id = validate_identifier(return_id, "return_id")
        
        if not hasattr(self._client, '_make_request_sync'):
            raise TypeError("This method requires a synchronous client")
        
        url = self._build_url(return_id, "tickets")
        response = self._client._make_request_sync("GET", url)
        
        # MySale returns tickets as a direct array
        if isinstance(response, list):
            tickets_data = response
        else:
            tickets_data = response.get('tickets', response)
        
        return [TicketListItem(**ticket_data) for ticket_data in tickets_data]
    
    def create_ticket_from_return(self, return_id: str, ticket_data: Union[Dict[str, Any], TicketCreate]) -> TicketRead:
        """Create a ticket from a return."""
        return_id = validate_identifier(return_id, "return_id")
        
        if not hasattr(self._client, '_make_request_sync'):
            raise TypeError("This method requires a synchronous client")
        
        url = self._build_url(return_id, "tickets")
        prepared_data = self._prepare_request_data(ticket_data)
        response = self._client._make_request_sync("POST", url, json_data=prepared_data)
        
        return TicketRead(**response)
    
    # Asynchronous collection methods
    
    async def get_return_async(self, return_id: str) -> "Returns":
        """Get a specific return by ID asynchronously."""
        return_id = validate_identifier(return_id, "return_id")
        return await self.get_async(return_id)
    
    async def list_pending_returns_async(self, offset: int = 0, limit: int = 50,
                                       paginated: bool = False) -> Union[List[ReturnListItem], "PaginatedResponse[ReturnListItem]"]:
        """List pending returns asynchronously."""
        return await self._list_returns_by_status_async("pending", offset, limit, paginated)
    
    async def list_awaiting_returns_async(self, offset: int = 0, limit: int = 50,
                                        paginated: bool = False) -> Union[List[ReturnListItem], "PaginatedResponse[ReturnListItem]"]:
        """List awaiting returns asynchronously."""
        return await self._list_returns_by_status_async("awaiting", offset, limit, paginated)
    
    async def list_received_returns_async(self, offset: int = 0, limit: int = 50,
                                        paginated: bool = False) -> Union[List[ReturnListItem], "PaginatedResponse[ReturnListItem]"]:
        """List received returns asynchronously."""
        return await self._list_returns_by_status_async("received", offset, limit, paginated)
    
    async def list_closed_returns_async(self, offset: int = 0, limit: int = 50,
                                      paginated: bool = False) -> Union[List[ReturnListItem], "PaginatedResponse[ReturnListItem]"]:
        """List closed returns asynchronously."""
        return await self._list_returns_by_status_async("closed", offset, limit, paginated)
    
    async def list_declined_returns_async(self, offset: int = 0, limit: int = 50,
                                        paginated: bool = False) -> Union[List[ReturnListItem], "PaginatedResponse[ReturnListItem]"]:
        """List declined returns asynchronously."""
        return await self._list_returns_by_status_async("declined", offset, limit, paginated)
    
    async def _list_returns_by_status_async(self, status: str, offset: int, limit: int,
                                          paginated: bool) -> Union[List[ReturnListItem], "PaginatedResponse[ReturnListItem]"]:
        """Helper method to list returns by status asynchronously."""
        if not hasattr(self._client, '_make_request_async'):
            raise TypeError("This method requires an asynchronous client")
        
        params = {
            'offset': offset,
            'limit': limit
        }
        
        url = self._build_url(status)
        prepared_params = self._prepare_request_params(params)
        response = await self._client._make_request_async("GET", url, params=prepared_params)
        
        # MySale returns returns as a direct array
        if isinstance(response, list):
            returns_data = response
        else:
            returns_data = response.get('returns', response)
        
        # Convert to ReturnListItem instances
        return_items = [ReturnListItem(**return_data) for return_data in returns_data]
        
        if paginated:
            from .base import PaginatedResponse
            pagination_data = self._extract_pagination_data(response, prepared_params)
            return PaginatedResponse(
                items=return_items,
                offset=pagination_data.get('offset', offset),
                limit=pagination_data.get('limit', limit),
                total_count=pagination_data.get('total_count'),
                has_more=len(return_items) >= limit
            )
        
        return return_items
    
    async def update_return_by_id_async(self, return_id: str, update_data: Union[Dict[str, Any], ReturnUpdate]) -> "Returns":
        """Update a return asynchronously."""
        return_id = validate_identifier(return_id, "return_id")
        
        if not hasattr(self._client, '_make_request_async'):
            raise TypeError("This method requires an asynchronous client")
        
        url = self._build_url(return_id)
        prepared_data = self._prepare_request_data(update_data)
        response = await self._client._make_request_async("PUT", url, json_data=prepared_data)
        
        return self._create_instance(response)
    
    async def approve_return_async(self, return_id: str) -> "Returns":
        """Approve a return asynchronously."""
        return await self._update_return_status_async(return_id, "approve")
    
    async def decline_return_async(self, return_id: str) -> "Returns":
        """Decline a return asynchronously."""
        return await self._update_return_status_async(return_id, "decline")
    
    async def receive_return_async(self, return_id: str) -> "Returns":
        """Mark a return as received asynchronously."""
        return await self._update_return_status_async(return_id, "receive")
    
    async def reopen_return_async(self, return_id: str) -> "Returns":
        """Reopen a return asynchronously."""
        return await self._update_return_status_async(return_id, "reopen")
    
    async def full_refund_return_async(self, return_id: str) -> "Returns":
        """Fully refund a return asynchronously."""
        return await self._update_return_status_async(return_id, "fullRefund")
    
    async def partial_refund_return_async(self, return_id: str, refund_data: Union[Dict[str, Any], PartialRefund]) -> "Returns":
        """Partially refund a return asynchronously."""
        return_id = validate_identifier(return_id, "return_id")
        
        if not hasattr(self._client, '_make_request_async'):
            raise TypeError("This method requires an asynchronous client")
        
        url = self._build_url(return_id + ":partialRefund")
        prepared_data = self._prepare_request_data(refund_data)
        response = await self._client._make_request_async("POST", url, json_data=prepared_data)
        
        return self._create_instance(response)
    
    async def _update_return_status_async(self, return_id: str, status_command: str) -> "Returns":
        """Helper method to update return status asynchronously."""
        return_id = validate_identifier(return_id, "return_id")
        
        if not hasattr(self._client, '_make_request_async'):
            raise TypeError("This method requires an asynchronous client")
        
        url = self._build_url(return_id + ":" + status_command)
        response = await self._client._make_request_async("POST", url)
        
        return self._create_instance(response)
    
    # Async ticket methods
    
    async def get_return_tickets_async(self, return_id: str) -> List[TicketListItem]:
        """Get all tickets for a return asynchronously."""
        return_id = validate_identifier(return_id, "return_id")
        
        if not hasattr(self._client, '_make_request_async'):
            raise TypeError("This method requires an asynchronous client")
        
        url = self._build_url(return_id, "tickets")
        response = await self._client._make_request_async("GET", url)
        
        # MySale returns tickets as a direct array
        if isinstance(response, list):
            tickets_data = response
        else:
            tickets_data = response.get('tickets', response)
        
        return [TicketListItem(**ticket_data) for ticket_data in tickets_data]
    
    async def create_ticket_from_return_async(self, return_id: str, ticket_data: Union[Dict[str, Any], TicketCreate]) -> TicketRead:
        """Create a ticket from a return asynchronously."""
        return_id = validate_identifier(return_id, "return_id")
        
        if not hasattr(self._client, '_make_request_async'):
            raise TypeError("This method requires an asynchronous client")
        
        url = self._build_url(return_id, "tickets")
        prepared_data = self._prepare_request_data(ticket_data)
        response = await self._client._make_request_async("POST", url, json_data=prepared_data)
        
        return TicketRead(**response)
