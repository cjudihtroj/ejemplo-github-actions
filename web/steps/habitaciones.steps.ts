import { expect } from '@playwright/test';
import { createBdd } from 'playwright-bdd';
import { Habitacion, PaginaHabitaciones } from '../pages/PaginaHabitaciones';
import { PaginaLogin } from '../pages/PaginaLogin';
import { test } from './fixtures';

const { Given, When, Then } = createBdd(test);

function nuevaHabitacion(tipo: string, precio: number): Habitacion {
  return { numero: Date.now().toString().slice(-4), tipo, precio }; // número único: el sitio es compartido
}

Given('que el administrador inició sesión', async ({ page }) => {
  const login = new PaginaLogin(page);
  await login.abrir();
  await login.iniciarSesion('admin', 'password');
});

Given('creó una habitación {string} accesible con precio {int}', async ({ page, contexto }, tipo: string, precio: number) => {
  contexto.habitacion = nuevaHabitacion(tipo, precio);
  await new PaginaHabitaciones(page).crear(contexto.habitacion);
});

When('crea una habitación {string} accesible con precio {int}', async ({ page, contexto }, tipo: string, precio: number) => {
  contexto.habitacion = nuevaHabitacion(tipo, precio);
  await new PaginaHabitaciones(page).crear(contexto.habitacion);
});

When('elimina la habitación', async ({ page, contexto }) => {
  await new PaginaHabitaciones(page).eliminar(contexto.habitacion!.numero);
});

Then(
  'la nueva habitación aparece en el listado con tipo {string} y precio {int}',
  async ({ page, contexto }, tipo: string, precio: number) => {
    const fila = new PaginaHabitaciones(page).habitacion(contexto.habitacion!.numero);
    await expect(fila).toContainText(tipo);
    await expect(fila).toContainText(String(precio));
    await test.info().attach('Habitación en el listado', {
      body: await page.screenshot(),
      contentType: 'image/png',
    });
  },
);

Then('la habitación ya no aparece en el listado', async ({ page, contexto }) => {
  await expect(new PaginaHabitaciones(page).habitacion(contexto.habitacion!.numero)).toHaveCount(0);
});
