import { Page, Locator } from '@playwright/test';

export class PaginaMensajes {
  readonly enlaceMensajes: Locator;

  constructor(private readonly page: Page) {
    this.enlaceMensajes = page.getByRole('link', { name: /Messages/ });
  }

  async abrir() {
    await this.enlaceMensajes.click();
  }

  mensaje(asunto: string) {
    return this.page.locator('.detail').filter({ hasText: asunto });
  }

  async eliminar(asunto: string) {
    const respuesta = this.page.waitForResponse(
      (r) => r.url().includes('/api/message/') && r.request().method() === 'DELETE',
      { timeout: 15_000 },
    );
    await this.mensaje(asunto).getByTestId(/^DeleteMessage/).click();
    await respuesta;
  }
}
