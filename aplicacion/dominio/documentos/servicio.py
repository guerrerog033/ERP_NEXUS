from __future__ import annotations

from .dv import DVCalculator
from .normalizador import NormalizadorDocumento
from .resultado import DocumentoResult
from .validador import ValidadorDocumento


class ServicioDocumento:
    """
    Reglas puras del ciclo de documento (sin DIAN, RUES ni BD).
    """

    CAMPOS_FUSION = (
        "origen",
        "estado_rut",
        "razon_social",
        "nombre_comercial",
        "primer_nombre",
        "segundo_nombre",
        "primer_apellido",
        "segundo_apellido",
        "direccion",
        "ciudad",
        "departamento",
        "pais",
        "telefono",
        "celular",
        "correo",
        "mensaje",
        "error",
    )

    @classmethod
    def preparar(
        cls,
        tipo_documento,
        numero_documento,
    ) -> tuple[str, str]:
        numero = NormalizadorDocumento.normalizar(
            numero_documento,
        )

        ValidadorDocumento.validar(
            tipo_documento,
            numero,
        )

        dv = ""

        if str(tipo_documento).upper() == "NIT":
            dv = DVCalculator.calcular(
                numero,
            )

        return numero, dv

    @classmethod
    def tiene_datos(
        cls,
        resultado: DocumentoResult,
    ) -> bool:
        return bool(
            resultado.razon_social
            or resultado.primer_nombre
            or resultado.primer_apellido
            or resultado.nombre_comercial
            or resultado.estado_rut
        )

    @classmethod
    def fusionar(
        cls,
        destino: DocumentoResult,
        origen: DocumentoResult,
    ) -> None:
        for campo in cls.CAMPOS_FUSION:
            valor = getattr(
                origen,
                campo,
            )

            if valor and not getattr(
                destino,
                campo,
            ):
                setattr(
                    destino,
                    campo,
                    valor,
                )

        if origen.externo and not destino.externo:
            destino.externo = origen.externo

    @classmethod
    def mensaje_no_encontrado(
        cls,
        tipo_documento,
    ) -> str:
        tipo = str(
            tipo_documento,
        ).upper()

        if tipo == "NIT":
            return (
                "No se encontró el NIT en RUT/DIAN ni en RUES."
            )

        if tipo in {
            "CC",
            "CE",
            "TI",
            "PAS",
        }:
            return (
                "No se encontró la persona en RUT/DIAN. "
                "RUES solo incluye cédulas registradas "
                "como comerciante."
            )

        return "No se encontró el documento consultado."
