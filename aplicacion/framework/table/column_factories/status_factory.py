from __future__ import annotations

from PySide6.QtWidgets import QTableWidgetItem

from .text_factory import TextColumnFactory


COLORES_ESTADO = {
    "borrador": ("#F1F5F9", "#475569"),
    "pendiente": ("#FFFAEB", "#B54708"),
    "en_preparacion": ("#EAF0F7", "#1E3A5F"),
    "aprobada": ("#EAF0F7", "#1E3A5F"),
    "emitida": ("#ECFDF3", "#067647"),
    "conciliado": ("#ECFDF3", "#067647"),
    "pagada": ("#ECFDF3", "#067647"),
    "parcial": ("#EAF0F7", "#1E3A5F"),
    "anulada": ("#FEF3F2", "#B42318"),
    "rechazada": ("#FEF3F2", "#B42318"),
    "vencida": ("#FEF3F2", "#B42318"),
    "activo": ("#ECFDF3", "#067647"),
    "inactivo": ("#F8FAFC", "#475569"),
    "true": ("#ECFDF3", "#067647"),
    "false": ("#F8FAFC", "#475569"),
    "prospeccion": ("#FFFAEB", "#B54708"),
    "calificacion": ("#EAF0F7", "#1E3A5F"),
    "propuesta": ("#EAF0F7", "#1E3A5F"),
    "negociacion": ("#FFFAEB", "#B54708"),
    "ganada": ("#ECFDF3", "#067647"),
    "perdida": ("#FEF3F2", "#B42318"),
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
                ("#E2E8F0", "#1E293B"),
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
