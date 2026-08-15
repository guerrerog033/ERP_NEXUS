class Sesion:

    _usuario = None
    _empresa = None
    _sucursal = None
    _periodo = None

    @classmethod
    def iniciar(
        cls,
        usuario,
        empresa=None,
        sucursal=None,
        periodo=None,
    ):

        cls._usuario = usuario
        cls._empresa = empresa
        cls._sucursal = sucursal
        cls._periodo = periodo

    @classmethod
    def cerrar(cls):

        cls._usuario = None
        cls._empresa = None
        cls._sucursal = None
        cls._periodo = None

    @classmethod
    def usuario(cls):
        return cls._usuario

    @classmethod
    def empresa(cls):
        return cls._empresa

    @classmethod
    def sucursal(cls):
        return cls._sucursal

    @classmethod
    def periodo(cls):
        return cls._periodo

    @classmethod
    def hay_sesion(cls):
        return cls._usuario is not None