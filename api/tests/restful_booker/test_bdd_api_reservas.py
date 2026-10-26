"""DEMO con pytest-bdd: escenarios Gherkin de la API de reservas.

Cada escenario envía UNA solicitud (el When) y verifica solo la respuesta (los Then).
"""

import pytest
from pytest_bdd import given, parsers, scenario, scenarios, then, when

from tests.restful_booker.datos import datos_de_reserva

pytestmark = pytest.mark.booker

FEATURE = "features/api_reservas.feature"


# ---------------------------------------------------------------- Defectos reportados
# Estos escenarios hoy fallan por un defecto conocido de Restful Booker. Quedan como fallo esperado
# (xfail estricto): el pipeline sigue en verde y, si el defecto se corrige, el escenario pasa y avisa.


@pytest.mark.xfail(reason="D-01: POST /booking con datos incompletos responde 500 en vez de 400", strict=True)
@scenario(FEATURE, "Crear una reserva con datos incompletos")
def test_crear_una_reserva_con_datos_incompletos():
    pass


@pytest.mark.xfail(reason="D-02: POST /booking acepta una salida anterior a la entrada (200 en vez de 400)", strict=True)
@scenario(FEATURE, "Crear una reserva con la salida antes que la entrada")
def test_crear_una_reserva_con_la_salida_antes_que_la_entrada():
    pass


@pytest.mark.xfail(reason="D-03: POST /booking acepta un precio total negativo (200 en vez de 400)", strict=True)
@scenario(FEATURE, "Crear una reserva con precio negativo")
def test_crear_una_reserva_con_precio_negativo():
    pass


@pytest.mark.xfail(reason="D-04: POST /auth con clave incorrecta responde 200 'Bad credentials' en vez de 401", strict=True)
@scenario(FEATURE, "Obtener un token con una clave incorrecta")
def test_obtener_un_token_con_una_clave_incorrecta():
    pass


scenarios(FEATURE)  # el resto de escenarios del archivo (va después de los vinculados a mano)


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


def _crear(booker, contexto, reservas_creadas, datos):
    """POST /booking. Si la reserva se crea (aunque no debía), se registra para eliminarla al terminar."""
    contexto["respuesta"] = booker.post("/booking", json=datos)
    if contexto["respuesta"].status_code == 200:
        reservas_creadas.append(contexto["respuesta"].json()["bookingid"])


@when(parsers.parse('se crea una reserva a nombre de "{apellido}" con precio total {precio:d}'))
def crear_reserva(booker, contexto, reservas_creadas, apellido, precio):
    _crear(booker, contexto, reservas_creadas, datos_de_reserva(lastname=apellido, totalprice=precio))


@when(parsers.parse('se crea una reserva con entrada "{entrada}" y salida "{salida}"'))
def crear_reserva_con_fechas(booker, contexto, reservas_creadas, entrada, salida):
    fechas = {"checkin": entrada, "checkout": salida}
    _crear(booker, contexto, reservas_creadas, datos_de_reserva(bookingdates=fechas))


@when("se crea una reserva solo con el nombre")
def crear_reserva_incompleta(booker, contexto, reservas_creadas):
    _crear(booker, contexto, reservas_creadas, {"firstname": "SoloNombre"})


@when("se elimina la reserva sin token")
def eliminar_sin_token(booker, contexto):
    contexto["respuesta"] = booker.delete(f"/booking/{contexto['reserva_id']}")


@when(parsers.parse('se solicita un token con usuario "{usuario}" y clave "{clave}"'))
def solicitar_token(booker, contexto, usuario, clave):
    contexto["respuesta"] = booker.post("/auth", json={"username": usuario, "password": clave})


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
