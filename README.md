# Ejemplo · Pipeline de pruebas en GitHub Actions

CS5383 · Semana 12. Ejecuta en cada push o pull request a `main`:

1. **Pruebas de API** (pytest + httpx, y pytest-bdd para los escenarios Gherkin) contra Restful Booker (S10).
2. **Pruebas web** (Playwright + Gherkin + Page Object) del login de Shady Meadows (S11), solo si la API pasó.
3. **Publicar reportes** en GitHub Pages (solo desde `main`, también cuando las pruebas fallan).

## Reportes: tres capas

| Capa | Para quién | Dónde se ve |
|---|---|---|
| **Resumen del job** | Quien revisa el run o el PR | Página del run (pestaña *Summary*): una tabla por suite, con los fallos primero y el motivo de cada *xfail* |
| **Reporte HTML** | Quien investiga un fallo | En **GitHub Pages** (un enlace, sin descargar nada) y dentro de los artefactos `reporte-api` y `reporte-web` |
| **JUnit XML** | Herramientas (CI, Kiwi TCMS, Xray…) | Dentro de los artefactos: alimenta la trazabilidad |

## Estructura

```
ejemplo-github-actions/
├── .github/
│   ├── workflows/pruebas.yml    el pipeline
│   └── scripts/
│       ├── resumen_junit.py     JUnit XML → tabla del resumen del job
│       └── indice_reportes.py   portada del sitio de reportes (GitHub Pages)
├── api/                         pruebas de API (S10)
│   ├── tests/restful_booker/
│   │   ├── test_demo.py                     casos con pytest
│   │   ├── features/api_reservas.feature
│   │   └── test_bdd_api_reservas.py         pasos del .feature (pytest-bdd)
│   ├── pytest.ini
│   └── requirements.txt
└── web/                         pruebas web (S11)
    ├── features/  steps/  pages/
    ├── playwright.config.ts     (en CI: 1 reintento, 1 worker, reporte JUnit)
    ├── package.json
    └── package-lock.json        necesario para `npm ci`
```

## Ejecutar en local

```bash
# API
cd api
python -m venv .venv
.venv\Scripts\activate           # Windows (Linux/macOS: source .venv/bin/activate)
pip install -r requirements.txt
pytest                                                    # 7 passed, 4 xfailed
pytest --html=reportes/api-reporte.html --self-contained-html   # con reporte HTML

# Web
cd ../web
npm ci
npx playwright install chromium
npm test                                                  # 2 passed
npx playwright show-report                                # reporte HTML

# Resumen como el del pipeline (desde api/ o web/)
python ../.github/scripts/resumen_junit.py "Pruebas web" reportes/web-junit.xml
```

> En PowerShell, si aparece "no está firmado digitalmente": `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned`.

## Ejecutar en GitHub

1. Crea un repositorio **público** en GitHub (Actions y Pages son gratuitos en repositorios públicos) y sube esta carpeta a la rama `main`.
2. **Activa GitHub Pages** (una sola vez): *Settings → Pages → Build and deployment → Source:* **GitHub Actions**.
3. Pestaña **Actions** → run "Pruebas": **Pruebas de API** → **Pruebas web (E2E)** → **Publicar reportes (GitHub Pages)**.
4. En la página del run:
   - **Summary**: la tabla de cada suite y el enlace a los reportes publicados (`https://<usuario>.github.io/<repo>/`).
   - **Artifacts**: `reporte-api` (HTML y JUnit XML) y `reporte-web` (reporte HTML, JUnit XML y, si algo falló, captura y traza).
5. Para ver un pipeline en rojo: crea una rama, cambia en `web/features/login.feature` el mensaje esperado por `"Credenciales inválidas"` y abre un pull request. El resumen muestra el paso que falló; el sitio de Pages no cambia, porque solo se publica desde `main`.

> Las pruebas marcadas con `xfail` en `api/` corresponden a defectos conocidos de Restful Booker: el pipeline sigue en verde y el resumen las muestra como *xfailed*, con el defecto como motivo.
>
> El sitio de Pages es **público** y muestra solo el último run de `main`. Los runs anteriores conservan sus artefactos (30 días para `reporte-web`).
