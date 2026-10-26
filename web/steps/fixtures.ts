import { test as base } from 'playwright-bdd';
import { Habitacion } from '../pages/PaginaHabitaciones';

// Escenarios que hoy fallan por un defecto conocido del sitio (título del escenario → defecto).
// Quedan como fallo esperado (test.fail): el pipeline sigue en verde y, si el defecto se corrige, avisa.
const DEFECTOS: Record<string, string> = {
  'Iniciar sesión y eliminar una habitación': 'D-05: DELETE /api/room/{id} responde 500: la habitación no se elimina',
};

// Datos que comparten los pasos de un mismo escenario (por ejemplo, la habitación que se crea)
type Contexto = { habitacion?: Habitacion };

export const test = base.extend<{ contexto: Contexto; defectoReportado: void }>({
  contexto: async ({}, use) => {
    await use({});
  },
  defectoReportado: [
    async ({}, use, testInfo) => {
      const defecto = DEFECTOS[testInfo.title];
      testInfo.fail(defecto !== undefined, defecto);
      await use();
    },
    { auto: true },
  ],
});
