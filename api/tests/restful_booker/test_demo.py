"""DEMO EN VIVO: casos del Ejercicio 2 automatizados (C1, C3, C7 y C9) y hallazgos del Ejercicio 3.

La reserva de la fixture tiene lastname "Utec", checkin 2026-11-10 y checkout 2026-11-15.
"""

import pytest

from tests.restful_booker.datos import datos_de_reserva

pytestmark = pytest.mark.booker


# ---------------------------------------------------------------- GET /booking: parámetros de consulta


def test_c1_filtrar_por_nombre_y_apellido(booker, reserva):
    filtros = {"firstname": reserva["datos"]["firstname"], "lastname": "Utec"}

    respuesta = booker.get("/booking", params=filtros)  # → /booking?firstname=Prueba1a2b3c4d&lastname=Utec

    assert respuesta.status_code == 200
    assert respuesta.json() == [{"bookingid": reserva["id"]}]


@pytest.mark.xfail(reason="Hallazgo D: el filtro checkin excluye la fecha límite (doc: 'mayor o igual')", strict=True)
def test_c3_filtro_checkin_incluye_la_fecha_exacta(booker, reserva):
    filtros = {"firstname": reserva["datos"]["firstname"], "checkin": "2026-11-10"}

    respuesta = booker.get("/booking", params=filtros)

    assert respuesta.json() == [{"bookingid": reserva["id"]}]


# ---------------------------------------------------------------- PUT /booking/{id}: ruta, cabeceras y cuerpo


def test_c7_reemplazar_con_token_en_la_cookie(booker, reserva, token_booker):
    nuevos = datos_de_reserva(firstname=reserva["datos"]["firstname"], totalprice=200)

    respuesta = booker.put(f"/booking/{reserva['id']}", json=nuevos, headers={"Cookie": f"token={token_booker}"})

    assert respuesta.status_code == 200
    assert respuesta.json()["totalprice"] == 200
    assert booker.get(f"/booking/{reserva['id']}").json()["totalprice"] == 200  # efecto


def test_c9_reemplazar_sin_autenticacion_no_cambia_nada(booker, reserva):
    nuevos = datos_de_reserva(firstname=reserva["datos"]["firstname"], totalprice=200)

    respuesta = booker.put(f"/booking/{reserva['id']}", json=nuevos)

    assert respuesta.status_code == 403
    assert booker.get(f"/booking/{reserva['id']}").json()["totalprice"] == 120  # sin efecto


# ---------------------------------------------------------------- Hallazgos del Ejercicio 3


@pytest.mark.xfail(reason="Hallazgo B: credenciales incorrectas responden 200 'Bad credentials'", strict=True)
def test_hallazgo_b_credenciales_incorrectas_responden_401(booker):
    respuesta = booker.post("/auth", json={"username": "admin", "password": "incorrecta"})

    assert respuesta.status_code == 401


@pytest.mark.xfail(reason="Hallazgo C: POST con cuerpo incompleto provoca 500", strict=True)
def test_hallazgo_c_post_incompleto_responde_400(booker):
    respuesta = booker.post("/booking", json={"firstname": "SoloNombre"})

    assert respuesta.status_code == 400


@pytest.mark.xfail(reason="Hallazgo E: la respuesta en XML declara Content-Type text/html", strict=True)
def test_hallazgo_e_respuesta_xml_declara_content_type_xml(booker, reserva):
    respuesta = booker.get(f"/booking/{reserva['id']}", headers={"Accept": "application/xml"})

    assert "xml" in respuesta.headers["content-type"]
