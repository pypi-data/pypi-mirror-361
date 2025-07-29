# models/returns.py

from typing import Dict, List, Optional, Any
from decimal import Decimal
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict, field_validator
from uuid import UUID
from .order import Price, OrderItem


class Customer(BaseModel):
    """Represents customer information."""
    id: UUID = Field(..., description="The unique MySale Customer ID")
    name: str = Field(..., description="Customer name")
    email: str = Field(..., description="Customer email")


class ReturnAttachment(BaseModel):
    """Represents a return attachment."""
    type: str = Field(..., description="Attachment type (e.g., image/png)")
    title: Optional[str] = Field(None, description="Attachment title")
    description: Optional[str] = Field(None, description="Attachment description")
    url: str = Field(..., description="URL to the attachment")


class ReturnRead(BaseModel):
    """Read model for MySale Returns."""
    id: UUID = Field(..., description="The unique MySale Return ID")
    ran: str = Field(..., description="The return RAN")
    merchant_return_id: Optional[str] = Field(None, description="The return ID assigned by merchant")
    order_id: Optional[UUID] = Field(None, description="The unique MySale Order ID")
    customer_order_reference: Optional[str] = Field(None, description="The customer order reference")
    status: str = Field(..., description="The return status")
    reason_for_return: Optional[str] = Field(None, description="The customer's reason of return")
    sale_id: Optional[UUID] = Field(None, description="The unique MySale Sale ID")
    sale_name: Optional[str] = Field(None, description="The sale name associated with return item")
    customer: Customer = Field(..., description="The customer details")
    items: Optional[List[OrderItem]] = Field(None, description="The list of returned items")
    attachments: Optional[List[ReturnAttachment]] = Field(None, description="The list of attached images")
    notes: Optional[str] = Field(None, description="The internal staff notes about return")
    items_amount: Optional[Price] = Field(None, description="The total items price")
    shipping_amount: Optional[Price] = Field(None, description="The total shipping price")
    total_amount: Optional[Price] = Field(None, description="The total amount")
    amount_to_refund: Optional[Price] = Field(None, description="The amount to refund")
    amount_refunded: Optional[Price] = Field(None, description="The actual refunded amount")
    
    @field_validator('status', mode='before')
    def validate_status(cls, v):
        allowed_statuses = ["pending", "approved", "received", "closed", "declined"]
        if v not in allowed_statuses:
            raise ValueError(f"Return status must be one of {allowed_statuses}")
        return v


class ReturnListItem(BaseModel):
    """Represents a return in list responses."""
    id: UUID = Field(..., description="The return ID")
    ran: str = Field(..., description="The return RAN")
    merchant_return_id: Optional[str] = Field(None, description="The return ID assigned by merchant")
    customer: Customer = Field(..., description="The customer info")
    customer_order_reference: Optional[str] = Field(None, description="The customer order reference")
    status: str = Field(..., description="The return status")


class ReturnList(BaseModel):
    """Container for return list responses."""
    returns: List[ReturnListItem] = Field(..., description="List of returns")


class ReturnUpdate(BaseModel):
    """Model for updating a return."""
    
    model_config = ConfigDict(
        populate_by_name=True,
        from_attributes=True,
        extra="forbid"
    )
    
    merchant_return_id: Optional[str] = Field(None, description="The return ID assigned by merchant")
    notes: Optional[str] = Field(None, description="The internal staff notes about return")


class PartialRefund(BaseModel):
    """Model for partial refund."""
    
    model_config = ConfigDict(
        populate_by_name=True,
        from_attributes=True,
        extra="forbid"
    )
    
    amount_to_refund: Price = Field(..., description="The amount to refund")


# Ticket Models

class TicketCustomer(BaseModel):
    """Represents customer in ticket context."""
    id: UUID = Field(..., description="The unique MySale Customer ID")
    name: str = Field(..., description="Customer name")
    email: str = Field(..., description="Customer email")


class TicketListItem(BaseModel):
    """Represents a ticket in list responses."""
    id: int = Field(..., description="The MySale Ticket ID")
    status: str = Field(..., description="The ticket status")
    customer: TicketCustomer = Field(..., description="The customer info")
    subject: str = Field(..., description="The ticket subject")
    order_id: Optional[UUID] = Field(None, description="The MySale Order ID associated with ticket")
    customer_order_reference: Optional[str] = Field(None, description="The customer order reference number")
    is_new: bool = Field(..., description="The flag showing ticket was recently created")


class TicketAttachment(BaseModel):
    """Represents a ticket attachment."""
    url: str = Field(..., description="URL to the attachment")


class TicketMessage(BaseModel):
    """Represents a ticket message."""
    id: UUID = Field(..., description="The unique message ID")
    message: str = Field(..., description="Message text")
    date: datetime = Field(..., description="Message date")
    is_answer: bool = Field(..., description="Whether this is an answer")
    is_seller: bool = Field(..., description="Whether the sender is a seller")
    attachments: Optional[List[TicketAttachment]] = Field(None, description="Message attachments")


class TicketRead(BaseModel):
    """Read model for tickets."""
    id: int = Field(..., description="The ticket ID")
    status: str = Field(..., description="The ticket status")
    customer: TicketCustomer = Field(..., description="The customer info")
    messages: List[TicketMessage] = Field(..., description="The ticket messages")
    last_message: str = Field(..., description="The text of last message")
    last_message_date: datetime = Field(..., description="The date of the last message")
    return_id: UUID = Field(..., description="The MySale Return ID")


class TicketCreate(BaseModel):
    """Model for creating a ticket."""
    
    model_config = ConfigDict(
        populate_by_name=True,
        from_attributes=True,
        extra="forbid"
    )
    
    message: str = Field(..., description="Text of the message")
    attachments: Optional[List[TicketAttachment]] = Field(None, description="List of attached files")
