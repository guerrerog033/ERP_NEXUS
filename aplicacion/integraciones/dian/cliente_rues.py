from __future__ import annotations

import re

import requests

from aplicacion.nucleo.configuracion import Configuracion

from .modelos import ResultadoDian


class ClienteRues:
    """
    Consulta datos abiertos RUES (datos.gov.co).
    No requiere certificado digital.
    """

    @classmethod
    def consultar_nit(
        cls,
        numero: str,
    ) -> ResultadoDian:

        numero_limpio = cls._limpiar_numero(
            numero,
        )

        resultado = ResultadoDian(
            tipo_documento="NIT",
            numero_documento=numero_limpio,
        )

        if len(numero_limpio) < 5:

            resultado.error = (
                "El NIT debe tener al menos 5 dígitos."
            )

            return resultado

        url = Configuracion.obtener(
            "dian",
            "url_rues",
        ) or (
            "https://www.datos.gov.co/resource/c82u-588k.json"
        )

        registro = cls._consultar_dataset(
            url,
            {
                "nit": numero_limpio,
                "$limit": 1,
            },
        )

        if registro is None:

            registro = cls._consultar_dataset(
                url,
                {
                    "numero_identificacion": numero_limpio,
                    "$limit": 1,
                },
            )

        if registro is None:

            return resultado

        cls._mapear_empresa(
            resultado,
            registro,
        )

        return resultado

    @classmethod
    def consultar_persona(
        cls,
        tipo_documento: str,
        numero: str,
    ) -> ResultadoDian:

        numero_limpio = cls._limpiar_numero(
            numero,
        )

        resultado = ResultadoDian(
            tipo_documento=tipo_documento,
            numero_documento=numero_limpio,
        )

        if len(numero_limpio) < 5:

            return resultado

        url = Configuracion.obtener(
            "dian",
            "url_rues_personas",
        ) or (
            "https://www.datos.gov.co/resource/cas9-r54x.json"
        )

        registro = cls._consultar_dataset(
            url,
            {
                "numero_identificacion": numero_limpio,
                "$limit": 1,
            },
        )

        if registro is None:

            registro = cls._consultar_dataset(
                url,
                {
                    "cedula": numero_limpio,
                    "$limit": 1,
                },
            )

        if registro is None:

            registro = cls._consultar_dataset(
                url,
                {
                    "nit": numero_limpio,
                    "$limit": 1,
                },
            )

        if registro is None:

            return resultado

        cls._mapear_persona(
            resultado,
            registro,
        )

        return resultado

    @classmethod
    def _consultar_dataset(
        cls,
        url: str,
        params: dict,
    ) -> dict | None:

        timeout = Configuracion.obtener(
            "dian",
            "timeout_segundos",
        ) or 30

        try:

            respuesta = requests.get(
                url,
                params=params,
                timeout=timeout,
                headers={
                    "Accept": "application/json",
                    "User-Agent": "ERP-NEXUS/0.1",
                },
            )

            respuesta.raise_for_status()

            registros = respuesta.json()

        except (
            requests.RequestException,
            ValueError,
        ):

            return None

        if not registros:

            return None

        return registros[0]

    @classmethod
    def _mapear_empresa(
        cls,
        resultado: ResultadoDian,
        registro: dict,
    ) -> None:

        resultado.encontrado = True
        resultado.origen = "RUES"
        resultado.datos_crudos = registro

        resultado.razon_social = cls._valor(
            registro,
            "razon_social",
        )

        resultado.nombre_comercial = cls._valor(
            registro,
            "nombre_comercial",
        )

        resultado.estado_rut = cls._valor(
            registro,
            "estado_matricula",
        ) or cls._valor(
            registro,
            "estado",
        )

        resultado.ciudad = cls._valor(
            registro,
            "municipio",
        ) or cls._valor(
            registro,
            "ciudad",
        )

        resultado.departamento = cls._valor(
            registro,
            "departamento",
        )

        dv = cls._valor(
            registro,
            "digito_verificacion",
        )

        if dv:

            resultado.dv = dv

        camara = cls._valor(
            registro,
            "camara_comercio",
        )

        resultado.mensaje = (
            "Datos obtenidos desde RUES (datos abiertos Colombia)."
        )

        if camara:

            resultado.mensaje = (
                f"{resultado.mensaje}\n"
                f"Cámara de comercio: {camara}"
            )

    @classmethod
    def _mapear_persona(
        cls,
        resultado: ResultadoDian,
        registro: dict,
    ) -> None:

        resultado.encontrado = True
        resultado.origen = "RUES"
        resultado.datos_crudos = registro

        resultado.primer_nombre = cls._valor(
            registro,
            "nombre_1",
        )

        resultado.segundo_nombre = cls._valor(
            registro,
            "nombre_2",
        )

        resultado.primer_apellido = cls._valor(
            registro,
            "apellido_1",
        )

        resultado.segundo_apellido = cls._valor(
            registro,
            "apellido_2",
        )

        resultado.razon_social = " ".join(
            filter(
                None,
                [
                    resultado.primer_nombre,
                    resultado.segundo_nombre,
                    resultado.primer_apellido,
                    resultado.segundo_apellido,
                ],
            )
        )

        resultado.direccion = cls._valor(
            registro,
            "dir_comercial",
        )

        resultado.correo = cls._valor(
            registro,
            "email_comercial",
        )

        resultado.estado_rut = cls._valor(
            registro,
            "estado_matricula",
        )

        resultado.mensaje = (
            "Datos obtenidos desde RUES (personas naturales)."
        )

    @staticmethod
    def _limpiar_numero(
        numero: str,
    ) -> str:

        return re.sub(
            r"\D",
            "",
            str(numero),
        )

    @staticmethod
    def _valor(
        registro: dict,
        clave: str,
    ) -> str:

        valor = registro.get(clave)

        if valor is None:

            return ""

        return str(valor).strip()
