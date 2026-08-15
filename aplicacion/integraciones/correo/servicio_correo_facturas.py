from __future__ import annotations

import email
import imaplib
import tempfile
from email.header import decode_header
from pathlib import Path

from aplicacion.integraciones.dian.importador_xml import (
    parsear_factura_xml_texto,
)
from aplicacion.nucleo.configuracion import Configuracion

from aplicacion.modulos.compras.facturas.automatizacion import (
    ServicioAutomatizacionCompras,
)
from aplicacion.integraciones.dian.servicio_recepcion import (
    ServicioRecepcionCompras,
)


class ServicioCorreoFacturas:
    """Lee correo IMAP y procesa facturas electrónicas adjuntas."""

    @classmethod
    def _config(cls) -> dict:
        return dict(
            Configuracion.obtener(
                "correo",
                "facturas",
            )
            or {},
        )

    @classmethod
    def habilitado(cls) -> bool:
        return bool(
            cls._config().get(
                "habilitado",
                False,
            )
        )

    @classmethod
    def procesar_buzon(cls) -> dict:
        config = cls._config()

        if not cls.habilitado():
            return {
                "procesadas": 0,
                "errores": [
                    "Correo deshabilitado.",
                ],
            }

        servidor = config.get(
            "servidor_imap",
            "",
        )
        usuario = config.get(
            "usuario",
            "",
        )
        clave = config.get(
            "clave",
            "",
        )

        if not all(
            (
                servidor,
                usuario,
                clave,
            )
        ):
            return {
                "procesadas": 0,
                "errores": [
                    "Configure servidor IMAP.",
                ],
            }

        procesadas = 0
        errores: list[str] = []

        try:
            conexion = imaplib.IMAP4_SSL(
                servidor,
            )
            conexion.login(
                usuario,
                clave,
            )
            conexion.select(
                config.get(
                    "carpeta",
                    "INBOX",
                )
            )

            _, datos = conexion.search(
                None,
                "UNSEEN",
            )

            for num in datos[0].split():
                try:
                    _, mensaje_data = conexion.fetch(
                        num,
                        "(RFC822)",
                    )

                    mensaje = email.message_from_bytes(
                        mensaje_data[0][1],
                    )

                    if cls._procesar_mensaje(
                        mensaje,
                    ):
                        procesadas += 1

                    if config.get(
                        "marcar_leido",
                        True,
                    ):
                        conexion.store(
                            num,
                            "+FLAGS",
                            "\\Seen",
                        )

                except Exception as error:
                    errores.append(
                        str(error),
                    )

            conexion.logout()

        except Exception as error:
            errores.append(
                str(error),
            )

        return {
            "procesadas": procesadas,
            "errores": errores,
        }

    @classmethod
    def _procesar_mensaje(
        cls,
        mensaje,
    ) -> bool:
        for parte in mensaje.walk():
            if parte.get_content_disposition() != "attachment":
                continue

            nombre = cls._decodificar_nombre(
                parte.get_filename(),
            )

            if not nombre:
                continue

            extension = Path(
                nombre,
            ).suffix.lower()

            if extension not in (
                ".xml",
                ".zip",
            ):
                continue

            contenido = parte.get_payload(
                decode=True,
            )

            if not contenido:
                continue

            if extension == ".xml":
                return cls._procesar_xml(
                    contenido.decode(
                        "utf-8",
                        errors="ignore",
                    ),
                    nombre,
                )

        return False

    @classmethod
    def _procesar_xml(
        cls,
        contenido: str,
        nombre: str,
    ) -> bool:
        try:
            parseada = parsear_factura_xml_texto(
                contenido,
            )
        except Exception:
            return False

        if not parseada.cufe:
            return False

        try:
            factura = (
                ServicioRecepcionCompras
                .importar_desde_contenido_xml(
                    contenido,
                    nombre_archivo=nombre,
                )
            )
        except ValueError:
            return False

        ServicioAutomatizacionCompras.procesar_factura(
            factura.id,
        )

        return True

    @classmethod
    def _decodificar_nombre(
        cls,
        nombre,
    ) -> str:
        if not nombre:
            return ""

        partes = decode_header(nombre)
        texto = ""

        for fragmento, codificacion in partes:
            if isinstance(
                fragmento,
                bytes,
            ):
                texto += fragmento.decode(
                    codificacion or "utf-8",
                    errors="ignore",
                )
            else:
                texto += str(fragmento)

        return texto
