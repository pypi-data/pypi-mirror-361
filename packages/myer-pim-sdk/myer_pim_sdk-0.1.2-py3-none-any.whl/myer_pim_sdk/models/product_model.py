# models/product_model.py

from typing import Dict, List, Optional, Any
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict

from .product import ProductValue, ProductAssociation, QuantifiedAssociation, ProductMetadata, QualityScore


class ProductModelRead(BaseModel):
    """Read model for Akeneo product models."""
    code: str
    family: Optional[str] = None
    family_variant: Optional[str] = Field(None, alias="family_variant")
    parent: Optional[str] = None
    categories: List[str] = Field(default_factory=list)
    values: Dict[str, List[ProductValue]] = Field(default_factory=dict)
    associations: Dict[str, ProductAssociation] = Field(default_factory=dict)
    quantified_associations: Dict[str, QuantifiedAssociation] = Field(
        default_factory=dict, alias="quantified_associations"
    )
    created: Optional[datetime] = None
    updated: Optional[datetime] = None
    metadata: Optional[ProductMetadata] = None
    quality_scores: List[QualityScore] = Field(default_factory=list, alias="quality_scores")


class ProductModelWrite(BaseModel):
    """Write model for Akeneo product models."""
    
    model_config = ConfigDict(
        populate_by_name=True,
        from_attributes=True,
        extra="forbid"
    )
    
    code: Optional[str] = None
    family: Optional[str] = None
    family_variant: Optional[str] = Field(None, alias="family_variant")
    parent: Optional[str] = None
    categories: Optional[List[str]] = None
    values: Optional[Dict[str, List[ProductValue]]] = None
    associations: Optional[Dict[str, ProductAssociation]] = None
    quantified_associations: Optional[Dict[str, QuantifiedAssociation]] = Field(
        None, alias="quantified_associations"
    )

class ProductModelCreateWrite(BaseModel):
    """Create model for Akeneo product models with required fields."""
    
    model_config = ConfigDict(
        populate_by_name=True,
        from_attributes=True,
        extra="forbid"
    )
    
    code: str
    family_variant: str = Field(alias="family_variant")
    parent: Optional[str] = None
    categories: List[str] = Field(default_factory=list)
    values: Dict[str, List[ProductValue]] = Field(default_factory=dict)
    associations: Dict[str, ProductAssociation] = Field(default_factory=dict)
    quantified_associations: Dict[str, QuantifiedAssociation] = Field(
        default_factory=dict, alias="quantified_associations"
    )
