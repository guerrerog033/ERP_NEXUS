from __future__ import annotations

import os
import uuid
from datetime import date, timedelta

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


def _crear_cliente(sufijo: str):

    from aplicacion.maestros.terceros.servicio import (
        TerceroServicio,
    )

    documento = str(
        900000000
        + int(sufijo[:6], 16) % 99999999,
    )

    return TerceroServicio.guardar(
        {
            "tipo_documento": "NIT",
            "numero_documento": documento,
            "tipo_tercero": "Cliente",
            "razon_social": f"Cliente Recurrente {sufijo}",
            "pais": "Colombia",
            "resp_r99_pn": True,
        },
    )


def _datos_plantilla(cliente_id, *, proxima_fecha, periodicidad="mensual"):

    return {
        "nombre": f"Arriendo {uuid.uuid4().hex[:6]}",
        "cliente_id": cliente_id,
        "periodicidad": periodicidad,
        "proxima_fecha": proxima_fecha,
        "activa": True,
    }


def _lineas():

    return [
        {
            "descripcion": "Arriendo mensual",
            "cantidad": 1,
            "precio_unitario": 800000,
        },
    ]


class TestServicioFacturaRecurrente:

    def test_guardar_y_listar(
        self,
        requiere_postgresql,
    ):

        from aplicacion.modulos.ventas.facturacion_recurrente.servicios import (
            ServicioFacturaRecurrente,
        )

        sufijo = _sufijo()

        cliente = _crear_cliente(sufijo)

        plantilla = ServicioFacturaRecurrente.guardar(
            _datos_plantilla(
                cliente.id,
                proxima_fecha=date.today() + timedelta(days=30),
            ),
            _lineas(),
        )

        filas = ServicioFacturaRecurrente.listar()

        fila = next(
            f for f in filas if f["id"] == plantilla.id
        )

        assert fila["cliente"] == cliente.nombre_completo
        assert fila["periodicidad"] == "mensual"
        assert fila["facturas_generadas"] == 0

    def test_guardar_sin_lineas_falla(
        self,
        requiere_postgresql,
    ):

        from aplicacion.modulos.ventas.facturacion_recurrente.servicios import (
            ServicioFacturaRecurrente,
        )

        sufijo = _sufijo()

        cliente = _crear_cliente(sufijo)

        with pytest.raises(ValueError, match="línea"):

            ServicioFacturaRecurrente.guardar(
                _datos_plantilla(
                    cliente.id,
                    proxima_fecha=date.today(),
                ),
                [],
            )

    def test_generar_una_crea_factura_y_avanza_proxima_fecha(
        self,
        requiere_postgresql,
    ):

        from aplicacion.modulos.ventas.facturacion_recurrente.servicios import (
            ServicioFacturaRecurrente,
        )

        sufijo = _sufijo()

        cliente = _crear_cliente(sufijo)

        proxima_original = date.today()

        plantilla = ServicioFacturaRecurrente.guardar(
            _datos_plantilla(
                cliente.id,
                proxima_fecha=proxima_original,
            ),
            _lineas(),
        )

        factura = ServicioFacturaRecurrente.generar_una(
            plantilla.id,
        )

        assert factura.cliente_id == cliente.id
        assert float(factura.total) == 800000.0

        fila = next(
            f
            for f in ServicioFacturaRecurrente.listar()
            if f["id"] == plantilla.id
        )

        assert fila["facturas_generadas"] == 1
        assert fila["proxima_fecha"] > proxima_original

    def test_generar_una_plantilla_inactiva_falla(
        self,
        requiere_postgresql,
    ):

        from aplicacion.modulos.ventas.facturacion_recurrente.servicios import (
            ServicioFacturaRecurrente,
        )

        sufijo = _sufijo()

        cliente = _crear_cliente(sufijo)

        datos = _datos_plantilla(
            cliente.id,
            proxima_fecha=date.today(),
        )
        datos["activa"] = False

        plantilla = ServicioFacturaRecurrente.guardar(
            datos,
            _lineas(),
        )

        with pytest.raises(ValueError, match="inactiva"):

            ServicioFacturaRecurrente.generar_una(
                plantilla.id,
            )

    def test_generar_pendientes_solo_toma_vencidas_y_activas(
        self,
        requiere_postgresql,
    ):

        from aplicacion.modulos.ventas.facturacion_recurrente.servicios import (
            ServicioFacturaRecurrente,
        )

        sufijo = _sufijo()

        cliente = _crear_cliente(sufijo)

        vencida = ServicioFacturaRecurrente.guardar(
            _datos_plantilla(
                cliente.id,
                proxima_fecha=date.today() - timedelta(days=1),
            ),
            _lineas(),
        )

        futura = ServicioFacturaRecurrente.guardar(
            _datos_plantilla(
                cliente.id,
                proxima_fecha=date.today() + timedelta(days=30),
            ),
            _lineas(),
        )

        datos_inactiva = _datos_plantilla(
            cliente.id,
            proxima_fecha=date.today() - timedelta(days=1),
        )
        datos_inactiva["activa"] = False

        inactiva = ServicioFacturaRecurrente.guardar(
            datos_inactiva,
            _lineas(),
        )

        resultado = ServicioFacturaRecurrente.generar_pendientes()

        assert resultado["generadas"] >= 1
        assert resultado["errores"] == []

        filas = {
            f["id"]: f
            for f in ServicioFacturaRecurrente.listar()
        }

        assert filas[vencida.id]["facturas_generadas"] == 1
        assert filas[futura.id]["facturas_generadas"] == 0
        assert filas[inactiva.id]["facturas_generadas"] == 0

    def test_eliminar_plantilla(
        self,
        requiere_postgresql,
    ):

        from aplicacion.modulos.ventas.facturacion_recurrente.servicios import (
            ServicioFacturaRecurrente,
        )

        sufijo = _sufijo()

        cliente = _crear_cliente(sufijo)

        plantilla = ServicioFacturaRecurrente.guardar(
            _datos_plantilla(
                cliente.id,
                proxima_fecha=date.today(),
            ),
            _lineas(),
        )

        ServicioFacturaRecurrente.eliminar(plantilla.id)

        ids = {
            f["id"] for f in ServicioFacturaRecurrente.listar()
        }

        assert plantilla.id not in ids
