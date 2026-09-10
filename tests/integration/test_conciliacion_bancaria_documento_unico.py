from __future__ import annotations

import os
import uuid
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


def _sufijo() -> str:

    return uuid.uuid4().hex[:8]


def _documento(sufijo: str) -> str:

    return str(
        900000000
        + int(sufijo[:6], 16) % 99999999,
    )


def _crear_tercero(
    sufijo: str,
    *,
    tipo_tercero: str = "Cliente",
):

    from aplicacion.maestros.terceros.servicio import (
        TerceroServicio,
    )

    return TerceroServicio.guardar(
        {
            "tipo_documento": "NIT",
            "numero_documento": _documento(sufijo),
            "tipo_tercero": tipo_tercero,
            "razon_social": f"Conciliación Doc Único {sufijo}",
            "pais": "Colombia",
            "resp_r99_pn": True,
        },
    )


def _crear_extracto(
    *,
    valor: float,
    tipo: str,
    descripcion: str = "",
    referencia: str = "",
):

    from aplicacion.base_datos.conexion import SessionLocal
    from aplicacion.modulos.tesoreria.conciliacion.modelos import (
        ExtractoBancario,
    )

    db = SessionLocal()

    try:

        registro = ExtractoBancario(
            banco="Banco Demo",
            cuenta="123456",
            fecha=date.today(),
            descripcion=descripcion,
            referencia=referencia,
            valor=valor,
            tipo=tipo,
            origen="manual",
        )

        db.add(registro)
        db.commit()
        db.refresh(registro)

        return registro.id

    finally:

        db.close()


def _crear_factura_venta(
    cliente_id: int,
    sufijo: str,
    *,
    total: float,
):

    from aplicacion.base_datos.conexion import SessionLocal
    from aplicacion.modulos.ventas.facturas.modelos import (
        FacturaVenta,
    )

    db = SessionLocal()

    try:

        registro = FacturaVenta(
            numero=f"FV-{sufijo}",
            fecha=date.today(),
            cliente_id=cliente_id,
            subtotal=total,
            total=total,
            saldo_pendiente=total,
        )

        db.add(registro)
        db.commit()
        db.refresh(registro)

        return registro.id

    finally:

        db.close()


def _conciliaciones_de(extracto_id: int):

    from aplicacion.modulos.tesoreria.conciliacion.servicios import (
        ServicioConciliacionBancaria,
    )

    return [
        registro
        for registro in ServicioConciliacionBancaria.listar_conciliadas()
        if registro.extracto_id == extracto_id
    ]


class TestDocumentoNoSeReutiliza:

    def test_automatico_no_asigna_el_mismo_documento_a_dos_movimientos(
        self,
        requiere_postgresql,
    ):

        from aplicacion.modulos.tesoreria.conciliacion.servicios import (
            ServicioConciliacionBancaria,
        )

        sufijo = _sufijo()
        cliente = _crear_tercero(sufijo)

        factura_id = _crear_factura_venta(
            cliente.id,
            sufijo,
            total=123456,
        )

        # Ambos movimientos citan la misma factura y valen lo mismo:
        # solo uno puede quedar conciliado con ella.
        referencia = f"FV-{sufijo}"
        extracto_a = _crear_extracto(
            valor=123456,
            tipo="credito",
            referencia=referencia,
        )
        extracto_b = _crear_extracto(
            valor=123456,
            tipo="credito",
            referencia=referencia,
        )

        ServicioConciliacionBancaria.conciliar_automatico()

        conc_a = _conciliaciones_de(extracto_a)
        conc_b = _conciliaciones_de(extracto_b)

        vinculan_factura = [
            registro
            for registro in conc_a + conc_b
            if registro.tipo_documento == "factura_venta"
            and registro.documento_id == factura_id
        ]

        # La factura solo puede quedar conciliada con uno de los dos
        # movimientos, nunca con ambos.
        assert len(vinculan_factura) == 1

        pendientes = {
            e.id
            for e in ServicioConciliacionBancaria.listar_pendientes()
        }

        assert {extracto_a, extracto_b} & pendientes

    def test_manual_rechaza_documento_ya_conciliado(
        self,
        requiere_postgresql,
    ):

        from aplicacion.modulos.tesoreria.conciliacion.servicios import (
            ServicioConciliacionBancaria,
        )

        sufijo = _sufijo()
        cliente = _crear_tercero(sufijo)

        factura_id = _crear_factura_venta(
            cliente.id,
            sufijo,
            total=90000,
        )

        extracto_a = _crear_extracto(valor=90000, tipo="credito")
        extracto_b = _crear_extracto(valor=90000, tipo="credito")

        ServicioConciliacionBancaria.conciliar_manual(
            extracto_a,
            "factura_venta",
            factura_id,
        )

        with pytest.raises(ValueError, match="ya está conciliado"):
            ServicioConciliacionBancaria.conciliar_manual(
                extracto_b,
                "factura_venta",
                factura_id,
            )

    def test_candidatos_documento_excluye_los_ya_conciliados(
        self,
        requiere_postgresql,
    ):

        from aplicacion.modulos.tesoreria.conciliacion.servicios import (
            ServicioConciliacionBancaria,
        )

        sufijo = _sufijo()
        cliente = _crear_tercero(sufijo)

        factura_id = _crear_factura_venta(
            cliente.id,
            sufijo,
            total=54321,
        )

        extracto_a = _crear_extracto(valor=54321, tipo="credito")
        extracto_b = _crear_extracto(valor=54321, tipo="credito")

        antes = ServicioConciliacionBancaria.candidatos_documento(
            extracto_b,
        )
        assert any(
            c["tipo_documento"] == "factura_venta"
            and c["documento_id"] == factura_id
            for c in antes
        )

        ServicioConciliacionBancaria.conciliar_manual(
            extracto_a,
            "factura_venta",
            factura_id,
        )

        despues = ServicioConciliacionBancaria.candidatos_documento(
            extracto_b,
        )
        assert not any(
            c["tipo_documento"] == "factura_venta"
            and c["documento_id"] == factura_id
            for c in despues
        )


class TestMatchExactoRequiereReferencia:

    def test_movimiento_sin_referencia_no_se_empareja_por_solo_valor(
        self,
        requiere_postgresql,
    ):

        from aplicacion.modulos.tesoreria.conciliacion.servicios import (
            ServicioConciliacionBancaria,
        )

        sufijo = _sufijo()
        cliente = _crear_tercero(sufijo)

        _crear_factura_venta(cliente.id, sufijo, total=333000)

        # Sin número de factura en la referencia ni en la
        # descripción: un movimiento que solo coincide en valor no
        # debe conciliarse solo (evita emparejar por casualidad).
        extracto_id = _crear_extracto(valor=333000, tipo="credito")

        ServicioConciliacionBancaria.conciliar_automatico()

        pendientes = {
            e.id
            for e in ServicioConciliacionBancaria.listar_pendientes()
        }
        assert extracto_id in pendientes

    def test_movimiento_con_numero_en_referencia_si_se_empareja(
        self,
        requiere_postgresql,
    ):

        from aplicacion.modulos.tesoreria.conciliacion.servicios import (
            ServicioConciliacionBancaria,
        )

        sufijo = _sufijo()
        cliente = _crear_tercero(sufijo)

        factura_id = _crear_factura_venta(
            cliente.id,
            sufijo,
            total=333000,
        )

        extracto_id = _crear_extracto(
            valor=333000,
            tipo="credito",
            referencia=f"FV-{sufijo}",
        )

        ServicioConciliacionBancaria.conciliar_automatico()

        conc = _conciliaciones_de(extracto_id)
        assert len(conc) == 1
        assert conc[0].documento_id == factura_id
        assert conc[0].estado == "conciliado"


class TestDeshacerMatchCombinado:

    def test_deshacer_elimina_todas_las_filas_del_movimiento(
        self,
        requiere_postgresql,
    ):

        from aplicacion.modulos.tesoreria.conciliacion.servicios import (
            ServicioConciliacionBancaria,
        )

        sufijo = _sufijo()
        cliente = _crear_tercero(sufijo)

        _crear_factura_venta(cliente.id, sufijo + "a", total=110000)
        _crear_factura_venta(cliente.id, sufijo + "b", total=140000)

        extracto_id = _crear_extracto(valor=250000, tipo="credito")

        ServicioConciliacionBancaria.conciliar_automatico()

        filas = _conciliaciones_de(extracto_id)
        assert len(filas) == 2
        assert all(f.estado == "combinado" for f in filas)

        ServicioConciliacionBancaria.deshacer(filas[0].id)

        # Ninguna fila hermana queda huérfana y el movimiento vuelve
        # a estar pendiente.
        assert _conciliaciones_de(extracto_id) == []

        pendientes = {
            e.id
            for e in ServicioConciliacionBancaria.listar_pendientes()
        }
        assert extracto_id in pendientes
