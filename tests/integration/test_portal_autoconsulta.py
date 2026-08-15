from __future__ import annotations

import os
import time
import urllib.request
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


def _crear_empresa_si_falta():
    from aplicacion.maestros.empresas.repositorio import (
        EmpresaRepositorio,
    )
    from aplicacion.maestros.empresas.servicios import (
        EmpresaServicio,
    )

    if EmpresaRepositorio.obtener_por_nit(
        "900123456",
    ) is None:

        EmpresaServicio.guardar(
            {
                "razon_social": "Empresa Demo S.A.S.",
                "nit": "900123456",
                "dv": "7",
                "pais": "Colombia",
                "activo": True,
            },
        )


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
            "razon_social": f"Cliente Portal Demo {sufijo}",
            "direccion": "Calle 1 # 2-3",
            "pais": "Colombia",
            "departamento": "Cundinamarca",
            "ciudad": "Bogotá",
            "correo": f"cliente.{sufijo}@demo.com",
            "dias_credito": 0,
            "cupo_credito": 0,
            "resp_r99_pn": True,
        },
    )


def _crear_factura_venta(cliente_id: int):
    from aplicacion.modulos.ventas.facturas.servicios import (
        ServicioFacturaVenta,
    )

    return ServicioFacturaVenta.guardar_completa(
        {
            "cliente_id": cliente_id,
            "fecha": date.today(),
        },
        [
            {
                "descripcion": "Servicio de prueba",
                "cantidad": 1,
                "precio_unitario": 100000,
            },
        ],
    )


class TestServicioPortalTercero:

    def test_datos_cuenta_token_invalido_devuelve_none(
        self,
        requiere_postgresql,
    ):
        from aplicacion.api.portal_servicio import (
            ServicioPortalTercero,
        )

        assert (
            ServicioPortalTercero.datos_cuenta(
                "token-que-no-existe",
            )
            is None
        )
        assert (
            ServicioPortalTercero.datos_cuenta(
                "",
            )
            is None
        )

    def test_datos_cuenta_lista_facturas_del_cliente(
        self,
        requiere_postgresql,
    ):
        from aplicacion.api.portal_servicio import (
            ServicioPortalTercero,
        )
        from aplicacion.maestros.terceros.servicio import (
            TerceroServicio,
        )

        _crear_empresa_si_falta()

        sufijo = _sufijo()

        cliente = _crear_cliente(
            sufijo,
        )

        assert cliente.es_cliente is True

        factura = _crear_factura_venta(
            cliente.id,
        )

        token = TerceroServicio.generar_token_portal(
            cliente.id,
        )

        datos = ServicioPortalTercero.datos_cuenta(
            token,
        )

        assert datos is not None
        assert datos["documento"] == cliente.numero_documento

        numeros = [
            f["numero"]
            for f in datos["facturas_venta"]
        ]

        assert factura.numero in numeros
        assert datos["facturas_compra"] == []

    def test_pdf_factura_venta_niega_acceso_a_factura_ajena(
        self,
        requiere_postgresql,
    ):
        from aplicacion.api.portal_servicio import (
            ServicioPortalTercero,
        )
        from aplicacion.maestros.terceros.servicio import (
            TerceroServicio,
        )

        _crear_empresa_si_falta()

        cliente_dueno = _crear_cliente(
            _sufijo(),
        )
        cliente_ajeno = _crear_cliente(
            _sufijo(),
        )

        factura = _crear_factura_venta(
            cliente_dueno.id,
        )

        token_ajeno = TerceroServicio.generar_token_portal(
            cliente_ajeno.id,
        )

        assert (
            ServicioPortalTercero.pdf_factura_venta(
                token_ajeno,
                factura.id,
            )
            is None
        )

    def test_pdf_factura_venta_del_dueno_genera_archivo_real(
        self,
        requiere_postgresql,
    ):
        from aplicacion.api.portal_servicio import (
            ServicioPortalTercero,
        )
        from aplicacion.maestros.terceros.servicio import (
            TerceroServicio,
        )

        _crear_empresa_si_falta()

        cliente = _crear_cliente(
            _sufijo(),
        )

        factura = _crear_factura_venta(
            cliente.id,
        )

        token = TerceroServicio.generar_token_portal(
            cliente.id,
        )

        ruta = ServicioPortalTercero.pdf_factura_venta(
            token,
            factura.id,
        )

        assert ruta is not None
        assert ruta.is_file()
        assert ruta.stat().st_size > 0


class TestPortalHttp:

    @pytest.fixture(autouse=True)
    def _servidor(
        self,
        requiere_postgresql,
        monkeypatch,
    ):
        from aplicacion.api.servidor import ServidorApiErp
        from aplicacion.nucleo.configuracion import Configuracion

        Configuracion.cargar()

        monkeypatch.setitem(
            Configuracion._datos,
            "api",
            {
                "habilitado": True,
                "puerto": 8799,
            },
        )

        ServidorApiErp.detener()

        ServidorApiErp.iniciar()

        time.sleep(0.2)

        yield

        ServidorApiErp.detener()

    def test_portal_mi_cuenta_token_invalido_404(self):

        peticion = urllib.request.Request(
            "http://127.0.0.1:8799/portal/mi-cuenta/token-invalido",
        )

        try:
            urllib.request.urlopen(
                peticion,
                timeout=5,
            )

            assert False, "Se esperaba HTTPError 404"

        except urllib.error.HTTPError as error:

            assert error.code == 404

    def test_portal_mi_cuenta_token_valido_muestra_facturas(
        self,
    ):
        from aplicacion.maestros.terceros.servicio import (
            TerceroServicio,
        )

        _crear_empresa_si_falta()

        cliente = _crear_cliente(
            _sufijo(),
        )

        factura = _crear_factura_venta(
            cliente.id,
        )

        token = TerceroServicio.generar_token_portal(
            cliente.id,
        )

        with urllib.request.urlopen(
            f"http://127.0.0.1:8799/portal/mi-cuenta/{token}",
            timeout=5,
        ) as respuesta:

            cuerpo = respuesta.read().decode(
                "utf-8",
            )

            assert respuesta.status == 200

        assert factura.numero in cuerpo
        assert cliente.nombre_completo in cuerpo
