from aplicacion.comunes.servicio_base import ServicioBase

from .repositorio import RepositorioImpuesto


class ServicioImpuesto(ServicioBase):

    repositorio = RepositorioImpuesto

    @classmethod
    def validar(
        cls,
        datos,
        id_registro=None,
    ):

        codigo = str(
            datos.get(
                "codigo",
                "",
            )
        ).strip()

        nombre = str(
            datos.get(
                "nombre",
                "",
            )
        ).strip()

        if not codigo:

            raise ValueError(
                "El código es obligatorio.",
            )

        if not nombre:

            raise ValueError(
                "El nombre es obligatorio.",
            )

        if cls.repositorio.existe_codigo(
            codigo.upper(),
            id_registro,
        ):

            raise ValueError(
                "Ya existe un impuesto con ese código.",
            )

        datos["codigo"] = codigo.upper()
        datos["nombre"] = nombre

        try:

            datos["porcentaje"] = float(
                datos.get(
                    "porcentaje",
                    0,
                )
                or 0,
            )

        except (
            TypeError,
            ValueError,
        ):

            datos["porcentaje"] = 0.0

        tipo = str(
            datos.get(
                "tipo",
                "IVA",
            )
        ).strip()

        datos["tipo"] = tipo or "IVA"

    @classmethod
    def buscar(cls, texto):

        texto = texto.strip()

        if not texto:

            return cls.obtener_todos()

        return cls.repositorio.buscar(
            texto,
        )

    @classmethod
    def inicializar_predeterminados(cls):

        if cls.repositorio.contar() == 0:

            predeterminados = [
                {
                    "codigo": "IVA19",
                    "nombre": "IVA 19%",
                    "porcentaje": 19.0,
                    "tipo": "IVA",
                    "activo": True,
                },
                {
                    "codigo": "IVA5",
                    "nombre": "IVA 5%",
                    "porcentaje": 5.0,
                    "tipo": "IVA",
                    "activo": True,
                },
                {
                    "codigo": "EXE0",
                    "nombre": "IVA 0%",
                    "porcentaje": 0.0,
                    "tipo": "IVA",
                    "activo": True,
                },
            ]

            for datos in predeterminados:

                cls.guardar(datos)

        cls.inicializar_retenciones()

    @classmethod
    def inicializar_retenciones(cls):

        from aplicacion.maestros.impuestos.retenciones_catalogo import (
            TODAS_RETENCIONES,
        )

        for datos in TODAS_RETENCIONES:

            registro = {
                **datos,
                "activo": True,
            }

            if cls.repositorio.existe_codigo(
                registro["codigo"],
            ):

                continue

            cls.guardar(registro)
