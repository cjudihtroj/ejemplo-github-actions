# Ejemplo · Pipeline de pruebas en GitHub Actions

CS5383 · Semana 12. En cada push o pull request a `main`, el workflow ejecuta:

1. **Pruebas de API** (pytest-bdd + httpx) contra Restful Booker.
2. **Pruebas web** (Playwright + Gherkin + Page Object) de Shady Meadows, solo si la API pasó.
3. **Publicación de reportes** en GitHub Pages (solo desde `main`).

## Estructura

```
ejemplo-github-actions/
├── .github/
│   ├── workflows/pruebas.yml    el pipeline
│   └── scripts/                 resumen del job y portada de GitHub Pages
├── api/
│   ├── tests/restful_booker/    features/ · pasos · conftest.py
│   ├── pytest.ini
│   └── requirements.txt
└── web/
    ├── features/  steps/  pages/
    ├── playwright.config.ts
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
pytest                           # 4 passed, 4 xfailed

# Web
cd ../web
npm ci
npx playwright install chromium
npm test                         # 3 passed
npx playwright show-report       # reporte HTML
```

> En PowerShell, si aparece "no está firmado digitalmente": `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned`.

## Ejecutar en GitHub

1. Crea un repositorio **público** y sube esta carpeta a la rama `main`.
2. Activa GitHub Pages (una sola vez): *Settings → Pages → Source:* **GitHub Actions**.
3. En **Actions**, abre el run "Pruebas automatizadas de API y web".
4. Revisa el **Summary** (tabla de cada suite y enlace a los reportes en Pages) y los **Artifacts** (`reporte-api` y `reporte-web`).
5. Para ver el pipeline en rojo: en una rama, cambia en `web/features/login.feature` el mensaje esperado por `"Credenciales inválidas"` y abre un pull request.
