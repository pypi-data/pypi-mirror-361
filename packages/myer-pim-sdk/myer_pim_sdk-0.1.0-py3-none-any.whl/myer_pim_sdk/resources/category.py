# resources/category.py

from typing import Dict, Any, List, Optional, Union, TYPE_CHECKING, Callable
import json

from .base import AkeneoResource
from ..models.category import CategoryRead, CategoryWrite, CategoryCreateWrite
from ..utils import validate_identifier
from ..search import SearchBuilder, FilterBuilder

if TYPE_CHECKING:
    from ..client import AkeneoClient, AkeneoAsyncClient


class Category(AkeneoResource):
    """Category resource for Akeneo API."""
    
    endpoint = "categories"
    model_class = CategoryRead
    
    def get_by_code(self, code: str) -> "Category":
        """Get a category by its code."""
        code = validate_identifier(code, "code")
        return self.get(code)
    
    def create_category(self, data: Union[Dict[str, Any], CategoryCreateWrite]) -> "Category":
        """Create a new category."""
        return self.create(data)
    
    def update_by_code(self, code: str, data: Union[Dict[str, Any], CategoryWrite]) -> "Category":
        """Update a category by code."""
        code = validate_identifier(code, "code")
        return self.update(code, data)
    
    def delete_by_code(self, code: str) -> None:
        """Delete a category by code."""
        code = validate_identifier(code, "code")
        self.delete(code)
    
    def search_with_builder(self, builder: Union[SearchBuilder, Callable[[FilterBuilder], None]],
                           paginated: bool = False) -> Union[List["Category"], "PaginatedResponse[Category]"]:
        """
        Search for categories using SearchBuilder or FilterBuilder.
        
        Args:
            builder: SearchBuilder instance or function that configures a FilterBuilder
            paginated: Whether to return paginated response
            
        Returns:
            List of categories or PaginatedResponse
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
        
        url = "/api/rest/v1/categories"
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
    
    def find_by_code(self, codes: List[str]) -> List["Category"]:
        """
        Find categories by their codes.
        
        Args:
            codes: List of category codes
            
        Returns:
            List of matching categories
        """
        return self.search_with_builder(
            lambda f: f.raw_filter("code", "IN", codes)
        )
    
    def find_root_categories(self) -> List["Category"]:
        """
        Find all root categories (categories without a parent).
        
        Returns:
            List of root categories
        """
        return self.search_with_builder(
            lambda f: f.raw_filter("parent", "EMPTY")
        )
    
    def find_child_categories(self, parent_code: str) -> List["Category"]:
        """
        Find child categories of a specific parent.
        
        Args:
            parent_code: Code of the parent category
            
        Returns:
            List of child categories
        """
        return self.search_with_builder(
            lambda f: f.raw_filter("parent", "=", parent_code)
        )
    
    def find_recently_updated(self, days: int) -> List["Category"]:
        """
        Find categories updated in the last N days.
        
        Args:
            days: Number of days to look back
            
        Returns:
            List of recently updated categories
        """
        return self.search_with_builder(
            lambda f: f.raw_filter("updated", "SINCE LAST N DAYS", days)
        )
    
    def bulk_update(self, categories: List[Union[Dict[str, Any], CategoryWrite]]) -> List[Dict[str, Any]]:
        """Update multiple categories at once."""
        if not hasattr(self._client, '_make_request_sync'):
            raise TypeError("This method requires a synchronous client")
        
        # Prepare the NDJSON payload
        lines = []
        for category_data in categories:
            if hasattr(category_data, 'model_dump'):
                prepared_data = category_data.model_dump(by_alias=True, exclude_none=True)
            else:
                prepared_data = category_data
            lines.append(json.dumps(prepared_data))
        
        ndjson_payload = '\n'.join(lines)
        url = "/api/rest/v1/categories"
        
        response = self._client._make_request_sync("PATCH", url, form_data=ndjson_payload)
        
        # Parse NDJSON response
        if isinstance(response, str):
            results = []
            for line in response.strip().split('\n'):
                if line.strip():
                    results.append(json.loads(line))
            return results
        
        return response if isinstance(response, list) else [response]
    
    def create_media_file(self, category_code: str, attribute_code: str, file_path: str, 
                         scope: Optional[str] = None, locale: Optional[str] = None) -> Dict[str, Any]:
        """
        Upload a media file for a category attribute.
        
        Args:
            category_code: Code of the category
            attribute_code: Code of the attribute
            file_path: Path to the file to upload
            scope: Channel scope (optional)
            locale: Locale (optional)
        """
        if not hasattr(self._client, '_make_request_sync'):
            raise TypeError("This method requires a synchronous client")
        
        category_code = validate_identifier(category_code, "category_code")
        
        url = "/api/rest/v1/category-media-files"
        
        # Prepare the category JSON
        category_json = {
            "code": category_code,
            "attribute_code": attribute_code,
            "channel": scope,
            "locale": locale
        }
        
        # Prepare the multipart form data
        with open(file_path, 'rb') as f:
            files = {
                'file': f,
            }
            form_data = {
                'category': json.dumps(category_json)
            }
            
            response = self._client._make_request_sync("POST", url, form_data=form_data, files=files)
        
        return response
    
    def download_media_file(self, file_path: str) -> bytes:
        """Download a category media file."""
        if not hasattr(self._client, '_make_request_sync'):
            raise TypeError("This method requires a synchronous client")
        
        url = f"/api/rest/v1/category-media-files/{file_path}/download"
        response = self._client._make_request_sync("GET", url)
        
        # For binary content, we need to access the raw response
        # This might need to be adjusted based on how the client handles binary responses
        return response
    
    # Asynchronous versions
    async def get_by_code_async(self, code: str) -> "Category":
        """Get a category by its code asynchronously."""
        code = validate_identifier(code, "code")
        return await self.get_async(code)
    
    async def create_category_async(self, data: Union[Dict[str, Any], CategoryCreateWrite]) -> "Category":
        """Create a new category asynchronously."""
        return await self.create_async(data)
    
    async def update_by_code_async(self, code: str, data: Union[Dict[str, Any], CategoryWrite]) -> "Category":
        """Update a category by code asynchronously."""
        code = validate_identifier(code, "code")
        return await self.update_async(code, data)
    
    async def delete_by_code_async(self, code: str) -> None:
        """Delete a category by code asynchronously."""
        code = validate_identifier(code, "code")
        await self.delete_async(code)
    
    async def bulk_update_async(self, categories: List[Union[Dict[str, Any], CategoryWrite]]) -> List[Dict[str, Any]]:
        """Update multiple categories at once asynchronously."""
        if not hasattr(self._client, '_make_request_async'):
            raise TypeError("This method requires an asynchronous client")
        
        # Prepare the NDJSON payload
        lines = []
        for category_data in categories:
            if hasattr(category_data, 'model_dump'):
                prepared_data = category_data.model_dump(by_alias=True, exclude_none=True)
            else:
                prepared_data = category_data
            lines.append(json.dumps(prepared_data))
        
        ndjson_payload = '\n'.join(lines)
        url = "/api/rest/v1/categories"
        
        response = await self._client._make_request_async("PATCH", url, form_data=ndjson_payload)
        
        # Parse NDJSON response
        if isinstance(response, str):
            results = []
            for line in response.strip().split('\n'):
                if line.strip():
                    results.append(json.loads(line))
            return results
        
        return response if isinstance(response, list) else [response]
    
    async def create_media_file_async(self, category_code: str, attribute_code: str, file_path: str, 
                                    scope: Optional[str] = None, locale: Optional[str] = None) -> Dict[str, Any]:
        """
        Upload a media file for a category attribute asynchronously.
        
        Args:
            category_code: Code of the category
            attribute_code: Code of the attribute
            file_path: Path to the file to upload
            scope: Channel scope (optional)
            locale: Locale (optional)
        """
        if not hasattr(self._client, '_make_request_async'):
            raise TypeError("This method requires an asynchronous client")
        
        category_code = validate_identifier(category_code, "category_code")
        
        url = "/api/rest/v1/category-media-files"
        
        # Prepare the category JSON
        category_json = {
            "code": category_code,
            "attribute_code": attribute_code,
            "channel": scope,
            "locale": locale
        }
        
        # Prepare the multipart form data
        with open(file_path, 'rb') as f:
            files = {
                'file': f,
            }
            form_data = {
                'category': json.dumps(category_json)
            }
            
            response = await self._client._make_request_async("POST", url, form_data=form_data, files=files)
        
        return response
    
    async def download_media_file_async(self, file_path: str) -> bytes:
        """Download a category media file asynchronously."""
        if not hasattr(self._client, '_make_request_async'):
            raise TypeError("This method requires an asynchronous client")
        
        url = f"/api/rest/v1/category-media-files/{file_path}/download"
        response = await self._client._make_request_async("GET", url)
        
        # For binary content, we need to access the raw response
        return response
