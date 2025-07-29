# MySale API SDK

A comprehensive Python SDK for integrating with the MySale Marketplace API. This SDK provides both synchronous and asynchronous clients with full support for all MySale API endpoints including SKUs, Products, Orders, Returns, Taxonomy, and Shipping management.

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Table of Contents

- [Features](#features)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Authentication](#authentication)
- [Usage Examples](#usage-examples)
- [API Reference](#api-reference)
- [Error Handling](#error-handling)
- [Rate Limiting](#rate-limiting)
- [Development](#development)
- [License](#license)

## Features

- **Complete API Coverage**: Support for all MySale API endpoints
- **Async/Sync Support**: Both synchronous and asynchronous clients
- **Type Safety**: Full type hints with Pydantic models
- **Rate Limiting**: Built-in rate limiting to respect API limits
- **Error Handling**: Comprehensive error handling with specific exception types
- **Pagination**: Automatic pagination support for list endpoints
- **Validation**: Request/response validation using Pydantic models
- **Retry Logic**: Automatic retry for rate-limited and server error responses

### Supported Resources

- **SKUs**: Create, read, update, and manage product SKUs
- **Products**: Product management and grouping
- **Orders**: Order lifecycle management (new, acknowledged, shipped, cancelled)
- **Returns**: Returns and refunds management
- **Shipping**: Shipping policies and configuration
- **Taxonomy**: Product categorization and taxonomy

## Installation

```bash
pip install mysale-api-sdk
```

### Development Installation

```bash
git clone https://github.com/DuneRaccoon/mysale-api-sdk.git
cd mysale-api-sdk
pip install -e .
```

## Quick Start

```python
from mysale_api import MySaleClient, MySaleAsyncClient

# Synchronous client
client = MySaleClient(api_token="your_api_token_here")

# Get all new orders
new_orders = client.orders.list_new_orders()
print(f"Found {len(new_orders)} new orders")

# Get a specific SKU
sku = client.skus.get_by_merchant_id("your-sku-id")
print(f"SKU: {sku.name}")

# Asynchronous client
import asyncio

async def main():
    async_client = MySaleAsyncClient(api_token="your_api_token_here")
    
    # Get orders asynchronously
    orders = await async_client.orders.list_new_orders_async()
    print(f"Found {len(orders)} new orders")
    
    await async_client.close()

asyncio.run(main())
```

## Authentication

The MySale API uses Bearer token authentication. You'll need to obtain an API token from your MySale merchant dashboard.

```python
from mysale_api import MySaleClient

client = MySaleClient(
    api_token="your_api_token_here",
    base_url="https://api.mysale.com",  # Optional: defaults to MySale API URL
    timeout=60.0,  # Optional: request timeout in seconds
    max_retries=5  # Optional: maximum retry attempts
)
```

## Usage Examples

### SKU Management

```python
from mysale_api import MySaleClient
from mysale_api.models import SKUCreateWrite, Weight
from uuid import uuid4

client = MySaleClient(api_token="your_token")

# Create a new SKU
sku_data = SKUCreateWrite(
    merchant_sku_id="MY-SKU-001",
    name="Premium T-Shirt",
    description="High quality cotton t-shirt",
    country_of_origin="AU",
    weight=Weight(value=0.3, unit="kg"),
    taxonomy_id=uuid4(),  # Use actual taxonomy ID
)

new_sku = client.skus.create_sku(sku_data)
print(f"Created SKU: {new_sku.merchant_sku_id}")

# Update SKU pricing
from mysale_api.models import SKUPrices, SKUPrice, PriceValue

price_data = SKUPrices(
    prices=SKUPrice(
        cost=PriceValue(currency="AUD", value=10.00),
        sell=PriceValue(currency="AUD", value=25.00),
        rrp=PriceValue(currency="AUD", value=30.00)
    )
)

client.skus.upload_prices("MY-SKU-001", price_data)

# List all SKUs with pagination
skus_page = client.skus.list_skus(offset=0, limit=50, paginated=True)
print(f"Total SKUs: {skus_page.total_count}")

for sku in skus_page.items:
    print(f"- {sku.merchant_sku_id}: {sku.name}")
```

### Order Management

```python
# Get new orders that need processing
new_orders = client.orders.list_new_orders(limit=100)

for order_item in new_orders:
    # Get full order details
    order = client.orders.get_order(str(order_item.order_id))
    
    print(f"Order {order.customer_order_reference}:")
    print(f"  Customer: {order.recipient.name}")
    print(f"  Items: {len(order.order_items)}")
    print(f"  Total: {order.order_shipping_price.currency} {order.order_shipping_price.amount}")

# Acknowledge an order
from mysale_api.models import OrderAcknowledgement

acknowledgement = OrderAcknowledgement(
    merchant_order_id="MY-ORDER-001",
    order_items=[]  # Optional: can specify merchant order item IDs
)

client.orders.acknowledge_order(str(order.order_id), acknowledgement)

# Create a shipment
from mysale_api.models import ShipmentCreate, ShipmentItem
from datetime import datetime

shipment_data = ShipmentCreate(
    merchant_shipment_id="SHIP-001",
    tracking_number="TR123456789",
    carrier="Australia Post",
    carrier_shipment_method="Express",
    dispatch_date=datetime.now(),
    shipment_items=[
        ShipmentItem(
            merchant_sku_id="MY-SKU-001",
            sku_id=order.order_items[0].sku_id,
            sku_qty=1
        )
    ]
)

shipment_id = client.orders.create_shipment(str(order.order_id), shipment_data)
print(f"Created shipment: {shipment_id}")
```

### Returns Management

```python
# Get pending returns
pending_returns = client.returns.list_pending_returns()

for return_item in pending_returns:
    # Get full return details
    return_detail = client.returns.get_return(str(return_item.id))
    
    print(f"Return {return_detail.ran}:")
    print(f"  Customer: {return_detail.customer.name}")
    print(f"  Reason: {return_detail.reason_for_return}")
    print(f"  Amount: {return_detail.total_amount.currency if return_detail.total_amount else 'N/A'}")

# Approve a return
approved_return = client.returns.approve_return(str(return_detail.id))
print(f"Approved return: {approved_return.ran}")

# Process partial refund
from mysale_api.models import PartialRefund, Price

partial_refund = PartialRefund(
    amount_to_refund=Price(currency="AUD", amount=15.50)
)

client.returns.partial_refund_return(str(return_detail.id), partial_refund)
```

### Product Management

```python
# Create a product
from mysale_api.models import ProductCreateWrite, ProductSKU

product_data = ProductCreateWrite(
    merchant_product_id="PROD-001",
    name="T-Shirt Collection",
    description="Premium cotton t-shirts in various colors",
    skus=[
        ProductSKU(merchant_sku_id="MY-SKU-001"),
        ProductSKU(merchant_sku_id="MY-SKU-002")
    ]
)

product = client.products.create_product(product_data)
print(f"Created product: {product.name}")
```

### Shipping Policies

```python
# Get all shipping policies
policies = client.shipping.list_policies()

for policy in policies:
    print(f"Policy: {policy.name}")
    print(f"  Enabled: {policy.enabled}")
    print(f"  Default: {policy.is_default}")
    print(f"  Locations: {len(policy.dispatch_location_ids)}")

# Get shipping coverage analysis
coverage = client.shipping.analyze_shipping_coverage()
print(f"Total policies: {coverage['total_policies']}")
print(f"Enabled policies: {coverage['enabled_policies']}")
```

### Taxonomy Navigation

```python
# Get root categories
root_branches = client.taxonomy.get_root_branches()

for branch in root_branches:
    print(f"Category: {branch.name}")
    
    # Get child categories
    children = client.taxonomy.get_child_branches(str(branch.branch_id))
    for child in children:
        print(f"  - {child.name}")

# Search for categories
search_results = client.taxonomy.search_branches("clothing")
for result in search_results:
    print(f"Found: {result.name} (Level {result.level})")
```

### Async Usage

```python
import asyncio
from mysale_api import MySaleAsyncClient

async def process_orders():
    client = MySaleAsyncClient(api_token="your_token")
    
    try:
        # Get new orders
        new_orders = await client.orders.list_new_orders_async(limit=50)
        
        # Process each order
        for order_item in new_orders:
            order = await client.orders.get_order_async(str(order_item.order_id))
            print(f"Processing order: {order.customer_order_reference}")
            
            # Acknowledge the order
            await client.orders.acknowledge_order_async(
                str(order.order_id),
                {"merchant_order_id": f"INTERNAL-{order.customer_order_reference}"}
            )
    
    finally:
        await client.close()

# Run async function
asyncio.run(process_orders())
```

## API Reference

### Client Classes

#### MySaleClient (Synchronous)
```python
MySaleClient(
    api_token: str,
    base_url: str = "https://api.mysale.com",
    timeout: float = 60.0,
    max_retries: int = 5
)
```

#### MySaleAsyncClient (Asynchronous)
```python
MySaleAsyncClient(
    api_token: str,
    base_url: str = "https://api.mysale.com", 
    timeout: float = 60.0,
    max_retries: int = 5
)
```

### Resource Endpoints

#### SKUs (`client.skus`)
- `get_by_merchant_id(merchant_sku_id)` - Get SKU by merchant ID
- `create_sku(data)` - Create new SKU
- `update_by_merchant_id(merchant_sku_id, data)` - Update SKU
- `list_skus(offset, limit, exclude_archived, paginated)` - List SKUs
- `upload_prices(merchant_sku_id, prices)` - Update SKU pricing
- `upload_inventory(merchant_sku_id, inventory)` - Update inventory
- `upload_images(merchant_sku_id, images)` - Upload images
- `enable(merchant_sku_id)` - Enable SKU for sale
- `disable(merchant_sku_id)` - Disable SKU

#### Orders (`client.orders`)
- `list_new_orders(offset, limit, paginated)` - Get new orders
- `list_acknowledged_orders(offset, limit, paginated)` - Get acknowledged orders
- `list_inprogress_orders(offset, limit, paginated)` - Get in-progress orders
- `list_completed_orders(offset, limit, paginated)` - Get completed orders
- `get_order(order_id)` - Get specific order
- `acknowledge_order(order_id, acknowledgement)` - Acknowledge order
- `create_shipment(order_id, shipment)` - Create shipment
- `get_shipments(order_id)` - Get order shipments
- `create_cancellation(order_id, cancellation)` - Cancel order items

#### Returns (`client.returns`)
- `list_pending_returns(offset, limit, paginated)` - Get pending returns
- `list_awaiting_returns(offset, limit, paginated)` - Get approved returns
- `get_return(return_id)` - Get specific return
- `approve_return(return_id)` - Approve return
- `decline_return(return_id)` - Decline return
- `receive_return(return_id)` - Mark return as received
- `partial_refund_return(return_id, refund_data)` - Process partial refund
- `full_refund_return(return_id)` - Process full refund

#### Products (`client.products`)
- `get_by_merchant_id(merchant_product_id)` - Get product by merchant ID
- `create_product(data)` - Create new product
- `update_by_merchant_id(merchant_product_id, data)` - Update product
- `list_products(offset, limit, paginated)` - List products

#### Shipping (`client.shipping`)
- `list_policies(paginated)` - Get shipping policies
- `get_policy(shipping_policy_id)` - Get specific policy
- `get_enabled_policies()` - Get enabled policies only
- `analyze_shipping_coverage()` - Analyze shipping coverage

#### Taxonomy (`client.taxonomy`)
- `get_branch(branch_id)` - Get taxonomy branch
- `list_branches(offset, limit, paginated)` - List all branches
- `search_branches(keyword)` - Search branches by keyword
- `get_root_branches()` - Get root categories
- `get_child_branches(parent_branch_id)` - Get child categories

## Error Handling

The SDK provides specific exception types for different error scenarios:

```python
from mysale_api import (
    MySaleAPIError,
    AuthenticationError,
    ValidationError,
    NotFoundError,
    RateLimitError,
    ServerError
)

try:
    client = MySaleClient(api_token="invalid_token")
    orders = client.orders.list_new_orders()
    
except AuthenticationError:
    print("Invalid API token")
except RateLimitError as e:
    print(f"Rate limited. Retry after: {e.retry_after} seconds")
except NotFoundError:
    print("Resource not found")
except ValidationError as e:
    print(f"Validation error: {e.message}")
except ServerError:
    print("Server error occurred")
except MySaleAPIError as e:
    print(f"API error: {e.message}")
```

### Exception Types

- `MySaleAPIError` - Base exception for all API errors
- `AuthenticationError` - Invalid credentials (401)
- `ForbiddenError` - Access forbidden (403)
- `NotFoundError` - Resource not found (404)
- `ValidationError` - Request validation failed (422)
- `RateLimitError` - Rate limit exceeded (429)
- `ServerError` - Server error (5xx)
- `ConflictError` - Resource conflict (409)

## Rate Limiting

The SDK automatically handles MySale's rate limits:
- **Burst**: 90 hits/second over 5-second period
- **Average**: 60 hits/second over 2-minute period

The SDK uses conservative limits (50 calls per 5 seconds) and will automatically wait when limits are approached.

```python
# Rate limiting is handled automatically
client = MySaleClient(api_token="your_token")

# These calls will be automatically throttled
for i in range(100):
    client.skus.get_statistics()  # Will respect rate limits
```

## Development

### Setting up Development Environment

```bash
git clone https://github.com/DuneRaccoon/mysale-api-sdk.git
cd mysale-api-sdk

# Install development dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Run linting
black mysale_api/
isort mysale_api/
flake8 mysale_api/

# Type checking
mypy mysale_api/
```

### Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=mysale_api

# Run specific test file
pytest tests/test_orders.py
```

### Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Add tests for new functionality
5. Run the test suite
6. Commit your changes (`git commit -m 'Add amazing feature'`)
7. Push to the branch (`git push origin feature/amazing-feature`)
8. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Links

- [MySale API Documentation](https://apacsale.atlassian.net/wiki/spaces/MPS/pages/2109931778/API+Documentation)
- [PyPI Package](https://pypi.org/project/mysale-api-sdk/)
- [GitHub Repository](https://github.com/DuneRaccoon/mysale-api-sdk)
- [Issue Tracker](https://github.com/DuneRaccoon/mysale-api-sdk/issues)

## Support

For support, please:
1. Check the [documentation](https://github.com/DuneRaccoon/mysale-api-sdk)
2. Search [existing issues](https://github.com/DuneRaccoon/mysale-api-sdk/issues)
3. Create a [new issue](https://github.com/DuneRaccoon/mysale-api-sdk/issues/new) if needed

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for version history and changes.
