import { test, expect } from '@playwright/test';

test('multi-user collaboration scenario', async ({ browser }) => {
  const userA = await browser.newContext();
  const pageA = await userA.newPage();
  const userB = await browser.newContext();
  const pageB = await userB.newPage();

  await pageA.goto('/');
  await pageB.goto('/');

  // Simulate user A creating a new conversation
  await pageA.click('button#create-conversation');
  await pageA.fill('input#title', 'E2E Test Room');
  await pageA.click('button#save-room');

  // User B joins and should see the conversation
  await pageB.click('button#join-room');
  await pageB.fill('input#room-id', await pageA.$eval('#room-id', el => el.textContent));
  await pageB.click('button#confirm-join');

  await expect(pageB.locator('.conversation-title')).toHaveText('E2E Test Room');
});