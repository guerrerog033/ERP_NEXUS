class Cache:

    _datos = {}

    @classmethod
    def guardar(
        cls,
        clave,
        valor
    ):

        cls._datos[clave] = valor

    @classmethod
    def obtener(
        cls,
        clave,
        defecto=None
    ):

        return cls._datos.get(
            clave,
            defecto
        )

    @classmethod
    def eliminar(
        cls,
        clave
    ):

        cls._datos.pop(
            clave,
            None
        )

    @classmethod
    def limpiar(cls):

        cls._datos.clear()