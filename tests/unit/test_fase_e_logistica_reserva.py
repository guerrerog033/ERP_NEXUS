from __future__ import annotations

from unittest.mock import MagicMock, patch


@patch(
    "aplicacion.modulos.ventas.pedidos.reservas.Configuracion.obtener",
    return_value=True,
)
def test_reserva_habilitada_por_defecto(
    mock_config,
):

    from aplicacion.modulos.ventas.pedidos.reservas import (
        ServicioReservaPedido,
    )

    assert ServicioReservaPedido.reserva_habilitada() is True

    mock_config.assert_called_once_with(
        "ventas",
        "reservar_stock_pedido",
    )


@patch(
    "aplicacion.modulos.ventas.pedidos.reservas.Configuracion.obtener",
    return_value=False,
)
def test_reservar_falla_si_deshabilitado(
    _mock_config,
):

    from aplicacion.modulos.ventas.pedidos.reservas import (
        ServicioReservaPedido,
    )

    try:

        ServicioReservaPedido.reservar(1)

    except ValueError as error:

        assert "deshabilitada" in str(error).lower()

    else:

        raise AssertionError(
            "Se esperaba ValueError",
        )


@patch(
    "aplicacion.modulos.ventas.pedidos.reservas.Configuracion.obtener",
    return_value=True,
)
def test_liberar_sin_reserva_falla(
    _mock_config,
):

    from aplicacion.modulos.ventas.pedidos.reservas import (
        ServicioReservaPedido,
    )

    pedido = MagicMock()
    pedido.reserva_aplicada = False

    query = MagicMock()
    query.filter.return_value = query
    query.first.return_value = pedido

    db = MagicMock()
    db.query.return_value = query

    with patch(
        "aplicacion.modulos.ventas.pedidos.reservas.SessionLocal",
        return_value=db,
    ):

        try:

            ServicioReservaPedido.liberar(1)

        except ValueError as error:

            assert "no tiene reserva" in str(error).lower()

        else:

            raise AssertionError(
                "Se esperaba ValueError",
            )


def test_listar_despachos_devuelve_filas():

    from aplicacion.modulos.logistica.despacho.servicios import (
        ServicioDespacho,
    )

    despacho = MagicMock()
    despacho.id = 1
    despacho.numero = "DES000001"
    despacho.pedido_id = 10
    despacho.remision_id = 5
    despacho.estado = "despachado"
    despacho.ciudad = "Bogotá"
    despacho.transportadora = "Transportes SA"
    despacho.conductor = "Juan Pérez"
    despacho.fecha_programada = None

    query = MagicMock()
    query.outerjoin.return_value = query
    query.filter.return_value = query
    query.order_by.return_value = query
    query.all.return_value = [
        (despacho, "REM000010"),
    ]

    db = MagicMock()
    db.query.return_value = query

    with patch(
        "aplicacion.modulos.logistica.despacho.servicios.SessionLocal",
        return_value=db,
    ):

        filas = ServicioDespacho.listar()

    assert len(filas) == 1
    assert filas[0]["numero"] == "DES000001"
    assert filas[0]["remision_numero"] == "REM000010"
    assert filas[0]["pedido_id"] == 10
