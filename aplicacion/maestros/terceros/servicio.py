from aplicacion.comunes.servicio_base import ServicioBase

from aplicacion.dominio.documentos.dv import DVCalculator
from aplicacion.dominio.documentos.validador import (
    ValidadorDocumento,
)

from .constantes import (
    CAMPOS_RESPONSABILIDAD_FISCAL,
    TIPO_A_ROL,
    TIPOS_TERCERO,
)
from .repositorio import TerceroRepositorio

from .documento.manager import DocumentoManager


class TerceroServicio(ServicioBase):

    repositorio = TerceroRepositorio

    entidad_auditoria = "Tercero"

    modulo_auditoria = "terceros"

    # ==================================================
    # Validación
    # ==================================================

    @classmethod
    def validar(
        cls,
        datos,
        id_registro=None,
    ):

        tipo_documento = str(
            datos.get(
                "tipo_documento",
                "",
            )
        ).strip().upper()

        numero_documento = str(
            datos.get(
                "numero_documento",
                "",
            )
        ).strip()

        tipo_tercero = str(
            datos.get(
                "tipo_tercero",
                "",
            )
        ).strip()

        if not tipo_documento:

            raise ValueError(
                "El tipo de documento es obligatorio."
            )

        if not numero_documento:

            raise ValueError(
                "El número de documento es obligatorio."
            )

        ValidadorDocumento.validar(
            tipo_documento,
            numero_documento,
        )

        if not tipo_tercero:

            raise ValueError(
                "El tipo de tercero es obligatorio."
            )

        if tipo_tercero not in TIPOS_TERCERO:

            raise ValueError(
                "El tipo de tercero debe ser Cliente, "
                "Proveedor, Empleado, Vendedor u Otro."
            )

        cls._sincronizar_roles(
            datos,
        )

        datos["tipo_documento"] = tipo_documento

        cls._validar_identificacion(
            datos,
        )

        cls._validar_contacto(
            datos,
        )

        cls._validar_condiciones_comerciales(
            datos,
        )

        cls._normalizar_responsabilidad_fiscal(
            datos,
        )

        existente = cls.repositorio.obtener_por_documento(
            tipo_documento,
            datos["numero_documento"],
        )

        if existente is None:

            return

        if (
            id_registro is not None
            and existente.id == id_registro
        ):

            return

        raise ValueError(
            "Ya existe un tercero con ese documento."
        )

    @classmethod
    def _validar_identificacion(
        cls,
        datos,
    ):

        tipo_documento = datos["tipo_documento"]
        numero = datos["numero_documento"]

        if tipo_documento == "NIT":

            nit = "".join(
                caracter
                for caracter in numero
                if caracter.isdigit()
            )

            if not nit:

                raise ValueError(
                    "El NIT debe contener dígitos.",
                )

            datos["numero_documento"] = nit

            razon_social = str(
                datos.get(
                    "razon_social",
                    "",
                )
                or "",
            ).strip()

            if not razon_social:

                raise ValueError(
                    "Para NIT debe indicar la razón social.",
                )

            datos["razon_social"] = razon_social

            dv = str(
                datos.get(
                    "dv",
                    "",
                )
                or "",
            ).strip()

            dv_calculado = DVCalculator.calcular(
                nit,
            )

            if (
                dv
                and dv != dv_calculado
            ):

                raise ValueError(
                    "El dígito de verificación no coincide "
                    f"con el NIT (esperado {dv_calculado}).",
                )

            datos["dv"] = (
                dv or dv_calculado
            )

            return

        datos["numero_documento"] = numero.strip()
        datos["dv"] = ""

        razon_social = str(
            datos.get(
                "razon_social",
                "",
            )
            or "",
        ).strip()

        primer_nombre = str(
            datos.get(
                "primer_nombre",
                "",
            )
            or "",
        ).strip()

        primer_apellido = str(
            datos.get(
                "primer_apellido",
                "",
            )
            or "",
        ).strip()

        if (
            not razon_social
            and (
                not primer_nombre
                or not primer_apellido
            )
        ):

            raise ValueError(
                "Indique razón social o primer nombre "
                "y primer apellido.",
            )

        datos["razon_social"] = razon_social
        datos["primer_nombre"] = primer_nombre
        datos["primer_apellido"] = primer_apellido

    @classmethod
    def _validar_contacto(
        cls,
        datos,
    ):

        for campo in (
            "direccion",
            "ciudad",
            "departamento",
            "telefono",
            "celular",
        ):

            datos[campo] = str(
                datos.get(
                    campo,
                    "",
                )
                or "",
            ).strip()

        pais = str(
            datos.get(
                "pais",
                "",
            )
            or "",
        ).strip()

        datos["pais"] = (
            pais or "Colombia"
        )

        correo = str(
            datos.get(
                "correo",
                "",
            )
            or "",
        ).strip()

        if (
            correo
            and "@" not in correo
        ):

            raise ValueError(
                "El correo electrónico no es válido.",
            )

        datos["correo"] = correo.lower()

    @classmethod
    def _validar_condiciones_comerciales(
        cls,
        datos,
    ):

        try:

            dias_credito = int(
                datos.get(
                    "dias_credito",
                    0,
                )
                or 0,
            )

        except (
            TypeError,
            ValueError,
        ):

            dias_credito = 0

        if dias_credito < 0:

            raise ValueError(
                "Los días de crédito no pueden ser negativos.",
            )

        try:

            cupo_credito = float(
                datos.get(
                    "cupo_credito",
                    0,
                )
                or 0,
            )

        except (
            TypeError,
            ValueError,
        ):

            cupo_credito = 0.0

        if cupo_credito < 0:

            raise ValueError(
                "El cupo de crédito no puede ser negativo.",
            )

        datos["dias_credito"] = dias_credito
        datos["cupo_credito"] = cupo_credito

        vendedor = str(
            datos.get(
                "vendedor_asignado",
                "",
            )
            or "",
        ).strip()

        datos["vendedor_asignado"] = vendedor

    @classmethod
    def _sincronizar_roles(
        cls,
        datos,
    ):

        tipo = str(
            datos.get(
                "tipo_tercero",
                "",
            )
        ).strip()

        campo_rol = TIPO_A_ROL.get(
            tipo,
        )

        if campo_rol:

            datos[campo_rol] = True

    @classmethod
    def _normalizar_responsabilidad_fiscal(
        cls,
        datos,
    ):

        seleccionados = [
            campo
            for campo in CAMPOS_RESPONSABILIDAD_FISCAL
            if datos.get(
                campo,
            )
        ]

        if not seleccionados:

            datos["resp_r99_pn"] = True

            for campo in CAMPOS_RESPONSABILIDAD_FISCAL:

                if campo != "resp_r99_pn":

                    datos[campo] = False

    @classmethod
    def listar(
        cls,
        **kwargs,
    ):

        pagina = kwargs.get(
            "pagina",
        )

        por_pagina = kwargs.get(
            "por_pagina",
            0,
        )

        if (
            pagina
            and por_pagina
        ):

            return cls.repositorio.consultar(
                pagina=pagina,
                por_pagina=por_pagina,
                filtros=kwargs.get(
                    "filtros",
                ),
                tipo_tercero=kwargs.get(
                    "tipo_tercero",
                ),
            )

        return cls.listar_filtrado(
            kwargs.get(
                "tipo_tercero",
            ),
        )

    @classmethod
    def listar_filtrado(
        cls,
        tipo_tercero=None,
    ):

        if tipo_tercero:

            return cls.repositorio.obtener_por_tipo(
                tipo_tercero,
            )

        return cls.obtener_todos()

    @classmethod
    def buscar(
        cls,
        texto,
        tipo_tercero=None,
        **kwargs,
    ):

        texto = str(
            texto
        ).strip()

        pagina = kwargs.get(
            "pagina",
        )

        por_pagina = kwargs.get(
            "por_pagina",
            0,
        )

        tipo = (
            tipo_tercero
            or kwargs.get(
                "tipo_tercero",
            )
        )

        if (
            pagina
            and por_pagina
        ):

            return cls.repositorio.consultar(
                pagina=pagina,
                por_pagina=por_pagina,
                filtros=kwargs.get(
                    "filtros",
                ),
                texto=texto or None,
                tipo_tercero=tipo,
            )

        if not texto:

            return cls.listar_filtrado(
                tipo,
            )

        return cls.repositorio.buscar(
            texto,
            tipo,
        )

    # ==================================================
    # Documento
    # ==================================================

    @classmethod
    def documento_changed(
        cls,
        tipo_documento,
        numero_documento,
    ):

        return DocumentoManager.buscar(

            tipo_documento,

            numero_documento,

        )
