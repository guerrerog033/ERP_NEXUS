from __future__ import annotations

from aplicacion.integraciones.dian.cliente_rues import ClienteRues

from .consulta_base import ConsultaDocumento
from ..documento_result import DocumentoResult


class ConsultaRUES(ConsultaDocumento):
    """
    Consulta datos abiertos RUES como respaldo para NIT.
    """

    def consultar(
        self,
        tipo_documento,
        numero_documento,
    ) -> DocumentoResult:

        resultado = DocumentoResult(
            tipo=tipo_documento,
            numero=numero_documento,
        )

        if str(
            tipo_documento
        ).upper() != "NIT":

            return resultado

        consulta = ClienteRues.consultar_nit(
            numero_documento,
        )

        if not consulta.encontrado:

            return resultado

        resultado.origen = consulta.origen
        resultado.estado_rut = consulta.estado_rut
        resultado.mensaje = consulta.mensaje
        resultado.externo = consulta.datos_crudos
        resultado.razon_social = consulta.razon_social
        resultado.nombre_comercial = consulta.nombre_comercial
        resultado.direccion = consulta.direccion
        resultado.ciudad = consulta.ciudad
        resultado.departamento = consulta.departamento
        resultado.pais = consulta.pais or (
            "Colombia"
            if consulta.encontrado
            else ""
        )

        return resultado
