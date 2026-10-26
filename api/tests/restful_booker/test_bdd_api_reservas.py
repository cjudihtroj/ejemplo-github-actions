"""DEMO con pytest-bdd: escenarios Gherkin de la API de reservas.

Cada escenario envía UNA solicitud (el When) y verifica solo la respuesta (los Then).
"""

import pytest
from pytest_bdd import given, parsers, scenarios, then, when

from tests.restful_booker.datos import datos_de_reserva

pytestmark = pytest.mark.booker

scenarios("features/api_reservas.feature")


@pytest.fixture
def contexto():
    """Estado compartido entre los pasos de un escenario: la reserva preparada y la respuesta."""
    return {}


@pytest.fixture
def reservas_creadas(booker, token_booker):
    """Reservas que crea el escenario: se eliminan al terminar (aunque el escenario falle)."""
    ids = []
    yield ids
    for reserva_id in ids:
        booker.delete(f"/booking/{reserva_id}", headers={"Cookie": f"token={token_booker}"})


# ---------------------------------------------------------------- Given: preparar


@given(parsers.parse('que existe una reserva a nombre de "{apellido}" con precio total {precio:d}'))
def reserva_existente(booker, contexto, reservas_creadas, apellido, precio):
    respuesta = booker.post("/booking", json=datos_de_reserva(lastname=apellido, totalprice=precio))
    assert respuesta.status_code == 200, respuesta.text
    contexto["reserva_id"] = respuesta.json()["bookingid"]
    reservas_creadas.append(contexto["reserva_id"])


# ---------------------------------------------------------------- When: una sola solicitud


@when("se consulta la reserva por su identificador")
def consultar_reserva_preparada(booker, contexto):
    contexto["respuesta"] = booker.get(f"/booking/{contexto['reserva_id']}")


@when(parsers.parse("se consulta la reserva con identificador {reserva_id:d}"))
def consultar_reserva(booker, contexto, reserva_id):
    contexto["respuesta"] = booker.get(f"/booking/{reserva_id}")


@when(parsers.parse('se crea una reserva a nombre de "{apellido}" con precio total {precio:d}'))
def crear_reserva(booker, contexto, reservas_creadas, apellido, precio):
    contexto["respuesta"] = booker.post("/booking", json=datos_de_reserva(lastname=apellido, totalprice=precio))
    if contexto["respuesta"].status_code == 200:
        reservas_creadas.append(contexto["respuesta"].json()["bookingid"])


@when("se elimina la reserva sin token")
def eliminar_sin_token(booker, contexto):
    contexto["respuesta"] = booker.delete(f"/booking/{contexto['reserva_id']}")


# ---------------------------------------------------------------- Then: verificar la respuesta


@then(parsers.parse("la respuesta tiene el estado {estado:d}"))
def estado_de_la_respuesta(contexto, estado):
    assert contexto["respuesta"].status_code == estado, contexto["respuesta"].text


@then(parsers.parse('la respuesta tiene el apellido "{apellido}" y el precio total {precio:d}'))
def datos_de_la_respuesta(contexto, apellido, precio):
    cuerpo = contexto["respuesta"].json()
    assert cuerpo["lastname"] == apellido
    assert cuerpo["totalprice"] == precio


@then("la respuesta incluye el identificador de la nueva reserva")
def identificador_de_la_respuesta(contexto):
    assert isinstance(contexto["respuesta"].json()["bookingid"], int)
