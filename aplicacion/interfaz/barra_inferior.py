from PySide6.QtCore import Signal, Qt
from PySide6.QtWidgets import (
    QWidget,
    QPushButton,
    QHBoxLayout,
    QFrame,
)

from aplicacion.framework.app_context import AppContext
from aplicacion.recursos.estilos.tema import habilitar_fondo_qss


class BarraInferior(QWidget):

    accion_rapida = Signal(
        str
    )

    def __init__(
        self,
    ):

        super().__init__()

        self.setObjectName(
            "BarraInferior"
        )

        habilitar_fondo_qss(
            self
        )

        self.setFixedHeight(
            52
        )

        layout = QHBoxLayout(
            self
        )

        layout.setContentsMargins(
            10,
            6,
            10,
            6,
        )

        layout.setSpacing(
            8
        )

        self.btn_inicio = self._crear_boton_rapido(
            "Inicio",
            "🏠",
            "Inicio",
            destacado=False,
        )

        self.btn_terceros = self._crear_boton_rapido(
            "Terceros",
            "👥",
            "Terceros",
            destacado=True,
        )

        self.btn_empresas = self._crear_boton_rapido(
            "Empresas",
            "🏢",
            "Empresas",
            destacado=False,
        )

        self.btn_config_dian = self._crear_boton_rapido(
            "DIAN",
            "🧾",
            "ConfiguracionDian",
            destacado=False,
        )

        separador = QFrame()

        separador.setFrameShape(
            QFrame.VLine
        )

        separador.setObjectName(
            "BarraInferiorSeparador"
        )

        layout.addWidget(
            self.btn_inicio
        )

        layout.addWidget(
            self.btn_terceros
        )

        layout.addWidget(
            self.btn_empresas
        )

        layout.addWidget(
            self.btn_config_dian
        )

        layout.addWidget(
            separador
        )

        layout.addStretch()

        self.btn_inicio.clicked.connect(
            lambda: self._ir_inicio()
        )

        self.btn_terceros.clicked.connect(
            lambda: self.accion_rapida.emit(
                "Clientes"
            )
        )

        self.btn_empresas.clicked.connect(
            lambda: self.accion_rapida.emit(
                "Empresas"
            )
        )

        self.btn_config_dian.clicked.connect(
            lambda: self.accion_rapida.emit(
                "ConfiguracionDian"
            )
        )

    def _crear_boton_rapido(
        self,
        texto: str,
        icono: str,
        modulo: str,
        destacado: bool,
    ) -> QPushButton:

        boton = QPushButton(
            f"{icono}  {texto}"
        )

        boton.setCursor(
            Qt.PointingHandCursor
        )

        if destacado:

            boton.setObjectName(
                "BotonRapidoDestacado"
            )

        else:

            boton.setObjectName(
                "BotonRapido"
            )

        boton.setProperty(
            "modulo",
            modulo,
        )

        return boton

    def _ir_inicio(
        self,
    ) -> None:

        if AppContext.area_trabajo is not None:

            AppContext.area_trabajo.mostrar_inicio()
