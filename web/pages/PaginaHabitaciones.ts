import { Page, Locator } from '@playwright/test';

export type Habitacion = { numero: string; tipo: string; precio: number };

export class PaginaHabitaciones {
  readonly numero: Locator;
  readonly tipo: Locator;
  readonly accesible: Locator;
  readonly precio: Locator;
  readonly botonCrear: Locator;

  constructor(private readonly page: Page) {
    this.numero = page.locator('#roomName');
    this.tipo = page.locator('#type');
    this.accesible = page.locator('#accessible');
    this.precio = page.locator('#roomPrice');
    this.botonCrear = page.getByRole('button', { name: 'Create' });
  }

  async crear(habitacion: Habitacion) {
    await this.numero.fill(habitacion.numero);
    await this.tipo.selectOption(habitacion.tipo);
    await this.accesible.selectOption('true');
    await this.precio.fill(String(habitacion.precio));
    // El sitio demo es compartido y a veces tarda: se espera la respuesta del servidor, no un tiempo fijo
    const respuesta = this.page.waitForResponse(
      (r) => r.url().endsWith('/api/room') && r.request().method() === 'POST',
      { timeout: 15_000 },
    );
    await this.botonCrear.click();
    await respuesta;
  }

  habitacion(numero: string) {
    return this.page.getByTestId('roomlisting').filter({ has: this.page.locator(`#roomName${numero}`) });
  }

  async eliminar(numero: string) {
    const respuesta = this.page.waitForResponse(
      (r) => r.url().includes('/api/room/') && r.request().method() === 'DELETE',
      { timeout: 15_000 },
    );
    await this.habitacion(numero).locator('.roomDelete').click();
    await respuesta;
  }
}
