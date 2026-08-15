from __future__ import annotations

import re

from aplicacion.nucleo.configuracion import Configuracion

from .cliente_muisca import ClienteMuisca
from .cliente_rues import ClienteRues
from .modelos import ResultadoDian


class DianServicio:
    """
    Orquesta consultas públicas DIAN/RUES sin certificado digital.
    Prioriza RUT (MUISCA) y enriquece con RUES cuando aplica.
    """

    TIPOS_PERSONA = {
        "CC",
        "CE",
        "TI",
        "PAS",
    }

    @classmethod
    def consultar(
        cls,
        tipo_documento: str,
        numero_documento: str,
    ) -> ResultadoDian:

        if not Configuracion.obtener(
            "dian",
            "habilitado",
        ):

            return ResultadoDian(
                tipo_documento=tipo_documento,
                numero_documento=numero_documento,
                error=(
                    "La integración DIAN está deshabilitada "
                    "en configuración."
                ),
            )

        numero = re.sub(
            r"\D",
            "",
            str(numero_documento),
        )

        tipo = str(
            tipo_documento
        ).upper().strip()

        resultado = ResultadoDian(
            tipo_documento=tipo,
            numero_documento=numero,
        )

        if Configuracion.obtener(
            "dian",
            "consulta_publica",
        ):

            if tipo in cls.TIPOS_PERSONA:

                cls._fusionar(
                    resultado,
                    ClienteRues.consultar_persona(
                        tipo,
                        numero,
                    ),
                )

            cls._fusionar(
                resultado,
                ClienteMuisca.consultar(
                    tipo,
                    numero,
                ),
            )

        if tipo == "NIT":

            cls._fusionar(
                resultado,
                ClienteRues.consultar_nit(
                    numero,
                ),
            )

        elif (
            tipo in cls.TIPOS_PERSONA
            and not cls._tiene_datos(
                resultado,
            )
        ):

            cls._fusionar(
                resultado,
                ClienteRues.consultar_persona(
                    tipo,
                    numero,
                ),
            )

        if cls._tiene_datos(
            resultado,
        ):

            resultado.encontrado = True
            resultado.error = ""

            if not resultado.mensaje:

                resultado.mensaje = (
                    "Datos obtenidos desde consulta externa."
                )

        elif resultado.error:

            if cls._es_error_transitorio(
                resultado.error,
            ):

                if not resultado.mensaje:

                    resultado.mensaje = resultado.error

                resultado.error = ""

        elif not resultado.mensaje:

            resultado.mensaje = resultado.error

        return resultado

    @staticmethod
    def _es_error_transitorio(
        mensaje: str,
    ) -> bool:

        texto = str(
            mensaje or "",
        ).lower()

        return any(
            clave in texto
            for clave in (
                "mantenimiento",
                "fuera de servicio",
                "temporalmente",
                "no entregó la página",
                "no respondió con datos",
            )
        )

    @staticmethod
    def _tiene_datos(
        resultado: ResultadoDian,
    ) -> bool:

        return bool(
            resultado.razon_social
            or resultado.primer_nombre
            or resultado.primer_apellido
            or resultado.estado_rut
        )

    @staticmethod
    def _fusionar(
        destino: ResultadoDian,
        origen: ResultadoDian,
    ) -> None:

        if origen.error and not destino.error:

            destino.error = origen.error

        if origen.origen and not destino.origen:

            destino.origen = origen.origen

        if origen.mensaje and not destino.mensaje:

            destino.mensaje = origen.mensaje

        if origen.datos_crudos:

            destino.datos_crudos.update(
                origen.datos_crudos,
            )

        for campo in (
            "dv",
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
            "correo",
            "estado_rut",
            "actividad_economica",
        ):

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
