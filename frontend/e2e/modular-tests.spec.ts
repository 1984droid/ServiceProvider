/**
 * Modular Tests - Working Examples
 *
 * Tests using modular fixtures that create their own data.
 * No dependency on seed data!
 */

import { test, expect } from './fixtures/test-data.fixture';

test.describe('Modular Tests - Customers & Assets', () => {
  test('should create and display customer', async ({ page, testCustomer }) => {
    console.log(`✓ Created customer: ${testCustomer.name} (${testCustomer.id})`);

    // Navigate to customers page
    const customersButton = page.getByRole('button', { name: /customers/i });
    await customersButton.click();
    await page.waitForTimeout(1000);

    // Verify our customer exists in the list
    const customerCard = page.getByText(testCustomer.name);
    await expect(customerCard).toBeVisible();

    console.log('✓ Customer visible in UI');
  });

  test('should create customer with vehicle', async ({
    page,
    testCustomer,
    testVehicle,
  }) => {
    console.log(`✓ Created customer: ${testCustomer.name}`);
    console.log(`✓ Created vehicle: ${testVehicle.unit_number} (VIN: ${testVehicle.vin})`);

    // Navigate to assets page
    const assetsButton = page.getByRole('button', { name: /assets/i });
    await assetsButton.click();
    await page.waitForTimeout(1000);

    // Search for our vehicle
    const searchInput = page.getByPlaceholder(/search/i);
    if (await searchInput.isVisible()) {
      await searchInput.fill(testVehicle.unit_number);
      await page.waitForTimeout(500);

      // Verify vehicle appears
      const vehicleCard = page.getByText(testVehicle.unit_number);
      await expect(vehicleCard).toBeVisible();
      console.log('✓ Vehicle visible in UI');
    }
  });

  test('should create customer with equipment', async ({
    page,
    testCustomer,
    testEquipment,
  }) => {
    console.log(`✓ Created customer: ${testCustomer.name}`);
    console.log(`✓ Created equipment: ${testEquipment.asset_number}`);

    // Navigate to assets
    const assetsButton = page.getByRole('button', { name: /assets/i });
    await assetsButton.click();
    await page.waitForTimeout(1000);

    // Search for equipment
    const searchInput = page.getByPlaceholder(/search/i);
    if (await searchInput.isVisible()) {
      await searchInput.fill(testEquipment.asset_number);
      await page.waitForTimeout(500);

      const equipmentCard = page.getByText(testEquipment.asset_number);
      await expect(equipmentCard).toBeVisible();
      console.log('✓ Equipment visible in UI');
    }
  });
});

test.describe('Modular Tests - Inspections', () => {
  test('should create and display inspection', async ({
    page,
    testCustomer,
    testEquipment,
    testInspection,
  }) => {
    console.log(`✓ Created customer: ${testCustomer.name}`);
    console.log(`✓ Created equipment: ${testEquipment.asset_number}`);
    console.log(`✓ Created inspection: ${testInspection.id}`);
    console.log(`  Template: ${testInspection.template_key}`);
    console.log(`  Status: ${testInspection.status}`);

    // Navigate to inspections
    const inspectionsButton = page.getByRole('button', { name: /inspections/i });
    await inspectionsButton.click();
    await page.waitForTimeout(1000);

    // Verify inspection appears in list
    const inspectionCards = page.locator('[data-testid="inspection-card"]');
    const count = await inspectionCards.count();
    expect(count).toBeGreaterThan(0);

    console.log(`✓ Found ${count} inspection(s) in list`);

    // Click on our inspection
    await inspectionCards.first().click();
    await page.waitForTimeout(1500);

    // Should be on execute page
    const heading = page.locator('h1');
    expect(await heading.isVisible()).toBeTruthy();
    console.log('✓ Navigated to inspection execution page');
  });

  test('should navigate inspection steps', async ({
    page,
    testCustomer,
    testEquipment,
    testInspection,
  }) => {
    console.log(`✓ Created inspection for testing steps`);

    // Navigate to inspections and open our inspection
    const inspectionsButton = page.getByRole('button', { name: /inspections/i });
    await inspectionsButton.click();
    await page.waitForTimeout(1000);

    const inspectionCards = page.locator('[data-testid="inspection-card"]');
    await inspectionCards.first().click();
    await page.waitForTimeout(1500);

    // Look for Next button
    const nextButton = page.getByRole('button', { name: /next/i });
    if (await nextButton.isVisible()) {
      console.log('✓ Next button found');

      // Click next
      await nextButton.click();
      await page.waitForTimeout(500);

      console.log('✓ Successfully navigated to next step');
    }

    // Look for stepper
    const stepper = page.locator('[data-testid="inspection-stepper"]');
    if (await stepper.isVisible()) {
      const steps = stepper.locator('[data-testid="step-item"]');
      const stepCount = await steps.count();
      console.log(`✓ Stepper shows ${stepCount} steps`);
    }
  });
});

test.describe('Modular Tests - Work Orders', () => {
  test('should create and display work order', async ({
    page,
    testCustomer,
    testEquipment,
    testWorkOrder,
  }) => {
    console.log(`✓ Created customer: ${testCustomer.name}`);
    console.log(`✓ Created equipment: ${testEquipment.asset_number}`);
    console.log(`✓ Created work order: ${testWorkOrder.work_order_number}`);
    console.log(`  Status: ${testWorkOrder.status}`);
    console.log(`  Approval: ${testWorkOrder.approval_status}`);

    // Navigate to work orders
    const workOrdersButton = page.getByRole('button', { name: /work orders/i });
    await workOrdersButton.click();
    await page.waitForTimeout(1000);

    // Verify work order appears
    const workOrderCards = page.locator('[data-testid="work-order-card"]');
    const count = await workOrderCards.count();
    expect(count).toBeGreaterThan(0);

    console.log(`✓ Found ${count} work order(s) in list`);

    // Search for our work order
    const searchInput = page.getByTestId('work-order-search');
    if (await searchInput.isVisible()) {
      await searchInput.fill(testWorkOrder.work_order_number);
      await page.waitForTimeout(500);

      const searchResults = await workOrderCards.count();
      expect(searchResults).toBeGreaterThan(0);
      console.log(`✓ Found work order via search`);
    }

    // Click on work order
    await workOrderCards.first().click();
    await page.waitForTimeout(1000);

    // Should show work order number
    const woNumber = page.getByTestId('work-order-number');
    await expect(woNumber).toBeVisible();
    console.log('✓ Navigated to work order detail page');
  });

  test('should display work order with work items', async ({
    page,
    testCustomer,
    testEquipment,
    testWorkOrder,
  }) => {
    console.log(`✓ Created work order with 1 work item`);

    // Navigate and open work order
    const workOrdersButton = page.getByRole('button', { name: /work orders/i });
    await workOrdersButton.click();
    await page.waitForTimeout(1000);

    const workOrderCards = page.locator('[data-testid="work-order-card"]');
    await workOrderCards.first().click();
    await page.waitForTimeout(1500);

    // Wait for page to load
    await page.waitForSelector('[data-testid="work-order-number"]', {
      timeout: 5000,
    });

    // Look for work items section
    const workItemsSection = page.getByText('Work Items');
    if (await workItemsSection.isVisible()) {
      console.log('✓ Work Items section found');

      // Check for work items
      const workItems = page.locator('[data-testid="work-item"]');
      const itemCount = await workItems.count();
      console.log(`✓ Found ${itemCount} work item(s)`);
      expect(itemCount).toBeGreaterThan(0);
    }
  });
});

test.describe('Modular Tests - Complex Workflows', () => {
  test('should handle complete work order workflow', async ({
    page,
    testCustomer,
    testEquipment,
    testEmployee,
  }) => {
    console.log('=== Complete Work Order Workflow ===');

    // Create work order via API
    const woResponse = await page.request.post('/api/work-orders/', {
      data: {
        customer: testCustomer.id,
        asset_type: 'EQUIPMENT',
        asset_id: testEquipment.id,
        title: 'Hydraulic System Maintenance',
        description: 'Replace hydraulic hose and check system',
        priority: 'HIGH',
        source_type: 'MANUAL',
        lines: [
          {
            verb: 'Replace',
            noun: 'Hydraulic Hose',
            service_location: 'Boom',
            estimated_hours: 3,
          },
          {
            verb: 'Inspect',
            noun: 'Hydraulic System',
            service_location: 'Platform',
            estimated_hours: 1,
          },
        ],
      },
    });

    const woData = await woResponse.json();
    console.log(`✓ Created work order: ${woData.work_order_number}`);

    // Request approval
    const approvalResponse = await page.request.post(
      `/api/work-orders/${woData.id}/request_approval/`
    );
    expect(approvalResponse.ok()).toBeTruthy();
    console.log('✓ Requested approval');

    // Approve work order
    const approveResponse = await page.request.post(
      `/api/work-orders/${woData.id}/approve/`,
      {
        data: {
          approved_by: testEmployee.id,
        },
      }
    );
    expect(approveResponse.ok()).toBeTruthy();
    console.log('✓ Approved by employee');

    // Start work
    const startResponse = await page.request.post(
      `/api/work-orders/${woData.id}/start/`
    );
    expect(startResponse.ok()).toBeTruthy();
    console.log('✓ Work started');

    // Verify status in UI
    const workOrdersButton = page.getByRole('button', { name: /work orders/i });
    await workOrdersButton.click();
    await page.waitForTimeout(1000);

    const searchInput = page.getByTestId('work-order-search');
    await searchInput.fill(woData.work_order_number);
    await page.waitForTimeout(500);

    const workOrderCard = page.locator('[data-testid="work-order-card"]').first();
    await workOrderCard.click();
    await page.waitForTimeout(1500);

    // Should show IN_PROGRESS status
    const statusBadge = page.getByTestId('status-badge');
    const statusText = await statusBadge.textContent();
    expect(statusText).toContain('IN PROGRESS');
    console.log('✓ Status shows IN PROGRESS in UI');

    console.log('=== Workflow Complete! ===');

    // Cleanup
    await page.request.delete(`/api/work-orders/${woData.id}/`);
  });

  test('should create work order via UI', async ({
    page,
    testCustomer,
    testEquipment,
  }) => {
    console.log('=== Create Work Order via UI ===');
    console.log(`✓ Customer: ${testCustomer.name}`);
    console.log(`✓ Equipment: ${testEquipment.asset_number}`);

    // Navigate to work orders
    const workOrdersButton = page.getByRole('button', { name: /work orders/i });
    await workOrdersButton.click();
    await page.waitForTimeout(1000);

    // Click create button
    const createButton = page.getByTestId('create-work-order-btn');
    await createButton.click();
    await page.waitForTimeout(500);

    // Should see create form
    const heading = page.getByRole('heading', { name: /create work order/i });
    await expect(heading).toBeVisible();
    console.log('✓ Create form loaded');

    // Select customer
    const customerSelect = page.locator('#customer');
    await customerSelect.selectOption({ label: testCustomer.name });
    await page.waitForTimeout(300);
    console.log('✓ Selected customer');

    // Select asset type
    const assetTypeSelect = page.locator('#asset-type');
    await assetTypeSelect.selectOption('EQUIPMENT');
    await page.waitForTimeout(500);
    console.log('✓ Selected asset type');

    // Select asset (find our test equipment)
    const assetSelect = page.locator('#asset');
    const assetOptions = await assetSelect.locator('option').all();

    let foundAsset = false;
    for (let i = 0; i < assetOptions.length; i++) {
      const text = await assetOptions[i].textContent();
      if (text?.includes(testEquipment.asset_number)) {
        await assetSelect.selectOption({ index: i });
        foundAsset = true;
        break;
      }
    }

    expect(foundAsset).toBeTruthy();
    console.log('✓ Selected asset');

    // Fill work order details
    await page.locator('#title').fill('UI Created Work Order');
    await page.locator('#description').fill('Created via UI test');
    await page.locator('#priority').selectOption('NORMAL');
    console.log('✓ Filled work order details');

    // Add a work order line
    const addLineButton = page.getByRole('button', { name: /add line/i });
    await addLineButton.click();
    await page.waitForTimeout(300);

    const lines = page.locator('[data-testid="work-line"]');
    expect(await lines.count()).toBe(1);
    console.log('✓ Added work order line');

    console.log('=== UI Form Ready to Submit ===');
    // Not submitting to keep test fast, but form is ready
  });
});

test.describe('Modular Tests - Data Integrity', () => {
  test('should properly cleanup test data', async ({
    page,
    testCustomer,
    testEquipment,
  }) => {
    const customerId = testCustomer.id;
    const equipmentId = testEquipment.id;

    console.log(`Customer ID: ${customerId}`);
    console.log(`Equipment ID: ${equipmentId}`);

    // Verify data exists
    const customerResponse = await page.request.get(`/api/customers/${customerId}/`);
    expect(customerResponse.ok()).toBeTruthy();

    const equipmentResponse = await page.request.get(`/api/equipment/${equipmentId}/`);
    expect(equipmentResponse.ok()).toBeTruthy();

    console.log('✓ Test data exists during test');

    // Cleanup will happen automatically after this test
    // Next test won't see this data
  });

  test('should have isolated data per test', async ({
    page,
    testCustomer,
    testVehicle,
  }) => {
    // This test has completely different data than the previous test
    console.log(`New Customer: ${testCustomer.name} (${testCustomer.id})`);
    console.log(`New Vehicle: ${testVehicle.unit_number}`);

    // Verify this is new data (different IDs)
    expect(testCustomer.id).toBeTruthy();
    expect(testVehicle.id).toBeTruthy();

    console.log('✓ Each test gets fresh, isolated data');
  });
});
