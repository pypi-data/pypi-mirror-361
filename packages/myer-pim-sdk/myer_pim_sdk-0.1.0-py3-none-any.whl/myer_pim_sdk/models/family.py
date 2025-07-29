# models/family.py

from typing import Dict, List, Optional
from pydantic import BaseModel, Field, ConfigDict


class FamilyRead(BaseModel):
    """Read model for Akeneo families."""
    code: str
    attribute_as_label: Optional[str] = Field(None, alias="attribute_as_label")
    attribute_as_image: Optional[str] = Field(None, alias="attribute_as_image")
    attributes: List[str] = Field(default_factory=list)
    attribute_requirements: Dict[str, List[str]] = Field(
        default_factory=dict, alias="attribute_requirements"
    )
    labels: Dict[str, str] = Field(default_factory=dict)


class FamilyWrite(BaseModel):
    """Write model for Akeneo families."""
    
    model_config = ConfigDict(
        populate_by_name=True,
        from_attributes=True,
        extra="forbid",
    )
    
    code: Optional[str] = None
    attribute_as_label: Optional[str] = Field(None, alias="attribute_as_label")
    attribute_as_image: Optional[str] = Field(None, alias="attribute_as_image")
    attributes: Optional[List[str]] = None
    attribute_requirements: Optional[Dict[str, List[str]]] = Field(
        None, alias="attribute_requirements"
    )
    labels: Optional[Dict[str, str]] = None

class FamilyCreateWrite(BaseModel):
    """Create model for Akeneo families with required fields."""
    
    model_config = ConfigDict(
        populate_by_name=True,
        from_attributes=True,
        extra="forbid"
    )
    
    code: str
    attribute_as_label: str = Field(alias="attribute_as_label")
    attributes: List[str] = Field(default_factory=list)
    attribute_requirements: Dict[str, List[str]] = Field(
        default_factory=dict, alias="attribute_requirements"
    )
    labels: Dict[str, str] = Field(default_factory=dict)
    attribute_as_image: Optional[str] = Field(None, alias="attribute_as_image")