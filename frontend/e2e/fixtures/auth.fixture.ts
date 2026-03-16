/**
 * Authentication Fixture for Playwright Tests
 *
 * Provides reusable authentication state for tests.
 */

import { test as base } from '@playwright/test';
import { LoginPage } from '../pages/login.page';

type AuthFixtures = {
  authenticatedPage: typeof base;
  authToken: string;
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

    // Wait for the dashboard to appear (indicating successful auth)
    // App uses state-based rendering, so we check for sidebar nav instead of URL
    await page.waitForSelector('text=Dashboard', { timeout: 10000 });
    await page.waitForLoadState('networkidle');

    // Use the authenticated page
    await use(base);

    // Logout after test (optional)
    // await page.goto('/logout');
  },

  authToken: async ({ page, authenticatedPage }, use) => {
    // Get JWT token from localStorage after authentication
    const token = await page.evaluate(() => {
      return localStorage.getItem('access_token');
    });

    if (!token) {
      throw new Error('Authentication failed: No access token found in localStorage');
    }

    await use(token);
  },
});

export { expect } from '@playwright/test';
