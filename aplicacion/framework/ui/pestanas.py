"""
Abrir formularios y vistas de documento como pestañas del área de
trabajo, en lugar de ventanas flotantes (QDialog).

Si no hay área de trabajo (pruebas, scripts) las funciones devuelven
``None`` y quien llama puede usar su ventana de siempre.
"""

from __future__ import annotations

from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)


def area_trabajo():

    from aplicacion.framework.app_context import AppContext

    return getattr(
        AppContext,
        "area_trabajo",
        None,
    )


def enfocar_pestana(
    clave,
) -> QWidget | None:
    """
    Si ya hay una pestaña abierta con esa clave (mismo registro),
    la trae al frente en vez de abrir otra igual.
    """

    area = area_trabajo()

    if area is None or clave is None:

        return None

    for indice in range(
        area.count(),
    ):

        widget = area.widget(
            indice,
        )

        if getattr(
            widget,
            "_clave_pestana",
            None,
        ) == clave:

            area.setCurrentIndex(
                indice,
            )

            return widget

    return None


def abrir_en_pestana(
    widget: QWidget,
    titulo: str,
    *,
    clave=None,
    ancho_maximo: int | None = None,
    al_cerrar=None,
) -> QWidget | None:
    """
    Agrega ``widget`` como pestaña. Si el widget tiene la señal
    ``cerrar`` (formularios y vistas de documento), al emitirla se
    cierra la pestaña. ``ancho_maximo`` centra contenidos angostos
    para que no queden estirados a todo lo ancho de la pantalla.
    ``al_cerrar`` se llama cuando la pestaña se cierra.
    """

    area = area_trabajo()

    if area is None:

        return None

    contenedor = QWidget()

    contenedor.setObjectName(
        "PestanaContenido",
    )

    contenedor._clave_pestana = clave

    # Hereda el módulo de la pestaña desde donde se abrió (color y
    # nombre en la barra de estado).
    contenedor._modulo_id = getattr(
        area.currentWidget(),
        "_modulo_id",
        None,
    )

    layout = QVBoxLayout(
        contenedor,
    )

    layout.setContentsMargins(
        16,
        12,
        16,
        12,
    )

    interior = widget

    if ancho_maximo:

        widget.setMaximumWidth(
            ancho_maximo,
        )

        fila = QWidget()

        fila.setObjectName(
            "PestanaContenidoFila",
        )

        layout_fila = QHBoxLayout(
            fila,
        )

        layout_fila.setContentsMargins(
            0,
            0,
            0,
            0,
        )

        layout_fila.addStretch(
            1,
        )

        layout_fila.addWidget(
            widget,
            100,
        )

        layout_fila.addStretch(
            1,
        )

        interior = fila

    scroll = QScrollArea()

    scroll.setObjectName(
        "PestanaContenidoScroll",
    )

    scroll.setWidgetResizable(
        True,
    )

    scroll.setFrameShape(
        QFrame.Shape.NoFrame,
    )

    scroll.setWidget(
        interior,
    )

    layout.addWidget(
        scroll,
    )

    senal_cerrar = getattr(
        widget,
        "cerrar",
        None,
    )

    if senal_cerrar is not None and hasattr(
        senal_cerrar,
        "connect",
    ):

        senal_cerrar.connect(
            lambda *_args: area.cerrar_widget(
                contenedor,
            ),
        )

    if al_cerrar is not None:

        def _al_destruir(
            *_args,
        ) -> None:

            try:

                al_cerrar()

            except RuntimeError:

                # El maestro que abrió la pestaña ya no existe.
                pass

        contenedor.destroyed.connect(
            _al_destruir,
        )

    area.abrir(
        contenedor,
        titulo,
    )

    return contenedor
