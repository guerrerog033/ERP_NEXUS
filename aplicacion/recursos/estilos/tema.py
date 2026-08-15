from PySide6.QtCore import Qt


def habilitar_fondo_qss(
    widget,
) -> None:

    widget.setAttribute(
        Qt.WA_StyledBackground,
        True,
    )


def aplicar_tema(app):

    from pathlib import Path

    archivo = (
        Path(__file__)
        .parent
        .joinpath("tema.qss")
    )

    with open(
        archivo,
        "r",
        encoding="utf-8",
    ) as f:

        app.setStyleSheet(
            f.read(),
        )
