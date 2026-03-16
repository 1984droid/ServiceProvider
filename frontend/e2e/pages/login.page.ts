/**
 * Login Page Object
 *
 * Page Object Model for the login page.
 */

import { Page, Locator } from '@playwright/test';

export class LoginPage {
  readonly page: Page;
  readonly usernameInput: Locator;
  readonly passwordInput: Locator;
  readonly loginButton: Locator;
  readonly errorMessage: Locator;

  constructor(page: Page) {
    this.page = page;
    this.usernameInput = page.getByLabel('Username');
    this.passwordInput = page.getByLabel('Password');
    this.loginButton = page.getByRole('button', { name: /sign in/i });
    this.errorMessage = page.getByRole('alert');
  }

  async goto() {
    await this.page.goto('/login');
  }

  async login(username: string, password: string) {
    await this.usernameInput.fill(username);
    await this.passwordInput.fill(password);

    // Wait for the login API call to complete
    const responsePromise = this.page.waitForResponse(
      response => response.url().includes('/api/auth/login') && response.status() === 200,
      { timeout: 5000 }
    );

    await this.loginButton.click();

    // Wait for successful response
    await responsePromise;
  }

  async expectErrorMessage(message: string) {
    await this.errorMessage.waitFor();
    await this.page.waitForSelector(`text=${message}`);
  }
}
