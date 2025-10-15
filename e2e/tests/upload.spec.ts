import { test, expect } from '@playwright/test';

test('file upload to analysis pipeline', async ({ page }) => {
  await page.goto('/');
  const input = await page.$('input[type=file]');
  await input.setInputFiles('test-data/sample.csv');
  await page.click('button#upload');
  await expect(page.locator('#status')).toHaveText(/processing/i);
});