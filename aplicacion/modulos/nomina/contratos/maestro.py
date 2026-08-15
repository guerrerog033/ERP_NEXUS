from aplicacion.framework.crud.crud_master import CrudMaster

from .datasource import ContratoDataSource
from .formulario import FormularioContrato


class MaestroContratos(CrudMaster):

    titulo = "Contratos históricos"

    titulo_singular = "Contrato"

    datasource = ContratoDataSource

    formulario = FormularioContrato
