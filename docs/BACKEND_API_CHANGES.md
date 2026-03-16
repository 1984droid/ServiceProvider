# Backend API Changes

## Work Order Creation Endpoint - Response Format Improvement

**Date**: 2026-03-16
**Endpoint**: `POST /api/work-orders/`
**Status**: ✅ Completed

### Change Summary

Modified `WorkOrderCreateSerializer` to return the full work order object representation after creation, matching the format returned by the detail endpoint.

### Previous Behavior

The work order creation endpoint only returned the input fields:

```json
{
  "customer": "uuid",
  "asset_type": "EQUIPMENT",
  "asset_id": "uuid",
  "title": "Work Order Title",
  "description": "Description",
  "priority": "NORMAL",
  "source_type": "MANUAL"
}
```

### New Behavior

The work order creation endpoint now returns the complete work order object with all generated fields:

```json
{
  "id": "uuid",
  "work_order_number": "WO-2026-00001",
  "customer": "uuid",
  "customer_name": "Customer Name",
  "asset_type": "EQUIPMENT",
  "asset_id": "uuid",
  "asset_display": "Equipment details",
  "department": null,
  "department_name": null,
  "title": "Work Order Title",
  "description": "Description",
  "priority": "NORMAL",
  "status": "DRAFT",
  "source_type": "MANUAL",
  "source_id": null,
  "approval_status": "DRAFT",
  "approved_by": null,
  "approved_by_name": null,
  "approved_at": null,
  "rejected_reason": "",
  "scheduled_date": null,
  "due_date": null,
  "started_at": null,
  "completed_at": null,
  "assigned_to": null,
  "assigned_to_name": null,
  "lines": [],
  "line_count": 0,
  "total_estimated_hours": null,
  "is_active": true,
  "notes": "",
  "created_at": "2026-03-16T17:00:00Z",
  "updated_at": "2026-03-16T17:00:00Z"
}
```

### Implementation Details

**File**: `apps/work_orders/serializers.py`

Added `to_representation()` method to `WorkOrderCreateSerializer`:

```python
def to_representation(self, instance):
    """Return full WorkOrderSerializer representation after creation."""
    return WorkOrderSerializer(instance, context=self.context).data
```

### Benefits

1. **API Consistency** - POST and GET endpoints now return the same format
2. **Better DX** - Clients can use the created work order immediately without additional GET request
3. **Standard Pattern** - Follows Django REST Framework best practices
4. **No Breaking Changes** - Only adds data to response, doesn't remove anything

### Testing

- ✅ All backend work order tests pass (7/7)
- ✅ Frontend fixtures verified working
- ✅ No regression in existing functionality

### Migration Notes

**For Frontend/API Consumers**:
- This is a **non-breaking change** - additional fields are added to response
- Update your code to use the returned `id` and `work_order_number` instead of making follow-up GET requests
- All existing code will continue to work

**Backward Compatibility**: ✅ Fully backward compatible
