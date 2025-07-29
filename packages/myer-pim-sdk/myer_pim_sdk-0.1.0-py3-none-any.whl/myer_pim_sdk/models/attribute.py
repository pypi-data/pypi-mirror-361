# models/attribute.py

from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field, ConfigDict


class TableColumn(BaseModel):
    """Represents a table attribute column configuration."""
    code: str
    data_type: str = Field(alias="data_type")
    labels: Dict[str, str] = Field(default_factory=dict)
    validations: Dict[str, Any] = Field(default_factory=dict)
    is_required_for_completeness: bool = Field(False, alias="is_required_for_completeness")


class AttributeRead(BaseModel):
    """Read model for Akeneo attributes."""
    
    code: str
    type: str
    labels: Dict[str, str] = Field(default_factory=dict)
    group: str
    group_labels: Dict[str, str] = Field(default_factory=dict, alias="group_labels")
    sort_order: int = Field(0, alias="sort_order")
    localizable: bool = False
    scopable: bool = False
    available_locales: List[str] = Field(default_factory=list, alias="available_locales")
    unique: bool = False
    useable_as_grid_filter: bool = Field(False, alias="useable_as_grid_filter")
    max_characters: Optional[int] = Field(None, alias="max_characters")
    validation_rule: Optional[str] = Field(None, alias="validation_rule")
    validation_regexp: Optional[str] = Field(None, alias="validation_regexp")
    wysiwyg_enabled: Optional[bool] = Field(None, alias="wysiwyg_enabled")
    number_min: Optional[str] = Field(None, alias="number_min")
    number_max: Optional[str] = Field(None, alias="number_max")
    decimals_allowed: Optional[bool] = Field(None, alias="decimals_allowed")
    negative_allowed: Optional[bool] = Field(None, alias="negative_allowed")
    metric_family: Optional[str] = Field(None, alias="metric_family")
    default_metric_unit: Optional[str] = Field(None, alias="default_metric_unit")
    date_min: Optional[str] = Field(None, alias="date_min")
    date_max: Optional[str] = Field(None, alias="date_max")
    allowed_extensions: List[str] = Field(default_factory=list, alias="allowed_extensions")
    max_file_size: Optional[str] = Field(None, alias="max_file_size")
    reference_data_name: Optional[str] = Field(None, alias="reference_data_name")
    default_value: Optional[bool] = Field(None, alias="default_value")
    table_configuration: List[TableColumn] = Field(default_factory=list, alias="table_configuration")
    is_main_identifier: bool = Field(False, alias="is_main_identifier")
    is_mandatory: bool = Field(False, alias="is_mandatory")
    decimal_places_strategy: Optional[str] = Field(None, alias="decimal_places_strategy")
    decimal_places: Optional[int] = Field(None, alias="decimal_places")


class AttributeWrite(BaseModel):
    """Write model for Akeneo attributes."""
    
    model_config = ConfigDict(
        populate_by_name=True,
        from_attributes=True,
        extra="forbid"
    )
    
    code: Optional[str] = None
    type: Optional[str] = None
    labels: Optional[Dict[str, str]] = None
    group: Optional[str] = None
    sort_order: Optional[int] = Field(None, alias="sort_order")
    localizable: Optional[bool] = None
    scopable: Optional[bool] = None
    available_locales: Optional[List[str]] = Field(None, alias="available_locales")
    unique: Optional[bool] = None
    useable_as_grid_filter: Optional[bool] = Field(None, alias="useable_as_grid_filter")
    max_characters: Optional[int] = Field(None, alias="max_characters")
    validation_rule: Optional[str] = Field(None, alias="validation_rule")
    validation_regexp: Optional[str] = Field(None, alias="validation_regexp")
    wysiwyg_enabled: Optional[bool] = Field(None, alias="wysiwyg_enabled")
    number_min: Optional[str] = Field(None, alias="number_min")
    number_max: Optional[str] = Field(None, alias="number_max")
    decimals_allowed: Optional[bool] = Field(None, alias="decimals_allowed")
    negative_allowed: Optional[bool] = Field(None, alias="negative_allowed")
    metric_family: Optional[str] = Field(None, alias="metric_family")
    default_metric_unit: Optional[str] = Field(None, alias="default_metric_unit")
    date_min: Optional[str] = Field(None, alias="date_min")
    date_max: Optional[str] = Field(None, alias="date_max")
    allowed_extensions: Optional[List[str]] = Field(None, alias="allowed_extensions")
    max_file_size: Optional[str] = Field(None, alias="max_file_size")
    reference_data_name: Optional[str] = Field(None, alias="reference_data_name")
    default_value: Optional[bool] = Field(None, alias="default_value")
    table_configuration: Optional[List[TableColumn]] = Field(None, alias="table_configuration")
    is_main_identifier: Optional[bool] = Field(None, alias="is_main_identifier")
    is_mandatory: Optional[bool] = Field(None, alias="is_mandatory")
    decimal_places_strategy: Optional[str] = Field(None, alias="decimal_places_strategy")
    decimal_places: Optional[int] = Field(None, alias="decimal_places")


class AttributeCreateWrite(BaseModel):
    """Create model for Akeneo attributes with required fields."""
    
    model_config = ConfigDict(
        populate_by_name=True,
        from_attributes=True,
        extra="forbid"
    )
    
    code: str
    type: str
    group: str
    labels: Dict[str, str] = Field(default_factory=dict)
    sort_order: int = Field(0, alias="sort_order")
    localizable: bool = False
    scopable: bool = False
    unique: bool = False