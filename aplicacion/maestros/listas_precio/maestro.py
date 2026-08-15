from aplicacion.framework.crud.crud_master import CrudMaster

from .datasource import ListaPrecioDataSource
from .formulario import FormularioListaPrecio
from .servicios import ServicioListaPrecio


class MaestroListasPrecio(CrudMaster):

    titulo = "Listas de precio"

    titulo_singular = "Lista de precio"

    datasource = ListaPrecioDataSource

    formulario = FormularioListaPrecio

    def __init__(self):

        ServicioListaPrecio.inicializar_predeterminados()

        super().__init__()
