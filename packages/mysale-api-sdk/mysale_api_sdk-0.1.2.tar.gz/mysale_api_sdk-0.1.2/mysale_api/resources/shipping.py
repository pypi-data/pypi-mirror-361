# resources/shipping.py

from typing import Dict, Any, List, Optional, Union, TYPE_CHECKING

from .base import MySaleResource
from ..models.shipping import ShippingPolicy
from ..utils import validate_identifier

if TYPE_CHECKING:
    from ..client import MySaleClient, MySaleAsyncClient


class Shipping(MySaleResource):
    """
    Shipping resource for MySale API.
    
    Provides access to shipping policies and related configuration.
    """
    
    endpoint = "shipping-policies"
    model_class = ShippingPolicy
    
    # Synchronous methods
    
    def get_policy(self, shipping_policy_id: str) -> "Shipping":
        """Get a specific shipping policy by ID."""
        shipping_policy_id = validate_identifier(shipping_policy_id, "shipping_policy_id")
        return self.get(shipping_policy_id)
    
    def list_policies(self, paginated: bool = False) -> Union[List["Shipping"], "PaginatedResponse[Shipping]"]:
        """
        List all shipping policies.
        
        Returns all available shipping policies for the merchant.
        """
        if not hasattr(self._client, '_make_request_sync'):
            raise TypeError("This method requires a synchronous client")
        
        url = self._build_url()
        response = self._client._make_request_sync("GET", url)
        
        # MySale returns shipping policies as a direct array
        if isinstance(response, list):
            policies = response
        else:
            policies = response.get('policies', [])
        
        instances = [self._create_instance(policy) for policy in policies]
        
        if paginated:
            # MySale doesn't paginate shipping policies, so we create a simple paginated response
            from .base import PaginatedResponse
            return PaginatedResponse(
                items=instances,
                offset=0,
                limit=len(instances),
                total_count=len(instances),
                has_more=False
            )
        
        return instances
    
    def get_enabled_policies(self) -> List["Shipping"]:
        """Get only enabled shipping policies."""
        all_policies = self.list_policies()
        return [policy for policy in all_policies if policy.enabled]
    
    def get_default_policies(self) -> List["Shipping"]:
        """Get default shipping policies."""
        all_policies = self.list_policies()
        return [policy for policy in all_policies if policy.is_default]
    
    def find_policies_by_name(self, name: str) -> List["Shipping"]:
        """Find shipping policies by name (case-insensitive partial match)."""
        all_policies = self.list_policies()
        name_lower = name.lower()
        return [policy for policy in all_policies if name_lower in policy.name.lower()]
    
    def get_policies_for_location(self, dispatch_location_id: str) -> List["Shipping"]:
        """Get shipping policies that cover a specific dispatch location."""
        all_policies = self.list_policies()
        return [
            policy for policy in all_policies 
            if dispatch_location_id in [str(loc_id) for loc_id in policy.dispatch_location_ids]
        ]
    
    def get_standard_shipping_policies(self) -> List["Shipping"]:
        """Get policies with standard shipping option."""
        all_policies = self.list_policies()
        return [policy for policy in all_policies if policy.shipping_option == "standard"]
    
    def analyze_shipping_coverage(self) -> Dict[str, Any]:
        """
        Analyze shipping policy coverage.
        
        Returns summary information about shipping policies.
        """
        all_policies = self.list_policies()
        
        total_policies = len(all_policies)
        enabled_policies = len([p for p in all_policies if p.enabled])
        default_policies = len([p for p in all_policies if p.is_default])
        
        # Count policies by shipping option
        shipping_options = {}
        for policy in all_policies:
            option = policy.shipping_option
            shipping_options[option] = shipping_options.get(option, 0) + 1
        
        # Count unique dispatch locations
        all_locations = set()
        for policy in all_policies:
            all_locations.update(str(loc_id) for loc_id in policy.dispatch_location_ids)
        
        return {
            'total_policies': total_policies,
            'enabled_policies': enabled_policies,
            'default_policies': default_policies,
            'shipping_options': shipping_options,
            'unique_dispatch_locations': len(all_locations),
            'dispatch_location_ids': list(all_locations)
        }
    
    # Asynchronous methods
    
    async def get_policy_async(self, shipping_policy_id: str) -> "Shipping":
        """Get a specific shipping policy by ID asynchronously."""
        shipping_policy_id = validate_identifier(shipping_policy_id, "shipping_policy_id")
        return await self.get_async(shipping_policy_id)
    
    async def list_policies_async(self, paginated: bool = False) -> Union[List["Shipping"], "PaginatedResponse[Shipping]"]:
        """List all shipping policies asynchronously."""
        if not hasattr(self._client, '_make_request_async'):
            raise TypeError("This method requires an asynchronous client")
        
        url = self._build_url()
        response = await self._client._make_request_async("GET", url)
        
        # MySale returns shipping policies as a direct array
        if isinstance(response, list):
            policies = response
        else:
            policies = response.get('policies', [])
        
        instances = [self._create_instance(policy) for policy in policies]
        
        if paginated:
            from .base import PaginatedResponse
            return PaginatedResponse(
                items=instances,
                offset=0,
                limit=len(instances),
                total_count=len(instances),
                has_more=False
            )
        
        return instances
    
    async def get_enabled_policies_async(self) -> List["Shipping"]:
        """Get only enabled shipping policies asynchronously."""
        all_policies = await self.list_policies_async()
        return [policy for policy in all_policies if policy.enabled]
    
    async def get_default_policies_async(self) -> List["Shipping"]:
        """Get default shipping policies asynchronously."""
        all_policies = await self.list_policies_async()
        return [policy for policy in all_policies if policy.is_default]
    
    async def find_policies_by_name_async(self, name: str) -> List["Shipping"]:
        """Find shipping policies by name asynchronously."""
        all_policies = await self.list_policies_async()
        name_lower = name.lower()
        return [policy for policy in all_policies if name_lower in policy.name.lower()]
    
    async def get_policies_for_location_async(self, dispatch_location_id: str) -> List["Shipping"]:
        """Get shipping policies for a specific dispatch location asynchronously."""
        all_policies = await self.list_policies_async()
        return [
            policy for policy in all_policies 
            if dispatch_location_id in [str(loc_id) for loc_id in policy.dispatch_location_ids]
        ]
    
    async def get_standard_shipping_policies_async(self) -> List["Shipping"]:
        """Get standard shipping policies asynchronously."""
        all_policies = await self.list_policies_async()
        return [policy for policy in all_policies if policy.shipping_option == "standard"]
    
    async def analyze_shipping_coverage_async(self) -> Dict[str, Any]:
        """Analyze shipping policy coverage asynchronously."""
        all_policies = await self.list_policies_async()
        
        total_policies = len(all_policies)
        enabled_policies = len([p for p in all_policies if p.enabled])
        default_policies = len([p for p in all_policies if p.is_default])
        
        # Count policies by shipping option
        shipping_options = {}
        for policy in all_policies:
            option = policy.shipping_option
            shipping_options[option] = shipping_options.get(option, 0) + 1
        
        # Count unique dispatch locations
        all_locations = set()
        for policy in all_policies:
            all_locations.update(str(loc_id) for loc_id in policy.dispatch_location_ids)
        
        return {
            'total_policies': total_policies,
            'enabled_policies': enabled_policies,
            'default_policies': default_policies,
            'shipping_options': shipping_options,
            'unique_dispatch_locations': len(all_locations),
            'dispatch_location_ids': list(all_locations)
        }
