from aplicacion.framework.crud.crud_master import CrudMaster

from .datasource import BodegaDataSource
from .formulario import FormularioBodega
from .servicios import ServicioBodega


class MaestroBodegas(CrudMaster):

    titulo = "Bodegas"

    titulo_singular = "Bodega"

    datasource = BodegaDataSource

    formulario = FormularioBodega

    def __init__(self):

        from aplicacion.modulos.inventario.servicios import (
            ServicioInventario,
        )

        ServicioInventario.inicializar_bodega()

        super().__init__()
