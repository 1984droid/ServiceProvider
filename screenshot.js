const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage();

  // Set viewport to 1920x1080
  await page.setViewportSize({ width: 1920, height: 1080 });

  // Navigate to the app
  await page.goto('http://localhost:5174');

  // Wait for login page to load
  await page.waitForTimeout(1000);

  // Fill in login credentials
  await page.fill('input[type="text"]', 'admin');
  await page.fill('input[type="password"]', 'admin');

  // Click sign in button
  await page.click('button:has-text("Sign In")');

  // Wait for navigation and page load
  await page.waitForTimeout(3000);

  // Get sidebar HTML and computed styles to debug
  const debugInfo = await page.evaluate(() => {
    const sidebar = document.querySelector('aside');
    const firstIcon = document.querySelector('aside svg');

    if (!firstIcon) return 'No icon found';

    const computed = window.getComputedStyle(firstIcon);

    return {
      iconClasses: firstIcon.className,
      computedWidth: computed.width,
      computedHeight: computed.height,
    };
  });

  console.log('Debug Info:', JSON.stringify(debugInfo, null, 2));

  // Take screenshot
  await page.screenshot({ path: 'screenshot.png', fullPage: false });

  console.log('Screenshot saved to screenshot.png');

  await browser.close();
})();
