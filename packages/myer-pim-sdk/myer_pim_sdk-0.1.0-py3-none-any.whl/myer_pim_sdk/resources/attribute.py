# resources/attribute.py

from typing import Dict, Any, List, Optional, Union, TYPE_CHECKING
import json

from .base import AkeneoResource
from ..models.attribute import AttributeRead, AttributeWrite, AttributeCreateWrite
from ..utils import validate_identifier

if TYPE_CHECKING:
    from ..client import AkeneoClient, AkeneoAsyncClient


class Attribute(AkeneoResource):
    """Attribute resource for Akeneo API."""
    
    endpoint = "attributes"
    model_class = AttributeRead
    
    def get_by_code(self, code: str) -> "Attribute":
        """Get an attribute by its code."""
        code = validate_identifier(code, "code")
        return self.get(code)
    
    def create_attribute(self, data: Union[Dict[str, Any], AttributeCreateWrite]) -> "Attribute":
        """Create a new attribute."""
        return self.create(data)
    
    def update_by_code(self, code: str, data: Union[Dict[str, Any], AttributeWrite]) -> "Attribute":
        """Update an attribute by code."""
        code = validate_identifier(code, "code")
        return self.update(code, data)
    
    def delete_by_code(self, code: str) -> None:
        """Delete an attribute by code."""
        code = validate_identifier(code, "code")
        self.delete(code)
    
    def bulk_update(self, attributes: List[Union[Dict[str, Any], AttributeWrite]]) -> List[Dict[str, Any]]:
        """Update multiple attributes at once."""
        if not hasattr(self._client, '_make_request_sync'):
            raise TypeError("This method requires a synchronous client")
        
        # Prepare the NDJSON payload
        lines = []
        for attribute_data in attributes:
            if hasattr(attribute_data, 'model_dump'):
                prepared_data = attribute_data.model_dump(by_alias=True, exclude_none=True)
            else:
                prepared_data = attribute_data
            lines.append(json.dumps(prepared_data))
        
        ndjson_payload = '\n'.join(lines)
        url = "/api/rest/v1/attributes"
        
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
    async def get_by_code_async(self, code: str) -> "Attribute":
        """Get an attribute by its code asynchronously."""
        code = validate_identifier(code, "code")
        return await self.get_async(code)
    
    async def create_attribute_async(self, data: Union[Dict[str, Any], AttributeCreateWrite]) -> "Attribute":
        """Create a new attribute asynchronously."""
        return await self.create_async(data)
    
    async def update_by_code_async(self, code: str, data: Union[Dict[str, Any], AttributeWrite]) -> "Attribute":
        """Update an attribute by code asynchronously."""
        code = validate_identifier(code, "code")
        return await self.update_async(code, data)
    
    async def delete_by_code_async(self, code: str) -> None:
        """Delete an attribute by code asynchronously."""
        code = validate_identifier(code, "code")
        await self.delete_async(code)
    
    async def bulk_update_async(self, attributes: List[Union[Dict[str, Any], AttributeWrite]]) -> List[Dict[str, Any]]:
        """Update multiple attributes at once asynchronously."""
        if not hasattr(self._client, '_make_request_async'):
            raise TypeError("This method requires an asynchronous client")
        
        # Prepare the NDJSON payload
        lines = []
        for attribute_data in attributes:
            if hasattr(attribute_data, 'model_dump'):
                prepared_data = attribute_data.model_dump(by_alias=True, exclude_none=True)
            else:
                prepared_data = attribute_data
            lines.append(json.dumps(prepared_data))
        
        ndjson_payload = '\n'.join(lines)
        url = "/api/rest/v1/attributes"
        
        response = await self._client._make_request_async("PATCH", url, form_data=ndjson_payload)
        
        # Parse NDJSON response
        if isinstance(response, str):
            results = []
            for line in response.strip().split('\n'):
                if line.strip():
                    results.append(json.loads(line))
            return results
        
        return response if isinstance(response, list) else [response]


class AttributeOption(AkeneoResource):
    """Attribute Option resource for Akeneo API."""
    
    def __init__(self, *, client, attribute_code: Optional[str] = None, **kwargs):
        self.attribute_code = attribute_code
        if attribute_code:
            kwargs['parent_path'] = f"/api/rest/v1/attributes/{attribute_code}"
        super().__init__(client=client, **kwargs)
    
    @property
    def endpoint(self) -> str:
        return "options"
    
    def get_by_code(self, attribute_code: str, option_code: str) -> "AttributeOption":
        """Get an attribute option by attribute code and option code."""
        attribute_code = validate_identifier(attribute_code, "attribute_code")
        option_code = validate_identifier(option_code, "option_code")
        
        if not hasattr(self._client, '_make_request_sync'):
            raise TypeError("This method requires a synchronous client")
        
        url = f"/api/rest/v1/attributes/{attribute_code}/options/{option_code}"
        response = self._client._make_request_sync("GET", url)
        
        return self._create_instance(response)
    
    def list_for_attribute(self, attribute_code: str, **params) -> List["AttributeOption"]:
        """List attribute options for a specific attribute."""
        attribute_code = validate_identifier(attribute_code, "attribute_code")
        
        if not hasattr(self._client, '_make_request_sync'):
            raise TypeError("This method requires a synchronous client")
        
        url = f"/api/rest/v1/attributes/{attribute_code}/options"
        prepared_params = self._prepare_request_params(params)
        response = self._client._make_request_sync("GET", url, params=prepared_params)
        
        items = self._extract_items(response)
        return [self._create_instance(item) for item in items]
    
    def create_for_attribute(self, attribute_code: str, data: Dict[str, Any]) -> "AttributeOption":
        """Create an attribute option for a specific attribute."""
        attribute_code = validate_identifier(attribute_code, "attribute_code")
        
        if not hasattr(self._client, '_make_request_sync'):
            raise TypeError("This method requires a synchronous client")
        
        url = f"/api/rest/v1/attributes/{attribute_code}/options"
        prepared_data = self._prepare_request_data(data)
        response = self._client._make_request_sync("POST", url, json_data=prepared_data)
        
        return self._create_instance(response)
    
    def update_by_code(self, attribute_code: str, option_code: str, data: Dict[str, Any]) -> "AttributeOption":
        """Update an attribute option."""
        attribute_code = validate_identifier(attribute_code, "attribute_code")
        option_code = validate_identifier(option_code, "option_code")
        
        if not hasattr(self._client, '_make_request_sync'):
            raise TypeError("This method requires a synchronous client")
        
        url = f"/api/rest/v1/attributes/{attribute_code}/options/{option_code}"
        prepared_data = self._prepare_request_data(data)
        response = self._client._make_request_sync("PATCH", url, json_data=prepared_data)
        
        if response:
            return self._create_instance(response)
        else:
            return self.get_by_code(attribute_code, option_code)
    
    def bulk_update_for_attribute(self, attribute_code: str, options: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Update multiple attribute options for a specific attribute."""
        attribute_code = validate_identifier(attribute_code, "attribute_code")
        
        if not hasattr(self._client, '_make_request_sync'):
            raise TypeError("This method requires a synchronous client")
        
        # Prepare the NDJSON payload
        lines = []
        for option_data in options:
            lines.append(json.dumps(option_data))
        
        ndjson_payload = '\n'.join(lines)
        url = f"/api/rest/v1/attributes/{attribute_code}/options"
        
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
    async def get_by_code_async(self, attribute_code: str, option_code: str) -> "AttributeOption":
        """Get an attribute option by attribute code and option code asynchronously."""
        attribute_code = validate_identifier(attribute_code, "attribute_code")
        option_code = validate_identifier(option_code, "option_code")
        
        if not hasattr(self._client, '_make_request_async'):
            raise TypeError("This method requires an asynchronous client")
        
        url = f"/api/rest/v1/attributes/{attribute_code}/options/{option_code}"
        response = await self._client._make_request_async("GET", url)
        
        return self._create_instance(response)
    
    async def list_for_attribute_async(self, attribute_code: str, **params) -> List["AttributeOption"]:
        """List attribute options for a specific attribute asynchronously."""
        attribute_code = validate_identifier(attribute_code, "attribute_code")
        
        if not hasattr(self._client, '_make_request_async'):
            raise TypeError("This method requires an asynchronous client")
        
        url = f"/api/rest/v1/attributes/{attribute_code}/options"
        prepared_params = self._prepare_request_params(params)
        response = await self._client._make_request_async("GET", url, params=prepared_params)
        
        items = self._extract_items(response)
        return [self._create_instance(item) for item in items]
    
    async def create_for_attribute_async(self, attribute_code: str, data: Dict[str, Any]) -> "AttributeOption":
        """Create an attribute option for a specific attribute asynchronously."""
        attribute_code = validate_identifier(attribute_code, "attribute_code")
        
        if not hasattr(self._client, '_make_request_async'):
            raise TypeError("This method requires an asynchronous client")
        
        url = f"/api/rest/v1/attributes/{attribute_code}/options"
        prepared_data = self._prepare_request_data(data)
        response = await self._client._make_request_async("POST", url, json_data=prepared_data)
        
        return self._create_instance(response)
    
    async def update_by_code_async(self, attribute_code: str, option_code: str, data: Dict[str, Any]) -> "AttributeOption":
        """Update an attribute option asynchronously."""
        attribute_code = validate_identifier(attribute_code, "attribute_code")
        option_code = validate_identifier(option_code, "option_code")
        
        if not hasattr(self._client, '_make_request_async'):
            raise TypeError("This method requires an asynchronous client")
        
        url = f"/api/rest/v1/attributes/{attribute_code}/options/{option_code}"
        prepared_data = self._prepare_request_data(data)
        response = await self._client._make_request_async("PATCH", url, json_data=prepared_data)
        
        if response:
            return self._create_instance(response)
        else:
            return await self.get_by_code_async(attribute_code, option_code)


class AttributeGroup(AkeneoResource):
    """Attribute Group resource for Akeneo API."""
    
    endpoint = "attribute-groups"
    
    def get_by_code(self, code: str) -> "AttributeGroup":
        """Get an attribute group by its code."""
        code = validate_identifier(code, "code")
        return self.get(code)
    
    def create_attribute_group(self, data: Dict[str, Any]) -> "AttributeGroup":
        """Create a new attribute group."""
        return self.create(data)
    
    def update_by_code(self, code: str, data: Dict[str, Any]) -> "AttributeGroup":
        """Update an attribute group by code."""
        code = validate_identifier(code, "code")
        return self.update(code, data)
    
    def delete_by_code(self, code: str) -> None:
        """Delete an attribute group by code."""
        code = validate_identifier(code, "code")
        self.delete(code)
    
    # Asynchronous versions
    async def get_by_code_async(self, code: str) -> "AttributeGroup":
        """Get an attribute group by its code asynchronously."""
        code = validate_identifier(code, "code")
        return await self.get_async(code)
    
    async def create_attribute_group_async(self, data: Dict[str, Any]) -> "AttributeGroup":
        """Create a new attribute group asynchronously."""
        return await self.create_async(data)
    
    async def update_by_code_async(self, code: str, data: Dict[str, Any]) -> "AttributeGroup":
        """Update an attribute group by code asynchronously."""
        code = validate_identifier(code, "code")
        return await self.update_async(code, data)
    
    async def delete_by_code_async(self, code: str) -> None:
        """Delete an attribute group by code asynchronously."""
        code = validate_identifier(code, "code")
        await self.delete_async(code)
