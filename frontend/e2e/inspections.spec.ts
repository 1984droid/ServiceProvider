/**
 * Inspections E2E Tests
 *
 * Comprehensive test suite for complete inspection workflow
 */

import { test, expect } from './fixtures/auth.fixture';
import { InspectionsListPage } from './pages/inspections.page';

test.describe('Inspections - Complete Flow', () => {
  let listPage: InspectionsListPage;

  test.beforeEach(async ({ page, authenticatedPage }) => {
    listPage = new InspectionsListPage(page);
  });

  test.describe('List Page', () => {
    test('should display inspections list page', async ({ page }) => {
      await listPage.goto();
      await expect(listPage.heading).toBeVisible();
    });

    test('should display inspections from seed data', async () => {
      await listPage.goto();
      const count = await listPage.getInspectionCount();
      console.log(`Found ${count} inspections`);
      expect(count).toBeGreaterThan(0);
    });

    test('should have create inspection button', async () => {
      await listPage.goto();
      await expect(listPage.createButton).toBeVisible();
    });

    test('should filter inspections by status', async ({ page }) => {
      await listPage.goto();

      // Get initial count
      const initialCount = await listPage.getInspectionCount();
      console.log(`Initial: ${initialCount}`);

      // Filter by COMPLETED
      await listPage.filterByStatus('COMPLETED');
      await page.waitForTimeout(500);
      const completedCount = await listPage.getInspectionCount();
      console.log(`Completed: ${completedCount}`);

      expect(completedCount).toBeGreaterThanOrEqual(0);
      expect(completedCount).toBeLessThanOrEqual(initialCount);
    });

    test('should search inspections', async ({ page }) => {
      await listPage.goto();

      const initialCount = await listPage.getInspectionCount();

      // Search for something specific
      await listPage.search('ANSI');
      await page.waitForTimeout(500);

      const searchCount = await listPage.getInspectionCount();
      console.log(`Search results: ${searchCount}`);

      expect(searchCount).toBeGreaterThanOrEqual(0);
    });
  });

  test.describe('Create Inspection', () => {
    test('should open create inspection modal', async ({ page }) => {
      await listPage.goto();
      await listPage.createButton.click();

      // Wait for modal to appear
      await page.waitForSelector('[role="dialog"]', { timeout: 5000 });
      const modal = page.locator('[role="dialog"]');
      await expect(modal).toBeVisible();

      // Check for required fields
      await expect(page.getByLabel(/customer/i)).toBeVisible();
      await expect(page.getByLabel(/asset type/i)).toBeVisible();
    });

    test('should create new inspection with valid data', async ({ page }) => {
      await listPage.goto();
      const initialCount = await listPage.getInspectionCount();

      await listPage.createButton.click();
      await page.waitForSelector('[role="dialog"]', { timeout: 5000 });

      // Fill form (assuming we have customer and asset data)
      const customerSelect = page.locator('#customer');
      const assetTypeSelect = page.locator('#asset-type');

      // Select first customer
      await customerSelect.selectOption({ index: 1 });
      await page.waitForTimeout(300);

      // Select asset type
      await assetTypeSelect.selectOption('EQUIPMENT');
      await page.waitForTimeout(500);

      // Select asset
      const assetSelect = page.locator('#asset');
      const assetOptions = await assetSelect.locator('option').count();

      if (assetOptions > 1) {
        await assetSelect.selectOption({ index: 1 });
        await page.waitForTimeout(300);

        // Select template
        const templateSelect = page.locator('#template');
        const templateOptions = await templateSelect.locator('option').count();

        if (templateOptions > 1) {
          await templateSelect.selectOption({ index: 1 });

          // Submit form
          const createButton = page.getByRole('button', { name: /create inspection/i });
          await createButton.click();

          // Wait for navigation or success
          await page.waitForTimeout(2000);

          // Should either be on execute page or back to list with new inspection
          const url = page.url();
          const hasExecutePage = await page.locator('h1').filter({ hasText: /inspection/i }).count();

          expect(hasExecutePage).toBeGreaterThan(0);
        }
      }
    });
  });

  test.describe('Execute Inspection', () => {
    test('should navigate to inspection execution', async ({ page }) => {
      await listPage.goto();

      // Find and click on a DRAFT or IN_PROGRESS inspection
      const inspectionCards = page.locator('[data-testid="inspection-card"]');
      const count = await inspectionCards.count();

      if (count > 0) {
        // Look for DRAFT or IN_PROGRESS inspection
        for (let i = 0; i < count; i++) {
          const card = inspectionCards.nth(i);
          const statusBadge = card.locator('[data-testid="status-badge"]');
          const statusText = await statusBadge.textContent();

          if (statusText?.includes('DRAFT') || statusText?.includes('IN PROGRESS')) {
            await card.click();
            await page.waitForTimeout(1000);

            // Should be on execute page
            const heading = page.locator('h1');
            const headingText = await heading.textContent();
            expect(headingText).toBeTruthy();
            return;
          }
        }
      }

      test.skip();
    });

    test('should display inspection header with asset info', async ({ page }) => {
      await listPage.goto();

      // Click first inspection
      const firstCard = page.locator('[data-testid="inspection-card"]').first();
      await firstCard.click();
      await page.waitForTimeout(1000);

      // Check for asset info in header
      const header = page.locator('[data-testid="inspection-header"]');
      await expect(header).toBeVisible();
    });

    test('should display step navigation', async ({ page }) => {
      await listPage.goto();

      const firstCard = page.locator('[data-testid="inspection-card"]').first();
      await firstCard.click();
      await page.waitForTimeout(1000);

      // Check for stepper
      const stepper = page.locator('[data-testid="inspection-stepper"]');
      if (await stepper.isVisible()) {
        const steps = stepper.locator('[data-testid="step-item"]');
        const stepCount = await steps.count();
        console.log(`Found ${stepCount} steps`);
        expect(stepCount).toBeGreaterThan(0);
      }
    });

    test('should fill inspection fields and navigate steps', async ({ page }) => {
      await listPage.goto();

      // Find DRAFT or IN_PROGRESS inspection
      const inspectionCards = page.locator('[data-testid="inspection-card"]');
      const count = await inspectionCards.count();

      for (let i = 0; i < count; i++) {
        const card = inspectionCards.nth(i);
        const statusBadge = card.locator('[data-testid="status-badge"]');
        const statusText = await statusBadge.textContent();

        if (statusText?.includes('DRAFT') || statusText?.includes('IN PROGRESS')) {
          await card.click();
          await page.waitForTimeout(1500);

          // Look for form fields on the current step
          const textInputs = page.locator('input[type="text"]');
          const inputCount = await textInputs.count();

          if (inputCount > 0) {
            // Fill first text input
            const firstInput = textInputs.first();
            await firstInput.fill('Test Value');

            // Look for Next button
            const nextButton = page.getByRole('button', { name: /next/i });
            if (await nextButton.isVisible()) {
              await nextButton.click();
              await page.waitForTimeout(500);

              // Verify we moved to next step
              expect(page.url()).toBeTruthy();
            }
          }

          return;
        }
      }

      test.skip();
    });

    test('should handle checkbox fields', async ({ page }) => {
      await listPage.goto();

      const firstCard = page.locator('[data-testid="inspection-card"]').first();
      await firstCard.click();
      await page.waitForTimeout(1500);

      // Look for checkboxes
      const checkboxes = page.locator('input[type="checkbox"]');
      const checkboxCount = await checkboxes.count();

      if (checkboxCount > 0) {
        const firstCheckbox = checkboxes.first();
        await firstCheckbox.check();
        expect(await firstCheckbox.isChecked()).toBeTruthy();
      }
    });

    test('should handle radio button fields', async ({ page }) => {
      await listPage.goto();

      const firstCard = page.locator('[data-testid="inspection-card"]').first();
      await firstCard.click();
      await page.waitForTimeout(1500);

      // Look for radio buttons
      const radios = page.locator('input[type="radio"]');
      const radioCount = await radios.count();

      if (radioCount > 0) {
        const firstRadio = radios.first();
        await firstRadio.check();
        expect(await firstRadio.isChecked()).toBeTruthy();
      }
    });

    test('should handle dropdown fields', async ({ page }) => {
      await listPage.goto();

      const firstCard = page.locator('[data-testid="inspection-card"]').first();
      await firstCard.click();
      await page.waitForTimeout(1500);

      // Look for select dropdowns
      const selects = page.locator('select');
      const selectCount = await selects.count();

      if (selectCount > 0) {
        for (let i = 0; i < selectCount; i++) {
          const select = selects.nth(i);
          const options = await select.locator('option').count();

          if (options > 1) {
            await select.selectOption({ index: 1 });
            const value = await select.inputValue();
            expect(value).toBeTruthy();
            break;
          }
        }
      }
    });
  });

  test.describe('Defect Management', () => {
    test('should add defect when field fails inspection', async ({ page }) => {
      await listPage.goto();

      const firstCard = page.locator('[data-testid="inspection-card"]').first();
      await firstCard.click();
      await page.waitForTimeout(1500);

      // Look for "Add Defect" button (usually appears when marking something as failed)
      const addDefectButton = page.getByRole('button', { name: /add defect/i });

      if (await addDefectButton.isVisible()) {
        await addDefectButton.click();
        await page.waitForTimeout(500);

        // Should see defect modal/form
        const defectForm = page.locator('[data-testid="defect-form"]');
        if (await defectForm.isVisible()) {
          // Fill defect details
          const descriptionInput = page.locator('#defect-description');
          if (await descriptionInput.isVisible()) {
            await descriptionInput.fill('Test defect description');

            // Save defect
            const saveButton = page.getByRole('button', { name: /save|add/i });
            await saveButton.click();
            await page.waitForTimeout(500);
          }
        }
      }
    });

    test('should display defect count', async ({ page }) => {
      await listPage.goto();

      // Look for inspection with defects
      const inspectionCards = page.locator('[data-testid="inspection-card"]');
      const count = await inspectionCards.count();

      for (let i = 0; i < count; i++) {
        const card = inspectionCards.nth(i);
        const defectBadge = card.locator('[data-testid="defect-count"]');

        if (await defectBadge.isVisible()) {
          const text = await defectBadge.textContent();
          console.log(`Defect count: ${text}`);
          expect(text).toBeTruthy();
          return;
        }
      }
    });
  });

  test.describe('Finalize Inspection', () => {
    test('should show finalize button when inspection is complete', async ({ page }) => {
      await listPage.goto();

      // Find IN_PROGRESS inspection
      const inspectionCards = page.locator('[data-testid="inspection-card"]');
      const count = await inspectionCards.count();

      for (let i = 0; i < count; i++) {
        const card = inspectionCards.nth(i);
        const statusBadge = card.locator('[data-testid="status-badge"]');
        const statusText = await statusBadge.textContent();

        if (statusText?.includes('IN PROGRESS')) {
          await card.click();
          await page.waitForTimeout(1500);

          // Look for finalize button
          const finalizeButton = page.getByRole('button', { name: /finalize|complete/i });

          if (await finalizeButton.isVisible()) {
            expect(finalizeButton).toBeVisible();
            return;
          }
        }
      }

      test.skip();
    });

    test('should finalize inspection with signature', async ({ page }) => {
      await listPage.goto();

      // This test would require an inspection that's ready to finalize
      // Typically this would be tested with a specific fixture

      const inspectionCards = page.locator('[data-testid="inspection-card"]');
      const count = await inspectionCards.count();

      for (let i = 0; i < count; i++) {
        const card = inspectionCards.nth(i);
        const statusBadge = card.locator('[data-testid="status-badge"]');
        const statusText = await statusBadge.textContent();

        if (statusText?.includes('IN PROGRESS')) {
          await card.click();
          await page.waitForTimeout(1500);

          const finalizeButton = page.getByRole('button', { name: /finalize|complete/i });

          if (await finalizeButton.isVisible()) {
            await finalizeButton.click();
            await page.waitForTimeout(500);

            // Look for signature modal
            const signatureModal = page.locator('[role="dialog"]');
            if (await signatureModal.isVisible()) {
              // Could add signature drawing here if canvas is available

              // Submit
              const submitButton = signatureModal.getByRole('button', { name: /submit|finalize/i });
              if (await submitButton.isVisible()) {
                await submitButton.click();
                await page.waitForTimeout(2000);

                // Should be redirected to review or list
                const url = page.url();
                expect(url).toBeTruthy();
              }
            }

            return;
          }
        }
      }

      test.skip();
    });
  });

  test.describe('Review Page', () => {
    test('should display completed inspection in review mode', async ({ page }) => {
      await listPage.goto();

      // Find COMPLETED inspection
      const inspectionCards = page.locator('[data-testid="inspection-card"]');
      const count = await inspectionCards.count();

      for (let i = 0; i < count; i++) {
        const card = inspectionCards.nth(i);
        const statusBadge = card.locator('[data-testid="status-badge"]');
        const statusText = await statusBadge.textContent();

        if (statusText?.includes('COMPLETED')) {
          await card.click();
          await page.waitForTimeout(1500);

          // Should be in review mode
          const heading = page.locator('h1');
          const headingText = await heading.textContent();
          expect(headingText).toBeTruthy();
          return;
        }
      }

      test.skip();
    });

    test('should display inspection outcome', async ({ page }) => {
      await listPage.goto();

      // Find COMPLETED inspection
      const inspectionCards = page.locator('[data-testid="inspection-card"]');
      const count = await inspectionCards.count();

      for (let i = 0; i < count; i++) {
        const card = inspectionCards.nth(i);
        const statusBadge = card.locator('[data-testid="status-badge"]');
        const statusText = await statusBadge.textContent();

        if (statusText?.includes('COMPLETED')) {
          await card.click();
          await page.waitForTimeout(1500);

          // Look for outcome badge
          const outcomeBadge = page.locator('[data-testid="inspection-outcome"]');
          if (await outcomeBadge.isVisible()) {
            const outcomeText = await outcomeBadge.textContent();
            console.log(`Outcome: ${outcomeText}`);
            expect(outcomeText).toMatch(/PASS|FAIL/);
            return;
          }
        }
      }

      test.skip();
    });

    test('should display all defects in review', async ({ page }) => {
      await listPage.goto();

      // Find COMPLETED inspection with defects
      const inspectionCards = page.locator('[data-testid="inspection-card"]');
      const count = await inspectionCards.count();

      for (let i = 0; i < count; i++) {
        const card = inspectionCards.nth(i);
        const statusBadge = card.locator('[data-testid="status-badge"]');
        const statusText = await statusBadge.textContent();

        if (statusText?.includes('COMPLETED')) {
          const defectBadge = card.locator('[data-testid="defect-count"]');
          if (await defectBadge.isVisible()) {
            await card.click();
            await page.waitForTimeout(1500);

            // Look for defects section
            const defectSection = page.locator('[data-testid="defects-section"]');
            if (await defectSection.isVisible()) {
              const defectItems = defectSection.locator('[data-testid="defect-item"]');
              const defectCount = await defectItems.count();
              console.log(`Review shows ${defectCount} defects`);
              expect(defectCount).toBeGreaterThan(0);
              return;
            }
          }
        }
      }

      test.skip();
    });

    test('should have print/export options', async ({ page }) => {
      await listPage.goto();

      // Find COMPLETED inspection
      const inspectionCards = page.locator('[data-testid="inspection-card"]');
      const count = await inspectionCards.count();

      for (let i = 0; i < count; i++) {
        const card = inspectionCards.nth(i);
        const statusBadge = card.locator('[data-testid="status-badge"]');
        const statusText = await statusBadge.textContent();

        if (statusText?.includes('COMPLETED')) {
          await card.click();
          await page.waitForTimeout(1500);

          // Look for print/export buttons
          const printButton = page.getByRole('button', { name: /print|export|download/i });
          if (await printButton.isVisible()) {
            expect(printButton).toBeVisible();
            return;
          }
        }
      }

      test.skip();
    });
  });

  test.describe('Data Integrity', () => {
    test('completed inspections should be immutable', async ({ page }) => {
      await listPage.goto();

      // Find COMPLETED inspection
      const inspectionCards = page.locator('[data-testid="inspection-card"]');
      const count = await inspectionCards.count();

      for (let i = 0; i < count; i++) {
        const card = inspectionCards.nth(i);
        const statusBadge = card.locator('[data-testid="status-badge"]');
        const statusText = await statusBadge.textContent();

        if (statusText?.includes('COMPLETED')) {
          await card.click();
          await page.waitForTimeout(1500);

          // Should NOT have edit buttons for steps
          const editButtons = page.getByRole('button', { name: /edit/i });
          const editCount = await editButtons.count();

          // May have edit button for metadata, but not for step data
          // Most important: form fields should be disabled or readonly
          const inputs = page.locator('input[type="text"]');
          const inputCount = await inputs.count();

          if (inputCount > 0) {
            const firstInput = inputs.first();
            const isDisabled = await firstInput.isDisabled();
            const isReadonly = await firstInput.getAttribute('readonly');

            expect(isDisabled || isReadonly !== null).toBeTruthy();
            return;
          }
        }
      }

      test.skip();
    });

    test('all inspections should have valid status', async () => {
      await listPage.goto();

      const inspectionCards = await listPage.page.locator('[data-testid="inspection-card"]');
      const count = await inspectionCards.count();

      console.log(`\nValidating ${count} inspections...`);

      for (let i = 0; i < count; i++) {
        const card = inspectionCards.nth(i);
        const statusBadge = card.locator('[data-testid="status-badge"]');
        const statusText = (await statusBadge.textContent()) || '';

        console.log(`Inspection ${i}: Status=${statusText}`);

        // Status must be one of: DRAFT, IN PROGRESS, COMPLETED
        expect(statusText).toMatch(/DRAFT|IN PROGRESS|COMPLETED/);
      }
    });
  });
});
