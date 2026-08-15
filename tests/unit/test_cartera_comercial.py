from __future__ import annotations

from unittest.mock import MagicMock, patch

from aplicacion.modulos.cartera.servicios import (
    ServicioCartera,
)


@patch.object(
    ServicioCartera,
    "listar_cxc",
)
def test_resumen_cliente_cxc_agrega_totales(
    mock_listar,
):
    mock_listar.return_value = [
        {
            "saldo": 100000.0,
            "dias_mora": 0,
        },
        {
            "saldo": 50000.0,
            "dias_mora": 15,
        },
    ]

    resumen = ServicioCartera.resumen_cliente_cxc(
        5,
    )

    assert resumen["saldo_total"] == 150000.0
    assert resumen["saldo_vencido"] == 50000.0
    assert resumen["facturas_pendientes"] == 2
    assert len(
        resumen["filas"],
    ) == 2

    mock_listar.assert_called_once_with(
        tercero_id=5,
    )


@patch.object(
    ServicioCartera,
    "listar_cxc",
    return_value=[],
)
def test_resumen_cliente_cxc_sin_saldos(
    mock_listar,
):
    resumen = ServicioCartera.resumen_cliente_cxc(
        99,
    )

    assert resumen["saldo_total"] == 0
    assert resumen["saldo_vencido"] == 0
    assert resumen["facturas_pendientes"] == 0

    mock_listar.assert_called_once_with(
        tercero_id=99,
    )


def test_consultar_cliente_cxc_configura_filtros_y_consulta(
    qapp,
):
    from aplicacion.modulos.cartera.estado_cuenta.vista import (
        CarteraEstadoCuentaPage,
    )

    pagina = CarteraEstadoCuentaPage()

    llamadas: dict[str, object] = {}

    pagina._cambiar_tipo = lambda: llamadas.update(
        cambiar_tipo=True,
    )
    pagina.lookup_cliente.setValue = lambda tercero_id: llamadas.update(
        tercero_id=tercero_id,
    )
    pagina.lookup_cliente.valor = lambda: 42
    pagina._consultar = lambda: llamadas.update(
        consultar=True,
    )

    pagina.consultar_cliente_cxc(
        42,
    )

    assert pagina.tipo.currentData() == "cxc"
    assert llamadas["tercero_id"] == 42
    assert llamadas.get("cambiar_tipo") is True
    assert llamadas.get("consultar") is True


def test_consultar_cliente_cxc_usa_fallback_directo(
    qapp,
    monkeypatch,
):
    from aplicacion.modulos.cartera.estado_cuenta.vista import (
        CarteraEstadoCuentaPage,
    )
    from aplicacion.modulos.cartera.servicios import (
        ServicioCartera,
    )

    pagina = CarteraEstadoCuentaPage()

    pagina.lookup_cliente.setValue = lambda _id: None
    pagina.lookup_cliente.valor = lambda: None

    mock_directo = MagicMock()
    monkeypatch.setattr(
        pagina,
        "_consultar_cxc_directo",
        mock_directo,
    )

    pagina.consultar_cliente_cxc(
        99,
    )

    mock_directo.assert_called_once_with(
        99,
    )


def test_estado_cuenta_modo_bloqueado_oculta_consulta(
    qapp,
):
    from aplicacion.modulos.cartera.estado_cuenta.vista import (
        CarteraEstadoCuentaPage,
    )

    pagina = CarteraEstadoCuentaPage(
        bloquear_tercero=True,
    )

    assert not pagina.tipo.isEnabled()
    assert not pagina.lookup_cliente.isEnabled()
    assert pagina._btn_consultar.isHidden()


@patch.object(
    ServicioCartera,
    "resumen_cliente_cxc",
)
def test_mostrar_cartera_ofrece_detalle_con_saldo(
    mock_resumen,
    monkeypatch,
):
    from aplicacion.modulos.cartera.ui_comercial import (
        mostrar_cartera_cliente,
    )

    mock_resumen.return_value = {
        "saldo_total": 50000.0,
        "saldo_vencido": 10000.0,
        "facturas_pendientes": 2,
        "filas": [],
    }

    llamadas: list[str] = []

    monkeypatch.setattr(
        "aplicacion.modulos.cartera.ui_comercial.QMessageBox.information",
        lambda *args, **kwargs: None,
    )
    monkeypatch.setattr(
        "aplicacion.modulos.cartera.ui_comercial.QMessageBox.question",
        lambda *args, **kwargs: __import__(
            "PySide6.QtWidgets",
            fromlist=["QMessageBox"],
        ).QMessageBox.StandardButton.Yes,
    )
    monkeypatch.setattr(
        "aplicacion.modulos.cartera.ui_comercial.mostrar_estado_cuenta_cliente",
        lambda *args, **kwargs: llamadas.append(
            "detalle",
        ),
    )

    mostrar_cartera_cliente(
        None,
        5,
        nombre_cliente="Cliente Demo",
    )

    assert llamadas == [
        "detalle",
    ]
