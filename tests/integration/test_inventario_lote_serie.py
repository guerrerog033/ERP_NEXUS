from __future__ import annotations

import os
import uuid
from unittest.mock import patch

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
        "codigo": f"LS{sufijo.upper()}",
        "nombre": f"Producto Lote/Serie Demo {sufijo}",
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


@pytest.fixture
def bodega_id(
    requiere_postgresql,
):
    from aplicacion.modulos.inventario.servicios import (
        ServicioInventario,
    )

    return ServicioInventario.inicializar_bodega().id


def test_guardar_lote_y_listar(
    requiere_postgresql,
):
    from aplicacion.modulos.inventario.lote_serie_servicio import (
        ServicioLoteSerie,
    )

    sufijo = uuid.uuid4().hex[:8]

    producto = _crear_producto(
        sufijo,
        maneja_lote=True,
    )

    ServicioLoteSerie.guardar(
        {
            "producto_id": producto.id,
            "numero": "L-001",
        },
    )

    lotes = ServicioLoteSerie.listar(
        producto.id,
    )

    assert len(lotes) == 1
    assert lotes[0].tipo == "lote"
    assert lotes[0].numero == "L-001"


def test_rechaza_producto_sin_control_de_lote_ni_serie(
    requiere_postgresql,
):
    from aplicacion.modulos.inventario.lote_serie_servicio import (
        ServicioLoteSerie,
    )

    sufijo = uuid.uuid4().hex[:8]

    producto = _crear_producto(
        sufijo,
    )

    with pytest.raises(
        ValueError,
        match="no está configurado",
    ):

        ServicioLoteSerie.guardar(
            {
                "producto_id": producto.id,
                "numero": "L-001",
            },
        )


def test_rechaza_numero_duplicado_para_el_mismo_producto(
    requiere_postgresql,
):
    from aplicacion.modulos.inventario.lote_serie_servicio import (
        ServicioLoteSerie,
    )

    sufijo = uuid.uuid4().hex[:8]

    producto = _crear_producto(
        sufijo,
        maneja_serie=True,
    )

    ServicioLoteSerie.guardar(
        {
            "producto_id": producto.id,
            "numero": "SN-001",
        },
    )

    with pytest.raises(
        ValueError,
        match="Ya existe",
    ):

        ServicioLoteSerie.guardar(
            {
                "producto_id": producto.id,
                "numero": "SN-001",
            },
        )


def test_mismo_numero_en_productos_distintos_no_choca(
    requiere_postgresql,
):
    from aplicacion.modulos.inventario.lote_serie_servicio import (
        ServicioLoteSerie,
    )

    sufijo = uuid.uuid4().hex[:8]

    producto_a = _crear_producto(
        f"{sufijo}A",
        maneja_lote=True,
    )
    producto_b = _crear_producto(
        f"{sufijo}B",
        maneja_lote=True,
    )

    ServicioLoteSerie.guardar(
        {
            "producto_id": producto_a.id,
            "numero": "L-001",
        },
    )

    # No debe fallar: mismo número, producto distinto.
    ServicioLoteSerie.guardar(
        {
            "producto_id": producto_b.id,
            "numero": "L-001",
        },
    )


def test_rechaza_vencimiento_anterior_a_fabricacion(
    requiere_postgresql,
):
    from datetime import date, timedelta

    from aplicacion.modulos.inventario.lote_serie_servicio import (
        ServicioLoteSerie,
    )

    sufijo = uuid.uuid4().hex[:8]

    producto = _crear_producto(
        sufijo,
        maneja_lote=True,
    )

    hoy = date.today()

    with pytest.raises(
        ValueError,
        match="vencimiento",
    ):

        ServicioLoteSerie.guardar(
            {
                "producto_id": producto.id,
                "numero": "L-001",
                "fecha_fabricacion": hoy,
                "fecha_vencimiento": hoy - timedelta(days=1),
            },
        )


def test_ajuste_entrada_con_lote_incrementa_existencia(
    requiere_postgresql,
    bodega_id,
):
    from aplicacion.modulos.inventario.lote_serie_servicio import (
        ServicioLoteSerie,
    )
    from aplicacion.modulos.inventario.servicios import (
        ServicioInventario,
    )

    sufijo = uuid.uuid4().hex[:8]

    producto = _crear_producto(
        sufijo,
        maneja_lote=True,
    )

    lote = ServicioLoteSerie.guardar(
        {
            "producto_id": producto.id,
            "numero": "L-100",
        },
    )

    ServicioInventario.registrar_ajuste(
        bodega_id=bodega_id,
        producto_id=producto.id,
        tipo="entrada",
        cantidad=10,
        lote_serie_id=lote.id,
    )

    assert (
        ServicioLoteSerie.existencia_total(
            lote.id,
        )
        == 10
    )


def test_ajuste_salida_con_lote_decrementa_existencia(
    requiere_postgresql,
    bodega_id,
):
    from aplicacion.modulos.inventario.lote_serie_servicio import (
        ServicioLoteSerie,
    )
    from aplicacion.modulos.inventario.servicios import (
        ServicioInventario,
    )

    sufijo = uuid.uuid4().hex[:8]

    producto = _crear_producto(
        sufijo,
        maneja_lote=True,
    )

    lote = ServicioLoteSerie.guardar(
        {
            "producto_id": producto.id,
            "numero": "L-200",
        },
    )

    ServicioInventario.registrar_ajuste(
        bodega_id=bodega_id,
        producto_id=producto.id,
        tipo="entrada",
        cantidad=10,
        lote_serie_id=lote.id,
    )

    ServicioInventario.registrar_ajuste(
        bodega_id=bodega_id,
        producto_id=producto.id,
        tipo="salida",
        cantidad=4,
        lote_serie_id=lote.id,
    )

    assert (
        ServicioLoteSerie.existencia_total(
            lote.id,
        )
        == 6
    )


def test_ajuste_salida_totalmente_sin_stock_falla_por_stock_general(
    requiere_postgresql,
    bodega_id,
):
    """
    Sin ninguna entrada previa, la salida falla en el guard
    general de stock (ExistenciaBodega) antes de llegar siquiera
    a mirar el lote específico — capa más gruesa, corre primero.
    """

    from aplicacion.modulos.inventario.lote_serie_servicio import (
        ServicioLoteSerie,
    )
    from aplicacion.modulos.inventario.servicios import (
        ServicioInventario,
    )

    sufijo = uuid.uuid4().hex[:8]

    producto = _crear_producto(
        sufijo,
        maneja_lote=True,
    )

    lote = ServicioLoteSerie.guardar(
        {
            "producto_id": producto.id,
            "numero": "L-300",
        },
    )

    with pytest.raises(
        ValueError,
        match="Stock insuficiente",
    ):

        ServicioInventario.registrar_ajuste(
            bodega_id=bodega_id,
            producto_id=producto.id,
            tipo="salida",
            cantidad=1,
            lote_serie_id=lote.id,
        )

    assert (
        ServicioLoteSerie.existencia_total(
            lote.id,
        )
        == 0
    )


def test_ajuste_salida_de_lote_sin_stock_falla_aunque_otro_lote_si_tenga(
    requiere_postgresql,
    bodega_id,
):
    """
    Con stock general suficiente (cubierto por OTRO lote del
    mismo producto), la salida contra un lote específico sin
    existencia propia debe fallar en la validación de lote/serie,
    no colarse usando el stock de un lote distinto.
    """

    from aplicacion.modulos.inventario.lote_serie_servicio import (
        ServicioLoteSerie,
    )
    from aplicacion.modulos.inventario.servicios import (
        ServicioInventario,
    )

    sufijo = uuid.uuid4().hex[:8]

    producto = _crear_producto(
        sufijo,
        maneja_lote=True,
    )

    lote_con_stock = ServicioLoteSerie.guardar(
        {
            "producto_id": producto.id,
            "numero": "L-310",
        },
    )
    lote_sin_stock = ServicioLoteSerie.guardar(
        {
            "producto_id": producto.id,
            "numero": "L-311",
        },
    )

    ServicioInventario.registrar_ajuste(
        bodega_id=bodega_id,
        producto_id=producto.id,
        tipo="entrada",
        cantidad=10,
        lote_serie_id=lote_con_stock.id,
    )

    with pytest.raises(
        ValueError,
        match="No hay existencia",
    ):

        ServicioInventario.registrar_ajuste(
            bodega_id=bodega_id,
            producto_id=producto.id,
            tipo="salida",
            cantidad=1,
            lote_serie_id=lote_sin_stock.id,
        )

    assert (
        ServicioLoteSerie.existencia_total(
            lote_con_stock.id,
        )
        == 10
    )
    assert (
        ServicioLoteSerie.existencia_total(
            lote_sin_stock.id,
        )
        == 0
    )


def test_ajuste_rechaza_lote_de_otro_producto(
    requiere_postgresql,
    bodega_id,
):
    from aplicacion.modulos.inventario.lote_serie_servicio import (
        ServicioLoteSerie,
    )
    from aplicacion.modulos.inventario.servicios import (
        ServicioInventario,
    )

    sufijo = uuid.uuid4().hex[:8]

    producto_a = _crear_producto(
        f"{sufijo}A",
        maneja_lote=True,
    )
    producto_b = _crear_producto(
        f"{sufijo}B",
        maneja_lote=True,
    )

    lote_de_b = ServicioLoteSerie.guardar(
        {
            "producto_id": producto_b.id,
            "numero": "L-400",
        },
    )

    with pytest.raises(
        ValueError,
        match="no pertenece a este producto",
    ):

        ServicioInventario.registrar_ajuste(
            bodega_id=bodega_id,
            producto_id=producto_a.id,
            tipo="entrada",
            cantidad=1,
            lote_serie_id=lote_de_b.id,
        )


def test_ajuste_sin_lote_serie_sigue_funcionando_igual(
    requiere_postgresql,
    bodega_id,
):
    """
    No debe romperse el flujo normal (sin lote/serie) para
    productos que no lo requieren — lote_serie_id es opcional.
    """

    from aplicacion.modulos.inventario.servicios import (
        ServicioInventario,
    )

    sufijo = uuid.uuid4().hex[:8]

    producto = _crear_producto(
        sufijo,
    )

    movimiento = ServicioInventario.registrar_ajuste(
        bodega_id=bodega_id,
        producto_id=producto.id,
        tipo="entrada",
        cantidad=5,
    )

    assert movimiento.lote_serie_id is None


def test_eliminar_lote(
    requiere_postgresql,
):
    from aplicacion.modulos.inventario.lote_serie_servicio import (
        ServicioLoteSerie,
    )

    sufijo = uuid.uuid4().hex[:8]

    producto = _crear_producto(
        sufijo,
        maneja_lote=True,
    )

    lote = ServicioLoteSerie.guardar(
        {
            "producto_id": producto.id,
            "numero": "L-500",
        },
    )

    ServicioLoteSerie.eliminar(
        lote.id,
    )

    assert (
        ServicioLoteSerie.listar(
            producto.id,
        )
        == []
    )


def _qapp():
    from PySide6.QtWidgets import QApplication

    app = QApplication.instance()

    if app is None:
        app = QApplication([])

    return app


def test_formulario_producto_muestra_lotes(
    requiere_postgresql,
):
    from aplicacion.maestros.productos.formulario import (
        FormularioProducto,
    )
    from aplicacion.modulos.inventario.lote_serie_servicio import (
        ServicioLoteSerie,
    )

    _qapp()

    sufijo = uuid.uuid4().hex[:8]

    producto = _crear_producto(
        sufijo,
        maneja_lote=True,
    )

    ServicioLoteSerie.guardar(
        {
            "producto_id": producto.id,
            "numero": "L-900",
        },
    )

    form = FormularioProducto(
        id_registro=producto.id,
    )

    assert not form._grupo_lote_serie.isHidden()
    assert form.lote_serie_widget.tabla.rowCount() == 1
    assert (
        form.lote_serie_widget.tabla.item(0, 0).text()
        == "L-900"
    )


def test_formulario_producto_oculta_lotes_si_no_aplica(
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

    assert form._grupo_lote_serie.isHidden()


def test_ajustes_vista_muestra_combo_lote_serie_para_producto_que_aplica(
    requiere_postgresql,
    bodega_id,
):
    from aplicacion.framework.lookup.lookup_result import (
        LookupResult,
    )
    from aplicacion.modulos.inventario.ajustes.vista import (
        AjustesInventarioPage,
    )
    from aplicacion.modulos.inventario.lote_serie_servicio import (
        ServicioLoteSerie,
    )

    _qapp()

    sufijo = uuid.uuid4().hex[:8]

    producto = _crear_producto(
        sufijo,
        maneja_serie=True,
    )

    ServicioLoteSerie.guardar(
        {
            "producto_id": producto.id,
            "numero": "SN-777",
        },
    )

    pagina = AjustesInventarioPage()

    pagina.producto.establecer(
        LookupResult(
            valor=producto.id,
            texto=producto.nombre,
            codigo=producto.codigo,
        ),
    )

    assert not pagina.lote_serie.isHidden()
    assert pagina.lote_serie.count() == 1
    assert pagina.lote_serie.itemText(0) == "SN-777"


def test_ajustes_vista_oculta_combo_para_producto_que_no_aplica(
    requiere_postgresql,
    bodega_id,
):
    from aplicacion.framework.lookup.lookup_result import (
        LookupResult,
    )
    from aplicacion.modulos.inventario.ajustes.vista import (
        AjustesInventarioPage,
    )

    _qapp()

    sufijo = uuid.uuid4().hex[:8]

    producto = _crear_producto(
        sufijo,
    )

    pagina = AjustesInventarioPage()

    pagina.producto.establecer(
        LookupResult(
            valor=producto.id,
            texto=producto.nombre,
            codigo=producto.codigo,
        ),
    )

    assert pagina.lote_serie.isHidden()


def test_ajustes_vista_registra_ajuste_creando_lote_nuevo(
    requiere_postgresql,
    bodega_id,
):
    """
    Flujo real: el usuario escribe un número de lote que todavía
    no existe (típico al recibir mercancía nueva) y el ajuste lo
    crea sobre la marcha, en vez de exigir que ya exista.
    """

    from aplicacion.framework.lookup.lookup_result import (
        LookupResult,
    )
    from aplicacion.modulos.inventario.ajustes.vista import (
        AjustesInventarioPage,
    )
    from aplicacion.modulos.inventario.lote_serie_servicio import (
        ServicioLoteSerie,
    )

    _qapp()

    sufijo = uuid.uuid4().hex[:8]

    producto = _crear_producto(
        sufijo,
        maneja_lote=True,
    )

    pagina = AjustesInventarioPage()

    indice_bodega = pagina.bodega.findData(
        bodega_id,
    )
    pagina.bodega.setCurrentIndex(
        indice_bodega,
    )

    pagina.producto.establecer(
        LookupResult(
            valor=producto.id,
            texto=producto.nombre,
            codigo=producto.codigo,
        ),
    )

    pagina.lote_serie.setEditText(
        "L-NUEVO",
    )

    pagina.tipo.setCurrentIndex(
        pagina.tipo.findData(
            "entrada",
        ),
    )
    pagina.cantidad.setValue(
        7,
    )

    with patch(
        "aplicacion.modulos.inventario.ajustes.vista.QMessageBox.information",
    ):

        pagina._guardar()

    lotes = ServicioLoteSerie.listar(
        producto.id,
    )

    assert len(lotes) == 1
    assert lotes[0].numero == "L-NUEVO"
    assert (
        ServicioLoteSerie.existencia_total(
            lotes[0].id,
        )
        == 7
    )
