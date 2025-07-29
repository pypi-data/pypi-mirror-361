# models/product.py

from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field, ConfigDict
from uuid import UUID


class ProductSKU(BaseModel):
    """Represents a SKU attached to a product."""
    merchant_sku_id: str = Field(..., description="SKU ID provided by Merchant")
    sku_id: Optional[UUID] = Field(None, description="The unique MySale SKU ID")


class ProductRead(BaseModel):
    """Read model for MySale Products."""
    merchant_product_id: str = Field(..., description="ID of the Product provided by Merchant")
    product_id: Optional[UUID] = Field(None, description="The unique MySale Product identifier")
    name: str = Field(..., description="Name of Product")
    description: str = Field(..., description="Description of Product")
    skus: List[ProductSKU] = Field(default_factory=list, description="Attached SKUs")


class ProductWrite(BaseModel):
    """Write model for MySale Products."""
    
    model_config = ConfigDict(
        populate_by_name=True,
        from_attributes=True,
        extra="forbid"
    )
    
    merchant_product_id: Optional[str] = Field(None, description="ID of the Product provided by Merchant")
    name: Optional[str] = Field(None, description="Name of Product")
    description: Optional[str] = Field(None, description="Description of Product")
    skus: Optional[List[ProductSKU]] = Field(None, description="Attached SKUs")


class ProductCreateWrite(BaseModel):
    """Create model for MySale Products with required fields."""
    
    model_config = ConfigDict(
        populate_by_name=True,
        from_attributes=True,
        extra="forbid"
    )
    
    merchant_product_id: str = Field(..., description="ID of the Product provided by Merchant")
    name: str = Field(..., description="Name of Product")
    description: str = Field(..., description="Description of Product")
    skus: List[ProductSKU] = Field(default_factory=list, description="Attached SKUs")


# Product Images Models

class ProductImage(BaseModel):
    """Represents a single product image."""
    merchant_url: str = Field(..., description="Original Merchant URL of image")
    url: Optional[str] = Field(None, description="URL of image at MySale Marketplace CDN")
    error: Optional[str] = Field(None, description="Error message if image failed to load")


class ProductImages(BaseModel):
    """Container for product images."""
    images: List[ProductImage] = Field(..., description="List of product images")


# Product List Models

class ProductListItem(BaseModel):
    """Represents a product in list responses."""
    merchant_product_id: str = Field(..., description="ID of the Product provided by Merchant")
    product_id: UUID = Field(..., description="The unique Product identifier")


class ProductList(BaseModel):
    """Container for product list responses."""
    products: List[ProductListItem] = Field(..., description="List of products")
