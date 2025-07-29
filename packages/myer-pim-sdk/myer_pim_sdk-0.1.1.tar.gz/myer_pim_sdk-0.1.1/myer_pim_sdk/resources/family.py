# resources/family.py

from typing import Dict, Any, List, Optional, Union, TYPE_CHECKING
import json

from .base import AkeneoResource
from ..models.family import FamilyRead, FamilyWrite, FamilyCreateWrite
from ..utils import validate_identifier

if TYPE_CHECKING:
    from ..client import AkeneoClient, AkeneoAsyncClient


class Family(AkeneoResource):
    """Family resource for Akeneo API."""
    
    endpoint = "families"
    model_class = FamilyRead
    
    def get_by_code(self, code: str) -> "Family":
        """Get a family by its code."""
        code = validate_identifier(code, "code")
        return self.get(code)
    
    def create_family(self, data: Union[Dict[str, Any], FamilyCreateWrite]) -> "Family":
        """Create a new family."""
        return self.create(data)
    
    def update_by_code(self, code: str, data: Union[Dict[str, Any], FamilyWrite]) -> "Family":
        """Update a family by code."""
        code = validate_identifier(code, "code")
        return self.update(code, data)
    
    def delete_by_code(self, code: str) -> None:
        """Delete a family by code."""
        code = validate_identifier(code, "code")
        self.delete(code)
    
    def bulk_update(self, families: List[Union[Dict[str, Any], FamilyWrite]]) -> List[Dict[str, Any]]:
        """Update multiple families at once."""
        if not hasattr(self._client, '_make_request_sync'):
            raise TypeError("This method requires a synchronous client")
        
        # Prepare the NDJSON payload
        lines = []
        for family_data in families:
            if hasattr(family_data, 'model_dump'):
                prepared_data = family_data.model_dump(by_alias=True, exclude_none=True)
            else:
                prepared_data = family_data
            lines.append(json.dumps(prepared_data))
        
        ndjson_payload = '\n'.join(lines)
        url = "/api/rest/v1/families"
        
        response = self._client._make_request_sync("PATCH", url, form_data=ndjson_payload)
        
        # Parse NDJSON response
        if isinstance(response, str):
            results = []
            for line in response.strip().split('\n'):
                if line.strip():
                    results.append(json.loads(line))
            return results
        
        return response if isinstance(response, list) else [response]
    
    # Asynchronous versions
    async def get_by_code_async(self, code: str) -> "Family":
        """Get a family by its code asynchronously."""
        code = validate_identifier(code, "code")
        return await self.get_async(code)
    
    async def create_family_async(self, data: Union[Dict[str, Any], FamilyCreateWrite]) -> "Family":
        """Create a new family asynchronously."""
        return await self.create_async(data)
    
    async def update_by_code_async(self, code: str, data: Union[Dict[str, Any], FamilyWrite]) -> "Family":
        """Update a family by code asynchronously."""
        code = validate_identifier(code, "code")
        return await self.update_async(code, data)
    
    async def delete_by_code_async(self, code: str) -> None:
        """Delete a family by code asynchronously."""
        code = validate_identifier(code, "code")
        await self.delete_async(code)
    
    async def bulk_update_async(self, families: List[Union[Dict[str, Any], FamilyWrite]]) -> List[Dict[str, Any]]:
        """Update multiple families at once asynchronously."""
        if not hasattr(self._client, '_make_request_async'):
            raise TypeError("This method requires an asynchronous client")
        
        # Prepare the NDJSON payload
        lines = []
        for family_data in families:
            if hasattr(family_data, 'model_dump'):
                prepared_data = family_data.model_dump(by_alias=True, exclude_none=True)
            else:
                prepared_data = family_data
            lines.append(json.dumps(prepared_data))
        
        ndjson_payload = '\n'.join(lines)
        url = "/api/rest/v1/families"
        
        response = await self._client._make_request_async("PATCH", url, form_data=ndjson_payload)
        
        # Parse NDJSON response
        if isinstance(response, str):
            results = []
            for line in response.strip().split('\n'):
                if line.strip():
                    results.append(json.loads(line))
            return results
        
        return response if isinstance(response, list) else [response]


class FamilyVariant(AkeneoResource):
    """Family Variant resource for Akeneo API."""
    
    def __init__(self, *, client, family_code: Optional[str] = None, **kwargs):
        self.family_code = family_code
        if family_code:
            kwargs['parent_path'] = f"/api/rest/v1/families/{family_code}"
        super().__init__(client=client, **kwargs)
    
    @property
    def endpoint(self) -> str:
        return "variants"
    
    def get_by_code(self, family_code: str, variant_code: str) -> "FamilyVariant":
        """Get a family variant by family code and variant code."""
        family_code = validate_identifier(family_code, "family_code")
        variant_code = validate_identifier(variant_code, "variant_code")
        
        if not hasattr(self._client, '_make_request_sync'):
            raise TypeError("This method requires a synchronous client")
        
        url = f"/api/rest/v1/families/{family_code}/variants/{variant_code}"
        response = self._client._make_request_sync("GET", url)
        
        return self._create_instance(response)
    
    def list_for_family(self, family_code: str, **params) -> List["FamilyVariant"]:
        """List family variants for a specific family."""
        family_code = validate_identifier(family_code, "family_code")
        
        if not hasattr(self._client, '_make_request_sync'):
            raise TypeError("This method requires a synchronous client")
        
        url = f"/api/rest/v1/families/{family_code}/variants"
        prepared_params = self._prepare_request_params(params)
        response = self._client._make_request_sync("GET", url, params=prepared_params)
        
        items = self._extract_items(response)
        return [self._create_instance(item) for item in items]
    
    def create_for_family(self, family_code: str, data: Dict[str, Any]) -> "FamilyVariant":
        """Create a family variant for a specific family."""
        family_code = validate_identifier(family_code, "family_code")
        
        if not hasattr(self._client, '_make_request_sync'):
            raise TypeError("This method requires a synchronous client")
        
        url = f"/api/rest/v1/families/{family_code}/variants"
        prepared_data = self._prepare_request_data(data)
        response = self._client._make_request_sync("POST", url, json_data=prepared_data)
        
        return self._create_instance(response)
    
    def update_by_code(self, family_code: str, variant_code: str, data: Dict[str, Any]) -> "FamilyVariant":
        """Update a family variant."""
        family_code = validate_identifier(family_code, "family_code")
        variant_code = validate_identifier(variant_code, "variant_code")
        
        if not hasattr(self._client, '_make_request_sync'):
            raise TypeError("This method requires a synchronous client")
        
        url = f"/api/rest/v1/families/{family_code}/variants/{variant_code}"
        prepared_data = self._prepare_request_data(data)
        response = self._client._make_request_sync("PATCH", url, json_data=prepared_data)
        
        if response:
            return self._create_instance(response)
        else:
            return self.get_by_code(family_code, variant_code)
    
    # Asynchronous versions
    async def get_by_code_async(self, family_code: str, variant_code: str) -> "FamilyVariant":
        """Get a family variant by family code and variant code asynchronously."""
        family_code = validate_identifier(family_code, "family_code")
        variant_code = validate_identifier(variant_code, "variant_code")
        
        if not hasattr(self._client, '_make_request_async'):
            raise TypeError("This method requires an asynchronous client")
        
        url = f"/api/rest/v1/families/{family_code}/variants/{variant_code}"
        response = await self._client._make_request_async("GET", url)
        
        return self._create_instance(response)
    
    async def list_for_family_async(self, family_code: str, **params) -> List["FamilyVariant"]:
        """List family variants for a specific family asynchronously."""
        family_code = validate_identifier(family_code, "family_code")
        
        if not hasattr(self._client, '_make_request_async'):
            raise TypeError("This method requires an asynchronous client")
        
        url = f"/api/rest/v1/families/{family_code}/variants"
        prepared_params = self._prepare_request_params(params)
        response = await self._client._make_request_async("GET", url, params=prepared_params)
        
        items = self._extract_items(response)
        return [self._create_instance(item) for item in items]
    
    async def create_for_family_async(self, family_code: str, data: Dict[str, Any]) -> "FamilyVariant":
        """Create a family variant for a specific family asynchronously."""
        family_code = validate_identifier(family_code, "family_code")
        
        if not hasattr(self._client, '_make_request_async'):
            raise TypeError("This method requires an asynchronous client")
        
        url = f"/api/rest/v1/families/{family_code}/variants"
        prepared_data = self._prepare_request_data(data)
        response = await self._client._make_request_async("POST", url, json_data=prepared_data)
        
        return self._create_instance(response)
    
    async def update_by_code_async(self, family_code: str, variant_code: str, data: Dict[str, Any]) -> "FamilyVariant":
        """Update a family variant asynchronously."""
        family_code = validate_identifier(family_code, "family_code")
        variant_code = validate_identifier(variant_code, "variant_code")
        
        if not hasattr(self._client, '_make_request_async'):
            raise TypeError("This method requires an asynchronous client")
        
        url = f"/api/rest/v1/families/{family_code}/variants/{variant_code}"
        prepared_data = self._prepare_request_data(data)
        response = await self._client._make_request_async("PATCH", url, json_data=prepared_data)
        
        if response:
            return self._create_instance(response)
        else:
            return await self.get_by_code_async(family_code, variant_code)
