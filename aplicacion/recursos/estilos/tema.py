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

        contenido = f.read()

    # Las imágenes del tema (flechas de combos y fechas) se referencian
    # como {ICONOS}/archivo.svg; se resuelven con la ruta absoluta para
    # que funcionen sin importar desde qué carpeta se abra el ERP.
    iconos = (
        Path(__file__)
        .resolve()
        .parent
        .parent
        .joinpath(
            "iconos",
            "acciones",
        )
        .as_posix()
    )

    app.setStyleSheet(
        contenido.replace(
            "{ICONOS}",
            iconos,
        ),
    )
