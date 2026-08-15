from aplicacion.comunes.servicio_base import ServicioBase

from .repositorio import RepositorioListaPrecio


class ServicioListaPrecio(ServicioBase):

    repositorio = RepositorioListaPrecio

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
                "Ya existe una lista con ese código.",
            )

        datos["codigo"] = codigo.upper()
        datos["nombre"] = nombre
        datos["predeterminada"] = bool(
            datos.get(
                "predeterminada",
                False,
            )
        )

    @classmethod
    def buscar(cls, texto):

        texto = texto.strip()

        if not texto:

            return cls.obtener_todos()

        return cls.repositorio.buscar(
            texto,
        )

    @classmethod
    def obtener_predeterminada(cls):

        lista = cls.repositorio.obtener_predeterminada()

        if lista is not None:

            return lista

        cls.inicializar_predeterminados()

        return cls.repositorio.obtener_predeterminada()

    @classmethod
    def inicializar_predeterminados(cls):

        if cls.repositorio.contar() > 0:

            predeterminada = (
                cls.repositorio.obtener_predeterminada()
            )

            if predeterminada is None:

                listas = cls.obtener_todos()

                if listas:

                    cls.actualizar(
                        listas[0].id,
                        {
                            "predeterminada": True,
                        },
                    )

            return

        cls.guardar(
            {
                "codigo": "PUBLICO",
                "nombre": "Público",
                "predeterminada": True,
                "activo": True,
            }
        )

        cls.guardar(
            {
                "codigo": "MAYOR",
                "nombre": "Mayorista",
                "predeterminada": False,
                "activo": True,
            }
        )
