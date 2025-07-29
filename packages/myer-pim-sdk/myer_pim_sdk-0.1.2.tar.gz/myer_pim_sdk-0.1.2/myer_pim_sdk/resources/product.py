# resources/product.py

from typing import Dict, Any, List, Optional, Union, TYPE_CHECKING, Callable
import json

from .base import AkeneoResource
from ..models.product import ProductRead, ProductWrite, ProductCreateWrite
from ..utils import validate_identifier
from ..search import SearchBuilder, FilterBuilder
from ..search.filters import ProductPropertyFilter, AttributeFilter

if TYPE_CHECKING:
    from ..client import AkeneoClient, AkeneoAsyncClient


class Product(AkeneoResource):
    """
    Product resource for Akeneo API.
    
    Handles both UUID-based and identifier-based product operations.
    For Myer's system, products are SKU-level items (Level 2).
    """
    
    endpoint = "products"
    model_class = ProductRead
    
    # Synchronous methods
    
    def get_by_uuid(self, uuid: str) -> "Product":
        """Get a product by its UUID."""
        if not hasattr(self._client, '_make_request_sync'):
            raise TypeError("This method requires a synchronous client")
        
        uuid = validate_identifier(uuid, "UUID")
        url = f"/api/rest/v1/products-uuid/{uuid}"
        response = self._client._make_request_sync("GET", url)
        
        return self._create_instance(response)
    
    def get_by_identifier(self, identifier: str) -> "Product":
        """Get a product by its identifier (SKU).""" 
        if not hasattr(self._client, '_make_request_sync'):
            raise TypeError("This method requires a synchronous client")
        
        identifier = validate_identifier(identifier, "identifier")
        url = f"/api/rest/v1/products/{identifier}"
        response = self._client._make_request_sync("GET", url)
        
        return self._create_instance(response)
    
    def list_by_uuid(self, paginated: bool = False, **params) -> Union[List["Product"], "PaginatedResponse[Product]"]:
        """List products using the UUID endpoint."""
        if not hasattr(self._client, '_make_request_sync'):
            raise TypeError("This method requires a synchronous client")
            
        url = "/api/rest/v1/products-uuid"
        prepared_params = self._prepare_request_params(params)
        response = self._client._make_request_sync("GET", url, params=prepared_params)
        
        items = self._extract_items(response)
        instances = [self._create_instance(item) for item in items]
        
        if paginated:
            pagination_data = self._extract_pagination_data(response)
            links = response.get('_links', {}) if isinstance(response, dict) else {}
            from .base import PaginatedResponse
            return PaginatedResponse(
                items=instances,
                current_page=pagination_data.get('current_page', 1),
                has_next=pagination_data.get('has_next', False),
                has_previous=pagination_data.get('has_previous', False),
                has_first=pagination_data.get('has_first', False),
                has_last=pagination_data.get('has_last', False),
                links=links
            )
        
        return instances
    
    def create_with_uuid(self, data: Union[Dict[str, Any], ProductCreateWrite]) -> "Product":
        """Create a new product using the UUID endpoint."""
        if not hasattr(self._client, '_make_request_sync'):
            raise TypeError("This method requires a synchronous client")
            
        url = "/api/rest/v1/products-uuid"
        prepared_data = self._prepare_request_data(data)
        response = self._client._make_request_sync("POST", url, json_data=prepared_data)
        
        return self._create_instance(response)
    
    def update_by_uuid(self, uuid: str, data: Union[Dict[str, Any], ProductWrite]) -> "Product":
        """Update a product by UUID."""
        if not hasattr(self._client, '_make_request_sync'):
            raise TypeError("This method requires a synchronous client")
            
        uuid = validate_identifier(uuid, "UUID")
        url = f"/api/rest/v1/products-uuid/{uuid}"
        prepared_data = self._prepare_request_data(data)
        response = self._client._make_request_sync("PATCH", url, json_data=prepared_data)
        
        # Akeneo PATCH often returns empty response, so fetch the updated product
        if response:
            return self._create_instance(response)
        else:
            return self.get_by_uuid(uuid)
    
    def update_by_identifier(self, identifier: str, data: Union[Dict[str, Any], ProductWrite]) -> "Product":
        """Update a product by identifier."""
        if not hasattr(self._client, '_make_request_sync'):
            raise TypeError("This method requires a synchronous client")
            
        identifier = validate_identifier(identifier, "identifier")
        url = f"/api/rest/v1/products/{identifier}"
        prepared_data = self._prepare_request_data(data)
        response = self._client._make_request_sync("PATCH", url, json_data=prepared_data)
        
        # Akeneo PATCH often returns empty response, so fetch the updated product
        if response:
            return self._create_instance(response)
        else:
            return self.get_by_identifier(identifier)
    
    def delete_by_uuid(self, uuid: str) -> None:
        """Delete a product by UUID."""
        if not hasattr(self._client, '_make_request_sync'):
            raise TypeError("This method requires a synchronous client")
            
        uuid = validate_identifier(uuid, "UUID")
        url = f"/api/rest/v1/products-uuid/{uuid}"
        self._client._make_request_sync("DELETE", url)
    
    def delete_by_identifier(self, identifier: str) -> None:
        """Delete a product by identifier."""
        if not hasattr(self._client, '_make_request_sync'):
            raise TypeError("This method requires a synchronous client")
            
        identifier = validate_identifier(identifier, "identifier")
        url = f"/api/rest/v1/products/{identifier}"
        self._client._make_request_sync("DELETE", url)
    
    def bulk_update(self, products: List[Union[Dict[str, Any], ProductWrite]], use_uuid: bool = False) -> List[Dict[str, Any]]:
        """
        Update multiple products at once.
        
        Args:
            products: List of product data to update
            use_uuid: Whether to use the UUID endpoint (default: identifier endpoint)
            
        Returns:
            List of status responses for each product update
        """
        if not hasattr(self._client, '_make_request_sync'):
            raise TypeError("This method requires a synchronous client")
        
        # Prepare the NDJSON payload
        lines = []
        for product_data in products:
            if hasattr(product_data, 'model_dump'):
                prepared_data = product_data.model_dump(by_alias=True, exclude_none=True)
            else:
                prepared_data = product_data
            lines.append(json.dumps(prepared_data))
        
        ndjson_payload = '\n'.join(lines)
        
        # Choose endpoint based on use_uuid flag
        url = "/api/rest/v1/products-uuid" if use_uuid else "/api/rest/v1/products"
        
        headers = {
            "Content-Type": "application/vnd.akeneo.collection+json"
        }
        
        response = self._client._make_request_sync("PATCH", url, form_data=ndjson_payload)
        
        # Parse NDJSON response
        if isinstance(response, str):
            results = []
            for line in response.strip().split('\n'):
                if line.strip():
                    results.append(json.loads(line))
            return results
        
        return response if isinstance(response, list) else [response]
    
    def search(self, search_criteria: Dict[str, Any], **params) -> List["Product"]:
        """
        Search for products using the search endpoint.
        
        Args:
            search_criteria: Search criteria in Akeneo format
            **params: Additional query parameters
            
        Returns:
            List of matching products
        """
        if not hasattr(self._client, '_make_request_sync'):
            raise TypeError("This method requires a synchronous client")
        
        url = "/api/rest/v1/products-uuid/search"
        
        # Prepare request body
        request_body = {
            "search": json.dumps(search_criteria) if search_criteria else None,
            **params
        }
        
        # Clean None values
        request_body = {k: v for k, v in request_body.items() if v is not None}
        
        response = self._client._make_request_sync("POST", url, json_data=request_body)
        
        items = self._extract_items(response)
        return [self._create_instance(item) for item in items]
    
    def search_with_builder(self, builder: Union[SearchBuilder, Callable[[FilterBuilder], None]],
                           use_uuid: bool = True, paginated: bool = False) -> Union[List["Product"], "PaginatedResponse[Product]"]:
        """
        Search for products using SearchBuilder or FilterBuilder.
        
        Args:
            builder: SearchBuilder instance or function that configures a FilterBuilder
            use_uuid: Whether to use UUID endpoint (default: True)
            paginated: Whether to return paginated response
            
        Returns:
            List of products or PaginatedResponse
            
        Examples:
            # Using SearchBuilder
            builder = SearchBuilder().filters(lambda f: f.enabled(True).family(["clothing"]))
            products = client.products.search_with_builder(builder)
            
            # Using function
            products = client.products.search_with_builder(
                lambda f: f.enabled(True).categories(["winter_collection"])
            )
        """
        if not hasattr(self._client, '_make_request_sync'):
            raise TypeError("This method requires a synchronous client")
        
        # Handle different builder types
        if callable(builder):
            # It's a function, create SearchBuilder and apply function
            search_builder = SearchBuilder()
            search_builder.filters(builder)
        else:
            # It's already a SearchBuilder
            search_builder = builder
        
        # Get search parameters
        search_params = search_builder.build_search_params()
        
        # Choose endpoint based on use_uuid
        if use_uuid:
            url = "/api/rest/v1/products-uuid"
        else:
            url = "/api/rest/v1/products"
        
        prepared_params = self._prepare_request_params(search_params)
        response = self._client._make_request_sync("GET", url, params=prepared_params)
        
        items = self._extract_items(response)
        instances = [self._create_instance(item) for item in items]
        
        if paginated:
            pagination_data = self._extract_pagination_data(response)
            links = response.get('_links', {}) if isinstance(response, dict) else {}
            from .base import PaginatedResponse
            return PaginatedResponse(
                items=instances,
                current_page=pagination_data.get('current_page', 1),
                has_next=pagination_data.get('has_next', False),
                has_previous=pagination_data.get('has_previous', False),
                has_first=pagination_data.get('has_first', False),
                has_last=pagination_data.get('has_last', False),
                links=links
            )
        
        return instances
    
    def find_by_uuid(self, uuids: List[str]) -> List["Product"]:
        """
        Find products by a list of UUIDs.
        
        Args:
            uuids: List of product UUIDs
            
        Returns:
            List of matching products
        """
        return self.search_with_builder(
            lambda f: f.uuid(uuids)
        )
    
    def find_enabled(self, **filters) -> List["Product"]:
        """
        Find enabled products with optional additional filters.
        
        Args:
            **filters: Additional search parameters
            
        Returns:
            List of enabled products
        """
        builder = SearchBuilder().raw_filter("enabled", "=", True)
        
        # Add any additional filters
        for key, value in filters.items():
            if key == "categories":
                builder.raw_filter("categories", "IN", value)
            elif key == "family":
                builder.raw_filter("family", "IN", value if isinstance(value, list) else [value])
            elif key == "updated_since_days":
                builder.raw_filter("updated", "SINCE LAST N DAYS", value)
        
        return self.search_with_builder(builder)
    
    def find_in_categories(self, category_codes: List[str], include_children: bool = False) -> List["Product"]:
        """
        Find products in specific categories.
        
        Args:
            category_codes: List of category codes
            include_children: Whether to include child categories
            
        Returns:
            List of products in the categories
        """
        operator = "IN CHILDREN" if include_children else "IN"
        return self.search_with_builder(
            lambda f: f.categories(category_codes, operator)
        )
    
    def find_by_family(self, family_codes: List[str]) -> List["Product"]:
        """
        Find products by family codes.
        
        Args:
            family_codes: List of family codes
            
        Returns:
            List of products in the families
        """
        return self.search_with_builder(
            lambda f: f.family(family_codes)
        )
    
    def find_incomplete(self, scope: str, threshold: int = 100, 
                       locales: Optional[List[str]] = None) -> List["Product"]:
        """
        Find incomplete products.
        
        Args:
            scope: Channel scope
            threshold: Completeness threshold (default: 100)
            locales: Specific locales to check
            
        Returns:
            List of incomplete products
        """
        return self.search_with_builder(
            lambda f: f.completeness(threshold - 1, scope, "<", locales)
        )
    
    def find_recently_updated(self, days: int) -> List["Product"]:
        """
        Find products updated in the last N days.
        
        Args:
            days: Number of days to look back
            
        Returns:
            List of recently updated products
        """
        return self.search_with_builder(
            lambda f: f.updated(days, "SINCE LAST N DAYS")
        )
    
    def find_by_attribute(self, attribute_code: str, value: Any, operator: str = "=",
                         locale: Optional[str] = None, scope: Optional[str] = None) -> List["Product"]:
        """
        Find products by attribute value.
        
        Args:
            attribute_code: Code of the attribute
            value: Value to search for
            operator: Comparison operator
            locale: Locale (if attribute is localizable)
            scope: Scope (if attribute is scopable)
            
        Returns:
            List of matching products
        """
        return self.search_with_builder(
            lambda f: f.attribute_text(attribute_code, value, operator, locale, scope)
        )
    
    def find_with_quality_score(self, scores: List[str], scope: str, locale: str) -> List["Product"]:
        """
        Find products with specific quality scores.
        
        Args:
            scores: List of quality scores ("A", "B", "C", "D", "E")
            scope: Channel scope
            locale: Locale
            
        Returns:
            List of products with the specified quality scores
        """
        return self.search_with_builder(
            lambda f: f.quality_score(scores, scope, locale)
        )
    
    def find_variants_of(self, parent_code: str) -> List["Product"]:
        """
        Find all variant products of a parent product model.
        
        Args:
            parent_code: Code of the parent product model
            
        Returns:
            List of variant products
        """
        return self.search_with_builder(
            lambda f: f.parent(parent_code, "=")
        )
    
    def find_simple_products(self) -> List["Product"]:
        """
        Find all simple products (products without a parent).
        
        Returns:
            List of simple products
        """
        return self.search_with_builder(
            lambda f: f.parent("", "EMPTY")
        )
    
    # Asynchronous methods
    
    async def get_by_uuid_async(self, uuid: str) -> "Product":
        """Get a product by its UUID asynchronously."""
        if not hasattr(self._client, '_make_request_async'):
            raise TypeError("This method requires an asynchronous client")
        
        uuid = validate_identifier(uuid, "UUID")
        url = f"/api/rest/v1/products-uuid/{uuid}"
        response = await self._client._make_request_async("GET", url)
        
        return self._create_instance(response)
    
    async def get_by_identifier_async(self, identifier: str) -> "Product":
        """Get a product by its identifier (SKU) asynchronously."""
        if not hasattr(self._client, '_make_request_async'):
            raise TypeError("This method requires an asynchronous client")
        
        identifier = validate_identifier(identifier, "identifier")
        url = f"/api/rest/v1/products/{identifier}"
        response = await self._client._make_request_async("GET", url)
        
        return self._create_instance(response)
    
    async def list_by_uuid_async(self, paginated: bool = False, **params) -> Union[List["Product"], "PaginatedResponse[Product]"]:
        """List products using the UUID endpoint asynchronously."""
        if not hasattr(self._client, '_make_request_async'):
            raise TypeError("This method requires an asynchronous client")
            
        url = "/api/rest/v1/products-uuid"
        prepared_params = self._prepare_request_params(params)
        response = await self._client._make_request_async("GET", url, params=prepared_params)
        
        items = self._extract_items(response)
        instances = [self._create_instance(item) for item in items]
        
        if paginated:
            pagination_data = self._extract_pagination_data(response)
            links = response.get('_links', {}) if isinstance(response, dict) else {}
            from .base import PaginatedResponse
            return PaginatedResponse(
                items=instances,
                current_page=pagination_data.get('current_page', 1),
                has_next=pagination_data.get('has_next', False),
                has_previous=pagination_data.get('has_previous', False),
                has_first=pagination_data.get('has_first', False),
                has_last=pagination_data.get('has_last', False),
                links=links
            )
        
        return instances
    
    async def create_with_uuid_async(self, data: Union[Dict[str, Any], ProductCreateWrite]) -> "Product":
        """Create a new product using the UUID endpoint asynchronously."""
        if not hasattr(self._client, '_make_request_async'):
            raise TypeError("This method requires an asynchronous client")
            
        url = "/api/rest/v1/products-uuid"
        prepared_data = self._prepare_request_data(data)
        response = await self._client._make_request_async("POST", url, json_data=prepared_data)
        
        return self._create_instance(response)
    
    async def update_by_uuid_async(self, uuid: str, data: Union[Dict[str, Any], ProductWrite]) -> "Product":
        """Update a product by UUID asynchronously."""
        if not hasattr(self._client, '_make_request_async'):
            raise TypeError("This method requires an asynchronous client")
            
        uuid = validate_identifier(uuid, "UUID")
        url = f"/api/rest/v1/products-uuid/{uuid}"
        prepared_data = self._prepare_request_data(data)
        response = await self._client._make_request_async("PATCH", url, json_data=prepared_data)
        
        # Akeneo PATCH often returns empty response, so fetch the updated product
        if response:
            return self._create_instance(response)
        else:
            return await self.get_by_uuid_async(uuid)
    
    async def update_by_identifier_async(self, identifier: str, data: Union[Dict[str, Any], ProductWrite]) -> "Product":
        """Update a product by identifier asynchronously."""
        if not hasattr(self._client, '_make_request_async'):
            raise TypeError("This method requires an asynchronous client")
            
        identifier = validate_identifier(identifier, "identifier")
        url = f"/api/rest/v1/products/{identifier}"
        prepared_data = self._prepare_request_data(data)
        response = await self._client._make_request_async("PATCH", url, json_data=prepared_data)
        
        # Akeneo PATCH often returns empty response, so fetch the updated product
        if response:
            return self._create_instance(response)
        else:
            return await self.get_by_identifier_async(identifier)
    
    async def delete_by_uuid_async(self, uuid: str) -> None:
        """Delete a product by UUID asynchronously."""
        if not hasattr(self._client, '_make_request_async'):
            raise TypeError("This method requires an asynchronous client")
            
        uuid = validate_identifier(uuid, "UUID")
        url = f"/api/rest/v1/products-uuid/{uuid}"
        await self._client._make_request_async("DELETE", url)
    
    async def delete_by_identifier_async(self, identifier: str) -> None:
        """Delete a product by identifier asynchronously."""
        if not hasattr(self._client, '_make_request_async'):
            raise TypeError("This method requires an asynchronous client")
            
        identifier = validate_identifier(identifier, "identifier")
        url = f"/api/rest/v1/products/{identifier}"
        await self._client._make_request_async("DELETE", url)
    
    async def bulk_update_async(self, products: List[Union[Dict[str, Any], ProductWrite]], use_uuid: bool = False) -> List[Dict[str, Any]]:
        """
        Update multiple products at once asynchronously.
        
        Args:
            products: List of product data to update
            use_uuid: Whether to use the UUID endpoint (default: identifier endpoint)
            
        Returns:
            List of status responses for each product update
        """
        if not hasattr(self._client, '_make_request_async'):
            raise TypeError("This method requires an asynchronous client")
        
        # Prepare the NDJSON payload
        lines = []
        for product_data in products:
            if hasattr(product_data, 'model_dump'):
                prepared_data = product_data.model_dump(by_alias=True, exclude_none=True)
            else:
                prepared_data = product_data
            lines.append(json.dumps(prepared_data))
        
        ndjson_payload = '\n'.join(lines)
        
        # Choose endpoint based on use_uuid flag
        url = "/api/rest/v1/products-uuid" if use_uuid else "/api/rest/v1/products"
        
        response = await self._client._make_request_async("PATCH", url, form_data=ndjson_payload)
        
        # Parse NDJSON response
        if isinstance(response, str):
            results = []
            for line in response.strip().split('\n'):
                if line.strip():
                    results.append(json.loads(line))
            return results
        
        return response if isinstance(response, list) else [response]
    
    async def search_async(self, search_criteria: Dict[str, Any], **params) -> List["Product"]:
        """
        Search for products using the search endpoint asynchronously.
        
        Args:
            search_criteria: Search criteria in Akeneo format
            **params: Additional query parameters
            
        Returns:
            List of matching products
        """
        if not hasattr(self._client, '_make_request_async'):
            raise TypeError("This method requires an asynchronous client")
        
        url = "/api/rest/v1/products-uuid/search"
        
        # Prepare request body
        request_body = {
            "search": json.dumps(search_criteria) if search_criteria else None,
            **params
        }
        
        # Clean None values
        request_body = {k: v for k, v in request_body.items() if v is not None}
        
        response = await self._client._make_request_async("POST", url, json_data=request_body)
        
        items = self._extract_items(response)
        return [self._create_instance(item) for item in items]
    
    async def search_with_builder_async(self, builder: Union[SearchBuilder, Callable[[FilterBuilder], None]],
                                       use_uuid: bool = True, paginated: bool = False) -> Union[List["Product"], "PaginatedResponse[Product]"]:
        """
        Search for products using SearchBuilder or FilterBuilder asynchronously.
        
        Args:
            builder: SearchBuilder instance or function that configures a FilterBuilder
            use_uuid: Whether to use UUID endpoint (default: True)
            paginated: Whether to return paginated response
            
        Returns:
            List of products or PaginatedResponse
        """
        if not hasattr(self._client, '_make_request_async'):
            raise TypeError("This method requires an asynchronous client")
        
        # Handle different builder types
        if callable(builder):
            # It's a function, create SearchBuilder and apply function
            search_builder = SearchBuilder()
            search_builder.filters(builder)
        else:
            # It's already a SearchBuilder
            search_builder = builder
        
        # Get search parameters
        search_params = search_builder.build_search_params()
        
        # Choose endpoint based on use_uuid
        if use_uuid:
            url = "/api/rest/v1/products-uuid"
        else:
            url = "/api/rest/v1/products"
        
        prepared_params = self._prepare_request_params(search_params)
        response = await self._client._make_request_async("GET", url, params=prepared_params)
        
        items = self._extract_items(response)
        instances = [self._create_instance(item) for item in items]
        
        if paginated:
            pagination_data = self._extract_pagination_data(response)
            links = response.get('_links', {}) if isinstance(response, dict) else {}
            from .base import PaginatedResponse
            return PaginatedResponse(
                items=instances,
                current_page=pagination_data.get('current_page', 1),
                has_next=pagination_data.get('has_next', False),
                has_previous=pagination_data.get('has_previous', False),
                has_first=pagination_data.get('has_first', False),
                has_last=pagination_data.get('has_last', False),
                links=links
            )
        
        return instances
    
    # Async versions of convenience methods
    
    async def find_by_uuid_async(self, uuids: List[str]) -> List["Product"]:
        """Find products by UUIDs asynchronously."""
        return await self.search_with_builder_async(lambda f: f.uuid(uuids))
    
    async def find_enabled_async(self, **filters) -> List["Product"]:
        """Find enabled products asynchronously."""
        builder = SearchBuilder().raw_filter("enabled", "=", True)
        
        for key, value in filters.items():
            if key == "categories":
                builder.raw_filter("categories", "IN", value)
            elif key == "family":
                builder.raw_filter("family", "IN", value if isinstance(value, list) else [value])
            elif key == "updated_since_days":
                builder.raw_filter("updated", "SINCE LAST N DAYS", value)
        
        return await self.search_with_builder_async(builder)
    
    async def find_in_categories_async(self, category_codes: List[str], include_children: bool = False) -> List["Product"]:
        """Find products in categories asynchronously."""
        operator = "IN CHILDREN" if include_children else "IN"
        return await self.search_with_builder_async(lambda f: f.categories(category_codes, operator))
    
    async def find_by_family_async(self, family_codes: List[str]) -> List["Product"]:
        """Find products by family asynchronously."""
        return await self.search_with_builder_async(lambda f: f.family(family_codes))
    
    async def find_incomplete_async(self, scope: str, threshold: int = 100, 
                                   locales: Optional[List[str]] = None) -> List["Product"]:
        """Find incomplete products asynchronously."""
        return await self.search_with_builder_async(
            lambda f: f.completeness(threshold - 1, scope, "<", locales)
        )
    
    async def find_recently_updated_async(self, days: int) -> List["Product"]:
        """Find recently updated products asynchronously."""
        return await self.search_with_builder_async(lambda f: f.updated(days, "SINCE LAST N DAYS"))
    
    async def find_by_attribute_async(self, attribute_code: str, value: Any, operator: str = "=",
                                     locale: Optional[str] = None, scope: Optional[str] = None) -> List["Product"]:
        """Find products by attribute asynchronously."""
        return await self.search_with_builder_async(
            lambda f: f.attribute_text(attribute_code, value, operator, locale, scope)
        )
    
    async def find_with_quality_score_async(self, scores: List[str], scope: str, locale: str) -> List["Product"]:
        """Find products with quality scores asynchronously."""
        return await self.search_with_builder_async(lambda f: f.quality_score(scores, scope, locale))
    
    async def find_variants_of_async(self, parent_code: str) -> List["Product"]:
        """Find variant products asynchronously."""
        return await self.search_with_builder_async(lambda f: f.parent(parent_code, "="))
    
    async def find_simple_products_async(self) -> List["Product"]:
        """Find simple products asynchronously."""
        return await self.search_with_builder_async(lambda f: f.parent("", "EMPTY"))
