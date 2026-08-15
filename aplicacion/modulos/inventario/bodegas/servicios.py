from aplicacion.comunes.servicio_base import ServicioBase

from .repositorio import RepositorioBodega


class ServicioBodega(ServicioBase):

    repositorio = RepositorioBodega

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
                "Ya existe una bodega con ese código.",
            )

        datos["codigo"] = codigo.upper()
        datos["nombre"] = nombre

    @classmethod
    def buscar(cls, texto):

        texto = texto.strip()

        if not texto:

            return cls.obtener_todos()

        return cls.repositorio.buscar(
            texto,
        )

    @classmethod
    def listar_activas(cls):

        return cls.repositorio.obtener_activas()
