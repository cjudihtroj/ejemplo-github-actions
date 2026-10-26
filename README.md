# Ejemplo · Pipeline de pruebas en GitHub Actions

CS5383 · Semana 12. Ejecuta en cada push o pull request a `main`:

1. **Pruebas de API** (pytest + httpx, y pytest-bdd para los escenarios Gherkin) contra Restful Booker (S10).
2. **Pruebas web** (Playwright + Gherkin + Page Object) del login de Shady Meadows (S11), solo si la API pasó.

Cada job publica su reporte como **artefacto** del run.

## Estructura

```
ejemplo-github-actions/
├── .github/workflows/
│   └── pruebas.yml          el pipeline
├── api/                     pruebas de API (S10)
│   ├── tests/restful_booker/
│   │   ├── test_demo.py                     casos con pytest
│   │   ├── features/api_reservas.feature
│   │   └── test_bdd_api_reservas.py         pasos del .feature (pytest-bdd)
│   ├── pytest.ini
│   └── requirements.txt
└── web/                     pruebas web (S11)
    ├── features/  steps/  pages/
    ├── playwright.config.ts  (en CI: 1 reintento, 1 worker, reporte JUnit)
    ├── package.json
    └── package-lock.json    necesario para `npm ci`
```

## Ejecutar en local

```bash
# API
cd api
pip install -r requirements.txt
pytest

# Web
cd ../web
npm ci
npx playwright install chromium
npm test
```

## Ejecutar en GitHub

1. Crea un repositorio **público** en GitHub (Actions es gratuito en repositorios públicos con los runners estándar) y sube esta carpeta a la rama `main`.
2. Pestaña **Actions** → run "Pruebas": job **Pruebas de API** y luego **Pruebas web (E2E)**.
3. Al final del run, en **Artifacts**: `reporte-api` (JUnit XML) y `reporte-web` (reporte HTML, JUnit XML y, si algo falló, captura y traza).
4. Para ver un pipeline en rojo: crea una rama, cambia en `web/features/login.feature` el mensaje esperado por `"Credenciales inválidas"` y abre un pull request.

> Las pruebas marcadas con `xfail` en `api/` corresponden a defectos conocidos de Restful Booker: el pipeline sigue en verde y el reporte los muestra como *xfailed*.
