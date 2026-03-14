/**
 * Playwright E2E tests for Customer Detail Page
 *
 * Tests:
 * - Customer detail page loads correctly
 * - All tabs display correct data
 * - Navigation works properly
 */

const { test, expect } = require('@playwright/test');

const BASE_URL = 'http://localhost:5174';
const API_BASE = 'http://localhost:8001';

test.describe('Customer Detail Page', () => {
  let customerId;

  test.beforeEach(async ({ page, request }) => {
    // Login first
    await page.goto(BASE_URL);
    await page.fill('input[type="text"]', 'admin');
    await page.fill('input[type="password"]', 'admin');
    await page.click('button:has-text("Sign In")');
    await page.waitForLoadState('networkidle');

    // Get the first customer from the list
    const response = await request.get(`${API_BASE}/api/customers/`, {
      headers: {
        'Authorization': `Bearer ${await page.evaluate(() => localStorage.getItem('access_token'))}`
      }
    });
    const data = await response.json();
    if (data.results && data.results.length > 0) {
      customerId = data.results[0].id;
    } else {
      throw new Error('No customers found. Please seed the database first.');
    }
  });

  test('should load customer detail page with correct header', async ({ page }) => {
    // Navigate to customers list
    await page.click('button:has-text("Customers")');
    await page.waitForTimeout(500);

    // Click first customer row to go to detail
    const firstRow = page.locator('tbody tr').first();
    await firstRow.click();
    await page.waitForTimeout(1000);

    // Verify we're on the detail page
    await expect(page.locator('h1')).toBeVisible();

    // Verify back button exists
    await expect(page.locator('button[title="Back to customers"]')).toBeVisible();

    // Verify status badge exists
    await expect(page.locator('text=Active, text=Inactive').first()).toBeVisible();
  });

  test('should display all tab options', async ({ page }) => {
    // Navigate to detail page
    await page.click('button:has-text("Customers")');
    await page.waitForTimeout(500);
    await page.locator('tbody tr').first().click();
    await page.waitForTimeout(1000);

    // Verify all tabs are present
    await expect(page.locator('button:has-text("Overview")')).toBeVisible();
    await expect(page.locator('button:has-text("Contacts")')).toBeVisible();
    await expect(page.locator('button:has-text("Assets")')).toBeVisible();
    await expect(page.locator('button:has-text("USDOT Data")')).toBeVisible();
    await expect(page.locator('button:has-text("Billing")')).toBeVisible();
  });

  test('should switch between tabs', async ({ page }) => {
    // Navigate to detail page
    await page.click('button:has-text("Customers")');
    await page.waitForTimeout(500);
    await page.locator('tbody tr').first().click();
    await page.waitForTimeout(1000);

    // Click Contacts tab
    await page.click('button:has-text("Contacts")');
    await page.waitForTimeout(500);

    // Verify Contacts content is visible (either contacts list or "No contacts" message)
    const contactsContent = page.locator('text=Active Contacts, text=No contacts');
    await expect(contactsContent.first()).toBeVisible();

    // Click Assets tab
    await page.click('button:has-text("Assets")');
    await page.waitForTimeout(500);

    // Verify Assets content is visible (either assets list or "No assets" message)
    const assetsContent = page.locator('text=Vehicles, text=Equipment, text=No assets');
    await expect(assetsContent.first()).toBeVisible();

    // Click USDOT Data tab
    await page.click('button:has-text("USDOT Data")');
    await page.waitForTimeout(500);

    // Verify USDOT content is visible (either profile or "No USDOT Profile" message)
    const usdotContent = page.locator('text=FMCSA Identifiers, text=No USDOT Profile');
    await expect(usdotContent.first()).toBeVisible();

    // Click Billing tab
    await page.click('button:has-text("Billing")');
    await page.waitForTimeout(500);

    // Verify Billing stub message
    await expect(page.locator('text=Billing System Coming Soon')).toBeVisible();

    // Click back to Overview
    await page.click('button:has-text("Overview")');
    await page.waitForTimeout(500);

    // Verify Overview stats are visible
    await expect(page.locator('text=Contacts')).toBeVisible();
  });

  test('should display overview tab statistics', async ({ page }) => {
    // Navigate to detail page
    await page.click('button:has-text("Customers")');
    await page.waitForTimeout(500);
    await page.locator('tbody tr').first().click();
    await page.waitForTimeout(1000);

    // Verify stats cards exist
    const statsCards = page.locator('.p-4.rounded-lg.border');
    await expect(statsCards).toHaveCount(4); // Contacts, Vehicles, Equipment, Status

    // Verify Company Information section exists
    await expect(page.locator('text=Company Information')).toBeVisible();
    await expect(page.locator('text=Business Identity')).toBeVisible();
  });

  test('should navigate back to customer list', async ({ page }) => {
    // Navigate to detail page
    await page.click('button:has-text("Customers")');
    await page.waitForTimeout(500);
    await page.locator('tbody tr').first().click();
    await page.waitForTimeout(1000);

    // Click back button
    await page.click('button[title="Back to customers"]');
    await page.waitForTimeout(500);

    // Verify we're back on the list page
    await expect(page.locator('h1:has-text("Customers")')).toBeVisible();
    await expect(page.locator('button:has-text("+ New Customer")')).toBeVisible();
  });

  test('should display contacts with correspondence indicators', async ({ page, request }) => {
    // First, ensure we have a customer with contacts
    // This test assumes seed data includes contacts

    await page.click('button:has-text("Customers")');
    await page.waitForTimeout(500);
    await page.locator('tbody tr').first().click();
    await page.waitForTimeout(1000);

    // Navigate to Contacts tab
    await page.click('button:has-text("Contacts")');
    await page.waitForTimeout(500);

    // Check for either contacts table or "No contacts" message
    const hasContacts = await page.locator('table').count() > 0;

    if (hasContacts) {
      // Verify table headers
      await expect(page.locator('th:has-text("Name")')).toBeVisible();
      await expect(page.locator('th:has-text("Contact Info")')).toBeVisible();
      await expect(page.locator('th:has-text("Correspondence")')).toBeVisible();
    } else {
      // Verify "No contacts" message
      await expect(page.locator('text=No contacts')).toBeVisible();
    }
  });

  test('should display assets with proper categorization', async ({ page }) => {
    await page.click('button:has-text("Customers")');
    await page.waitForTimeout(500);
    await page.locator('tbody tr').first().click();
    await page.waitForTimeout(1000);

    // Navigate to Assets tab
    await page.click('button:has-text("Assets")');
    await page.waitForTimeout(500);

    // Check for either assets tables or "No assets" message
    const hasAssets = await page.locator('table').count() > 0;

    if (hasAssets) {
      // Could have vehicles, equipment, or both
      // Just verify the tab loaded successfully
      const assetsContent = page.locator('text=Vehicles, text=Equipment, text=Active');
      await expect(assetsContent.first()).toBeVisible();
    } else {
      await expect(page.locator('text=No assets')).toBeVisible();
    }
  });

  test('should handle customer with no USDOT profile gracefully', async ({ page }) => {
    await page.click('button:has-text("Customers")');
    await page.waitForTimeout(500);
    await page.locator('tbody tr').first().click();
    await page.waitForTimeout(1000);

    // Navigate to USDOT Data tab
    await page.click('button:has-text("USDOT Data")');
    await page.waitForTimeout(500);

    // Should show either USDOT profile data or "No USDOT Profile" message
    const usdotContent = page.locator('text=FMCSA Identifiers, text=No USDOT Profile');
    await expect(usdotContent.first()).toBeVisible();
  });

  test('should display responsive layout on 1920x1080', async ({ page }) => {
    // Set viewport to 1920x1080
    await page.setViewportSize({ width: 1920, height: 1080 });

    await page.click('button:has-text("Customers")');
    await page.waitForTimeout(500);
    await page.locator('tbody tr').first().click();
    await page.waitForTimeout(1000);

    // Verify page fits without horizontal scroll
    const bodyWidth = await page.evaluate(() => document.body.scrollWidth);
    expect(bodyWidth).toBeLessThanOrEqual(1920);

    // Verify all tabs are visible without overflow
    const tabsContainer = page.locator('.flex.gap-4').first();
    await expect(tabsContainer).toBeVisible();

    // Verify stats grid on overview displays properly
    const statsGrid = page.locator('.grid.grid-cols-4');
    await expect(statsGrid).toBeVisible();
  });
});
