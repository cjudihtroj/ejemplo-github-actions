import { Page, Locator } from '@playwright/test';

export class PaginaLogin {
  readonly usuario: Locator;
  readonly clave: Locator;
  readonly botonIngresar: Locator;

  constructor(private readonly page: Page) {
    this.usuario = page.getByLabel('Username');
    this.clave = page.getByLabel('Password');
    this.botonIngresar = page.getByRole('button', { name: 'Login' });
  }

  async abrir() {
    await this.page.goto('/admin');
  }

  async iniciarSesion(usuario: string, clave: string) {
    await this.usuario.fill(usuario);
    await this.clave.fill(clave);
    await this.botonIngresar.click();
  }

  mensaje(texto: string) {
    return this.page.getByText(texto);
  }
}
