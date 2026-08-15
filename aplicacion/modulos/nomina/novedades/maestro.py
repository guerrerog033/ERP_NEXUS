from aplicacion.framework.crud.crud_master import CrudMaster

from .datasource import NovedadDataSource
from .formulario import FormularioNovedad


class MaestroNovedades(CrudMaster):

    titulo = "Novedades de nómina"

    titulo_singular = "Novedad"

    datasource = NovedadDataSource

    formulario = FormularioNovedad
