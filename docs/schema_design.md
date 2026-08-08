# VeritasIQ Product Schema

## 1. Core Product Information

These are the strongest cross-category product attributes.

| Attribute | Description | Example |
|---|---|---|
| `product_name` | Name/model of the product | Galaxy S25 |
| `brand` | Consumer-facing brand | Samsung |
| `manufacturer` | Actual manufacturer/company | Samsung Electronics |
| `model_number` | Manufacturer/model identifier | SM-S931B |
| `product_code` | Product/catalog/item code | ABC-12345 |
| `product_type` | General type of product | Smartphone |
| `category` | Broad classification | Electronics |
| `subcategory` | More specific classification | Mobile Phone |
| `country_of_origin` | Manufacturing origin | India |
| `intended_use` | Intended purpose/use | Consumer use |
| `quantity` | Number of units/items | 1 |

### Schema principle

The universal schema should contain stable attributes that are useful across many physical product categories.

Category-specific attributes should not be forced into this section.

---

## 2. Physical / Commercial Information

### Physical Characteristics

| Attribute | Description | Example |
|---|---|---|
| `dimensions` | Physical dimensions | 15 × 10 × 5 cm |
| `weight` | Product weight | 1.2 kg |
| `material` | Main material | Stainless steel |
| `color` | Product color(s) | Black |
| `finish` | Surface finish | Matte |
| `shape` | Physical shape | Rectangular |
| `capacity` | Capacity where applicable | 500 mL |
| `size` | Product size | Medium, 42 inch |

These fields are optional because not every product category has every physical attribute.

### Commercial Information

| Attribute | Description | Example |
|---|---|---|
| `price` | Listed/current price | ₹24,999 |
| `currency` | Currency | INR |
| `mrp` | Maximum/list price where applicable | ₹29,999 |
| `sale_price` | Discounted price | ₹24,999 |
| `availability` | Availability status | In stock |
| `pack_size` | Number/amount in package | Pack of 4 |
| `unit_of_sale` | How product is sold | Piece, set, box |
| `purchase_channel` | Sales channel | Retail, online |

### Structured Data

Values that require structured representation should not remain uncontrolled strings.

Examples:

```text
Weight
→ value + unit

Dimensions
→ length + width + height + unit

Price
→ value + currency

Warranty
→ duration + type + coverage + exclusions + provider
```

## 3. Category-Specific Specifications

Category-specific attributes should remain separate from the universal product schema.

The universal schema should not become one giant model containing every possible product attribute.

Instead:

```text
Universal Product Schema
        +
Category-Specific Specifications
       
```

## 4. Normalization Targets

### Initial Normalization Targets

- Weight units
- Dimensions
- Currency
- Warranty duration
- Colors
- Quantities
- Storage units
- RAM units
- Battery capacity
- Screen size
- Ratings