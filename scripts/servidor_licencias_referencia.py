"""
Servidor HTTP de referencia para validación online de licencias.

Uso:
    python scripts/servidor_licencias_referencia.py

Endpoints (POST JSON):
    /api/v1/licencias/validar
    /api/v1/licencias/activar

Respuesta ejemplo:
    {"valido": true, "revocado": false, "mensaje": "OK", "edicion": "profesional", "max_usuarios": 10}
"""

from __future__ import annotations

import json
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse


SERiales_REVOCADOS: set[str] = set()


class ManejadorLicencias(BaseHTTPRequestHandler):

    def log_message(
        self,
        formato,
        *args,
    ):

        print(
            f"[servidor] {self.address_string()} - {formato % args}",
        )

    def _responder(
        self,
        codigo: int,
        cuerpo: dict,
    ) -> None:

        datos = json.dumps(
            cuerpo,
            ensure_ascii=False,
        ).encode(
            "utf-8",
        )

        self.send_response(
            codigo,
        )

        self.send_header(
            "Content-Type",
            "application/json; charset=utf-8",
        )

        self.send_header(
            "Content-Length",
            str(
                len(
                    datos,
                ),
            ),
        )

        self.end_headers()

        self.wfile.write(
            datos,
        )

    def _leer_json(
        self,
    ) -> dict:

        longitud = int(
            self.headers.get(
                "Content-Length",
                0,
            )
            or 0,
        )

        if longitud <= 0:

            return {}

        raw = self.rfile.read(
            longitud,
        )

        if not raw:

            return {}

        return json.loads(
            raw.decode(
                "utf-8",
            ),
        )

    def do_POST(
        self,
    ) -> None:

        ruta = urlparse(
            self.path,
        ).path

        payload = self._leer_json()

        if payload.get(
            "prueba",
        ):

            self._responder(
                200,
                {
                    "valido": True,
                    "mensaje": "Servidor de referencia activo.",
                },
            )

            return

        serial = str(
            payload.get(
                "serial",
                "",
            )
            or "",
        ).strip()

        if not serial:

            self._responder(
                400,
                {
                    "valido": False,
                    "mensaje": "Falta serial.",
                },
            )

            return

        revocado = serial in SERiales_REVOCADOS

        if ruta.endswith(
            "/activar",
        ):

            self._responder(
                200,
                {
                    "valido": not revocado,
                    "revocado": revocado,
                    "mensaje": (
                        "Activación registrada."
                        if not revocado
                        else "Serial revocado en servidor."
                    ),
                    "edicion": "profesional",
                    "max_usuarios": 10,
                },
            )

            return

        if ruta.endswith(
            "/validar",
        ):

            self._responder(
                200,
                {
                    "valido": not revocado,
                    "revocado": revocado,
                    "mensaje": (
                        "Licencia vigente."
                        if not revocado
                        else "Licencia revocada."
                    ),
                    "edicion": "profesional",
                    "max_usuarios": 10,
                },
            )

            return

        self._responder(
            404,
            {
                "valido": False,
                "mensaje": f"Ruta no encontrada: {ruta}",
            },
        )


def main() -> None:

    host = "127.0.0.1"

    puerto = 8765

    servidor = HTTPServer(
        (
            host,
            puerto,
        ),
        ManejadorLicencias,
    )

    print(
        f"Servidor de licencias en http://{host}:{puerto}",
    )

    print(
        "  POST /api/v1/licencias/validar",
    )

    print(
        "  POST /api/v1/licencias/activar",
    )

    try:

        servidor.serve_forever()

    except KeyboardInterrupt:

        print("\nDetenido.")

        servidor.server_close()


if __name__ == "__main__":

    main()
