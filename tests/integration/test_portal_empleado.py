from __future__ import annotations

import os
import time
import urllib.error
import urllib.parse
import urllib.request
import uuid

import pytest

from aplicacion.base_datos.registro_modelos import (
    importar_modelos,
)

pytestmark = pytest.mark.integration

PUERTO = 8798


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


def _crear_usuario_prueba(password: str = "Clave123"):

    from aplicacion.autenticacion.modelos import Usuario
    from aplicacion.autenticacion.seguridad import (
        cifrar_password,
    )
    from aplicacion.base_datos.conexion import SessionLocal

    sufijo = _sufijo()
    nombre_usuario = f"empleado.{sufijo}"

    db = SessionLocal()

    try:

        registro = Usuario(
            usuario=nombre_usuario,
            nombre=f"Empleado Demo {sufijo}",
            correo=f"{nombre_usuario}@demo.com",
            password=cifrar_password(
                password,
            ),
            activo=True,
        )

        db.add(registro)
        db.commit()
        db.refresh(registro)

        return registro.usuario, registro.nombre

    finally:

        db.close()


class TestServicioPortalEmpleado:

    def test_ventas_del_dia_incluye_factura_de_hoy(
        self,
        requiere_postgresql,
    ):

        from datetime import date

        from aplicacion.api.portal_empleado_servicio import (
            ServicioPortalEmpleado,
        )
        from aplicacion.maestros.terceros.servicio import (
            TerceroServicio,
        )
        from aplicacion.modulos.ventas.facturas.servicios import (
            ServicioFacturaVenta,
        )

        sufijo = _sufijo()

        documento = str(
            900000000
            + int(sufijo[:6], 16) % 99999999,
        )

        cliente = TerceroServicio.guardar(
            {
                "tipo_documento": "NIT",
                "numero_documento": documento,
                "tipo_tercero": "Cliente",
                "razon_social": f"Cliente Portal Emp {sufijo}",
                "pais": "Colombia",
                "resp_r99_pn": True,
            },
        )

        factura = ServicioFacturaVenta.guardar_completa(
            {
                "cliente_id": cliente.id,
                "fecha": date.today(),
            },
            [
                {
                    "descripcion": "Servicio de prueba",
                    "cantidad": 1,
                    "precio_unitario": 250000,
                },
            ],
        )

        from aplicacion.base_datos.conexion import (
            SessionLocal,
        )
        from aplicacion.modulos.ventas.facturas.modelos import (
            FacturaVenta,
        )

        db = SessionLocal()

        try:

            registro = (
                db.query(FacturaVenta)
                .filter(
                    FacturaVenta.id == factura.id,
                )
                .one()
            )

            registro.contabilizado = True

            db.commit()

        finally:

            db.close()

        datos = ServicioPortalEmpleado.ventas_del_dia()

        numeros = [
            fila["numero"] for fila in datos["facturas"]
        ]

        assert factura.numero in numeros
        assert datos["total"] >= 250000.0

    def test_buscar_inventario_texto_vacio_no_consulta(
        self,
        requiere_postgresql,
    ):

        from aplicacion.api.portal_empleado_servicio import (
            ServicioPortalEmpleado,
        )

        assert (
            ServicioPortalEmpleado.buscar_inventario(
                "",
            )
            == []
        )

    def test_buscar_inventario_encuentra_producto_creado(
        self,
        requiere_postgresql,
    ):

        from aplicacion.api.portal_empleado_servicio import (
            ServicioPortalEmpleado,
        )
        from aplicacion.maestros.productos.servicios import (
            ServicioProducto,
        )

        sufijo = _sufijo()

        producto = ServicioProducto.guardar_completo(
            {
                "codigo": f"PORTMOV{sufijo.upper()}",
                "nombre": f"Producto Portal Movil {sufijo}",
                "tipo": "producto",
                "precio_venta": 1000,
                "costo": 500,
                "existencia": 12,
                "stock_minimo": 0,
                "activo": True,
            },
        )

        resultados = (
            ServicioPortalEmpleado.buscar_inventario(
                producto.codigo,
            )
        )

        codigos = [r["codigo"] for r in resultados]

        assert producto.codigo in codigos


class TestServicioSesionMovilConUsuarioReal:

    def test_login_credenciales_invalidas_no_genera_sesion(
        self,
        requiere_postgresql,
    ):

        from aplicacion.api.servidor import ServidorApiErp

        nombre_usuario, _ = _crear_usuario_prueba(
            "ClaveCorrecta",
        )

        assert (
            ServidorApiErp._empleado_login(
                nombre_usuario,
                "ClaveIncorrecta",
            )
            is None
        )

    def test_login_credenciales_validas_genera_sesion(
        self,
        requiere_postgresql,
    ):

        from aplicacion.api.servidor import ServidorApiErp
        from aplicacion.api.sesion_movil import (
            ServicioSesionMovil,
        )

        nombre_usuario, nombre = _crear_usuario_prueba(
            "ClaveCorrecta",
        )

        token = ServidorApiErp._empleado_login(
            nombre_usuario,
            "ClaveCorrecta",
        )

        assert token is not None

        sesion = ServicioSesionMovil.obtener_sesion(
            token,
        )

        assert sesion is not None
        assert sesion["nombre"] == nombre


class TestPortalEmpleadoHttp:

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
                "puerto": PUERTO,
            },
        )

        ServidorApiErp.detener()

        ServidorApiErp.iniciar()

        time.sleep(0.2)

        yield

        ServidorApiErp.detener()

    def test_pagina_login_carga(self):

        with urllib.request.urlopen(
            f"http://127.0.0.1:{PUERTO}/portal/empleado",
            timeout=5,
        ) as respuesta:

            cuerpo = respuesta.read().decode("utf-8")

            assert respuesta.status == 200

        assert "Ingresar" in cuerpo

    def test_login_incorrecto_devuelve_401(self):

        datos = urllib.parse.urlencode(
            {
                "usuario": "no-existe",
                "password": "no-importa",
            },
        ).encode("utf-8")

        peticion = urllib.request.Request(
            f"http://127.0.0.1:{PUERTO}"
            "/portal/empleado/login",
            data=datos,
            method="POST",
        )

        try:

            urllib.request.urlopen(
                peticion,
                timeout=5,
            )

            assert False, "Se esperaba HTTPError 401"

        except urllib.error.HTTPError as error:

            assert error.code == 401

    def test_login_correcto_lleva_al_panel(self):

        nombre_usuario, nombre = _crear_usuario_prueba(
            "ClaveCorrecta",
        )

        datos = urllib.parse.urlencode(
            {
                "usuario": nombre_usuario,
                "password": "ClaveCorrecta",
            },
        ).encode("utf-8")

        peticion = urllib.request.Request(
            f"http://127.0.0.1:{PUERTO}"
            "/portal/empleado/login",
            data=datos,
            method="POST",
        )

        with urllib.request.urlopen(
            peticion,
            timeout=5,
        ) as respuesta:

            cuerpo = respuesta.read().decode("utf-8")

            assert respuesta.status == 200
            assert "panel" in respuesta.geturl()

        assert nombre in cuerpo

    def test_ruta_protegida_sin_token_regresa_a_login(self):

        with urllib.request.urlopen(
            f"http://127.0.0.1:{PUERTO}"
            "/portal/empleado/cartera",
            timeout=5,
        ) as respuesta:

            cuerpo = respuesta.read().decode("utf-8")

        assert "Ingresar" in cuerpo

    def test_cartera_con_token_valido_responde_200(self):

        from aplicacion.api.sesion_movil import (
            ServicioSesionMovil,
        )
        from aplicacion.autenticacion.modelos import Usuario
        from aplicacion.base_datos.conexion import (
            SessionLocal,
        )

        nombre_usuario, _ = _crear_usuario_prueba(
            "ClaveCorrecta",
        )

        db = SessionLocal()

        try:

            usuario_obj = (
                db.query(Usuario)
                .filter(
                    Usuario.usuario == nombre_usuario,
                )
                .first()
            )

            token = ServicioSesionMovil.iniciar_sesion(
                usuario_obj,
            )

        finally:

            db.close()

        with urllib.request.urlopen(
            f"http://127.0.0.1:{PUERTO}"
            f"/portal/empleado/cartera?token={token}",
            timeout=5,
        ) as respuesta:

            cuerpo = respuesta.read().decode("utf-8")

            assert respuesta.status == 200

        assert "Cartera" in cuerpo

    def test_salir_invalida_la_sesion(self):

        from aplicacion.api.sesion_movil import (
            ServicioSesionMovil,
        )
        from aplicacion.autenticacion.modelos import Usuario
        from aplicacion.base_datos.conexion import (
            SessionLocal,
        )

        nombre_usuario, _ = _crear_usuario_prueba(
            "ClaveCorrecta",
        )

        db = SessionLocal()

        try:

            usuario_obj = (
                db.query(Usuario)
                .filter(
                    Usuario.usuario == nombre_usuario,
                )
                .first()
            )

            token = ServicioSesionMovil.iniciar_sesion(
                usuario_obj,
            )

        finally:

            db.close()

        urllib.request.urlopen(
            f"http://127.0.0.1:{PUERTO}"
            f"/portal/empleado/salir?token={token}",
            timeout=5,
        )

        assert (
            ServicioSesionMovil.obtener_sesion(
                token,
            )
            is None
        )
