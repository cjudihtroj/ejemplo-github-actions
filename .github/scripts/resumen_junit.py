"""Convierte un reporte JUnit XML en una tabla Markdown para la página del run (resumen del job).

Uso:  python resumen_junit.py "<título>" <reporte.xml>

En GitHub Actions escribe en $GITHUB_STEP_SUMMARY; fuera de GitHub, imprime en la consola.
Solo usa la biblioteca estándar: no hay que instalar nada en el runner.
"""

import os
import sys
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from pathlib import Path

RESULTADOS = {  # orden de la tabla: primero lo que hay que mirar
    "failed": "❌ failed",
    "xfailed": "⚠️ xfailed",
    "skipped": "⏭️ skipped",
    "passed": "✅ passed",
}


@dataclass
class Caso:
    nombre: str
    suite: str
    resultado: str  # una clave de RESULTADOS
    segundos: float
    detalle: str


def leer_junit(ruta: Path) -> list[Caso]:
    """Lee los <testcase> del reporte. Sirve para pytest y para Playwright."""
    casos = []
    for caso in ET.parse(ruta).getroot().iter("testcase"):
        fallo = caso.find("failure")
        if fallo is None:
            fallo = caso.find("error")
        omitido = caso.find("skipped")

        if fallo is not None:
            resultado, detalle = "failed", _detalle_del_fallo(fallo)
        elif omitido is not None and omitido.get("type") == "pytest.xfail":
            resultado, detalle = "xfailed", omitido.get("message", "")  # el motivo: el defecto reportado
        elif omitido is not None:
            resultado, detalle = "skipped", omitido.get("message", "")
        else:
            resultado, detalle = "passed", ""

        nombre, suite = _nombre_y_suite(caso.get("name", ""), caso.get("classname", ""))
        casos.append(Caso(nombre, suite, resultado, float(caso.get("time") or 0), detalle))
    return casos


def _nombre_y_suite(nombre: str, clase: str) -> tuple[str, str]:
    if " › " in nombre:  # Playwright: "Feature › Scenario"
        suite, _, escenario = nombre.rpartition(" › ")
        return escenario, suite
    if nombre.startswith("test_"):  # pytest: test_c1_filtrar_por_nombre → "C1 filtrar por nombre"
        nombre = nombre.removeprefix("test_").replace("_", " ")
        nombre = nombre[:1].upper() + nombre[1:]
    return nombre, clase.rpartition(".")[2]  # tests.restful_booker.test_demo → test_demo


def _detalle_del_fallo(fallo: ET.Element) -> str:
    detalle = (fallo.get("message") or "").strip()
    # Playwright indica el paso de Gherkin que falló al final de la primera línea: "… › Then ve el panel"
    primera_linea = (fallo.text or "").strip().splitlines()[:1]
    if primera_linea:
        paso = primera_linea[0].rpartition(" › ")[2].strip()
        if paso.split(" ")[0] in {"Given", "When", "Then", "And", "But"}:
            detalle = f"{paso}: {detalle}"
    return detalle


def totales_a_mostrar(cuenta: dict[str, int]) -> list[tuple[str, int]]:
    """passed y failed siempre (aunque sean 0); xfailed y skipped solo si hay."""
    return [(clave, cuenta[clave]) for clave in ("passed", "failed", "xfailed", "skipped")
            if cuenta[clave] or clave in ("passed", "failed")]


def _celda(texto: str, largo: int = 160) -> str:
    texto = " ".join(texto.split()).replace("|", "\\|")
    return texto if len(texto) <= largo else texto[: largo - 1] + "…"


def resumen_markdown(titulo: str, ruta: Path) -> str:
    if not ruta.exists():
        return f"## ⚠️ {titulo}\n\nNo se encontró `{ruta}`: las pruebas no llegaron a ejecutarse.\n"

    casos = leer_junit(ruta)
    cuenta = {clave: sum(c.resultado == clave for c in casos) for clave in RESULTADOS}
    icono = "❌" if cuenta["failed"] else "✅"
    totales = " · ".join(f"{n} {clave}" for clave, n in totales_a_mostrar(cuenta))
    segundos = sum(c.segundos for c in casos)

    lineas = [
        f"## {icono} {titulo}",
        "",
        f"**{totales}** · {len(casos)} pruebas en {segundos:.1f} s",
        "",
        "| Resultado | Prueba | Suite | Tiempo | Detalle |",
        "|---|---|---|---:|---|",
    ]
    orden = list(RESULTADOS)
    for c in sorted(casos, key=lambda c: orden.index(c.resultado)):
        lineas.append(
            f"| {RESULTADOS[c.resultado]} | {_celda(c.nombre)} | {_celda(c.suite)} "
            f"| {c.segundos:.1f} s | {_celda(c.detalle)} |"
        )
    return "\n".join(lineas) + "\n"


def main() -> None:
    if len(sys.argv) != 3:
        sys.exit('Uso: python resumen_junit.py "<título>" <reporte.xml>')
    texto = resumen_markdown(sys.argv[1], Path(sys.argv[2]))

    destino = os.getenv("GITHUB_STEP_SUMMARY")
    if destino:
        with open(destino, "a", encoding="utf-8") as resumen:
            resumen.write(texto + "\n")
    else:
        sys.stdout.reconfigure(encoding="utf-8")
        print(texto)


if __name__ == "__main__":
    main()
