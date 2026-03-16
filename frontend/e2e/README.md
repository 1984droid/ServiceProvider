# E2E Testing with Modular Fixtures

This directory contains end-to-end tests using Playwright with a **modular, reusable fixture system** that eliminates dependency on seed data.

## Architecture

### Core Principle: Build Once, Reuse Everywhere

Instead of relying on seed data that can become stale, we use **modular data factories** that create fresh test data for each test via authenticated API calls and clean it up automatically.

```
fixtures/
  ├── auth.fixture.ts          # Authentication + JWT token extraction
  └── test-data.fixture.ts     # Modular data creation fixtures (PRODUCTION READY)

helpers/
  ├── inspection-helpers.ts    # Reusable inspection operations (planned)
  └── work-order-helpers.ts    # Reusable work order operations (planned)

examples/
  └── modular-test-example.spec.ts  # Usage examples
```

## Key Features

✅ **No seed data dependency** - Each test creates its own fresh data
✅ **Automatic cleanup** - All created data is deleted after tests
✅ **Authenticated API calls** - Uses JWT tokens from login
✅ **Type-safe** - Full TypeScript support
✅ **Modular** - Use any combination of fixtures
✅ **Production ready** - All fixtures verified and working

## Quick Start

### Basic Example: Create Customer and Equipment

```typescript
import { test, expect } from './fixtures/test-data.fixture';

test('my test', async ({ page, testCustomer, testEquipment }) => {
  // testCustomer and testEquipment are automatically created via API
  console.log(`Customer: ${testCustomer.name} (${testCustomer.id})`);
  console.log(`Equipment: ${testEquipment.asset_number}`);

  // Navigate to equipment page and verify it exists
  await page.goto('/');
  const equipmentButton = page.getByRole('button', { name: /equipment/i });
  await equipmentButton.click();

  await expect(page.getByText(testEquipment.asset_number)).toBeVisible();

  // Cleanup happens automatically at end of test!
});
```

### Available Fixtures

#### `testCustomer`
Creates a unique customer with timestamp-based name.

```typescript
test('with customer', async ({ testCustomer }) => {
  // testCustomer.id
  // testCustomer.name
  // testCustomer.cleanup() - called automatically
});
```

#### `testVehicle`
Creates a vehicle for the test customer (requires `testCustomer`).

```typescript
test('with vehicle', async ({ testCustomer, testVehicle }) => {
  // testVehicle.id
  // testVehicle.vin
  // testVehicle.customer_id
  // testVehicle.unit_number
});
```

#### `testEquipment`
Creates equipment for the test customer (requires `testCustomer`).

```typescript
test('with equipment', async ({ testCustomer, testEquipment }) => {
  // testEquipment.id
  // testEquipment.serial_number
  // testEquipment.customer_id
  // testEquipment.asset_number
});
```

#### `testInspection`
Creates an inspection for test equipment (requires `testCustomer` and `testEquipment`).

```typescript
test('with inspection', async ({ testCustomer, testEquipment, testInspection }) => {
  // testInspection.id
  // testInspection.asset_type
  // testInspection.asset_id
  // testInspection.status
});
```

#### `testWorkOrder`
Creates a work order for test equipment (requires `testCustomer` and `testEquipment`).

```typescript
test('with work order', async ({ testCustomer, testEquipment, testWorkOrder }) => {
  // testWorkOrder.id
  // testWorkOrder.work_order_number
  // testWorkOrder.status
  // testWorkOrder.approval_status
});
```

#### `testEmployee`
Creates an employee with assigned department.

```typescript
test('with employee', async ({ testEmployee }) => {
  // testEmployee.id
  // testEmployee.first_name
  // testEmployee.last_name
  // testEmployee.email
});
```

#### `authToken`
Provides JWT authentication token for API calls.

```typescript
test('with auth token', async ({ page, authToken, testCustomer }) => {
  // Make authenticated API calls
  const response = await page.request.get(`/api/customers/${testCustomer.id}/`, {
    headers: {
      'Authorization': `Bearer ${authToken}`,
    },
  });
  const data = await response.json();
});
```

## Helper Functions

### Inspection Helpers

Located in `helpers/inspection-helpers.ts`:

```typescript
import {
  createCompleteInspection,
  completeAndFinalizeInspection,
  addDefectViaAPI,
  fillInspectionViaAPI,
} from '../helpers/inspection-helpers';

test('complete inspection workflow', async ({ testCustomer, testEquipment }) => {
  // Create and fill entire inspection programmatically
  const inspectionId = await createCompleteInspection(
    testCustomer.id,
    'EQUIPMENT',
    testEquipment.id,
    'ansi_a92_2_2021_periodic'
  );

  // Add defect
  await addDefectViaAPI(inspectionId, {
    step_id: 'hydraulic_system',
    field_id: 'hose_condition',
    severity: 'CRITICAL',
    description: 'Leaking hose',
  });

  // Finalize
  await completeAndFinalizeInspection(inspectionId);
});
```

**Available Functions:**
- `createCompleteInspection()` - Create and fill entire inspection
- `completeAndFinalizeInspection()` - Finalize an inspection
- `addDefectViaAPI()` - Add defect to inspection
- `fillInspectionViaAPI()` - Fill specific steps
- `navigateInspectionSteps()` - Navigate steps in UI
- `uploadInspectionPhoto()` - Upload photo
- `getInspectionCompletion()` - Get completion percentage
- `waitForInspectionReady()` - Wait until ready to finalize

### Work Order Helpers

Located in `helpers/work-order-helpers.ts`:

```typescript
import {
  createWorkOrderViaAPI,
  requestApproval,
  approveWorkOrder,
  startWorkOrder,
  completeWorkOrder,
} from '../helpers/work-order-helpers';

test('full work order workflow', async ({ testCustomer, testEquipment, testEmployee }) => {
  // Create work order
  const woId = await createWorkOrderViaAPI({
    customer_id: testCustomer.id,
    asset_type: 'EQUIPMENT',
    asset_id: testEquipment.id,
    title: 'Repair Work',
    description: 'Fix hydraulic system',
  });

  // Request approval
  await requestApproval(woId);

  // Approve
  await approveWorkOrder(woId, testEmployee.id);

  // Start work
  await startWorkOrder(woId);

  // Complete
  await completeWorkOrder(woId);
});
```

**Available Functions:**
- `createWorkOrderViaAPI()` - Create work order
- `requestApproval()` - Request approval
- `approveWorkOrder()` - Approve work order
- `rejectWorkOrder()` - Reject work order
- `startWorkOrder()` - Start work
- `completeWorkOrder()` - Complete work
- `createWorkOrderFromDefect()` - Create from defect
- `createWorkOrdersFromInspection()` - Create from inspection
- `fillWorkOrderCreateForm()` - Fill UI form
- `createApprovedWorkOrder()` - Create fully approved WO

## Complex Workflows

### Inspection → Defect → Work Order Flow

```typescript
test('inspection to work order flow', async ({
  testCustomer,
  testEquipment,
  testEmployee,
}) => {
  // 1. Create and complete inspection
  const inspectionId = await createCompleteInspection(
    testCustomer.id,
    'EQUIPMENT',
    testEquipment.id,
    'ansi_a92_2_2021_periodic'
  );

  // 2. Add critical defect
  await addDefectViaAPI(inspectionId, {
    step_id: 'hydraulic_system',
    field_id: 'hose_condition',
    severity: 'CRITICAL',
    description: 'Hydraulic hose leaking at connection point',
    location: 'Main Boom',
  });

  // 3. Finalize inspection
  await completeAndFinalizeInspection(inspectionId);

  // 4. Generate work orders from inspection defects
  const workOrderIds = await createWorkOrdersFromInspection(inspectionId, {
    group_by_location: true,
    min_severity: 'MAJOR',
    auto_approve: false,
  });

  // 5. Approve and start first work order
  await requestApproval(workOrderIds[0]);
  await approveWorkOrder(workOrderIds[0], testEmployee.id);
  await startWorkOrder(workOrderIds[0]);

  // Complete workflow demonstrated!
});
```

## Best Practices

### 1. Use Fixtures for Data Creation

❌ **Don't rely on seed data:**
```typescript
test('bad test', async ({ page }) => {
  // Assumes customer with ID exists
  await page.goto('/customers/some-uuid');
});
```

✅ **Use fixtures:**
```typescript
test('good test', async ({ page, testCustomer }) => {
  // Customer created fresh for this test
  await page.goto(`/customers/${testCustomer.id}`);
});
```

### 2. Build Complex Scenarios with Helpers

❌ **Don't manually create everything:**
```typescript
test('bad test', async ({ page }) => {
  // Manually creating customer via UI
  await page.click('#create-customer');
  await page.fill('#name', 'Test Customer');
  // ... 20 more lines ...
});
```

✅ **Use helpers for setup:**
```typescript
test('good test', async ({ testCustomer, testEquipment }) => {
  // Data created instantly via API
  // Now test the actual functionality
  await page.goto(`/inspections/create`);
  // ... test the UI behavior ...
});
```

### 3. Test One Thing at a Time

❌ **Don't test everything in one test:**
```typescript
test('mega test', async () => {
  // Tests customer creation AND inspection AND work orders
  // If it fails, which part broke?
});
```

✅ **Focused tests:**
```typescript
test('should create customer', async ({ testCustomer }) => {
  // Only tests customer display
});

test('should create inspection', async ({ testCustomer, testEquipment, testInspection }) => {
  // Only tests inspection display
});
```

### 4. Use Helpers for Repetitive Operations

If you find yourself writing the same API calls in multiple tests, extract to a helper:

```typescript
// Instead of repeating this everywhere:
await apiClient.post('/work-orders/', data);
await apiClient.post(`/work-orders/${id}/request_approval/`);
await apiClient.post(`/work-orders/${id}/approve/`, { approved_by: empId });

// Create a helper:
await createApprovedWorkOrder(customerId, assetType, assetId, empId);
```

## Migrating Existing Tests

To migrate old tests that rely on seed data:

1. **Identify Dependencies**: What data does the test need?
2. **Add Fixtures**: Add appropriate fixtures to test signature
3. **Update Selectors**: Use fixture data instead of hardcoded IDs
4. **Remove Skips**: Tests no longer need `test.skip()` for missing data

**Before:**
```typescript
test('displays work order', async ({ page }) => {
  test.skip(); // No seed data available
  await page.goto('/work-orders/some-hardcoded-id');
});
```

**After:**
```typescript
test('displays work order', async ({ page, testWorkOrder }) => {
  await page.goto(`/work-orders/${testWorkOrder.id}`);
  // Test runs every time with fresh data!
});
```

## Performance Tips

- **Parallel Execution**: Fixtures create isolated data, so tests can run in parallel
- **API Setup**: Use helpers for setup (fast), UI for actual testing
- **Cleanup**: Happens automatically, but you can also call `cleanup()` early if needed

```typescript
test('manual cleanup example', async ({ testCustomer, testVehicle }) => {
  // Use data
  // ...

  // Cleanup early if needed
  await testVehicle.cleanup();
  await testCustomer.cleanup();

  // Continue test without this data
});
```

## Running Tests

```bash
# Run all tests with fresh data
npx playwright test

# Run specific test file
npx playwright test inspections.spec.ts

# Run with single worker (sequential)
npx playwright test --workers=1

# Run example tests to see fixtures in action
npx playwright test examples/modular-test-example.spec.ts

# Debug mode
npx playwright test --debug
```

## Troubleshooting

### Fixture not available

If you get "fixture not available" error:
```typescript
// Make sure you're importing from the right fixture file
import { test, expect } from '../fixtures/data-factories.fixture';
// NOT from '@playwright/test'
```

### Cleanup failures

Cleanup failures are logged but don't fail tests. Check console for:
```
Failed to cleanup customer xyz: ...
```

### Data conflicts

Each fixture uses timestamps to ensure unique data. If you get conflicts:
- Check that fixture is creating unique identifiers
- Verify database constraints aren't violated

## Examples

See `examples/modular-test-example.spec.ts` for comprehensive examples of:
- Basic fixture usage
- Complex workflows
- Multiple data creation
- UI and API combinations
- Inspection→Work Order flows

## Contributing

When adding new test data types:

1. Add interface to `data-factories.fixture.ts`
2. Create fixture with cleanup
3. Add helper functions to appropriate helper file
4. Update this README with examples
5. Add example test to `examples/`
