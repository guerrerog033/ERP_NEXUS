from __future__ import annotations

from datetime import date
from pathlib import Path

from aplicacion.integraciones.dian.firmador_xml import (
    FirmadorXml,
)
from aplicacion.nucleo.configuracion import Configuracion


class ValidadorGoLiveDian:

    _PREFIJOS_HABILITACION = (
        "SETP",
        "SETT",
        "SETPRUEBAS",
    )

    @classmethod
    def _ambiente_normalizado(
        cls,
        valor: str | None,
    ) -> str:

        ambiente = str(
            valor or "",
        ).strip().lower()

        if ambiente in (
            "produccion",
            "production",
            "prod",
        ):

            return "produccion"

        return "habilitacion"

    @classmethod
    def _texto(
        cls,
        seccion: str,
        clave: str,
        predeterminado=None,
    ):

        valor = Configuracion.obtener(
            seccion,
            clave,
        )

        if valor is None:

            return predeterminado

        return valor

    @classmethod
    def _agregar_si_vacio(
        cls,
        destino: list[str],
        condicion: bool,
        mensaje: str,
    ) -> None:

        if condicion:

            destino.append(
                mensaje,
            )

    @classmethod
    def _certificado_disponible(cls) -> bool:

        try:

            return (
                FirmadorXml._ruta_certificado()
                is not None
            )

        except OSError:

            return False

    @classmethod
    def _validar_resolucion(
        cls,
        bloqueantes: list[str],
        avisos: list[str],
    ) -> None:

        resolucion = str(
            cls._texto(
                "dian",
                "resolucion_numero",
                "",
            )
            or "",
        ).strip()

        cls._agregar_si_vacio(
            bloqueantes,
            not resolucion,
            "Configure dian.resolucion_numero.",
        )

        for clave, etiqueta in (
            (
                "resolucion_fecha_inicio",
                "dian.resolucion_fecha_inicio",
            ),
            (
                "resolucion_fecha_fin",
                "dian.resolucion_fecha_fin",
            ),
        ):

            valor = cls._texto(
                "dian",
                clave,
            )

            if not valor:

                bloqueantes.append(
                    f"Configure {etiqueta}.",
                )

                continue

            if clave == "resolucion_fecha_fin":

                try:

                    fin = date.fromisoformat(
                        str(
                            valor,
                        ),
                    )

                    if fin < date.today():

                        avisos.append(
                            "La resolución DIAN está vencida "
                            "(resolucion_fecha_fin).",
                        )

                except ValueError:

                    bloqueantes.append(
                        f"Fecha inválida en {etiqueta}.",
                    )

        for clave, etiqueta in (
            (
                "resolucion_desde",
                "dian.resolucion_desde",
            ),
            (
                "resolucion_hasta",
                "dian.resolucion_hasta",
            ),
        ):

            cls._agregar_si_vacio(
                bloqueantes,
                not str(
                    cls._texto(
                        "dian",
                        clave,
                        "",
                    )
                    or "",
                ).strip(),
                f"Configure {etiqueta}.",
            )

    @classmethod
    def _validar_empresa(
        cls,
        bloqueantes: list[str],
        avisos: list[str],
    ) -> None:

        nit = str(
            cls._texto(
                "empresa",
                "nit",
                "",
            )
            or "",
        ).strip()

        cls._agregar_si_vacio(
            bloqueantes,
            not nit,
            "Configure empresa.nit (debe coincidir con el certificado).",
        )

        for clave, etiqueta in (
            ("nombre", "empresa.nombre"),
            ("direccion", "empresa.direccion"),
            ("ciudad", "empresa.ciudad"),
        ):

            cls._agregar_si_vacio(
                avisos,
                not str(
                    cls._texto(
                        "empresa",
                        clave,
                        "",
                    )
                    or "",
                ).strip(),
                f"Complete {etiqueta} para el XML electrónico.",
            )

    @classmethod
    def verificar(
        cls,
        *,
        ambiente_objetivo: str = "produccion",
    ) -> dict:

        objetivo = cls._ambiente_normalizado(
            ambiente_objetivo,
        )

        bloqueantes: list[str] = []
        avisos: list[str] = []

        emision_habilitada = bool(
            cls._texto(
                "dian",
                "emision_habilitada",
                False,
            ),
        )

        cls._agregar_si_vacio(
            bloqueantes,
            not emision_habilitada,
            "Habilite dian.emision_habilitada.",
        )

        ambiente_actual = cls._ambiente_normalizado(
            cls._texto(
                "dian",
                "ambiente_emision",
                "habilitacion",
            ),
        )

        if ambiente_actual != objetivo:

            avisos.append(
                f"dian.ambiente_emision está en "
                f"'{ambiente_actual}' "
                f"(objetivo: '{objetivo}').",
            )

        cls._agregar_si_vacio(
            bloqueantes,
            not cls._certificado_disponible(),
            "Configure dian.certificado_ruta con un .p12/.pfx válido.",
        )

        cls._agregar_si_vacio(
            bloqueantes,
            not str(
                cls._texto(
                    "dian",
                    "certificado_clave",
                    "",
                )
                or "",
            ).strip(),
            "Configure dian.certificado_clave.",
        )

        prefijo = str(
            cls._texto(
                "dian",
                "prefijo_factura",
                "",
            )
            or "",
        ).strip().upper()

        cls._agregar_si_vacio(
            bloqueantes,
            not prefijo,
            "Configure dian.prefijo_factura.",
        )

        test_set_id = str(
            cls._texto(
                "dian",
                "test_set_id",
                "",
            )
            or "",
        ).strip()

        if objetivo == "produccion":

            if prefijo in cls._PREFIJOS_HABILITACION:

                bloqueantes.append(
                    "En producción no use prefijos de "
                    "habilitación (SETP/SETT). "
                    "Actualice dian.prefijo_factura.",
                )

            cls._agregar_si_vacio(
                bloqueantes,
                bool(
                    test_set_id,
                ),
                "Vacíe dian.test_set_id al pasar a producción.",
            )

        else:

            cls._agregar_si_vacio(
                avisos,
                not test_set_id,
                "En habilitación conviene definir dian.test_set_id.",
            )

            if (
                prefijo
                and prefijo
                not in cls._PREFIJOS_HABILITACION
            ):

                avisos.append(
                    "En habilitación DIAN suele usarse "
                    "prefijo SETP en dian.prefijo_factura.",
                )

        cls._validar_resolucion(
            bloqueantes,
            avisos,
        )
        cls._validar_empresa(
            bloqueantes,
            avisos,
        )

        carpeta_xml = str(
            cls._texto(
                "dian",
                "carpeta_xml_venta",
                "",
            )
            or "",
        ).strip()

        if carpeta_xml:

            try:

                Path(
                    carpeta_xml,
                ).mkdir(
                    parents=True,
                    exist_ok=True,
                )

            except OSError as error:

                bloqueantes.append(
                    "No se puede escribir en "
                    f"dian.carpeta_xml_venta: {error}",
                )

        else:

            avisos.append(
                "Defina dian.carpeta_xml_venta para "
                "conservar XML/ZIP emitidos.",
            )

        return {
            "ambiente_objetivo": objetivo,
            "ambiente_actual": ambiente_actual,
            "listo": not bloqueantes,
            "bloqueantes": bloqueantes,
            "avisos": avisos,
            "configuracion": {
                "emision_habilitada": emision_habilitada,
                "prefijo_factura": prefijo,
                "resolucion_numero": str(
                    cls._texto(
                        "dian",
                        "resolucion_numero",
                        "",
                    )
                    or "",
                ),
                "test_set_id": test_set_id,
                "certificado_configurado": (
                    cls._certificado_disponible()
                ),
            },
        }

    @classmethod
    def verificar_habilitacion(cls) -> dict:

        return cls.verificar(
            ambiente_objetivo="habilitacion",
        )

    @classmethod
    def verificar_produccion(cls) -> dict:

        return cls.verificar(
            ambiente_objetivo="produccion",
        )

    @classmethod
    def resumen_texto(
        cls,
        resultado: dict,
    ) -> str:

        lineas = [
            (
                f"Go-live DIAN "
                f"({resultado.get('ambiente_objetivo', '')})"
            ),
            (
                "Estado: "
                + (
                    "LISTO"
                    if resultado.get(
                        "listo",
                    )
                    else "PENDIENTE"
                )
            ),
        ]

        for etiqueta, clave in (
            ("Bloqueantes", "bloqueantes"),
            ("Avisos", "avisos"),
        ):

            items = resultado.get(
                clave,
                [],
            )

            if not items:

                continue

            lineas.append(
                f"{etiqueta}:",
            )

            lineas.extend(
                f"- {item}"
                for item in items
            )

        return "\n".join(
            lineas,
        )
