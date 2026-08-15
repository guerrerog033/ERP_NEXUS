from __future__ import annotations

import json
import secrets
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse

from aplicacion.nucleo.configuracion import Configuracion


class ServidorApiErp:
    """API REST y portal web para integraciones externas."""

    _servidor: ThreadingHTTPServer | None = None
    _hilo: threading.Thread | None = None

    @classmethod
    def iniciar(cls) -> None:
        config = Configuracion.obtener(
            "api",
        ) or {}

        if not config.get(
            "habilitado",
            False,
        ):
            return

        if cls._servidor is not None:
            return

        puerto = int(
            config.get(
                "puerto",
                8765,
            )
        )

        cls._servidor = ThreadingHTTPServer(
            ("127.0.0.1", puerto),
            cls._fabrica_handler(),
        )

        cls._hilo = threading.Thread(
            target=cls._servidor.serve_forever,
            daemon=True,
            name="erp-api",
        )
        cls._hilo.start()

    @classmethod
    def detener(cls) -> None:
        if cls._servidor is not None:
            cls._servidor.shutdown()
            cls._servidor = None

    @classmethod
    def _fabrica_handler(cls):
        api = cls

        class Handler(BaseHTTPRequestHandler):
            def _responder(
                self,
                codigo: int,
                datos: dict,
            ):
                cuerpo = json.dumps(
                    datos,
                    ensure_ascii=False,
                ).encode("utf-8")

                self.send_response(codigo)
                self.send_header(
                    "Content-Type",
                    "application/json; charset=utf-8",
                )
                self.send_header(
                    "Access-Control-Allow-Origin",
                    "*",
                )
                self.end_headers()
                self.wfile.write(cuerpo)

            def _html(
                self,
                codigo: int,
                html: str,
            ):
                cuerpo = html.encode("utf-8")
                self.send_response(codigo)
                self.send_header(
                    "Content-Type",
                    "text/html; charset=utf-8",
                )
                self.end_headers()
                self.wfile.write(cuerpo)

            def do_GET(self):
                ruta = urlparse(
                    self.path,
                )
                partes = [
                    p
                    for p in ruta.path.split(
                        "/",
                    )
                    if p
                ]

                if partes == ["api", "salud"]:
                    self._responder(
                        200,
                        {
                            "estado": "ok",
                            "producto": "ERP NEXUS",
                        },
                    )
                    return

                if (
                    len(partes) == 3
                    and partes[0] == "portal"
                    and partes[1] == "cotizacion"
                ):
                    html = api._portal_cotizacion(
                        partes[2],
                    )
                    self._html(
                        200,
                        html,
                    )
                    return

                self._responder(
                    404,
                    {"error": "No encontrado"},
                )

            def do_POST(self):
                ruta = urlparse(
                    self.path,
                )
                partes = [
                    p
                    for p in ruta.path.split(
                        "/",
                    )
                    if p
                ]

                longitud = int(
                    self.headers.get(
                        "Content-Length",
                        0,
                    )
                )

                cuerpo = (
                    self.rfile.read(longitud)
                    if longitud
                    else b""
                )

                datos = {}

                if cuerpo:
                    try:
                        datos = json.loads(
                            cuerpo.decode(
                                "utf-8",
                            )
                        )
                    except json.JSONDecodeError:
                        datos = {
                            k: v[0]
                            for k, v in parse_qs(
                                cuerpo.decode(
                                    "utf-8",
                                )
                            ).items()
                        }

                if (
                    len(partes) == 4
                    and partes[:3]
                    == [
                        "api",
                        "cotizaciones",
                        "aceptar",
                    ]
                ):
                    resultado = (
                        api._aceptar_cotizacion(
                            partes[3],
                            datos,
                        )
                    )
                    self._responder(
                        200,
                        resultado,
                    )
                    return

                if partes == [
                    "api",
                    "correo",
                    "procesar",
                ]:
                    from aplicacion.integraciones.correo.servicio_correo_facturas import (
                        ServicioCorreoFacturas,
                    )

                    self._responder(
                        200,
                        ServicioCorreoFacturas.procesar_buzon(),
                    )
                    return

                if partes == [
                    "api",
                    "compras",
                    "sincronizar",
                ]:
                    from aplicacion.integraciones.dian.servicio_recepcion import (
                        ServicioRecepcionCompras,
                    )

                    resultado = (
                        ServicioRecepcionCompras.sincronizar()
                    )

                    self._responder(
                        200,
                        {
                            "importadas": resultado.importadas,
                            "mensaje": resultado.mensaje,
                        },
                    )
                    return

                self._responder(
                    404,
                    {"error": "No encontrado"},
                )

            def log_message(
                self,
                format,
                *args,
            ):
                return

        return Handler

    @classmethod
    def _aceptar_cotizacion(
        cls,
        codigo: str,
        datos: dict,
    ) -> dict:
        from aplicacion.modulos.ventas.cotizaciones.servicios import (
            ServicioCotizacion,
        )

        codigo_verificacion = str(
            datos.get(
                "codigo_verificacion",
                "",
            )
        )

        firma = str(
            datos.get(
                "firma",
                "",
            )
        )

        return ServicioCotizacion.aceptar_por_codigo(
            codigo,
            codigo_verificacion=codigo_verificacion,
            firma_cliente=firma,
        )

    @classmethod
    def _portal_cotizacion(
        cls,
        codigo: str,
    ) -> str:
        from aplicacion.comunes.qr_util import (
            generar_qr_data_uri,
        )
        from aplicacion.modulos.ventas.cotizaciones.servicios import (
            ServicioCotizacion,
        )

        cotizacion = (
            ServicioCotizacion.obtener_por_codigo_aceptacion(
                codigo,
            )
        )

        if cotizacion is None:
            return "<h1>Cotización no encontrada</h1>"

        url = (
            f"http://127.0.0.1:"
            f"{Configuracion.obtener('api', 'puerto', 8765)}"
            f"/portal/cotizacion/{codigo}"
        )

        qr = generar_qr_data_uri(
            url,
        )

        return f"""
        <!DOCTYPE html>
        <html><head><meta charset="utf-8"><title>Cotización {cotizacion.numero}</title></head>
        <body style="font-family:Arial,sans-serif;max-width:720px;margin:40px auto;">
        <h1>Cotización {cotizacion.numero}</h1>
        <p>Total: ${cotizacion.total:,.0f}</p>
        <p>Estado: {cotizacion.estado_aceptacion or 'pendiente'}</p>
        <img src="{qr}" alt="QR" width="160"/>
        <form method="post" action="/api/cotizaciones/aceptar/{codigo}">
          <p><label>Código verificación<br><input name="codigo_verificacion" required></label></p>
          <p><label>Firma (nombre completo)<br><input name="firma" required></label></p>
          <button type="submit">Aceptar cotización</button>
        </form>
        </body></html>
        """

    @classmethod
    def generar_codigo_verificacion(cls) -> str:
        return secrets.token_hex(
            3,
        ).upper()
