import re
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
                # Handle array parameters for Akeneo API
                if value:  # Only add non-empty lists
                    cleaned[key] = value
            else:
                cleaned[key] = value
    return cleaned


def build_query_string(params: Dict[str, Any]) -> str:
    """Build a query string from parameters, handling arrays properly."""
    if not params:
        return ""
    
    query_parts = []
    for key, value in params.items():
        if isinstance(value, list):
            # For Akeneo API, arrays are usually comma-separated in a single parameter
            if value:  # Only add non-empty lists
                query_parts.append(f"{key}={','.join(str(v) for v in value)}")
        else:
            query_parts.append(f"{key}={value}")
    
    return "?" + "&".join(query_parts) if query_parts else ""


def format_akeneo_datetime(dt) -> str:
    """Format a datetime object for Akeneo API."""
    if hasattr(dt, 'isoformat'):
        # Remove microseconds and ensure Z suffix for UTC
        return dt.replace(microsecond=0).isoformat() + 'Z'
    return str(dt)


def parse_pagination_links(links: Dict[str, Any]) -> Dict[str, Optional[str]]:
    """Parse pagination links from Akeneo API response."""
    parsed_links = {
        'first': None,
        'previous': None,
        'next': None,
        'self': None
    }
    
    for link_type, link_data in links.items():
        if isinstance(link_data, dict) and 'href' in link_data:
            parsed_links[link_type] = link_data['href']
    
    return parsed_links


def extract_items_from_response(response: Any) -> List[Dict[str, Any]]:
    """Extract items from an Akeneo API response."""
    if isinstance(response, dict):
        if '_embedded' in response and 'items' in response['_embedded']:
            return response['_embedded']['items']
        elif 'items' in response:
            return response['items']
        else:
            # Single item response
            return [response]
    elif isinstance(response, list):
        return response
    else:
        return []


def get_pagination_info(response: Dict[str, Any]) -> Dict[str, Any]:
    """Extract pagination information from Akeneo API response."""
    pagination_info = {
        'current_page': 1,
        'has_next': False,
        'has_previous': False,
        'has_first': False,
        'has_last': False,
        'items_count': 0
    }
    
    if isinstance(response, dict):
        # Extract current page from Akeneo response
        if 'current_page' in response:
            pagination_info['current_page'] = response['current_page']
        
        # Extract links to determine pagination - following Akeneo format
        links = response.get('_links', {})
        pagination_info['has_next'] = 'next' in links
        pagination_info['has_previous'] = 'previous' in links
        pagination_info['has_first'] = 'first' in links
        pagination_info['has_last'] = 'last' in links
        
        # Count items in current page
        if '_embedded' in response and 'items' in response['_embedded']:
            items = response['_embedded']['items']
            pagination_info['items_count'] = len(items)
    
    return pagination_info


def validate_identifier(identifier: str, identifier_type: str = "identifier") -> str:
    """Validate and clean an identifier for use in API calls."""
    if not identifier or not isinstance(identifier, str):
        raise ValueError(f"Invalid {identifier_type}: must be a non-empty string")
    
    # Remove leading/trailing whitespace
    identifier = identifier.strip()
    
    if not identifier:
        raise ValueError(f"Invalid {identifier_type}: cannot be empty or whitespace only")
    
    return identifier


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
