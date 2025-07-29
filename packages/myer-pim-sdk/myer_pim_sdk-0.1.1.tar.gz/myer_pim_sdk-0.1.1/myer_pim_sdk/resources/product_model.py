# resources/product_model.py

from typing import Dict, Any, List, Optional, Union, TYPE_CHECKING, Callable
import json

from .base import AkeneoResource, PaginatedResponse
from ..models.product_model import ProductModelRead, ProductModelWrite, ProductModelCreateWrite
from ..utils import validate_identifier
from ..search import SearchBuilder, FilterBuilder
from ..search.filters import ProductModelPropertyFilter, AttributeFilter

if TYPE_CHECKING:
    from ..client import AkeneoClient, AkeneoAsyncClient


class ProductModel(AkeneoResource):
    """
    Product Model resource for Akeneo API.
    
    For Myer's system, product models are the main entities (Level 1) 
    where copy and image enrichment is performed.
    """
    
    endpoint = "product-models"
    model_class = ProductModelRead
    
    # Synchronous methods
    
    def search(self, **filter) -> List["ProductModel"]:
        """Search for product models."""
        if not hasattr(self._client, '_make_request_sync'):
            raise TypeError("This method requires a synchronous client")
        
        url = f"/api/rest/v1/{self.endpoint}"
        response = self._client._make_request_sync("GET", url)
        
        return [self._create_instance(item) for item in response.get('_embedded', {}).get('items', [])]
    
    def search_with_builder(self, builder: Union[SearchBuilder, Callable[[FilterBuilder], None]],
                           paginated: bool = False) -> Union[List["ProductModel"], "PaginatedResponse[ProductModel]"]:
        """
        Search for product models using SearchBuilder or FilterBuilder.
        
        Args:
            builder: SearchBuilder instance or function that configures a FilterBuilder
            paginated: Whether to return paginated response
            
        Returns:
            List of product models or PaginatedResponse
            
        Examples:
            # Using SearchBuilder
            builder = SearchBuilder().filters(lambda f: f.family(["clothing"]))
            models = client.product_models.search_with_builder(builder)
            
            # Using function
            models = client.product_models.search_with_builder(
                lambda f: f.categories(["winter_collection"])
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
        
        url = "/api/rest/v1/product-models"
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
    
    def find_by_identifier(self, identifiers: List[str]) -> List["ProductModel"]:
        """
        Find product models by identifiers.
        
        Args:
            identifiers: List of product model identifiers
            
        Returns:
            List of matching product models
        """
        return self.search_with_builder(
            lambda f: f.identifier(identifiers)
        )
    
    def find_in_categories(self, category_codes: List[str], include_children: bool = False) -> List["ProductModel"]:
        """
        Find product models in specific categories.
        
        Args:
            category_codes: List of category codes
            include_children: Whether to include child categories
            
        Returns:
            List of product models in the categories
        """
        operator = "IN CHILDREN" if include_children else "IN"
        return self.search_with_builder(
            lambda f: f.categories(category_codes, operator)
        )
    
    def find_by_family(self, family_codes: List[str]) -> List["ProductModel"]:
        """
        Find product models by family codes.
        
        Args:
            family_codes: List of family codes
            
        Returns:
            List of product models in the families
        """
        return self.search_with_builder(
            lambda f: f.family(family_codes)
        )
    
    def find_complete(self, scope: str, locale: Optional[str] = None, 
                     locales: Optional[List[str]] = None) -> List["ProductModel"]:
        """
        Find product models that are complete.
        
        Args:
            scope: Channel scope
            locale: Specific locale to check
            locales: Multiple locales to check
            
        Returns:
            List of complete product models
        """
        return self.search_with_builder(
            lambda f: f.model_completeness(scope, "ALL COMPLETE", locale, locales)
        )
    
    def find_incomplete(self, scope: str, locale: Optional[str] = None,
                       locales: Optional[List[str]] = None) -> List["ProductModel"]:
        """
        Find product models that have incomplete variants.
        
        Args:
            scope: Channel scope
            locale: Specific locale to check
            locales: Multiple locales to check
            
        Returns:
            List of product models with incomplete variants
        """
        return self.search_with_builder(
            lambda f: f.model_completeness(scope, "AT LEAST INCOMPLETE", locale, locales)
        )
    
    def find_recently_updated(self, days: int) -> List["ProductModel"]:
        """
        Find product models updated in the last N days.
        
        Args:
            days: Number of days to look back
            
        Returns:
            List of recently updated product models
        """
        return self.search_with_builder(
            lambda f: f.updated(days, "SINCE LAST N DAYS")
        )
    
    def find_root_models(self) -> List["ProductModel"]:
        """
        Find all root product models (models without a parent).
        
        Returns:
            List of root product models
        """
        return self.search_with_builder(
            lambda f: f.parent("", "EMPTY")
        )
    
    def find_sub_models(self, parent_codes: Optional[List[str]] = None) -> List["ProductModel"]:
        """
        Find sub product models.
        
        Args:
            parent_codes: Specific parent codes to filter by (optional)
            
        Returns:
            List of sub product models
        """
        if parent_codes:
            return self.search_with_builder(
                lambda f: f.parent(parent_codes, "IN")
            )
        else:
            return self.search_with_builder(
                lambda f: f.parent("", "NOT EMPTY")
            )
    
    def find_by_attribute(self, attribute_code: str, value: Any, operator: str = "=",
                         locale: Optional[str] = None, scope: Optional[str] = None) -> List["ProductModel"]:
        """
        Find product models by attribute value.
        
        Args:
            attribute_code: Code of the attribute
            value: Value to search for
            operator: Comparison operator
            locale: Locale (if attribute is localizable)
            scope: Scope (if attribute is scopable)
            
        Returns:
            List of matching product models
        """
        return self.search_with_builder(
            lambda f: f.attribute_text(attribute_code, value, operator, locale, scope)
        )
    
    def find_for_enrichment(self, status_type: str = "image", status_value: int = 10) -> List["ProductModel"]:
        """
        Find product models ready for enrichment (Myer-specific).
        
        Args:
            status_type: Type of enrichment status (e.g., 'image', 'copy')
            status_value: Status value to filter by (default: 10 for "ready")
            
        Returns:
            List of product models ready for enrichment
        """
        return self.search_with_builder(
            lambda f: f.attribute_number(f"{status_type}_status", status_value)
        )
    
    def get_by_code(self, code: str) -> "ProductModel":
        """Get a product model by its code."""
        if not hasattr(self._client, '_make_request_sync'):
            raise TypeError("This method requires a synchronous client")
        
        code = validate_identifier(code, "code")
        url = f"/api/rest/v1/product-models/{code}"
        response = self._client._make_request_sync("GET", url)
        
        return self._create_instance(response)
    
    def create_product_model(self, data: Union[Dict[str, Any], ProductModelCreateWrite]) -> "ProductModel":
        """Create a new product model."""
        if not hasattr(self._client, '_make_request_sync'):
            raise TypeError("This method requires a synchronous client")
            
        url = "/api/rest/v1/product-models"
        prepared_data = self._prepare_request_data(data)
        response = self._client._make_request_sync("POST", url, json_data=prepared_data)
        
        return self._create_instance(response)
    
    def update_by_code(self, code: str, data: Union[Dict[str, Any], ProductModelWrite]) -> "ProductModel":
        """Update a product model by code."""
        if not hasattr(self._client, '_make_request_sync'):
            raise TypeError("This method requires a synchronous client")
            
        code = validate_identifier(code, "code")
        url = f"/api/rest/v1/product-models/{code}"
        prepared_data = self._prepare_request_data(data)
        response = self._client._make_request_sync("PATCH", url, json_data=prepared_data)
        
        # Akeneo PATCH often returns empty response, so fetch the updated product model
        if response:
            return self._create_instance(response)
        else:
            return self.get_by_code(code)
    
    def delete_by_code(self, code: str) -> None:
        """Delete a product model by code."""
        if not hasattr(self._client, '_make_request_sync'):
            raise TypeError("This method requires a synchronous client")
            
        code = validate_identifier(code, "code")
        url = f"/api/rest/v1/product-models/{code}"
        self._client._make_request_sync("DELETE", url)
    
    def bulk_update(self, product_models: List[Union[Dict[str, Any], ProductModelWrite]]) -> List[Dict[str, Any]]:
        """
        Update multiple product models at once.
        
        Args:
            product_models: List of product model data to update
            
        Returns:
            List of status responses for each product model update
        """
        if not hasattr(self._client, '_make_request_sync'):
            raise TypeError("This method requires a synchronous client")
        
        # Prepare the NDJSON payload
        lines = []
        for product_model_data in product_models:
            if hasattr(product_model_data, 'model_dump'):
                prepared_data = product_model_data.model_dump(by_alias=True, exclude_none=True)
            else:
                prepared_data = product_model_data
            lines.append(json.dumps(prepared_data))
        
        ndjson_payload = '\n'.join(lines)
        
        url = "/api/rest/v1/product-models"
        
        response = self._client._make_request_sync("PATCH", url, form_data=ndjson_payload)
        
        # Parse NDJSON response
        if isinstance(response, str):
            results = []
            for line in response.strip().split('\n'):
                if line.strip():
                    results.append(json.loads(line))
            return results
        
        return response if isinstance(response, list) else [response]
    
    def update_enrichment_status(self, code: str, status_type: str, status_value: int) -> None:
        """
        Update the enrichment status for a product model.
        
        This is specific to Myer's implementation where enrichment status
        is tracked (e.g., image status 10, copy status 10, etc.)
        
        Args:
            code: Product model code
            status_type: Type of status (e.g., 'image', 'copy')
            status_value: Status value (e.g., 10, 20, 30)
        """
        if not hasattr(self._client, '_make_request_sync'):
            raise TypeError("This method requires a synchronous client")
        
        code = validate_identifier(code, "code")
        
        # This would typically update a specific attribute value
        # The exact implementation depends on how Myer structures their enrichment status
        status_data = {
            "values": {
                f"{status_type}_status": [
                    {
                        "data": status_value,
                        "locale": None,
                        "scope": None
                    }
                ]
            }
        }
        
        self.update_by_code(code, status_data)
    
    # Asynchronous search methods
    
    async def search_with_builder_async(self, builder: Union[SearchBuilder, Callable[[FilterBuilder], None]],
                                       paginated: bool = False) -> Union[List["ProductModel"], "PaginatedResponse[ProductModel]"]:
        """
        Search for product models using SearchBuilder or FilterBuilder asynchronously.
        
        Args:
            builder: SearchBuilder instance or function that configures a FilterBuilder
            paginated: Whether to return paginated response
            
        Returns:
            List of product models or PaginatedResponse
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
        
        url = "/api/rest/v1/product-models"
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
    
    async def find_by_identifier_async(self, identifiers: List[str]) -> List["ProductModel"]:
        """Find product models by identifiers asynchronously."""
        return await self.search_with_builder_async(lambda f: f.identifier(identifiers))
    
    async def find_in_categories_async(self, category_codes: List[str], include_children: bool = False) -> List["ProductModel"]:
        """Find product models in categories asynchronously."""
        operator = "IN CHILDREN" if include_children else "IN"
        return await self.search_with_builder_async(lambda f: f.categories(category_codes, operator))
    
    async def find_by_family_async(self, family_codes: List[str]) -> List["ProductModel"]:
        """Find product models by family asynchronously."""
        return await self.search_with_builder_async(lambda f: f.family(family_codes))
    
    async def find_complete_async(self, scope: str, locale: Optional[str] = None,
                                 locales: Optional[List[str]] = None) -> List["ProductModel"]:
        """Find complete product models asynchronously."""
        return await self.search_with_builder_async(
            lambda f: f.model_completeness(scope, "ALL COMPLETE", locale, locales)
        )
    
    async def find_incomplete_async(self, scope: str, locale: Optional[str] = None,
                                   locales: Optional[List[str]] = None) -> List["ProductModel"]:
        """Find incomplete product models asynchronously."""
        return await self.search_with_builder_async(
            lambda f: f.model_completeness(scope, "AT LEAST INCOMPLETE", locale, locales)
        )
    
    async def find_recently_updated_async(self, days: int) -> List["ProductModel"]:
        """Find recently updated product models asynchronously."""
        return await self.search_with_builder_async(lambda f: f.updated(days, "SINCE LAST N DAYS"))
    
    async def find_root_models_async(self) -> List["ProductModel"]:
        """Find root product models asynchronously."""
        return await self.search_with_builder_async(lambda f: f.parent("", "EMPTY"))
    
    async def find_sub_models_async(self, parent_codes: Optional[List[str]] = None) -> List["ProductModel"]:
        """Find sub product models asynchronously."""
        if parent_codes:
            return await self.search_with_builder_async(lambda f: f.parent(parent_codes, "IN"))
        else:
            return await self.search_with_builder_async(lambda f: f.parent("", "NOT EMPTY"))
    
    async def find_by_attribute_async(self, attribute_code: str, value: Any, operator: str = "=",
                                     locale: Optional[str] = None, scope: Optional[str] = None) -> List["ProductModel"]:
        """Find product models by attribute asynchronously."""
        return await self.search_with_builder_async(
            lambda f: f.attribute_text(attribute_code, value, operator, locale, scope)
        )
    
    async def find_for_enrichment_async(self, status_type: str = "image", status_value: int = 10) -> List["ProductModel"]:
        """Find product models for enrichment asynchronously."""
        return await self.search_with_builder_async(
            lambda f: f.attribute_number(f"{status_type}_status", status_value)
        )
    
    # Asynchronous methods
    
    async def get_by_code_async(self, code: str) -> "ProductModel":
        """Get a product model by its code asynchronously."""
        if not hasattr(self._client, '_make_request_async'):
            raise TypeError("This method requires an asynchronous client")
        
        code = validate_identifier(code, "code")
        url = f"/api/rest/v1/product-models/{code}"
        response = await self._client._make_request_async("GET", url)
        
        return self._create_instance(response)
    
    async def create_product_model_async(self, data: Union[Dict[str, Any], ProductModelCreateWrite]) -> "ProductModel":
        """Create a new product model asynchronously."""
        if not hasattr(self._client, '_make_request_async'):
            raise TypeError("This method requires an asynchronous client")
            
        url = "/api/rest/v1/product-models"
        prepared_data = self._prepare_request_data(data)
        response = await self._client._make_request_async("POST", url, json_data=prepared_data)
        
        return self._create_instance(response)
    
    async def update_by_code_async(self, code: str, data: Union[Dict[str, Any], ProductModelWrite]) -> "ProductModel":
        """Update a product model by code asynchronously."""
        if not hasattr(self._client, '_make_request_async'):
            raise TypeError("This method requires an asynchronous client")
            
        code = validate_identifier(code, "code")
        url = f"/api/rest/v1/product-models/{code}"
        prepared_data = self._prepare_request_data(data)
        response = await self._client._make_request_async("PATCH", url, json_data=prepared_data)
        
        # Akeneo PATCH often returns empty response, so fetch the updated product model
        if response:
            return self._create_instance(response)
        else:
            return await self.get_by_code_async(code)
    
    async def delete_by_code_async(self, code: str) -> None:
        """Delete a product model by code asynchronously."""
        if not hasattr(self._client, '_make_request_async'):
            raise TypeError("This method requires an asynchronous client")
            
        code = validate_identifier(code, "code")
        url = f"/api/rest/v1/product-models/{code}"
        await self._client._make_request_async("DELETE", url)
    
    async def bulk_update_async(self, product_models: List[Union[Dict[str, Any], ProductModelWrite]]) -> List[Dict[str, Any]]:
        """
        Update multiple product models at once asynchronously.
        
        Args:
            product_models: List of product model data to update
            
        Returns:
            List of status responses for each product model update
        """
        if not hasattr(self._client, '_make_request_async'):
            raise TypeError("This method requires an asynchronous client")
        
        # Prepare the NDJSON payload
        lines = []
        for product_model_data in product_models:
            if hasattr(product_model_data, 'model_dump'):
                prepared_data = product_model_data.model_dump(by_alias=True, exclude_none=True)
            else:
                prepared_data = product_model_data
            lines.append(json.dumps(prepared_data))
        
        ndjson_payload = '\n'.join(lines)
        
        url = "/api/rest/v1/product-models"
        
        response = await self._client._make_request_async("PATCH", url, form_data=ndjson_payload)
        
        # Parse NDJSON response
        if isinstance(response, str):
            results = []
            for line in response.strip().split('\n'):
                if line.strip():
                    results.append(json.loads(line))
            return results
        
        return response if isinstance(response, list) else [response]
    
    async def update_enrichment_status_async(self, code: str, status_type: str, status_value: int) -> None:
        """
        Update the enrichment status for a product model asynchronously.
        
        This is specific to Myer's implementation where enrichment status
        is tracked (e.g., image status 10, copy status 10, etc.)
        
        Args:
            code: Product model code
            status_type: Type of status (e.g., 'image', 'copy')
            status_value: Status value (e.g., 10, 20, 30)
        """
        if not hasattr(self._client, '_make_request_async'):
            raise TypeError("This method requires an asynchronous client")
        
        code = validate_identifier(code, "code")
        
        # This would typically update a specific attribute value
        # The exact implementation depends on how Myer structures their enrichment status
        status_data = {
            "values": {
                f"{status_type}_status": [
                    {
                        "data": status_value,
                        "locale": None,
                        "scope": None
                    }
                ]
            }
        }
        
        await self.update_by_code_async(code, status_data)
