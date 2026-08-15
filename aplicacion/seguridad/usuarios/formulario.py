from aplicacion.framework.base.formulario_base import FormularioBase

from aplicacion.seguridad.usuarios.datasource import (
    UsuarioDataSource,
)
from aplicacion.seguridad.usuarios.usuario_definition import (
    UsuarioDefinition,
)


class FormularioUsuario(FormularioBase):

    titulo = "Usuarios"

    definition = UsuarioDefinition

    datasource = UsuarioDataSource

    def _crear_formulario(self):

        self.definition.campos = (
            UsuarioDefinition.campos_dinamicos()
        )

        super()._crear_formulario()

    def _cargar_registro(self):

        if self.datasource is None:

            return

        objeto = self.datasource.obtener_por_id(
            self.id_registro,
        )

        if objeto is None:

            return

        self.formulario.cargar(
            objeto,
        )

        password = self.widget(
            "password",
        )

        if password is not None:

            password.clear()
