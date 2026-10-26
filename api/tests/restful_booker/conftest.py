"""Fixtures para Restful Booker: una API pública de reservas de hotel creada para practicar pruebas.

Documentación: https://restful-booker.herokuapp.com/apidoc/index.html
Es COMPARTIDA: otras personas crean y borran reservas al mismo tiempo. Por eso cada prueba
crea sus propios datos (con un nombre único) y los elimina al terminar.
"""

import os

import httpx
import pytest

from tests.restful_booker.datos import ADMIN

BOOKER_URL = os.getenv("BOOKER_URL", "https://restful-booker.herokuapp.com")


def pytest_collection_modifyitems(items):
    """Copia las etiquetas @HU-xx y @CP-xx de cada escenario al JUnit XML (matriz de trazabilidad)."""
    for item in items:
        for marca in item.iter_markers():
            if marca.name.startswith(("HU-", "CP-")):
                item.user_properties.append((marca.name[:2], marca.name))


@pytest.fixture(scope="session")
def booker():
    """Cliente HTTP de Restful Booker. Por defecto pide las respuestas en JSON."""
    with httpx.Client(base_url=BOOKER_URL, timeout=30, headers={"Accept": "application/json"}) as cliente:
        yield cliente


@pytest.fixture(scope="session")
def token_booker(booker):
    """Token de administrador: se envía en la cabecera Cookie (token=...)."""
    respuesta = booker.post("/auth", json={"username": ADMIN[0], "password": ADMIN[1]})
    assert respuesta.status_code == 200
    return respuesta.json()["token"]
