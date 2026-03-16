/**
 * Fixture Verification Tests
 *
 * Verifies that all modular fixtures work correctly by creating data via API
 * and verifying it can be retrieved.
 */

import { test, expect } from './fixtures/test-data.fixture';

test.describe('Fixture Verification', () => {
  test('All fixtures work correctly', async ({
    page,
    authToken,
    testCustomer,
    testEquipment,
    testInspection,
    testWorkOrder,
    testEmployee
  }) => {
    // Verify customer
    expect(testCustomer.id).toBeTruthy();
    const customerResponse = await page.request.get(`/api/customers/${testCustomer.id}/`, {
      headers: { 'Authorization': `Bearer ${authToken}` },
    });
    expect(customerResponse.ok()).toBeTruthy();
    console.log('✅ Customer fixture works');

    // Verify equipment
    expect(testEquipment.id).toBeTruthy();
    const equipmentResponse = await page.request.get(`/api/equipment/${testEquipment.id}/`, {
      headers: { 'Authorization': `Bearer ${authToken}` },
    });
    expect(equipmentResponse.ok()).toBeTruthy();
    console.log('✅ Equipment fixture works');

    // Verify inspection
    expect(testInspection.id).toBeTruthy();
    const inspectionResponse = await page.request.get(`/api/inspections/${testInspection.id}/`, {
      headers: { 'Authorization': `Bearer ${authToken}` },
    });
    expect(inspectionResponse.ok()).toBeTruthy();
    console.log('✅ Inspection fixture works');

    // Verify work order
    expect(testWorkOrder.id).toBeTruthy();
    const workOrderResponse = await page.request.get(`/api/work-orders/${testWorkOrder.id}/`, {
      headers: { 'Authorization': `Bearer ${authToken}` },
    });
    expect(workOrderResponse.ok()).toBeTruthy();
    console.log('✅ Work order fixture works');

    // Verify employee
    expect(testEmployee.id).toBeTruthy();
    const employeeResponse = await page.request.get(`/api/employees/${testEmployee.id}/`, {
      headers: { 'Authorization': `Bearer ${authToken}` },
    });
    expect(employeeResponse.ok()).toBeTruthy();
    console.log('✅ Employee fixture works');

    console.log('\n🎉 ALL FIXTURES WORKING CORRECTLY!\n');
  });
});
