from aplicacion.framework.crud.crud_master import CrudMaster



from .controlador import TerceroControlador

from .datasource import (

    ClienteDataSource,

    OtroDataSource,

    ProveedorDataSource,

    TerceroDataSource,

)

from .formulario import TerceroFormulario
from .formulario_cliente import (
    ClienteFormulario,
)





class MaestroTerceros(CrudMaster):



    titulo = "Terceros"



    titulo_singular = "Tercero"



    controlador = TerceroControlador



    datasource = TerceroDataSource



    formulario = TerceroFormulario



    tipo_filtro = None



    def crear_formulario(

        self,

        id_registro=None,

        parent=None,

        *,

        modo=None,

    ):

        kwargs = {

            "id_registro": id_registro,

            "tipo_tercero_inicial": self.tipo_filtro,

            "parent": parent,

        }

        if modo is not None:

            kwargs["modo"] = modo

        return self.formulario(

            **kwargs,

        )



    def _icono_dialogo_formulario(self):



        from aplicacion.recursos.ui.recursos import (

            Recursos,

        )



        return Recursos.icono_terceros()



    def _tamanio_dialogo_formulario(

        self,

        formulario,

    ) -> tuple[int, int]:



        ancho, alto = super()._tamanio_dialogo_formulario(

            formulario,

        )



        return (

            min(

                ancho,

                820,

            ),

            min(

                alto,

                600,

            ),

        )



    def _limites_dialogo_formulario(

        self,

        ancho: int,

        alto: int,

    ) -> tuple[

        tuple[int, int],

        tuple[int, int] | None,

    ]:



        minimo, _ = super()._limites_dialogo_formulario(

            ancho,

            alto,

        )



        return (

            minimo,

            (

                max(

                    640,

                    self.width() - 16,

                ),

                max(

                    480,

                    self.height() - 16,

                ),

            ),

        )





class MaestroClientes(MaestroTerceros):



    titulo = "Clientes"



    titulo_singular = "Cliente"



    tipo_filtro = "Cliente"



    datasource = ClienteDataSource

    formulario = ClienteFormulario





class MaestroProveedores(MaestroTerceros):



    titulo = "Proveedores"



    titulo_singular = "Proveedor"



    tipo_filtro = "Proveedor"



    datasource = ProveedorDataSource





class MaestroOtros(MaestroTerceros):



    titulo = "Otros"



    titulo_singular = "Tercero"



    tipo_filtro = "Otro"



    datasource = OtroDataSource

