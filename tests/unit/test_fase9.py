from datetime import date

from aplicacion.modulos.ventas.pos.servicios import (
    ServicioPOSVenta,
)
from aplicacion.modulos.ventas.pos.ticket import (
    generar_html_ticket_pos,
)


def test_generar_html_ticket_pos():

    html = generar_html_ticket_pos(
        factura_numero="FV-0001",
        cliente="Cliente Demo",
        lineas=[
            {
                "descripcion": "Producto A",
                "cantidad": 2,
                "precio_unitario": 1000,
                "total_linea": 2000,
            },
        ],
        total=2000,
        recibido=5000,
        cambio=3000,
        metodo_pago="efectivo",
        usuario="cajero1",
    )

    assert "FV-0001" in html
    assert "Producto A" in html
    assert "Gracias por su compra" in html


def test_listar_historial_pasa_filtros(
    monkeypatch,
):

    capturado = {}

    def _fake_listar(
        **kwargs,
    ):

        capturado.update(
            kwargs,
        )

        return []

    monkeypatch.setattr(
        ServicioPOSVenta.repositorio_log,
        "listar_historial",
        _fake_listar,
    )

    ServicioPOSVenta.listar_historial(
        fecha_desde=date(
            2026,
            1,
            1,
        ),
        fecha_hasta=date(
            2026,
            1,
            31,
        ),
        metodo_pago="tarjeta",
        usuario="ana",
    )

    assert capturado["metodo_pago"] == "tarjeta"
    assert capturado["usuario"] == "ana"


def test_resumen_caja_delega(
    monkeypatch,
):

    esperado = {
        "ventas": 3,
        "total": 150000.0,
        "recibido": 160000.0,
        "cambio": 10000.0,
        "por_metodo": [],
    }

    monkeypatch.setattr(
        ServicioPOSVenta.repositorio_log,
        "resumen_caja",
        lambda **kwargs: esperado,
    )

    resultado = ServicioPOSVenta.resumen_caja(
        fecha=date.today(),
    )

    assert resultado["ventas"] == 3
    assert resultado["total"] == 150000.0


def test_verificar_alembic_cadena(
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
