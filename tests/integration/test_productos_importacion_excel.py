from __future__ import annotations

import os
import uuid

import pytest
from openpyxl import Workbook

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


def _sufijo() -> str:

    return uuid.uuid4().hex[:8]


def _crear_archivo(tmp_path, filas):

    from aplicacion.maestros.productos.importacion_excel import (
        COLUMNAS,
    )

    libro = Workbook()
    hoja = libro.active

    hoja.append(
        [encabezado for _, encabezado in COLUMNAS],
    )

    for fila in filas:

        hoja.append(fila)

    ruta = tmp_path / "importacion.xlsx"

    libro.save(ruta)

    return ruta


class TestImportarProductosDesdeExcel:

    def test_crea_productos_nuevos(
        self,
        requiere_postgresql,
        tmp_path,
    ):

        from aplicacion.maestros.productos.importacion_excel import (
            importar_desde_excel,
        )

        sufijo = _sufijo()
        codigo = f"IMP-{sufijo}"

        filas = [
            (
                codigo,
                f"Producto Importado {sufijo}",
                "",
                "",
                "",
                "",
                50000,
                30000,
                5,
                "No",
            ),
        ]

        ruta = _crear_archivo(tmp_path, filas)

        resultado = importar_desde_excel(ruta)

        assert resultado.creados == 1
        assert resultado.actualizados == 0
        assert resultado.errores == []

        from aplicacion.base_datos.conexion import (
            SessionLocal,
        )
        from aplicacion.maestros.productos.modelos import (
            Producto,
        )

        db = SessionLocal()

        try:

            producto = (
                db.query(Producto)
                .filter(Producto.codigo == codigo.upper())
                .first()
            )

        finally:

            db.close()

        assert producto is not None
        assert producto.nombre == f"Producto Importado {sufijo}"
        assert float(producto.precio_venta) == 50000.0
        assert producto.precio_incluye_iva is False

    def test_actualiza_producto_existente_por_codigo(
        self,
        requiere_postgresql,
        tmp_path,
    ):

        from aplicacion.maestros.productos.importacion_excel import (
            importar_desde_excel,
        )
        from aplicacion.maestros.productos.servicios import (
            ServicioProducto,
        )

        sufijo = _sufijo()
        codigo = f"UPD-{sufijo}"

        ServicioProducto.guardar(
            {
                "codigo": codigo,
                "nombre": f"Original {sufijo}",
                "precio_venta": 10000,
            },
        )

        filas = [
            (
                codigo,
                f"Actualizado {sufijo}",
                "",
                "",
                "",
                "",
                20000,
                0,
                0,
                "Sí",
            ),
        ]

        ruta = _crear_archivo(tmp_path, filas)

        resultado = importar_desde_excel(ruta)

        assert resultado.creados == 0
        assert resultado.actualizados == 1

        from aplicacion.base_datos.conexion import (
            SessionLocal,
        )
        from aplicacion.maestros.productos.modelos import (
            Producto,
        )

        db = SessionLocal()

        try:

            producto = (
                db.query(Producto)
                .filter(Producto.codigo == codigo.upper())
                .first()
            )

        finally:

            db.close()

        assert producto.nombre == f"Actualizado {sufijo}"
        assert float(producto.precio_venta) == 20000.0
        assert producto.precio_incluye_iva is True

    def test_resuelve_categoria_marca_y_unidad_medida(
        self,
        requiere_postgresql,
        tmp_path,
    ):

        from aplicacion.maestros.categorias.servicios import (
            ServicioCategoria,
        )
        from aplicacion.maestros.marcas.servicios import (
            ServicioMarca,
        )
        from aplicacion.maestros.productos.importacion_excel import (
            importar_desde_excel,
        )
        from aplicacion.maestros.unidades_medida.servicios import (
            ServicioUnidadMedida,
        )

        sufijo = _sufijo()

        categoria = ServicioCategoria.guardar(
            {
                "codigo": f"CAT-{sufijo}",
                "nombre": f"Categoria {sufijo}",
            },
        )

        marca = ServicioMarca.guardar(
            {
                "codigo": f"MAR-{sufijo}",
                "nombre": f"Marca {sufijo}",
            },
        )

        unidad = ServicioUnidadMedida.guardar(
            {
                "codigo": f"U{sufijo[:3]}",
                "nombre": f"Unidad {sufijo}",
            },
        )

        codigo = f"FK-{sufijo}"

        filas = [
            (
                codigo,
                f"Producto con FKs {sufijo}",
                "",
                categoria.nombre,
                marca.nombre,
                unidad.codigo,
                15000,
                0,
                0,
                "No",
            ),
        ]

        ruta = _crear_archivo(tmp_path, filas)

        resultado = importar_desde_excel(ruta)

        assert resultado.creados == 1
        assert resultado.errores == []

        from aplicacion.base_datos.conexion import (
            SessionLocal,
        )
        from aplicacion.maestros.productos.modelos import (
            Producto,
        )

        db = SessionLocal()

        try:

            producto = (
                db.query(Producto)
                .filter(Producto.codigo == codigo.upper())
                .first()
            )

        finally:

            db.close()

        assert producto.categoria_id == categoria.id
        assert producto.marca_id == marca.id
        assert producto.unidad_medida_id == unidad.id

    def test_categoria_inexistente_genera_error_en_la_fila(
        self,
        requiere_postgresql,
        tmp_path,
    ):

        from aplicacion.maestros.productos.importacion_excel import (
            importar_desde_excel,
        )

        sufijo = _sufijo()

        filas = [
            (
                f"ERR-{sufijo}",
                f"Producto con error {sufijo}",
                "",
                f"Categoria que no existe {sufijo}",
                "",
                "",
                10000,
                0,
                0,
                "No",
            ),
        ]

        ruta = _crear_archivo(tmp_path, filas)

        resultado = importar_desde_excel(ruta)

        assert resultado.creados == 0
        assert len(resultado.errores) == 1
        assert resultado.errores[0][0] == 2
        assert "categoría" in resultado.errores[0][1]

    def test_filas_vacias_se_omiten(
        self,
        requiere_postgresql,
        tmp_path,
    ):

        from aplicacion.maestros.productos.importacion_excel import (
            importar_desde_excel,
        )

        filas = [
            tuple("" for _ in range(10)),
        ]

        ruta = _crear_archivo(tmp_path, filas)

        resultado = importar_desde_excel(ruta)

        assert resultado.creados == 0
        assert resultado.actualizados == 0
        assert resultado.errores == []
