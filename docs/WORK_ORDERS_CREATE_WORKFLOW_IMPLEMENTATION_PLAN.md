# Work Orders Create & Workflow Implementation Plan
## Comprehensive, Production-Ready Implementation

**Date:** 2026-03-16
**Scope:** Complete Work Order Creation and Approval Workflow
**Approach:** No corners cut, full DATA_CONTRACT compliance, comprehensive validation

---

## Executive Summary

This plan implements the remaining Work Orders functionality:
1. **Create Flow** - Full work order creation with validation
2. **Workflow Actions** - Approval, rejection, status transitions
3. **Work Order Lines** - Add/edit/remove task lines
4. **Validation** - Business rules, data integrity, error handling

**Design Principles:**
- ✅ DATA_CONTRACT compliance - all field names, types, relationships match
- ✅ Backend-first - API endpoints exist, frontend consumes them
- ✅ Single source of truth - no duplicate patterns
- ✅ Comprehensive validation - client-side + server-side
- ✅ User experience - clear errors, loading states, success feedback
- ✅ E2E tested - all flows verified by automated tests

---

## Phase 1: Backend Validation & Enhancement

### 1.1 Review & Document Existing API Endpoints

**Already Available (✅ Working):**
```python
# Work Order CRUD
GET    /api/work-orders/              # List with filters
POST   /api/work-orders/              # Create (uses WorkOrderCreateSerializer)
GET    /api/work-orders/{id}/         # Detail
PATCH  /api/work-orders/{id}/         # Update
DELETE /api/work-orders/{id}/         # Delete

# Workflow Actions
POST   /api/work-orders/{id}/approve/    # Approve work order
POST   /api/work-orders/{id}/reject/     # Reject work order
POST   /api/work-orders/{id}/start/      # Start work
POST   /api/work-orders/{id}/complete/   # Complete work

# Special Creation
POST   /api/work-orders/from_defect/     # Create from defect
POST   /api/work-orders/from_inspection/ # Create from inspection

# Work Order Lines
GET    /api/work-order-lines/            # List lines
POST   /api/work-order-lines/            # Create line
PATCH  /api/work-order-lines/{id}/       # Update line
DELETE /api/work-order-lines/{id}/       # Delete line
POST   /api/work-order-lines/{id}/complete/  # Complete line
```

### 1.2 Missing API Endpoints to Implement

**Need to Add:**
```python
# Request Approval (NEW)
POST   /api/work-orders/{id}/request_approval/
Body: {}
Response: { work_order: WorkOrder (with approval_status='PENDING_APPROVAL') }

# Get Available Assets (NEW - for cascading dropdowns)
GET    /api/work-orders/available_assets/
Query: ?customer_id={uuid}&asset_type={VEHICLE|EQUIPMENT}
Response: { assets: [{ id, name, asset_number, ... }] }

# Get Vocabulary (Already exists via VocabularyViewSet)
GET    /api/vocabulary/verbs/
GET    /api/vocabulary/nouns/
GET    /api/vocabulary/service_locations/
```

### 1.3 Backend Validation Rules to Enforce

**Work Order Creation Validation:**
```python
class WorkOrderCreateSerializer:
    def validate(self, data):
        # 1. Customer owns the asset
        asset = get_asset(data['asset_type'], data['asset_id'])
        if asset.customer_id != data['customer']:
            raise ValidationError("Asset must belong to selected customer")

        # 2. Source inspection matches asset (if applicable)
        if data['source_type'] == 'INSPECTION_DEFECT' and data.get('source_id'):
            validate_source_matches_asset(data['source_id'], data['asset_id'])

        # 3. Scheduled date not in past
        if data.get('scheduled_date') and data['scheduled_date'] < timezone.now().date():
            raise ValidationError("Cannot schedule work in the past")

        # 4. Due date after scheduled date
        if data.get('scheduled_date') and data.get('due_date'):
            if data['due_date'] < data['scheduled_date']:
                raise ValidationError("Due date must be after scheduled date")

        return data
```

**Workflow Action Validation:**
```python
# Request Approval
- Must be in DRAFT approval_status
- Must have description and at least one line item
- Sets approval_status to PENDING_APPROVAL

# Approve
- Must be in PENDING_APPROVAL status
- Requires approved_by (employee)
- Sets approval_status to APPROVED, approved_at to now

# Reject
- Must be in PENDING_APPROVAL status
- Requires rejected_reason
- Sets approval_status to REJECTED

# Start Work
- Must have APPROVED approval_status
- Sets status to IN_PROGRESS, started_at to now

# Complete Work
- Must be in IN_PROGRESS status
- All lines must be COMPLETED
- Sets status to COMPLETED, completed_at to now
- Updates asset meters if provided
```

### 1.4 New Backend Code to Write

**File: `apps/work_orders/views.py`**
```python
@action(detail=True, methods=['post'])
def request_approval(self, request, pk=None):
    """
    Request approval for work order.

    POST /api/work-orders/{id}/request_approval/

    Business Rules:
    - Must be in DRAFT approval status
    - Must have description
    - Must have at least one work order line
    """
    work_order = self.get_object()

    # Validate current state
    if work_order.approval_status != 'DRAFT':
        return Response(
            {'error': f'Cannot request approval from {work_order.approval_status} status'},
            status=status.HTTP_400_BAD_REQUEST
        )

    # Validate has content
    if not work_order.description:
        return Response(
            {'error': 'Work order must have a description before requesting approval'},
            status=status.HTTP_400_BAD_REQUEST
        )

    if work_order.lines.count() == 0:
        return Response(
            {'error': 'Work order must have at least one line item before requesting approval'},
            status=status.HTTP_400_BAD_REQUEST
        )

    # Update approval status
    work_order.approval_status = 'PENDING_APPROVAL'
    work_order.save()

    return Response(WorkOrderSerializer(work_order).data)


@action(detail=False, methods=['get'])
def available_assets(self, request):
    """
    Get available assets for creating work orders.

    GET /api/work-orders/available_assets/?customer_id={uuid}&asset_type={VEHICLE|EQUIPMENT}

    Returns assets belonging to customer, filtered by type.
    """
    customer_id = request.query_params.get('customer_id')
    asset_type = request.query_params.get('asset_type')

    if not customer_id:
        return Response(
            {'error': 'customer_id required'},
            status=status.HTTP_400_BAD_REQUEST
        )

    if not asset_type or asset_type not in ['VEHICLE', 'EQUIPMENT']:
        return Response(
            {'error': 'asset_type must be VEHICLE or EQUIPMENT'},
            status=status.HTTP_400_BAD_REQUEST
        )

    # Get assets
    if asset_type == 'VEHICLE':
        from apps.assets.models import Vehicle
        from apps.assets.serializers import VehicleSerializer
        assets = Vehicle.objects.filter(customer_id=customer_id, is_active=True)
        data = VehicleSerializer(assets, many=True).data
    else:
        from apps.assets.models import Equipment
        from apps.assets.serializers import EquipmentSerializer
        assets = Equipment.objects.filter(customer_id=customer_id, is_active=True)
        data = EquipmentSerializer(assets, many=True).data

    return Response({'assets': data})
```

---

## Phase 2: Frontend - Create Work Order Page

### 2.1 Component Structure

```
WorkOrderCreatePage/
├── WorkOrderCreatePage.tsx          # Main create form
├── AssetSelector.tsx                # Cascading customer -> asset type -> asset
├── WorkOrderLinesEditor.tsx         # Manage work order lines
├── WorkOrderLineForm.tsx            # Add/edit single line
└── types.ts                         # TypeScript interfaces
```

### 2.2 WorkOrderCreatePage Component

**File: `frontend/src/features/work-orders/WorkOrderCreatePage.tsx`**

```typescript
import { useState, useEffect } from 'react';
import { workOrdersApi } from '@/api/workOrders.api';
import { customersApi } from '@/api/customers.api';
import { vocabularyApi } from '@/api/vocabulary.api';

interface WorkOrderCreatePageProps {
  onCancel: () => void;
  onSuccess: (workOrderId: string) => void;
}

interface CreateFormData {
  customer: string;
  asset_type: 'VEHICLE' | 'EQUIPMENT' | '';
  asset_id: string;
  title: string;
  description: string;
  priority: 'LOW' | 'NORMAL' | 'HIGH' | 'EMERGENCY';
  source_type: 'MANUAL' | 'CUSTOMER_REQUEST' | 'BREAKDOWN' | 'MAINTENANCE_SCHEDULE';
  scheduled_date?: string;
  due_date?: string;
  department?: string;
  assigned_to?: string;
  lines: WorkOrderLineInput[];
}

interface WorkOrderLineInput {
  line_number: number;
  verb: string;
  noun: string;
  service_location: string;
  description: string;
  estimated_hours?: number;
  parts_required: string[];
}

export function WorkOrderCreatePage({ onCancel, onSuccess }: WorkOrderCreatePageProps) {
  // Form state
  const [formData, setFormData] = useState<CreateFormData>({
    customer: '',
    asset_type: '',
    asset_id: '',
    title: '',
    description: '',
    priority: 'NORMAL',
    source_type: 'MANUAL',
    lines: []
  });

  // Dropdown data
  const [customers, setCustomers] = useState([]);
  const [assets, setAssets] = useState([]);
  const [departments, setDepartments] = useState([]);
  const [employees, setEmployees] = useState([]);

  // Vocabulary data
  const [verbs, setVerbs] = useState<string[]>([]);
  const [nouns, setNouns] = useState<string[]>([]);
  const [serviceLocations, setServiceLocations] = useState<string[]>([]);

  // UI state
  const [isLoading, setIsLoading] = useState(false);
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [isSaving, setIsSaving] = useState(false);

  // Load initial data
  useEffect(() => {
    loadCustomers();
    loadDepartments();
    loadVocabulary();
  }, []);

  // Load assets when customer + asset type selected
  useEffect(() => {
    if (formData.customer && formData.asset_type) {
      loadAssets(formData.customer, formData.asset_type);
    }
  }, [formData.customer, formData.asset_type]);

  const loadCustomers = async () => {
    try {
      const data = await customersApi.list();
      setCustomers(data.results || []);
    } catch (err) {
      console.error('Failed to load customers', err);
    }
  };

  const loadAssets = async (customerId: string, assetType: string) => {
    try {
      setIsLoading(true);
      const data = await workOrdersApi.getAvailableAssets(customerId, assetType);
      setAssets(data.assets || []);
    } catch (err) {
      console.error('Failed to load assets', err);
    } finally {
      setIsLoading(false);
    }
  };

  const loadVocabulary = async () => {
    try {
      const [verbsData, nounsData, locationsData] = await Promise.all([
        vocabularyApi.getVerbs(),
        vocabularyApi.getNouns(),
        vocabularyApi.getServiceLocations()
      ]);

      setVerbs(verbsData.verbs || []);
      setNouns(nounsData.nouns || []);
      setServiceLocations(locationsData.service_locations || []);
    } catch (err) {
      console.error('Failed to load vocabulary', err);
    }
  };

  const validateForm = (): boolean => {
    const newErrors: Record<string, string> = {};

    if (!formData.customer) newErrors.customer = 'Customer is required';
    if (!formData.asset_type) newErrors.asset_type = 'Asset type is required';
    if (!formData.asset_id) newErrors.asset_id = 'Asset is required';
    if (!formData.title) newErrors.title = 'Title is required';
    if (!formData.description) newErrors.description = 'Description is required';

    if (formData.scheduled_date && formData.due_date) {
      if (new Date(formData.due_date) < new Date(formData.scheduled_date)) {
        newErrors.due_date = 'Due date must be after scheduled date';
      }
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!validateForm()) return;

    try {
      setIsSaving(true);
      setErrors({});

      const payload = {
        ...formData,
        initial_lines: formData.lines
      };

      const created = await workOrdersApi.create(payload);
      onSuccess(created.id);
    } catch (err: any) {
      if (err.response?.data) {
        setErrors(err.response.data);
      } else {
        setErrors({ _general: 'Failed to create work order' });
      }
    } finally {
      setIsSaving(false);
    }
  };

  const addLine = () => {
    const newLine: WorkOrderLineInput = {
      line_number: formData.lines.length + 1,
      verb: '',
      noun: '',
      service_location: '',
      description: '',
      parts_required: []
    };
    setFormData({
      ...formData,
      lines: [...formData.lines, newLine]
    });
  };

  const updateLine = (index: number, updates: Partial<WorkOrderLineInput>) => {
    const newLines = [...formData.lines];
    newLines[index] = { ...newLines[index], ...updates };
    setFormData({ ...formData, lines: newLines });
  };

  const removeLine = (index: number) => {
    const newLines = formData.lines.filter((_, i) => i !== index);
    // Renumber remaining lines
    newLines.forEach((line, i) => {
      line.line_number = i + 1;
    });
    setFormData({ ...formData, lines: newLines });
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-6 py-6">
          <h1 className="text-2xl font-bold text-gray-900" data-testid="create-heading">
            Create Work Order
          </h1>
          <p className="text-sm text-gray-600 mt-1">
            Fill in the details below to create a new work order
          </p>
        </div>
      </div>

      {/* Form */}
      <div className="max-w-4xl mx-auto px-6 py-6">
        <form onSubmit={handleSubmit} className="space-y-6">
          {/* General Error */}
          {errors._general && (
            <div className="bg-red-50 border border-red-200 rounded-lg p-4">
              <p className="text-red-800 text-sm">{errors._general}</p>
            </div>
          )}

          {/* Customer & Asset Selection */}
          <div className="bg-white rounded-lg shadow p-6 space-y-4">
            <h2 className="text-lg font-semibold text-gray-900">Customer & Asset</h2>

            {/* Customer */}
            <div>
              <label htmlFor="customer" className="block text-sm font-medium text-gray-700 mb-2">
                Customer *
              </label>
              <select
                id="customer"
                data-testid="customer-select"
                value={formData.customer}
                onChange={(e) => setFormData({
                  ...formData,
                  customer: e.target.value,
                  asset_type: '',
                  asset_id: ''
                })}
                className={`w-full px-3 py-2 border rounded-lg ${
                  errors.customer ? 'border-red-300' : 'border-gray-300'
                }`}
                required
              >
                <option value="">Select customer...</option>
                {customers.map((c: any) => (
                  <option key={c.id} value={c.id}>{c.name}</option>
                ))}
              </select>
              {errors.customer && (
                <p className="text-red-600 text-sm mt-1">{errors.customer}</p>
              )}
            </div>

            {/* Asset Type */}
            <div>
              <label htmlFor="asset-type" className="block text-sm font-medium text-gray-700 mb-2">
                Asset Type *
              </label>
              <select
                id="asset-type"
                data-testid="asset-type-select"
                value={formData.asset_type}
                onChange={(e) => setFormData({
                  ...formData,
                  asset_type: e.target.value as 'VEHICLE' | 'EQUIPMENT',
                  asset_id: ''
                })}
                disabled={!formData.customer}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg disabled:bg-gray-100"
                required
              >
                <option value="">Select asset type...</option>
                <option value="VEHICLE">Vehicle</option>
                <option value="EQUIPMENT">Equipment</option>
              </select>
              {errors.asset_type && (
                <p className="text-red-600 text-sm mt-1">{errors.asset_type}</p>
              )}
            </div>

            {/* Asset */}
            <div>
              <label htmlFor="asset" className="block text-sm font-medium text-gray-700 mb-2">
                Asset *
              </label>
              <select
                id="asset"
                data-testid="asset-select"
                value={formData.asset_id}
                onChange={(e) => setFormData({ ...formData, asset_id: e.target.value })}
                disabled={!formData.asset_type || isLoading}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg disabled:bg-gray-100"
                required
              >
                <option value="">Select asset...</option>
                {assets.map((a: any) => (
                  <option key={a.id} value={a.id}>
                    {a.asset_number} - {a.make} {a.model || a.equipment_type}
                  </option>
                ))}
              </select>
              {errors.asset_id && (
                <p className="text-red-600 text-sm mt-1">{errors.asset_id}</p>
              )}
            </div>
          </div>

          {/* Work Details */}
          <div className="bg-white rounded-lg shadow p-6 space-y-4">
            <h2 className="text-lg font-semibold text-gray-900">Work Details</h2>

            {/* Title */}
            <div>
              <label htmlFor="title" className="block text-sm font-medium text-gray-700 mb-2">
                Title *
              </label>
              <input
                id="title"
                type="text"
                data-testid="title-input"
                value={formData.title}
                onChange={(e) => setFormData({ ...formData, title: e.target.value })}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                placeholder="Brief description of work..."
                required
              />
              {errors.title && (
                <p className="text-red-600 text-sm mt-1">{errors.title}</p>
              )}
            </div>

            {/* Description */}
            <div>
              <label htmlFor="description" className="block text-sm font-medium text-gray-700 mb-2">
                Description *
              </label>
              <textarea
                id="description"
                data-testid="description-input"
                value={formData.description}
                onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                rows={4}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                placeholder="Detailed description of work to be performed..."
                required
              />
              {errors.description && (
                <p className="text-red-600 text-sm mt-1">{errors.description}</p>
              )}
            </div>

            {/* Priority & Source Type */}
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label htmlFor="priority" className="block text-sm font-medium text-gray-700 mb-2">
                  Priority *
                </label>
                <select
                  id="priority"
                  data-testid="priority-select"
                  value={formData.priority}
                  onChange={(e) => setFormData({ ...formData, priority: e.target.value as any })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                >
                  <option value="LOW">Low</option>
                  <option value="NORMAL">Normal</option>
                  <option value="HIGH">High</option>
                  <option value="EMERGENCY">Emergency</option>
                </select>
              </div>

              <div>
                <label htmlFor="source-type" className="block text-sm font-medium text-gray-700 mb-2">
                  Source Type
                </label>
                <select
                  id="source-type"
                  data-testid="source-type-select"
                  value={formData.source_type}
                  onChange={(e) => setFormData({ ...formData, source_type: e.target.value as any })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                >
                  <option value="MANUAL">Manual</option>
                  <option value="CUSTOMER_REQUEST">Customer Request</option>
                  <option value="BREAKDOWN">Breakdown</option>
                  <option value="MAINTENANCE_SCHEDULE">Maintenance Schedule</option>
                </select>
              </div>
            </div>

            {/* Dates */}
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label htmlFor="scheduled-date" className="block text-sm font-medium text-gray-700 mb-2">
                  Scheduled Date
                </label>
                <input
                  id="scheduled-date"
                  type="date"
                  value={formData.scheduled_date || ''}
                  onChange={(e) => setFormData({ ...formData, scheduled_date: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                />
              </div>

              <div>
                <label htmlFor="due-date" className="block text-sm font-medium text-gray-700 mb-2">
                  Due Date
                </label>
                <input
                  id="due-date"
                  type="date"
                  value={formData.due_date || ''}
                  onChange={(e) => setFormData({ ...formData, due_date: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                />
                {errors.due_date && (
                  <p className="text-red-600 text-sm mt-1">{errors.due_date}</p>
                )}
              </div>
            </div>
          </div>

          {/* Work Order Lines */}
          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-lg font-semibold text-gray-900">Work Items</h2>
              <button
                type="button"
                onClick={addLine}
                className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 text-sm font-medium"
              >
                + Add Line
              </button>
            </div>

            {formData.lines.length === 0 ? (
              <p className="text-gray-500 text-sm">No work items added yet. Click "Add Line" to get started.</p>
            ) : (
              <div className="space-y-4">
                {formData.lines.map((line, index) => (
                  <WorkOrderLineForm
                    key={index}
                    line={line}
                    lineNumber={index + 1}
                    verbs={verbs}
                    nouns={nouns}
                    serviceLocations={serviceLocations}
                    onChange={(updates) => updateLine(index, updates)}
                    onRemove={() => removeLine(index)}
                  />
                ))}
              </div>
            )}
          </div>

          {/* Form Actions */}
          <div className="flex items-center justify-end gap-4">
            <button
              type="button"
              onClick={onCancel}
              data-testid="cancel-button"
              className="px-6 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 font-medium"
              disabled={isSaving}
            >
              Cancel
            </button>
            <button
              type="submit"
              data-testid="save-button"
              className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 font-medium disabled:bg-gray-400"
              disabled={isSaving}
            >
              {isSaving ? 'Creating...' : 'Create Work Order'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
```

### 2.3 Work Order Line Form Component

```typescript
// WorkOrderLineForm.tsx
interface WorkOrderLineFormProps {
  line: WorkOrderLineInput;
  lineNumber: number;
  verbs: string[];
  nouns: string[];
  serviceLocations: string[];
  onChange: (updates: Partial<WorkOrderLineInput>) => void;
  onRemove: () => void;
}

export function WorkOrderLineForm({
  line,
  lineNumber,
  verbs,
  nouns,
  serviceLocations,
  onChange,
  onRemove
}: WorkOrderLineFormProps) {
  return (
    <div className="border border-gray-200 rounded-lg p-4 bg-gray-50">
      <div className="flex items-start justify-between mb-3">
        <span className="text-sm font-medium text-gray-700">Line {lineNumber}</span>
        <button
          type="button"
          onClick={onRemove}
          className="text-red-600 hover:text-red-700 text-sm"
        >
          Remove
        </button>
      </div>

      <div className="grid grid-cols-3 gap-3 mb-3">
        {/* Verb */}
        <div>
          <label className="block text-xs font-medium text-gray-600 mb-1">
            Verb *
          </label>
          <select
            value={line.verb}
            onChange={(e) => onChange({ verb: e.target.value })}
            className="w-full px-2 py-1.5 text-sm border border-gray-300 rounded"
            required
          >
            <option value="">Select...</option>
            {verbs.map(v => (
              <option key={v} value={v}>{v}</option>
            ))}
          </select>
        </div>

        {/* Noun */}
        <div>
          <label className="block text-xs font-medium text-gray-600 mb-1">
            Noun *
          </label>
          <select
            value={line.noun}
            onChange={(e) => onChange({ noun: e.target.value })}
            className="w-full px-2 py-1.5 text-sm border border-gray-300 rounded"
            required
          >
            <option value="">Select...</option>
            {nouns.map(n => (
              <option key={n} value={n}>{n}</option>
            ))}
          </select>
        </div>

        {/* Service Location */}
        <div>
          <label className="block text-xs font-medium text-gray-600 mb-1">
            Location *
          </label>
          <select
            value={line.service_location}
            onChange={(e) => onChange({ service_location: e.target.value })}
            className="w-full px-2 py-1.5 text-sm border border-gray-300 rounded"
            required
          >
            <option value="">Select...</option>
            {serviceLocations.map(l => (
              <option key={l} value={l}>{l}</option>
            ))}
          </select>
        </div>
      </div>

      {/* Description */}
      <div className="mb-3">
        <label className="block text-xs font-medium text-gray-600 mb-1">
          Description *
        </label>
        <textarea
          value={line.description}
          onChange={(e) => onChange({ description: e.target.value })}
          rows={2}
          className="w-full px-2 py-1.5 text-sm border border-gray-300 rounded"
          placeholder="Detailed description of this task..."
          required
        />
      </div>

      {/* Estimated Hours & Parts */}
      <div className="grid grid-cols-2 gap-3">
        <div>
          <label className="block text-xs font-medium text-gray-600 mb-1">
            Estimated Hours
          </label>
          <input
            type="number"
            step="0.5"
            min="0"
            value={line.estimated_hours || ''}
            onChange={(e) => onChange({ estimated_hours: parseFloat(e.target.value) })}
            className="w-full px-2 py-1.5 text-sm border border-gray-300 rounded"
            placeholder="0.0"
          />
        </div>

        <div>
          <label className="block text-xs font-medium text-gray-600 mb-1">
            Parts Required
          </label>
          <input
            type="text"
            value={line.parts_required.join(', ')}
            onChange={(e) => onChange({
              parts_required: e.target.value.split(',').map(p => p.trim()).filter(Boolean)
            })}
            className="w-full px-2 py-1.5 text-sm border border-gray-300 rounded"
            placeholder="Part 1, Part 2, ..."
          />
        </div>
      </div>
    </div>
  );
}
```

---

## Phase 3: Frontend - Workflow Actions

### 3.1 Wire Up Existing Buttons in WorkOrderDetailPage

**Update: `WorkOrderDetailPage.tsx` Actions Section**

```typescript
// Add state for workflow actions
const [isProcessing, setIsProcessing] = useState(false);
const [actionError, setActionError] = useState<string | null>(null);

// Workflow action handlers
const handleRequestApproval = async () => {
  if (!confirm('Request approval for this work order?')) return;

  try {
    setIsProcessing(true);
    setActionError(null);
    const updated = await workOrdersApi.requestApproval(workOrder.id);
    setWorkOrder(updated);
    // Show success message
  } catch (err: any) {
    setActionError(err.response?.data?.error || 'Failed to request approval');
  } finally {
    setIsProcessing(false);
  }
};

const handleApprove = async () => {
  // Get current user (from auth context)
  const currentUser = useAuth().user;

  if (!confirm('Approve this work order?')) return;

  try {
    setIsProcessing(true);
    setActionError(null);
    const updated = await workOrdersApi.approve(workOrder.id, currentUser.employee_id);
    setWorkOrder(updated);
  } catch (err: any) {
    setActionError(err.response?.data?.error || 'Failed to approve work order');
  } finally {
    setIsProcessing(false);
  }
};

const handleReject = async () => {
  const reason = prompt('Enter rejection reason:');
  if (!reason) return;

  try {
    setIsProcessing(true);
    setActionError(null);
    const updated = await workOrdersApi.reject(workOrder.id, reason);
    setWorkOrder(updated);
  } catch (err: any) {
    setActionError(err.response?.data?.error || 'Failed to reject work order');
  } finally {
    setIsProcessing(false);
  }
};

const handleStartWork = async () => {
  if (!confirm('Start work on this work order?')) return;

  try {
    setIsProcessing(true);
    setActionError(null);
    const updated = await workOrdersApi.start(workOrder.id);
    setWorkOrder(updated);
  } catch (err: any) {
    setActionError(err.response?.data?.error || 'Failed to start work');
  } finally {
    setIsProcessing(false);
  }
};

const handleComplete = async () => {
  if (!confirm('Mark this work order as complete? This cannot be undone.')) return;

  try {
    setIsProcessing(true);
    setActionError(null);
    const updated = await workOrdersApi.complete(workOrder.id);
    setWorkOrder(updated);
  } catch (err: any) {
    setActionError(err.response?.data?.error || 'Failed to complete work order');
  } finally {
    setIsProcessing(false);
  }
};

// Update button JSX to call handlers
<button
  data-testid="request-approval-button"
  onClick={handleRequestApproval}
  disabled={isProcessing}
  className="..."
>
  {isProcessing ? 'Processing...' : 'Request Approval'}
</button>

// Similar updates for all other buttons...
```

### 3.2 Add API Methods

**File: `frontend/src/api/workOrders.api.ts`**

```typescript
export const workOrdersApi = {
  // ... existing methods

  /**
   * Request approval for work order
   */
  async requestApproval(id: string): Promise<WorkOrder> {
    const response = await apiClient.post(`/work-orders/${id}/request_approval/`);
    return response.data;
  },

  /**
   * Approve work order
   */
  async approve(id: string, approvedBy: string): Promise<WorkOrder> {
    const response = await apiClient.post(`/work-orders/${id}/approve/`, {
      approved_by: approvedBy
    });
    return response.data;
  },

  /**
   * Reject work order
   */
  async reject(id: string, reason: string): Promise<WorkOrder> {
    const response = await apiClient.post(`/work-orders/${id}/reject/`, {
      rejected_reason: reason
    });
    return response.data;
  },

  /**
   * Start work on work order
   */
  async start(id: string): Promise<WorkOrder> {
    const response = await apiClient.post(`/work-orders/${id}/start/`);
    return response.data;
  },

  /**
   * Complete work order
   */
  async complete(id: string): Promise<WorkOrder> {
    const response = await apiClient.post(`/work-orders/${id}/complete/`);
    return response.data;
  },

  /**
   * Get available assets for creating work orders
   */
  async getAvailableAssets(customerId: string, assetType: 'VEHICLE' | 'EQUIPMENT'): Promise<{ assets: any[] }> {
    const response = await apiClient.get('/work-orders/available_assets/', {
      params: { customer_id: customerId, asset_type: assetType }
    });
    return response.data;
  },

  /**
   * Create work order
   */
  async create(data: WorkOrderCreateInput): Promise<WorkOrder> {
    const response = await apiClient.post('/work-orders/', data);
    return response.data;
  }
};
```

---

## Phase 4: Testing & Validation

### 4.1 Update E2E Tests

All E2E tests should pass after implementation:
- ✅ List page tests (7/7 already passing)
- ✅ Detail page tests (12/12 already passing)
- ✅ Workflow action tests (4 tests - will pass after workflow implementation)
- ✅ Create flow tests (4 tests - will pass after create page implementation)

### 4.2 Manual Testing Checklist

**Create Flow:**
- [ ] Can select customer and see assets filtered
- [ ] Asset type cascades correctly (Vehicle/Equipment)
- [ ] Asset list populates based on customer + type
- [ ] Validation errors show for required fields
- [ ] Can add/remove work order lines
- [ ] Vocabulary dropdowns populate correctly
- [ ] Form submits and creates work order
- [ ] Redirects to detail page on success
- [ ] Backend validation errors display properly

**Workflow Actions:**
- [ ] DRAFT work order shows "Request Approval" button
- [ ] Request Approval validates (requires description + lines)
- [ ] PENDING_APPROVAL shows "Approve" and "Reject" buttons
- [ ] Approve updates approval_status and approved_by
- [ ] Reject prompts for reason and updates status
- [ ] APPROVED work order shows "Start Work" button
- [ ] Start Work updates status to IN_PROGRESS
- [ ] IN_PROGRESS shows "Complete" button
- [ ] Complete validates all lines are done
- [ ] Complete updates asset meters if provided
- [ ] All transitions show loading states
- [ ] All errors display clearly

### 4.3 Data Integrity Tests

- [ ] Cannot create WO for asset not owned by customer
- [ ] Cannot schedule in the past
- [ ] Due date must be after scheduled date
- [ ] Cannot approve without PENDING_APPROVAL status
- [ ] Cannot start without APPROVED status
- [ ] Cannot complete without all lines COMPLETED
- [ ] Cannot reopen COMPLETED/CANCELLED work orders

---

## Phase 5: Documentation

### 5.1 API Documentation Updates

Update API docs with new endpoints:
- POST /work-orders/{id}/request_approval/
- GET /work-orders/available_assets/

### 5.2 User Guide

Create user-facing documentation:
- How to create a work order
- Understanding approval workflow
- Managing work order lines
- Status transitions and what they mean

### 5.3 Developer Guide

Document for future developers:
- Component structure and responsibilities
- State management patterns used
- Validation rules (client vs server)
- How to add new workflow actions

---

## Implementation Timeline

**Phase 1: Backend (1-2 days)**
- Add request_approval endpoint
- Add available_assets endpoint
- Update validation rules
- Test API endpoints manually

**Phase 2: Create Page (2-3 days)**
- WorkOrderCreatePage component
- WorkOrderLineForm component
- Asset cascading logic
- Form validation
- API integration
- E2E tests passing

**Phase 3: Workflow Actions (1-2 days)**
- Wire up button handlers
- Add API methods
- Loading states and error handling
- Success feedback
- E2E tests passing

**Phase 4: Testing (1 day)**
- Run full E2E suite
- Manual testing checklist
- Fix any bugs found
- Data integrity validation

**Phase 5: Documentation (1 day)**
- API documentation
- User guide
- Developer guide
- Code comments

**Total: 6-9 days for complete, production-ready implementation**

---

## Success Criteria

✅ All 29 E2E tests passing
✅ Zero console errors or warnings
✅ All DATA_CONTRACT rules enforced
✅ Comprehensive validation (client + server)
✅ Clear error messages for users
✅ Loading states for all async operations
✅ Success feedback for all actions
✅ Full documentation complete
✅ Manual testing checklist 100% complete
✅ Code reviewed and approved
✅ Ready for production deployment

---

## Risk Mitigation

**Risk: Vocabulary API might not exist**
- Mitigation: Verified VocabularyViewSet exists in views.py
- Fallback: Hardcode common verbs/nouns if API unavailable

**Risk: Asset serializers might not match expected format**
- Mitigation: Check Vehicle/Equipment serializers before implementation
- Fallback: Custom serializer for available_assets endpoint

**Risk: Approval workflow might conflict with existing code**
- Mitigation: Review all existing workflow endpoints first
- Fallback: Follow existing patterns exactly

**Risk: E2E tests might have timing issues**
- Mitigation: Proper waits for loading states
- Fallback: Increase timeouts and add explicit waits

---

## Conclusion

This plan provides a complete, no-corners-cut implementation of Work Orders Create and Workflow functionality. It:
- ✅ Follows DATA_CONTRACT exactly
- ✅ Uses existing backend patterns
- ✅ Implements comprehensive validation
- ✅ Provides excellent UX
- ✅ Is fully E2E tested
- ✅ Is production-ready

**Next Step:** Review plan with stakeholders, then begin Phase 1 implementation.
