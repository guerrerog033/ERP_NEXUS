from aplicacion.framework.crud.crud_master import CrudMaster

from .datasource import EmpleadoDataSource
from .formulario import FormularioEmpleado


class MaestroEmpleados(CrudMaster):

    titulo = "Empleados"

    titulo_singular = "Empleado"

    datasource = EmpleadoDataSource

    formulario = FormularioEmpleado
