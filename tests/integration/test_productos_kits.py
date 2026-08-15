from __future__ import annotations

import os
import uuid

import pytest

from aplicacion.base_datos.registro_modelos import (
    importar_modelos,
)


pytestmark = pytest.mark.integration


@pytest.fixture(
    scope="session",
    autouse=True,
)
def _registrar_modelos():

    importar_modelos()


@pytest.fixture(
    scope="session",
)
def requiere_postgresql():

    if not os.getenv(
        "DB_HOST",
    ):

        pytest.skip(
            "DB_HOST no configurado",
        )


def _crear_producto(sufijo: str, **extra) -> object:
    from aplicacion.maestros.productos.servicios import (
        ServicioProducto,
    )

    datos = {
        "codigo": f"KIT{sufijo.upper()}",
        "nombre": f"Producto Kit Demo {sufijo}",
        "tipo": "producto",
        "precio_venta": 1000,
        "precio_incluye_iva": False,
        "costo": 500,
        "existencia": 0,
        "stock_minimo": 0,
        "activo": True,
        "maneja_variantes": False,
    }
    datos.update(extra)

    return ServicioProducto.guardar_completo(
        datos,
    )


def test_agregar_componente_y_expandir(
    requiere_postgresql,
):
    from aplicacion.maestros.productos.kit_servicio import (
        ServicioProductoKit,
    )

    sufijo = uuid.uuid4().hex[:8]

    kit = _crear_producto(
        sufijo,
        es_kit=True,
    )
    tornillo = _crear_producto(
        f"{sufijo}T",
    )
    tuerca = _crear_producto(
        f"{sufijo}N",
    )

    ServicioProductoKit.guardar(
        {
            "kit_id": kit.id,
            "componente_id": tornillo.id,
            "cantidad": 4,
        },
    )
    ServicioProductoKit.guardar(
        {
            "kit_id": kit.id,
            "componente_id": tuerca.id,
            "cantidad": 4,
        },
    )

    expandido = ServicioProductoKit.expandir(
        kit.id,
        cantidad=3,
    )

    por_producto = {
        c.producto_id: c.cantidad_total
        for c in expandido
    }

    assert por_producto[tornillo.id] == 12
    assert por_producto[tuerca.id] == 12


def test_expandir_kit_sin_componentes_devuelve_vacio(
    requiere_postgresql,
):
    from aplicacion.maestros.productos.kit_servicio import (
        ServicioProductoKit,
    )

    sufijo = uuid.uuid4().hex[:8]

    kit = _crear_producto(
        sufijo,
        es_kit=True,
    )

    assert (
        ServicioProductoKit.expandir(
            kit.id,
        )
        == []
    )


def test_rechaza_kit_como_su_propio_componente(
    requiere_postgresql,
):
    from aplicacion.maestros.productos.kit_servicio import (
        ServicioProductoKit,
    )

    sufijo = uuid.uuid4().hex[:8]

    kit = _crear_producto(
        sufijo,
        es_kit=True,
    )

    with pytest.raises(
        ValueError,
        match="a sí mismo",
    ):

        ServicioProductoKit.guardar(
            {
                "kit_id": kit.id,
                "componente_id": kit.id,
                "cantidad": 1,
            },
        )


def test_rechaza_kits_anidados(
    requiere_postgresql,
):
    from aplicacion.maestros.productos.kit_servicio import (
        ServicioProductoKit,
    )

    sufijo = uuid.uuid4().hex[:8]

    kit_a = _crear_producto(
        f"{sufijo}A",
        es_kit=True,
    )
    kit_b = _crear_producto(
        f"{sufijo}B",
        es_kit=True,
    )

    with pytest.raises(
        ValueError,
        match="kits anidados",
    ):

        ServicioProductoKit.guardar(
            {
                "kit_id": kit_a.id,
                "componente_id": kit_b.id,
                "cantidad": 1,
            },
        )


def test_rechaza_componente_duplicado(
    requiere_postgresql,
):
    from aplicacion.maestros.productos.kit_servicio import (
        ServicioProductoKit,
    )

    sufijo = uuid.uuid4().hex[:8]

    kit = _crear_producto(
        sufijo,
        es_kit=True,
    )
    tornillo = _crear_producto(
        f"{sufijo}T",
    )

    ServicioProductoKit.guardar(
        {
            "kit_id": kit.id,
            "componente_id": tornillo.id,
            "cantidad": 1,
        },
    )

    with pytest.raises(
        ValueError,
        match="ya está agregado",
    ):

        ServicioProductoKit.guardar(
            {
                "kit_id": kit.id,
                "componente_id": tornillo.id,
                "cantidad": 2,
            },
        )


def test_rechaza_cantidad_no_positiva(
    requiere_postgresql,
):
    from aplicacion.maestros.productos.kit_servicio import (
        ServicioProductoKit,
    )

    sufijo = uuid.uuid4().hex[:8]

    kit = _crear_producto(
        sufijo,
        es_kit=True,
    )
    tornillo = _crear_producto(
        f"{sufijo}T",
    )

    with pytest.raises(
        ValueError,
        match="mayor a cero",
    ):

        ServicioProductoKit.guardar(
            {
                "kit_id": kit.id,
                "componente_id": tornillo.id,
                "cantidad": 0,
            },
        )


def test_eliminar_componente(
    requiere_postgresql,
):
    from aplicacion.maestros.productos.kit_servicio import (
        ServicioProductoKit,
    )

    sufijo = uuid.uuid4().hex[:8]

    kit = _crear_producto(
        sufijo,
        es_kit=True,
    )
    tornillo = _crear_producto(
        f"{sufijo}T",
    )

    componente = ServicioProductoKit.guardar(
        {
            "kit_id": kit.id,
            "componente_id": tornillo.id,
            "cantidad": 1,
        },
    )

    ServicioProductoKit.eliminar(
        componente.id,
    )

    assert (
        ServicioProductoKit.listar_componentes(
            kit.id,
        )
        == []
    )


def _qapp():
    from PySide6.QtWidgets import QApplication

    app = QApplication.instance()

    if app is None:
        app = QApplication([])

    return app


def test_formulario_edicion_muestra_componentes_del_kit(
    requiere_postgresql,
):
    from aplicacion.maestros.productos.formulario import (
        FormularioProducto,
    )
    from aplicacion.maestros.productos.kit_servicio import (
        ServicioProductoKit,
    )

    _qapp()

    sufijo = uuid.uuid4().hex[:8]

    kit = _crear_producto(
        sufijo,
        es_kit=True,
    )
    tornillo = _crear_producto(
        f"{sufijo}T",
    )

    ServicioProductoKit.guardar(
        {
            "kit_id": kit.id,
            "componente_id": tornillo.id,
            "cantidad": 6,
        },
    )

    form = FormularioProducto(
        id_registro=kit.id,
    )

    assert not form._grupo_kit.isHidden()
    assert form.kit_componentes_widget.tabla.rowCount() == 1
    assert (
        form.kit_componentes_widget.tabla.item(0, 0).text()
        == tornillo.codigo
    )


def test_formulario_edicion_oculta_componentes_si_no_es_kit(
    requiere_postgresql,
):
    from aplicacion.maestros.productos.formulario import (
        FormularioProducto,
    )

    _qapp()

    sufijo = uuid.uuid4().hex[:8]

    producto = _crear_producto(
        sufijo,
    )

    form = FormularioProducto(
        id_registro=producto.id,
    )

    assert form._grupo_kit.isHidden()
