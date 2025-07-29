# search/filters.py

from typing import Any, Dict, List, Optional, Union
from datetime import datetime
from dataclasses import dataclass, field
from .operators import (
    ComparisonOperator,
    ListOperator,
    DateOperator,
    TextOperator,
    CategoryOperator,
    CompletenessOperator,
    BooleanOperator,
    ParentOperator,
    QualityScoreOperator,
    EmptyOperator
)


@dataclass
class FilterCondition:
    """Represents a single filter condition."""
    operator: str
    value: Any = None
    locale: Optional[str] = None
    scope: Optional[str] = None
    locales: Optional[List[str]] = None


@dataclass
class BaseFilter:
    """Base class for all filters."""
    property_name: str
    conditions: List[FilterCondition] = field(default_factory=list)
    
    def add_condition(self, operator: str, value: Any = None, 
                     locale: Optional[str] = None, scope: Optional[str] = None,
                     locales: Optional[List[str]] = None) -> "BaseFilter":
        """Add a filter condition."""
        self.conditions.append(FilterCondition(
            operator=operator,
            value=value,
            locale=locale,
            scope=scope,
            locales=locales
        ))
        return self
    
    def to_dict(self) -> Dict[str, List[Dict[str, Any]]]:
        """Convert filter to dictionary format for API."""
        conditions_list = []
        for condition in self.conditions:
            condition_dict = {"operator": condition.operator}
            
            if condition.value is not None:
                condition_dict["value"] = condition.value
            if condition.locale is not None:
                condition_dict["locale"] = condition.locale
            if condition.scope is not None:
                condition_dict["scope"] = condition.scope
            if condition.locales is not None:
                condition_dict["locales"] = condition.locales
                
            conditions_list.append(condition_dict)
        
        return {self.property_name: conditions_list}


class ProductPropertyFilter(BaseFilter):
    """Filter for product properties."""
    
    @classmethod
    def uuid(cls, uuids: List[str], operator: ListOperator = ListOperator.IN) -> "ProductPropertyFilter":
        """Filter by product UUIDs."""
        filter_obj = cls("uuid")
        filter_obj.add_condition(operator.value, uuids)
        return filter_obj
    
    @classmethod
    def categories(cls, category_codes: List[str], 
                  operator: CategoryOperator = CategoryOperator.IN) -> "ProductPropertyFilter":
        """Filter by categories."""
        filter_obj = cls("categories")
        if operator == CategoryOperator.UNCLASSIFIED:
            filter_obj.add_condition(operator.value)
        else:
            filter_obj.add_condition(operator.value, category_codes)
        return filter_obj
    
    @classmethod
    def enabled(cls, is_enabled: bool, 
               operator: BooleanOperator = BooleanOperator.EQUALS) -> "ProductPropertyFilter":
        """Filter by enabled status."""
        filter_obj = cls("enabled")
        filter_obj.add_condition(operator.value, is_enabled)
        return filter_obj
    
    @classmethod
    def completeness(cls, value: int, scope: str, 
                    operator: CompletenessOperator = CompletenessOperator.EQUALS,
                    locales: Optional[List[str]] = None) -> "ProductPropertyFilter":
        """Filter by completeness."""
        filter_obj = cls("completeness")
        filter_obj.add_condition(operator.value, value, scope=scope, locales=locales)
        return filter_obj
    
    @classmethod
    def family(cls, family_codes: List[str], 
              operator: ListOperator = ListOperator.IN) -> "ProductPropertyFilter":
        """Filter by family."""
        filter_obj = cls("family")
        if operator in [ListOperator.IN, ListOperator.NOT_IN]:
            filter_obj.add_condition(operator.value, family_codes)
        else:
            filter_obj.add_condition(operator.value)
        return filter_obj
    
    @classmethod
    def groups(cls, group_codes: List[str], 
              operator: ListOperator = ListOperator.IN) -> "ProductPropertyFilter":
        """Filter by groups."""
        filter_obj = cls("groups")
        if operator in [ListOperator.IN, ListOperator.NOT_IN]:
            filter_obj.add_condition(operator.value, group_codes)
        else:
            filter_obj.add_condition(operator.value)
        return filter_obj
    
    @classmethod
    def created(cls, date_value: Union[str, datetime, List[Union[str, datetime]]], 
               operator: DateOperator = DateOperator.EQUALS) -> "ProductPropertyFilter":
        """Filter by creation date."""
        filter_obj = cls("created")
        
        # Handle datetime objects
        if isinstance(date_value, datetime):
            date_value = date_value.strftime("%Y-%m-%d %H:%M:%S")
        elif isinstance(date_value, list):
            date_value = [
                d.strftime("%Y-%m-%d %H:%M:%S") if isinstance(d, datetime) else d
                for d in date_value
            ]
        
        if operator == DateOperator.SINCE_LAST_N_DAYS:
            filter_obj.add_condition(operator.value, int(date_value))
        else:
            filter_obj.add_condition(operator.value, date_value)
        return filter_obj
    
    @classmethod
    def updated(cls, date_value: Union[str, datetime, List[Union[str, datetime]]], 
               operator: DateOperator = DateOperator.EQUALS) -> "ProductPropertyFilter":
        """Filter by update date."""
        filter_obj = cls("updated")
        
        # Handle datetime objects
        if isinstance(date_value, datetime):
            date_value = date_value.strftime("%Y-%m-%d %H:%M:%S")
        elif isinstance(date_value, list):
            date_value = [
                d.strftime("%Y-%m-%d %H:%M:%S") if isinstance(d, datetime) else d
                for d in date_value
            ]
        
        if operator == DateOperator.SINCE_LAST_N_DAYS:
            filter_obj.add_condition(operator.value, int(date_value))
        else:
            filter_obj.add_condition(operator.value, date_value)
        return filter_obj
    
    @classmethod
    def parent(cls, parent_codes: Union[str, List[str]], 
              operator: ParentOperator = ParentOperator.EQUALS) -> "ProductPropertyFilter":
        """Filter by parent product model."""
        filter_obj = cls("parent")
        
        if operator == ParentOperator.EQUALS and isinstance(parent_codes, str):
            filter_obj.add_condition(operator.value, parent_codes)
        elif operator == ParentOperator.IN and isinstance(parent_codes, list):
            filter_obj.add_condition(operator.value, parent_codes)
        elif operator in [ParentOperator.EMPTY, ParentOperator.NOT_EMPTY]:
            filter_obj.add_condition(operator.value)
        else:
            raise ValueError(f"Invalid operator {operator} for parent filter")
        
        return filter_obj
    
    @classmethod
    def quality_score(cls, scores: List[str], scope: str, locale: str,
                     operator: QualityScoreOperator = QualityScoreOperator.IN) -> "ProductPropertyFilter":
        """Filter by quality score."""
        filter_obj = cls("quality_score")
        filter_obj.add_condition(operator.value, scores, scope=scope, locale=locale)
        return filter_obj


class ProductModelPropertyFilter(BaseFilter):
    """Filter for product model properties."""
    
    @classmethod
    def identifier(cls, identifiers: List[str], 
                  operator: ListOperator = ListOperator.IN) -> "ProductModelPropertyFilter":
        """Filter by product model identifiers."""
        filter_obj = cls("identifier")
        filter_obj.add_condition(operator.value, identifiers)
        return filter_obj
    
    @classmethod
    def categories(cls, category_codes: List[str], 
                  operator: CategoryOperator = CategoryOperator.IN) -> "ProductModelPropertyFilter":
        """Filter by categories."""
        filter_obj = cls("categories")
        if operator == CategoryOperator.UNCLASSIFIED:
            filter_obj.add_condition(operator.value)
        else:
            filter_obj.add_condition(operator.value, category_codes)
        return filter_obj
    
    @classmethod
    def completeness(cls, scope: str, operator: CompletenessOperator,
                    locale: Optional[str] = None, 
                    locales: Optional[List[str]] = None) -> "ProductModelPropertyFilter":
        """Filter by completeness."""
        filter_obj = cls("completeness")
        filter_obj.add_condition(operator.value, scope=scope, locale=locale, locales=locales)
        return filter_obj
    
    @classmethod
    def family(cls, family_codes: List[str], 
              operator: ListOperator = ListOperator.IN) -> "ProductModelPropertyFilter":
        """Filter by family."""
        filter_obj = cls("family")
        if operator in [ListOperator.IN, ListOperator.NOT_IN]:
            filter_obj.add_condition(operator.value, family_codes)
        else:
            filter_obj.add_condition(operator.value)
        return filter_obj
    
    @classmethod
    def created(cls, date_value: Union[str, datetime, List[Union[str, datetime]]], 
               operator: DateOperator = DateOperator.EQUALS) -> "ProductModelPropertyFilter":
        """Filter by creation date."""
        filter_obj = cls("created")
        
        # Handle datetime objects
        if isinstance(date_value, datetime):
            date_value = date_value.strftime("%Y-%m-%d %H:%M:%S")
        elif isinstance(date_value, list):
            date_value = [
                d.strftime("%Y-%m-%d %H:%M:%S") if isinstance(d, datetime) else d
                for d in date_value
            ]
        
        if operator == DateOperator.SINCE_LAST_N_DAYS:
            filter_obj.add_condition(operator.value, int(date_value))
        else:
            filter_obj.add_condition(operator.value, date_value)
        return filter_obj
    
    @classmethod
    def updated(cls, date_value: Union[str, datetime, List[Union[str, datetime]]], 
               operator: DateOperator = DateOperator.EQUALS) -> "ProductModelPropertyFilter":
        """Filter by update date."""
        filter_obj = cls("updated")
        
        # Handle datetime objects
        if isinstance(date_value, datetime):
            date_value = date_value.strftime("%Y-%m-%d %H:%M:%S")
        elif isinstance(date_value, list):
            date_value = [
                d.strftime("%Y-%m-%d %H:%M:%S") if isinstance(d, datetime) else d
                for d in date_value
            ]
        
        if operator == DateOperator.SINCE_LAST_N_DAYS:
            filter_obj.add_condition(operator.value, int(date_value))
        else:
            filter_obj.add_condition(operator.value, date_value)
        return filter_obj
    
    @classmethod
    def parent(cls, parent_codes: Union[str, List[str]], 
              operator: ParentOperator = ParentOperator.IN) -> "ProductModelPropertyFilter":
        """Filter by parent product model."""
        filter_obj = cls("parent")
        
        if operator == ParentOperator.IN and isinstance(parent_codes, list):
            filter_obj.add_condition(operator.value, parent_codes)
        elif operator in [ParentOperator.EMPTY, ParentOperator.NOT_EMPTY]:
            filter_obj.add_condition(operator.value)
        else:
            raise ValueError(f"Invalid operator {operator} for parent filter")
        
        return filter_obj


class AttributeFilter(BaseFilter):
    """Filter for product/product model attribute values."""
    
    def __init__(self, attribute_code: str):
        super().__init__(attribute_code)
    
    @classmethod
    def text(cls, attribute_code: str, value: Union[str, List[str]], 
            operator: TextOperator = TextOperator.EQUALS,
            locale: Optional[str] = None, scope: Optional[str] = None) -> "AttributeFilter":
        """Filter by text attribute."""
        filter_obj = cls(attribute_code)
        filter_obj.add_condition(operator.value, value, locale=locale, scope=scope)
        return filter_obj
    
    @classmethod
    def number(cls, attribute_code: str, value: Union[int, float],
              operator: ComparisonOperator = ComparisonOperator.EQUALS,
              locale: Optional[str] = None, scope: Optional[str] = None) -> "AttributeFilter":
        """Filter by numeric attribute."""
        filter_obj = cls(attribute_code)
        filter_obj.add_condition(operator.value, value, locale=locale, scope=scope)
        return filter_obj
    
    @classmethod
    def select(cls, attribute_code: str, option_codes: List[str],
              operator: ListOperator = ListOperator.IN,
              locale: Optional[str] = None, scope: Optional[str] = None) -> "AttributeFilter":
        """Filter by select attribute (simple or multi)."""
        filter_obj = cls(attribute_code)
        filter_obj.add_condition(operator.value, option_codes, locale=locale, scope=scope)
        return filter_obj
    
    @classmethod
    def boolean(cls, attribute_code: str, value: bool,
               operator: BooleanOperator = BooleanOperator.EQUALS,
               locale: Optional[str] = None, scope: Optional[str] = None) -> "AttributeFilter":
        """Filter by boolean attribute."""
        filter_obj = cls(attribute_code)
        filter_obj.add_condition(operator.value, value, locale=locale, scope=scope)
        return filter_obj
    
    @classmethod
    def date(cls, attribute_code: str, value: Union[str, datetime, List[Union[str, datetime]]],
            operator: DateOperator = DateOperator.EQUALS,
            locale: Optional[str] = None, scope: Optional[str] = None) -> "AttributeFilter":
        """Filter by date attribute."""
        filter_obj = cls(attribute_code)
        
        # Handle datetime objects
        if isinstance(value, datetime):
            value = value.strftime("%Y-%m-%d")
        elif isinstance(value, list):
            value = [
                v.strftime("%Y-%m-%d") if isinstance(v, datetime) else v
                for v in value
            ]
        
        filter_obj.add_condition(operator.value, value, locale=locale, scope=scope)
        return filter_obj
    
    @classmethod
    def empty(cls, attribute_code: str, is_empty: bool = True,
             locale: Optional[str] = None, scope: Optional[str] = None) -> "AttributeFilter":
        """Filter by empty/not empty attribute."""
        filter_obj = cls(attribute_code)
        operator = EmptyOperator.EMPTY if is_empty else EmptyOperator.NOT_EMPTY
        filter_obj.add_condition(operator.value, locale=locale, scope=scope)
        return filter_obj
    
    @classmethod
    def file(cls, attribute_code: str, filename: str,
            operator: TextOperator = TextOperator.EQUALS,
            locale: Optional[str] = None, scope: Optional[str] = None) -> "AttributeFilter":
        """Filter by file/image attribute."""
        filter_obj = cls(attribute_code)
        filter_obj.add_condition(operator.value, filename, locale=locale, scope=scope)
        return filter_obj
    
    @classmethod
    def product_link(cls, attribute_code: str, product_links: List[Dict[str, str]],
                    operator: ListOperator = ListOperator.IN,
                    locale: Optional[str] = None, scope: Optional[str] = None) -> "AttributeFilter":
        """Filter by product link attribute."""
        filter_obj = cls(attribute_code)
        filter_obj.add_condition(operator.value, product_links, locale=locale, scope=scope)
        return filter_obj
