# Customer Duplicate Detection System

## Overview
Comprehensive fuzzy matching system to prevent duplicate customer creation using PostgreSQL trigram similarity search with weighted scoring and popularity tracking.

## Features
✅ **PostgreSQL Trigram Fuzzy Search** - Fast similarity matching using pg_trgm extension with GIN indexes
✅ **Weighted Similarity Scoring** - Configurable weights for name (50%), legal_name (30%), regulatory IDs (10%), address (10%)
✅ **Popularity Tracking** - selection_count field with logarithmic boost for frequently-used customers
✅ **Exact Regulatory Match** - USDOT/MC# exact matches are strong duplicate signals
✅ **Confidence Levels** - VERY_HIGH (0.8+), HIGH (0.6+), MEDIUM (0.4+), LOW (<0.4)
✅ **Case-Insensitive** - All matching is case-insensitive
✅ **Configurable Threshold** - Default 0.3 similarity threshold (0.0-1.0)

## Architecture

### Database Layer
**Extensions:**
- `pg_trgm` - Trigram similarity extension for fuzzy text matching

**Indexes:**
- GIN index on `customers.name` for fast trigram search
- GIN index on `customers.legal_name` for legal name matching
- B-tree index on `customers.selection_count` for popularity sorting

**Schema Changes:**
```sql
-- Customer model additions
selection_count INTEGER DEFAULT 0  -- Popularity tracking
last_selected_at TIMESTAMP NULL    -- Last selection timestamp
```

### Service Layer
**`DuplicateDetectionService`** (`apps/customers/services/duplicate_detection_service.py`)

**Methods:**
- `find_duplicates()` - Main search method with weighted scoring
- `increment_selection_count()` - Track customer selections
- `_calculate_composite_score()` - Multi-factor similarity scoring
- `_score_to_confidence()` - Convert score to human-readable confidence

**Scoring Formula:**
```python
base_score = (
    name_similarity * 0.5 +
    legal_name_similarity * 0.3 +
    regulatory_match * 0.1 +
    address_score * 0.1
)

popularity_multiplier = 1.0 + (log10(selection_count + 1) * 0.05)
total_score = min(base_score * popularity_multiplier, 1.0)
```

### API Endpoints

**Check for Duplicates**
```
POST /api/customers/check_duplicates/
```

Request Body:
```json
{
  "name": "ABC Trucking Company",
  "legal_name": "ABC Trucking LLC",
  "usdot_number": "123456",
  "mc_number": "MC-789",
  "city": "Los Angeles",
  "state": "CA",
  "exclude_customer_id": "uuid"  // Optional: for update scenarios
}
```

Response:
```json
{
  "found_duplicates": true,
  "count": 2,
  "matches": [
    {
      "customer": {
        "id": "uuid",
        "name": "ABC Trucking Company",
        "legal_name": "ABC Trucking LLC",
        "usdot_number": "123456",
        ...
      },
      "score": 0.95,
      "confidence": "VERY_HIGH",
      "match_details": {
        "total_score": 0.95,
        "base_score": 0.92,
        "name_similarity": 1.0,
        "legal_name_similarity": 0.98,
        "regulatory_match": true,
        "usdot_match": true,
        "mc_match": false,
        "address_score": 0.08,
        "city_similarity": 0.85,
        "state_match": true,
        "popularity_multiplier": 1.03,
        "selection_count": 15
      }
    }
  ]
}
```

**Increment Selection Count**
```
POST /api/customers/{id}/increment_selection/
```

Response:
```json
{
  "id": "uuid",
  "name": "ABC Trucking Company",
  "selection_count": 16,
  "last_selected_at": "2026-03-16T18:30:00Z",
  ...
}
```

## Usage Workflow

### 1. Pre-Creation Check
Before creating a new customer, check for duplicates:

```python
from apps.customers.services import DuplicateDetectionService

service = DuplicateDetectionService()
matches = service.find_duplicates(
    name="ABC Trucking",
    usdot_number="123456",
    city="Los Angeles",
    state="CA"
)

if matches:
    for match in matches:
        print(f"Found: {match['customer'].name} (score: {match['score']}, confidence: {match['confidence']})")
```

### 2. User Decision
If duplicates found:
- **Option A:** Select existing customer (increment selection_count)
- **Option B:** Create new customer anyway (user override)

### 3. Track Selection
When user selects a customer:
```python
service.increment_selection_count(customer_id)
```

## Match Quality

### Confidence Levels
- **VERY_HIGH (≥0.8):** Almost certainly a duplicate
- **HIGH (≥0.6):** Likely duplicate, recommend user review
- **MEDIUM (≥0.4):** Possible duplicate, show as suggestion
- **LOW (<0.4):** Weak match, may not show to user

### Strong Duplicate Signals
1. **Exact USDOT/MC# match** - Same regulatory ID = very likely duplicate
2. **High name similarity + same state** - Geographic + name match
3. **Exact legal name match** - Legal entity match
4. **High selection count** - Popular customer boosted in results

## Performance

### Query Optimization
- GIN indexes enable fast trigram searches on large datasets
- Initial fetch limited to 100 candidates for scoring
- Results capped at configurable max (default 10)
- Inactive customers filtered out early

### Caching
- No caching required - database queries are fast (<100ms)
- Trigram indexes make similarity queries efficient

## Testing
Comprehensive test suite with 25 tests:
- Service layer tests (16 tests)
- API endpoint tests (7 tests)
- Integration workflow tests (2 tests)

Run tests:
```bash
python -m pytest tests/test_duplicate_detection.py -v
```

## Configuration

### Adjust Similarity Threshold
```python
# More strict (fewer matches)
service = DuplicateDetectionService(similarity_threshold=0.5)

# More lenient (more matches)
service = DuplicateDetectionService(similarity_threshold=0.2)
```

### Adjust Weights
Edit `DuplicateDetectionService` class constants:
```python
NAME_WEIGHT = 0.5        # Primary business name
LEGAL_NAME_WEIGHT = 0.3  # Legal registered name
REGULATORY_WEIGHT = 0.1  # USDOT/MC# exact match
ADDRESS_WEIGHT = 0.1     # Physical address
```

## Future Enhancements
- [ ] Frontend duplicate warning modal
- [ ] Merge duplicate customers functionality
- [ ] Analytics dashboard for duplicate detection effectiveness
- [ ] ML-based similarity scoring
- [ ] Phonetic matching (Soundex/Metaphone)
- [ ] Address normalization and standardization

## Migrations
```bash
# Enable pg_trgm extension
python manage.py migrate customers 0005_enable_pg_trgm

# Add selection tracking fields
python manage.py migrate customers 0006_add_duplicate_detection_fields

# Add GIN indexes
python manage.py migrate customers 0007_add_gin_indexes_for_fuzzy_search
```

## Dependencies
- PostgreSQL 12+ (pg_trgm extension)
- Django 6.0+
- Python 3.14+

## References
- PostgreSQL pg_trgm documentation: https://www.postgresql.org/docs/current/pgtrgm.html
- Trigram similarity: https://en.wikipedia.org/wiki/Trigram
