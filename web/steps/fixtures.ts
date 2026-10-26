import { test as base } from 'playwright-bdd';
import { Habitacion } from '../pages/PaginaHabitaciones';

// Escenarios que hoy fallan por un defecto conocido del sitio (título del escenario → defecto).
// Quedan como fallo esperado (test.fail): el pipeline sigue en verde y, si el defecto se corrige, avisa.
const DEFECTOS: Record<string, string> = {
  'Iniciar sesión y eliminar una habitación': 'D-05: DELETE /api/room/{id} responde 500: la habitación no se elimina',
};

// Datos que comparten los pasos de un mismo escenario (por ejemplo, la habitación que se crea)
type Contexto = { habitacion?: Habitacion };

export const test = base.extend<{ contexto: Contexto; trazabilidad: void; defectoReportado: void }>({
  contexto: async ({}, use) => {
    await use({});
  },
  // Copia las etiquetas @HU-xx y @CP-xx del escenario al JUnit XML (matriz de trazabilidad)
  trazabilidad: [
    async ({}, use, testInfo) => {
      for (const tag of testInfo.tags.filter((t) => /^@(HU|CP)-/.test(t))) {
        testInfo.annotations.push({ type: tag.slice(1, 3), description: tag.slice(1) });
      }
      await use();
    },
    { auto: true },
  ],
  defectoReportado: [
    async ({}, use, testInfo) => {
      const defecto = DEFECTOS[testInfo.title];
      testInfo.fail(defecto !== undefined, defecto);
      await use();
    },
    { auto: true },
  ],
});
