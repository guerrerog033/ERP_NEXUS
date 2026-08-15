from __future__ import annotations

import os
import uuid
from unittest.mock import patch

import pytest

from aplicacion.base_datos.registro_modelos import (
    importar_modelos,
)

pytestmark = pytest.mark.integration


PNG_1X1 = bytes.fromhex(
    "89504e470d0a1a0a0000000d49484452"
    "00000001000000010802000000907753"
    "de0000000c49444154789c63f8cfc000"
    "0003010100c9fe92ef0000000049454e"
    "44ae426082"
)


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


@pytest.fixture(autouse=True)
def _ruta_imagenes_temporal(
    requiere_postgresql,
    tmp_path,
    monkeypatch,
):

    from aplicacion.maestros.productos import servicios

    monkeypatch.setattr(
        servicios,
        "RUTA_IMAGENES",
        tmp_path / "productos",
    )


def _qapp():
    from PySide6.QtWidgets import QApplication

    app = QApplication.instance()

    if app is None:
        app = QApplication([])

    return app


def _png_archivo(tmp_path) -> str:

    archivo = tmp_path / "producto_prueba.png"

    archivo.write_bytes(
        PNG_1X1,
    )

    return str(archivo)


def _crear_producto(sufijo: str, **extra) -> object:
    from aplicacion.maestros.productos.servicios import (
        ServicioProducto,
    )

    datos = {
        "codigo": f"IMG{sufijo.upper()}",
        "nombre": f"Producto Imagen Demo {sufijo}",
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


def test_guardar_formulario_producto_persiste_imagen_seleccionada(
    tmp_path,
):
    """
    Regresión: FormularioBase.guardar() leía self.formulario.valores()
    (valores crudos del motor) en vez de self.valores() (que
    FormularioProducto sobrescribe para incluir _imagen_archivo). Con
    ese bug, seleccionar una imagen y pulsar "Guardar" no persistía
    nada.
    """
    from aplicacion.maestros.productos.formulario import (
        FormularioProducto,
    )
    from aplicacion.maestros.productos.servicios import (
        ServicioProducto,
    )

    _qapp()

    sufijo = uuid.uuid4().hex[:8]

    producto = _crear_producto(
        sufijo,
    )

    form = FormularioProducto(
        id_registro=producto.id,
    )

    archivo = _png_archivo(
        tmp_path,
    )

    form.imagen_widget.establecer_archivo(
        archivo,
    )

    with patch(
        "aplicacion.framework.base.formulario_base.QMessageBox.information",
    ):

        form.guardar()

    actualizado = ServicioProducto.obtener_completo(
        producto.id,
    )

    assert actualizado.imagen == (
        f"productos/{producto.codigo}.png"
    )

    ruta_absoluta = ServicioProducto.ruta_imagen_absoluta(
        actualizado.imagen,
    )

    assert ruta_absoluta is not None
    assert ruta_absoluta.is_file()
