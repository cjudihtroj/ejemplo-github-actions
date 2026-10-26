import { defineConfig, devices } from '@playwright/test';
import { defineBddConfig } from 'playwright-bdd';

const testDir = defineBddConfig({
  features: 'features/*.feature',
  steps: 'steps/*.ts',
});

const enCI = !!process.env.CI; // GitHub Actions define CI=true

export default defineConfig({
  testDir,
  forbidOnly: enCI,            // en CI falla si alguien dejó un test.only
  retries: enCI ? 1 : 0,       // un reintento solo en CI: si pasa al reintentar, se reporta como "flaky"
  workers: enCI ? 1 : undefined,
  reporter: [
    ['list'],
    ['html', { open: 'never' }],
    ['junit', { outputFile: 'reportes/web-junit.xml' }],
  ],
  use: {
    baseURL: process.env.BASE_URL ?? 'https://automationintesting.online',
    trace: 'retain-on-failure',
    screenshot: 'on',
  },
  projects: [{ name: 'chromium', use: { ...devices['Desktop Chrome'] } }],
});
