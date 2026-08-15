from __future__ import annotations

import re
import tempfile
from pathlib import Path
from urllib.parse import quote

from PySide6.QtCore import QUrl
from PySide6.QtGui import QDesktopServices
from PySide6.QtWidgets import (
    QInputDialog,
    QMessageBox,
    QWidget,
)

from aplicacion.integraciones.correo.servicio_envios import (
    ServicioEnviosCorreo,
)

from .documento_pdf import (
    DocumentoPdf,
)


def _sanitizar_telefono(
    telefono: str,
) -> str:

    digitos = re.sub(
        r"\D",
        "",
        str(
            telefono or "",
        ),
    )

    if len(
        digitos,
    ) == 10:

        digitos = f"57{digitos}"

    return digitos


def generar_pdf_temporal(
    documento: DocumentoPdf,
    *,
    formato_pagina: str = "carta",
) -> Path:

    ruta = Path(
        tempfile.gettempdir(),
    ) / documento.reporte.nombre_archivo_pdf()

    documento.exportar_pdf(
        ruta,
        formato_pagina=formato_pagina,
    )

    return ruta


def enviar_documento_correo(
    documento: DocumentoPdf,
    *,
    parent: QWidget | None = None,
    formato_pagina: str = "carta",
    destinatario: str | None = None,
) -> bool:

    reporte = documento.reporte

    correo = str(
        destinatario
        or reporte.correo_destinatario()
        or "",
    ).strip()

    if not correo:

        texto, aceptar = QInputDialog.getText(
            parent,
            "Enviar correo",
            "Correo del destinatario:",
        )

        if (
            not aceptar
            or not str(
                texto,
            ).strip()
        ):

            return False

        correo = str(
            texto,
        ).strip()

    try:

        ruta = generar_pdf_temporal(
            documento,
            formato_pagina=formato_pagina,
        )

    except Exception as error:

        if parent is not None:

            QMessageBox.warning(
                parent,
                "Correo",
                f"No se pudo generar el PDF:\n{error}",
            )

        return False

    asunto = reporte.asunto_correo()
    cuerpo = reporte.cuerpo_correo()

    try:

        if ServicioEnviosCorreo._habilitado():

            ServicioEnviosCorreo._enviar_documento(
                destinatario=correo,
                asunto=asunto,
                cuerpo=cuerpo,
                adjuntos=[
                    ruta,
                ],
            )

        else:

            url = (
                "mailto:"
                f"{quote(correo)}"
                f"?subject={quote(asunto)}"
                f"&body={quote(cuerpo)}"
            )

            if not QDesktopServices.openUrl(
                QUrl(
                    url,
                ),
            ):

                raise ValueError(
                    "No se pudo abrir el cliente de correo.",
                )

    except Exception as error:

        if parent is not None:

            QMessageBox.warning(
                parent,
                "Correo",
                str(
                    error,
                ),
            )

        return False

    if parent is not None:

        QMessageBox.information(
            parent,
            "Correo",
            f"Documento enviado a {correo}.",
        )

    return True


def enviar_documento_whatsapp(
    documento: DocumentoPdf,
    *,
    parent: QWidget | None = None,
    telefono: str | None = None,
) -> bool:

    reporte = documento.reporte

    mensaje = reporte.texto_whatsapp()

    numero = _sanitizar_telefono(
        telefono
        or reporte.telefono_destinatario()
        or "",
    )

    if numero:

        url = (
            "https://wa.me/"
            f"{numero}?text={quote(mensaje)}"
        )

    else:

        url = (
            "https://wa.me/?text="
            f"{quote(mensaje)}"
        )

    if not QDesktopServices.openUrl(
        QUrl(
            url,
        ),
    ):

        if parent is not None:

            QMessageBox.warning(
                parent,
                "WhatsApp",
                "No se pudo abrir WhatsApp.",
            )

        return False

    return True
