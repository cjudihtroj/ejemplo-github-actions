"""Datos de prueba para Restful Booker."""

import uuid

ADMIN = ("admin", "password123")


def datos_de_reserva(**cambios) -> dict:
    """Cuerpo válido de una reserva, con un nombre único para no chocar con datos de otras personas."""
    datos = {
        "firstname": f"Prueba{uuid.uuid4().hex[:8]}",
        "lastname": "Utec",
        "totalprice": 120,
        "depositpaid": True,
        "bookingdates": {"checkin": "2026-11-10", "checkout": "2026-11-15"},
        "additionalneeds": "Desayuno",
    }
    datos.update(cambios)
    return datos
