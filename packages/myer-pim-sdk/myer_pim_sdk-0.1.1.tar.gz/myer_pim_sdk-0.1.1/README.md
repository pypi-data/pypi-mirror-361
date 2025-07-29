# Myer PIM SDK

[![PyPI version](https://badge.fury.io/py/myer-pim-sdk.svg)](https://badge.fury.io/py/myer-pim-sdk)
[![License: MIT](https://img.shields.io/badge/license-MIT-lightgrey.svg)](https://opensource.org/licenses/MIT)

A comprehensive Python SDK for integrating with Akeneo REST API, specifically designed for Myer's Product Information Management (PIM) system.

## Features

- **Full Akeneo REST API Coverage**: Support for products, product models, families, attributes, categories, and media files
- **Rate Limiting**: Built-in throttling to respect Myer's 20 calls per minute limit
- **Synchronous & Asynchronous**: Both sync and async client implementations
- **Type Safety**: Full Pydantic model support with type hints
- **Bulk Operations**: Efficient bulk updates for multiple entities
- **Media File Handling**: Streamlined image and file upload for product enrichment
- **Error Handling**: Comprehensive error handling with specific exception types
- **Retry Logic**: Automatic retry on transient failures
- **OAuth2 Authentication**: Automatic token management and refresh

## Installation

```bash
pip install myer-pim-sdk
```

For development with Redis support:
```bash
pip install myer-pim-sdk[redis,dev]
```

## Quick Start

### Basic Setup

```python
from myer_pim_sdk import AkeneoClient

# Initialize the client
client = AkeneoClient(
    client_id="your_client_id",
    client_secret="your_client_secret", 
    base_url="https://your-pim.akeneo.com"
)

# Get a product by identifier (SKU)
product = client.products.get_by_identifier("SKU123")
print(f"Product: {product.identifier} - {product.values}")
```

### Async Usage

```python
from myer_pim_sdk import AkeneoAsyncClient
import asyncio

async def main():
    client = AkeneoAsyncClient(
        client_id="your_client_id",
        client_secret="your_client_secret",
        base_url="https://your-pim.akeneo.com"
    )
    
    try:
        # Get product asynchronously
        product = await client.products.get_by_identifier_async("SKU123")
        print(f"Product: {product.identifier}")
        
        # List products with pagination
        products = await client.products.list_by_uuid_async(limit=50, paginated=True)
        print(f"Found {len(products.items)} products")
        
    finally:
        await client.close()

asyncio.run(main())
```

## Comprehensive Search & Filtering

The SDK provides powerful search and filtering capabilities that support all Akeneo API filter types with a fluent, pythonic interface.

### Quick Search Examples

```python
# Find enabled products
products = client.products.find_enabled()

# Find products in specific categories
winter_products = client.products.find_in_categories(["winter_collection"])

# Find incomplete products
incomplete = client.products.find_incomplete("ecommerce", threshold=80)

# Find recently updated products
recent = client.products.find_recently_updated(7)  # Last 7 days

# Find products by family
clothing = client.products.find_by_family(["clothing"])
```

### Advanced Search with SearchBuilder

```python
from myer_pim_sdk import SearchBuilder

# Complex search with multiple filters
products = client.products.search_with_builder(
    lambda f: f.enabled(True)
              .categories(["winter_collection"], "IN")
              .family(["clothing"])
              .completeness(80, "ecommerce", ">")
              .updated(30, "SINCE LAST N DAYS")
)

# Using SearchBuilder directly for more control
builder = (SearchBuilder()
           .filters(lambda f: f.enabled(True).family(["shoes"]))
           .search_locale("en_US")
           .search_scope("ecommerce")
           .pagination(page=1, limit=50))

products = client.products.search_with_builder(builder, paginated=True)
print(f"Found {len(products.items)} shoes on page {products.current_page}")
```

### Product Property Filters

Supports all Akeneo product property filters:

```python
# UUID-based filtering
products = client.products.find_by_uuid(["uuid1", "uuid2"])

# Category filters with operators
products = client.products.search_with_builder(
    lambda f: f.categories(["winter"], "IN")
              .categories(["clearance"], "NOT IN")
)

# Completeness filters
products = client.products.search_with_builder(
    lambda f: f.completeness(100, "ecommerce", "GREATER OR EQUALS THAN ON ALL LOCALES",
                            ["en_US", "fr_FR"])
)

# Date-based filters
products = client.products.search_with_builder(
    lambda f: f.created(["2024-01-01 00:00:00", "2024-12-31 23:59:59"], "BETWEEN")
              .updated(7, "SINCE LAST N DAYS")
)

# Parent/variant relationships
variants = client.products.find_variants_of("product_model_code")
simple_products = client.products.find_simple_products()

# Quality score filtering
low_quality = client.products.find_with_quality_score(["C", "D", "E"], "ecommerce", "en_US")
```

### Attribute-Based Filtering

Filter by any product attribute with type-specific operators:

```python
# Text attributes
products = client.products.search_with_builder(
    lambda f: f.attribute_text("description", "premium", "CONTAINS", "en_US", "ecommerce")
              .attribute_text("brand", "Nike", "=")
)

# Select attributes (simple/multi-select)
products = client.products.search_with_builder(
    lambda f: f.attribute_select("color", ["red", "blue"], "IN")
              .attribute_select("size", ["XL"], "NOT IN")
)

# Numeric attributes
products = client.products.search_with_builder(
    lambda f: f.attribute_number("price", 100, ">")
              .attribute_number("weight", 5.0, "<=")
)

# Boolean attributes
products = client.products.search_with_builder(
    lambda f: f.attribute_boolean("is_featured", True)
)

# Date attributes
products = client.products.search_with_builder(
    lambda f: f.attribute_date("release_date", "2024-01-01", ">")
)

# Empty/not empty attributes
products = client.products.search_with_builder(
    lambda f: f.attribute_empty("description", True, "en_US", "ecommerce")
)
```

### Product Model Search

Product models have their own specialized search methods:

```python
# Find by identifier
models = client.product_models.find_by_identifier(["model1", "model2"])

# Find root vs sub product models
root_models = client.product_models.find_root_models()
sub_models = client.product_models.find_sub_models(["parent1", "parent2"])

# Completeness for product models
complete_models = client.product_models.find_complete("ecommerce", locale="en_US")
incomplete_models = client.product_models.find_incomplete("ecommerce")

# Myer-specific: Find models ready for enrichment
enrichment_ready = client.product_models.find_for_enrichment("image", 10)
```

### Pagination

Supports Akeneo's pagination format with full control:

```python
# Basic pagination
page1 = client.products.search_with_builder(
    lambda f: f.enabled(True),
    paginated=True
)
print(f"Page {page1.current_page}: {len(page1.items)} items")
print(f"Has next: {page1.has_next}")
print(f"Next URL: {page1.next_href}")

# Manual pagination
builder = SearchBuilder().filters(lambda f: f.family(["clothing"])).limit(20)
page_num = 1

while True:
    builder.page(page_num)
    page = client.products.search_with_builder(builder, paginated=True)
    
    # Process page.items
    
    if not page.has_next:
        break
    page_num += 1

# Iterator-style pagination
for product in client.products.paginate(family=["shoes"], limit=100):
    # Process each product
    pass
```

### Asynchronous Search

All search methods have async equivalents:

```python
# Async search
products = await client.products.find_enabled_async()
models = await client.product_models.find_by_family_async(["clothing"])

# Async complex search
products = await client.products.search_with_builder_async(
    lambda f: f.enabled(True).completeness(90, "ecommerce", ">"),
    paginated=True
)

# Parallel async searches
results = await asyncio.gather(
    client.products.find_enabled_async(),
    client.products.find_incomplete_async("ecommerce", 90),
    client.product_models.find_root_models_async()
)
```

### Raw Search (Advanced)

For complete control, use raw search criteria:

```python
# Raw search criteria
search_criteria = {
    "enabled": [{"operator": "=", "value": True}],
    "family": [{"operator": "IN", "value": ["clothing"]}],
    "completeness": [{"operator": ">", "value": 80, "scope": "ecommerce"}]
}
products = client.products.search(search_criteria)

# Mix raw and builder patterns
builder = (SearchBuilder()
           .raw_filter("enabled", "=", True)
           .raw_filter("categories", "IN", ["winter_collection"])
           .filters(lambda f: f.attribute_text("brand", "Nike")))

products = client.products.search_with_builder(builder)
```

### Myer-Specific Search Workflows

```python
# Find products ready for image enrichment
image_ready = client.product_models.search_with_builder(
    lambda f: f.attribute_number("image_status", 10)  # Status 10 = ready
)

# Find products with copy enrichment complete
copy_complete = client.product_models.search_with_builder(
    lambda f: f.attribute_number("copy_status", 20)  # Status 20 = complete
)

# Complex enrichment workflow
enrichment_candidates = client.product_models.search_with_builder(
    lambda f: f.attribute_number("image_status", 10)
              .attribute_empty("description", True, "en_US", "ecommerce")
              .family(["clothing", "shoes"])
              .categories(["new_arrivals"], "IN")
)

# Find supplier products needing attention
supplier_products = client.products.search_with_builder(
    lambda f: f.categories(["supplier_category_1"], "IN")
              .completeness(90, "ecommerce", "<")
              .enabled(True)
)
```

## Magic Search for Product Values

The SDK includes powerful "magic" search capabilities specifically designed for Myer's complex product attribute structure, making it easy to search by any product value with minimal code.

### Generic Attribute Search

The `by_attribute()` method automatically detects value types and applies appropriate operators:

```python
# Generic search by any attribute - the "magic" method
products = client.product_models.search_with_builder(
    lambda f: f.by_attribute("supplier_style", "FI02847")
              .by_attribute("copy_status", "20")
              .by_attribute("concession", True)
              .by_attribute("days_in_stock", 1000, ">")
)
```

### Myer-Specific Convenience Methods

Pre-built methods for common Myer product attributes:

```python
# Myer-specific convenience methods
products = client.product_models.search_with_builder(
    lambda f: f.supplier_style("FI02847")  # Supplier style search
              .brand(["Oxford", "Nike"])  # Multiple brands
              .online_name("Belt", "CONTAINS")  # Search in product names
              .copy_status("20")  # Copy enrichment status
              .image_status("10")  # Image enrichment status
              .supplier_trust_level(["gold", "silver"])  # Trust levels
              .online_category("women_accessories")
              .concession(True)  # Concession products
              .online_ind(True)  # Available online
              .buyable_ind(True)  # Buyable products
)
```

### Quick Search Functions

Pre-configured search builders for common patterns:

```python
from myer_pim_sdk.search import (
    by_supplier_style, by_brand, ready_for_enrichment,
    enrichment_complete, missing_images, online_products
)

# Quick searches
products = client.product_models.search_with_builder(by_supplier_style("FI02847"))
models = client.product_models.search_with_builder(by_brand("Oxford"))
ready = client.product_models.search_with_builder(ready_for_enrichment("image", 10))
complete = client.product_models.search_with_builder(enrichment_complete("copy", 20))
missing = client.product_models.search_with_builder(missing_images(1))
online = client.product_models.search_with_builder(online_products())
```

### Value Filtering

Filter response values to only return specific attributes, locales, or scopes:

```python
# Only return specific attributes to reduce response size
products = client.product_models.search_with_builder(
    SearchBuilder()
    .filters(lambda f: f.brand("Trenery"))
    .attributes(["supplier_style", "online_name", "brand", "copy_status"])
    .locales(["en_AU"])  # Only Australian English
    .scope("ecommerce")  # Only ecommerce scope
    .limit(50)
)

# Response will only contain the specified attributes/locales/scope
print(f"Attributes returned: {list(products[0].values.keys())}")
```

### Complex Myer Workflows

Real-world enrichment and operational scenarios:

```python
# Find products needing comprehensive enrichment
enrichment_candidates = client.product_models.search_with_builder(
    lambda f: f.copy_status("20")  # Copy complete
              .image_status("10")  # Ready for images
              .supplier_trust_level(["gold", "silver"])  # Trusted suppliers
              .online_ind(True)  # Available online
              .missing_images(1)  # Missing images
              .has_description()  # Has description
)

# Witchery women's accessories needing attention
witchery_womens = client.product_models.search_with_builder(
    lambda f: f.brand("Witchery")
              .online_department("women")
              .online_category("women_accessories")
              .copy_status("10")  # Ready for copy
              .missing_description()  # No description yet
)

# High-priority enrichment queue
high_priority = client.product_models.search_with_builder(
    lambda f: f.online_ind(True)
              .buyable_ind(True)
              .concession(False)  # Direct Myer products
              .clearance_ind(False)  # Not clearance
              .supplier_trust_level(["gold"])  # Gold suppliers only
              .copy_status("10")
)

# Audit enrichment discrepancies
discrepancies = client.product_models.search_with_builder(
    lambda f: f.copy_status("20")  # Copy supposedly complete
              .myer_copy_status("10")  # But Myer status disagrees
              .online_ind(True)
)
```

### Supplier Analysis

```python
# Analyze performance by supplier trust level
for level in ["gold", "silver", "bronze"]:
    count = len(client.product_models.search_with_builder(
        lambda f: f.supplier_trust_level([level])
                  .copy_status("20")
                  .image_status("20")
    ))
    print(f"{level.title()} suppliers: {count} products fully enriched")

# Find specific supplier's products
supplier_products = client.product_models.search_with_builder(
    lambda f: f.supplier("9000395")
              .copy_status("10")  # Ready for enrichment
              .online_ind(True)
)
```

### Image and Content Management

```python
# Products missing specific images
products_no_image1 = client.product_models.search_with_builder(
    lambda f: f.missing_images(1)  # Missing image 1
              .online_ind(True)
              .buyable_ind(True)
)

# Products with images but missing descriptions
images_no_copy = client.product_models.search_with_builder(
    lambda f: f.has_images(1)  # Has at least image 1
              .missing_description()  # But no description
              .online_ind(True)
)

# Ready for final review
ready_for_review = client.product_models.search_with_builder(
    lambda f: f.copy_status("20")  # Copy complete
              .image_status("20")  # Images complete
              .has_description()  # Has description
              .has_images(1)  # Has images
              .online_ind(True)
)
```

### Async Magic Search

```python
# All magic search methods have async equivalents
products = await client.product_models.search_with_builder_async(
    lambda f: f.supplier_style("FI02847")
              .copy_status("20")
)

# Parallel searches for dashboard
results = await asyncio.gather(
    client.product_models.search_with_builder_async(
        lambda f: f.copy_status("10")  # Copy queue
    ),
    client.product_models.search_with_builder_async(
        lambda f: f.image_status("10")  # Image queue
    ),
    client.product_models.search_with_builder_async(
        lambda f: f.copy_status("20").image_status("20")  # Complete
    )
)
copy_queue, image_queue, complete = results
```

### Available Magic Methods

**Product Value Searches:**
- `supplier_style()` - Search by supplier style code
- `brand()` - Search by brand name
- `online_name()` - Search in product names
- `supplier()` - Search by supplier code
- `supplier_colour()` - Search by supplier color
- `product_type()` - Search by product type
- `online_category()` - Search by online category
- `online_department()` - Search by department

**Status Searches:**
- `copy_status()` - Copy enrichment status
- `image_status()` - Image enrichment status
- `myer_copy_status()` - Myer copy status
- `myer_image_status()` - Myer image status
- `supplier_trust_level()` - Supplier trust level

**Boolean Filters:**
- `concession()` - Concession products
- `online_ind()` - Online indicator
- `buyable_ind()` - Buyable indicator
- `clearance_ind()` - Clearance indicator

**Content Filters:**
- `has_images()` - Products with specific images
- `missing_images()` - Products missing images
- `has_description()` - Products with descriptions
- `missing_description()` - Products missing descriptions

**Generic:**
- `by_attribute()` - Search any attribute with auto-type detection

## Key Concepts for Myer's System

### Product Hierarchy

In Myer's Akeneo implementation:

- **Product Models** (Level 1): Main entities where copy and image enrichment occurs
- **Products** (Level 2): SKU-level items that inherit from product models

### Enrichment Status

The SDK supports Myer's enrichment status workflow:

```python
# Update enrichment status for a product model
client.product_models.update_enrichment_status(
    code="product_model_code",
    status_type="image", 
    status_value=10  # Ready for enrichment
)

# After enrichment is complete
client.product_models.update_enrichment_status(
    code="product_model_code",
    status_type="image",
    status_value=20  # Enrichment complete
)
```

### Image Upload (Core Myer Workflow)

```python
# Upload image for a product model (recommended approach)
media_file = client.media_files.upload_for_product_model(
    product_model_code="700000540",
    attribute_code="new_image1", 
    file_path="/path/to/image.jpg"
)

# Update image status after upload
client.product_models.update_enrichment_status(
    code="700000540",
    status_type="image",
    status_value=20
)
```

## Core Resources

### Products

```python
# Get product by UUID or identifier
product = client.products.get_by_uuid("uuid-here")
product = client.products.get_by_identifier("SKU123")

# Create a new product
new_product = client.products.create_with_uuid({
    "identifier": "NEW_SKU",
    "family": "clothing",
    "values": {
        "name": [{"data": "New Product", "locale": "en_US", "scope": None}]
    }
})

# Bulk update products
results = client.products.bulk_update([
    {"identifier": "SKU1", "values": {...}},
    {"identifier": "SKU2", "values": {...}}
])

# Search products
products = client.products.search({
    "family": [{"operator": "IN", "value": ["shoes", "bags"]}]
})
```

### Product Models

```python
# Get product model by code
product_model = client.product_models.get_by_code("model_code")

# Create product model
new_model = client.product_models.create_product_model({
    "code": "new_model",
    "family_variant": "clothing_material_size",
    "values": {
        "description": [{"data": "Model description", "locale": "en_US", "scope": "ecommerce"}]
    }
})

# Update product model
updated_model = client.product_models.update_by_code("model_code", {
    "values": {
        "name": [{"data": "Updated Name", "locale": "en_US", "scope": None}]
    }
})
```

### Media Files

```python
# Upload image for product model (Myer's main use case)
media_file = client.media_files.upload_for_product_model(
    product_model_code="700000540",
    attribute_code="new_image1",
    file_path="/path/to/image.jpg"
)

# Upload image for specific product
media_file = client.media_files.upload_for_product(
    product_identifier="SKU123",
    attribute_code="image", 
    file_path="/path/to/image.jpg",
    scope="ecommerce"
)

# Download media file
binary_data = client.media_files.download("media_file_code")

# Get media file info
file_info = client.media_files.get_file_info("media_file_code")
```

### Families and Attributes

```python
# Get family details
family = client.families.get_by_code("clothing")

# List attributes
attributes = client.attributes.list(limit=100)

# Create new attribute
new_attribute = client.attributes.create_attribute({
    "code": "new_attribute",
    "type": "pim_catalog_text",
    "group": "marketing",
    "labels": {"en_US": "New Attribute"}
})

# Get family variants
variants = client.family_variants.list_for_family("clothing")
```

### Categories

```python
# Get category
category = client.categories.get_by_code("men_shoes")

# Create category
new_category = client.categories.create_category({
    "code": "new_category",
    "parent": "master",
    "labels": {"en_US": "New Category"}
})

# Upload category media
client.categories.create_media_file(
    category_code="men_shoes",
    attribute_code="category_image",
    file_path="/path/to/category_image.jpg"
)
```

## Advanced Features

### Pagination

The SDK now fully supports Akeneo's pagination format with `_links`, `current_page`, and `_embedded.items`:

```python
# Manual pagination with full Akeneo support
page1 = client.products.list_by_uuid(page=1, limit=100, paginated=True)
print(f"Current page: {page1.current_page}")
print(f"Has next: {page1.has_next}")
print(f"Next URL: {page1.next_href}")
print(f"Items on page: {len(page1.items)}")

if page1.has_next:
    page2 = client.products.list_by_uuid(page=2, limit=100, paginated=True)

# Access pagination URLs directly
print(f"First page: {page1.first_href}")
print(f"Previous page: {page1.previous_href}")
print(f"Self page: {page1.self_href}")
print(f"Last page: {page1.last_href}")

# Auto-pagination generator
for product in client.products.paginate(limit=100):
    print(f"Processing product: {product.identifier}")
```

#### Pagination Response Structure

The `PaginatedResponse` object matches Akeneo's API format exactly:

```python
# Properties available on PaginatedResponse
response = client.families.list(paginated=True, limit=10)

# Basic pagination info
response.current_page      # Current page number
response.has_next         # True if next page exists
response.has_previous     # True if previous page exists  
response.has_first        # True if first page link exists
response.has_last         # True if last page link exists
response.items            # List of resource instances

# Direct URL access (matching Akeneo's _links structure)
response.next_href        # URL for next page
response.previous_href    # URL for previous page
response.first_href       # URL for first page
response.last_href        # URL for last page
response.self_href        # URL for current page
response.links            # Full _links object from Akeneo

# Standard list operations
len(response)             # Number of items on current page
response[0]               # First item
for item in response:     # Iterate over items
    process(item)
```

### Bulk Operations

```python
# Bulk update products with status tracking
products_to_update = [
    {"identifier": "SKU1", "values": {"name": [...]}},
    {"identifier": "SKU2", "values": {"description": [...]}}
]

results = client.products.bulk_update(products_to_update)
for result in results:
    if result['status_code'] == 204:
        print(f"Successfully updated {result['identifier']}")
    else:
        print(f"Failed to update {result['identifier']}: {result['message']}")
```

### Error Handling

```python
from myer_pim_sdk import (
    AkeneoAPIError,
    AuthenticationError, 
    ValidationError,
    NotFoundError,
    RateLimitError
)

try:
    product = client.products.get_by_identifier("INVALID_SKU")
except NotFoundError:
    print("Product not found")
except ValidationError as e:
    print(f"Validation error: {e.message}")
except RateLimitError as e:
    print(f"Rate limited. Retry after {e.retry_after} seconds")
except AkeneoAPIError as e:
    print(f"API error: {e.message}")
```

### System Information

```python
# Check API health
is_healthy = client.system.check_health()

# Get system info
info = client.system.get_system_information()
print(f"PIM Version: {info['version']}, Edition: {info['edition']}")

# List all available endpoints
endpoints = client.system.get_endpoints()
```

## Configuration

### Rate Limiting

The SDK automatically handles Myer's rate limit of 20 calls per minute:

```python
from myer_pim_sdk import AkeneoClient

# Rate limiting is automatically configured for Myer's limits
client = AkeneoClient(
    client_id="client_id",
    client_secret="client_secret",
    base_url="https://your-pim.akeneo.com",
    # Rate limiting is handled automatically
)
```

### Custom Configuration

```python
client = AkeneoClient(
    client_id="client_id",
    client_secret="client_secret", 
    base_url="https://your-pim.akeneo.com",
    timeout=120.0,  # Request timeout in seconds
    max_retries=3,  # Number of retries on failure
    token_buffer_seconds=300  # Refresh token 5 minutes before expiry
)
```

## Myer-Specific Workflows

### Complete Product Enrichment Workflow

```python
# 1. Get products with enrichment status 10 (ready for enrichment)
products = client.product_models.list(
    search='{"enrichment_status":[{"operator":"=","value":"10"}]}'
)

for product_model in products:
    try:
        # 2. Upload product images
        for i in range(1, 6):  # Upload up to 5 images
            try:
                image_path = f"/images/{product_model.code}_image_{i}.jpg"
                client.media_files.upload_for_product_model(
                    product_model_code=product_model.code,
                    attribute_code=f"new_image{i}",
                    file_path=image_path
                )
            except FileNotFoundError:
                break  # No more images for this product
        
        # 3. Update copy/attributes
        client.product_models.update_by_code(product_model.code, {
            "values": {
                "description": [{
                    "data": "Enhanced product description",
                    "locale": "en_US", 
                    "scope": "ecommerce"
                }],
                "short_description": [{
                    "data": "Short description",
                    "locale": "en_US",
                    "scope": "ecommerce"  
                }]
            }
        })
        
        # 4. Set enrichment status to 20 (complete)
        client.product_models.update_enrichment_status(
            code=product_model.code,
            status_type="image",
            status_value=20
        )
        
        print(f"Successfully enriched {product_model.code}")
        
    except Exception as e:
        print(f"Failed to enrich {product_model.code}: {e}")
```

### Batch Image Upload

```python
import os
from pathlib import Path

def upload_images_batch(client, image_directory: str, product_codes: list):
    """Upload images for multiple product models in batch."""
    
    results = []
    
    for product_code in product_codes:
        product_results = {"code": product_code, "uploaded_images": []}
        
        # Look for images matching the product code
        image_patterns = [
            f"{product_code}_*.jpg",
            f"{product_code}_*.png", 
            f"{product_code}_*.jpeg"
        ]
        
        image_files = []
        for pattern in image_patterns:
            image_files.extend(Path(image_directory).glob(pattern))
        
        # Upload each image found
        for i, image_path in enumerate(image_files[:5], 1):  # Max 5 images
            try:
                media_file = client.media_files.upload_for_product_model(
                    product_model_code=product_code,
                    attribute_code=f"new_image{i}",
                    file_path=str(image_path)
                )
                product_results["uploaded_images"].append({
                    "attribute": f"new_image{i}",
                    "file": image_path.name,
                    "media_code": media_file.code
                })
            except Exception as e:
                print(f"Failed to upload {image_path} for {product_code}: {e}")
        
        # Update enrichment status if any images were uploaded
        if product_results["uploaded_images"]:
            try:
                client.product_models.update_enrichment_status(
                    code=product_code,
                    status_type="image", 
                    status_value=20
                )
                product_results["status"] = "completed"
            except Exception as e:
                print(f"Failed to update status for {product_code}: {e}")
                product_results["status"] = "uploaded_but_status_failed"
        else:
            product_results["status"] = "no_images_found"
        
        results.append(product_results)
    
    return results

# Usage
image_results = upload_images_batch(
    client=client,
    image_directory="/path/to/images",
    product_codes=["700000540", "700000541", "700000542"]
)
```

## Testing

```bash
# Install development dependencies
pip install -e .[dev]

# Run tests
pytest

# Run with coverage
pytest --cov=myer_pim_sdk

# Type checking
mypy myer_pim_sdk/

# Code formatting
black myer_pim_sdk/
isort myer_pim_sdk/
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass
6. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For issues and questions:

- GitHub Issues: https://github.com/DuneRaccoon/myer-pim-sdk/issues
- Documentation: https://api.akeneo.com/api-reference.html

## Changelog

### 1.0.0 (2025-07-09)

- Initial release
- Full Akeneo REST API support
- Synchronous and asynchronous clients
- Rate limiting for Myer's API constraints
- Comprehensive media file handling
- Bulk operations support
- Type-safe models with Pydantic
- Automatic OAuth2 token management
- Easy + Magic search system for easily finding specific products