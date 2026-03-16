/**
 * Work Orders Page Object Model
 *
 * Encapsulates interactions with the work orders pages.
 */

import { Page, Locator } from '@playwright/test';

export class WorkOrdersListPage {
  readonly page: Page;
  readonly heading: Locator;
  readonly createButton: Locator;
  readonly searchInput: Locator;
  readonly statusFilter: Locator;
  readonly priorityFilter: Locator;
  readonly workOrderCards: Locator;
  readonly workOrderRows: Locator;

  constructor(page: Page) {
    this.page = page;
    this.heading = page.locator('h1').filter({ hasText: 'Work Orders' });
    this.createButton = page.getByTestId('create-work-order-btn');
    this.searchInput = page.getByTestId('work-order-search');
    this.statusFilter = page.getByTestId('status-filter');
    this.priorityFilter = page.getByTestId('priority-filter');
    this.workOrderCards = page.getByTestId('work-order-card');
    this.workOrderRows = this.workOrderCards; // Same element for this component
  }

  async goto() {
    // App uses state-based routing, so we need to click the nav button
    // instead of using page.goto()
    const workOrdersButton = this.page.getByRole('button', { name: /work orders/i });
    await workOrdersButton.click();
    await this.page.waitForLoadState('networkidle');
    // Wait for either heading or error message to appear
    await this.page.waitForSelector('h1, .text-red-600', { timeout: 10000 }).catch(() => {});
  }

  async getWorkOrderCount(): Promise<number> {
    // Try cards first, then rows
    const cards = await this.workOrderCards.count();
    if (cards > 0) return cards;

    return await this.workOrderRows.count();
  }

  async clickWorkOrder(index: number = 0) {
    const cards = await this.workOrderCards.count();
    if (cards > 0) {
      await this.workOrderCards.nth(index).click();
    } else {
      await this.workOrderRows.nth(index).click();
    }
  }

  async searchFor(query: string) {
    await this.searchInput.fill(query);
    await this.page.waitForTimeout(500); // Debounce
  }

  async filterByStatus(status: string) {
    await this.statusFilter.selectOption(status);
    await this.page.waitForLoadState('networkidle');
  }

  async filterByPriority(priority: string) {
    await this.priorityFilter.selectOption(priority);
    await this.page.waitForLoadState('networkidle');
  }
}

export class WorkOrderDetailPage {
  readonly page: Page;
  readonly workOrderNumber: Locator;
  readonly statusBadge: Locator;
  readonly priorityBadge: Locator;
  readonly approvalStatusBadge: Locator;
  readonly assetInfo: Locator;
  readonly customerInfo: Locator;
  readonly sourceType: Locator;
  readonly description: Locator;
  readonly workItems: Locator;
  readonly requestApprovalButton: Locator;
  readonly approveButton: Locator;
  readonly rejectButton: Locator;
  readonly startWorkButton: Locator;
  readonly completeButton: Locator;
  readonly editButton: Locator;
  readonly deleteButton: Locator;
  readonly backButton: Locator;

  constructor(page: Page) {
    this.page = page;
    this.workOrderNumber = page.locator('[data-testid="work-order-number"]');
    this.statusBadge = page.locator('[data-testid="status-badge"]');
    this.priorityBadge = page.locator('[data-testid="priority-badge"]');
    this.approvalStatusBadge = page.locator('[data-testid="approval-status"]');
    this.assetInfo = page.locator('[data-testid="asset-info"]');
    this.customerInfo = page.locator('[data-testid="customer-info"]');
    this.sourceType = page.locator('[data-testid="source-type"]');
    this.description = page.locator('[data-testid="description"]');
    this.workItems = page.locator('[data-testid="work-item"]');
    this.requestApprovalButton = page.getByRole('button', { name: /request approval/i });
    this.approveButton = page.getByRole('button', { name: /approve/i });
    this.rejectButton = page.getByRole('button', { name: /reject/i });
    this.startWorkButton = page.getByRole('button', { name: /start work/i });
    this.completeButton = page.getByRole('button', { name: /complete/i });
    this.editButton = page.getByRole('button', { name: /edit/i });
    this.deleteButton = page.getByRole('button', { name: /delete/i });
    this.backButton = page.getByRole('button', { name: /back/i });
  }

  async goto(workOrderId: string) {
    await this.page.goto(`/work-orders/${workOrderId}`);
    await this.page.waitForLoadState('networkidle');
  }

  async getWorkOrderNumber(): Promise<string> {
    return await this.workOrderNumber.textContent() || '';
  }

  async getStatus(): Promise<string> {
    return await this.statusBadge.textContent() || '';
  }

  async getPriority(): Promise<string> {
    return await this.priorityBadge.textContent() || '';
  }

  async getApprovalStatus(): Promise<string> {
    return await this.approvalStatusBadge.textContent() || '';
  }

  async getSourceType(): Promise<string> {
    return await this.sourceType.textContent() || '';
  }

  async getWorkItemCount(): Promise<number> {
    return await this.workItems.count();
  }

  async requestApproval() {
    await this.requestApprovalButton.click();
    await this.page.waitForLoadState('networkidle');
  }

  async approve() {
    await this.approveButton.click();
    await this.page.waitForLoadState('networkidle');
  }

  async startWork() {
    await this.startWorkButton.click();
    await this.page.waitForLoadState('networkidle');
  }

  async complete() {
    await this.completeButton.click();
    await this.page.waitForLoadState('networkidle');
  }

  async goBack() {
    await this.backButton.click();
  }
}

export class WorkOrderCreatePage {
  readonly page: Page;
  readonly heading: Locator;
  readonly customerSelect: Locator;
  readonly assetTypeSelect: Locator;
  readonly assetSelect: Locator;
  readonly titleInput: Locator;
  readonly descriptionInput: Locator;
  readonly prioritySelect: Locator;
  readonly sourceTypeSelect: Locator;
  readonly addLineButton: Locator;
  readonly saveButton: Locator;
  readonly cancelButton: Locator;

  constructor(page: Page) {
    this.page = page;
    this.heading = page.getByRole('heading', { name: /create work order/i });
    this.customerSelect = page.locator('#customer');
    this.assetTypeSelect = page.locator('#asset-type');
    this.assetSelect = page.locator('#asset');
    this.titleInput = page.locator('#title');
    this.descriptionInput = page.locator('#description');
    this.prioritySelect = page.locator('#priority');
    this.sourceTypeSelect = page.locator('#source');
    this.addLineButton = page.getByRole('button', { name: /add line/i });
    this.saveButton = page.getByRole('button', { name: /save|create/i });
    this.cancelButton = page.getByRole('button', { name: /cancel/i });
  }

  async goto() {
    // App uses state-based routing, so we need to click the nav button first,
    // then click the create button
    const workOrdersButton = this.page.getByRole('button', { name: /work orders/i });
    await workOrdersButton.click();
    await this.page.waitForLoadState('networkidle');

    const createButton = this.page.getByTestId('create-work-order-btn');
    await createButton.click();
    await this.page.waitForLoadState('networkidle');
  }

  async selectCustomer(customerName: string) {
    await this.customerSelect.selectOption({ label: customerName });
    await this.page.waitForTimeout(300);
  }

  async selectAssetType(type: string) {
    await this.assetTypeSelect.selectOption(type);
    await this.page.waitForTimeout(300);
  }

  async selectAsset(assetLabel: string) {
    await this.assetSelect.selectOption({ label: assetLabel });
  }

  async fillTitle(title: string) {
    await this.titleInput.fill(title);
  }

  async fillDescription(description: string) {
    await this.descriptionInput.fill(description);
  }

  async selectPriority(priority: string) {
    await this.prioritySelect.selectOption(priority);
  }

  async selectSourceType(sourceType: string) {
    await this.sourceTypeSelect.selectOption(sourceType);
  }

  async addWorkLine(verb: string, noun: string, location: string) {
    await this.addLineButton.click();

    // Fill the last added line
    const lines = this.page.locator('[data-testid="work-line"]');
    const lastLine = lines.last();

    await lastLine.getByLabel(/verb/i).fill(verb);
    await lastLine.getByLabel(/noun/i).fill(noun);
    await lastLine.getByLabel(/location/i).selectOption(location);
  }

  async save() {
    await this.saveButton.click();
    await this.page.waitForLoadState('networkidle');
  }

  async cancel() {
    await this.cancelButton.click();
  }
}
