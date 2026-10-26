"""Arma la portada (index.html) del sitio de reportes que se publica en GitHub Pages.

Uso:  python indice_reportes.py <carpeta-del-sitio>

La carpeta contiene los artefactos del run, uno por subcarpeta (así los deja actions/download-artifact):
    reporte-api/api-reporte.html, reporte-api/api-junit.xml
    reporte-web/playwright-report/index.html, reporte-web/reportes/web-junit.xml
Si una suite no se ejecutó (por ejemplo, la web se omite cuando falla la API), su tarjeta lo indica.
"""

import html
import os
import sys
from datetime import UTC, datetime
from pathlib import Path

from resumen_junit import RESULTADOS, leer_junit, totales_a_mostrar

SUITES = [  # (título, reporte HTML, reporte JUnit), relativos a la carpeta del sitio
    ("Pruebas de API", "reporte-api/api-reporte.html", "reporte-api/api-junit.xml"),
    ("Pruebas web (E2E)", "reporte-web/playwright-report/index.html", "reporte-web/reportes/web-junit.xml"),
]

PLANTILLA = """<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Reportes de pruebas</title>
<style>
  :root {{ --fondo: #f6f7f9; --tarjeta: #fff; --texto: #1d2129; --suave: #5b6270; --borde: #dde1e6;
          --ok: #1a7f37; --mal: #cf222e; --aviso: #9a6700; --enlace: #0b57d0; }}
  @media (prefers-color-scheme: dark) {{
    :root {{ --fondo: #0f1115; --tarjeta: #181b21; --texto: #e6e8eb; --suave: #9aa1ad; --borde: #2c313a;
            --ok: #3fb950; --mal: #f85149; --aviso: #d29922; --enlace: #79a8ff; }}
  }}
  body {{ margin: 0; background: var(--fondo); color: var(--texto); font: 16px/1.5 system-ui, sans-serif; }}
  main {{ max-width: 760px; margin: 0 auto; padding: 32px 16px; }}
  h1 {{ margin: 0 0 4px; font-size: 1.6rem; }}
  .meta {{ color: var(--suave); margin: 0 0 24px; }}
  .meta a, .tarjeta a {{ color: var(--enlace); }}
  .tarjeta {{ background: var(--tarjeta); border: 1px solid var(--borde); border-radius: 10px;
             padding: 18px 20px; margin-bottom: 16px; }}
  .tarjeta h2 {{ margin: 0 0 6px; font-size: 1.15rem; }}
  .totales {{ margin: 0 0 10px; color: var(--suave); }}
  .failed {{ color: var(--mal); font-weight: 600; }} .passed {{ color: var(--ok); font-weight: 600; }}
  .xfailed, .skipped, .ausente {{ color: var(--aviso); font-weight: 600; }}
</style>
</head>
<body>
<main>
  <h1>Reportes de pruebas</h1>
  <p class="meta">{meta}</p>
  {tarjetas}
</main>
</body>
</html>
"""


def tarjeta(sitio: Path, titulo: str, reporte_html: str, reporte_junit: str) -> str:
    junit = sitio / reporte_junit
    if not junit.exists():
        return (
            f'<section class="tarjeta"><h2>⚠️ {titulo}</h2>'
            '<p class="ausente">No se ejecutó en este run.</p></section>'
        )

    casos = leer_junit(junit)
    cuenta = {clave: sum(c.resultado == clave for c in casos) for clave in RESULTADOS}
    icono = "❌" if cuenta["failed"] else "✅"
    totales = " · ".join(f'<span class="{clave if n else ""}">{n} {clave}</span>' for clave, n in totales_a_mostrar(cuenta))
    enlace = (
        f'<a href="{reporte_html}">Abrir el reporte completo →</a>'
        if (sitio / reporte_html).exists()
        else "Reporte HTML no disponible."
    )
    return (
        f'<section class="tarjeta"><h2>{icono} {titulo}</h2>'
        f'<p class="totales">{totales} · {len(casos)} pruebas</p><p>{enlace}</p></section>'
    )


def meta_del_run() -> str:
    fecha = datetime.now(UTC).strftime("%Y-%m-%d %H:%M UTC")
    numero, sha = os.getenv("GITHUB_RUN_NUMBER"), os.getenv("GITHUB_SHA", "")[:7]
    if not numero:
        return f"Generado en local · {fecha}"
    url = f"{os.getenv('GITHUB_SERVER_URL')}/{os.getenv('GITHUB_REPOSITORY')}/actions/runs/{os.getenv('GITHUB_RUN_ID')}"
    return f'<a href="{html.escape(url)}">Run #{numero}</a> · commit <code>{sha}</code> · {fecha}'


def main() -> None:
    if len(sys.argv) != 2:
        sys.exit("Uso: python indice_reportes.py <carpeta-del-sitio>")
    sitio = Path(sys.argv[1])
    tarjetas = "\n  ".join(tarjeta(sitio, *suite) for suite in SUITES)
    (sitio / "index.html").write_text(PLANTILLA.format(meta=meta_del_run(), tarjetas=tarjetas), encoding="utf-8")
    print(f"Portada creada: {sitio / 'index.html'}")


if __name__ == "__main__":
    main()
