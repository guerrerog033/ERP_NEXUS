from PySide6.QtWidgets import QApplication

from aplicacion.framework.base.formulario_base import FormularioBase
from aplicacion.framework.form import (
    FormDefinition,
    LookupField,
)

from aplicacion.maestros.marcas.marca_lookup import MarcaLookup


class DemoDefinition(FormDefinition):

    titulo = "Prueba Lookup"

    campos = [

        LookupField(
            nombre="marca_id",
            titulo="Marca",
            controlador=MarcaLookup,
        ),

    ]


class DemoFormulario(FormularioBase):

    definition = DemoDefinition

    datasource = None


if __name__ == "__main__":

    import sys

    app = QApplication(sys.argv)

    formulario = DemoFormulario()

    formulario.show()

    sys.exit(app.exec())