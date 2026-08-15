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

            def _archivo(
                self,
                ruta,
                *,
                tipo_contenido: str,
            ):
                if ruta is None:
                    self._responder(
                        404,
                        {"error": "Documento no encontrado"},
                    )
                    return

                cuerpo = ruta.read_bytes()

                self.send_response(200)
                self.send_header(
                    "Content-Type",
                    tipo_contenido,
                )
                self.send_header(
                    "Content-Disposition",
                    f'attachment; filename="{ruta.name}"',
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

                if (
                    len(partes) == 3
                    and partes[0] == "portal"
                    and partes[1] == "mi-cuenta"
                ):
                    html = api._portal_mi_cuenta(
                        partes[2],
                    )
                    self._html(
                        200 if html else 404,
                        html
                        or "<h1>Acceso no válido</h1>",
                    )
                    return

                if (
                    len(partes) == 6
                    and partes[0] == "portal"
                    and partes[1] == "mi-cuenta"
                    and partes[3] in (
                        "venta",
                        "compra",
                    )
                    and partes[5] in (
                        "pdf",
                        "xml",
                    )
                ):
                    self._servir_documento_portal(
                        token=partes[2],
                        tipo_documento=partes[3],
                        factura_id=partes[4],
                        formato=partes[5],
                    )
                    return

                self._responder(
                    404,
                    {"error": "No encontrado"},
                )

            def _servir_documento_portal(
                self,
                *,
                token: str,
                tipo_documento: str,
                factura_id: str,
                formato: str,
            ):
                try:
                    id_factura = int(
                        factura_id,
                    )
                except ValueError:
                    self._responder(
                        404,
                        {"error": "Documento no encontrado"},
                    )
                    return

                ruta = api._ruta_documento_portal(
                    token,
                    tipo_documento,
                    id_factura,
                    formato,
                )

                tipo_contenido = (
                    "application/pdf"
                    if formato == "pdf"
                    else "application/xml"
                )

                self._archivo(
                    ruta,
                    tipo_contenido=tipo_contenido,
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
    def _portal_mi_cuenta(
        cls,
        token: str,
    ) -> str | None:
        from aplicacion.api.portal_servicio import (
            ServicioPortalTercero,
        )

        datos = ServicioPortalTercero.datos_cuenta(
            token,
        )

        if datos is None:
            return None

        def _fila(
            factura: dict,
            tipo: str,
        ) -> str:
            base = (
                f"/portal/mi-cuenta/{token}/"
                f"{tipo}/{factura['id']}"
            )

            pdf_link = (
                f'<a href="{base}/pdf">PDF</a>'
            )

            xml_link = (
                f' · <a href="{base}/xml">XML</a>'
                if factura["tiene_xml"]
                else ""
            )

            return f"""
            <tr>
                <td>{factura['numero']}</td>
                <td>{factura['fecha']}</td>
                <td style="text-align:right;">
                    ${factura['total']:,.0f}
                </td>
                <td style="text-align:right;">
                    ${factura['saldo_pendiente']:,.0f}
                </td>
                <td>{factura['estado_pago'] or ''}</td>
                <td>{pdf_link}{xml_link}</td>
            </tr>
            """

        def _tabla(
            titulo: str,
            facturas: list[dict],
            tipo: str,
        ) -> str:
            if not facturas:
                return ""

            filas = "".join(
                _fila(
                    factura,
                    tipo,
                )
                for factura in facturas
            )

            return f"""
            <h2>{titulo}</h2>
            <table border="1" cellpadding="6"
                   style="border-collapse:collapse;width:100%;">
                <thead><tr>
                    <th>Número</th><th>Fecha</th>
                    <th>Total</th><th>Saldo</th>
                    <th>Estado</th><th>Documentos</th>
                </tr></thead>
                <tbody>{filas}</tbody>
            </table>
            """

        return f"""
        <!DOCTYPE html>
        <html><head><meta charset="utf-8">
        <title>Mi cuenta — {datos['nombre']}</title></head>
        <body style="font-family:Arial,sans-serif;max-width:900px;margin:40px auto;">
        <h1>{datos['nombre']}</h1>
        <p>Documento: {datos['documento']}</p>
        {_tabla(
            "Mis facturas",
            datos['facturas_venta'],
            'venta',
        )}
        {_tabla(
            "Facturas a mi proveedor",
            datos['facturas_compra'],
            'compra',
        )}
        </body></html>
        """

    @classmethod
    def _ruta_documento_portal(
        cls,
        token: str,
        tipo_documento: str,
        factura_id: int,
        formato: str,
    ):
        from aplicacion.api.portal_servicio import (
            ServicioPortalTercero,
        )

        metodos = {
            ("venta", "pdf"): (
                ServicioPortalTercero.pdf_factura_venta
            ),
            ("venta", "xml"): (
                ServicioPortalTercero.xml_factura_venta
            ),
            ("compra", "pdf"): (
                ServicioPortalTercero.pdf_factura_compra
            ),
            ("compra", "xml"): (
                ServicioPortalTercero.xml_factura_compra
            ),
        }

        metodo = metodos.get(
            (
                tipo_documento,
                formato,
            ),
        )

        if metodo is None:
            return None

        return metodo(
            token,
            factura_id,
        )

    @classmethod
    def generar_codigo_verificacion(cls) -> str:
        return secrets.token_hex(
            3,
        ).upper()
