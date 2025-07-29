# search/operators.py

from enum import Enum
from typing import List, Union, Any, Dict


class ComparisonOperator(str, Enum):
    """Comparison operators for numeric, date, and other comparable types."""
    EQUALS = "="
    NOT_EQUALS = "!="
    LESS_THAN = "<"
    LESS_THAN_OR_EQUAL = "<="
    GREATER_THAN = ">"
    GREATER_THAN_OR_EQUAL = ">="
    

class ListOperator(str, Enum):
    """List-based operators."""
    IN = "IN"
    NOT_IN = "NOT IN"


class DateOperator(str, Enum):
    """Date-specific operators."""
    EQUALS = "="
    NOT_EQUALS = "!="
    LESS_THAN = "<"
    GREATER_THAN = ">"
    BETWEEN = "BETWEEN"
    NOT_BETWEEN = "NOT BETWEEN"
    SINCE_LAST_N_DAYS = "SINCE LAST N DAYS"


class TextOperator(str, Enum):
    """Text-specific operators."""
    EQUALS = "="
    NOT_EQUALS = "!="
    STARTS_WITH = "STARTS WITH"
    CONTAINS = "CONTAINS"
    DOES_NOT_CONTAIN = "DOES NOT CONTAIN"
    IN = "IN"
    NOT_IN = "NOT IN"
    EMPTY = "EMPTY"
    NOT_EMPTY = "NOT EMPTY"


class CategoryOperator(str, Enum):
    """Category-specific operators."""
    IN = "IN"
    NOT_IN = "NOT IN"
    IN_OR_UNCLASSIFIED = "IN OR UNCLASSIFIED"
    IN_CHILDREN = "IN CHILDREN"
    NOT_IN_CHILDREN = "NOT IN CHILDREN"
    UNCLASSIFIED = "UNCLASSIFIED"


class CompletenessOperator(str, Enum):
    """Completeness-specific operators."""
    EQUALS = "="
    NOT_EQUALS = "!="
    LESS_THAN = "<"
    LESS_THAN_OR_EQUAL = "<="
    GREATER_THAN = ">"
    GREATER_THAN_OR_EQUAL = ">="
    GREATER_THAN_ON_ALL_LOCALES = "GREATER THAN ON ALL LOCALES"
    GREATER_OR_EQUALS_THAN_ON_ALL_LOCALES = "GREATER OR EQUALS THAN ON ALL LOCALES"
    LOWER_THAN_ON_ALL_LOCALES = "LOWER THAN ON ALL LOCALES"
    LOWER_OR_EQUALS_THAN_ON_ALL_LOCALES = "LOWER OR EQUALS THAN ON ALL LOCALES"
    AT_LEAST_COMPLETE = "AT LEAST COMPLETE"
    AT_LEAST_INCOMPLETE = "AT LEAST INCOMPLETE"
    ALL_COMPLETE = "ALL COMPLETE"
    ALL_INCOMPLETE = "ALL INCOMPLETE"


class BooleanOperator(str, Enum):
    """Boolean-specific operators."""
    EQUALS = "="
    NOT_EQUALS = "!="
    EMPTY = "EMPTY"
    NOT_EMPTY = "NOT EMPTY"


class ParentOperator(str, Enum):
    """Parent-specific operators."""
    EQUALS = "="
    IN = "IN"
    EMPTY = "EMPTY"
    NOT_EMPTY = "NOT EMPTY"


class QualityScoreOperator(str, Enum):
    """Quality score operators."""
    IN = "IN"


class EmptyOperator(str, Enum):
    """Empty/Not empty operators."""
    EMPTY = "EMPTY"
    NOT_EMPTY = "NOT EMPTY"


# Attribute type to operators mapping
ATTRIBUTE_TYPE_OPERATORS = {
    "pim_catalog_identifier": [
        TextOperator.STARTS_WITH,
        TextOperator.CONTAINS,
        TextOperator.DOES_NOT_CONTAIN,
        TextOperator.EQUALS,
        TextOperator.NOT_EQUALS,
        TextOperator.EMPTY,
        TextOperator.NOT_EMPTY,
        TextOperator.IN,
        TextOperator.NOT_IN
    ],
    "pim_catalog_text": [
        TextOperator.STARTS_WITH,
        TextOperator.CONTAINS,
        TextOperator.DOES_NOT_CONTAIN,
        TextOperator.EQUALS,
        TextOperator.NOT_EQUALS,
        TextOperator.EMPTY,
        TextOperator.NOT_EMPTY,
        TextOperator.IN,
        TextOperator.NOT_IN
    ],
    "pim_catalog_textarea": [
        TextOperator.STARTS_WITH,
        TextOperator.CONTAINS,
        TextOperator.DOES_NOT_CONTAIN,
        TextOperator.EQUALS,
        TextOperator.NOT_EQUALS,
        TextOperator.EMPTY,
        TextOperator.NOT_EMPTY,
        TextOperator.IN,
        TextOperator.NOT_IN
    ],
    "pim_catalog_number": [
        ComparisonOperator.LESS_THAN,
        ComparisonOperator.LESS_THAN_OR_EQUAL,
        ComparisonOperator.EQUALS,
        ComparisonOperator.NOT_EQUALS,
        ComparisonOperator.GREATER_THAN_OR_EQUAL,
        ComparisonOperator.GREATER_THAN,
        EmptyOperator.EMPTY,
        EmptyOperator.NOT_EMPTY
    ],
    "pim_catalog_metric": [
        ComparisonOperator.LESS_THAN,
        ComparisonOperator.LESS_THAN_OR_EQUAL,
        ComparisonOperator.EQUALS,
        ComparisonOperator.NOT_EQUALS,
        ComparisonOperator.GREATER_THAN_OR_EQUAL,
        ComparisonOperator.GREATER_THAN,
        EmptyOperator.EMPTY,
        EmptyOperator.NOT_EMPTY
    ],
    "pim_catalog_price_collection": [
        ComparisonOperator.LESS_THAN,
        ComparisonOperator.LESS_THAN_OR_EQUAL,
        ComparisonOperator.EQUALS,
        ComparisonOperator.NOT_EQUALS,
        ComparisonOperator.GREATER_THAN_OR_EQUAL,
        ComparisonOperator.GREATER_THAN,
        EmptyOperator.EMPTY,
        EmptyOperator.NOT_EMPTY
    ],
    "pim_catalog_simpleselect": [
        ListOperator.IN,
        ListOperator.NOT_IN,
        EmptyOperator.EMPTY,
        EmptyOperator.NOT_EMPTY
    ],
    "pim_catalog_multiselect": [
        ListOperator.IN,
        ListOperator.NOT_IN,
        EmptyOperator.EMPTY,
        EmptyOperator.NOT_EMPTY
    ],
    "pim_catalog_boolean": [
        BooleanOperator.EQUALS,
        BooleanOperator.NOT_EQUALS,
        BooleanOperator.EMPTY,
        BooleanOperator.NOT_EMPTY
    ],
    "pim_catalog_date": [
        DateOperator.LESS_THAN,
        DateOperator.EQUALS,
        DateOperator.NOT_EQUALS,
        DateOperator.GREATER_THAN,
        DateOperator.BETWEEN,
        DateOperator.NOT_BETWEEN,
        EmptyOperator.EMPTY,
        EmptyOperator.NOT_EMPTY
    ],
    "pim_catalog_file": [
        TextOperator.STARTS_WITH,
        TextOperator.CONTAINS,
        TextOperator.DOES_NOT_CONTAIN,
        TextOperator.EQUALS,
        TextOperator.NOT_EQUALS,
        EmptyOperator.EMPTY,
        EmptyOperator.NOT_EMPTY
    ],
    "pim_catalog_image": [
        TextOperator.STARTS_WITH,
        TextOperator.CONTAINS,
        TextOperator.DOES_NOT_CONTAIN,
        TextOperator.EQUALS,
        TextOperator.NOT_EQUALS,
        EmptyOperator.EMPTY,
        EmptyOperator.NOT_EMPTY
    ],
    "pim_catalog_product_link": [
        ListOperator.IN,
        ListOperator.NOT_IN,
        EmptyOperator.EMPTY,
        EmptyOperator.NOT_EMPTY
    ]
}


def get_available_operators(attribute_type: str) -> List[str]:
    """Get available operators for a given attribute type."""
    return [op.value for op in ATTRIBUTE_TYPE_OPERATORS.get(attribute_type, [])]


def is_valid_operator(attribute_type: str, operator: str) -> bool:
    """Check if an operator is valid for a given attribute type."""
    return operator in get_available_operators(attribute_type)
