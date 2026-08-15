from __future__ import annotations

from PySide6.QtWidgets import QTableWidgetItem

from .text_factory import TextColumnFactory


COLORES_ESTADO = {
    "borrador": ("#FEF3C7", "#92400E"),
    "pendiente": ("#FEF3C7", "#92400E"),
    "en_preparacion": ("#DBEAFE", "#1E40AF"),
    "aprobada": ("#DBEAFE", "#1E40AF"),
    "emitida": ("#D1FAE5", "#065F46"),
    "conciliado": ("#D1FAE5", "#065F46"),
    "pagada": ("#D1FAE5", "#065F46"),
    "parcial": ("#DBEAFE", "#1E40AF"),
    "anulada": ("#FEE2E2", "#991B1B"),
    "rechazada": ("#FEE2E2", "#991B1B"),
    "vencida": ("#FEE2E2", "#991B1B"),
    "activo": ("#D1FAE5", "#065F46"),
    "inactivo": ("#F3F4F6", "#374151"),
    "true": ("#D1FAE5", "#065F46"),
    "false": ("#F3F4F6", "#374151"),
    "prospeccion": ("#FEF3C7", "#92400E"),
    "calificacion": ("#DBEAFE", "#1E40AF"),
    "propuesta": ("#E0E7FF", "#3730A3"),
    "negociacion": ("#FDE68A", "#92400E"),
    "ganada": ("#D1FAE5", "#065F46"),
    "perdida": ("#FEE2E2", "#991B1B"),
}


class StatusColumnFactory(
    TextColumnFactory,
):

    def badge_info(
        self,
        valor,
        columna,
    ) -> dict | None:

        texto = self.formatear_valor(
            valor,
            columna,
        )

        if not texto:

            return None

        clave = str(
            valor or "",
        ).strip().lower()

        mapa = columna.meta(
            "colores",
            COLORES_ESTADO,
        )

        fondo, texto_color = mapa.get(
            clave,
            mapa.get(
                texto.lower(),
                ("#E5E7EB", "#111827"),
            ),
        )

        return {
            "texto": texto,
            "fondo": fondo,
            "texto_color": texto_color,
        }

    def     formatear_valor(
        self,
        valor,
        columna,
    ) -> str:

        if isinstance(
            valor,
            bool,
        ):

            etiquetas = columna.meta(
                "etiquetas_bool",
                {
                    True: "Sí",
                    False: "No",
                },
            )

            return etiquetas.get(
                valor,
                str(
                    valor,
                ),
            )

        if valor is None:

            return ""

        texto = str(
            valor,
        ).replace(
            "_",
            " ",
        )

        return texto.title()

    def crear_item(
        self,
        valor,
        columna,
    ) -> QTableWidgetItem:

        item = super().crear_item(
            self.formatear_valor(
                valor,
                columna,
            ),
            columna,
        )

        return item
