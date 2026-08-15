from aplicacion.framework.form.campo_contenedor import CampoContenedor
from aplicacion.framework.form.validation_engine import ValidationEngine
from aplicacion.framework.form.validators import Required
from aplicacion.interfaz.barra_lateral import BarraLateral
from aplicacion.recursos.ui.botones import Botones


def _qapp():
    from PySide6.QtWidgets import QApplication

    app = QApplication.instance()

    if app is None:

        app = QApplication([])

    return app


def test_barra_lateral_ancho_colapsado():
    assert BarraLateral.ANCHO == 240
    assert BarraLateral.ANCHO_COLAPSADO == 68


def test_botones_jerarquia_object_name():
    _qapp()

    assert Botones.guardar().objectName() == "BotonPrimario"
    assert Botones.cancelar().objectName() == "BotonSecundario"
    assert Botones.eliminar().objectName() == "BotonPeligro"
    assert Botones.primario().objectName() == "BotonPrimario"
    assert Botones.secundario().objectName() == "BotonSecundario"
    assert Botones.peligro().objectName() == "BotonPeligro"


def test_validation_engine_errores():
    from aplicacion.framework.form.text_field import TextField
    from aplicacion.framework.form.form_definition import FormDefinition
    from aplicacion.framework.form.field_group import FieldGroup

    class DemoDefinition(FormDefinition):
        titulo = "Demo"

        @classmethod
        def obtener_grupos(cls):
            return [
                FieldGroup(
                    "",
                    [
                        TextField(
                            "nombre",
                            "Nombre",
                            validadores=[
                                Required(),
                            ],
                        ),
                    ],
                ),
            ]

    motor = ValidationEngine(
        DemoDefinition,
    )

    errores = motor.errores(
        {
            "nombre": "",
        },
    )

    assert "nombre" in errores


def test_campo_contenedor_marca_error():
    from PySide6.QtWidgets import QLineEdit

    _qapp()

    linea = QLineEdit()
    contenedor = CampoContenedor(
        linea,
    )

    contenedor.show()

    contenedor.marcar_error(
        "Campo obligatorio",
    )

    assert contenedor.lbl_error.isVisible()
    assert contenedor.lbl_error.text() == "Campo obligatorio"
    assert linea.property(
        "invalid",
    )

    contenedor.limpiar_error()

    assert not contenedor.lbl_error.isVisible()
    assert not linea.property(
        "invalid",
    )


def test_form_context_aplica_errores():
    from PySide6.QtWidgets import QLineEdit

    from aplicacion.framework.form.form_context import FormContext

    _qapp()

    contexto = FormContext()
    contenedor = CampoContenedor(
        QLineEdit(),
    )

    contenedor.show()

    contexto.registrar_campo_contenedor(
        "nombre",
        contenedor,
    )

    contexto.aplicar_errores(
        {
            "nombre": "Requerido",
        },
    )

    assert contenedor.lbl_error.text() == "Requerido"

    contexto.limpiar_errores()

    assert not contenedor.lbl_error.isVisible()
