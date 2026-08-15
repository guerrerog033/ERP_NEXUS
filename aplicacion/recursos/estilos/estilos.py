from aplicacion.recursos.estilos.colores import Colores
from aplicacion.recursos.estilos import dimensiones as dim


class Estilos:

    # =====================================================
    # Etiquetas
    # =====================================================

    @staticmethod
    def titulo(widget):
        widget.setStyleSheet(f"""
            QLabel {{
                color:{Colores.PRIMARIO};
                font-size:24px;
                font-weight:700;
                padding:{dim.ESPACIADO_4}px;
            }}
        """)

    @staticmethod
    def subtitulo(widget):
        widget.setStyleSheet(f"""
            QLabel {{
                color:{Colores.TEXTO_SECUNDARIO};
                font-size:13px;
            }}
        """)

    # =====================================================
    # Método interno
    # =====================================================

    @staticmethod
    def _boton(
        widget,
        fondo,
        hover,
        pressed,
        texto=Colores.SUPERFICIE,
        borde="none",
    ):
        widget.setMinimumHeight(dim.CONTROL_MD + 2)

        widget.setStyleSheet(f"""
            QPushButton {{
                background:{fondo};
                color:{texto};
                border:{borde};
                border-radius:{dim.RADIO_GRANDE}px;
                padding:{dim.ESPACIADO_8}px {dim.ESPACIADO_16}px;
                font-size:13px;
                font-weight:600;
            }}
            QPushButton:hover {{
                background:{hover};
            }}
            QPushButton:pressed {{
                background:{pressed};
            }}
            QPushButton:disabled {{
                background:{Colores.TEXTO_DESHABILITADO};
                color:{Colores.SUPERFICIE};
            }}
        """)

    # =====================================================
    # Botones
    # =====================================================

    @staticmethod
    def boton_guardar(widget):
        Estilos._boton(
            widget,
            "#16A34A",
            "#15803D",
            "#166534",
        )

    @staticmethod
    def boton_nuevo(widget):
        Estilos._boton(
            widget,
            Colores.INFORMACION,
            "#1D4ED8",
            "#1E40AF",
        )

    @staticmethod
    def boton_editar(widget):
        Estilos._boton(
            widget,
            "#F59E0B",
            "#D97706",
            "#B45309",
        )

    @staticmethod
    def boton_eliminar(widget):
        Estilos._boton(
            widget,
            Colores.PELIGRO,
            "#B91C1C",
            "#991B1B",
        )

    @staticmethod
    def boton_actualizar(widget):
        Estilos._boton(
            widget,
            "#0891B2",
            "#0E7490",
            "#155E75",
        )

    @staticmethod
    def boton_buscar(widget):
        Estilos._boton(
            widget,
            "#4F46E5",
            "#4338CA",
            "#3730A3",
        )

    @staticmethod
    def boton_cancelar(widget):
        Estilos._boton(
            widget,
            Colores.TEXTO_SECUNDARIO,
            "#4B5563",
            "#374151",
        )

    @staticmethod
    def boton_primario(widget):
        Estilos.boton_nuevo(widget)

    @staticmethod
    def boton_secundario(widget):
        Estilos.boton_cancelar(widget)

    # =====================================================
    # Controles
    # =====================================================

    @staticmethod
    def line_edit(widget):
        widget.setMinimumHeight(dim.CONTROL_SM + 6)

        widget.setStyleSheet(f"""
            QLineEdit {{
                padding:{dim.ESPACIADO_8}px;
                border:1px solid {Colores.TEXTO_DESHABILITADO};
                border-radius:{dim.RADIO_GRANDE}px;
                background:{Colores.SUPERFICIE};
            }}
            QLineEdit:hover {{
                border:1px solid {Colores.TEXTO_SECUNDARIO};
            }}
            QLineEdit:focus {{
                border:2px solid {Colores.BORDE_FOCO};
            }}
        """)

    @staticmethod
    def combo(widget):
        widget.setMinimumHeight(dim.CONTROL_SM + 6)

        widget.setStyleSheet(f"""
            QComboBox {{
                padding:{dim.ESPACIADO_8}px;
                border:1px solid {Colores.TEXTO_DESHABILITADO};
                border-radius:{dim.RADIO_GRANDE}px;
                background:{Colores.SUPERFICIE};
            }}
            QComboBox:hover {{
                border:1px solid {Colores.TEXTO_SECUNDARIO};
            }}
            QComboBox:focus {{
                border:2px solid {Colores.BORDE_FOCO};
            }}
        """)

    @staticmethod
    def checkbox(widget):
        widget.setStyleSheet(f"""
            QCheckBox {{
                spacing:{dim.ESPACIADO_8}px;
                font-size:13px;
            }}
            QCheckBox::indicator {{
                width:18px;
                height:18px;
                border:1px solid {Colores.TEXTO_SECUNDARIO};
                border-radius:{dim.RADIO_PEQUEÑO}px;
                background:{Colores.SUPERFICIE};
            }}
            QCheckBox::indicator:hover {{
                border:2px solid {Colores.BORDE_FOCO};
            }}
            QCheckBox::indicator:checked {{
                background:{Colores.BORDE_FOCO};
                border:1px solid {Colores.BORDE_FOCO};
            }}
        """)
