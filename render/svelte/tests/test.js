import { expect, test } from '@playwright/test';

test('Take a screenshot of the Dashboard', async ({ page }) => {
	await page.goto('/');

	await page.setViewportSize({ width: 800, height: 480 });

	await page.screenshot({ path: 'output.png' });
});