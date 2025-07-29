# models/taxonomy.py

from typing import List, Optional
from pydantic import BaseModel, Field
from uuid import UUID


class TaxonomyBranch(BaseModel):
    """Represents a taxonomy branch."""
    branch_id: UUID = Field(..., description="The unique MySale Taxonomy branch identifier")
    parent_id: Optional[UUID] = Field(None, description="The unique MySale Taxonomy branch parent identifier")
    level: int = Field(..., description="Level of the Taxonomy branch in the Taxonomy tree")
    name: str = Field(..., description="Name of the Taxonomy branch")
    keywords: List[str] = Field(default_factory=list, description="List of keywords for the Taxonomy branch")
    is_main_category: bool = Field(default=False, description="Obsolete field")


class TaxonomyBranches(BaseModel):
    """Container for taxonomy branch list responses."""
    branches: List[str] = Field(..., description="List of taxonomy branch IDs (GUID)")
