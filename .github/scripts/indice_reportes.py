"""Arma la portada (index.html) del sitio de reportes que se publica en GitHub Pages.

Uso:  python indice_reportes.py <carpeta-del-sitio>

La portada tiene una tarjeta por suite y la matriz de trazabilidad (HU → CP → resultado), armada con
las etiquetas @HU-xx y @CP-xx que cada suite copia al JUnit XML. En GitHub Actions, la matriz también
se escribe en la página del run.

La carpeta contiene los artefactos del run, uno por subcarpeta (así los deja actions/download-artifact):
    reporte-api/api-reporte.html, reporte-api/api-junit.xml
    reporte-web/playwright-report/index.html, reporte-web/reportes/web-junit.xml
Si una suite no se ejecutó (por ejemplo, la web se omite cuando falla la API), su tarjeta lo indica.
"""

import html
import os
import re
import sys
from datetime import UTC, datetime
from pathlib import Path

from resumen_junit import RESULTADOS, Caso, leer_junit, totales_a_mostrar

SUITES = [  # (título, nivel, reporte HTML, reporte JUnit), relativos a la carpeta del sitio
    ("Pruebas de API", "API", "reporte-api/api-reporte.html", "reporte-api/api-junit.xml"),
    ("Pruebas web (E2E)", "Web", "reporte-web/playwright-report/index.html", "reporte-web/reportes/web-junit.xml"),
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
  .tabla {{ overflow-x: auto; }}
  table {{ width: 100%; border-collapse: collapse; font-size: .95rem; }}
  th, td {{ text-align: left; padding: 6px 8px; border-bottom: 1px solid var(--borde); vertical-align: top; }}
  th {{ color: var(--suave); font-weight: 600; }}
  td:nth-child(-n+2), td:nth-child(4), td:nth-child(5) {{ white-space: nowrap; }}
</style>
</head>
<body>
<main>
  <h1>Reportes de pruebas</h1>
  <p class="meta">{meta}</p>
  {tarjetas}
  {matriz}
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


def filas_de_la_matriz(sitio: Path) -> list[tuple[str, Caso]]:
    """(nivel, caso) de las suites que se ejecutaron, ordenadas por HU y CP."""
    filas = [(nivel, caso) for _, nivel, _, junit in SUITES if (sitio / junit).exists()
             for caso in leer_junit(sitio / junit)]
    numero = lambda etiqueta: int(etiqueta.partition("-")[2] or 0)  # "CP-10" → 10, para que vaya después de "CP-9"
    return sorted(filas, key=lambda fila: (numero(fila[1].hu), numero(fila[1].cp)))


def resultado_en_la_matriz(caso: Caso) -> str:
    """El resultado y, si es un fallo esperado, el defecto reportado (D-xx al inicio del motivo)."""
    defecto = re.match(r"D-\d+", caso.detalle) if caso.resultado == "xfailed" else None
    return RESULTADOS[caso.resultado] + (f" · {defecto.group()}" if defecto else "")


def matriz_html(filas: list[tuple[str, Caso]]) -> str:
    if not filas:
        return ""
    celdas = "".join(
        f"<tr><td>{c.hu or '—'}</td><td>{c.cp or '—'}</td><td>{html.escape(c.nombre)}</td><td>{nivel}</td>"
        f'<td class="{c.resultado}">{resultado_en_la_matriz(c)}</td></tr>'
        for nivel, c in filas
    )
    return (
        '<section class="tarjeta"><h2>🔗 Matriz de trazabilidad</h2><div class="tabla"><table>'
        "<tr><th>HU</th><th>CP</th><th>Escenario</th><th>Nivel</th><th>Resultado</th></tr>"
        f"{celdas}</table></div></section>"
    )


def matriz_markdown(filas: list[tuple[str, Caso]]) -> str:
    lineas = ["## 🔗 Matriz de trazabilidad", "", "| HU | CP | Escenario | Nivel | Resultado |", "|---|---|---|---|---|"]
    lineas += [f"| {c.hu or '—'} | {c.cp or '—'} | {c.nombre} | {nivel} | {resultado_en_la_matriz(c)} |"
               for nivel, c in filas]
    return "\n".join(lineas) + "\n"


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
    tarjetas = "\n  ".join(tarjeta(sitio, titulo, html_, junit) for titulo, _, html_, junit in SUITES)
    filas = filas_de_la_matriz(sitio)
    portada = PLANTILLA.format(meta=meta_del_run(), tarjetas=tarjetas, matriz=matriz_html(filas))
    (sitio / "index.html").write_text(portada, encoding="utf-8")
    print(f"Portada creada: {sitio / 'index.html'}")

    destino = os.getenv("GITHUB_STEP_SUMMARY")
    if destino and filas:
        with open(destino, "a", encoding="utf-8") as resumen:
            resumen.write(matriz_markdown(filas) + "\n")


if __name__ == "__main__":
    main()
