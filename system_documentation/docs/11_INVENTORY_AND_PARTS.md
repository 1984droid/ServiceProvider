# 11 Inventory and Parts

Tags: inventory, parts, locations, purchasing, cycle_count, reservations

## Goals
- Accurate on-hand by location (warehouse/truck/bin)
- Auditable stock movements
- Tight linkage to work orders and POS sales
- Purchasing with traceability to vendor invoices
- Special order parts reserved to specific jobs

## Inventory ledger
Use append-only InventoryTransaction as the truth:
- RECEIVE
- ISSUE
- TRANSFER
- ADJUSTMENT / COUNT_ADJUSTMENT
- RETURN_TO_VENDOR, SCRAP

Maintain a cached InventoryStock for performance.

## Locations
Locations are hierarchical and typed:
- WAREHOUSE → AISLE → BIN
- TRUCK → BIN
- CAGE / SPECIAL ORDER STAGING

A truck location can be assigned to an Asset (service truck).

## Reservations
Reservation is required for special orders and recommended generally:
- reserved_qty reduces available_qty
- on_hand_qty unchanged until issue

## Counts / cycle counts
Cycle counts should:
- snapshot system qty at start
- record counted qty
- reconcile by writing COUNT_ADJUSTMENT transactions
- require approvals for large variances

## Reorder planning (min/max)
Reorder policies exist per (part, location):
- min_qty, max_qty, lead_time, review_period
Auto-suggest min/max based on usage history (deterministic and explainable).

## References
- packages/inventory_management_gold_standard_package_v1.zip

---

## Implementation Status

### Overall Progress: 🚧 40% Complete (Models Complete, Services Pending)

**Date**: 2026-02-08
**Package**: `inventory_management_gold_standard_package_v1`
**Django App**: `apps/inventory`

---

### ✅ COMPLETED

#### 1. Django App Structure
- ✅ Created `apps/inventory` Django app
- ✅ Added to `INSTALLED_APPS` in settings.py

#### 2. Model Implementation (All 8 Phases - 100% Complete)

**Total Models**: 19 models across 8 implementation phases
**Files**:
- `apps/inventory/models.py` - Core models (Part, Location, Stock, Transaction, Reservation, Vendor)
- `apps/inventory/models_purchasing.py` - Purchasing, Cycle Count, Core, Reorder models
- Clean import structure with `__all__` export

---

### Phase I1: Parts Catalog - ✅ COMPLETE

**File**: `apps/inventory/models.py` (lines 77-218)

**Part Model**:
- `sku` - Unique per tenant
- Barcode/UPC support
- Noun classification integration (`noun_item` FK to `NounItem`)
- Core charge configuration: `is_rebuildable`, `core_charge_amount`
- Unit of measure: `base_uom`, `purchase_uom`, `conversion_factor`
- Costing defaults: `default_unit_cost`, `default_unit_price`
- Manufacturer tracking
- Flags: `is_stocked`, `is_serialized`
- **Unique constraint**: `(tenant_root, sku)`

**Database Features**:
- UUID primary keys
- Multi-tenant isolation (tenant_root FK)
- Comprehensive indexing
- Audit fields (created_at, updated_at, created_by)

---

### Phase I2: Stock & Locations - ✅ COMPLETE

**File**: `apps/inventory/models.py` (lines 225-529)

**InventoryLocation Model**:
- Hierarchy support with `parent_location` FK
- Location types: `WAREHOUSE`, `TRUCK`, `BIN`, `CAGE`, `SITE`
- Asset assignment for service trucks (`assigned_to_asset` FK)
- **Unique constraint**: `(tenant_root, code)`

**InventoryStock Model (Cache Table)**:
- Per-part, per-location stock tracking
- Fields: `on_hand_qty`, `reserved_qty`, `available_qty`
- Cached values updated via transactions
- **Unique constraint**: `(tenant_root, part, location)`
- Property: `available_qty = on_hand_qty - reserved_qty`

**InventoryTransaction Model (Append-Only Ledger)**:
- Transaction types:
  - `RECEIVE` - Parts received from vendor
  - `ISSUE` - Parts issued to work order/POS
  - `TRANSFER` - Move between locations
  - `ADJUSTMENT` - Manual adjustment
  - `COUNT_ADJUSTMENT` - Cycle count reconciliation
  - `RETURN_TO_VENDOR` - Return defective parts
  - `SCRAP` - Dispose of unusable parts
  - `CORE_RETURN` - Return core for credit
- Traceability via `source_type` and `source_id` (GenericForeignKey pattern)
- Validation in `clean()` method
- Immutable: Never delete or edit transactions

**Indexes**:
- `(tenant_root, part, location, transaction_type, created_at)` - Query by part/location
- `(tenant_root, source_type, source_id)` - Traceability lookups

---

### Phase I3: Cycle Counts - ✅ COMPLETE

**File**: `apps/inventory/models_purchasing.py` (lines 395-484)

**CycleCountSession Model**:
- Approval workflow: `IN_PROGRESS → PENDING_APPROVAL → COMPLETED/REJECTED`
- Variance threshold for manager approval
- Status tracking: `status`, `started_at`, `completed_at`, `approved_by`

**CycleCountLine Model**:
- Variance tracking per part/location
- Fields:
  - `system_qty_at_start` - Frozen snapshot
  - `counted_qty` - Actual count
  - `variance_qty` - Difference
  - `variance_value` - Financial impact
- Links to cycle count session

**Workflow**:
1. Create session with status `IN_PROGRESS`
2. Count parts, record `counted_qty`
3. System calculates `variance_qty` and `variance_value`
4. If variance > threshold: status → `PENDING_APPROVAL`
5. Manager approves: status → `COMPLETED`
6. System creates `COUNT_ADJUSTMENT` transactions

---

### Phase I4: Work Order Consumption & Reservations - ✅ COMPLETE

**File**: `apps/inventory/models.py` (lines 536-602)
**File**: `apps/inventory/models_purchasing.py` (lines 283-360)

**InventoryReservation Model**:
- Reserve parts for specific work orders
- Status: `ACTIVE`, `FULFILLED`, `CANCELLED`
- Fields:
  - `part`, `location`, `quantity_reserved`
  - `work_order_id` (UUID) - Links to WorkOrder
  - `reserved_at`, `fulfilled_at`, `cancelled_at`
- Reserved parts reduce `available_qty` but not `on_hand_qty`
- Auto-fulfilled when parts issued to work order

**SpecialOrderPartRequest Model**:
- Track special order parts for specific jobs
- Links to `work_order` and `purchase_order_line`
- Status: `REQUESTED`, `ORDERED`, `RECEIVED`, `FULFILLED`, `CANCELLED`
- Auto-reserve on receipt (logic in services layer)

---

### Phase I5: Vendor & Purchasing - ✅ COMPLETE

**File**: `apps/inventory/models.py` (lines 24-70) - Vendor
**File**: `apps/inventory/models_purchasing.py` (lines 13-266)

**Vendor Model**:
- Vendor contact info, payment terms
- Default lead time
- Active/inactive flag

**PurchaseOrder Model**:
- Status workflow: `DRAFT → SUBMITTED → PARTIALLY_RECEIVED → RECEIVED → CANCELLED`
- Fields: `po_number`, `vendor`, `order_date`, `expected_delivery_date`
- `special_order_for_work_order` flag

**PurchaseOrderLine Model**:
- Line items on PO
- Fields: `part`, `quantity_ordered`, `quantity_received`, `unit_cost_estimate`
- `special_order_for_work_order_id` - Link to work order

**ReceivingReceipt Model**:
- Record receipt of goods from vendor
- Fields: `purchase_order`, `received_date`, `received_by`, `packing_slip_number`
- Links to `ReceivingReceiptLine`

**ReceivingReceiptLine Model**:
- Line items on receipt
- Fields: `po_line`, `quantity_received`, `received_to_location`
- Triggers `RECEIVE` transaction creation

**PartReceiptCost Model**:
- Actual cost tracking for received parts
- Fields: `receipt_line`, `unit_cost_actual`, `extended_cost`
- Used for cost variance analysis

**VendorBill Model**:
- Vendor invoice for payment
- Fields: `vendor`, `bill_number`, `bill_date`, `due_date`, `total_amount`
- QBO sync status: `qbo_sync_status`, `qbo_synced_at`
- 3-way match traceability: PO → Receipt → Bill

**VendorBillLine Model**:
- Line items on vendor bill
- Fields: `receipt_line`, `quantity_billed`, `unit_cost`, `extended_cost`
- Property: `extended_cost = quantity_billed * unit_cost`

---

### Phase I6: Reorder Planning - ✅ COMPLETE

**File**: `apps/inventory/models_purchasing.py` (lines 486-613)

**ReorderPolicy Model**:
- Min/max inventory levels per part/location
- Fields:
  - `part`, `location`
  - `min_qty`, `max_qty` - Reorder thresholds
  - `lead_time_days`, `review_period_days`
  - `preferred_vendor`, `is_active`
- **Unique constraint**: `(tenant_root, part, location)`

**ReorderSuggestion Model**:
- Auto-generated reorder suggestions
- Status: `PENDING`, `APPROVED`, `ORDERED`, `REJECTED`
- Fields:
  - `part`, `location`, `policy`
  - `current_on_hand`, `suggested_order_qty`
  - `reason` - Why reorder suggested
  - `purchase_order` - Link to PO when converted
- Workflow:
  1. System generates suggestions (nightly job)
  2. Manager reviews: `PENDING → APPROVED`
  3. Convert to PO: `APPROVED → ORDERED`

**Indexes**:
- `(tenant_root, part, location)` - Policy lookups
- `(tenant_root, status, generated_at)` - Pending suggestions

---

### Phase I7: Core Charges - ✅ COMPLETE

**File**: `apps/inventory/models_purchasing.py` (lines 362-455)

**CoreLedgerEvent Model (Append-Only Ledger)**:
- Track core charge lifecycle
- Party types: `CUSTOMER`, `VENDOR`
- Event types:
  - `CORE_CHARGED` - Core charge to customer
  - `CORE_RETURNED` - Customer returns core
  - `CORE_CREDIT_ISSUED` - Credit customer for core
  - `CORE_WRITEOFF` - Write off uncollected core
- Fields:
  - `party_type`, `party_id` (customer/vendor ID)
  - `part`, `quantity`, `unit_core_amount`, `total_amount`
  - `event_type`, `event_date`
  - Traceability: `source_type`, `source_id` (invoice, credit memo, etc.)
- Indexes for balance aggregation queries:
  - `(tenant_root, party_type, party_id, part)` - Balance by customer/vendor/part
  - `(tenant_root, event_type, event_date)` - Reporting

**Use Case**: Track customer/vendor core balances
```python
# Customer core balance for brake drums
events = CoreLedgerEvent.objects.filter(
    tenant_root=tenant,
    party_type='CUSTOMER',
    party_id=customer_id,
    part=brake_drum_part
)
balance = sum(e.total_amount for e in events)
```

---

### Phase I8: QBO Integration Support - ✅ COMPLETE

**VendorBill QBO Sync Fields**:
- `qbo_sync_status` - `PENDING`, `SYNCED`, `FAILED`
- `qbo_synced_at` - Timestamp of last sync
- Ready for QBOMapping integration (from financial system)

---

### Database Design Features

**UUID Primary Keys**: All models use UUID for distributed systems
**Multi-Tenant Isolation**: `tenant_root` FK on all models
**Comprehensive Indexing**: 13+ indexes for query performance
**Unique Constraints**: Data integrity enforcement
**Append-Only Ledgers**: InventoryTransaction, CoreLedgerEvent (immutable audit trail)
**Audit Fields**: `created_at`, `updated_at`, `created_by` on all models
**Proper Related Names**: For reverse lookups
**Help Text**: On all fields for documentation
**Choices for Enum Fields**: Status, transaction type, party type, etc.

---

### ⏳ PENDING (Next Steps)

#### 1. Migrations - ⏳ PENDING (30 min)
```bash
python manage.py makemigrations inventory
python manage.py migrate
```

#### 2. Service Layer (apps/inventory/services.py) - ⏳ PENDING (~800 lines, 4 hours)

**InventoryService**:
- `receive_parts(receipt, unit_costs=None)` - Create RECEIVE transactions + update stock cache
- `issue_part_to_work_order(work_order_item, from_location)` - Create ISSUE transaction + clear reservation
- `transfer_parts(part, from_location, to_location, quantity)` - Create TRANSFER transaction + update both locations
- `adjust_stock(part, location, quantity, reason, user)` - Manual adjustment with audit trail

**ReservationService**:
- `reserve_for_work_order(part, location, quantity, work_order_id)` - Reserve parts + update stock.reserved_qty
- `clear_reservation(reservation_id)` - Mark fulfilled + update stock.reserved_qty

**CycleCountService**:
- `reconcile_cycle_count(session)` - Compare counted vs system qtys, create COUNT_ADJUSTMENT transactions, check variance threshold
- `approve_variance(session, approved_by)` - Manager approval + apply adjustments

**PurchasingService**:
- `receive_po(po_id, lines_received, location)` - Create ReceivingReceipt, update PO status, call InventoryService.receive_parts(), auto-reserve special order parts
- `create_po_from_reorder_suggestions(suggestion_ids, vendor)` - Convert suggestions to PO

**ReorderPlanningService**:
- `generate_reorder_suggestions(tenant_root)` - Find parts below min, calculate demand from transactions, create ReorderSuggestion records
- `suggest_min_max_from_history(part, location, days=90)` - Auto-calculate optimal min/max

**CoreChargeService**:
- `get_customer_core_balance(customer_id, part_id=None)` - Aggregate CoreLedgerEvent for customer
- `get_vendor_core_balance(vendor_id, part_id=None)` - Aggregate CoreLedgerEvent for vendor
- `create_core_return(party_type, party_id, part, qty)` - Log CORE_RETURNED event

#### 3. Admin Interfaces (apps/inventory/admin.py) - ⏳ PENDING (~500 lines, 2 hours)

**Admin Classes Needed**:
- VendorAdmin - list_display, search, filters
- PartAdmin - SKU search, noun filter, core charge inline
- InventoryLocationAdmin - Hierarchy display, type filter
- InventoryStockAdmin - Part/location search, available_qty display
- InventoryTransactionAdmin - Read-only, type filter, date hierarchy
- PurchaseOrderAdmin - Inline PO lines, status workflow actions
- ReceivingReceiptAdmin - Inline receipt lines
- VendorBillAdmin - QBO sync status, inline bill lines
- CycleCountSessionAdmin - Inline count lines, approve action
- ReorderSuggestionAdmin - Bulk approve, convert to PO action
- CoreLedgerEventAdmin - Read-only, party/part filters

**Admin Actions**:
- Bulk approve reorder suggestions
- Convert suggestions to PO
- Approve cycle count variance
- Mark PO as submitted
- QBO sync retry (for failed bills)

#### 4. Comprehensive Test Suite - ⏳ PENDING (~5000 lines, 200+ tests)

**Test Files to Create**:
```
apps/inventory/tests/
├── __init__.py
├── fixtures.py                     # Reusable test fixtures
├── test_models_part.py             # Phase I1: 15 tests
├── test_models_stock.py            # Phase I2: 25 tests
├── test_models_cycle_count.py      # Phase I3: 12 tests
├── test_models_reservation.py      # Phase I4: 15 tests
├── test_models_purchasing.py       # Phase I5: 20 tests
├── test_models_reorder.py          # Phase I6: 12 tests
├── test_models_core.py             # Phase I7: 18 tests
├── test_services_inventory.py      # Service layer tests
├── test_services_purchasing.py     # Purchasing workflow tests
├── test_services_cycle_count.py    # Cycle count tests
├── test_services_reorder.py        # Reorder planning tests
├── test_services_core.py           # Core charge tests
├── test_integration_full_cycle.py  # End-to-end tests
├── test_performance.py             # Performance tests
└── test_security.py                # Multi-tenancy tests
```

**See**: `INVENTORY_COMPREHENSIVE_TEST_PLAN.md` (1646 lines) for full test specifications covering:
- Phase I1: Parts Catalog (15 tests)
- Phase I2: Stock & Transactions (25 tests)
- Phase I3: Cycle Counts (12 tests)
- Phase I4: Reservations (15 tests)
- Phase I5: Purchasing (20 tests)
- Phase I6: Reorder Planning (12 tests)
- Phase I7: Core Charges (18 tests)
- Integration Tests (10 tests)
- Performance Tests (5 tests)
- Security Tests (8 tests)

#### 5. API Endpoints (Optional for Phase 1) - ⏳ PENDING (~400 lines)

REST API views:
```
POST   /api/inventory/parts/
GET    /api/inventory/parts/?sku=&noun_item=
GET    /api/inventory/stock/?part=&location=
POST   /api/inventory/transactions/receive/
POST   /api/inventory/transactions/issue/
POST   /api/inventory/transactions/transfer/
POST   /api/inventory/purchase-orders/
POST   /api/inventory/receive/
GET    /api/inventory/reorder-suggestions/
POST   /api/inventory/cycle-counts/
```

---

### Implementation Progress by Component

| Phase | Component | Status | Completion |
|-------|-----------|--------|------------|
| **Models** | All 8 phases | ✅ Done | 100% |
| **Migrations** | Initial migration | ⏳ Pending | 0% |
| **Services** | Inventory operations | ⏳ Pending | 0% |
| **Services** | Purchasing workflow | ⏳ Pending | 0% |
| **Services** | Cycle counts | ⏳ Pending | 0% |
| **Services** | Reorder planning | ⏳ Pending | 0% |
| **Services** | Core charges | ⏳ Pending | 0% |
| **Admin** | All model admins | ⏳ Pending | 0% |
| **Tests** | Phase I1 (Parts) | ⏳ Pending | 0% |
| **Tests** | Phase I2 (Stock) | ⏳ Pending | 0% |
| **Tests** | Phase I3 (Cycle Count) | ⏳ Pending | 0% |
| **Tests** | Phase I4 (Reservation) | ⏳ Pending | 0% |
| **Tests** | Phase I5 (Purchasing) | ⏳ Pending | 0% |
| **Tests** | Phase I6 (Reorder) | ⏳ Pending | 0% |
| **Tests** | Phase I7 (Core) | ⏳ Pending | 0% |
| **Tests** | Integration tests | ⏳ Pending | 0% |
| **API** | REST endpoints | ⏳ Not Started | 0% |

---

### Recommended Implementation Order

1. **Generate & Apply Migrations** (30 min)
2. **Service Layer - Core Operations** (4 hours)
3. **Admin Interfaces** (2 hours)
4. **Phase I1 Tests - Parts Catalog** (2 hours)
5. **Phase I2 Tests - Stock Transactions** (3 hours)
6. **Service Layer - Purchasing** (3 hours)
7. **Phase I5 Tests - Purchasing Workflow** (3 hours)
8. **Service Layer - Cycle Counts** (2 hours)
9. **Phase I3 Tests - Cycle Counts** (2 hours)
10. **Service Layer - Reorder Planning** (3 hours)
11. **Phase I6 Tests - Reorder Planning** (2 hours)
12. **Service Layer - Core Charges** (2 hours)
13. **Phase I7 Tests - Core Charges** (3 hours)
14. **Integration Tests** (4 hours)
15. **Performance & Security Tests** (2 hours)

**Total Estimated Time**: ~35 hours

---

### Integration Points

**Work Orders**:
- Special order parts auto-reserve on receipt
- Issue parts to work orders (ISSUE transaction)
- Track part consumption per work order

**Financial System**:
- VendorBill.qbo_sync_status for QuickBooks sync
- 3-way match: PO → Receipt → Bill
- Core charges appear on invoices (via CoreLedgerEvent)

**Leasing**:
- Core charges on customer invoices
- Parts issued for leased asset maintenance

**Assets**:
- InventoryLocation.assigned_to_asset for truck inventory
- Track parts used per asset (via work orders)

---

### Known Limitations (MVP)

- No WMS features (wave picking, RF routes)
- No full manufacturing/BOM costing
- No advanced ML forecasting (deterministic heuristics only)
- QBO sync logic not yet implemented (structure ready)

---

### Success Criteria

**✅ Models Complete**:
- [x] All 8 phases implemented (19 models)
- [x] Split into two files for maintainability
- [x] UUID primary keys for all models
- [x] Multi-tenant isolation enforced
- [x] Comprehensive indexing strategy
- [x] Unique constraints for data integrity
- [x] Append-only ledgers (immutable audit trail)
- [x] Audit fields on all models
- [x] Proper related_name for reverse lookups
- [x] Help text on all fields
- [x] Choices for enum fields

**⏳ Pending for MVP**:
- [ ] All migrations applied successfully
- [ ] 90%+ test coverage
- [ ] All service methods tested
- [ ] Admin interface functional for all models
- [ ] Multi-tenant isolation verified
- [ ] No data integrity issues (stock balances correct)
- [ ] Performance acceptable (<500ms queries, <60s batch jobs)

---

**Inventory System Status**: ✅ **Models 100% Complete** | ⏳ **Services & Tests Pending**
**Next Action**: Run `python manage.py makemigrations inventory` to generate initial migration
