import { expect, Page } from '@playwright/test';
import { createBdd } from 'playwright-bdd';
import { MensajeDeContacto, PaginaInicio } from '../pages/PaginaInicio';
import { PaginaLogin } from '../pages/PaginaLogin';
import { PaginaMensajes } from '../pages/PaginaMensajes';
import { test } from './fixtures';

const { Given, When, Then } = createBdd(test);

const ADMIN = { usuario: 'admin', clave: 'password' };

function mensajeDelHuesped(asunto: string): MensajeDeContacto {
  return {
    nombre: 'Ana Torres',
    correo: 'ana.torres@example.com',
    telefono: '01234567890',
    asunto: `${asunto} ${Date.now().toString().slice(-6)}`, // sufijo único: el sitio es compartido
    texto: 'Quisiera saber si la habitación doble tiene vista al jardín.',
  };
}

async function abrirBandejaComoAdministrador(page: Page) {
  const login = new PaginaLogin(page);
  await login.abrir();
  await login.iniciarSesion(ADMIN.usuario, ADMIN.clave);
  await new PaginaMensajes(page).abrir();
}

Given('que un huésped está en la página principal', async ({ page }) => {
  await new PaginaInicio(page).abrir();
});

Given('que un huésped envió un mensaje de contacto', async ({ page, contexto }) => {
  contexto.mensaje = mensajeDelHuesped('Consulta de disponibilidad');
  const inicio = new PaginaInicio(page);
  await inicio.abrir();
  await inicio.enviarMensaje(contexto.mensaje);
});

When('envía un mensaje de contacto con el asunto {string}', async ({ page, contexto }, asunto: string) => {
  contexto.mensaje = mensajeDelHuesped(asunto);
  await new PaginaInicio(page).enviarMensaje(contexto.mensaje);
});

Then('ve la confirmación de que su mensaje fue recibido', async ({ page, contexto }) => {
  await expect(new PaginaInicio(page).confirmacion(contexto.mensaje!.nombre)).toBeVisible();
  await test.info().attach('Confirmación del mensaje', {
    body: await page.screenshot(),
    contentType: 'image/png',
  });
});

When('el administrador inicia sesión y abre la bandeja de mensajes', async ({ page }) => {
  await abrirBandejaComoAdministrador(page);
});

When('el administrador lo elimina de la bandeja', async ({ page, contexto }) => {
  await abrirBandejaComoAdministrador(page);
  await new PaginaMensajes(page).eliminar(contexto.mensaje!.asunto);
});

Then('ve el mensaje del huésped con su nombre y asunto', async ({ page, contexto }) => {
  await expect(new PaginaMensajes(page).mensaje(contexto.mensaje!.asunto)).toContainText(contexto.mensaje!.nombre);
  await test.info().attach('Mensaje en la bandeja del administrador', {
    body: await page.screenshot(),
    contentType: 'image/png',
  });
});

Then('el mensaje ya no aparece en la bandeja', async ({ page, contexto }) => {
  await expect(new PaginaMensajes(page).mensaje(contexto.mensaje!.asunto)).toHaveCount(0);
});
