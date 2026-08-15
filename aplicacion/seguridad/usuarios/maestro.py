from aplicacion.framework.crud.crud_master import CrudMaster
from aplicacion.seguridad.acceso import panel_seguridad_visible

from aplicacion.seguridad.usuarios.datasource import (
    UsuarioDataSource,
)
from aplicacion.seguridad.usuarios.formulario import (
    FormularioUsuario,
)


class MaestroUsuarios(CrudMaster):

    titulo = "Usuarios"

    titulo_singular = "Usuario"

    datasource = UsuarioDataSource

    formulario = FormularioUsuario

    def __init__(self):

        if not panel_seguridad_visible():

            raise PermissionError(
                "No tiene permisos para administrar usuarios.",
            )

        super().__init__()
