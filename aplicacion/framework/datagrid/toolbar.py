from PySide6.QtCore import Signal, Qt
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLineEdit,
    QMenu,
    QToolButton,
    QWidget,
)

from aplicacion.recursos.estilos.estilos import Estilos
from aplicacion.recursos.ui.botones import Botones


class MaestroToolbar(QWidget):
    """
    Toolbar unificada del maestro: CRUD + Más + búsqueda.
    """

    buscar = Signal(str)
    actualizar = Signal()
    excel = Signal()
    pdf = Signal()
    imprimir = Signal()

    def __init__(
        self,
    ):
        super().__init__()

        self.setObjectName(
            "DataGridToolbar",
        )

        self._crear_interfaz()

    def _crear_interfaz(
        self,
    ) -> None:
        layout = QHBoxLayout(
            self,
        )

        layout.setContentsMargins(
            4,
            4,
            4,
            4,
        )

        layout.setSpacing(
            8,
        )

        self.btn_nuevo = Botones.nuevo()
        self.btn_editar = Botones.editar()
        self.btn_consultar = Botones.secundario(
            "Consultar",
        )
        self.btn_eliminar = Botones.eliminar()

        for boton in (
            self.btn_nuevo,
            self.btn_editar,
            self.btn_consultar,
            self.btn_eliminar,
        ):
            boton.setMinimumHeight(
                34,
            )
            boton.setMinimumWidth(
                96,
            )
            layout.addWidget(
                boton,
            )

        self.btn_mas = QToolButton()
        self.btn_mas.setObjectName(
            "MaestroToolbarMas",
        )
        self.btn_mas.setText(
            "Más",
        )
        self.btn_mas.setPopupMode(
            QToolButton.InstantPopup,
        )
        self.btn_mas.setToolButtonStyle(
            Qt.ToolButtonTextBesideIcon,
        )
        self.btn_mas.setMinimumHeight(
            34,
        )

        menu = QMenu(
            self,
        )

        self.accion_actualizar = menu.addAction(
            "Actualizar",
        )
        self.accion_excel = menu.addAction(
            "Exportar Excel",
        )
        self.accion_pdf = menu.addAction(
            "Exportar PDF",
        )
        self.accion_imprimir = menu.addAction(
            "Imprimir",
        )

        self.accion_actualizar.triggered.connect(
            self.actualizar.emit,
        )
        self.accion_excel.triggered.connect(
            self.excel.emit,
        )
        self.accion_pdf.triggered.connect(
            self.pdf.emit,
        )
        self.accion_imprimir.triggered.connect(
            self.imprimir.emit,
        )

        self.btn_mas.setMenu(
            menu,
        )

        layout.addWidget(
            self.btn_mas,
        )

        layout.addStretch(
            1,
        )

        self.txt_buscar = QLineEdit()
        self.txt_buscar.setPlaceholderText(
            "Buscar...",
        )
        self.txt_buscar.setMinimumHeight(
            38,
        )
        self.txt_buscar.setMinimumWidth(
            220,
        )

        Estilos.line_edit(
            self.txt_buscar,
        )

        self.txt_buscar.textChanged.connect(
            self.buscar.emit,
        )

        layout.addWidget(
            self.txt_buscar,
            1,
        )

        self.btn_actualizar = self.accion_actualizar
        self.btn_excel = self.accion_excel
        self.btn_pdf = self.accion_pdf
        self.btn_imprimir = self.accion_imprimir


Toolbar = MaestroToolbar
