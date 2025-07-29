# resources/__init__.py

from .base import MySaleResource, PaginatedResponse
from .sku import SKU
from .product import Product
from .taxonomy import Taxonomy
from .shipping import Shipping
from .order import Order
from .returns import Returns

__all__ = [
    "MySaleResource",
    "PaginatedResponse",
    "SKU",
    "Product", 
    "Taxonomy",
    "Shipping",
    "Order",
    "Returns"
]
