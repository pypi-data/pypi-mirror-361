# models/product.py

from typing import Dict, List, Optional, Any, Union
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict


class ProductValue(BaseModel):
    """Represents a product attribute value in Akeneo."""
    data: Any
    locale: Optional[str] = None
    scope: Optional[str] = None
    attribute_type: Optional[str] = Field(None, alias="attribute_type")


class ProductAssociation(BaseModel):
    """Represents product associations."""
    groups: List[str] = Field(default_factory=list)
    products: List[str] = Field(default_factory=list)
    product_models: List[str] = Field(default_factory=list, alias="product_models")


class QuantifiedAssociationItem(BaseModel):
    """Represents a quantified association item."""
    identifier: Optional[str] = None
    uuid: Optional[str] = None
    quantity: int


class QuantifiedAssociation(BaseModel):
    """Represents quantified associations."""
    products: List[QuantifiedAssociationItem] = Field(default_factory=list)
    product_models: List[QuantifiedAssociationItem] = Field(default_factory=list, alias="product_models")


class ProductMetadata(BaseModel):
    """Represents product metadata."""
    workflow_status: Optional[str] = Field(None, alias="workflow_status")


class QualityScore(BaseModel):
    """Represents a quality score for a specific scope/locale."""
    scope: str
    locale: str
    data: str


class Completeness(BaseModel):
    """Represents completeness for a specific scope/locale."""
    scope: str
    locale: str
    data: int


class ProductRead(BaseModel):
    """Read model for Akeneo products."""
    uuid: Optional[str] = None
    identifier: Optional[str] = None
    enabled: bool = True
    family: Optional[str] = None
    categories: List[str] = Field(default_factory=list)
    groups: List[str] = Field(default_factory=list)
    parent: Optional[str] = None
    values: Dict[str, List[ProductValue]] = Field(default_factory=dict)
    associations: Dict[str, ProductAssociation] = Field(default_factory=dict)
    quantified_associations: Dict[str, QuantifiedAssociation] = Field(
        default_factory=dict, alias="quantified_associations"
    )
    created: Optional[datetime] = None
    updated: Optional[datetime] = None
    metadata: Optional[ProductMetadata] = None
    quality_scores: List[QualityScore] = Field(default_factory=list, alias="quality_scores")
    completenesses: List[Completeness] = Field(default_factory=list)


class ProductWrite(BaseModel):
    """Write model for Akeneo products."""
    
    model_config = ConfigDict(
        populate_by_name=True,
        from_attributes=True,
        extra="forbid"
    )
    
    uuid: Optional[str] = None
    identifier: Optional[str] = None
    enabled: Optional[bool] = None
    family: Optional[str] = None
    categories: Optional[List[str]] = None
    groups: Optional[List[str]] = None
    parent: Optional[str] = None
    values: Optional[Dict[str, List[ProductValue]]] = None
    associations: Optional[Dict[str, ProductAssociation]] = None
    quantified_associations: Optional[Dict[str, QuantifiedAssociation]] = Field(
        None, alias="quantified_associations"
    )

class ProductCreateWrite(BaseModel):
    """Create model for Akeneo products with required fields."""
    
    model_config = ConfigDict(
        populate_by_name=True,
        from_attributes=True,
        extra="forbid"
    )
    
    identifier: str
    enabled: bool = True
    family: Optional[str] = None
    categories: List[str] = Field(default_factory=list)
    groups: List[str] = Field(default_factory=list)
    parent: Optional[str] = None
    values: Dict[str, List[ProductValue]] = Field(default_factory=dict)
    associations: Dict[str, ProductAssociation] = Field(default_factory=dict)
    quantified_associations: Dict[str, QuantifiedAssociation] = Field(
        default_factory=dict, alias="quantified_associations"
    )