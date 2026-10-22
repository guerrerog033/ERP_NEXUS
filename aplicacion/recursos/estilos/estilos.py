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
            "#067647",
            "#067647",
            "#067647",
        )

    @staticmethod
    def boton_nuevo(widget):
        Estilos._boton(
            widget,
            Colores.INFORMACION,
            "#1E3A5F",
            "#1E3A5F",
        )

    @staticmethod
    def boton_editar(widget):
        Estilos._boton(
            widget,
            "#B54708",
            "#B54708",
            "#B54708",
        )

    @staticmethod
    def boton_eliminar(widget):
        Estilos._boton(
            widget,
            Colores.PELIGRO,
            "#B42318",
            "#B42318",
        )

    @staticmethod
    def boton_actualizar(widget):
        Estilos._boton(
            widget,
            "#1E3A5F",
            "#1E3A5F",
            "#1E3A5F",
        )

    @staticmethod
    def boton_buscar(widget):
        Estilos._boton(
            widget,
            "#1E3A5F",
            "#1E3A5F",
            "#1E3A5F",
        )

    @staticmethod
    def boton_cancelar(widget):
        Estilos._boton(
            widget,
            Colores.TEXTO_SECUNDARIO,
            "#475569",
            "#475569",
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
