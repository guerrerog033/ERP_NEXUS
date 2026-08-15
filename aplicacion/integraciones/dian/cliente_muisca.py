from __future__ import annotations

import re

import requests
from bs4 import BeautifulSoup

from aplicacion.nucleo.configuracion import Configuracion

from .modelos import ResultadoDian


class ClienteMuisca:
    """
    Consulta pública del estado RUT en MUISCA (DIAN).
    No requiere certificado digital ni software habilitado.
    """

    PREFIJO = (
        "vistaConsultaEstadoRUT:formConsultaEstadoRUT:"
    )

    CAMPOS_RESULTADO = {
        "razonSocial": "razon_social",
        "primerNombre": "primer_nombre",
        "otrosNombres": "segundo_nombre",
        "primerApellido": "primer_apellido",
        "segundoApellido": "segundo_apellido",
        "dv": "dv",
        "estado": "estado_rut",
        "direccionPrincipal": "direccion",
        "municipio": "ciudad",
        "departamento": "departamento",
        "email": "correo",
        "telefono": "telefono",
    }

    ETIQUETAS = {
        "razon social": "razon_social",
        "nombre o razón social": "razon_social",
        "nombre o razon social": "razon_social",
        "primer apellido": "primer_apellido",
        "segundo apellido": "segundo_apellido",
        "primer nombre": "primer_nombre",
        "segundo nombre": "segundo_nombre",
        "estado": "estado_rut",
        "estado del rut": "estado_rut",
        "actividad económica": "actividad_economica",
        "actividad economica": "actividad_economica",
        "correo electrónico": "correo",
        "correo electronico": "correo",
        "dirección": "direccion",
        "direccion": "direccion",
        "municipio": "ciudad",
        "departamento": "departamento",
    }

    @classmethod
    def consultar(
        cls,
        tipo_documento: str,
        numero: str,
    ) -> ResultadoDian:

        resultado = ResultadoDian(
            tipo_documento=tipo_documento,
            numero_documento=numero,
        )

        if not Configuracion.obtener(
            "dian",
            "consulta_publica",
        ):

            resultado.error = (
                "La consulta pública DIAN está deshabilitada."
            )

            return resultado

        url = Configuracion.obtener(
            "dian",
            "url_muisca",
        )

        if not url:

            resultado.error = (
                "No está configurada la URL de MUISCA."
            )

            return resultado

        timeout = Configuracion.obtener(
            "dian",
            "timeout_segundos",
        ) or 30

        numero_limpio = re.sub(
            r"\D",
            "",
            str(numero),
        )

        if len(numero_limpio) < 5:

            resultado.error = (
                "El documento debe tener al menos 5 dígitos."
            )

            return resultado

        session = cls._crear_sesion()

        try:

            cls._precalentar_sesion(
                session,
                url,
                timeout,
            )

            pagina = session.get(
                url,
                timeout=timeout,
            )

            pagina.raise_for_status()

            if cls._es_mantenimiento(
                pagina,
            ):

                resultado.error = cls._mensaje_mantenimiento()

                return resultado

            if not cls._es_html(
                pagina,
            ):

                resultado.error = (
                    "La DIAN no entregó la página de consulta RUT. "
                    "Verifique su conexión e intente nuevamente."
                )

                return resultado

            payload = cls._construir_payload(
                pagina.text,
                numero_limpio,
            )

            if payload is None:

                resultado.error = (
                    "No fue posible preparar la consulta RUT en MUISCA."
                )

                return resultado

            respuesta = session.post(
                url,
                data=payload,
                timeout=timeout,
                headers={
                    "Referer": url,
                    "Origin": cls._origen(
                        url,
                    ),
                    "Content-Type": (
                        "application/x-www-form-urlencoded"
                    ),
                },
            )

            respuesta.raise_for_status()

            if cls._es_mantenimiento(
                respuesta,
            ):

                resultado.error = cls._mensaje_mantenimiento()

                return resultado

            if not cls._es_html(
                respuesta,
            ):

                resultado.error = (
                    "La DIAN no respondió con datos del RUT."
                )

                return resultado

        except requests.RequestException as error:

            resultado.error = (
                f"No fue posible consultar RUT en DIAN: {error}"
            )

            return resultado

        cls._interpretar_respuesta(
            respuesta.text,
            resultado,
        )

        if cls._tiene_datos(
            resultado,
        ):

            resultado.encontrado = True
            resultado.origen = "DIAN"
            resultado.mensaje = (
                "Datos obtenidos desde consulta pública "
                "DIAN (RUT/MUISCA)."
            )

        return resultado

    @classmethod
    def _crear_sesion(
        cls,
    ) -> requests.Session:

        session = requests.Session()

        session.headers.update(
            {
                "User-Agent": (
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/122.0.0.0 Safari/537.36"
                ),
                "Accept": (
                    "text/html,application/xhtml+xml,"
                    "application/xml;q=0.9,image/avif,"
                    "image/webp,image/apng,*/*;q=0.8"
                ),
                "Accept-Language": "es-CO,es;q=0.9",
                "Cache-Control": "no-cache",
                "Pragma": "no-cache",
            }
        )

        return session

    @staticmethod
    def _origen(
        url: str,
    ) -> str:

        coincidencia = re.match(
            r"(https?://[^/]+)",
            url,
        )

        if coincidencia is None:

            return "https://muisca.dian.gov.co"

        return coincidencia.group(
            1,
        )

    @classmethod
    def _precalentar_sesion(
        cls,
        session: requests.Session,
        url: str,
        timeout: int,
    ) -> None:

        origen = cls._origen(
            url,
        )

        try:

            session.get(
                f"{origen}/",
                timeout=timeout,
            )

        except requests.RequestException:

            return

    @staticmethod
    def _mensaje_mantenimiento() -> str:

        return (
            "La consulta pública RUT de la DIAN está temporalmente "
            "fuera de servicio (mantenimiento). "
            "Consulte manualmente en "
            "https://muisca.dian.gov.co/WebRutMuisca/"
            "DefConsultaEstadoRUT.faces "
            "o complete los datos del tercero manualmente."
        )

    @staticmethod
    def _es_mantenimiento(
        respuesta: requests.Response,
    ) -> bool:

        contenido = respuesta.headers.get(
            "content-type",
            "",
        ).lower()

        if "image/jpeg" in contenido or "image/jpg" in contenido:

            return True

        url = str(
            respuesta.url,
        ).lower()

        return "mantenimiento" in url

    @staticmethod
    def _es_html(
        respuesta: requests.Response,
    ) -> bool:

        contenido = respuesta.headers.get(
            "content-type",
            "",
        ).lower()

        if "html" in contenido:

            return True

        if "text" in contenido:

            return True

        muestra = respuesta.text[:200].lower()

        return (
            "<html" in muestra
            or "<!doctype" in muestra
        )

    @classmethod
    def _construir_payload(
        cls,
        html: str,
        numero: str,
    ) -> dict | None:

        payload = cls._extraer_campos_ocultos(
            html,
        )

        viewstate = cls._extraer_viewstate(
            html,
        )

        if viewstate:

            payload[
                "javax.faces.ViewState"
            ] = viewstate

        if "javax.faces.ViewState" not in payload:

            return None

        payload[
            f"{cls.PREFIJO}numNit"
        ] = numero

        boton = cls._extraer_boton_buscar(
            html,
        )

        if boton is None:

            payload[
                f"{cls.PREFIJO}btnBuscar"
            ] = "Buscar"

        else:

            payload[
                boton["name"]
            ] = boton["value"]

        return payload

    @classmethod
    def _extraer_campos_ocultos(
        cls,
        html: str,
    ) -> dict:

        payload = {}

        for etiqueta in re.findall(
            r"<input[^>]+>",
            html,
            flags=re.IGNORECASE,
        ):

            tipo = re.search(
                r'type=["\']([^"\']+)["\']',
                etiqueta,
                flags=re.IGNORECASE,
            )

            if (
                tipo is None
                or tipo.group(
                    1,
                ).lower()
                != "hidden"
            ):

                continue

            nombre = re.search(
                r'name=["\']([^"\']+)["\']',
                etiqueta,
                flags=re.IGNORECASE,
            )

            if nombre is None:

                continue

            valor = re.search(
                r'value=["\']([^"\']*)["\']',
                etiqueta,
                flags=re.IGNORECASE,
            )

            payload[
                nombre.group(
                    1,
                )
            ] = (
                valor.group(
                    1,
                )
                if valor
                else ""
            )

        return payload

    @staticmethod
    def _extraer_viewstate(
        html: str,
    ) -> str:

        coincidencia = re.search(
            r'name="javax\.faces\.ViewState"[^>]*value="([^"]+)"',
            html,
            flags=re.IGNORECASE,
        )

        if coincidencia is None:

            coincidencia = re.search(
                r'id="javax\.faces\.ViewState"[^>]*value="([^"]+)"',
                html,
                flags=re.IGNORECASE,
            )

        if coincidencia is None:

            return ""

        return coincidencia.group(
            1,
        )

    @classmethod
    def _extraer_boton_buscar(
        cls,
        html: str,
    ) -> dict | None:

        for etiqueta in re.findall(
            r"<input[^>]+>",
            html,
            flags=re.IGNORECASE,
        ):

            if re.search(
                r'type=["\']submit["\']',
                etiqueta,
                flags=re.IGNORECASE,
            ) is None:

                continue

            nombre = re.search(
                r'name=["\']([^"\']+)["\']',
                etiqueta,
                flags=re.IGNORECASE,
            )

            if nombre is None:

                continue

            if "btnbuscar" not in nombre.group(
                1,
            ).lower():

                continue

            valor = re.search(
                r'value=["\']([^"\']*)["\']',
                etiqueta,
                flags=re.IGNORECASE,
            )

            return {
                "name": nombre.group(
                    1,
                ),
                "value": (
                    valor.group(
                        1,
                    )
                    if valor
                    else "Buscar"
                ),
            }

        return None

    @classmethod
    def _interpretar_respuesta(
        cls,
        html: str,
        resultado: ResultadoDian,
    ) -> None:

        texto = BeautifulSoup(
            html,
            "html.parser",
        ).get_text(
            " ",
            strip=True,
        ).lower()

        if cls._es_no_encontrado(
            html,
            texto,
        ):

            return

        cls._extraer_campos_jsf(
            html,
            resultado,
        )

        cls._extraer_tablas(
            BeautifulSoup(
                html,
                "html.parser",
            ),
            resultado,
        )

        cls._extraer_etiquetas(
            BeautifulSoup(
                html,
                "html.parser",
            ),
            resultado,
        )

        if (
            resultado.primer_nombre
            or resultado.primer_apellido
        ) and not resultado.razon_social:

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

    @staticmethod
    def _es_no_encontrado(
        html: str,
        texto: str,
    ) -> bool:

        if (
            "eldivscroll" in html.lower()
            and any(
                mensaje in texto
                for mensaje in (
                    "no se encontr",
                    "no existe",
                    "no registra",
                )
            )
        ):

            return True

        return any(
            mensaje in texto
            for mensaje in (
                "no se encontr",
                "no existe en las bases",
                "no registra información",
                "no hay informaci",
            )
        )

    @classmethod
    def _extraer_campos_jsf(
        cls,
        html: str,
        resultado: ResultadoDian,
    ) -> None:

        for origen, destino in cls.CAMPOS_RESULTADO.items():

            valor = cls._extraer_valor_elemento(
                html,
                f"{cls.PREFIJO}{origen}",
            )

            if not valor:

                continue

            actual = getattr(
                resultado,
                destino,
            )

            if actual:

                continue

            setattr(
                resultado,
                destino,
                valor,
            )

    @staticmethod
    def _extraer_valor_elemento(
        html: str,
        element_id: str,
    ) -> str:

        id_escapado = re.escape(
            element_id,
        )

        patrones = (
            rf'id="{id_escapado}"[^>]*>([^<]+)<',
            rf'id="{id_escapado}"[^>]*value="([^"]*)"',
            rf'id="{id_escapado}"[^>]*>(.*?)</span>',
            rf'id="{id_escapado}"[^>]*>(.*?)</td>',
        )

        for patron in patrones:

            coincidencia = re.search(
                patron,
                html,
                flags=re.IGNORECASE
                | re.DOTALL,
            )

            if coincidencia is None:

                continue

            valor = BeautifulSoup(
                coincidencia.group(
                    1,
                ),
                "html.parser",
            ).get_text(
                " ",
                strip=True,
            )

            if valor:

                return valor

        return ""

    @classmethod
    def _extraer_tablas(
        cls,
        soup: BeautifulSoup,
        resultado: ResultadoDian,
    ) -> None:

        for tabla in soup.find_all("table"):

            for fila in tabla.find_all("tr"):

                celdas = fila.find_all(
                    ["td", "th"]
                )

                if len(celdas) < 2:

                    continue

                etiqueta = celdas[0].get_text(
                    " ",
                    strip=True,
                ).lower()

                valor = celdas[1].get_text(
                    " ",
                    strip=True,
                )

                cls._asignar_valor(
                    resultado,
                    etiqueta,
                    valor,
                )

    @classmethod
    def _extraer_etiquetas(
        cls,
        soup: BeautifulSoup,
        resultado: ResultadoDian,
    ) -> None:

        for etiqueta in soup.find_all(
            ["label", "span", "td"]
        ):

            texto = etiqueta.get_text(
                " ",
                strip=True,
            )

            if ":" not in texto:

                continue

            clave, _, valor = texto.partition(":")

            cls._asignar_valor(
                resultado,
                clave.strip().lower(),
                valor.strip(),
            )

    @classmethod
    def _asignar_valor(
        cls,
        resultado: ResultadoDian,
        etiqueta: str,
        valor: str,
    ) -> None:

        if not valor:

            return

        etiqueta = etiqueta.strip().lower()

        destino = cls.ETIQUETAS.get(
            etiqueta,
        )

        if destino is None:

            return

        actual = getattr(
            resultado,
            destino,
        )

        if actual:

            return

        setattr(
            resultado,
            destino,
            valor,
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
