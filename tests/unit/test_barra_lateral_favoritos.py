from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import patch

from aplicacion.interfaz.barra_lateral import BarraLateral


def _qapp():
    from PySide6.QtWidgets import QApplication

    app = QApplication.instance()

    if app is None:
        app = QApplication([])

    return app


def _navegacion_falsa(favoritos):

    return SimpleNamespace(
        favoritos=lambda: list(
            favoritos,
        ),
        etiqueta=lambda modulo_id: modulo_id,
    )


def _etiquetas_visibles(barra: BarraLateral) -> list[str]:

    return [
        etiqueta.text()
        for etiqueta in barra._etiquetas_acceso
    ]


def test_accesos_rapidos_no_muestra_recientes_con_favoritos(
    monkeypatch,
):

    _qapp()

    barra = BarraLateral()

    with patch(
        "aplicacion.framework.app_context.AppContext.navegacion",
        _navegacion_falsa(
            ["Clientes"],
        ),
    ):

        monkeypatch.setattr(
            "aplicacion.interfaz.barra_lateral.modulo_accesible",
            lambda _modulo_id: True,
        )

        barra.actualizar_accesos_rapidos()

    etiquetas = _etiquetas_visibles(
        barra,
    )

    assert etiquetas == ["FAVORITOS"]
    assert "RECIENTES" not in etiquetas
    assert not barra._contenedor_accesos.isHidden()


def test_accesos_rapidos_oculto_sin_favoritos(
    monkeypatch,
):

    _qapp()

    barra = BarraLateral()

    with patch(
        "aplicacion.framework.app_context.AppContext.navegacion",
        _navegacion_falsa(
            [],
        ),
    ):

        monkeypatch.setattr(
            "aplicacion.interfaz.barra_lateral.modulo_accesible",
            lambda _modulo_id: True,
        )

        barra.actualizar_accesos_rapidos()

    assert _etiquetas_visibles(
        barra,
    ) == []
    assert barra._contenedor_accesos.isHidden()


def test_navegacion_usuario_ya_no_tiene_recientes():

    from aplicacion.interfaz.navegacion_usuario import (
        NavegacionUsuario,
    )

    assert not hasattr(
        NavegacionUsuario,
        "recientes",
    )
    assert not hasattr(
        NavegacionUsuario,
        "registrar_visita",
    )
