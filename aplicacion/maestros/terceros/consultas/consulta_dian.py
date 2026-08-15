from __future__ import annotations

from aplicacion.integraciones.dian import DianServicio

from .consulta_base import ConsultaDocumento
from ..documento_result import DocumentoResult


class ConsultaDIAN(ConsultaDocumento):
    """
    Consulta pública DIAN/RUT al registrar terceros.
    No requiere certificado digital.
    """

    CAMPOS_DATOS = (
        "razon_social",
        "nombre_comercial",
        "primer_nombre",
        "segundo_nombre",
        "primer_apellido",
        "segundo_apellido",
        "direccion",
        "ciudad",
        "departamento",
        "telefono",
        "correo",
        "estado_rut",
    )

    def consultar(
        self,
        tipo_documento,
        numero_documento,
    ) -> DocumentoResult:

        resultado = DocumentoResult(
            tipo=tipo_documento,
            numero=numero_documento,
        )

        consulta = DianServicio.consultar(
            tipo_documento,
            numero_documento,
        )

        tiene_datos = self._tiene_datos(
            consulta,
        )

        if tiene_datos:

            self._mapear(
                resultado,
                consulta,
            )

        if consulta.error:

            if (
                not tiene_datos
                or "mantenimiento"
                not in consulta.error.lower()
            ):

                resultado.error = consulta.error

        elif (
            not tiene_datos
            and consulta.mensaje
        ):

            resultado.mensaje = consulta.mensaje

        return resultado

    @classmethod
    def _tiene_datos(
        cls,
        consulta,
    ) -> bool:

        return any(
            getattr(
                consulta,
                campo,
            )
            for campo in cls.CAMPOS_DATOS
        )

    @classmethod
    def _mapear(
        cls,
        resultado: DocumentoResult,
        consulta,
    ) -> None:

        resultado.origen = consulta.origen
        resultado.estado_rut = consulta.estado_rut
        resultado.mensaje = consulta.mensaje
        resultado.externo = consulta.datos_crudos

        resultado.razon_social = consulta.razon_social
        resultado.nombre_comercial = consulta.nombre_comercial
        resultado.primer_nombre = consulta.primer_nombre
        resultado.segundo_nombre = consulta.segundo_nombre
        resultado.primer_apellido = consulta.primer_apellido
        resultado.segundo_apellido = consulta.segundo_apellido
        resultado.direccion = consulta.direccion
        resultado.ciudad = consulta.ciudad
        resultado.departamento = consulta.departamento
        resultado.pais = consulta.pais or (
            "Colombia"
            if any(
                getattr(
                    consulta,
                    campo,
                )
                for campo in cls.CAMPOS_DATOS
            )
            else ""
        )
        resultado.telefono = consulta.telefono
        resultado.correo = consulta.correo
