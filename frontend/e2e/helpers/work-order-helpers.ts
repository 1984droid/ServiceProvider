/**
 * Work Order Helper Functions
 *
 * Reusable functions for common work order operations
 */

import { Page } from '@playwright/test';
import { apiClient } from '../../src/lib/axios';

/**
 * Create a work order via API
 */
export async function createWorkOrderViaAPI(data: {
  customer_id: string;
  asset_type: 'VEHICLE' | 'EQUIPMENT';
  asset_id: string;
  title: string;
  description: string;
  priority?: 'LOW' | 'NORMAL' | 'HIGH' | 'EMERGENCY';
  source_type?: string;
  lines?: Array<{
    verb: string;
    noun: string;
    service_location?: string;
    description?: string;
    estimated_hours?: number;
  }>;
}): Promise<string> {
  const workOrderData = {
    customer: data.customer_id,
    asset_type: data.asset_type,
    asset_id: data.asset_id,
    title: data.title,
    description: data.description,
    priority: data.priority || 'NORMAL',
    source_type: data.source_type || 'MANUAL',
    lines: data.lines || [
      {
        verb: 'Inspect',
        noun: 'Hydraulic System',
        estimated_hours: 2,
      },
    ],
  };

  const response = await apiClient.post('/work-orders/', workOrderData);
  return response.data.id;
}

/**
 * Request approval for a work order
 */
export async function requestApproval(workOrderId: string): Promise<void> {
  await apiClient.post(`/work-orders/${workOrderId}/request_approval/`);
}

/**
 * Approve a work order
 */
export async function approveWorkOrder(
  workOrderId: string,
  employeeId: string
): Promise<void> {
  await apiClient.post(`/work-orders/${workOrderId}/approve/`, {
    approved_by: employeeId,
  });
}

/**
 * Reject a work order
 */
export async function rejectWorkOrder(
  workOrderId: string,
  reason?: string
): Promise<void> {
  await apiClient.post(`/work-orders/${workOrderId}/reject/`, {
    rejected_reason: reason || 'Test rejection',
  });
}

/**
 * Start a work order
 */
export async function startWorkOrder(workOrderId: string): Promise<void> {
  await apiClient.post(`/work-orders/${workOrderId}/start/`);
}

/**
 * Complete a work order
 */
export async function completeWorkOrder(workOrderId: string): Promise<void> {
  await apiClient.post(`/work-orders/${workOrderId}/complete/`);
}

/**
 * Complete a work order line
 */
export async function completeWorkOrderLine(
  lineId: string,
  employeeId: string,
  actualHours?: number
): Promise<void> {
  await apiClient.post(`/work-order-lines/${lineId}/complete/`, {
    completed_by: employeeId,
    actual_hours: actualHours || 2,
  });
}

/**
 * Create work order from inspection defect
 */
export async function createWorkOrderFromDefect(
  defectId: string,
  departmentId?: string,
  autoApprove: boolean = false
): Promise<string> {
  const response = await apiClient.post('/work-orders/from_defect/', {
    defect_id: defectId,
    department_id: departmentId,
    auto_approve: autoApprove,
  });

  return response.data.id;
}

/**
 * Create work orders from all defects in an inspection
 */
export async function createWorkOrdersFromInspection(
  inspectionId: string,
  options?: {
    group_by_location?: boolean;
    min_severity?: 'ADVISORY' | 'MINOR' | 'MAJOR' | 'CRITICAL';
    department_id?: string;
    auto_approve?: boolean;
  }
): Promise<string[]> {
  const response = await apiClient.post('/work-orders/from_inspection/', {
    inspection_id: inspectionId,
    group_by_location: options?.group_by_location ?? true,
    min_severity: options?.min_severity,
    department_id: options?.department_id,
    auto_approve: options?.auto_approve ?? false,
  });

  return response.data.work_orders.map((wo: any) => wo.id);
}

/**
 * Fill work order create form via UI
 */
export async function fillWorkOrderCreateForm(
  page: Page,
  data: {
    customer_name: string;
    asset_type: 'VEHICLE' | 'EQUIPMENT';
    asset_index: number;
    title: string;
    description: string;
    priority: 'LOW' | 'NORMAL' | 'HIGH' | 'EMERGENCY';
    lines: Array<{
      verb: string;
      noun: string;
      location?: string;
      description?: string;
    }>;
  }
): Promise<void> {
  // Select customer
  await page.locator('#customer').selectOption({ label: data.customer_name });
  await page.waitForTimeout(300);

  // Select asset type
  await page.locator('#asset-type').selectOption(data.asset_type);
  await page.waitForTimeout(500);

  // Select asset
  await page.locator('#asset').selectOption({ index: data.asset_index });
  await page.waitForTimeout(300);

  // Fill title
  await page.locator('#title').fill(data.title);

  // Fill description
  await page.locator('#description').fill(data.description);

  // Select priority
  await page.locator('#priority').selectOption(data.priority);

  // Add work order lines
  for (const line of data.lines) {
    // Click add line button
    const addLineButton = page.getByRole('button', { name: /add line/i });
    await addLineButton.click();
    await page.waitForTimeout(300);

    // Get the last added line
    const lines = page.locator('[data-testid="work-line"]');
    const lastLine = lines.last();

    // Fill verb
    const verbSelect = lastLine.locator('select').filter({ hasText: /select verb/i });
    if ((await verbSelect.count()) > 0) {
      await verbSelect.first().selectOption(line.verb);
    }

    // Fill noun
    const nounSelect = lastLine.locator('select').filter({ hasText: /select noun/i });
    if ((await nounSelect.count()) > 0) {
      await nounSelect.first().selectOption(line.noun);
    }

    // Fill location if provided
    if (line.location) {
      const locationSelect = lastLine.locator('select').filter({ hasText: /select location/i });
      if ((await locationSelect.count()) > 0) {
        await locationSelect.first().selectOption(line.location);
      }
    }

    // Fill description if provided
    if (line.description) {
      const descInput = lastLine.locator('input[placeholder*="additional details"]');
      if ((await descInput.count()) > 0) {
        await descInput.first().fill(line.description);
      }
    }
  }
}

/**
 * Submit work order create form
 */
export async function submitWorkOrderCreateForm(page: Page): Promise<void> {
  const createButton = page.getByRole('button', { name: /create work order/i });
  await createButton.click();
  await page.waitForTimeout(2000);
}

/**
 * Get work order status
 */
export async function getWorkOrderStatus(
  workOrderId: string
): Promise<{ status: string; approval_status: string }> {
  const response = await apiClient.get(`/work-orders/${workOrderId}/`);
  return {
    status: response.data.status,
    approval_status: response.data.approval_status,
  };
}

/**
 * Wait for work order to reach specific status
 */
export async function waitForWorkOrderStatus(
  workOrderId: string,
  targetStatus: string,
  maxAttempts: number = 10
): Promise<boolean> {
  for (let i = 0; i < maxAttempts; i++) {
    const { status } = await getWorkOrderStatus(workOrderId);

    if (status === targetStatus) {
      return true;
    }

    await new Promise((resolve) => setTimeout(resolve, 500));
  }

  return false;
}

/**
 * Get all work order lines
 */
export async function getWorkOrderLines(workOrderId: string): Promise<any[]> {
  const response = await apiClient.get(`/work-orders/${workOrderId}/`);
  return response.data.lines || [];
}

/**
 * Create a fully approved work order ready for work
 */
export async function createApprovedWorkOrder(
  customerId: string,
  assetType: 'VEHICLE' | 'EQUIPMENT',
  assetId: string,
  employeeId: string
): Promise<string> {
  // Create work order
  const workOrderId = await createWorkOrderViaAPI({
    customer_id: customerId,
    asset_type: assetType,
    asset_id: assetId,
    title: 'Approved Test Work Order',
    description: 'Test work order for testing',
  });

  // Request approval
  await requestApproval(workOrderId);

  // Approve
  await approveWorkOrder(workOrderId, employeeId);

  return workOrderId;
}
