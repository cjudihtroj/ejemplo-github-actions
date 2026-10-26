import { expect } from '@playwright/test';
import { createBdd } from 'playwright-bdd';
import { PaginaLogin } from '../pages/PaginaLogin';
import { test } from './fixtures';

const { Given, When, Then } = createBdd(test);

Given('que el administrador está en la página de login', async ({ page }) => {
  await new PaginaLogin(page).abrir();
});

When('inicia sesión con usuario {string} y clave {string}', async ({ page }, usuario: string, clave: string) => {
  await new PaginaLogin(page).iniciarSesion(usuario, clave);
});

Then('ve el panel de administración', async ({ page }) => {
  await expect(page).toHaveURL(/\/admin\/rooms/);
  await test.info().attach('Validación del panel de administración', {
    body: await page.screenshot(),
    contentType: 'image/png',
  });
});

Then('valida que se muestre la sección de habitaciones', async ({ page }) => {
  await expect(page.getByText('Rooms', { exact: true })).toBeVisible();
  await test.info().attach('Validación de la sección de habitaciones', {
    body: await page.screenshot(),
    contentType: 'image/png',
  });
});

Then('ve el mensaje {string}', async ({ page }, mensaje: string) => {
  await expect(new PaginaLogin(page).mensaje(mensaje)).toBeVisible();
  await test.info().attach('Validación del mensaje de error', {
    body: await page.screenshot(),
    contentType: 'image/png',
  });
});
