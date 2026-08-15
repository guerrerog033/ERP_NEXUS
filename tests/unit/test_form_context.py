from aplicacion.framework.form.form_context import FormContext
from aplicacion.framework.form.form_definition import FormDefinition
from aplicacion.framework.form.text_field import TextField


class _DefPrueba(FormDefinition):

    titulo = "Prueba"

    campos = (
        TextField(
            nombre="nombre",
            titulo="Nombre",
        ),
        TextField(
            nombre="dv",
            titulo="DV",
        ),
    )


class _WidgetStub:

    def __init__(
        self,
    ):

        self.enabled = True
        self.visible = True
        self.focused = False

    def setEnabled(
        self,
        valor,
    ):

        self.enabled = bool(
            valor,
        )

    def setVisible(
        self,
        valor,
    ):

        self.visible = bool(
            valor,
        )

    def setFocus(
        self,
    ):

        self.focused = True


def test_form_context_campo():

    contexto = FormContext()
    contexto.formulario = _DefPrueba

    campo = contexto.campo(
        "nombre",
    )

    assert campo is not None
    assert campo.nombre == "nombre"


def test_form_context_habilitar_mostrar_enfocar():

    contexto = FormContext()
    widget = _WidgetStub()

    contexto.registrar_widget(
        "dv",
        widget,
    )

    contexto.habilitar(
        "dv",
        False,
    )
    contexto.mostrar(
        "dv",
        False,
    )
    contexto.enfocar(
        "dv",
    )

    assert widget.enabled is False
    assert widget.visible is False
    assert widget.focused is True


def test_form_context_cambiar_delega_engine(
    monkeypatch,
):

    contexto = FormContext()

    class _Engine:

        registrado = {}

        def on(
            self,
            evento,
            callback,
        ):

            self.registrado[
                evento
            ] = callback

    motor = _Engine()
    contexto.engine = motor

    def _callback():
        pass

    contexto.cambiar(
        "numero_documento",
        _callback,
    )

    assert (
        motor.registrado[
            "campo:numero_documento"
        ]
        is _callback
    )
