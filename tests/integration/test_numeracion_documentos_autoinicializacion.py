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

    return uuid.uuid4().hex[:6].upper()


def _documento(sufijo: str) -> str:

    return str(
        900000000
        + int(sufijo, 36) % 99999999,
    )


def _crear_cliente(sufijo: str):

    from aplicacion.maestros.terceros.servicio import (
        TerceroServicio,
    )

    return TerceroServicio.guardar(
        {
            "tipo_documento": "NIT",
            "numero_documento": _documento(sufijo),
            "tipo_tercero": "Cliente",
            "razon_social": f"Numeracion Demo {sufijo}",
            "pais": "Colombia",
            "resp_r99_pn": True,
        },
    )


def _crear_factura_venta(cliente_id: int, sufijo: str):

    from aplicacion.base_datos.conexion import SessionLocal
    from aplicacion.modulos.ventas.facturas.modelos import (
        FacturaVenta,
    )

    db = SessionLocal()

    try:

        registro = FacturaVenta(
            numero=f"FV-NUM-{sufijo}",
            fecha=date.today(),
            cliente_id=cliente_id,
            subtotal=100000,
            total=100000,
            saldo_pendiente=100000,
        )

        db.add(registro)
        db.commit()
        db.refresh(registro)

        return registro.id

    finally:

        db.close()


class TestSiguienteNumeroConsecutivoMinimo:

    def test_usa_consecutivo_minimo_al_crear_por_primera_vez(
        self,
        requiere_postgresql,
    ):

        from aplicacion.nucleo.numeracion.servicio import (
            ServicioNumeracion,
        )

        codigo_tipo = f"tipo_prueba_{_sufijo()}"

        numero = ServicioNumeracion.siguiente_numero(
            codigo_tipo,
            "PFX",
            longitud=6,
            consecutivo_minimo=41,
        )

        assert numero == "PFX000042"

    def test_consecutivo_minimo_no_afecta_fila_ya_existente(
        self,
        requiere_postgresql,
    ):

        from aplicacion.nucleo.numeracion.servicio import (
            ServicioNumeracion,
        )

        codigo_tipo = f"tipo_prueba_{_sufijo()}"

        primero = ServicioNumeracion.siguiente_numero(
            codigo_tipo,
            "PFX",
            longitud=6,
            consecutivo_minimo=5,
        )

        assert primero == "PFX000006"

        segundo = ServicioNumeracion.siguiente_numero(
            codigo_tipo,
            "PFX",
            longitud=6,
            consecutivo_minimo=100,
        )

        assert segundo == "PFX000007"

    def test_sin_consecutivo_minimo_arranca_en_uno(
        self,
        requiere_postgresql,
    ):

        from aplicacion.nucleo.numeracion.servicio import (
            ServicioNumeracion,
        )

        codigo_tipo = f"tipo_prueba_{_sufijo()}"

        numero = ServicioNumeracion.siguiente_numero(
            codigo_tipo,
            "PFX",
            longitud=6,
        )

        assert numero == "PFX000001"


class TestGenerarNumeroNoChocaConDocumentosPreexistentes:

    def test_nota_credito_venta_hereda_maximo_de_documentos_legados(
        self,
        requiere_postgresql,
        monkeypatch,
    ):
        """
        Reproduce el bug real: una base de datos que ya tenía notas
        crédito creadas por fuera de la numeración centralizada
        (o antes de que existiera) no debe chocar cuando se pide el
        primer número por ese camino.
        """

        from aplicacion.base_datos.conexion import SessionLocal
        from aplicacion.modulos.ventas.notas_credito.modelos import (
            NotaCreditoVenta,
        )
        from aplicacion.modulos.ventas.notas_credito.servicios import (
            ServicioNotaCreditoVenta,
        )
        from aplicacion.nucleo.configuracion import Configuracion

        prefijo = f"NC{_sufijo()}"
        sufijo = _sufijo()

        cliente = _crear_cliente(sufijo)
        factura_id = _crear_factura_venta(cliente.id, sufijo)

        db = SessionLocal()

        try:

            for consecutivo in (1, 2, 3):

                db.add(
                    NotaCreditoVenta(
                        numero=f"{prefijo}{consecutivo:06d}",
                        fecha=date.today(),
                        cliente_id=cliente.id,
                        factura_id=factura_id,
                        motivo="Prueba",
                        subtotal=0,
                        iva=0,
                        total=0,
                    )
                )

            db.commit()

        finally:

            db.close()

        datos = Configuracion.cargar()

        monkeypatch.setitem(
            datos,
            "ventas",
            {
                "prefijo_nota_credito": prefijo,
            },
        )

        numero = ServicioNotaCreditoVenta.generar_numero()

        assert numero == f"{prefijo}000004"
