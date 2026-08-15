from aplicacion.framework.form.events import FormEvents
from aplicacion.framework.form.campo_signals import conectar_cambio
from aplicacion.recursos.estilos import colores, dimensiones
from aplicacion.recursos.estilos.colores import Colores


def test_form_events_guardar_cancelar_cambio():

    eventos = FormEvents()

    guardados = []
    cancelados = []
    cambios = []

    eventos.al_guardar(
        lambda: guardados.append(
            True,
        ),
    )
    eventos.al_cancelar(
        lambda: cancelados.append(
            True,
        ),
    )
    eventos.al_cambiar(
        lambda nombre, valor: cambios.append(
            (
                nombre,
                valor,
            ),
        ),
    )

    eventos.emitir_guardar()
    eventos.emitir_cancelar()
    eventos.emitir_cambio(
        "nombre",
        "Ana",
    )

    assert guardados == [
        True,
    ]
    assert cancelados == [
        True,
    ]
    assert cambios == [
        (
            "nombre",
            "Ana",
        ),
    ]


def test_engine_emite_campo_al_cambiar():

    class _LineEdit:

        def __init__(
            self,
        ):

            self._texto = ""
            self._callback = None

        def text(
            self,
        ):

            return self._texto

        def textChanged(self):

            return self

        def connect(
            self,
            callback,
        ):

            self._callback = callback

        def setText(
            self,
            valor,
        ):

            self._texto = str(
                valor or "",
            )

            if self._callback is not None:

                self._callback(
                    self._texto,
                )

    capturado = {}

    widget = _LineEdit()

    def _emitir():

        capturado[
            "valor"
        ] = widget.text()

    conectar_cambio(
        widget,
        None,
        _emitir,
    )

    widget.setText(
        "German",
    )

    assert capturado[
        "valor"
    ] == "German"


def test_design_tokens():

    assert colores.PRIMARY == "#1B4F8A"
    assert Colores.PRIMARIO == colores.PRIMARY
    assert dimensiones.CONTROL_MD == 36


def test_form_builder_sin_stylesheet_inline():

    from pathlib import Path

    contenido = (
        Path(
            "aplicacion/framework/form/builder.py",
        )
        .read_text(
            encoding="utf-8",
        )
    )

    assert "groupbox.setStyleSheet" not in contenido
    assert 'setObjectName(\n            "FormGroupBox"' in contenido
