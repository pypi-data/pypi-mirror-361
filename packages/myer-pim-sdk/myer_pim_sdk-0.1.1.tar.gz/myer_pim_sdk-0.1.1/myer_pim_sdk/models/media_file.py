# models/media_file.py

from typing import Optional
from pydantic import BaseModel, Field, ConfigDict


class MediaFileRead(BaseModel):
    """Read model for Akeneo media files."""
    code: str
    original_filename: str = Field(alias="original_filename")
    mime_type: str = Field(alias="mime_type")
    size: int
    extension: str


class MediaFileUpload(BaseModel):
    """Model for uploading media files."""
    
    model_config = ConfigDict(
        populate_by_name=True,
        from_attributes=True,
        extra="forbid"
    )
    
    product: Optional[str] = None
    product_model: Optional[str] = Field(None, alias="product_model")