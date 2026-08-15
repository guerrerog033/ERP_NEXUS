from __future__ import annotations

import json
from pathlib import Path

from aplicacion.nucleo.configuracion import Configuracion


class MotorPlantillas:
    """Motor de plantillas editables sin modificar código."""

    TIPOS = (
        "factura",
        "cotizacion",
        "proforma",
        "orden_compra",
        "remision",
        "recibo_caja",
        "comprobante",
        "estado_cuenta",
    )

    @classmethod
    def carpeta(cls) -> Path:
        ruta = Configuracion.obtener(
            "plantillas",
            "ruta",
            "configuracion/plantillas",
        )

        carpeta = Path(ruta)
        carpeta.mkdir(
            parents=True,
            exist_ok=True,
        )

        return carpeta

    @classmethod
    def ruta_plantilla(
        cls,
        tipo: str,
        nombre: str = "predeterminada",
    ) -> Path:
        return (
            cls.carpeta()
            / tipo
            / f"{nombre}.json"
        )

    @classmethod
    def cargar(
        cls,
        tipo: str,
        nombre: str = "predeterminada",
    ) -> dict:
        ruta = cls.ruta_plantilla(
            tipo,
            nombre,
        )

        if not ruta.exists():
            return cls.plantilla_defecto(tipo)

        return json.loads(
            ruta.read_text(
                encoding="utf-8",
            )
        )

    @classmethod
    def guardar(
        cls,
        tipo: str,
        datos: dict,
        nombre: str = "predeterminada",
    ) -> Path:
        ruta = cls.ruta_plantilla(
            tipo,
            nombre,
        )
        ruta.parent.mkdir(
            parents=True,
            exist_ok=True,
        )
        ruta.write_text(
            json.dumps(
                datos,
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf-8",
        )

        return ruta

    @classmethod
    def plantilla_defecto(cls, tipo: str) -> dict:
        return {
            "tipo": tipo,
            "nombre": "predeterminada",
            "pagina": {
                "ancho_mm": 80
                if tipo == "tirilla"
                else 215,
                "margen_mm": 10,
            },
            "estilo": {
                "color_primario": "#1b4f8a",
                "fuente": "Arial",
            },
            "bloques": [
                {"tipo": "logo", "x": 0, "y": 0},
                {"tipo": "empresa", "x": 0, "y": 20},
                {"tipo": "cliente", "x": 0, "y": 60},
                {"tipo": "detalle", "x": 0, "y": 120},
                {"tipo": "totales", "x": 0, "y": 400},
                {"tipo": "qr", "x": 0, "y": 480},
                {"tipo": "pie", "x": 0, "y": 520},
            ],
        }

    @classmethod
    def renderizar_html(
        cls,
        tipo: str,
        contexto: dict,
        nombre: str = "predeterminada",
    ) -> str:
        plantilla = cls.cargar(
            tipo,
            nombre,
        )
        color = plantilla["estilo"]["color_primario"]

        bloques_html = []

        for bloque in plantilla.get(
            "bloques",
            [],
        ):
            tipo_bloque = bloque.get(
                "tipo",
                "",
            )

            if tipo_bloque == "logo" and contexto.get(
                "logo",
            ):
                bloques_html.append(
                    f"<img src='{contexto['logo']}' "
                    f"style='max-height:70px'/>"
                )

            elif tipo_bloque == "empresa":
                bloques_html.append(
                    f"<h2 style='color:{color}'>"
                    f"{contexto.get('empresa_nombre','')}"
                    f"</h2>"
                )

            elif tipo_bloque == "detalle":
                bloques_html.append(
                    contexto.get(
                        "tabla_detalle",
                        "",
                    )
                )

            elif tipo_bloque == "totales":
                bloques_html.append(
                    contexto.get(
                        "totales_html",
                        "",
                    )
                )

            elif tipo_bloque == "qr" and contexto.get(
                "qr",
            ):
                bloques_html.append(
                    f"<img src='{contexto['qr']}' "
                    f"width='120'/>"
                )

        return (
            "<html><body style='font-family:Arial'>"
            + "".join(bloques_html)
            + "</body></html>"
        )
