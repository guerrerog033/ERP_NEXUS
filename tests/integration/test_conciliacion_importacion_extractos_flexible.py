from __future__ import annotations

import os
from datetime import date

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


class TestImportarCsvFormatosFlexibles:

    def test_importa_csv_cp1252_con_punto_y_coma_y_columnas_debito_credito(
        self,
        requiere_postgresql,
        tmp_path,
    ):

        from aplicacion.modulos.tesoreria.conciliacion.servicios import (
            ServicioConciliacionBancaria,
        )

        contenido = (
            "Fecha;Descripción;Documento;Débito;Crédito;Saldo\n"
            "01/03/2026;PAGO PROVEEDOR XYZ;FC-0001;150000;;900000\n"
            "02/03/2026;CONSIGNACION CLIENTE;FV-0002;;300000;1200000\n"
        )

        ruta = tmp_path / "extracto_banco.csv"
        ruta.write_bytes(
            contenido.encode("cp1252"),
        )

        importados = ServicioConciliacionBancaria.importar_csv(
            ruta,
            banco="Banco Demo",
        )

        assert importados == 2

        extractos = ServicioConciliacionBancaria.listar_extractos()

        movimiento_debito = next(
            e for e in extractos if e.referencia == "FC-0001"
        )
        movimiento_credito = next(
            e for e in extractos if e.referencia == "FV-0002"
        )

        assert movimiento_debito.tipo == "debito"
        assert float(movimiento_debito.valor) == 150000.0
        assert movimiento_debito.fecha == date(2026, 3, 1)

        assert movimiento_credito.tipo == "credito"
        assert float(movimiento_credito.valor) == 300000.0
        assert movimiento_credito.fecha == date(2026, 3, 2)

    def test_importa_csv_generico_previo_sigue_funcionando(
        self,
        requiere_postgresql,
        tmp_path,
    ):

        from aplicacion.modulos.tesoreria.conciliacion.servicios import (
            ServicioConciliacionBancaria,
        )

        contenido = (
            "fecha,descripcion,referencia,valor,saldo\n"
            "05/03/2026,Transferencia,REF-GENERICO-9,-45000,500000\n"
        )

        ruta = tmp_path / "extracto_generico.csv"
        ruta.write_text(contenido, encoding="utf-8")

        importados = ServicioConciliacionBancaria.importar_csv(
            ruta,
        )

        assert importados == 1

        extractos = ServicioConciliacionBancaria.listar_extractos()

        movimiento = next(
            e
            for e in extractos
            if e.referencia == "REF-GENERICO-9"
        )

        assert movimiento.tipo == "debito"
        assert float(movimiento.valor) == 45000.0

    def test_fila_sin_movimiento_en_debito_ni_credito_se_omite(
        self,
        requiere_postgresql,
        tmp_path,
    ):

        from aplicacion.modulos.tesoreria.conciliacion.servicios import (
            ServicioConciliacionBancaria,
        )

        contenido = (
            "Fecha;Descripcion;Debito;Credito\n"
            "10/03/2026;Movimiento sin valor;0;0\n"
        )

        ruta = tmp_path / "extracto_vacio.csv"
        ruta.write_text(contenido, encoding="utf-8")

        importados = ServicioConciliacionBancaria.importar_csv(
            ruta,
        )

        assert importados == 0
