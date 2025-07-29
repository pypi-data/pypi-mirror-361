# search/builder.py

import json
from typing import Any, Dict, List, Optional, Union
from .filters import BaseFilter, ProductPropertyFilter, ProductModelPropertyFilter, AttributeFilter


class FilterBuilder:
    """Helper class for building filters with a fluent interface."""
    
    def __init__(self):
        self._filters: List[BaseFilter] = []
    
    # Product property filters
    def uuid(self, uuids: List[str], operator: str = "IN") -> "FilterBuilder":
        """Filter by product UUIDs."""
        from .operators import ListOperator
        self._filters.append(ProductPropertyFilter.uuid(uuids, ListOperator(operator)))
        return self
    
    def categories(self, category_codes: List[str], operator: str = "IN") -> "FilterBuilder":
        """Filter by categories."""
        from .operators import CategoryOperator
        self._filters.append(ProductPropertyFilter.categories(category_codes, CategoryOperator(operator)))
        return self
    
    def enabled(self, is_enabled: bool, operator: str = "=") -> "FilterBuilder":
        """Filter by enabled status."""
        from .operators import BooleanOperator
        self._filters.append(ProductPropertyFilter.enabled(is_enabled, BooleanOperator(operator)))
        return self
    
    def completeness(self, value: int, scope: str, operator: str = "=", 
                    locales: Optional[List[str]] = None) -> "FilterBuilder":
        """Filter by completeness."""
        from .operators import CompletenessOperator
        self._filters.append(ProductPropertyFilter.completeness(
            value, scope, CompletenessOperator(operator), locales
        ))
        return self
    
    def family(self, family_codes: List[str], operator: str = "IN") -> "FilterBuilder":
        """Filter by family."""
        from .operators import ListOperator
        self._filters.append(ProductPropertyFilter.family(family_codes, ListOperator(operator)))
        return self
    
    def groups(self, group_codes: List[str], operator: str = "IN") -> "FilterBuilder":
        """Filter by groups."""
        from .operators import ListOperator
        self._filters.append(ProductPropertyFilter.groups(group_codes, ListOperator(operator)))
        return self
    
    def created(self, date_value: Union[str, List[str]], operator: str = "=") -> "FilterBuilder":
        """Filter by creation date."""
        from .operators import DateOperator
        self._filters.append(ProductPropertyFilter.created(date_value, DateOperator(operator)))
        return self
    
    def updated(self, date_value: Union[str, List[str]], operator: str = "=") -> "FilterBuilder":
        """Filter by update date."""
        from .operators import DateOperator
        self._filters.append(ProductPropertyFilter.updated(date_value, DateOperator(operator)))
        return self
    
    def parent(self, parent_codes: Union[str, List[str]], operator: str = "=") -> "FilterBuilder":
        """Filter by parent product model."""
        from .operators import ParentOperator
        self._filters.append(ProductPropertyFilter.parent(parent_codes, ParentOperator(operator)))
        return self
    
    def quality_score(self, scores: List[str], scope: str, locale: str, 
                     operator: str = "IN") -> "FilterBuilder":
        """Filter by quality score."""
        from .operators import QualityScoreOperator
        self._filters.append(ProductPropertyFilter.quality_score(
            scores, scope, locale, QualityScoreOperator(operator)
        ))
        return self
    
    # Product model specific filters
    def identifier(self, identifiers: List[str], operator: str = "IN") -> "FilterBuilder":
        """Filter by product model identifiers."""
        from .operators import ListOperator
        self._filters.append(ProductModelPropertyFilter.identifier(identifiers, ListOperator(operator)))
        return self
    
    def model_completeness(self, scope: str, operator: str, locale: Optional[str] = None,
                          locales: Optional[List[str]] = None) -> "FilterBuilder":
        """Filter by product model completeness."""
        from .operators import CompletenessOperator
        self._filters.append(ProductModelPropertyFilter.completeness(
            scope, CompletenessOperator(operator), locale, locales
        ))
        return self
    
    # Attribute filters
    def attribute_text(self, attribute_code: str, value: Union[str, List[str]], 
                      operator: str = "=", locale: Optional[str] = None, 
                      scope: Optional[str] = None) -> "FilterBuilder":
        """Filter by text attribute."""
        from .operators import TextOperator
        self._filters.append(AttributeFilter.text(
            attribute_code, value, TextOperator(operator), locale, scope
        ))
        return self
    
    def attribute_number(self, attribute_code: str, value: Union[int, float],
                        operator: str = "=", locale: Optional[str] = None,
                        scope: Optional[str] = None) -> "FilterBuilder":
        """Filter by numeric attribute."""
        from .operators import ComparisonOperator
        self._filters.append(AttributeFilter.number(
            attribute_code, value, ComparisonOperator(operator), locale, scope
        ))
        return self
    
    def attribute_select(self, attribute_code: str, option_codes: List[str],
                        operator: str = "IN", locale: Optional[str] = None,
                        scope: Optional[str] = None) -> "FilterBuilder":
        """Filter by select attribute."""
        from .operators import ListOperator
        self._filters.append(AttributeFilter.select(
            attribute_code, option_codes, ListOperator(operator), locale, scope
        ))
        return self
    
    def attribute_boolean(self, attribute_code: str, value: bool,
                         operator: str = "=", locale: Optional[str] = None,
                         scope: Optional[str] = None) -> "FilterBuilder":
        """Filter by boolean attribute."""
        from .operators import BooleanOperator
        self._filters.append(AttributeFilter.boolean(
            attribute_code, value, BooleanOperator(operator), locale, scope
        ))
        return self
    
    def attribute_date(self, attribute_code: str, value: Union[str, List[str]],
                      operator: str = "=", locale: Optional[str] = None,
                      scope: Optional[str] = None) -> "FilterBuilder":
        """Filter by date attribute."""
        from .operators import DateOperator
        self._filters.append(AttributeFilter.date(
            attribute_code, value, DateOperator(operator), locale, scope
        ))
        return self
    
    def attribute_empty(self, attribute_code: str, is_empty: bool = True,
                       locale: Optional[str] = None, scope: Optional[str] = None) -> "FilterBuilder":
        """Filter by empty/not empty attribute."""
        self._filters.append(AttributeFilter.empty(attribute_code, is_empty, locale, scope))
        return self
    
    def attribute_file(self, attribute_code: str, filename: str,
                      operator: str = "=", locale: Optional[str] = None,
                      scope: Optional[str] = None) -> "FilterBuilder":
        """Filter by file/image attribute."""
        from .operators import TextOperator
        self._filters.append(AttributeFilter.file(
            attribute_code, filename, TextOperator(operator), locale, scope
        ))
        return self
    
    # Generic attribute method - the "magic" method
    def by_attribute(self, attribute_code: str, value: Any, operator: str = "=",
                    locale: Optional[str] = None, scope: Optional[str] = None) -> "FilterBuilder":
        """Generic method to filter by any attribute with automatic type detection."""
        if isinstance(value, bool):
            return self.attribute_boolean(attribute_code, value, operator, locale, scope)
        elif isinstance(value, (int, float)):
            return self.attribute_number(attribute_code, value, operator, locale, scope)
        elif isinstance(value, list):
            return self.attribute_select(attribute_code, value, operator, locale, scope)
        else:
            return self.attribute_text(attribute_code, str(value), operator, locale, scope)
    
    # Myer-specific convenience methods for common product values
    def supplier_style(self, value: Union[str, List[str]], operator: str = "=", 
                      locale: str = "en_AU", scope: str = "ecommerce") -> "FilterBuilder":
        """Filter by supplier style (common Myer attribute)."""
        if isinstance(value, list):
            return self.attribute_select("supplier_style", value, "IN", locale, scope)
        return self.attribute_text("supplier_style", value, operator, locale, scope)
    
    def brand(self, value: Union[str, List[str]], operator: str = "=",
             locale: str = "en_AU", scope: str = "ecommerce") -> "FilterBuilder":
        """Filter by brand."""
        if isinstance(value, list):
            return self.attribute_select("brand", value, "IN", locale, scope)
        return self.attribute_text("brand", value, operator, locale, scope)
    
    def online_name(self, value: str, operator: str = "CONTAINS",
                   locale: str = "en_AU", scope: str = "ecommerce") -> "FilterBuilder":
        """Filter by online name."""
        return self.attribute_text("online_name", value, operator, locale, scope)
    
    def copy_status(self, value: Union[int, str], operator: str = "=") -> "FilterBuilder":
        """Filter by copy enrichment status."""
        return self.attribute_text("copy_status", str(value), operator)
    
    def image_status(self, value: Union[int, str], operator: str = "=") -> "FilterBuilder":
        """Filter by image enrichment status."""
        return self.attribute_text("image_status", str(value), operator)
    
    def myer_copy_status(self, value: Union[int, str], operator: str = "=") -> "FilterBuilder":
        """Filter by Myer copy status."""
        return self.attribute_text("myer_copy_status", str(value), operator)
    
    def myer_image_status(self, value: Union[int, str], operator: str = "=") -> "FilterBuilder":
        """Filter by Myer image status."""
        return self.attribute_text("myer_image_status", str(value), operator)
    
    def supplier_trust_level(self, value: Union[str, List[str]], operator: str = "IN") -> "FilterBuilder":
        """Filter by supplier trust level (gold, silver, bronze)."""
        if isinstance(value, str):
            value = [value]
        return self.attribute_select("supplier_trust_level", value, operator)
    
    def product_type(self, value: Union[str, List[str]], operator: str = "=") -> "FilterBuilder":
        """Filter by product type."""
        if isinstance(value, list):
            return self.attribute_select("product_type", value, "IN")
        return self.attribute_text("product_type", value, operator)
    
    def supplier_colour(self, value: Union[str, List[str]], operator: str = "=") -> "FilterBuilder":
        """Filter by supplier colour."""
        if isinstance(value, list):
            return self.attribute_select("supplier_colour", value, "IN")
        return self.attribute_text("supplier_colour", value, operator)
    
    def online_category(self, value: Union[str, List[str]], operator: str = "=") -> "FilterBuilder":
        """Filter by online category."""
        if isinstance(value, list):
            return self.attribute_select("online_category", value, "IN")
        return self.attribute_text("online_category", value, operator)
    
    def online_department(self, value: Union[str, List[str]], operator: str = "=") -> "FilterBuilder":
        """Filter by online department."""
        if isinstance(value, list):
            return self.attribute_select("online_department", value, "IN")
        return self.attribute_text("online_department", value, operator)
    
    def supplier(self, value: Union[str, List[str]], operator: str = "=") -> "FilterBuilder":
        """Filter by supplier code."""
        if isinstance(value, list):
            return self.attribute_select("supplier", value, "IN")
        return self.attribute_text("supplier", value, operator)
    
    def concession(self, value: bool = True) -> "FilterBuilder":
        """Filter by concession status."""
        return self.attribute_boolean("concession", value)
    
    def online_ind(self, value: bool = True) -> "FilterBuilder":
        """Filter by online indicator."""
        return self.attribute_boolean("online_ind", value)
    
    def buyable_ind(self, value: bool = True) -> "FilterBuilder":
        """Filter by buyable indicator."""
        return self.attribute_boolean("buyable_ind", value)
    
    def clearance_ind(self, value: bool = False, operator: str = "=") -> "FilterBuilder":
        """Filter by clearance indicator."""
        return self.attribute_boolean("clearance_ind", value, operator)
    
    def has_images(self, image_num: int = 1) -> "FilterBuilder":
        """Filter products that have specific image numbers."""
        return self.attribute_empty(f"new_image{image_num}", False)
    
    def missing_images(self, image_num: int = 1) -> "FilterBuilder":
        """Filter products missing specific image numbers."""
        return self.attribute_empty(f"new_image{image_num}", True)
    
    def has_description(self, locale: str = "en_AU", scope: str = "ecommerce") -> "FilterBuilder":
        """Filter products that have descriptions."""
        return self.attribute_empty("online_long_desc", False, locale, scope)
    
    def missing_description(self, locale: str = "en_AU", scope: str = "ecommerce") -> "FilterBuilder":
        """Filter products missing descriptions."""
        return self.attribute_empty("online_long_desc", True, locale, scope)
    
    def build(self) -> Dict[str, Any]:
        """Build the final search criteria dictionary."""
        search_dict = {}
        
        for filter_obj in self._filters:
            filter_dict = filter_obj.to_dict()
            
            # Merge filters for the same property
            for property_name, conditions in filter_dict.items():
                if property_name in search_dict:
                    search_dict[property_name].extend(conditions)
                else:
                    search_dict[property_name] = conditions
        
        return search_dict


class SearchBuilder:
    """Main search builder for constructing Akeneo API search queries."""
    
    def __init__(self):
        self._search_criteria: Dict[str, Any] = {}
        self._search_locale: Optional[str] = None
        self._search_scope: Optional[str] = None
        self._pagination_params: Dict[str, Any] = {}
        self._value_filters: Dict[str, Any] = {}  # For attributes, locales, scope filtering
    
    def filters(self, builder_func) -> "SearchBuilder":
        """Add filters using a builder function."""
        filter_builder = FilterBuilder()
        builder_func(filter_builder)
        self._search_criteria.update(filter_builder.build())
        return self
    
    def add_filter(self, filter_obj: BaseFilter) -> "SearchBuilder":
        """Add a single filter object."""
        filter_dict = filter_obj.to_dict()
        
        for property_name, conditions in filter_dict.items():
            if property_name in self._search_criteria:
                self._search_criteria[property_name].extend(conditions)
            else:
                self._search_criteria[property_name] = conditions
        
        return self
    
    def raw_filter(self, property_name: str, operator: str, value: Any = None,
                   locale: Optional[str] = None, scope: Optional[str] = None,
                   locales: Optional[List[str]] = None) -> "SearchBuilder":
        """Add a raw filter condition."""
        condition = {"operator": operator}
        
        if value is not None:
            condition["value"] = value
        if locale is not None:
            condition["locale"] = locale
        if scope is not None:
            condition["scope"] = scope
        if locales is not None:
            condition["locales"] = locales
        
        if property_name in self._search_criteria:
            self._search_criteria[property_name].append(condition)
        else:
            self._search_criteria[property_name] = [condition]
        
        return self
    
    # Enhanced value filtering methods
    def attributes(self, attribute_codes: List[str]) -> "SearchBuilder":
        """Filter to only return specific attributes in the response."""
        self._value_filters["attributes"] = ",".join(attribute_codes)
        return self
    
    def locales(self, locale_codes: List[str]) -> "SearchBuilder":
        """Filter to only return values for specific locales."""
        self._value_filters["locales"] = ",".join(locale_codes)
        return self
    
    def scope(self, scope_code: str) -> "SearchBuilder":
        """Filter to only return values for a specific scope/channel."""
        self._value_filters["scope"] = scope_code
        return self
    
    def search_locale(self, locale: str) -> "SearchBuilder":
        """Set the default locale for all localizable filters."""
        self._search_locale = locale
        return self
    
    def search_scope(self, scope: str) -> "SearchBuilder":
        """Set the default scope for all scopable filters."""
        self._search_scope = scope
        return self
    
    def page(self, page: int) -> "SearchBuilder":
        """Set the page number."""
        self._pagination_params["page"] = page
        return self
    
    def limit(self, limit: int) -> "SearchBuilder":
        """Set the page size limit."""
        self._pagination_params["limit"] = limit
        return self
    
    def with_count(self, with_count: bool = True) -> "SearchBuilder":
        """Include count in response."""
        self._pagination_params["with_count"] = with_count
        return self
    
    def pagination(self, page: Optional[int] = None, limit: Optional[int] = None,
                  with_count: Optional[bool] = None) -> "SearchBuilder":
        """Set pagination parameters."""
        if page is not None:
            self._pagination_params["page"] = page
        if limit is not None:
            self._pagination_params["limit"] = limit
        if with_count is not None:
            self._pagination_params["with_count"] = with_count
        return self
    
    def build_search_params(self) -> Dict[str, Any]:
        """Build the complete search parameters for API request."""
        params = {}
        
        # Add search criteria if any
        if self._search_criteria:
            params["search"] = json.dumps(self._search_criteria)
        
        # Add search locale and scope
        if self._search_locale:
            params["search_locale"] = self._search_locale
        if self._search_scope:
            params["search_scope"] = self._search_scope
        
        # Add value filters
        params.update(self._value_filters)
        
        # Add pagination parameters
        params.update(self._pagination_params)
        
        return params
    
    def build_search_criteria(self) -> Dict[str, Any]:
        """Build just the search criteria (for POST search endpoints)."""
        return self._search_criteria.copy()
    
    def clear(self) -> "SearchBuilder":
        """Clear all search criteria and parameters."""
        self._search_criteria.clear()
        self._search_locale = None
        self._search_scope = None
        self._pagination_params.clear()
        self._value_filters.clear()
        return self
    
    # Convenience methods for common search patterns
    
    @classmethod
    def products(cls) -> "SearchBuilder":
        """Create a search builder for products."""
        return cls()
    
    @classmethod
    def product_models(cls) -> "SearchBuilder":
        """Create a search builder for product models."""
        return cls()
    
    @classmethod
    def enabled_products(cls) -> "SearchBuilder":
        """Create a search builder for enabled products only."""
        builder = cls()
        builder.raw_filter("enabled", "=", True)
        return builder
    
    @classmethod
    def products_in_categories(cls, category_codes: List[str]) -> "SearchBuilder":
        """Create a search builder for products in specific categories."""
        builder = cls()
        builder.raw_filter("categories", "IN", category_codes)
        return builder
    
    @classmethod
    def products_with_family(cls, family_codes: List[str]) -> "SearchBuilder":
        """Create a search builder for products with specific families."""
        builder = cls()
        builder.raw_filter("family", "IN", family_codes)
        return builder
    
    @classmethod
    def recently_updated(cls, days: int) -> "SearchBuilder":
        """Create a search builder for recently updated products."""
        builder = cls()
        builder.raw_filter("updated", "SINCE LAST N DAYS", days)
        return builder
    
    @classmethod
    def incomplete_products(cls, scope: str, threshold: int = 100) -> "SearchBuilder":
        """Create a search builder for incomplete products."""
        builder = cls()
        builder.raw_filter("completeness", "<", threshold, scope=scope)
        return builder


# Convenience functions for quick searches

def search_products() -> SearchBuilder:
    """Create a product search builder."""
    return SearchBuilder.products()


def search_product_models() -> SearchBuilder:
    """Create a product model search builder.""" 
    return SearchBuilder.product_models()


def simple_search(property_name: str, operator: str, value: Any = None,
                 locale: Optional[str] = None, scope: Optional[str] = None) -> SearchBuilder:
    """Create a simple search with one filter."""
    builder = SearchBuilder()
    builder.raw_filter(property_name, operator, value, locale, scope)
    return builder


# Myer-specific magic search functions

def by_supplier_style(style: str) -> SearchBuilder:
    """Quick search by supplier style."""
    return SearchBuilder().filters(lambda f: f.supplier_style(style))


def by_brand(brand: str) -> SearchBuilder:
    """Quick search by brand."""
    return SearchBuilder().filters(lambda f: f.brand(brand))


def ready_for_enrichment(status_type: str = "image", status_value: int = 10) -> SearchBuilder:
    """Find product models ready for enrichment."""
    return SearchBuilder().filters(
        lambda f: f.by_attribute(f"{status_type}_status", str(status_value))
    )


def enrichment_complete(status_type: str = "image", status_value: int = 20) -> SearchBuilder:
    """Find product models with enrichment complete."""
    return SearchBuilder().filters(
        lambda f: f.by_attribute(f"{status_type}_status", str(status_value))
    )


def missing_images(image_num: int = 1) -> SearchBuilder:
    """Find products missing specific image numbers."""
    return SearchBuilder().filters(lambda f: f.missing_images(image_num))


def by_supplier(supplier_code: str) -> SearchBuilder:
    """Quick search by supplier code."""
    return SearchBuilder().filters(lambda f: f.supplier(supplier_code))


def concession_products(is_concession: bool = True) -> SearchBuilder:
    """Find concession or non-concession products."""
    return SearchBuilder().filters(lambda f: f.concession(is_concession))


def online_products() -> SearchBuilder:
    """Find products available online."""
    return SearchBuilder().filters(lambda f: f.online_ind(True).buyable_ind(True))


def clearance_products() -> SearchBuilder:
    """Find clearance products."""
    return SearchBuilder().filters(lambda f: f.clearance_ind(True))
