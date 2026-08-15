from aplicacion.framework.crud.crud_master import CrudMaster

from .datasource import ActividadDataSource
from .formulario import FormularioActividad


class MaestroActividadesCRM(CrudMaster):

    titulo = "Actividades CRM"

    titulo_singular = "Actividad"

    datasource = ActividadDataSource

    formulario = FormularioActividad
