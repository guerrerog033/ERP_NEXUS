from __future__ import annotations

from unittest.mock import MagicMock, patch


@patch(
    "aplicacion.modulos.compras.facturas.repositorio_eventos_radian.SessionLocal",
)
def test_listar_por_factura_orden_desc(
    mock_session,
):

    from aplicacion.modulos.compras.facturas.repositorio_eventos_radian import (
        RepositorioFacturaCompraEventoRadian,
    )

    evento_nuevo = MagicMock()
    evento_nuevo.codigo_evento = "031"

    evento_viejo = MagicMock()
    evento_viejo.codigo_evento = "030"

    query = MagicMock()
    query.filter.return_value = query
    query.order_by.return_value = query
    query.all.return_value = [
        evento_nuevo,
        evento_viejo,
    ]

    db = MagicMock()
    db.query.return_value = query
    mock_session.return_value = db

    eventos = (
        RepositorioFacturaCompraEventoRadian
        .listar_por_factura(
            5,
        )
    )

    assert len(eventos) == 2
    assert eventos[0].codigo_evento == "031"
    db.close.assert_called_once()


@patch(
    "aplicacion.modulos.compras.facturas.repositorio_eventos_radian.SessionLocal",
)
def test_existe_exitoso_consulta_estado(
    mock_session,
):

    from aplicacion.modulos.compras.facturas.repositorio_eventos_radian import (
        RepositorioFacturaCompraEventoRadian,
    )

    query = MagicMock()
    query.filter.return_value = query
    query.first.return_value = MagicMock()

    db = MagicMock()
    db.query.return_value = query
    mock_session.return_value = db

    assert RepositorioFacturaCompraEventoRadian.existe_exitoso(
        3,
        "033",
    )

    db.close.assert_called_once()


@patch(
    "aplicacion.integraciones.dian.programador_radian.Configuracion.obtener",
    return_value={
        "habilitado": True,
        "modo_automatico": True,
    },
)
def test_programador_radian_033_habilitado(
    _mock_config,
):

    from aplicacion.integraciones.dian.programador_radian import (
        ProgramadorRadian033,
    )

    assert ProgramadorRadian033.modo_automatico_habilitado()
