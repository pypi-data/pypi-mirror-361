# resources/taxonomy.py

from typing import Dict, Any, List, Optional, Union, TYPE_CHECKING

from .base import MySaleResource
from ..models.taxonomy import TaxonomyBranch, TaxonomyBranches
from ..utils import validate_identifier

if TYPE_CHECKING:
    from ..client import MySaleClient, MySaleAsyncClient


class Taxonomy(MySaleResource):
    """
    Taxonomy resource for MySale API.
    
    Taxonomy provides the category structure for SKUs in MySale marketplace.
    """
    
    endpoint = "taxonomy"
    model_class = TaxonomyBranch
    
    # Synchronous methods
    
    def get_branch(self, branch_id: str) -> "Taxonomy":
        """Get a specific taxonomy branch by ID."""
        branch_id = validate_identifier(branch_id, "branch_id")
        return self.get(branch_id)
    
    def list_branches(self, offset: int = 0, limit: int = 100, 
                     paginated: bool = False) -> Union[List[str], "PaginatedResponse[str]"]:
        """
        List all taxonomy branches.
        
        Returns a list of branch IDs (GUIDs).
        """
        if not hasattr(self._client, '_make_request_sync'):
            raise TypeError("This method requires a synchronous client")
        
        params = {
            'offset': offset,
            'limit': limit
        }
        
        url = self._build_url()
        prepared_params = self._prepare_request_params(params)
        response = self._client._make_request_sync("GET", url, params=prepared_params)
        
        # Extract branches list
        branches = response.get('branches', [])
        
        if paginated:
            pagination_data = self._extract_pagination_data(response, prepared_params)
            from .base import PaginatedResponse
            return PaginatedResponse(
                items=branches,
                offset=pagination_data.get('offset', 0),
                limit=pagination_data.get('limit', 100),
                total_count=pagination_data.get('total_count'),
                has_more=pagination_data.get('has_more', False)
            )
        
        return branches
    
    def search_branches(self, keyword: str) -> List["Taxonomy"]:
        """
        Search taxonomy branches by keyword.
        
        This is a client-side search that fetches all branches and filters by keyword.
        """
        if not hasattr(self._client, '_make_request_sync'):
            raise TypeError("This method requires a synchronous client")
        
        # Get all branches first
        all_branch_ids = self.list_branches(limit=1000)  # Large limit to get all
        
        matching_branches = []
        keyword_lower = keyword.lower()
        
        # Fetch each branch and check if keyword matches
        for branch_id in all_branch_ids:
            try:
                branch = self.get_branch(branch_id)
                # Check if keyword matches name or any keywords
                if (keyword_lower in branch.name.lower() or 
                    any(keyword_lower in kw.lower() for kw in branch.keywords)):
                    matching_branches.append(branch)
            except Exception:
                # Skip branches that can't be fetched
                continue
        
        return matching_branches
    
    def get_branch_hierarchy(self, branch_id: str) -> List["Taxonomy"]:
        """
        Get the complete hierarchy for a branch (from root to this branch).
        """
        if not hasattr(self._client, '_make_request_sync'):
            raise TypeError("This method requires a synchronous client")
        
        branch_id = validate_identifier(branch_id, "branch_id")
        hierarchy = []
        current_branch_id = branch_id
        
        while current_branch_id:
            try:
                branch = self.get_branch(current_branch_id)
                hierarchy.insert(0, branch)  # Insert at beginning to maintain order
                current_branch_id = str(branch.parent_id) if branch.parent_id else None
            except Exception:
                break
        
        return hierarchy
    
    def get_child_branches(self, parent_branch_id: str) -> List["Taxonomy"]:
        """
        Get all direct child branches of a parent branch.
        
        This requires fetching all branches and filtering by parent_id.
        """
        if not hasattr(self._client, '_make_request_sync'):
            raise TypeError("This method requires a synchronous client")
        
        parent_branch_id = validate_identifier(parent_branch_id, "parent_branch_id")
        
        # Get all branches
        all_branch_ids = self.list_branches(limit=1000)
        
        child_branches = []
        
        # Fetch each branch and check if it's a child of the parent
        for branch_id in all_branch_ids:
            try:
                branch = self.get_branch(branch_id)
                if branch.parent_id and str(branch.parent_id) == parent_branch_id:
                    child_branches.append(branch)
            except Exception:
                continue
        
        # Sort by level and name
        child_branches.sort(key=lambda x: (x.level, x.name))
        
        return child_branches
    
    def get_root_branches(self) -> List["Taxonomy"]:
        """Get all root branches (branches with no parent)."""
        if not hasattr(self._client, '_make_request_sync'):
            raise TypeError("This method requires a synchronous client")
        
        # Get all branches
        all_branch_ids = self.list_branches(limit=1000)
        
        root_branches = []
        
        # Fetch each branch and check if it's a root (no parent)
        for branch_id in all_branch_ids:
            try:
                branch = self.get_branch(branch_id)
                if not branch.parent_id:
                    root_branches.append(branch)
            except Exception:
                continue
        
        # Sort by name
        root_branches.sort(key=lambda x: x.name)
        
        return root_branches
    
    # Asynchronous methods
    
    async def get_branch_async(self, branch_id: str) -> "Taxonomy":
        """Get a specific taxonomy branch by ID asynchronously."""
        branch_id = validate_identifier(branch_id, "branch_id")
        return await self.get_async(branch_id)
    
    async def list_branches_async(self, offset: int = 0, limit: int = 100,
                                 paginated: bool = False) -> Union[List[str], "PaginatedResponse[str]"]:
        """List all taxonomy branches asynchronously."""
        if not hasattr(self._client, '_make_request_async'):
            raise TypeError("This method requires an asynchronous client")
        
        params = {
            'offset': offset,
            'limit': limit
        }
        
        url = self._build_url()
        prepared_params = self._prepare_request_params(params)
        response = await self._client._make_request_async("GET", url, params=prepared_params)
        
        # Extract branches list
        branches = response.get('branches', [])
        
        if paginated:
            pagination_data = self._extract_pagination_data(response, prepared_params)
            from .base import PaginatedResponse
            return PaginatedResponse(
                items=branches,
                offset=pagination_data.get('offset', 0),
                limit=pagination_data.get('limit', 100),
                total_count=pagination_data.get('total_count'),
                has_more=pagination_data.get('has_more', False)
            )
        
        return branches
    
    async def search_branches_async(self, keyword: str) -> List["Taxonomy"]:
        """Search taxonomy branches by keyword asynchronously."""
        if not hasattr(self._client, '_make_request_async'):
            raise TypeError("This method requires an asynchronous client")
        
        # Get all branches first
        all_branch_ids = await self.list_branches_async(limit=1000)
        
        matching_branches = []
        keyword_lower = keyword.lower()
        
        # Fetch each branch and check if keyword matches
        for branch_id in all_branch_ids:
            try:
                branch = await self.get_branch_async(branch_id)
                # Check if keyword matches name or any keywords
                if (keyword_lower in branch.name.lower() or 
                    any(keyword_lower in kw.lower() for kw in branch.keywords)):
                    matching_branches.append(branch)
            except Exception:
                # Skip branches that can't be fetched
                continue
        
        return matching_branches
    
    async def get_branch_hierarchy_async(self, branch_id: str) -> List["Taxonomy"]:
        """Get the complete hierarchy for a branch asynchronously."""
        if not hasattr(self._client, '_make_request_async'):
            raise TypeError("This method requires an asynchronous client")
        
        branch_id = validate_identifier(branch_id, "branch_id")
        hierarchy = []
        current_branch_id = branch_id
        
        while current_branch_id:
            try:
                branch = await self.get_branch_async(current_branch_id)
                hierarchy.insert(0, branch)
                current_branch_id = str(branch.parent_id) if branch.parent_id else None
            except Exception:
                break
        
        return hierarchy
    
    async def get_child_branches_async(self, parent_branch_id: str) -> List["Taxonomy"]:
        """Get all direct child branches of a parent branch asynchronously."""
        if not hasattr(self._client, '_make_request_async'):
            raise TypeError("This method requires an asynchronous client")
        
        parent_branch_id = validate_identifier(parent_branch_id, "parent_branch_id")
        
        # Get all branches
        all_branch_ids = await self.list_branches_async(limit=1000)
        
        child_branches = []
        
        # Fetch each branch and check if it's a child of the parent
        for branch_id in all_branch_ids:
            try:
                branch = await self.get_branch_async(branch_id)
                if branch.parent_id and str(branch.parent_id) == parent_branch_id:
                    child_branches.append(branch)
            except Exception:
                continue
        
        # Sort by level and name
        child_branches.sort(key=lambda x: (x.level, x.name))
        
        return child_branches
    
    async def get_root_branches_async(self) -> List["Taxonomy"]:
        """Get all root branches asynchronously."""
        if not hasattr(self._client, '_make_request_async'):
            raise TypeError("This method requires an asynchronous client")
        
        # Get all branches
        all_branch_ids = await self.list_branches_async(limit=1000)
        
        root_branches = []
        
        # Fetch each branch and check if it's a root
        for branch_id in all_branch_ids:
            try:
                branch = await self.get_branch_async(branch_id)
                if not branch.parent_id:
                    root_branches.append(branch)
            except Exception:
                continue
        
        # Sort by name
        root_branches.sort(key=lambda x: x.name)
        
        return root_branches
