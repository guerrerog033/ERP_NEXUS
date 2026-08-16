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


def _documento(sufijo: str) -> str:

    return str(
        900000000
        + int(sufijo[:6], 16) % 99999999,
    )


def _crear_archivo(tmp_path, filas):

    from aplicacion.maestros.terceros.importacion_excel import (
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


class TestImportarDesdeExcel:

    def test_crea_terceros_nuevos(
        self,
        requiere_postgresql,
        tmp_path,
    ):

        from aplicacion.maestros.terceros.importacion_excel import (
            importar_desde_excel,
        )
        from aplicacion.maestros.terceros.repositorio import (
            TerceroRepositorio,
        )

        sufijo = _sufijo()
        documento = _documento(sufijo)

        filas = [
            (
                "NIT",
                documento,
                "Cliente",
                f"Importado Excel {sufijo}",
                "",
                "",
                "",
                "",
                "Calle 1 # 2-3",
                "Bogotá",
                "Cundinamarca",
                "Colombia",
                "",
                "3001234567",
                f"importado.{sufijo}@demo.com",
                30,
                1000000,
            ),
        ]

        ruta = _crear_archivo(tmp_path, filas)

        resultado = importar_desde_excel(ruta)

        assert resultado.creados == 1
        assert resultado.actualizados == 0
        assert resultado.errores == []

        tercero = TerceroRepositorio.obtener_por_documento(
            "NIT",
            documento,
        )

        assert tercero is not None
        assert tercero.razon_social == f"Importado Excel {sufijo}"
        assert tercero.dias_credito == 30

    def test_actualiza_tercero_existente_por_documento(
        self,
        requiere_postgresql,
        tmp_path,
    ):

        from aplicacion.maestros.terceros.importacion_excel import (
            importar_desde_excel,
        )
        from aplicacion.maestros.terceros.servicio import (
            TerceroServicio,
        )

        sufijo = _sufijo()
        documento = _documento(sufijo)

        TerceroServicio.guardar(
            {
                "tipo_documento": "NIT",
                "numero_documento": documento,
                "tipo_tercero": "Cliente",
                "razon_social": f"Original {sufijo}",
                "pais": "Colombia",
                "resp_r99_pn": True,
            },
        )

        filas = [
            (
                "NIT",
                documento,
                "Cliente",
                f"Actualizado Excel {sufijo}",
                "",
                "",
                "",
                "",
                "",
                "",
                "",
                "Colombia",
                "",
                "",
                "",
                0,
                0,
            ),
        ]

        ruta = _crear_archivo(tmp_path, filas)

        resultado = importar_desde_excel(ruta)

        assert resultado.creados == 0
        assert resultado.actualizados == 1

        from aplicacion.maestros.terceros.repositorio import (
            TerceroRepositorio,
        )

        tercero = TerceroRepositorio.obtener_por_documento(
            "NIT",
            documento,
        )

        assert tercero.razon_social == f"Actualizado Excel {sufijo}"

    def test_fila_invalida_no_detiene_las_demas(
        self,
        requiere_postgresql,
        tmp_path,
    ):

        from aplicacion.maestros.terceros.importacion_excel import (
            importar_desde_excel,
        )

        sufijo = _sufijo()

        filas = [
            (
                "",
                "",
                "",
                "Fila sin documento",
                "",
                "",
                "",
                "",
                "",
                "",
                "",
                "",
                "",
                "",
                "",
                0,
                0,
            ),
            (
                "NIT",
                _documento(sufijo),
                "Cliente",
                f"Fila válida {sufijo}",
                "",
                "",
                "",
                "",
                "",
                "",
                "",
                "Colombia",
                "",
                "",
                "",
                0,
                0,
            ),
        ]

        ruta = _crear_archivo(tmp_path, filas)

        resultado = importar_desde_excel(ruta)

        assert resultado.creados == 1
        assert len(resultado.errores) == 1
        assert resultado.errores[0][0] == 2

    def test_filas_vacias_se_omiten(
        self,
        requiere_postgresql,
        tmp_path,
    ):

        from aplicacion.maestros.terceros.importacion_excel import (
            importar_desde_excel,
        )

        filas = [
            tuple(
                "" if i != 5 else None
                for i in range(17)
            ),
        ]

        ruta = _crear_archivo(tmp_path, filas)

        resultado = importar_desde_excel(ruta)

        assert resultado.creados == 0
        assert resultado.actualizados == 0
        assert resultado.errores == []
