# models/sku.py

from typing import Dict, List, Optional, Any, Union
from decimal import Decimal
from pydantic import BaseModel, Field, ConfigDict, field_validator
from uuid import UUID


class Weight(BaseModel):
    """Represents weight of SKU."""
    value: Decimal = Field(..., description="Weight value")
    unit: str = Field(default="g", description="Weight unit (g by default)")


class Volume(BaseModel):
    """Represents volume/dimensions of SKU."""
    height: Optional[Decimal] = Field(None, description="Height of SKU")
    width: Optional[Decimal] = Field(None, description="Width of SKU")
    length: Optional[Decimal] = Field(None, description="Length of SKU")
    unit: str = Field(default="cm", description="Dimension unit (cm by default)")


class StandardProductCode(BaseModel):
    """Represents a standard product code."""
    code: str = Field(..., description="Product code")
    type: str = Field(..., description="Code type: EAN, UPC, ISBN_10, ISBN_13, GTIN_14")
    
    @field_validator('type', mode='before')
    def validate_type(cls, v):
        allowed_types = ["EAN", "UPC", "ISBN_10", "ISBN_13", "GTIN_14"]
        if v not in allowed_types:
            raise ValueError(f"Type must be one of {allowed_types}")
        return v


class ShippingCountries(BaseModel):
    """Represents shipping country restrictions."""
    excluded_countries: Optional[List[str]] = Field(None, description="List of excluded country codes")
    allowed_countries: List[str] = Field(..., description="List of allowed country codes")
    
    @field_validator('allowed_countries', 'excluded_countries')
    def validate_country_codes(cls, v):
        if v is None:
            return v
        allowed_codes = ["AU", "NZ"]
        for code in v:
            if code not in allowed_codes:
                raise ValueError(f"Country code '{code}' not supported. Allowed: {allowed_codes}")
        return v


class SKURead(BaseModel):
    """Read model for MySale SKUs."""
    merchant_sku_id: str = Field(..., description="SKU ID provided by Merchant (Max 50)")
    sku_id: Optional[UUID] = Field(None, description="The unique MySale SKU ID")
    name: str = Field(..., description="SKU Name")
    description: str = Field(..., description="SKU Description. May contain HTML")
    country_of_origin: str = Field(..., description="Country of origin of SKU")
    size: Optional[str] = Field(None, description="SKU Size")
    weight: Weight = Field(..., description="Weight of SKU")
    volume: Optional[Volume] = Field(None, description="Volume of SKU")
    standard_product_codes: Optional[List[StandardProductCode]] = Field(
        None, description="List of Standard product codes"
    )
    barcodes: Optional[List[str]] = Field(None, description="Barcodes of SKU")
    brand: Optional[str] = Field(None, max_length=128, description="Brand name of SKU")
    taxonomy_id: UUID = Field(..., description="Internal ID of SKU Taxonomy")
    shipping_policies: Optional[List[UUID]] = Field(None, description="List of shipping policy IDs")
    shipping: Optional[ShippingCountries] = Field(None, description="Shipping country restrictions")
    enabled: bool = Field(default=False, description="If true then SKU is published for sales")


class SKUWrite(BaseModel):
    """Write model for MySale SKUs."""
    
    model_config = ConfigDict(
        populate_by_name=True,
        from_attributes=True,
        extra="forbid"
    )
    
    merchant_sku_id: Optional[str] = Field(None, max_length=50, description="SKU ID provided by Merchant")
    name: Optional[str] = Field(None, description="SKU Name")
    description: Optional[str] = Field(None, description="SKU Description. May contain HTML")
    country_of_origin: Optional[str] = Field(None, description="Country of origin of SKU")
    size: Optional[str] = Field(None, description="SKU Size")
    weight: Optional[Weight] = Field(None, description="Weight of SKU")
    volume: Optional[Volume] = Field(None, description="Volume of SKU")
    standard_product_codes: Optional[List[StandardProductCode]] = Field(
        None, description="List of Standard product codes"
    )
    barcodes: Optional[List[str]] = Field(None, description="Barcodes of SKU")
    brand: Optional[str] = Field(None, max_length=128, description="Brand name of SKU")
    taxonomy_id: Optional[UUID] = Field(None, description="Internal ID of SKU Taxonomy")
    shipping_policies: Optional[List[UUID]] = Field(None, description="List of shipping policy IDs")
    shipping: Optional[ShippingCountries] = Field(None, description="Shipping country restrictions")


class SKUCreateWrite(BaseModel):
    """Create model for MySale SKUs with required fields."""
    
    model_config = ConfigDict(
        populate_by_name=True,
        from_attributes=True,
        extra="forbid"
    )
    
    merchant_sku_id: str = Field(..., max_length=50, description="SKU ID provided by Merchant")
    name: str = Field(..., description="SKU Name")
    description: str = Field(..., description="SKU Description. May contain HTML")
    country_of_origin: str = Field(..., description="Country of origin of SKU")
    weight: Weight = Field(..., description="Weight of SKU")
    taxonomy_id: UUID = Field(..., description="Internal ID of SKU Taxonomy")
    size: Optional[str] = Field(None, description="SKU Size")
    volume: Optional[Volume] = Field(None, description="Volume of SKU")
    standard_product_codes: Optional[List[StandardProductCode]] = Field(
        None, description="List of Standard product codes"
    )
    barcodes: Optional[List[str]] = Field(None, description="Barcodes of SKU")
    brand: Optional[str] = Field(None, max_length=128, description="Brand name of SKU")
    shipping_policies: Optional[List[UUID]] = Field(None, description="List of shipping policy IDs")
    shipping: Optional[ShippingCountries] = Field(None, description="Shipping country restrictions")


# SKU Images Models

class SKUImage(BaseModel):
    """Represents a single SKU image."""
    merchant_url: str = Field(..., description="Original Merchant URL of image to upload")
    url: Optional[str] = Field(None, description="URL of image at MySale Marketplace CDN (read-only)")
    error: Optional[str] = Field(None, description="Error message if image failed to load")


class SKUImages(BaseModel):
    """Container for SKU images."""
    images: List[SKUImage] = Field(..., description="List of SKU images")


# SKU Prices Models

class PriceValue(BaseModel):
    """Represents a price value with currency."""
    currency: str = Field(..., description="Price currency")
    value: Decimal = Field(..., description="Price value")
    
    @field_validator('currency')
    def validate_currency(cls, v):
        allowed_currencies = ["AUD", "NZD", "MYR", "SGD"]
        if v.upper() not in allowed_currencies:
            raise ValueError(f"Currency must be one of {allowed_currencies}")
        return v.upper()


class SKUShopPrice(BaseModel):
    """Represents shop-specific pricing."""
    shop_code: str = Field(..., description="Shop code (BN, NZ, MY, SI)")
    cost: PriceValue = Field(..., description="Cost price")
    sell: PriceValue = Field(..., description="Sell price")
    rrp: PriceValue = Field(..., description="RRP price")
    currency: str = Field(..., description="Currency for this shop")
    value: Decimal = Field(..., description="Value for this shop")
    
    @field_validator('shop_code')
    def validate_shop_code(cls, v):
        allowed_shops = ["BN", "NZ", "MY", "SI"]
        if v.upper() not in allowed_shops:
            raise ValueError(f"Shop code must be one of {allowed_shops}")
        return v.upper()


class SKUPrice(BaseModel):
    """Represents SKU pricing."""
    cost: PriceValue = Field(..., description="Cost price")
    sell: PriceValue = Field(..., description="Sell price")
    rrp: PriceValue = Field(..., description="RRP price")
    shop_prices: Optional[List[SKUShopPrice]] = Field(None, description="Shop-specific prices")


class SKUPrices(BaseModel):
    """Container for SKU prices."""
    prices: SKUPrice = Field(..., description="SKU pricing information")


# SKU Inventory Models

class LocationQuantity(BaseModel):
    """Represents inventory at a specific location."""
    location: str = Field(..., description="Location name")
    quantity: int = Field(..., description="Quantity available at location")


class SKUInventory(BaseModel):
    """Container for SKU inventory."""
    inventory: List[LocationQuantity] = Field(..., description="Inventory by location")


# SKU Attributes Models

class SKUAttribute(BaseModel):
    """Represents a single SKU attribute."""
    name: str = Field(..., description="Attribute name")
    value: str = Field(..., description="Attribute value")
    is_locked: bool = Field(default=False, description="Whether attribute is locked")


class SKUAttributes(BaseModel):
    """Container for SKU attributes."""
    sku_id: Optional[UUID] = Field(None, description="MySale SKU ID")
    attributes: List[SKUAttribute] = Field(..., description="List of SKU attributes")


# SKU Statistics Model

class SKUStatistics(BaseModel):
    """Represents SKU statistics."""
    total: Optional[int] = Field(None, description="Total SKUs count in account")
    archived: Optional[int] = Field(None, description="Archived SKUs count in account")


# SKU List Models

class SKUListItem(BaseModel):
    """Represents a SKU in list responses."""
    merchant_sku_id: str = Field(..., description="SKU ID provided by Merchant")
    sku_id: UUID = Field(..., description="The unique MySale SKU ID")


class SKUList(BaseModel):
    """Container for SKU list responses."""
    SKUs: List[SKUListItem] = Field(..., description="List of SKUs")
