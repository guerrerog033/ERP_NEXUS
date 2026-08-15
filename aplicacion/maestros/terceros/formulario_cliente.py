from __future__ import annotations

from PySide6.QtWidgets import (
    QHBoxLayout,
    QPushButton,
)

from aplicacion.maestros.terceros.formulario import (
    TerceroFormulario,
)
from aplicacion.modulos.cartera.ui_comercial import (
    cartera_desde_tercero,
    estado_cuenta_desde_tercero,
)


class ClienteFormulario(
    TerceroFormulario,
):

    def _crear_botones(
        self,
    ) -> None:

        super()._crear_botones()

        if (
            not self.es_edicion
            or not self.id_registro
        ):

            return

        layout = QHBoxLayout()

        btn_cartera = QPushButton(
            "Cartera cliente",
        )
        btn_cartera.clicked.connect(
            self._ver_cartera_cliente,
        )

        btn_estado = QPushButton(
            "Estado de cuenta",
        )
        btn_estado.clicked.connect(
            self._ver_estado_cuenta_cliente,
        )

        layout.addWidget(
            btn_cartera,
        )
        layout.addWidget(
            btn_estado,
        )
        layout.addStretch()

        indice = max(
            0,
            self.card.contenido.count()
            - 1,
        )

        self.card.contenido.insertLayout(
            indice,
            layout,
        )

    def _nombre_cliente_actual(
        self,
    ) -> str:

        if self.engine is None:

            return ""

        ctx = self.engine.context

        for campo in (
            "razon_social",
            "nombre_comercial",
            "primer_nombre",
        ):

            valor = (
                ctx.valor(
                    campo,
                )
                or ""
            ).strip()

            if valor:

                return valor

        return ""

    def _ver_cartera_cliente(
        self,
    ) -> None:

        cartera_desde_tercero(
            self,
            self.id_registro,
            nombre=self._nombre_cliente_actual(),
        )

    def _ver_estado_cuenta_cliente(
        self,
    ) -> None:

        estado_cuenta_desde_tercero(
            self,
            self.id_registro,
            nombre=self._nombre_cliente_actual(),
        )
