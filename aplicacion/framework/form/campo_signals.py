from __future__ import annotations

from collections.abc import Callable

from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDateEdit,
    QDoubleSpinBox,
    QPlainTextEdit,
    QSpinBox,
    QTextEdit,
)


def conectar_cambio(
    widget,
    campo,
    callback: Callable[[], None],
) -> None:

    if widget is None:

        return

    if hasattr(
        widget,
        "documentoChanged",
    ):

        widget.documentoChanged.connect(
            lambda *_args: callback(),
        )

        return

    if isinstance(
        widget,
        QComboBox,
    ):

        widget.currentIndexChanged.connect(
            lambda *_args: callback(),
        )

        return

    if isinstance(
        widget,
        QCheckBox,
    ):

        widget.stateChanged.connect(
            lambda *_args: callback(),
        )

        return

    if isinstance(
        widget,
        (
            QSpinBox,
            QDoubleSpinBox,
        ),
    ):

        widget.valueChanged.connect(
            lambda *_args: callback(),
        )

        return

    if isinstance(
        widget,
        QDateEdit,
    ):

        widget.dateChanged.connect(
            lambda *_args: callback(),
        )

        return

    if isinstance(
        widget,
        (
            QTextEdit,
            QPlainTextEdit,
        ),
    ):

        widget.textChanged.connect(
            callback,
        )

        return

    if hasattr(
        widget,
        "textChanged",
    ):

        senal = widget.textChanged

        if (
            callable(
                senal,
            )
            and not hasattr(
                senal,
                "connect",
            )
        ):

            senal = senal()

        if hasattr(
            senal,
            "connect",
        ):

            senal.connect(
                lambda *_args: callback(),
            )

        return

    if hasattr(
        widget,
        "valueChanged",
    ):

        widget.valueChanged.connect(
            lambda *_args: callback(),
        )

        return

    if hasattr(
        widget,
        "editingFinished",
    ):

        widget.editingFinished.connect(
            callback,
        )
