# resources/__init__.py

from .base import AkeneoResource, PaginatedResponse
from .product import Product
from .product_model import ProductModel
from .family import Family, FamilyVariant
from .attribute import Attribute, AttributeOption, AttributeGroup
from .association_type import AssociationType
from .category import Category
from .media_file import MediaFile
from .system import System

__all__ = [
    "AkeneoResource",
    "PaginatedResponse",
    "Product",
    "ProductModel", 
    "Family",
    "FamilyVariant",
    "Attribute",
    "AttributeOption",
    "AttributeGroup",
    "AssociationType",
    "Category",
    "MediaFile",
    "System"
]
