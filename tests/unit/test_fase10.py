from datetime import date

from types import SimpleNamespace

import pytest

from aplicacion.modulos.ventas.pos.servicios import (
    ServicioPOSVenta,
)


def test_alertas_stock_insuficiente(
    monkeypatch,
):

    class _Producto:

        id = 1
        nombre = "Producto A"
        stock_minimo = 5.0

    class _Db:

        def query(
            self,
            _modelo,
        ):

            return self

        def filter(
            self,
            *_args,
            **_kwargs,
        ):

            return self

        def first(
            self,
        ):

            return _Producto()

        def close(
            self,
        ):

            return None

    monkeypatch.setattr(
        "aplicacion.base_datos.conexion.SessionLocal",
        lambda: _Db(),
    )
    monkeypatch.setattr(
        "aplicacion.modulos.inventario.servicios.ServicioInventario._bodega_operacion",
        lambda _db, contexto="pos": SimpleNamespace(
            id=1,
        ),
    )
    monkeypatch.setattr(
        "aplicacion.modulos.inventario.servicios.ServicioInventario._obtener_existencia",
        lambda _db, _producto, _variante_id, bodega_id=None: (
            1.0,
            None,
        ),
    )

    bloqueantes, avisos = ServicioPOSVenta.alertas_stock(
        [
            {
                "producto_id": 1,
                "descripcion": "Producto A",
                "cantidad": 2,
            },
        ],
    )

    assert len(
        bloqueantes,
    ) == 1
    assert "insuficiente" in bloqueantes[
        0
    ].lower()
    assert avisos == []


def test_alertas_stock_bajo_minimo(
    monkeypatch,
):

    class _Producto:

        id = 2
        nombre = "Producto B"
        stock_minimo = 10.0

    class _Db:

        def query(
            self,
            _modelo,
        ):

            return self

        def filter(
            self,
            *_args,
            **_kwargs,
        ):

            return self

        def first(
            self,
        ):

            return _Producto()

        def close(
            self,
        ):

            return None

    monkeypatch.setattr(
        "aplicacion.base_datos.conexion.SessionLocal",
        lambda: _Db(),
    )
    monkeypatch.setattr(
        "aplicacion.modulos.inventario.servicios.ServicioInventario._bodega_operacion",
        lambda _db, contexto="pos": SimpleNamespace(
            id=1,
        ),
    )
    monkeypatch.setattr(
        "aplicacion.modulos.inventario.servicios.ServicioInventario._obtener_existencia",
        lambda _db, _producto, _variante_id, bodega_id=None: (
            12.0,
            None,
        ),
    )

    bloqueantes, avisos = ServicioPOSVenta.alertas_stock(
        [
            {
                "producto_id": 2,
                "descripcion": "Producto B",
                "cantidad": 5,
            },
        ],
    )

    assert bloqueantes == []
    assert len(
        avisos,
    ) == 1
    assert "mínimo" in avisos[
        0
    ].lower()


def test_efectivo_esperado_delega(
    monkeypatch,
):

    monkeypatch.setattr(
        ServicioPOSVenta.repositorio_log,
        "efectivo_esperado",
        lambda **kwargs: 125000.0,
    )

    assert (
        ServicioPOSVenta.efectivo_esperado(
            fecha=date.today(),
        )
        == 125000.0
    )


def test_cerrar_caja_delega(
    monkeypatch,
):

    capturado = {}

    monkeypatch.setattr(
        ServicioPOSVenta,
        "resumen_caja",
        lambda **kwargs: {
            "ventas": 4,
            "total": 200000.0,
        },
    )
    monkeypatch.setattr(
        ServicioPOSVenta,
        "efectivo_esperado",
        lambda **kwargs: 150000.0,
    )

    def _registrar(
        **kwargs,
    ):

        capturado.update(
            kwargs,
        )

        return {
            "diferencia": 0.0,
        }

    monkeypatch.setattr(
        ServicioPOSVenta.repositorio_cierre,
        "registrar",
        _registrar,
    )

    ServicioPOSVenta.cerrar_caja(
        efectivo_contado=150000.0,
        fecha=date(
            2026,
            8,
            10,
        ),
        observaciones="ok",
    )

    assert (
        capturado["efectivo_esperado"]
        == 150000.0
    )
    assert (
        capturado["efectivo_contado"]
        == 150000.0
    )
    assert capturado["ventas_count"] == 4


def test_reimprimir_ticket_delega(
    monkeypatch,
):

    class _Detalle:

        descripcion = "Item"
        cantidad = 1
        precio_unitario = 5000
        total_linea = 5000

    class _Factura:

        id = 10
        numero = "FV-0010"
        total = 5000
        cliente_id = 3
        detalles = [
            _Detalle(),
        ]

    class _Tercero:

        nombre_completo = "Cliente POS"

    llamadas = {}

    monkeypatch.setattr(
        ServicioPOSVenta.repositorio_log,
        "obtener_log_por_id",
        lambda log_id: {
            "factura_id": 10,
            "recibido": 10000.0,
            "cambio": 5000.0,
            "metodo_pago": "efectivo",
        },
    )
    monkeypatch.setattr(
        "aplicacion.modulos.ventas.facturas.servicios.ServicioFacturaVenta.obtener_completa",
        lambda _id: _Factura(),
    )
    monkeypatch.setattr(
        "aplicacion.maestros.terceros.repositorio.TerceroRepositorio.obtener_por_id",
        lambda _id: _Tercero(),
    )

    def _imprimir(
        **kwargs,
    ):

        llamadas.update(
            kwargs,
        )

        return True

    monkeypatch.setattr(
        ServicioPOSVenta,
        "imprimir_ticket_venta",
        _imprimir,
    )

    assert ServicioPOSVenta.reimprimir_ticket(
        1,
    )
    assert (
        llamadas["cliente_nombre"]
        == "Cliente POS"
    )
    assert (
        llamadas["metodo_pago"]
        == "efectivo"
    )


def test_devolver_venta_desde_log_id(
    monkeypatch,
):

    capturado = {}

    class _Nota:

        id = 20
        numero = "NC-0020"

    monkeypatch.setattr(
        ServicioPOSVenta.repositorio_log,
        "obtener_log_por_id",
        lambda log_id: {
            "factura_id": 10,
        },
    )
    monkeypatch.setattr(
        ServicioPOSVenta.repositorio_log,
        "obtener_log_por_factura",
        lambda factura_id: {
            "id": 1,
            "factura_id": factura_id,
        },
    )
    monkeypatch.setattr(
        "aplicacion.modulos.ventas.facturas.servicios.ServicioFacturaVenta.obtener_completa",
        lambda _id: SimpleNamespace(
            id=10,
            saldo_pendiente=29750.0,
        ),
    )
    monkeypatch.setattr(
        "aplicacion.modulos.ventas.notas_credito.servicios.ServicioNotaCreditoVenta.crear_desde_factura",
        lambda factura_id, motivo=None: (
            capturado.update(
                {
                    "factura_id": factura_id,
                    "motivo": motivo,
                }
            )
            or _Nota()
        ),
    )
    monkeypatch.setattr(
        "aplicacion.modulos.ventas.notas_credito.integracion.IntegracionNotaCreditoVenta.confirmar_generacion",
        lambda id_registro, emitir_dian=False: _Nota(),
    )

    nota = ServicioPOSVenta.devolver_venta(
        log_id=5,
        motivo="Devolución POS",
    )

    assert nota.numero == "NC-0020"
    assert capturado["factura_id"] == 10
    assert capturado["motivo"] == "Devolución POS"


def test_devolver_venta_rechaza_sin_log_pos(
    monkeypatch,
):

    monkeypatch.setattr(
        ServicioPOSVenta.repositorio_log,
        "obtener_log_por_factura",
        lambda _id: None,
    )

    with pytest.raises(
        ValueError,
        match="no proviene de una venta POS",
    ):
        ServicioPOSVenta.devolver_venta(
            factura_id=99,
        )


def test_verificar_alembic_cadena_fase10(
    monkeypatch,
):

    class _Revision:

        revision = "0006_fase10_pos"

    class _Script:

        def get_revisions(
            self,
            label,
        ):

            assert label == "heads"

            return [
                _Revision(),
            ]

    monkeypatch.setattr(
        "alembic.script.ScriptDirectory.from_config",
        lambda config: _Script(),
    )

    from scripts.ci.verificar_alembic import (
        verificar_cadena,
    )

    assert (
        verificar_cadena()
        == "0006_fase10_pos"
    )
