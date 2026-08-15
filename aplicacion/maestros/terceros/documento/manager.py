from ..consultas.consulta_local import ConsultaLocal
from ..consultas.consulta_dian import ConsultaDIAN
from ..consultas.consulta_rues import ConsultaRUES
from ..consultas.consulta_api import ConsultaAPI

from aplicacion.dominio.documentos.resultado import DocumentoResult
from aplicacion.dominio.documentos.servicio import ServicioDocumento




class DocumentoManager:

    """

    Adaptador de infraestructura para consulta de documentos.



    Usa reglas de ``dominio.documentos`` y proveedores externos (DIAN, RUES, ERP).

    """



    proveedores = [

        ConsultaDIAN(),

        ConsultaRUES(),

        ConsultaAPI(),

    ]



    @classmethod

    def buscar(

        cls,

        tipo_documento,

        numero_documento,

    ) -> DocumentoResult:



        numero, dv = ServicioDocumento.preparar(

            tipo_documento,

            numero_documento,

        )



        resultado = DocumentoResult(

            tipo=tipo_documento,

            numero=numero,

            dv=dv,

        )



        local = ConsultaLocal().consultar(

            tipo_documento,

            numero,

        )



        local.dv = dv



        if local.existe:

            return local



        for proveedor in cls.proveedores:

            consulta = proveedor.consultar(

                tipo_documento,

                numero,

            )



            consulta.dv = dv



            ServicioDocumento.fusionar(

                resultado,

                consulta,

            )



            if ServicioDocumento.tiene_datos(

                resultado,

            ):

                break



        if (

            not ServicioDocumento.tiene_datos(

                resultado,

            )

            and not resultado.error

            and not resultado.mensaje

        ):

            resultado.mensaje = ServicioDocumento.mensaje_no_encontrado(

                tipo_documento,

            )



        return resultado



    @classmethod

    def preparar(

        cls,

        tipo_documento,

        numero_documento,

    ):

        return ServicioDocumento.preparar(

            tipo_documento,

            numero_documento,

        )


