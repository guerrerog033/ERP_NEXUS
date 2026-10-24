from __future__ import annotations

from PySide6.QtCore import QSize
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)


class ModuleShellPage(QWidget):
    """
    Contenedor con título para módulos abiertos en pestañas.
    Distinto de framework.base.page.Page (layout de formularios/páginas).

    El encabezado lleva el color del módulo (franja a la izquierda e
    ícono) y la ruta "Área › Pantalla", al estilo de los programas
    contables de escritorio.
    """

    def __init__(
        self,
        titulo: str = "",
        subtitulo: str = "",
    ):

        super().__init__()

        self.setObjectName("PaginaModulo")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 6)

        panel = QFrame()
        panel.setObjectName("PanelModulo")

        panel_layout = QVBoxLayout(panel)
        panel_layout.setContentsMargins(0, 0, 0, 0)
        panel_layout.setSpacing(0)

        self.encabezado = QFrame()
        self.encabezado.setObjectName("EncabezadoModulo")

        fila = QHBoxLayout(self.encabezado)
        fila.setContentsMargins(12, 6, 12, 6)
        fila.setSpacing(10)

        self.lbl_icono = QLabel()
        self.lbl_icono.setObjectName("EncabezadoModuloIcono")
        self.lbl_icono.setFixedSize(QSize(26, 26))
        self.lbl_icono.hide()

        textos = QVBoxLayout()
        textos.setSpacing(0)

        self.lbl_titulo = QLabel(titulo)
        self.lbl_subtitulo = QLabel(subtitulo)

        self.lbl_titulo.setObjectName("PaginaModuloTitulo")
        self.lbl_subtitulo.setObjectName("PaginaModuloSubtitulo")

        textos.addWidget(self.lbl_titulo)
        textos.addWidget(self.lbl_subtitulo)

        fila.addWidget(self.lbl_icono)
        fila.addLayout(textos, 1)

        panel_layout.addWidget(self.encabezado)

        self.layout_contenido = QVBoxLayout()
        self.layout_contenido.setContentsMargins(6, 4, 6, 4)

        panel_layout.addLayout(self.layout_contenido, 1)

        layout.addWidget(panel, 1)

    def set_modulo(
        self,
        modulo_id: str,
    ) -> None:
        """Aplica el color, el ícono y la ruta del área del módulo."""

        from aplicacion.framework.ui.colores_modulo import (
            area_modulo,
            color_modulo,
            nombre_area,
        )
        from aplicacion.framework.ui.iconos import icono_modulo

        color = color_modulo(modulo_id)
        area = area_modulo(modulo_id)

        self.encabezado.setStyleSheet(
            "QFrame#EncabezadoModulo {"
            f" border-left: 5px solid {color};"
            "}",
        )

        if area:

            self.lbl_icono.setPixmap(
                icono_modulo(area, color, 24).pixmap(24, 24),
            )

            self.lbl_icono.show()

        nombre = nombre_area(modulo_id)
        titulo = self.lbl_titulo.text()

        if nombre and nombre != titulo:

            self.lbl_subtitulo.setText(f"{nombre}  ›  {titulo}")

    def setContenido(
        self,
        widget,
    ) -> None:

        widget.setSizePolicy(
            QSizePolicy.Expanding,
            QSizePolicy.Expanding,
        )

        self.layout_contenido.addWidget(widget, 1)
