from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QSizePolicy,
    QTabBar,
    QTabWidget,
)
from aplicacion.interfaz.inicio import Inicio


class AreaTrabajo(QTabWidget):

    def __init__(
        self,
    ):

        super().__init__()

        self.setObjectName(
            "AreaTrabajo",
        )

        self.setDocumentMode(
            True,
        )

        self.setMovable(
            True,
        )

        self.setTabsClosable(
            True,
        )

        barra_pestanas = self.tabBar()

        barra_pestanas.setExpanding(
            False,
        )

        barra_pestanas.setUsesScrollButtons(
            True,
        )

        self.tabCloseRequested.connect(
            self.cerrar_pestana,
        )

        self.inicio = Inicio()

        self.addTab(
            self.inicio,
            "Inicio",
        )

        self.tabBar().setTabVisible(
            0,
            False,
        )

        self._actualizar_barra_pestanas()

        self.setCurrentIndex(
            0,
        )

    def _actualizar_barra_pestanas(
        self,
    ) -> None:

        if self.count() <= 1:

            self.tabBar().setVisible(
                False,
            )

            return

        self.tabBar().setTabVisible(
            0,
            False,
        )

        self.tabBar().setVisible(
            True,
        )

    def abrir(
        self,
        widget,
        titulo,
    ):

        for indice in range(
            self.count(),
        ):

            if self.widget(
                indice,
            ) == widget:

                widget.setAttribute(
                    Qt.WA_DontShowOnScreen,
                    False,
                )

                widget.show()

                self.setCurrentIndex(
                    indice,
                )

                self._actualizar_barra_pestanas()

                return indice

        if widget.parent() is None:

            widget.setParent(
                self,
            )

        widget.setAttribute(
            Qt.WA_DontShowOnScreen,
            True,
        )

        if widget.isWindow():

            widget.hide()

        widget.setSizePolicy(
            QSizePolicy.Expanding,
            QSizePolicy.Expanding,
        )

        indice = self.addTab(
            widget,
            titulo,
        )

        widget.setAttribute(
            Qt.WA_DontShowOnScreen,
            False,
        )

        widget.show()

        self.setCurrentIndex(
            indice,
        )

        self._actualizar_barra_pestanas()

        return indice

    def indice_widget(
        self,
        widget,
    ):

        for indice in range(
            self.count(),
        ):

            if self.widget(
                indice,
            ) == widget:

                return indice

        return -1

    def cerrar_pestana(
        self,
        indice,
    ):

        if indice == 0:

            return

        widget = self.widget(
            indice,
        )

        self.removeTab(
            indice,
        )

        if widget is not None:

            widget.deleteLater()

        self._actualizar_barra_pestanas()

    def cerrar_widget(
        self,
        widget,
    ):

        indice = self.indice_widget(
            widget,
        )

        if indice > 0:

            self.cerrar_pestana(
                indice,
            )

    def cerrar_actual(
        self,
    ):

        indice = self.currentIndex()

        if indice > 0:

            self.cerrar_pestana(
                indice,
            )

    def mostrar_inicio(
        self,
    ):

        self.setCurrentIndex(
            0,
        )

        self.inicio.actualizar()
