# models/category.py

from typing import Dict, List, Optional, Any
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict


class CategoryValue(BaseModel):
    """Represents a category attribute value."""
    data: Any
    locale: Optional[str] = None
    channel: Optional[str] = None
    attribute_code: str = Field(alias="attribute_code")


class CategoryRead(BaseModel):
    """Read model for Akeneo categories."""
    code: str
    parent: Optional[str] = None
    updated: Optional[datetime] = None
    position: Optional[int] = None
    labels: Dict[str, str] = Field(default_factory=dict)
    values: Dict[str, CategoryValue] = Field(default_factory=dict)
    channel_requirements: List[str] = Field(default_factory=list, alias="channel_requirements")


class CategoryWrite(BaseModel):
    """Write model for Akeneo categories."""
    
    model_config = ConfigDict(
        populate_by_name=True,
        from_attributes=True,
        extra="forbid"
    )
    
    code: Optional[str] = None
    parent: Optional[str] = None
    labels: Optional[Dict[str, str]] = None
    values: Optional[Dict[str, CategoryValue]] = None
    channel_requirements: Optional[List[str]] = Field(None, alias="channel_requirements")


class CategoryCreateWrite(BaseModel):
    """Create model for Akeneo categories with required fields."""
    
    model_config = ConfigDict(
        populate_by_name=True,
        from_attributes=True,
        extra="forbid"
    )
    
    code: str
    parent: Optional[str] = None
    labels: Dict[str, str] = Field(default_factory=dict)
    values: Dict[str, CategoryValue] = Field(default_factory=dict)
    channel_requirements: List[str] = Field(default_factory=list, alias="channel_requirements")