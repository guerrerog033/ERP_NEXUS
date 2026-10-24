"""
Atajos de teclado del ERP.

Cada pantalla registra los suyos con ``registrar_atajos``; quedan
activos solo mientras esa pantalla (pestaña) tiene el foco, así una
misma tecla puede hacer cosas distintas en una lista y en un documento.

Resumen (también se muestra con F1):

  General
    F1 ................ Ver atajos
    Ctrl+K ............ Buscar módulo
    Ctrl+W ............ Cerrar pestaña
    Ctrl+Tab .......... Pestaña siguiente (Ctrl+Shift+Tab: anterior)

  Listas
    Ctrl+N / Insert ... Nuevo
    Enter / F2 ........ Editar el registro seleccionado
    Supr .............. Eliminar el registro seleccionado
    Ctrl+F / F3 ....... Ir al buscador
    F5 ................ Actualizar

  Formularios y documentos
    Tab / Enter ....... Siguiente campo (Shift+Tab: anterior)
    Ctrl+S / F10 ...... Guardar
    F3 ................ Buscar cliente / proveedor
    F4 ................ Buscar producto en la línea actual
    Ctrl+L ............ Agregar línea
    Ctrl+Supr ......... Quitar la línea actual
    Ctrl+P ............ Imprimir
    Ctrl+I ............ Importar XML (factura de compra)
"""

from __future__ import annotations

from PySide6.QtCore import QEvent, QObject, Qt
from PySide6.QtGui import QKeySequence, QShortcut
from PySide6.QtWidgets import (
    QAbstractButton,
    QAbstractSpinBox,
    QApplication,
    QComboBox,
    QLineEdit,
    QMessageBox,
    QPlainTextEdit,
    QTextEdit,
    QWidget,
)


TEXTO_AYUDA = __doc__.split(
    "Resumen (también se muestra con F1):",
)[1].strip()


def registrar_atajos(
    widget: QWidget,
    atajos,
    *,
    contexto=Qt.ShortcutContext.WidgetWithChildrenShortcut,
) -> list[QShortcut]:
    """
    ``atajos``: iterable de (secuencia o lista de secuencias, función).
    """

    creados: list[QShortcut] = []

    for secuencias, accion in atajos:

        if isinstance(
            secuencias,
            (
                str,
                QKeySequence,
                QKeySequence.StandardKey,
            ),
        ):

            secuencias = (
                secuencias,
            )

        for secuencia in secuencias:

            atajo = QShortcut(
                QKeySequence(
                    secuencia,
                ),
                widget,
            )

            atajo.setContext(
                contexto,
            )

            atajo.activated.connect(
                accion,
            )

            creados.append(
                atajo,
            )

    return creados


def pulsar(
    boton,
) -> None:
    """Hace clic en el botón solo si está visible y habilitado."""

    if (
        isinstance(
            boton,
            QAbstractButton,
        )
        and boton.isVisible()
        and boton.isEnabled()
    ):

        boton.click()


def mostrar_ayuda(
    parent=None,
) -> None:

    QMessageBox.information(
        parent,
        "Atajos de teclado",
        TEXTO_AYUDA,
    )


class FiltroTeclado(QObject):
    """
    Ajustes de teclado para toda la aplicación:

    - En los cuadros de texto de varias líneas (observaciones) la
      tecla Tab pasa al siguiente campo en vez de escribir un
      tabulador, para poder recorrer cualquier pantalla con Tab.
    - En los formularios, Enter en un campo de una línea (texto,
      combo, fecha, número) también pasa al siguiente campo, salvo
      que la pantalla ya maneje Enter por su cuenta.
    """

    def eventFilter(
        self,
        objeto,
        evento,
    ):

        tipo = evento.type()

        if tipo == QEvent.Type.FocusIn and isinstance(
            objeto,
            (
                QTextEdit,
                QPlainTextEdit,
            ),
        ):

            if not objeto.tabChangesFocus():

                objeto.setTabChangesFocus(
                    True,
                )

        if (
            tipo == QEvent.Type.KeyPress
            and evento.key()
            in (
                Qt.Key.Key_Return,
                Qt.Key.Key_Enter,
            )
            and not evento.modifiers()
            & (
                Qt.KeyboardModifier.ControlModifier
                | Qt.KeyboardModifier.AltModifier
                | Qt.KeyboardModifier.ShiftModifier
            )
            and _enter_avanza(
                objeto,
            )
        ):

            objeto.focusNextChild()

            return True

        return super().eventFilter(
            objeto,
            evento,
        )


def _enter_avanza(
    objeto,
) -> bool:

    if not isinstance(
        objeto,
        (
            QLineEdit,
            QComboBox,
            QAbstractSpinBox,
        ),
    ):

        return False

    # Un combo con la lista abierta usa Enter para elegir.
    if isinstance(
        objeto,
        QComboBox,
    ) and objeto.view().isVisible():

        return False

    # El editor interno de un combo editable o de un spinbox le
    # pertenece a su contenedor.
    padre = objeto.parentWidget()

    if isinstance(
        objeto,
        QLineEdit,
    ) and isinstance(
        padre,
        (
            QComboBox,
            QAbstractSpinBox,
        ),
    ):

        return False

    # Solo dentro de formularios de maestros: los documentos y
    # tablas ya tienen su propia navegación con Enter.
    widget = objeto

    while widget is not None:

        if widget.property(
            "enter_avanza",
        ):

            return True

        if widget.property(
            "enter_propio",
        ):

            return False

        widget = widget.parentWidget()

    return False


_filtro_global: FiltroTeclado | None = None


def instalar_filtro_teclado() -> None:

    global _filtro_global

    app = QApplication.instance()

    if app is None or _filtro_global is not None:

        return

    _filtro_global = FiltroTeclado(
        app,
    )

    app.installEventFilter(
        _filtro_global,
    )
