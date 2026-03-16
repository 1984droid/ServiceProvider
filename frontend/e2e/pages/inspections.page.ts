/**
 * Inspections Page Object Model
 *
 * Page objects for inspection list, execution, and review pages
 */

import { Page, Locator } from '@playwright/test';

export class InspectionsListPage {
  readonly page: Page;
  readonly heading: Locator;
  readonly createButton: Locator;
  readonly searchInput: Locator;
  readonly statusFilter: Locator;
  readonly inspectionCards: Locator;

  constructor(page: Page) {
    this.page = page;
    this.heading = page.locator('h1').filter({ hasText: 'Inspections' });
    this.createButton = page.getByRole('button', { name: /create inspection/i });
    this.searchInput = page.getByPlaceholder(/search/i);
    this.statusFilter = page.getByLabel(/status/i).or(page.locator('#status-filter'));
    this.inspectionCards = page.locator('[data-testid="inspection-card"]');
  }

  async goto() {
    // App uses state-based routing, click nav button
    const inspectionsButton = this.page.getByRole('button', { name: /inspections/i });
    await inspectionsButton.click();
    await this.page.waitForLoadState('networkidle');
  }

  async getInspectionCount(): Promise<number> {
    return await this.inspectionCards.count();
  }

  async filterByStatus(status: string) {
    await this.statusFilter.selectOption(status);
  }

  async search(query: string) {
    await this.searchInput.fill(query);
    // Assuming search triggers on input change
    await this.page.waitForTimeout(300);
  }

  async clickInspection(index: number) {
    await this.inspectionCards.nth(index).click();
  }
}

export class InspectionExecutePage {
  readonly page: Page;
  readonly header: Locator;
  readonly stepper: Locator;
  readonly nextButton: Locator;
  readonly previousButton: Locator;
  readonly saveButton: Locator;
  readonly finalizeButton: Locator;
  readonly addDefectButton: Locator;

  constructor(page: Page) {
    this.page = page;
    this.header = page.locator('[data-testid="inspection-header"]');
    this.stepper = page.locator('[data-testid="inspection-stepper"]');
    this.nextButton = page.getByRole('button', { name: /next/i });
    this.previousButton = page.getByRole('button', { name: /previous|back/i });
    this.saveButton = page.getByRole('button', { name: /save/i });
    this.finalizeButton = page.getByRole('button', { name: /finalize|complete/i });
    this.addDefectButton = page.getByRole('button', { name: /add defect/i });
  }

  async fillTextField(label: string, value: string) {
    const field = this.page.getByLabel(label);
    await field.fill(value);
  }

  async selectDropdown(label: string, value: string) {
    const field = this.page.getByLabel(label);
    await field.selectOption(value);
  }

  async checkCheckbox(label: string) {
    const field = this.page.getByLabel(label);
    await field.check();
  }

  async selectRadio(label: string) {
    const field = this.page.getByLabel(label);
    await field.check();
  }

  async goToNextStep() {
    await this.nextButton.click();
    await this.page.waitForLoadState('networkidle');
  }

  async goToPreviousStep() {
    await this.previousButton.click();
    await this.page.waitForLoadState('networkidle');
  }

  async saveInspection() {
    await this.saveButton.click();
    await this.page.waitForTimeout(500);
  }

  async finalizeInspection() {
    await this.finalizeButton.click();
    await this.page.waitForTimeout(500);
  }

  async addDefect(description: string, severity: string) {
    await this.addDefectButton.click();
    await this.page.waitForTimeout(300);

    // Fill defect form
    const descField = this.page.locator('#defect-description');
    if (await descField.isVisible()) {
      await descField.fill(description);
    }

    const severityField = this.page.locator('#defect-severity');
    if (await severityField.isVisible()) {
      await severityField.selectOption(severity);
    }

    // Save defect
    const saveButton = this.page.getByRole('button', { name: /save|add/i }).last();
    await saveButton.click();
    await this.page.waitForTimeout(500);
  }

  async getCurrentStepTitle(): Promise<string> {
    const activeStep = this.page.locator('[data-testid="step-item"][data-active="true"]');
    return await activeStep.textContent() || '';
  }

  async getCompletionPercentage(): Promise<number> {
    const progressBar = this.page.locator('[data-testid="progress-bar"]');
    if (await progressBar.isVisible()) {
      const text = await progressBar.textContent();
      const match = text?.match(/(\d+)%/);
      return match ? parseInt(match[1]) : 0;
    }
    return 0;
  }
}

export class InspectionReviewPage {
  readonly page: Page;
  readonly heading: Locator;
  readonly outcomeBadge: Locator;
  readonly defectsSection: Locator;
  readonly printButton: Locator;
  readonly exportButton: Locator;
  readonly backButton: Locator;

  constructor(page: Page) {
    this.page = page;
    this.heading = page.locator('h1');
    this.outcomeBadge = page.locator('[data-testid="inspection-outcome"]');
    this.defectsSection = page.locator('[data-testid="defects-section"]');
    this.printButton = page.getByRole('button', { name: /print/i });
    this.exportButton = page.getByRole('button', { name: /export|download/i });
    this.backButton = page.getByRole('button', { name: /back/i });
  }

  async getOutcome(): Promise<string> {
    return await this.outcomeBadge.textContent() || '';
  }

  async getDefectCount(): Promise<number> {
    const defectItems = this.defectsSection.locator('[data-testid="defect-item"]');
    return await defectItems.count();
  }

  async goBack() {
    await this.backButton.click();
    await this.page.waitForLoadState('networkidle');
  }

  async print() {
    await this.printButton.click();
  }

  async export() {
    await this.exportButton.click();
  }
}

export class CreateInspectionModal {
  readonly page: Page;
  readonly modal: Locator;
  readonly customerSelect: Locator;
  readonly assetTypeSelect: Locator;
  readonly assetSelect: Locator;
  readonly templateSelect: Locator;
  readonly createButton: Locator;
  readonly cancelButton: Locator;

  constructor(page: Page) {
    this.page = page;
    this.modal = page.locator('[role="dialog"]');
    this.customerSelect = page.locator('#customer');
    this.assetTypeSelect = page.locator('#asset-type');
    this.assetSelect = page.locator('#asset');
    this.templateSelect = page.locator('#template');
    this.createButton = page.getByRole('button', { name: /create inspection/i });
    this.cancelButton = page.getByRole('button', { name: /cancel/i });
  }

  async selectCustomer(customerName: string) {
    await this.customerSelect.selectOption({ label: customerName });
    await this.page.waitForTimeout(300);
  }

  async selectAssetType(type: 'VEHICLE' | 'EQUIPMENT') {
    await this.assetTypeSelect.selectOption(type);
    await this.page.waitForTimeout(500);
  }

  async selectAsset(index: number) {
    await this.assetSelect.selectOption({ index });
    await this.page.waitForTimeout(300);
  }

  async selectTemplate(index: number) {
    await this.templateSelect.selectOption({ index });
  }

  async create() {
    await this.createButton.click();
    await this.page.waitForTimeout(2000);
  }

  async cancel() {
    await this.cancelButton.click();
  }
}
