from __future__ import annotations

from datetime import datetime, timedelta
from types import SimpleNamespace

from aplicacion.api.sesion_movil import ServicioSesionMovil


def _usuario(nombre="Ana Prueba", usuario="ana"):

    return SimpleNamespace(
        id=1,
        nombre=nombre,
        usuario=usuario,
    )


def test_iniciar_sesion_genera_token_recuperable():

    token = ServicioSesionMovil.iniciar_sesion(
        _usuario(),
    )

    sesion = ServicioSesionMovil.obtener_sesion(
        token,
    )

    assert sesion is not None
    assert sesion["nombre"] == "Ana Prueba"

    ServicioSesionMovil.cerrar_sesion(token)


def test_obtener_sesion_usa_usuario_como_nombre_si_falta_nombre():

    token = ServicioSesionMovil.iniciar_sesion(
        _usuario(nombre="", usuario="pepito"),
    )

    sesion = ServicioSesionMovil.obtener_sesion(
        token,
    )

    assert sesion["nombre"] == "pepito"

    ServicioSesionMovil.cerrar_sesion(token)


def test_obtener_sesion_token_invalido_retorna_none():

    assert (
        ServicioSesionMovil.obtener_sesion(
            "token-que-no-existe",
        )
        is None
    )


def test_obtener_sesion_token_vacio_retorna_none():

    assert ServicioSesionMovil.obtener_sesion("") is None


def test_cerrar_sesion_invalida_el_token():

    token = ServicioSesionMovil.iniciar_sesion(
        _usuario(),
    )

    ServicioSesionMovil.cerrar_sesion(token)

    assert (
        ServicioSesionMovil.obtener_sesion(
            token,
        )
        is None
    )


def test_sesion_expirada_retorna_none():

    token = ServicioSesionMovil.iniciar_sesion(
        _usuario(),
    )

    ServicioSesionMovil._sesiones[token][
        "expira_en"
    ] = datetime.now() - timedelta(minutes=1)

    assert (
        ServicioSesionMovil.obtener_sesion(
            token,
        )
        is None
    )
