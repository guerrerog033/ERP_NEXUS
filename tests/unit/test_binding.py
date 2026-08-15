from dataclasses import dataclass

from aplicacion.framework.form.accessors.check_accessor import (
    CheckAccessor,
)
from aplicacion.framework.form.accessors.text_accessor import (
    TextAccessor,
)
from aplicacion.framework.form.binding import FormBinding
from aplicacion.framework.form.check_field import CheckField
from aplicacion.framework.form.form_definition import FormDefinition
from aplicacion.framework.form.text_field import TextField


@dataclass
class _Registro:

    nombre: str = ""
    activo: bool = False


class _DefPrueba(FormDefinition):

    titulo = "Prueba"

    campos = (
        TextField(
            nombre="nombre",
            titulo="Nombre",
        ),
        CheckField(
            nombre="activo",
            titulo="Activo",
        ),
    )


class _CheckStub:

    def __init__(
        self,
    ):

        self._checked = False

    def isChecked(
        self,
    ) -> bool:

        return self._checked

    def setChecked(
        self,
        value: bool,
    ) -> None:

        self._checked = bool(
            value,
        )


class _TextStub:

    def __init__(
        self,
    ):

        self._text = ""

    def text(
        self,
    ) -> str:

        return self._text

    def setText(
        self,
        value: str,
    ) -> None:

        self._text = str(
            value or "",
        )


def test_form_binding_carga_y_lee_valores():
    widgets = {
        "nombre": _TextStub(),
        "activo": _CheckStub(),
    }

    binding = FormBinding(
        _DefPrueba,
        widgets,
    )

    binding.cargar(
        _Registro(
            nombre="Acme",
            activo=True,
        ),
    )

    valores = binding.valores()

    assert valores["nombre"] == "Acme"
    assert valores["activo"] is True


def test_check_accessor():
    accessor = CheckAccessor()
    widget = _CheckStub()

    accessor.escribir(
        widget,
        True,
        None,
    )

    assert accessor.leer(
        widget,
        None,
    ) is True

    accessor.escribir(
        widget,
        False,
        None,
    )

    assert accessor.leer(
        widget,
        None,
    ) is False


def test_text_accessor():
    accessor = TextAccessor()
    widget = _TextStub()

    accessor.escribir(
        widget,
        " ERP ",
        None,
    )

    assert (
        accessor.leer(
            widget,
            None,
        )
        == " ERP "
    )
