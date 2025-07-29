# resources/media_file.py

from typing import Dict, Any, List, Optional, Union, TYPE_CHECKING
import json

from .base import AkeneoResource
from ..models.media_file import MediaFileRead, MediaFileUpload
from ..utils import validate_identifier

if TYPE_CHECKING:
    from ..client import AkeneoClient, AkeneoAsyncClient


class MediaFile(AkeneoResource):
    """
    Media File resource for Akeneo API.
    
    This is particularly important for Myer's enrichment process,
    as suppliers need to upload product images.
    """
    
    endpoint = "media-files"
    model_class = MediaFileRead
    
    def get_by_code(self, code: str) -> "MediaFile":
        """Get a media file by its code."""
        code = validate_identifier(code, "code")
        return self.get(code)
    
    def upload_for_product(self, product_identifier: str, attribute_code: str, file_path: str,
                          scope: Optional[str] = None, locale: Optional[str] = None) -> "MediaFile":
        """
        Upload a media file for a product.
        
        Args:
            product_identifier: Product identifier (SKU)
            attribute_code: Attribute code for the media
            file_path: Path to the file to upload
            scope: Channel scope (optional)
            locale: Locale (optional)
            
        Returns:
            MediaFile instance representing the uploaded file
        """
        if not hasattr(self._client, '_make_request_sync'):
            raise TypeError("This method requires a synchronous client")
        
        product_identifier = validate_identifier(product_identifier, "product_identifier")
        
        url = "/api/rest/v1/media-files"
        
        # Prepare the product JSON as per Myer's documentation
        product_json = {
            "identifier": product_identifier,
            "attribute": attribute_code,
            "scope": scope,
            "locale": locale
        }
        
        # Prepare the multipart form data
        with open(file_path, 'rb') as f:
            files = {
                'file': f,
            }
            form_data = {
                'product': json.dumps(product_json)
            }
            
            response = self._client._make_request_sync("POST", url, form_data=form_data, files=files)
        
        return self._create_instance(response)
    
    def upload_for_product_model(self, product_model_code: str, attribute_code: str, file_path: str,
                                scope: Optional[str] = None, locale: Optional[str] = None) -> "MediaFile":
        """
        Upload a media file for a product model.
        
        This is the main method for Myer's enrichment process since
        image enrichment is typically done at the product model level.
        
        Args:
            product_model_code: Product model code
            attribute_code: Attribute code for the media (e.g., "new_image1")
            file_path: Path to the file to upload
            scope: Channel scope (optional)
            locale: Locale (optional)
            
        Returns:
            MediaFile instance representing the uploaded file
        """
        if not hasattr(self._client, '_make_request_sync'):
            raise TypeError("This method requires a synchronous client")
        
        product_model_code = validate_identifier(product_model_code, "product_model_code")
        
        url = "/api/rest/v1/media-files"
        
        # Prepare the product_model JSON as per Myer's documentation
        product_model_json = {
            "code": product_model_code,
            "attribute": attribute_code,
            "scope": scope,
            "locale": locale
        }
        
        # Prepare the multipart form data
        with open(file_path, 'rb') as f:
            files = {
                'file': f,
            }
            form_data = {
                'product_model': json.dumps(product_model_json)
            }
            
            response = self._client._make_request_sync("POST", url, form_data=form_data, files=files)
        
        return self._create_instance(response)
    
    def download(self, code: str) -> bytes:
        """
        Download a media file by its code.
        
        Args:
            code: Media file code
            
        Returns:
            Binary content of the file
        """
        if not hasattr(self._client, '_make_request_sync'):
            raise TypeError("This method requires a synchronous client")
        
        code = validate_identifier(code, "code")
        url = f"/api/rest/v1/media-files/{code}/download"
        
        # This will return binary content
        response = self._client._make_request_sync("GET", url)
        return response
    
    def get_file_info(self, code: str) -> "MediaFile":
        """
        Get information about a media file without downloading it.
        
        Args:
            code: Media file code
            
        Returns:
            MediaFile instance with file metadata
        """
        return self.get_by_code(code)
    
    # Asynchronous versions
    
    async def get_by_code_async(self, code: str) -> "MediaFile":
        """Get a media file by its code asynchronously."""
        code = validate_identifier(code, "code")
        return await self.get_async(code)
    
    async def upload_for_product_async(self, product_identifier: str, attribute_code: str, file_path: str,
                                     scope: Optional[str] = None, locale: Optional[str] = None) -> "MediaFile":
        """
        Upload a media file for a product asynchronously.
        
        Args:
            product_identifier: Product identifier (SKU)
            attribute_code: Attribute code for the media
            file_path: Path to the file to upload
            scope: Channel scope (optional)
            locale: Locale (optional)
            
        Returns:
            MediaFile instance representing the uploaded file
        """
        if not hasattr(self._client, '_make_request_async'):
            raise TypeError("This method requires an asynchronous client")
        
        product_identifier = validate_identifier(product_identifier, "product_identifier")
        
        url = "/api/rest/v1/media-files"
        
        # Prepare the product JSON
        product_json = {
            "identifier": product_identifier,
            "attribute": attribute_code,
            "scope": scope,
            "locale": locale
        }
        
        # Prepare the multipart form data
        with open(file_path, 'rb') as f:
            files = {
                'file': f,
            }
            form_data = {
                'product': json.dumps(product_json)
            }
            
            response = await self._client._make_request_async("POST", url, form_data=form_data, files=files)
        
        return self._create_instance(response)
    
    async def upload_for_product_model_async(self, product_model_code: str, attribute_code: str, file_path: str,
                                           scope: Optional[str] = None, locale: Optional[str] = None) -> "MediaFile":
        """
        Upload a media file for a product model asynchronously.
        
        This is the main method for Myer's enrichment process since
        image enrichment is typically done at the product model level.
        
        Args:
            product_model_code: Product model code
            attribute_code: Attribute code for the media (e.g., "new_image1")
            file_path: Path to the file to upload
            scope: Channel scope (optional)
            locale: Locale (optional)
            
        Returns:
            MediaFile instance representing the uploaded file
        """
        if not hasattr(self._client, '_make_request_async'):
            raise TypeError("This method requires an asynchronous client")
        
        product_model_code = validate_identifier(product_model_code, "product_model_code")
        
        url = "/api/rest/v1/media-files"
        
        # Prepare the product_model JSON
        product_model_json = {
            "code": product_model_code,
            "attribute": attribute_code,
            "scope": scope,
            "locale": locale
        }
        
        # Prepare the multipart form data
        with open(file_path, 'rb') as f:
            files = {
                'file': f,
            }
            form_data = {
                'product_model': json.dumps(product_model_json)
            }
            
            response = await self._client._make_request_async("POST", url, form_data=form_data, files=files)
        
        return self._create_instance(response)
    
    async def download_async(self, code: str) -> bytes:
        """
        Download a media file by its code asynchronously.
        
        Args:
            code: Media file code
            
        Returns:
            Binary content of the file
        """
        if not hasattr(self._client, '_make_request_async'):
            raise TypeError("This method requires an asynchronous client")
        
        code = validate_identifier(code, "code")
        url = f"/api/rest/v1/media-files/{code}/download"
        
        # This will return binary content
        response = await self._client._make_request_async("GET", url)
        return response
    
    async def get_file_info_async(self, code: str) -> "MediaFile":
        """
        Get information about a media file without downloading it asynchronously.
        
        Args:
            code: Media file code
            
        Returns:
            MediaFile instance with file metadata
        """
        return await self.get_by_code_async(code)
