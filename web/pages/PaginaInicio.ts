import { Page, Locator } from '@playwright/test';

export type MensajeDeContacto = { nombre: string; correo: string; telefono: string; asunto: string; texto: string };

export class PaginaInicio {
  readonly nombre: Locator;
  readonly correo: Locator;
  readonly telefono: Locator;
  readonly asunto: Locator;
  readonly texto: Locator;
  readonly botonEnviar: Locator;

  constructor(private readonly page: Page) {
    this.nombre = page.getByRole('textbox', { name: 'Name' });
    this.correo = page.getByRole('textbox', { name: 'Email' });
    this.telefono = page.getByRole('textbox', { name: 'Phone' });
    this.asunto = page.getByRole('textbox', { name: 'Subject' });
    this.texto = page.locator('#description');
    this.botonEnviar = page.getByRole('button', { name: 'Submit' });
  }

  async abrir() {
    await this.page.goto('/');
  }

  async enviarMensaje(mensaje: MensajeDeContacto) {
    await this.nombre.fill(mensaje.nombre);
    await this.correo.fill(mensaje.correo);
    await this.telefono.fill(mensaje.telefono);
    await this.asunto.fill(mensaje.asunto);
    await this.texto.fill(mensaje.texto);
    // El sitio demo es compartido y a veces tarda: se espera la respuesta del envío, no un tiempo fijo
    const respuesta = this.page.waitForResponse(
      (r) => r.url().includes('/api/message') && r.request().method() === 'POST',
      { timeout: 15_000 },
    );
    await this.botonEnviar.click();
    await respuesta;
  }

  confirmacion(nombre: string) {
    return this.page.getByRole('heading', { name: `Thanks for getting in touch ${nombre}!` });
  }
}
