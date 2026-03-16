/**
 * Work Orders E2E Tests
 *
 * Comprehensive end-to-end tests for work order functionality.
 */

import { test, expect } from './fixtures/auth.fixture';
import { WorkOrdersListPage, WorkOrderDetailPage, WorkOrderCreatePage } from './pages/work-orders.page';

test.describe('Work Orders - List Page', () => {
  let listPage: WorkOrdersListPage;

  test.beforeEach(async ({ page, authenticatedPage }) => {
    listPage = new WorkOrdersListPage(page);
    await listPage.goto();
  });

  test('should display work orders list page', async ({ page }) => {
    await expect(listPage.heading).toBeVisible();
    await expect(listPage.heading).toContainText(/work orders/i);
  });

  test('should display work orders from seed data', async () => {
    const count = await listPage.getWorkOrderCount();
    expect(count).toBeGreaterThan(0);
    console.log(`Found ${count} work orders`);
  });

  test('should have create work order button', async () => {
    await expect(listPage.createButton).toBeVisible();
  });

  test('should filter work orders by status', async ({ page }) => {
    const initialCount = await listPage.getWorkOrderCount();

    // Filter by COMPLETED
    await listPage.filterByStatus('COMPLETED');
    await page.waitForTimeout(500);
    const completedCount = await listPage.getWorkOrderCount();

    console.log(`Initial: ${initialCount}, Completed: ${completedCount}`);
    // Should have fewer or same items after filtering
    expect(completedCount).toBeLessThanOrEqual(initialCount);
  });

  test('should filter work orders by priority', async ({ page }) => {
    const initialCount = await listPage.getWorkOrderCount();

    // Filter by EMERGENCY
    await listPage.filterByPriority('EMERGENCY');
    await page.waitForTimeout(500);
    const emergencyCount = await listPage.getWorkOrderCount();

    console.log(`Initial: ${initialCount}, Emergency: ${emergencyCount}`);
    expect(emergencyCount).toBeLessThanOrEqual(initialCount);
  });

  test('should search work orders', async ({ page }) => {
    // Search for "WO-" to find work order numbers
    await listPage.searchFor('WO-');
    await page.waitForTimeout(500);

    const count = await listPage.getWorkOrderCount();
    expect(count).toBeGreaterThan(0);
  });

  test('should navigate to work order detail on click', async ({ page }) => {
    await listPage.clickWorkOrder(0);

    // Should navigate to detail page
    await page.waitForURL(/\/work-orders\/[^/]+$/);
    expect(page.url()).toContain('/work-orders/');
  });
});

test.describe('Work Orders - Detail Page', () => {
  let listPage: WorkOrdersListPage;
  let detailPage: WorkOrderDetailPage;

  test.beforeEach(async ({ page, authenticatedPage }) => {
    listPage = new WorkOrdersListPage(page);
    detailPage = new WorkOrderDetailPage(page);

    // Navigate to first work order
    await listPage.goto();
    await listPage.clickWorkOrder(0);
    await page.waitForURL(/\/work-orders\/[^/]+$/);
  });

  test('should display work order details', async () => {
    const woNumber = await detailPage.getWorkOrderNumber();
    expect(woNumber).toMatch(/WO-\d{4}-\d+/);

    await expect(detailPage.statusBadge).toBeVisible();
    await expect(detailPage.priorityBadge).toBeVisible();
  });

  test('should display work order number', async () => {
    await expect(detailPage.workOrderNumber).toBeVisible();
    const number = await detailPage.getWorkOrderNumber();
    expect(number).toContain('WO-');
  });

  test('should display status badge', async () => {
    await expect(detailPage.statusBadge).toBeVisible();
    const status = await detailPage.getStatus();
    expect(['DRAFT', 'PENDING', 'IN_PROGRESS', 'COMPLETED', 'CANCELLED']).toContain(status);
  });

  test('should display priority badge', async () => {
    await expect(detailPage.priorityBadge).toBeVisible();
    const priority = await detailPage.getPriority();
    expect(['LOW', 'NORMAL', 'HIGH', 'EMERGENCY']).toContain(priority);
  });

  test('should display approval status', async () => {
    const approvalStatus = await detailPage.getApprovalStatus();
    console.log(`Approval Status: ${approvalStatus}`);
    expect(approvalStatus.length).toBeGreaterThan(0);
  });

  test('should display source type', async () => {
    const sourceType = await detailPage.getSourceType();
    console.log(`Source Type: ${sourceType}`);
    // Should be one of the valid source types
    const validSourceTypes = ['INSPECTION DEFECT', 'MAINTENANCE SCHEDULE', 'CUSTOMER REQUEST', 'BREAKDOWN', 'MANUAL'];
    expect(validSourceTypes.some(type => sourceType.includes(type))).toBeTruthy();
  });

  test('should display asset information', async () => {
    await expect(detailPage.assetInfo).toBeVisible();
  });

  test('should display customer information', async () => {
    await expect(detailPage.customerInfo).toBeVisible();
  });

  test('should display work items/lines', async ({ page }) => {
    // Wait for the page to finish loading (loading spinner should disappear)
    await page.waitForSelector('text=Loading work order...', { state: 'hidden', timeout: 10000 }).catch(() => {
      // If loading text doesn't exist, that's fine - page already loaded
    });

    // Wait for work items section to be visible
    await page.waitForSelector('text=Work Items', { timeout: 5000 });

    const itemCount = await detailPage.getWorkItemCount();
    console.log(`Work Items: ${itemCount}`);
    expect(itemCount).toBeGreaterThan(0);
  });

  test('should NOT show COMPLETED status with DRAFT approval', async () => {
    const status = await detailPage.getStatus();
    const approval = await detailPage.getApprovalStatus();

    console.log(`Status: ${status}, Approval: ${approval}`);

    // If COMPLETED, must NOT be DRAFT approval
    if (status === 'COMPLETED') {
      expect(approval).not.toContain('DRAFT');
      expect(approval).toContain('APPROVED');
    }
  });

  test('should have back button', async () => {
    await expect(detailPage.backButton).toBeVisible();
  });

  test('back button should navigate to list', async ({ page }) => {
    await detailPage.goBack();
    // App uses state-based routing, so check for list page content instead of URL
    await page.waitForSelector('h1:has-text("Work Orders")', { timeout: 5000 });
    // Should see the list page heading
    const heading = await page.locator('h1').filter({ hasText: 'Work Orders' });
    await expect(heading).toBeVisible();
    // Should see work order cards (not detail page)
    const cards = await page.locator('[data-testid="work-order-card"]').count();
    expect(cards).toBeGreaterThan(0);
  });
});

test.describe('Work Orders - Workflow Actions', () => {
  let listPage: WorkOrdersListPage;
  let detailPage: WorkOrderDetailPage;

  test.beforeEach(async ({ page, authenticatedPage }) => {
    listPage = new WorkOrdersListPage(page);
    detailPage = new WorkOrderDetailPage(page);
    await listPage.goto();
  });

  test('PENDING_APPROVAL work order should have approve button', async ({ page }) => {
    // Navigate to list
    await listPage.goto();

    // Look for PENDING_APPROVAL work order
    const count = await listPage.getWorkOrderCount();
    for (let i = 0; i < count; i++) {
      await listPage.clickWorkOrder(i);
      await page.waitForURL(/\/work-orders\/[^/]+$/);

      const approval = await detailPage.getApprovalStatus();
      console.log(`WO ${i}: Approval = ${approval}`);

      if (approval.includes('PENDING')) {
        // Should have approve button
        await expect(detailPage.approveButton).toBeVisible();
        return; // Test passed
      }

      // Go back to list for next iteration
      await listPage.goto();
    }

    test.skip(); // Skip if no PENDING_APPROVAL found
  });

  test('DRAFT work order should have Request Approval button', async ({ page }) => {
    // Look for DRAFT work order
    const count = await listPage.getWorkOrderCount();
    for (let i = 0; i < count; i++) {
      await listPage.clickWorkOrder(i);
      await page.waitForURL(/\/work-orders\/[^/]+$/);

      const status = await detailPage.getStatus();
      const approval = await detailPage.getApprovalStatus();

      console.log(`WO ${i}: Status = ${status}, Approval = ${approval}`);

      if (approval.includes('DRAFT')) {
        // Should have request approval button
        await expect(detailPage.requestApprovalButton).toBeVisible();
        return; // Test passed
      }

      await listPage.goto();
    }

    test.skip(); // Skip if no DRAFT found
  });

  test('APPROVED work order should have Start Work button', async ({ page }) => {
    const count = await listPage.getWorkOrderCount();
    for (let i = 0; i < count; i++) {
      await listPage.clickWorkOrder(i);
      await page.waitForURL(/\/work-orders\/[^/]+$/);

      const status = await detailPage.getStatus();
      const approval = await detailPage.getApprovalStatus();

      console.log(`WO ${i}: Status = ${status}, Approval = ${approval}`);

      if (status === 'PENDING' && approval.includes('APPROVED')) {
        // Should have start work button
        await expect(detailPage.startWorkButton).toBeVisible();
        return;
      }

      await listPage.goto();
    }

    test.skip();
  });

  test('IN_PROGRESS work order should have Complete button', async ({ page }) => {
    const count = await listPage.getWorkOrderCount();
    for (let i = 0; i < count; i++) {
      await listPage.clickWorkOrder(i);
      await page.waitForURL(/\/work-orders\/[^/]+$/);

      const status = await detailPage.getStatus();
      console.log(`WO ${i}: Status = ${status}`);

      if (status === 'IN_PROGRESS') {
        await expect(detailPage.completeButton).toBeVisible();
        return;
      }

      await listPage.goto();
    }

    test.skip();
  });
});

test.describe('Work Orders - Create Flow', () => {
  let createPage: WorkOrderCreatePage;

  test.beforeEach(async ({ page, authenticatedPage }) => {
    createPage = new WorkOrderCreatePage(page);
  });

  test('should navigate to create page', async ({ page }) => {
    const listPage = new WorkOrdersListPage(page);
    await listPage.goto();

    await listPage.createButton.click();
    // App uses state-based routing, so check for page content instead of URL
    await page.waitForSelector('h1:has-text("Create Work Order")', { timeout: 5000 });

    await expect(createPage.heading).toBeVisible();
  });

  test('create page should have all required fields', async () => {
    await createPage.goto();

    await expect(createPage.customerSelect).toBeVisible();
    await expect(createPage.assetTypeSelect).toBeVisible();
    await expect(createPage.titleInput).toBeVisible();
    await expect(createPage.descriptionInput).toBeVisible();
    await expect(createPage.prioritySelect).toBeVisible();
    await expect(createPage.saveButton).toBeVisible();
    await expect(createPage.cancelButton).toBeVisible();
  });

  test('should be able to select customer', async () => {
    await createPage.goto();

    await createPage.selectCustomer('Midwest Express Logistics');
    // Asset type should now be available
    await expect(createPage.assetTypeSelect).toBeEnabled();
  });

  test('should cascade customer -> asset type -> asset', async ({ page }) => {
    await createPage.goto();

    // Select customer
    await createPage.selectCustomer('Midwest Express Logistics');

    // Select asset type
    await createPage.selectAssetType('EQUIPMENT');

    // Asset dropdown should be populated
    await expect(createPage.assetSelect).toBeEnabled();
  });

  test.skip('should create a new work order', async ({ page }) => {
    await createPage.goto();

    // Fill form
    await createPage.selectCustomer('Midwest Express Logistics');
    await createPage.selectAssetType('EQUIPMENT');
    // Wait for assets to load
    await page.waitForTimeout(500);

    await createPage.fillTitle('Test Work Order');
    await createPage.fillDescription('This is a test work order');
    await createPage.selectPriority('NORMAL');
    await createPage.selectSourceType('MANUAL');

    // Add a work line
    await createPage.addWorkLine('Inspect', 'Hydraulic System', 'BOOM');

    // Save
    await createPage.save();

    // Should redirect to detail page
    await page.waitForURL(/\/work-orders\/[^/]+$/);
    expect(page.url()).toContain('/work-orders/');
  });
});

test.describe('Work Orders - Data Integrity', () => {
  test('all work orders should have consistent status/approval combinations', async ({ page, authenticatedPage }) => {
    const listPage = new WorkOrdersListPage(page);
    const detailPage = new WorkOrderDetailPage(page);

    await listPage.goto();
    const count = await listPage.getWorkOrderCount();

    const issues: string[] = [];

    for (let i = 0; i < count; i++) {
      await listPage.clickWorkOrder(i);
      await page.waitForURL(/\/work-orders\/[^/]+$/);

      const woNumber = await detailPage.getWorkOrderNumber();
      const status = await detailPage.getStatus();
      const approval = await detailPage.getApprovalStatus();

      console.log(`${woNumber}: Status=${status}, Approval=${approval}`);

      // Check for contradictions
      if (status === 'COMPLETED' && approval.includes('DRAFT')) {
        issues.push(`${woNumber}: COMPLETED with DRAFT approval`);
      }

      if (status === 'COMPLETED' && approval.includes('PENDING')) {
        issues.push(`${woNumber}: COMPLETED with PENDING approval`);
      }

      if (status === 'IN_PROGRESS' && approval.includes('DRAFT')) {
        issues.push(`${woNumber}: IN_PROGRESS with DRAFT approval`);
      }

      await listPage.goto();
    }

    // Report all issues
    if (issues.length > 0) {
      console.error('Data integrity issues found:');
      issues.forEach(issue => console.error(`  - ${issue}`));
    }

    expect(issues).toHaveLength(0);
  });
});
