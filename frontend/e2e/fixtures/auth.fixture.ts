/**
 * Authentication Fixture for Playwright Tests
 *
 * Provides reusable authentication state for tests.
 */

import { test as base } from '@playwright/test';
import { LoginPage } from '../pages/login.page';

type AuthFixtures = {
  authenticatedPage: typeof base;
};

/**
 * Extend base test with authenticated user fixture
 */
export const test = base.extend<AuthFixtures>({
  authenticatedPage: async ({ page }, use) => {
    // Login before test
    const loginPage = new LoginPage(page);
    await loginPage.goto();
    await loginPage.login('admin', 'admin'); // Use credentials from seed data

    // Use the authenticated page
    await use(base);

    // Logout after test (optional)
    // await page.goto('/logout');
  },
});

export { expect } from '@playwright/test';
