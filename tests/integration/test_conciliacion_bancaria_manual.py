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
            "razon_social": f"Conciliación Demo {sufijo}",
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


def _crear_factura_compra(
    proveedor_id: int,
    sufijo: str,
    *,
    total: float,
):

    from aplicacion.base_datos.conexion import SessionLocal
    from aplicacion.modulos.compras.facturas.modelos import (
        FacturaCompra,
    )

    db = SessionLocal()

    try:

        registro = FacturaCompra(
            numero=f"FC-{sufijo}",
            fecha=date.today(),
            proveedor_id=proveedor_id,
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


class TestConciliarManual:

    def test_conciliar_manual_vincula_documento_y_marca_conciliado(
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
            total=250000,
        )
        extracto_id = _crear_extracto(
            valor=250000,
            tipo="credito",
        )

        registro = ServicioConciliacionBancaria.conciliar_manual(
            extracto_id,
            "factura_venta",
            factura_id,
        )

        assert registro.id is not None
        assert registro.estado == "manual"

        pendientes = ServicioConciliacionBancaria.listar_pendientes()

        assert all(
            extracto.id != extracto_id
            for extracto in pendientes
        )

    def test_conciliar_manual_extracto_ya_conciliado_lanza_error(
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
            total=100000,
        )
        extracto_id = _crear_extracto(
            valor=100000,
            tipo="credito",
        )

        ServicioConciliacionBancaria.conciliar_manual(
            extracto_id,
            "factura_venta",
            factura_id,
        )

        with pytest.raises(
            ValueError,
            match="ya está conciliado",
        ):

            ServicioConciliacionBancaria.conciliar_manual(
                extracto_id,
                "factura_venta",
                factura_id,
            )

    def test_conciliar_manual_tipo_documento_invalido_lanza_error(
        self,
        requiere_postgresql,
    ):

        from aplicacion.modulos.tesoreria.conciliacion.servicios import (
            ServicioConciliacionBancaria,
        )

        extracto_id = _crear_extracto(
            valor=50000,
            tipo="debito",
        )

        with pytest.raises(
            ValueError,
            match="no soportado",
        ):

            ServicioConciliacionBancaria.conciliar_manual(
                extracto_id,
                "tipo_invalido",
                1,
            )

    def test_deshacer_revierte_conciliacion(
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
            total=75000,
        )
        extracto_id = _crear_extracto(
            valor=75000,
            tipo="credito",
        )

        registro = ServicioConciliacionBancaria.conciliar_manual(
            extracto_id,
            "factura_venta",
            factura_id,
        )

        ServicioConciliacionBancaria.deshacer(registro.id)

        pendientes = ServicioConciliacionBancaria.listar_pendientes()

        assert any(
            extracto.id == extracto_id
            for extracto in pendientes
        )

    def test_candidatos_documento_ordena_por_cercania_de_valor(
        self,
        requiere_postgresql,
    ):

        from aplicacion.modulos.tesoreria.conciliacion.servicios import (
            ServicioConciliacionBancaria,
        )

        sufijo = _sufijo()
        cliente = _crear_tercero(sufijo)

        factura_lejana_id = _crear_factura_venta(
            cliente.id,
            sufijo + "a",
            total=10000,
        )
        factura_cercana_id = _crear_factura_venta(
            cliente.id,
            sufijo + "b",
            total=199000,
        )

        extracto_id = _crear_extracto(
            valor=200000,
            tipo="credito",
        )

        candidatos = ServicioConciliacionBancaria.candidatos_documento(
            extracto_id,
        )

        ids_ordenados = [
            candidato["documento_id"]
            for candidato in candidatos
            if candidato["tipo_documento"] == "factura_venta"
            and candidato["documento_id"]
            in (factura_lejana_id, factura_cercana_id)
        ]

        assert ids_ordenados[0] == factura_cercana_id
        assert ids_ordenados[1] == factura_lejana_id

    def test_conciliar_manual_debito_con_factura_compra(
        self,
        requiere_postgresql,
    ):

        from aplicacion.modulos.tesoreria.conciliacion.servicios import (
            ServicioConciliacionBancaria,
        )

        sufijo = _sufijo()
        proveedor = _crear_tercero(
            sufijo,
            tipo_tercero="Proveedor",
        )
        factura_id = _crear_factura_compra(
            proveedor.id,
            sufijo,
            total=180000,
        )
        extracto_id = _crear_extracto(
            valor=180000,
            tipo="debito",
        )

        candidatos = ServicioConciliacionBancaria.candidatos_documento(
            extracto_id,
        )

        assert any(
            candidato["tipo_documento"] == "factura_compra"
            and candidato["documento_id"] == factura_id
            for candidato in candidatos
        )

        registro = ServicioConciliacionBancaria.conciliar_manual(
            extracto_id,
            "factura_compra",
            factura_id,
        )

        assert registro.tipo_documento == "factura_compra"

    def test_listar_pendientes_excluye_conciliados(
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
            total=30000,
        )
        extracto_id = _crear_extracto(
            valor=30000,
            tipo="credito",
        )

        antes = {
            extracto.id
            for extracto in ServicioConciliacionBancaria.listar_pendientes()
        }
        assert extracto_id in antes

        ServicioConciliacionBancaria.conciliar_manual(
            extracto_id,
            "factura_venta",
            factura_id,
        )

        despues = {
            extracto.id
            for extracto in ServicioConciliacionBancaria.listar_pendientes()
        }
        assert extracto_id not in despues
