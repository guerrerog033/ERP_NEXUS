from aplicacion.framework.crud.crud_master import CrudMaster
from aplicacion.seguridad.acceso import panel_seguridad_visible

from aplicacion.seguridad.roles.datasource import (
    RolDataSource,
)
from aplicacion.seguridad.roles.formulario import (
    FormularioRol,
)


class MaestroRoles(CrudMaster):

    titulo = "Roles"

    titulo_singular = "Rol"

    datasource = RolDataSource

    formulario = FormularioRol

    def __init__(self):

        if not panel_seguridad_visible():

            raise PermissionError(
                "No tiene permisos para administrar roles.",
            )

        super().__init__()
