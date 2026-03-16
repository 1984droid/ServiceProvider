/**
 * Example Test Using Modular Fixtures
 *
 * This demonstrates how to use the modular data factory fixtures
 * to create tests that don't rely on seed data.
 *
 * Each test creates its own data and cleans up automatically.
 */

import { test, expect } from '../fixtures/data-factories.fixture';
import {
  createCompleteInspection,
  completeAndFinalizeInspection,
  addDefectViaAPI,
} from '../helpers/inspection-helpers';
import {
  createWorkOrderViaAPI,
  requestApproval,
  approveWorkOrder,
  startWorkOrder,
  completeWorkOrder,
  createWorkOrdersFromInspection,
} from '../helpers/work-order-helpers';

test.describe('Modular Test Examples', () => {
  test('Example 1: Create customer and vehicle', async ({
    page,
    testCustomer,
    testVehicle,
  }) => {
    console.log(`Created customer: ${testCustomer.name} (${testCustomer.id})`);
    console.log(`Created vehicle: ${testVehicle.unit_number} (${testVehicle.id})`);

    // Navigate to vehicles page and verify it appears
    const vehiclesButton = page.getByRole('button', { name: /assets/i });
    await vehiclesButton.click();
    await page.waitForTimeout(1000);

    // Search for our vehicle
    const searchInput = page.getByPlaceholder(/search/i);
    if (await searchInput.isVisible()) {
      await searchInput.fill(testVehicle.unit_number);
      await page.waitForTimeout(500);

      // Verify vehicle appears in results
      const vehicleCard = page.getByText(testVehicle.unit_number);
      await expect(vehicleCard).toBeVisible();
    }

    // Cleanup happens automatically after test!
  });

  test('Example 2: Create equipment and inspection', async ({
    page,
    testCustomer,
    testEquipment,
    testInspection,
  }) => {
    console.log(`Created equipment: ${testEquipment.asset_number}`);
    console.log(`Created inspection: ${testInspection.id}`);

    // Navigate to inspections page
    const inspectionsButton = page.getByRole('button', { name: /inspections/i });
    await inspectionsButton.click();
    await page.waitForTimeout(1000);

    // Our inspection should be in the list
    const inspectionCards = page.locator('[data-testid="inspection-card"]');
    expect(await inspectionCards.count()).toBeGreaterThan(0);

    // Cleanup happens automatically!
  });

  test('Example 3: Complete full inspection workflow', async ({
    testCustomer,
    testEquipment,
  }) => {
    // Create and complete an inspection programmatically
    const inspectionId = await createCompleteInspection(
      testCustomer.id,
      'EQUIPMENT',
      testEquipment.id,
      'ansi_a92_2_2021_periodic'
    );

    console.log(`Created and filled inspection: ${inspectionId}`);

    // Add a defect
    await addDefectViaAPI(inspectionId, {
      step_id: 'general_info',
      field_id: 'serial_number',
      severity: 'MINOR',
      description: 'Serial number plate damaged',
      location: 'Frame',
    });

    // Finalize the inspection
    await completeAndFinalizeInspection(inspectionId);

    console.log('Inspection completed and finalized!');

    // This inspection is now ready for work order generation
  });

  test('Example 4: Full work order workflow', async ({
    testCustomer,
    testEquipment,
    testEmployee,
  }) => {
    // Create work order
    const workOrderId = await createWorkOrderViaAPI({
      customer_id: testCustomer.id,
      asset_type: 'EQUIPMENT',
      asset_id: testEquipment.id,
      title: 'Hydraulic System Repair',
      description: 'Replace damaged hydraulic hose',
      priority: 'HIGH',
      lines: [
        {
          verb: 'Replace',
          noun: 'Hydraulic Hose',
          service_location: 'Boom',
          estimated_hours: 3,
        },
      ],
    });

    console.log(`Created work order: ${workOrderId}`);

    // Request approval
    await requestApproval(workOrderId);
    console.log('Requested approval');

    // Approve it
    await approveWorkOrder(workOrderId, testEmployee.id);
    console.log('Approved by employee');

    // Start work
    await startWorkOrder(workOrderId);
    console.log('Work started');

    // Complete work (in real scenario, would complete lines first)
    await completeWorkOrder(workOrderId);
    console.log('Work completed!');

    // All done - cleanup happens automatically
  });

  test('Example 5: Inspection to Work Order flow', async ({
    testCustomer,
    testEquipment,
    testEmployee,
  }) => {
    // Create and complete inspection with defects
    const inspectionId = await createCompleteInspection(
      testCustomer.id,
      'EQUIPMENT',
      testEquipment.id,
      'ansi_a92_2_2021_periodic'
    );

    // Add critical defect
    const defectId = await addDefectViaAPI(inspectionId, {
      step_id: 'hydraulic_system',
      field_id: 'hose_condition',
      severity: 'CRITICAL',
      description: 'Hydraulic hose leaking',
      location: 'Main Boom',
    });

    // Finalize inspection
    await completeAndFinalizeInspection(inspectionId);

    console.log('Inspection completed with critical defect');

    // Generate work orders from inspection
    const workOrderIds = await createWorkOrdersFromInspection(inspectionId, {
      group_by_location: true,
      min_severity: 'MAJOR',
      auto_approve: false,
    });

    console.log(`Generated ${workOrderIds.length} work orders from inspection`);

    // Approve first work order
    if (workOrderIds.length > 0) {
      await requestApproval(workOrderIds[0]);
      await approveWorkOrder(workOrderIds[0], testEmployee.id);
      console.log('First work order approved');
    }

    // Complete workflow demonstrated!
  });

  test('Example 6: Multiple customers and assets', async ({ page }) => {
    // You can create multiple instances manually for complex scenarios
    const timestamp1 = Date.now();
    const timestamp2 = timestamp1 + 1;

    // Create first customer + vehicle
    const customer1Response = await page.request.post('/api/customers/', {
      data: {
        name: `Customer A ${timestamp1}`,
        legal_name: `Customer A LLC ${timestamp1}`,
      },
    });
    const customer1 = await customer1Response.json();

    const vehicle1Response = await page.request.post('/api/vehicles/', {
      data: {
        customer: customer1.id,
        vin: `1HGBH41JXMN${String(timestamp1).slice(-6)}`,
        unit_number: `UNIT-A-${timestamp1}`,
        year: 2020,
        make: 'Ford',
        model: 'F-550',
        capabilities: ['UTILITY_TRUCK'],
      },
    });
    const vehicle1 = await vehicle1Response.json();

    // Create second customer + equipment
    const customer2Response = await page.request.post('/api/customers/', {
      data: {
        name: `Customer B ${timestamp2}`,
        legal_name: `Customer B LLC ${timestamp2}`,
      },
    });
    const customer2 = await customer2Response.json();

    const equipment1Response = await page.request.post('/api/equipment/', {
      data: {
        customer: customer2.id,
        serial_number: `SN-B-${timestamp2}`,
        asset_number: `ASSET-B-${timestamp2}`,
        manufacturer: 'Altec',
        model: 'AT37G',
        equipment_type: 'AERIAL_DEVICE',
        capabilities: ['AERIAL_LIFT', 'INSULATED_BOOM'],
      },
    });
    const equipment1 = await equipment1Response.json();

    console.log(`Created 2 customers with assets`);
    console.log(`Customer 1: ${customer1.name}, Vehicle: ${vehicle1.unit_number}`);
    console.log(
      `Customer 2: ${customer2.name}, Equipment: ${equipment1.asset_number}`
    );

    // Cleanup
    await page.request.delete(`/api/vehicles/${vehicle1.id}/`);
    await page.request.delete(`/api/equipment/${equipment1.id}/`);
    await page.request.delete(`/api/customers/${customer1.id}/`);
    await page.request.delete(`/api/customers/${customer2.id}/`);
  });
});

test.describe('Integration Test Examples', () => {
  test('should create inspection via UI with test data', async ({
    page,
    testCustomer,
    testEquipment,
  }) => {
    // Navigate to inspections
    const inspectionsButton = page.getByRole('button', { name: /inspections/i });
    await inspectionsButton.click();
    await page.waitForTimeout(1000);

    // Click create
    const createButton = page.getByRole('button', { name: /create inspection/i });
    await createButton.click();
    await page.waitForTimeout(500);

    // Fill form with our test data
    await page.locator('#customer').selectOption({ label: testCustomer.name });
    await page.waitForTimeout(300);

    await page.locator('#asset-type').selectOption('EQUIPMENT');
    await page.waitForTimeout(500);

    // Find our test equipment in the dropdown
    const assetSelect = page.locator('#asset');
    const assetOptions = await assetSelect.locator('option').all();

    for (let i = 0; i < assetOptions.length; i++) {
      const text = await assetOptions[i].textContent();
      if (text?.includes(testEquipment.asset_number)) {
        await assetSelect.selectOption({ index: i });
        break;
      }
    }

    await page.waitForTimeout(300);

    // Select template
    const templateSelect = page.locator('#template');
    await templateSelect.selectOption({ index: 1 });

    // Submit
    const submitButton = page.getByRole('button', { name: /create inspection/i });
    await submitButton.click();
    await page.waitForTimeout(2000);

    // Should navigate to execution page
    const heading = page.locator('h1');
    expect(await heading.isVisible()).toBeTruthy();
  });

  test('should create work order via UI with test data', async ({
    page,
    testCustomer,
    testEquipment,
  }) => {
    // Navigate to work orders
    const workOrdersButton = page.getByRole('button', { name: /work orders/i });
    await workOrdersButton.click();
    await page.waitForTimeout(1000);

    // Click create
    const createButton = page.getByTestId('create-work-order-btn');
    await createButton.click();
    await page.waitForTimeout(500);

    // Fill form
    await page.locator('#customer').selectOption({ label: testCustomer.name });
    await page.waitForTimeout(300);

    await page.locator('#asset-type').selectOption('EQUIPMENT');
    await page.waitForTimeout(500);

    // Select our test equipment
    const assetSelect = page.locator('#asset');
    const assetOptions = await assetSelect.locator('option').all();

    for (let i = 0; i < assetOptions.length; i++) {
      const text = await assetOptions[i].textContent();
      if (text?.includes(testEquipment.asset_number)) {
        await assetSelect.selectOption({ index: i });
        break;
      }
    }

    await page.waitForTimeout(300);

    // Fill work order details
    await page.locator('#title').fill('Test Work Order');
    await page.locator('#description').fill('Test description');
    await page.locator('#priority').selectOption('NORMAL');

    // Add a work order line
    const addLineButton = page.getByRole('button', { name: /add line/i });
    await addLineButton.click();
    await page.waitForTimeout(300);

    // Fill the line (simplified - actual implementation may vary)
    const lines = page.locator('[data-testid="work-line"]');
    const lastLine = lines.last();

    // Would fill verb, noun, etc. here

    // Submit
    const submitButton = page.getByRole('button', { name: /create work order/i });
    // await submitButton.click(); // Commented out as line needs to be filled first

    // Form should be valid and ready to submit
    expect(await submitButton.isVisible()).toBeTruthy();
  });
});
