# models/order.py

from typing import Dict, List, Optional, Any
from decimal import Decimal
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict, field_validator
from uuid import UUID


class Price(BaseModel):
    """Represents a price with currency."""
    currency: str = Field(..., description="Alpha-3 ISO currency code")
    amount: Decimal = Field(..., description="Cost amount")
    
    @field_validator('currency')
    def validate_currency(cls, v):
        allowed_currencies = ["AUD", "NZD", "MYR", "SGD"]
        if v.upper() not in allowed_currencies:
            raise ValueError(f"Currency must be one of {allowed_currencies}")
        return v.upper()


class Address(BaseModel):
    """Represents an address."""
    country_code: str = Field(..., description="Alpha-2 ISO country code")
    address_line: str = Field(..., description="Address info")
    city: str = Field(..., description="City of the address")
    state: Optional[str] = Field(None, description="State of the address")
    postcode: str = Field(..., description="Post code of the address")
    authority_to_leave: Optional[str] = Field(None, description="Permission to leave parcel without signature")


class PickupPoint(BaseModel):
    """Represents a pickup point."""
    id: str = Field(..., description="Internal pickup point identifier")
    carrier: str = Field(..., description="Post service name")
    name: str = Field(..., description="Pickup point name")
    address_line: str = Field(..., description="Pickup point address line")
    city: str = Field(..., description="City of the address")
    state: Optional[str] = Field(None, description="State of the address")
    postcode: str = Field(..., description="Post code of the address")


class Recipient(BaseModel):
    """Represents order recipient."""
    name: str = Field(..., description="The name of the person")
    email: str = Field(..., description="The email for the person")
    phone_number: Optional[str] = Field(None, description="The phone number for the person")
    address: Address = Field(..., description="Where the order is being shipped to")
    billing_address: Optional[Address] = Field(None, description="Where the bill to be sent to")
    pickup_point: Optional[PickupPoint] = Field(None, description="Optional pickup point identification")


class OrderItem(BaseModel):
    """Represents an order item."""
    order_item_id: UUID = Field(..., description="MySale unique ID for a given Merchant order item")
    merchant_order_item_id: Optional[str] = Field(None, description="Optional Merchant supplied order item ID")
    sku_id: UUID = Field(..., description="MySale unique ID for SKU")
    merchant_sku_id: str = Field(..., description="SKU ID provided by Merchant")
    sku_qty: int = Field(..., description="Quantity of this SKU")
    item_cost_price: Price = Field(..., description="Price the Merchant sets")
    item_sell_price: Price = Field(..., description="Price the customer pays")
    item_shipping_price: Optional[Price] = Field(None, description="Price of delivery")


class OrderRead(BaseModel):
    """Read model for MySale Orders."""
    order_id: UUID = Field(..., description="The unique order identifier")
    merchant_order_id: Optional[str] = Field(None, description="The order identifier given by Merchant")
    customer_order_reference: str = Field(..., description="MySale human readable order ID number")
    order_date: datetime = Field(..., description="The date the merchant order was placed")
    order_status: str = Field(..., description="Current status of the order")
    completion_kind: Optional[str] = Field(None, description="How the order was completed (for completed orders)")
    recipient: Recipient = Field(..., description="Who is receiving the order")
    order_items: List[OrderItem] = Field(..., description="List of Order items (SKU + QTY)")
    order_shipping_price: Price = Field(..., description="The order shipping/delivery price")
    shipping_policy_id: UUID = Field(..., description="The shipping policy ID")
    shipping_policy_name: str = Field(..., description="The shipping policy name")
    
    @field_validator('order_status', mode='before')
    def validate_order_status(cls, v):
        allowed_statuses = ["new", "acknowledged", "inprogress", "complete", "incomplete"]
        if v not in allowed_statuses:
            raise ValueError(f"Order status must be one of {allowed_statuses}")
        return v


class OrderListItem(BaseModel):
    """Represents an order in list responses."""
    order_id: UUID = Field(..., description="The unique order identifier")
    merchant_order_id: Optional[str] = Field(None, description="The order identifier given by Merchant")


class OrderList(BaseModel):
    """Container for order list responses."""
    orders: List[OrderListItem] = Field(..., description="List of orders")


# Order Acknowledgement Models

class AcknowledgementOrderItem(BaseModel):
    """Represents an order item in acknowledgement."""
    order_item_id: UUID = Field(..., description="MySale unique ID for a given Merchant order item")
    merchant_order_item_id: Optional[str] = Field(None, description="Optional Merchant supplied order item ID")


class OrderAcknowledgement(BaseModel):
    """Model for order acknowledgement."""
    merchant_order_id: Optional[str] = Field(None, max_length=100, description="Optional Merchant supplied order ID")
    order_items: Optional[List[AcknowledgementOrderItem]] = Field(None, description="List of Order items")


# Shipment Models

class ShipmentItem(BaseModel):
    """Represents a shipment item."""
    merchant_shipment_item_id: Optional[str] = Field(None, description="Shipment Item ID provided by Merchant")
    merchant_sku_id: str = Field(..., description="SKU ID provided by Merchant")
    sku_id: UUID = Field(..., description="MySale unique ID for SKU")
    sku_qty: int = Field(..., description="Quantity of this SKU to be shipped")


class Shipment(BaseModel):
    """Represents a shipment."""
    shipment_id: Optional[UUID] = Field(None, description="MySale unique ID for Shipment")
    merchant_shipment_id: Optional[str] = Field(None, description="Shipment ID provided by Merchant")
    tracking_number: Optional[str] = Field(None, description="Merchant tracking number")
    delivery_option: Optional[str] = Field(None, description="Delivery option")
    carrier: Optional[str] = Field(None, description="Post service name")
    carrier_shipment_method: Optional[str] = Field(None, description="Post service option")
    dispatch_date: Optional[datetime] = Field(None, description="Date/Time that a given shipment was shipped")
    expected_delivery_date: Optional[datetime] = Field(None, description="Date/Time that a given shipment is expected to be delivered")
    shipment_items: List[ShipmentItem] = Field(..., description="List of items to be shipped")


class ShipmentCreate(BaseModel):
    """Model for creating a shipment."""
    
    model_config = ConfigDict(
        populate_by_name=True,
        from_attributes=True,
        extra="forbid"
    )
    
    merchant_shipment_id: Optional[str] = Field(None, description="Shipment ID provided by Merchant")
    tracking_number: Optional[str] = Field(None, description="Merchant tracking number")
    delivery_option: Optional[str] = Field(None, description="Delivery option")
    carrier: Optional[str] = Field(None, description="Post service name")
    carrier_shipment_method: Optional[str] = Field(None, description="Post service option")
    dispatch_date: Optional[datetime] = Field(None, description="Date/Time that a given shipment was shipped")
    expected_delivery_date: Optional[datetime] = Field(None, description="Date/Time that a given shipment is expected to be delivered")
    shipment_items: List[ShipmentItem] = Field(..., description="List of items to be shipped")


class ShipmentList(BaseModel):
    """Container for shipment list responses."""
    shipments: List[Shipment] = Field(..., description="List of shipments")


# Cancellation Models

class CancelledItem(BaseModel):
    """Represents a cancelled item."""
    merchant_cancel_item_id: Optional[str] = Field(None, description="ID of Cancellation Item provided by Merchant")
    merchant_sku_id: str = Field(..., description="SKU ID provided by Merchant")
    sku_id: UUID = Field(..., description="MySale unique ID for SKU")
    sku_qty: int = Field(..., description="Quantity of this SKU to be cancelled")
    cancellation_reason: str = Field(..., description="Reason of cancellation")
    
    @field_validator('cancellation_reason', mode='before')
    def validate_cancellation_reason(cls, v):
        allowed_reasons = [
            "no_stock", "fraud_high_risk", "fraud_charge_back", "fraud_confirmed",
            "customer_cancelled_sale_error", "customer_cancelled_delayed", 
            "customer_cancelled_change_of_mind", "unfulfillable_address", "other"
        ]
        if v not in allowed_reasons:
            raise ValueError(f"Cancellation reason must be one of {allowed_reasons}")
        return v


class Cancellation(BaseModel):
    """Represents a cancellation."""
    cancellation_id: Optional[UUID] = Field(None, description="MySale unique ID for Cancellation")
    cancelled_items: List[CancelledItem] = Field(..., description="List of items to be cancelled")


class CancellationCreate(BaseModel):
    """Model for creating a cancellation."""
    
    model_config = ConfigDict(
        populate_by_name=True,
        from_attributes=True,
        extra="forbid"
    )
    
    cancelled_items: List[CancelledItem] = Field(..., description="List of items to be cancelled")


class CancellationList(BaseModel):
    """Container for cancellation list responses."""
    cancellations: List[Cancellation] = Field(..., description="List of cancellations")
