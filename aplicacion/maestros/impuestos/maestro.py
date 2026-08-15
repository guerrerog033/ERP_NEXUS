from aplicacion.framework.crud.crud_master import CrudMaster

from .datasource import ImpuestoDataSource
from .formulario import FormularioImpuesto
from .servicios import ServicioImpuesto


class MaestroImpuestos(CrudMaster):

    titulo = "Impuestos"

    titulo_singular = "Impuesto"

    datasource = ImpuestoDataSource

    formulario = FormularioImpuesto

    def __init__(self):

        ServicioImpuesto.inicializar_predeterminados()

        super().__init__()
