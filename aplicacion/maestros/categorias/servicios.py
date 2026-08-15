from aplicacion.comunes.servicio_base import ServicioBase
from aplicacion.maestros.categorias.repositorio import (
    RepositorioCategoria,
)


class ServicioCategoria(ServicioBase):

    repositorio = RepositorioCategoria

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
                "El código es obligatorio."
            )

        if not nombre:

            raise ValueError(
                "El nombre es obligatorio."
            )

        if cls.repositorio.existe_codigo(
            codigo.upper(),
            id_registro,
        ):

            raise ValueError(
                "Ya existe una categoría con ese código."
            )

        datos["codigo"] = codigo.upper()
        datos["nombre"] = nombre

        descripcion = datos.get(
            "descripcion",
            "",
        )

        datos["descripcion"] = str(
            descripcion
        ).strip()

    @classmethod
    def buscar(cls, texto):

        texto = texto.strip()

        if not texto:

            return cls.obtener_todos()

        return cls.repositorio.buscar(
            texto
        )
