# Myer PIM SDK - Akeneo REST API Integration

from .client import AkeneoClient, AkeneoAsyncClient
from .exceptions import (
    AkeneoAPIError,
    AuthenticationError,
    ValidationError,
    NotFoundError,
    RateLimitError,
    ServerError
)
from .search import (
    SearchBuilder,
    FilterBuilder,
    ProductPropertyFilter,
    ProductModelPropertyFilter,
    AttributeFilter
)
from .search.operators import (
    ComparisonOperator,
    ListOperator,
    DateOperator,
    TextOperator,
    CategoryOperator,
    CompletenessOperator,
    BooleanOperator,
    ParentOperator,
    QualityScoreOperator,
    EmptyOperator
)
from .search.builder import (
    by_supplier_style,
    by_brand,
    ready_for_enrichment,
    enrichment_complete,
    missing_images,
    by_supplier,
    concession_products,
    online_products,
    clearance_products
)

__version__ = "1.0.0"
__all__ = [
    "AkeneoClient",
    "AkeneoAsyncClient",
    "AkeneoAPIError",
    "AuthenticationError", 
    "ValidationError",
    "NotFoundError",
    "RateLimitError",
    "ServerError",
    "SearchBuilder",
    "FilterBuilder",
    "ComparisonOperator",
    "ListOperator",
    "DateOperator",
    "TextOperator",
    "CategoryOperator",
    "CompletenessOperator",
    "BooleanOperator",
    "ParentOperator",
    "QualityScoreOperator",
    "EmptyOperator",
    "ProductPropertyFilter",
    "ProductModelPropertyFilter",
    "AttributeFilter",
    # Magic search functions
    "by_supplier_style",
    "by_brand",
    "ready_for_enrichment",
    "enrichment_complete",
    "missing_images",
    "by_supplier",
    "concession_products",
    "online_products",
    "clearance_products"
]
