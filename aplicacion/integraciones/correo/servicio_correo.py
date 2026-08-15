from __future__ import annotations

import email
import imaplib
import smtplib
import ssl
from dataclasses import dataclass, field
from email.header import decode_header
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path

from aplicacion.nucleo.configuracion import Configuracion


PRESETS_CORREO = {
    "gmail": {
        "imap": "imap.gmail.com",
        "smtp": "smtp.gmail.com",
        "puerto_imap": 993,
        "puerto_smtp": 587,
    },
    "google_workspace": {
        "imap": "imap.gmail.com",
        "smtp": "smtp.gmail.com",
        "puerto_imap": 993,
        "puerto_smtp": 587,
    },
    "outlook": {
        "imap": "outlook.office365.com",
        "smtp": "smtp.office365.com",
        "puerto_imap": 993,
        "puerto_smtp": 587,
    },
    "microsoft365": {
        "imap": "outlook.office365.com",
        "smtp": "smtp.office365.com",
        "puerto_imap": 993,
        "puerto_smtp": 587,
    },
}


@dataclass
class ResultadoCorreo:
    procesados: int = 0
    errores: int = 0
    movidos: int = 0
    mensajes: list[str] = field(
        default_factory=list,
    )


class ServicioCorreo:
    """IMAP/SMTP unificado para Gmail, Outlook, M365, Workspace y corporativo."""

    @classmethod
    def _config(cls) -> dict:
        return dict(
            Configuracion.obtener(
                "correo",
            )
            or {},
        )

    @classmethod
    def preset(cls, nombre: str) -> dict:
        return dict(
            PRESETS_CORREO.get(
                str(nombre or "").lower(),
                {},
            )
        )

    @classmethod
    def _resolver_servidores(cls) -> dict:
        config = cls._config()
        preset = cls.preset(
            config.get(
                "proveedor",
                "",
            )
        )

        return {
            "imap": config.get(
                "servidor_imap",
            )
            or preset.get(
                "imap",
                "",
            ),
            "smtp": config.get(
                "servidor_smtp",
            )
            or preset.get(
                "smtp",
                "",
            ),
            "puerto_imap": int(
                config.get(
                    "puerto_imap",
                    preset.get(
                        "puerto_imap",
                        993,
                    ),
                )
            ),
            "puerto_smtp": int(
                config.get(
                    "puerto_smtp",
                    preset.get(
                        "puerto_smtp",
                        587,
                    ),
                )
            ),
            "usuario": config.get(
                "usuario",
                "",
            ),
            "clave": config.get(
                "clave",
                "",
            ),
            "carpeta_entrada": config.get(
                "carpeta_entrada",
                "INBOX",
            ),
            "carpeta_procesados": config.get(
                "carpeta_procesados",
                "Procesados",
            ),
            "carpeta_errores": config.get(
                "carpeta_errores",
                "Errores",
            ),
        }

    @classmethod
    def conectar_imap(cls):
        srv = cls._resolver_servidores()

        if not all(
            (
                srv["imap"],
                srv["usuario"],
                srv["clave"],
            )
        ):
            raise ValueError(
                "Configure correo.imap/smtp y credenciales.",
            )

        conexion = imaplib.IMAP4_SSL(
            srv["imap"],
            srv["puerto_imap"],
        )
        conexion.login(
            srv["usuario"],
            srv["clave"],
        )

        return conexion, srv

    @classmethod
    def _decodificar_nombre(cls, nombre) -> str:
        if not nombre:
            return ""

        partes = decode_header(nombre)
        texto = ""

        for fragmento, codificacion in partes:
            if isinstance(fragmento, bytes):
                texto += fragmento.decode(
                    codificacion or "utf-8",
                    errors="ignore",
                )
            else:
                texto += str(fragmento)

        return texto

    @classmethod
    def listar_adjuntos(
        cls,
        mensaje,
    ) -> list[tuple[str, bytes]]:
        adjuntos: list[tuple[str, bytes]] = []

        for parte in mensaje.walk():
            if parte.get_content_disposition() != "attachment":
                continue

            nombre = cls._decodificar_nombre(
                parte.get_filename(),
            )
            contenido = parte.get_payload(
                decode=True,
            )

            if contenido:
                adjuntos.append(
                    (
                        nombre,
                        contenido,
                    )
                )

        return adjuntos

    @classmethod
    def _asegurar_carpeta(
        cls,
        conexion,
        nombre: str,
    ) -> None:
        try:
            conexion.create(
                nombre,
            )
        except imaplib.IMAP4.error:
            pass

    @classmethod
    def mover_mensaje(
        cls,
        conexion,
        uid: bytes,
        carpeta_destino: str,
    ) -> None:
        cls._asegurar_carpeta(
            conexion,
            carpeta_destino,
        )
        conexion.uid(
            "COPY",
            uid,
            carpeta_destino,
        )
        conexion.uid(
            "STORE",
            uid,
            "+FLAGS",
            "(\\Deleted)",
        )
        conexion.expunge()

    @classmethod
    def marcar_error(
        cls,
        conexion,
        uid: bytes,
        srv: dict,
    ) -> None:
        cls.mover_mensaje(
            conexion,
            uid,
            srv["carpeta_errores"],
        )

    @classmethod
    def marcar_procesado(
        cls,
        conexion,
        uid: bytes,
        srv: dict,
    ) -> None:
        cls.mover_mensaje(
            conexion,
            uid,
            srv["carpeta_procesados"],
        )

    @classmethod
    def procesar_carpeta(
        cls,
        *,
        callback,
        solo_no_leidos: bool = True,
    ) -> ResultadoCorreo:
        resultado = ResultadoCorreo()
        conexion, srv = cls.conectar_imap()

        try:
            conexion.select(
                srv["carpeta_entrada"],
            )

            criterio = (
                "UNSEEN"
                if solo_no_leidos
                else "ALL"
            )

            _, datos = conexion.uid(
                "SEARCH",
                None,
                criterio,
            )

            uids = datos[0].split()

            for uid in uids:
                try:
                    _, mensaje_data = conexion.uid(
                        "FETCH",
                        uid,
                        "(RFC822)",
                    )

                    mensaje = email.message_from_bytes(
                        mensaje_data[0][1],
                    )

                    exito = callback(
                        mensaje,
                        cls.listar_adjuntos(
                            mensaje,
                        ),
                    )

                    if exito:
                        cls.marcar_procesado(
                            conexion,
                            uid,
                            srv,
                        )
                        resultado.procesados += 1
                        resultado.movidos += 1
                    else:
                        cls.marcar_error(
                            conexion,
                            uid,
                            srv,
                        )
                        resultado.errores += 1

                except Exception as error:
                    resultado.errores += 1
                    resultado.mensajes.append(
                        str(error),
                    )

                    try:
                        cls.marcar_error(
                            conexion,
                            uid,
                            srv,
                        )
                    except Exception:
                        pass

        finally:
            try:
                conexion.logout()
            except Exception:
                pass

        return resultado

    @classmethod
    def enviar(
        cls,
        *,
        destinatario: str,
        asunto: str,
        cuerpo: str,
        adjuntos: list[str | Path] | None = None,
        html: bool = False,
    ) -> None:
        srv = cls._resolver_servidores()

        if not srv["smtp"]:
            raise ValueError(
                "Configure servidor SMTP.",
            )

        mensaje = MIMEMultipart()
        mensaje["From"] = srv["usuario"]
        mensaje["To"] = destinatario
        mensaje["Subject"] = asunto

        tipo = "html" if html else "plain"
        mensaje.attach(
            MIMEText(
                cuerpo,
                tipo,
                "utf-8",
            )
        )

        for ruta in adjuntos or []:
            archivo = Path(ruta)

            if not archivo.exists():
                continue

            parte = MIMEApplication(
                archivo.read_bytes(),
            )
            parte.add_header(
                "Content-Disposition",
                "attachment",
                filename=archivo.name,
            )
            mensaje.attach(parte)

        contexto = ssl.create_default_context()

        with smtplib.SMTP(
            srv["smtp"],
            srv["puerto_smtp"],
        ) as servidor:
            servidor.starttls(
                context=contexto,
            )
            servidor.login(
                srv["usuario"],
                srv["clave"],
            )
            servidor.send_message(
                mensaje,
            )

    @classmethod
    def enviar_respuesta_automatica(
        cls,
        destinatario: str,
        *,
        tipo: str = "recibido",
    ) -> None:
        plantillas = {
            "recibido": (
                "Hemos recibido su mensaje y lo "
                "procesaremos en breve.",
            ),
            "factura_procesada": (
                "Su factura fue registrada "
                "correctamente en nuestro ERP.",
            ),
            "error": (
                "No pudimos procesar su adjunto. "
                "Por favor envíe el XML UBL válido.",
            ),
        }

        cls.enviar(
            destinatario=destinatario,
            asunto="Confirmación ERP NEXUS",
            cuerpo=plantillas.get(
                tipo,
                plantillas["recibido"],
            ),
        )
