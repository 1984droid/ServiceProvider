# 08 Work Orders

Tags: work_orders, vocabulary, verbs, nouns, locations, costing

## The structured work order line
A WorkOrderItem is structured as:
- verb (action)
- noun (thing)
- location (where)
- quantity + uom

This enables:
- reporting
- search
- consistent quoting and parts classification

## Costing and pricing
Each WorkOrderItem carries:
- unit_cost / extended_cost (internal)
- unit_price / extended_price (billable)
- cost_type (customer_billable, warranty, internal, etc.)
- labor_hours (for labor lines)
- is_billable (for internal work)

Totals on WorkOrder:
- internal_cost_total
- billable_price_total

## Work order status semantics
Recommended states:
- OPEN
- IN_PROGRESS
- COMPLETE
- VOID/CANCELLED

Completion should:
- set started_at/completed_at timestamps
- emit AssetCostEvent ledger entries (idempotent)
- resolve linked defects (and require verification for unsafe, if enabled)
- optionally mark maintenance due instance DONE (hybrid)

## Work orders vs invoices
Work orders are execution truth. Invoices are billing truth.
A work order can generate an invoice draft; it is not itself an invoice.

## References
- packages/work_orders_gold_standard_package_v1.zip
- references/WORK_ORDER_SYSTEM_ASSESSMENT.md

---

## Implementation Status

### Work Order System v2.2 - ✅ COMPLETE

**Status**: Fully implemented and tested
**Date**: 2026-01-15
**Version**: 2.2
**File**: `asset_templates_v2_2/work_order_vocabulary/`

#### Overview

Production-ready work order system with structured vocabulary (verb+noun+location) enabling:
- Intelligent search and selection with fuzzy matching
- Standardized reporting across work orders
- Consistent quoting and parts classification
- Automatic suggestions based on noun selection
- Usage-based popularity ranking

---

### Core Components

#### 1. Work Order Models (`apps/work_orders/models.py`)

**WorkOrder Model**:
- Status workflow: `OPEN → IN_PROGRESS → COMPLETE → VOID/CANCELLED`
- Timestamps: `started_at`, `completed_at`, `created_at`, `updated_at`
- Asset linkage: `asset` FK
- Totals: `internal_cost_total`, `billable_price_total`
- Source tracking: `source_type`, `source_id` (from inspection, maintenance, manual)

**WorkOrderItem Model (Structured Line)**:
- **Verb** (action) - FK to `Verb`
- **Noun** (thing) - FK to `NounItem`
- **Service Location** (where) - FK to `ServiceLocation`
- Quantity + UOM
- Costing:
  - `unit_cost`, `extended_cost` (internal)
  - `unit_price`, `extended_price` (billable)
  - `cost_type` (customer_billable, warranty, internal, etc.)
  - `labor_hours` (for labor lines)
  - `is_billable` flag
- Line ordering: `line_order`

---

#### 2. Vocabulary System v2.3 - ✅ COMPLETE

**Status**: ✅ Fully Implemented & Tested
**Database**: SQLite (with PostgreSQL trigram support when available)
**Source**: `asset_templates_v2_3/work_order_vocabulary/`

**Stats**:
- **686 Nouns** (all active)
- **89 Verbs** (all active)
- **69 Service Locations** (all active)
- **21 Noun Categories**
- **9 Location Categories**

---

### Vocabulary Models

#### 1. NounItem (686 items)

**Purpose**: Things that can be serviced (parts, services, fees, supplies)

**Key Fields**:
- `key` - Unique identifier (e.g., `brakes_and_air_system.brake_drum`)
- `item` - Human-readable label (e.g., "Brake Drum")
- `category` - FK to NounCategory (e.g., "Brakes & Air System")
- `item_type` - PART/SERVICE/FEE/SUPPLY
- `suggested_verbs_top` - Pipe-delimited verb keys (e.g., `"replace|inspect|adjust"`)
- `suggested_verbs_more` - Additional verb suggestions
- `suggested_locations` - Pipe-delimited location codes
- `usage_count` - **Popularity ranking** (incremented on usage)
- `is_active` - Active flag

**Auto-Suggestion Logic**:
When user selects a noun, system automatically suggests:
- Top 5 verbs (most common actions for this noun)
- More verbs (additional actions)
- Relevant service locations (where work is typically done)

**Example**:
```json
{
  "key": "brakes_and_air_system.brake_drum",
  "item": "Brake Drum",
  "category": "brakes_and_air_system",
  "suggested_verbs_top": "replace|inspect|adjust|measure|torque",
  "suggested_locations": "drive_axle_forward|steer_axle_left_wheel_end|drive_axle_rear",
  "usage_count": 2
}
```

#### 2. Verb (89 items)

**Purpose**: Actions that can be performed

**Key Fields**:
- `key` - Unique identifier (e.g., `replace`)
- `label` - Display name (e.g., "Replace")
- `category` - service/inspection/adjustment/diagnostic/administrative/fabrication/disposal
- `is_active` - Active flag

**Categories**:
- **Service** (34): replace, install, repair, remove, rebuild, etc.
- **Inspection** (15): inspect, verify, test, check, monitor, etc.
- **Adjustment** (14): adjust, align, calibrate, tension, torque, etc.
- **Diagnostic** (8): diagnose, troubleshoot, analyze, measure, etc.
- **Administrative** (11): document, label, notify, schedule, etc.
- **Fabrication** (4): fabricate, weld, modify, machine
- **Disposal** (3): dispose, scrap, recycle

#### 3. ServiceLocation (69 items)

**Purpose**: Where work is performed on asset

**Key Fields**:
- `code` - Unique identifier (e.g., `drive_axle_forward`)
- `label` - Display name (e.g., "Drive Axle (Forward)")
- `category` - FK to LocationCategory
- `is_quick_pick` - Show in quick-access list
- `is_active` - Active flag

**Categories**:
- **Axles & Wheels** (18): Drive axle, steer axle, wheel ends
- **Engine & Powertrain** (8): Engine, transmission, driveline
- **Body & Structure** (10): Body panels, frame, undercarriage
- **Electrical** (7): Batteries, wiring, lighting
- **HVAC & Cab** (6): Climate control, cab interior
- **Hydraulic Systems** (9): Hydraulic components, cylinders
- **Safety & Compliance** (5): Safety equipment, DOT items
- **Fuel & Exhaust** (4): Fuel system, exhaust system
- **Auxiliary Equipment** (2): PTO, mounted equipment

---

### Intelligent Search & Suggestions

#### API Endpoint: Search Nouns (Fuzzy + Ranked)

```http
GET /api/noun-items/?q=brake&limit=20
```

**Query Parameters**:
- `q` - Search query (fuzzy match on `item` and `key`)
- `limit` - Result limit (default: 20)
- `category` - Filter by category key
- `item_type` - Filter by type (PART, SERVICE, FEE, SUPPLY)

**Search Behavior**:
- **PostgreSQL**: Uses trigram similarity (`pg_trgm` extension)
- **SQLite/Fallback**: Uses `icontains` search
- **Ranking**: Orders by similarity → usage_count → item name

**Response** (`NounItemSerializer` with parsed suggestions):
```json
{
  "count": 3,
  "results": [
    {
      "key": "brakes_and_air_system.brake_drum",
      "item": "Brake Drum",
      "category": "brakes_and_air_system",
      "category_name": "Brakes & Air System",
      "item_type": "PART",
      "usage_count": 2,
      "suggested_verbs_top": "replace|inspect|adjust|measure|torque",
      "suggested_verbs_top_parsed": [
        {"key": "replace", "label": "Replace", "category": "service"},
        {"key": "inspect", "label": "Inspect", "category": "inspection"},
        {"key": "adjust", "label": "Adjust", "category": "service"}
      ],
      "suggested_verbs_more_parsed": [...],
      "suggested_locations_parsed": [
        {"code": "drive_axle_forward", "label": "Drive Axle (Forward)", "is_quick_pick": true},
        {"code": "steer_axle_left_wheel_end", "label": "Steer Axle - Left Wheel End", "is_quick_pick": true}
      ]
    }
  ]
}
```

---

### Frontend Workflow

**Step 1: User Searches for Noun**
```javascript
// User types "brake" in search box
const response = await fetch('/api/noun-items/?q=brake&limit=20');
const data = await response.json();

// Display results with item name and category
data.results.forEach(noun => {
  console.log(`${noun.item} (${noun.category_name})`);
});
```

**Step 2: User Selects Noun → Show Suggestions**
```javascript
// User selects "Brake Drum"
const selectedNoun = data.results[0]; // brake_drum

// Show suggested verbs (top suggestions as buttons/chips)
selectedNoun.suggested_verbs_top_parsed.forEach(verb => {
  console.log(`Button: ${verb.label} (${verb.key})`);
});

// Show suggested locations (dropdown or buttons)
selectedNoun.suggested_locations_parsed.forEach(location => {
  console.log(`Location: ${location.label} (${location.code})`);
});
```

**If no suggestions** → Show all verbs/locations:
```javascript
if (selectedNoun.suggested_verbs_top_parsed.length === 0) {
  // Fetch all verbs: GET /api/verbs/
}
```

**Step 3: User Picks Suggestions → Submit**
```javascript
// User picks verb="replace" and location="steer_axle_left_wheel_end"
const payload = {
  work_order: currentWorkOrderId,
  verb: selectedVerb.key,  // "replace" (NOT "Replace")
  noun_item: selectedNoun.key,  // "brakes_and_air_system.brake_drum"
  service_location: selectedLocation.code,  // "steer_axle_left_wheel_end" (NOT label)
  quantity: 1,
  notes: "Worn drum needs replacement"
};

await fetch('/api/work-order-items/', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify(payload)
});

// Backend automatically increments usage_count for brake_drum
```

---

### Usage Tracking & Popularity

**How It Works**:
1. **Initialization**: All nouns start with `usage_count = 0`
2. **Tracking**: When `WorkOrderItem` is created, `noun.increment_usage()` is called
3. **Ranking**: Search results ordered by `usage_count` (descending)
4. **Over Time**: Most-used nouns rise to the top of search results

**Increment Logic**:
```python
def increment_usage(self):
    """Increment usage counter for popularity ranking."""
    self.usage_count = models.F('usage_count') + 1
    self.save(update_fields=['usage_count'])
```

Uses Django's F() expression for atomic increment (no race conditions).

**Query Performance - Indexes Added**:
```python
indexes = [
    models.Index(fields=['category', '-usage_count']),
    models.Index(fields=['-usage_count']),
]
```

Ensures fast queries on:
- Search by category + popularity
- Global popularity ranking

---

### Database State

**Import Command**:
```bash
python manage.py import_work_order_vocabulary_v2_3 \
  asset_templates_v2_3/work_order_vocabulary/nouns.json \
  --tenant=acme \
  --update
```

**Idempotent**: Can re-run safely without duplicates

**Current Stats**:
- 686 nouns (all active)
- 89 verbs (all active)
- 69 service locations (all active)
- 21 noun categories
- 9 location categories

**Sample Nouns with Suggestions**:
- `brakes_and_air_system.brake_drum` → 5 verbs, 9 locations
- `brakes_and_air_system.air_line_hose` → 15 verbs, 9 locations
- `equipment_and_hydraulics.aerial_boom` → 10 verbs, 5 locations

---

### API Endpoints Summary

**1. Noun Search (Fuzzy + Ranked)**
```http
GET /api/noun-items/?q=brake&limit=20
GET /api/noun-items/brakes_and_air_system.brake_drum/  # Get specific noun
POST /api/noun-items/{key}/track-usage/  # Manual usage tracking
```

**2. Verbs**
```http
GET /api/verbs/
GET /api/verbs/replace/
```

**3. Service Locations**
```http
GET /api/service-locations/
GET /api/service-locations/drive_axle_forward/
```

**4. Work Order Items**
```http
POST /api/work-order-items/
GET /api/work-order-items/?work_order={id}
PATCH /api/work-order-items/{id}/
DELETE /api/work-order-items/{id}/
```

**IMPORTANT**: Use **codes** not **labels**:
- ✅ `"verb": "replace"`
- ❌ `"verb": "Replace"`
- ✅ `"service_location": "drive_axle_forward"`
- ❌ `"service_location": "Drive Axle (Forward)"`

---

### Configuration

#### Enable PostgreSQL Trigram (Optional - Better Fuzzy Search)

If using PostgreSQL instead of SQLite:
```sql
CREATE EXTENSION IF NOT EXISTS pg_trgm;
```

The code will automatically use trigram similarity when available.

#### Adjust Search Ranking

In `apps/work_orders/api_views.py`:
```python
# Adjust similarity threshold (default: 0.1)
queryset = queryset.filter(Q(similarity__gt=0.1) | ...)

# Adjust result limit (default: 20)
limit = int(self.request.query_params.get('limit', 20))
```

---

### Common Issues & Fixes

**Issue 1: "Invalid pk - object does not exist"**
- **Cause**: Frontend sending location **label** instead of **code**
- **Fix**: Use `location.code` not `location.label`
  - ❌ Wrong: `service_location: "Drive Axle (Forward)"`
  - ✅ Correct: `service_location: "drive_axle_forward"`

**Issue 2: No suggestions appearing**
- **Cause**: Noun has empty `suggested_verbs_top`/`suggested_locations`
- **Fix**: Show all verbs/locations as fallback

**Issue 3: Search returns too many results**
- **Cause**: Default limit is 20
- **Fix**: Adjust limit parameter
  - Get more results: `?q=brake&limit=50`
  - Get fewer results: `?q=brake&limit=5`

---

### Future Enhancements

1. **Tenant-specific usage tracking** - Track usage per tenant for personalized ranking
2. **Asset-type filtering** - Show nouns relevant to asset type (truck vs aerial device)
3. **Recently used** - Endpoint for "Recently used nouns" for quick access
4. **Search analytics** - Track what users search for to improve vocabulary
5. **Synonym support** - Map common typos/variations to canonical nouns

---

### Testing Checklist

- [x] Fuzzy search returns relevant results
- [x] Popularity ranking works (most-used first)
- [x] NounItemSerializer parses suggestions correctly
- [x] WorkOrderItem creation increments usage_count
- [x] Suggestions return full objects (not just keys/codes)
- [x] Fallback search works without PostgreSQL trigram
- [x] End-to-end workflow tested successfully

---

### Related Files

**Models**:
- `apps/work_orders/models.py` - WorkOrder, WorkOrderItem, NounItem, Verb, ServiceLocation

**Serializers**:
- `apps/work_orders/serializers.py` - NounItemSerializer (with parsed suggestions)

**Views**:
- `apps/work_orders/api_views.py` - NounItemViewSet (fuzzy search + ranking)

**Utilities**:
- `apps/work_orders/suggestions.py` - Original suggestion parser (deprecated in favor of serializer)

**Import**:
- `apps/work_orders/management/commands/import_work_order_vocabulary_v2_3.py`

**Templates**:
- `asset_templates_v2_3/work_order_vocabulary/nouns.json` - Source of truth

---

**Work Order System Status**: ✅ **v2.2 Complete & Production-Ready**
**Vocabulary System Status**: ✅ **v2.3 Implemented & Tested**
**Ready For**: Structured work orders, intelligent suggestions, usage tracking, invoice generation
