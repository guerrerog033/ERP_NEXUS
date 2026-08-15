from __future__ import annotations

from unittest.mock import MagicMock, patch


@patch(
    "aplicacion.modulos.ventas.guias_remision.servicios.Configuracion.obtener",
    return_value=True,
)
def test_validar_guia_sin_emitir_falla(
    _mock_config,
):

    from aplicacion.modulos.ventas.guias_remision.servicios import (
        ServicioGuiaRemisionElectronica,
    )

    guia = MagicMock()
    guia.numero = "GRE000001"
    guia.estado = "borrador"

    with patch.object(
        ServicioGuiaRemisionElectronica,
        "obtener_por_remision",
        return_value=guia,
    ):

        try:

            ServicioGuiaRemisionElectronica.validar_guia_emitida_remision(
                1,
            )

        except ValueError as error:

            assert "emitida" in str(error).lower()

        else:

            raise AssertionError(
                "Se esperaba ValueError",
            )


@patch(
    "aplicacion.modulos.ventas.guias_remision.servicios.Configuracion.obtener",
    return_value=True,
)
def test_validar_guia_emitida_ok(
    _mock_config,
):

    from aplicacion.modulos.ventas.guias_remision.servicios import (
        ServicioGuiaRemisionElectronica,
    )

    with patch.object(
        ServicioGuiaRemisionElectronica,
        "guia_emitida_para_remision",
        return_value=True,
    ):

        ServicioGuiaRemisionElectronica.validar_guia_emitida_remision(
            1,
        )


@patch(
    "aplicacion.modulos.logistica.despacho.servicios.ServicioDespacho._validar_guia_para_estado",
)
def test_cambiar_estado_entregado_valida_guia(
    mock_validar,
):

    from aplicacion.modulos.logistica.despacho.servicios import (
        ServicioDespacho,
    )

    despacho = MagicMock()
    despacho.remision_id = 5
    despacho.pedido_id = 10

    query = MagicMock()
    query.filter.return_value = query
    query.first.return_value = despacho

    db = MagicMock()
    db.query.return_value = query

    with patch(
        "aplicacion.modulos.logistica.despacho.servicios.SessionLocal",
        return_value=db,
    ):

        ServicioDespacho.cambiar_estado(
            1,
            "entregado",
        )

    mock_validar.assert_called_once_with(
        5,
        "entregado",
    )
