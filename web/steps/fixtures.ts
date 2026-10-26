import { test as base } from 'playwright-bdd';
import { MensajeDeContacto } from '../pages/PaginaInicio';

// Escenarios que hoy fallan por un defecto conocido del sitio (título del escenario → defecto).
// Quedan como fallo esperado (test.fail): el pipeline sigue en verde y, si el defecto se corrige, avisa.
const DEFECTOS: Record<string, string> = {
  'El administrador elimina un mensaje de la bandeja': 'D-05: DELETE /api/message/{id} responde 500: el mensaje no se elimina',
};

// Datos que comparten los pasos de un mismo escenario (por ejemplo, el mensaje que envía el huésped)
type Contexto = { mensaje?: MensajeDeContacto };

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
