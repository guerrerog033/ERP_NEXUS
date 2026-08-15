from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from aplicacion.modulos.inventario.servicios import (
    ServicioInventario,
)


def test_sembrar_existencias_omitido_si_ya_existen():

    db = MagicMock()

    db.query.return_value.first.return_value = 1

    with patch(
        "aplicacion.modulos.inventario.servicios.SessionLocal",
        return_value=db,
    ):

        ServicioInventario.sembrar_existencias_desde_productos()

    db.add.assert_not_called()


def test_actualizar_existencia_bodega_rechaza_salida_sin_stock():

    db = MagicMock()
    producto = MagicMock()
    producto.id = 1

    with patch.object(
        ServicioInventario,
        "_buscar_existencia_bodega",
        return_value=None,
    ):

        with pytest.raises(
            ValueError,
            match="Stock insuficiente",
        ):

            ServicioInventario._actualizar_existencia_bodega(
                db,
                bodega_id=1,
                producto=producto,
                variante=None,
                cantidad=5,
                sumar=False,
            )


def test_bodega_operacion_usa_config_ventas():

    db = MagicMock()
    bodega = MagicMock()
    bodega.id = 7

    with patch(
        "aplicacion.modulos.inventario.servicios.Configuracion.obtener",
        return_value=7,
    ), patch.object(
        ServicioInventario,
        "_resolver_bodega",
        return_value=bodega,
    ) as mock_resolver:

        resultado = ServicioInventario._bodega_operacion(
            db,
            contexto="ventas",
        )

    assert resultado is bodega
    mock_resolver.assert_called_once_with(
        db,
        7,
    )


def test_obtener_existencia_por_bodega_sin_registro():

    db = MagicMock()
    producto = MagicMock()
    producto.id = 10

    with patch.object(
        ServicioInventario,
        "_resolver_bodega",
    ) as mock_bodega, patch.object(
        ServicioInventario,
        "_buscar_existencia_bodega",
        return_value=None,
    ):

        mock_bodega.return_value.id = 3

        existencia, variante = (
            ServicioInventario._obtener_existencia(
                db,
                producto,
                None,
                bodega_id=3,
            )
        )

    assert existencia == 0
    assert variante is None
