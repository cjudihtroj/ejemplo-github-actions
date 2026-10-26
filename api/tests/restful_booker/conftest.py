"""Fixtures para Restful Booker: una API pública de reservas de hotel creada para practicar pruebas.

Documentación: https://restful-booker.herokuapp.com/apidoc/index.html
Es COMPARTIDA: otras personas crean y borran reservas al mismo tiempo. Por eso cada prueba
crea sus propios datos (con un nombre único) y los elimina al terminar.
"""

import os

import httpx
import pytest

from tests.restful_booker.datos import ADMIN, datos_de_reserva

BOOKER_URL = os.getenv("BOOKER_URL", "https://restful-booker.herokuapp.com")


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


@pytest.fixture
def reserva(booker, token_booker):
    """Crea una reserva propia para la prueba y la elimina al terminar (aunque la prueba falle)."""
    datos = datos_de_reserva()
    respuesta = booker.post("/booking", json=datos)
    assert respuesta.status_code == 200, respuesta.text
    reserva_id = respuesta.json()["bookingid"]
    yield {"id": reserva_id, "datos": datos}
    booker.delete(f"/booking/{reserva_id}", headers={"Cookie": f"token={token_booker}"})
