from __future__ import annotations

from pathlib import Path

from aplicacion.integraciones.correo.servicio_correo import (
    ServicioCorreo,
)
from aplicacion.nucleo.configuracion import Configuracion


class ServicioEnviosCorreo:
    """Envío de cotizaciones, facturas, estados de cuenta y recordatorios."""

    @classmethod
    def _habilitado(cls) -> bool:
        return bool(
            Configuracion.obtener(
                "correo",
                "smtp_habilitado",
                False,
            )
        )

    @classmethod
    def enviar_cotizacion(
        cls,
        *,
        destinatario: str,
        numero: str,
        ruta_pdf: str | Path,
    ) -> None:
        cls._enviar_documento(
            destinatario=destinatario,
            asunto=f"Cotización {numero}",
            cuerpo=(
                f"Adjuntamos la cotización {numero}. "
                "Quedamos atentos a su respuesta."
            ),
            adjuntos=[ruta_pdf],
        )

    @classmethod
    def enviar_factura(
        cls,
        *,
        destinatario: str,
        numero: str,
        ruta_pdf: str | Path,
        ruta_xml: str | Path | None = None,
    ) -> None:
        adjuntos = [ruta_pdf]

        if ruta_xml:
            adjuntos.append(ruta_xml)

        cls._enviar_documento(
            destinatario=destinatario,
            asunto=f"Factura {numero}",
            cuerpo=(
                f"Adjuntamos la factura {numero} "
                "y sus soportes electrónicos."
            ),
            adjuntos=adjuntos,
        )

    @classmethod
    def enviar_estado_cuenta(
        cls,
        *,
        destinatario: str,
        cliente: str,
        ruta_pdf: str | Path,
    ) -> None:
        cls._enviar_documento(
            destinatario=destinatario,
            asunto=f"Estado de cuenta — {cliente}",
            cuerpo=(
                "Adjuntamos su estado de cuenta "
                "actualizado."
            ),
            adjuntos=[ruta_pdf],
        )

    @classmethod
    def enviar_recordatorio_cartera(
        cls,
        *,
        destinatario: str,
        cliente: str,
        saldo: float,
        facturas: list[str],
    ) -> None:
        lista = ", ".join(facturas[:5])

        cls._enviar_documento(
            destinatario=destinatario,
            asunto=f"Recordatorio de pago — {cliente}",
            cuerpo=(
                f"Saldo pendiente: ${saldo:,.0f}. "
                f"Documentos: {lista}."
            ),
            adjuntos=[],
        )

    @classmethod
    def _enviar_documento(
        cls,
        *,
        destinatario: str,
        asunto: str,
        cuerpo: str,
        adjuntos: list,
    ) -> None:
        if not cls._habilitado():
            raise ValueError(
                "Active correo.smtp_habilitado.",
            )

        ServicioCorreo.enviar(
            destinatario=destinatario,
            asunto=asunto,
            cuerpo=cuerpo,
            adjuntos=adjuntos,
        )
