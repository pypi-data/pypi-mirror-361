# resources/system.py

from typing import Dict, Any, List, Optional, TYPE_CHECKING

from .base import AkeneoResource

if TYPE_CHECKING:
    from ..client import AkeneoClient, AkeneoAsyncClient


class System(AkeneoResource):
    """System resource for Akeneo API."""
    
    def get_endpoints(self) -> Dict[str, Any]:
        """
        Get list of all available endpoints.
        
        This endpoint doesn't require authentication.
        
        Returns:
            Dictionary containing all available endpoints
        """
        if not hasattr(self._client, '_make_request_sync'):
            raise TypeError("This method requires a synchronous client")
        
        url = "/api/rest/v1"
        
        # For this endpoint, we don't need authentication
        # but we'll use the client's request method anyway
        response = self._client._make_request_sync("GET", url)
        return response
    
    def get_system_information(self) -> Dict[str, Any]:
        """
        Get system information including version and edition.
        
        Returns:
            Dictionary containing system information like:
            - version: Version of the PIM
            - edition: Edition of the PIM (CE, EE, Serenity, etc.)
        """
        if not hasattr(self._client, '_make_request_sync'):
            raise TypeError("This method requires a synchronous client")
        
        url = "/api/rest/v1/system-information"
        response = self._client._make_request_sync("GET", url)
        return response
    
    def check_health(self) -> bool:
        """
        Check if the Akeneo API is healthy by making a basic request.
        
        Returns:
            True if the API is accessible, False otherwise
        """
        try:
            self.get_endpoints()
            return True
        except Exception:
            return False
    
    def get_version(self) -> str:
        """
        Get the PIM version.
        
        Returns:
            Version string
        """
        system_info = self.get_system_information()
        return system_info.get("version", "unknown")
    
    def get_edition(self) -> str:
        """
        Get the PIM edition.
        
        Returns:
            Edition string (e.g., "CE", "EE", "Serenity")
        """
        system_info = self.get_system_information()
        return system_info.get("edition", "unknown")
    
    # Asynchronous versions
    
    async def get_endpoints_async(self) -> Dict[str, Any]:
        """
        Get list of all available endpoints asynchronously.
        
        Returns:
            Dictionary containing all available endpoints
        """
        if not hasattr(self._client, '_make_request_async'):
            raise TypeError("This method requires an asynchronous client")
        
        url = "/api/rest/v1"
        response = await self._client._make_request_async("GET", url)
        return response
    
    async def get_system_information_async(self) -> Dict[str, Any]:
        """
        Get system information including version and edition asynchronously.
        
        Returns:
            Dictionary containing system information
        """
        if not hasattr(self._client, '_make_request_async'):
            raise TypeError("This method requires an asynchronous client")
        
        url = "/api/rest/v1/system-information"
        response = await self._client._make_request_async("GET", url)
        return response
    
    async def check_health_async(self) -> bool:
        """
        Check if the Akeneo API is healthy asynchronously.
        
        Returns:
            True if the API is accessible, False otherwise
        """
        try:
            await self.get_endpoints_async()
            return True
        except Exception:
            return False
    
    async def get_version_async(self) -> str:
        """
        Get the PIM version asynchronously.
        
        Returns:
            Version string
        """
        system_info = await self.get_system_information_async()
        return system_info.get("version", "unknown")
    
    async def get_edition_async(self) -> str:
        """
        Get the PIM edition asynchronously.
        
        Returns:
            Edition string (e.g., "CE", "EE", "Serenity")
        """
        system_info = await self.get_system_information_async()
        return system_info.get("edition", "unknown")
