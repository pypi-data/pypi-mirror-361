# resources/association_type.py

from typing import Dict, Any, List, Optional, Union, TYPE_CHECKING
import json

from .base import AkeneoResource
from ..utils import validate_identifier

if TYPE_CHECKING:
    from ..client import AkeneoClient, AkeneoAsyncClient


class AssociationType(AkeneoResource):
    """Association Type resource for Akeneo API."""
    
    endpoint = "association-types"
    
    def get_by_code(self, code: str) -> "AssociationType":
        """Get an association type by its code."""
        code = validate_identifier(code, "code")
        return self.get(code)
    
    def create_association_type(self, data: Dict[str, Any]) -> "AssociationType":
        """Create a new association type."""
        return self.create(data)
    
    def update_by_code(self, code: str, data: Dict[str, Any]) -> "AssociationType":
        """Update an association type by code."""
        code = validate_identifier(code, "code")
        return self.update(code, data)
    
    def delete_by_code(self, code: str) -> None:
        """Delete an association type by code."""
        code = validate_identifier(code, "code")
        self.delete(code)
    
    def bulk_update(self, association_types: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Update multiple association types at once."""
        if not hasattr(self._client, '_make_request_sync'):
            raise TypeError("This method requires a synchronous client")
        
        # Prepare the NDJSON payload
        lines = []
        for association_type_data in association_types:
            lines.append(json.dumps(association_type_data))
        
        ndjson_payload = '\n'.join(lines)
        url = "/api/rest/v1/association-types"
        
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
    async def get_by_code_async(self, code: str) -> "AssociationType":
        """Get an association type by its code asynchronously."""
        code = validate_identifier(code, "code")
        return await self.get_async(code)
    
    async def create_association_type_async(self, data: Dict[str, Any]) -> "AssociationType":
        """Create a new association type asynchronously."""
        return await self.create_async(data)
    
    async def update_by_code_async(self, code: str, data: Dict[str, Any]) -> "AssociationType":
        """Update an association type by code asynchronously."""
        code = validate_identifier(code, "code")
        return await self.update_async(code, data)
    
    async def delete_by_code_async(self, code: str) -> None:
        """Delete an association type by code asynchronously."""
        code = validate_identifier(code, "code")
        await self.delete_async(code)
    
    async def bulk_update_async(self, association_types: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Update multiple association types at once asynchronously."""
        if not hasattr(self._client, '_make_request_async'):
            raise TypeError("This method requires an asynchronous client")
        
        # Prepare the NDJSON payload
        lines = []
        for association_type_data in association_types:
            lines.append(json.dumps(association_type_data))
        
        ndjson_payload = '\n'.join(lines)
        url = "/api/rest/v1/association-types"
        
        response = await self._client._make_request_async("PATCH", url, form_data=ndjson_payload)
        
        # Parse NDJSON response
        if isinstance(response, str):
            results = []
            for line in response.strip().split('\n'):
                if line.strip():
                    results.append(json.loads(line))
            return results
        
        return response if isinstance(response, list) else [response]
