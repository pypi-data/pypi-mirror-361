import re
from uuid import UUID
from typing import Any, Dict, List, Optional, Union, Generator
from urllib.parse import urlencode


def to_snake_case(string: str) -> str:
    """Convert CamelCase to snake_case."""
    # Insert an underscore before any uppercase letter that follows a lowercase letter
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', string)
    # Insert an underscore before any uppercase letter that follows a lowercase letter or digit
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()


def to_camel_case(string: str) -> str:
    """Convert snake_case to camelCase."""
    components = string.split('_')
    return components[0] + ''.join(word.capitalize() for word in components[1:])


def clean_params(params: Dict[str, Any]) -> Dict[str, Any]:
    """Clean parameters by removing None values and converting types."""
    cleaned = {}
    for key, value in params.items():
        if value is not None:
            if isinstance(value, bool):
                cleaned[key] = str(value).lower()
            elif isinstance(value, list):
                # Handle array parameters
                if value:  # Only add non-empty lists
                    cleaned[key] = value
            else:
                cleaned[key] = value
    return cleaned


def build_query_string(params: Dict[str, Any]) -> str:
    """Build a query string from parameters."""
    if not params:
        return ""
    
    query_parts = []
    for key, value in params.items():
        if isinstance(value, list):
            # For array parameters, add each item separately
            for item in value:
                query_parts.append(f"{key}={item}")
        else:
            query_parts.append(f"{key}={value}")
    
    return "?" + "&".join(query_parts) if query_parts else ""


def validate_identifier(identifier: Union[str, UUID], identifier_type: str = "identifier") -> str:
    """Validate and clean an identifier for use in API calls."""
    if isinstance(identifier, UUID):
        # If it's a UUID, convert to string
        identifier = str(identifier)
        
    if not identifier or not isinstance(identifier, str):
        raise ValueError(f"Invalid {identifier_type}: must be a non-empty string")
    
    # Remove leading/trailing whitespace
    identifier = identifier.strip()
    
    if not identifier:
        raise ValueError(f"Invalid {identifier_type}: cannot be empty or whitespace only")
    
    return identifier


def validate_merchant_sku_id(sku_id: str) -> str:
    """Validate merchant SKU ID (max 50 characters)."""
    sku_id = validate_identifier(sku_id, "merchant_sku_id")
    
    if len(sku_id) > 50:
        raise ValueError(f"merchant_sku_id cannot exceed 50 characters, got {len(sku_id)}")
    
    return sku_id


def validate_brand_name(brand: str) -> str:
    """Validate brand name (max 128 characters)."""
    brand = validate_identifier(brand, "brand")
    
    if len(brand) > 128:
        raise ValueError(f"brand cannot exceed 128 characters, got {len(brand)}")
    
    return brand


def chunk_list(items: List[Any], chunk_size: int) -> Generator[List[Any], None, None]:
    """Split a list into chunks of specified size."""
    for i in range(0, len(items), chunk_size):
        yield items[i:i + chunk_size]


def safe_get_nested(data: Dict[str, Any], path: str, default: Any = None) -> Any:
    """Safely get a nested value from a dictionary using dot notation."""
    keys = path.split('.')
    current = data
    
    for key in keys:
        if isinstance(current, dict) and key in current:
            current = current[key]
        else:
            return default
    
    return current


def format_pagination_response(response: Dict[str, Any], items_key: str = "items") -> Dict[str, Any]:
    """Format a paginated response to extract pagination info."""
    pagination_info = {
        'total_count': response.get('total_count'),
        'offset': response.get('offset', 0),
        'limit': response.get('limit', 50),
        'items': response.get(items_key, [])
    }
    
    return pagination_info


def validate_currency(currency: str) -> str:
    """Validate currency code."""
    if not currency or not isinstance(currency, str):
        raise ValueError("Currency must be a non-empty string")
    
    currency = currency.strip().upper()
    
    # MySale supports AUD, NZD, MYR, SGD
    allowed_currencies = ["AUD", "NZD", "MYR", "SGD"]
    if currency not in allowed_currencies:
        raise ValueError(f"Currency '{currency}' not supported. Allowed currencies: {allowed_currencies}")
    
    return currency


def validate_country_code(country_code: str) -> str:
    """Validate country code for MySale API."""
    if not country_code or not isinstance(country_code, str):
        raise ValueError("Country code must be a non-empty string")
    
    country_code = country_code.strip().upper()
    
    # MySale primarily supports AU and NZ
    allowed_countries = ["AU", "NZ"]
    if country_code not in allowed_countries:
        raise ValueError(f"Country code '{country_code}' not supported. Allowed countries: {allowed_countries}")
    
    return country_code


def validate_standard_product_code_type(code_type: str) -> str:
    """Validate standard product code type."""
    if not code_type or not isinstance(code_type, str):
        raise ValueError("Standard product code type must be a non-empty string")
    
    code_type = code_type.strip().upper()
    
    # Allowed values from MySale API
    allowed_types = ["EAN", "UPC", "ISBN_10", "ISBN_13", "GTIN_14"]
    if code_type not in allowed_types:
        raise ValueError(f"Standard product code type '{code_type}' not supported. Allowed types: {allowed_types}")
    
    return code_type


def validate_shop_code(shop_code: str) -> str:
    """Validate shop code for MySale API."""
    if not shop_code or not isinstance(shop_code, str):
        raise ValueError("Shop code must be a non-empty string")
    
    shop_code = shop_code.strip().upper()
    
    # MySale shop codes
    allowed_shops = ["BN", "NZ", "MY", "SI"]  # BuyInvite, NZSale, Malaysia, Singapore
    if shop_code not in allowed_shops:
        raise ValueError(f"Shop code '{shop_code}' not supported. Allowed shop codes: {allowed_shops}")
    
    return shop_code


def validate_weight_unit(unit: str) -> str:
    """Validate weight unit."""
    if not unit or not isinstance(unit, str):
        raise ValueError("Weight unit must be a non-empty string")
    
    unit = unit.strip().lower()
    
    # Common weight units
    allowed_units = ["g", "kg", "lb", "oz"]
    if unit not in allowed_units:
        raise ValueError(f"Weight unit '{unit}' not supported. Allowed units: {allowed_units}")
    
    return unit


def validate_dimension_unit(unit: str) -> str:
    """Validate dimension unit."""
    if not unit or not isinstance(unit, str):
        raise ValueError("Dimension unit must be a non-empty string")
    
    unit = unit.strip().lower()
    
    # Common dimension units
    allowed_units = ["cm", "m", "in", "ft"]
    if unit not in allowed_units:
        raise ValueError(f"Dimension unit '{unit}' not supported. Allowed units: {allowed_units}")
    
    return unit


def build_api_url(base_url: str, path: str) -> str:
    """Build a complete API URL."""
    base_url = base_url.rstrip('/')
    path = path.lstrip('/')
    return f"{base_url}/{path}"


def extract_items_from_response(response: Any, items_key: str = "items") -> List[Dict[str, Any]]:
    """Extract items from a MySale API response."""
    if isinstance(response, dict):
        if items_key in response:
            return response[items_key]
        elif "SKUs" in response:  # For SKU list responses
            return response["SKUs"]
        elif "products" in response:  # For product list responses
            return response["products"]
        elif "branches" in response:  # For taxonomy list responses
            return response["branches"]
        else:
            # Single item response
            return [response]
    elif isinstance(response, list):
        return response
    else:
        return []


def validate_gender(gender: str) -> str:
    """Validate gender value for MySale API."""
    if not gender or not isinstance(gender, str):
        raise ValueError("Gender must be a non-empty string")
    
    gender = gender.strip().title()
    
    # Allowed gender values from MySale API
    allowed_genders = ["Women", "Men", "Girls", "Boys", "Unisex"]
    if gender not in allowed_genders:
        raise ValueError(f"Gender '{gender}' not supported. Allowed genders: {allowed_genders}")
    
    return gender


def validate_age_group(age_group: str) -> str:
    """Validate age group value for MySale API."""
    if not age_group or not isinstance(age_group, str):
        raise ValueError("Age group must be a non-empty string")
    
    age_group = age_group.strip().title()
    
    # Allowed age group values from MySale API
    allowed_age_groups = ["Adult", "Baby", "Kids", "Teen"]
    if age_group not in allowed_age_groups:
        raise ValueError(f"Age group '{age_group}' not supported. Allowed age groups: {allowed_age_groups}")
    
    return age_group
