from aplicacion.framework.crud.crud_master import CrudMaster

from .datasource import OportunidadDataSource
from .formulario import FormularioOportunidad


class MaestroOportunidades(CrudMaster):

    titulo = "Oportunidades"

    titulo_singular = "Oportunidad"

    datasource = OportunidadDataSource

    formulario = FormularioOportunidad
