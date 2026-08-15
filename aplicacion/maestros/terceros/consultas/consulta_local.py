from .consulta_base import ConsultaDocumento

from ..documento_result import DocumentoResult

from ..repositorio import TerceroRepositorio


class ConsultaLocal(ConsultaDocumento):
    """
    Consulta primero la base de datos del ERP.
    """

    # =====================================================
    # Consultar
    # =====================================================

    def consultar(
        self,
        tipo_documento,
        numero_documento,
    ) -> DocumentoResult:

        resultado = DocumentoResult(

            tipo=tipo_documento,

            numero=numero_documento,

        )

        tercero = TerceroRepositorio.obtener_por_documento(

            tipo_documento,

            numero_documento,

        )

        if tercero is None:

            return resultado

        resultado.existe = True

        resultado.tercero = tercero

        resultado.dv = tercero.dv or ""

        resultado.razon_social = tercero.razon_social or ""

        resultado.nombre_comercial = tercero.nombre_comercial or ""

        resultado.primer_nombre = tercero.primer_nombre or ""

        resultado.segundo_nombre = tercero.segundo_nombre or ""

        resultado.primer_apellido = tercero.primer_apellido or ""

        resultado.segundo_apellido = tercero.segundo_apellido or ""

        resultado.direccion = tercero.direccion or ""

        resultado.ciudad = tercero.ciudad or ""

        resultado.departamento = tercero.departamento or ""

        resultado.pais = tercero.pais or ""

        resultado.telefono = tercero.telefono or ""

        resultado.celular = tercero.celular or ""

        resultado.correo = tercero.correo or ""

        return resultado