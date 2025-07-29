# models/shipping.py

from typing import List, Optional, Any, Dict
from pydantic import BaseModel, Field
from uuid import UUID


class ShippingRuleParameters(BaseModel):
    """Represents shipping rule parameters."""
    result: Dict[str, Any] = Field(..., description="The set of parameters")
    shipping_price_amount: Optional[float] = Field(None, description="The shipping price amount")
    shipping_time_from: Optional[int] = Field(None, description="The minimum delivery time in business days")
    shipping_time_to: Optional[int] = Field(None, description="The maximum delivery time in business days")
    shipping_price_additional_charge_type: Optional[str] = Field(None, description="The additional delivery price charge type")
    shipping_cost_additional_charge_type: Optional[str] = Field(None, description="The additional delivery cost charge type")


class ShippingRule(BaseModel):
    """Represents a domestic shipping rule."""
    type: str = Field(..., description="The type of the rule")
    shipping_zones: List[UUID] = Field(..., description="The array of shipping zones which will follow this rule")
    rule_based_on: str = Field(..., description="The name of a parent rule")
    parameters: List[ShippingRuleParameters] = Field(..., description="The rule parameters")


class DomesticShipping(BaseModel):
    """Represents domestic shipping configuration."""
    excluded_shipping_zones: Optional[List[UUID]] = Field(default_factory=list, description="The list of shipping zones which will be excluded")
    rules: List[ShippingRule] = Field(..., description="The array of shipping rules")


class ShippingPolicy(BaseModel):
    """Represents a shipping policy."""
    shipping_policy_id: UUID = Field(..., description="The unique Shipping policy ID")
    name: str = Field(..., description="The Shipping policy name provided by Merchant")
    dispatch_location_ids: List[UUID] = Field(..., description="The ids of dispatch locations covered by this policy")
    enabled: bool = Field(..., description="Flag that this policy is active")
    domestic_shipping: DomesticShipping = Field(..., description="Domestic shipping rules")
    shipping_option: str = Field(..., description="The shipping option")
    is_default: bool = Field(..., description="The flag that this policy will apply to all undefined locations")


class ShippingPolicyList(BaseModel):
    """Container for shipping policy list responses."""
    policies: List[ShippingPolicy] = Field(..., description="List of shipping policies")
