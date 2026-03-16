/**
 * Test Data Fixtures - Working Implementation
 *
 * Modular fixtures that create test data without relying on seed data.
 * Extends auth fixture to ensure API calls are authenticated.
 */

import { test as authTest } from './auth.fixture';
import { Page } from '@playwright/test';

// Type definitions
export interface TestCustomer {
  id: string;
  name: string;
  cleanup: () => Promise<void>;
}

export interface TestVehicle {
  id: string;
  vin: string;
  customer_id: string;
  unit_number: string;
  cleanup: () => Promise<void>;
}

export interface TestEquipment {
  id: string;
  serial_number: string;
  customer_id: string;
  asset_number: string;
  cleanup: () => Promise<void>;
}

export interface TestInspection {
  id: string;
  asset_type: 'VEHICLE' | 'EQUIPMENT';
  asset_id: string;
  customer_id: string;
  template_key: string;
  status: string;
  cleanup: () => Promise<void>;
}

export interface TestWorkOrder {
  id: string;
  work_order_number: string;
  customer_id: string;
  asset_type: 'VEHICLE' | 'EQUIPMENT';
  asset_id: string;
  status: string;
  approval_status: string;
  cleanup: () => Promise<void>;
}

export interface TestEmployee {
  id: string;
  first_name: string;
  last_name: string;
  email: string;
  cleanup: () => Promise<void>;
}

// Extend auth test with data fixtures
interface TestDataFixtures {
  testCustomer: TestCustomer;
  testVehicle: TestVehicle;
  testEquipment: TestEquipment;
  testInspection: TestInspection;
  testWorkOrder: TestWorkOrder;
  testEmployee: TestEmployee;
}

export const test = authTest.extend<TestDataFixtures>({
  /**
   * Create test customer
   */
  testCustomer: async ({ page, authenticatedPage, authToken }, use) => {
    const timestamp = Date.now();
    const customerData = {
      name: `Test Customer ${timestamp}`,
      legal_name: `Test Customer LLC ${timestamp}`,
      address_line1: '123 Test St',
      city: 'Test City',
      state: 'CA',
      postal_code: '12345',
      country: 'US', // ISO 2-letter country code
    };

    let customerId: string | null = null;

    try {
      const response = await page.request.post('/api/customers/', {
        data: customerData,
        headers: {
          'Authorization': `Bearer ${authToken}`,
        },
      });

      const data = await response.json();
      customerId = data.id;

      const customer: TestCustomer = {
        id: customerId,
        name: customerData.name,
        cleanup: async () => {
          if (customerId) {
            try {
              await page.request.delete(`/api/customers/${customerId}/`, {
                headers: {
                  'Authorization': `Bearer ${authToken}`,
                },
              });
            } catch (e) {
              console.log(`Failed to cleanup customer ${customerId}`);
            }
          }
        },
      };

      await use(customer);
      await customer.cleanup();
    } catch (error) {
      console.error('Failed to create test customer:', error);
      throw error;
    }
  },

  /**
   * Create test vehicle (requires testCustomer)
   */
  testVehicle: async ({ page, testCustomer, authToken }, use) => {
    const timestamp = Date.now();
    const vin = `1HGBH41JXMN${String(timestamp).slice(-6)}`;
    const vehicleData = {
      customer: testCustomer.id,
      vin: vin,
      unit_number: `UNIT-${timestamp}`,
      year: 2020,
      make: 'Test Make',
      model: 'Test Model',
      body_type: 'UTILITY',
      capabilities: ['UTILITY_TRUCK'],
    };

    let vehicleId: string | null = null;

    try {
      const response = await page.request.post('/api/vehicles/', {
        data: vehicleData,
        headers: {
          'Authorization': `Bearer ${authToken}`,
        },
      });
      const data = await response.json();
      vehicleId = data.id;

      const vehicle: TestVehicle = {
        id: vehicleId,
        vin: vin,
        customer_id: testCustomer.id,
        unit_number: vehicleData.unit_number,
        cleanup: async () => {
          if (vehicleId) {
            try {
              await page.request.delete(`/api/vehicles/${vehicleId}/`, {
                headers: {
                  'Authorization': `Bearer ${authToken}`,
                },
              });
            } catch (e) {
              console.log(`Failed to cleanup vehicle ${vehicleId}`);
            }
          }
        },
      };

      await use(vehicle);
      await vehicle.cleanup();
    } catch (error) {
      console.error('Failed to create test vehicle:', error);
      throw error;
    }
  },

  /**
   * Create test equipment (requires testCustomer)
   */
  testEquipment: async ({ page, testCustomer, authToken }, use) => {
    const timestamp = Date.now();
    const equipmentData = {
      customer: testCustomer.id,
      serial_number: `SN-${timestamp}`,
      asset_number: `ASSET-${timestamp}`,
      manufacturer: 'Test Manufacturer',
      model: 'Test Equipment Model',
      equipment_type: 'A92_2_AERIAL', // Valid: Aerial Device (ANSI A92.2)
      year: 2020,
      capabilities: ['HYDRAULIC', 'ELECTRIC'], // Valid capabilities
    };

    let equipmentId: string | null = null;

    try {
      const response = await page.request.post('/api/equipment/', {
        data: equipmentData,
        headers: {
          'Authorization': `Bearer ${authToken}`,
        },
      });

      const data = await response.json();
      equipmentId = data.id;

      const equipment: TestEquipment = {
        id: equipmentId,
        serial_number: equipmentData.serial_number,
        customer_id: testCustomer.id,
        asset_number: equipmentData.asset_number,
        cleanup: async () => {
          if (equipmentId) {
            try {
              await page.request.delete(`/api/equipment/${equipmentId}/`, {
                headers: {
                  'Authorization': `Bearer ${authToken}`,
                },
              });
            } catch (e) {
              console.log(`Failed to cleanup equipment ${equipmentId}`);
            }
          }
        },
      };

      await use(equipment);
      await equipment.cleanup();
    } catch (error) {
      console.error('Failed to create test equipment:', error);
      throw error;
    }
  },

  /**
   * Create test inspection (requires testCustomer and testEquipment)
   */
  testInspection: async ({ page, testCustomer, testEquipment, authToken }, use) => {
    const inspectionData = {
      template_key: 'ansi_a92_2_frequent_inspection', // Valid template key format
      asset_type: 'EQUIPMENT' as const,
      asset_id: testEquipment.id,
      inspector_name: 'Test Inspector',
    };

    let inspectionId: string | null = null;

    try {
      const response = await page.request.post('/api/inspections/', {
        data: inspectionData,
        headers: {
          'Authorization': `Bearer ${authToken}`,
        },
      });

      if (!response.ok()) {
        const errorText = await response.text();
        throw new Error(`Failed to create inspection: ${response.status()} ${errorText}`);
      }

      const data = await response.json();
      inspectionId = data.id;

      const inspection: TestInspection = {
        id: inspectionId,
        asset_type: inspectionData.asset_type,
        asset_id: testEquipment.id,
        customer_id: testCustomer.id,
        template_key: inspectionData.template_key,
        status: 'DRAFT',
        cleanup: async () => {
          if (inspectionId) {
            try {
              await page.request.delete(`/api/inspections/${inspectionId}/`, {
                headers: {
                  'Authorization': `Bearer ${authToken}`,
                },
              });
            } catch (e) {
              console.log(`Failed to cleanup inspection ${inspectionId}`);
            }
          }
        },
      };

      await use(inspection);
      await inspection.cleanup();
    } catch (error) {
      console.error('Failed to create test inspection:', error);
      throw error;
    }
  },

  /**
   * Create test work order (requires testCustomer and testEquipment)
   */
  testWorkOrder: async ({ page, testCustomer, testEquipment, authToken }, use) => {
    const workOrderData = {
      customer: testCustomer.id,
      asset_type: 'EQUIPMENT' as const,
      asset_id: testEquipment.id,
      title: 'Test Work Order',
      description: 'Test work order description',
      priority: 'NORMAL' as const,
      source_type: 'MANUAL' as const,
      lines: [
        {
          verb: 'Inspect',
          noun: 'Hydraulic System',
          service_location: 'Boom',
          estimated_hours: 2,
        },
      ],
    };

    let workOrderId: string | null = null;

    try {
      const response = await page.request.post('/api/work-orders/', {
        data: workOrderData,
        headers: {
          'Authorization': `Bearer ${authToken}`,
        },
      });

      if (!response.ok()) {
        const errorText = await response.text();
        throw new Error(`Failed to create work order: ${response.status()} ${errorText}`);
      }

      const data = await response.json();
      workOrderId = data.id;

      const workOrder: TestWorkOrder = {
        id: workOrderId,
        work_order_number: data.work_order_number,
        customer_id: testCustomer.id,
        asset_type: data.asset_type,
        asset_id: testEquipment.id,
        status: data.status,
        approval_status: data.approval_status,
        cleanup: async () => {
          if (workOrderId) {
            try {
              await page.request.delete(`/api/work-orders/${workOrderId}/`, {
                headers: {
                  'Authorization': `Bearer ${authToken}`,
                },
              });
            } catch (e) {
              console.log(`Failed to cleanup work order ${workOrderId}`);
            }
          }
        },
      };

      await use(workOrder);
      await workOrder.cleanup();
    } catch (error) {
      console.error('Failed to create test work order:', error);
      throw error;
    }
  },

  /**
   * Create test employee
   */
  testEmployee: async ({ page, authenticatedPage, authToken }, use) => {
    const timestamp = Date.now();

    // First, get or create a department (base_department is required)
    const departmentsResponse = await page.request.get('/api/departments/?limit=1', {
      headers: {
        'Authorization': `Bearer ${authToken}`,
      },
    });

    let departmentId: string;
    if (departmentsResponse.ok()) {
      const departmentsData = await departmentsResponse.json();
      if (departmentsData.results && departmentsData.results.length > 0) {
        departmentId = departmentsData.results[0].id;
      } else {
        // Create a test department
        const deptResponse = await page.request.post('/api/departments/', {
          data: {
            name: `Test Department ${timestamp}`,
            code: `TEST${timestamp}`,
          },
          headers: {
            'Authorization': `Bearer ${authToken}`,
          },
        });
        const deptData = await deptResponse.json();
        departmentId = deptData.id;
      }
    } else {
      throw new Error('Failed to fetch or create department');
    }

    const employeeData = {
      first_name: 'Test',
      last_name: `Employee${timestamp}`,
      email: `test.employee.${timestamp}@example.com`,
      employee_number: `EMP-${timestamp}`,
      role: 'TECHNICIAN',
      is_active: true,
      base_department: departmentId, // Required field
    };

    let employeeId: string | null = null;

    try {
      const response = await page.request.post('/api/employees/', {
        data: employeeData,
        headers: {
          'Authorization': `Bearer ${authToken}`,
        },
      });

      if (!response.ok()) {
        const errorText = await response.text();
        console.error('Employee API Error:', errorText);
        throw new Error(`Failed to create employee: ${response.status()} ${errorText}`);
      }

      const data = await response.json();
      employeeId = data.id;

      const employee: TestEmployee = {
        id: employeeId,
        first_name: employeeData.first_name,
        last_name: employeeData.last_name,
        email: employeeData.email,
        cleanup: async () => {
          if (employeeId) {
            try {
              await page.request.delete(`/api/employees/${employeeId}/`, {
                headers: {
                  'Authorization': `Bearer ${authToken}`,
                },
              });
            } catch (e) {
              console.log(`Failed to cleanup employee ${employeeId}`);
            }
          }
        },
      };

      await use(employee);
      await employee.cleanup();
    } catch (error) {
      console.error('Failed to create test employee:', error);
      throw error;
    }
  },
});

export { expect } from '@playwright/test';
