from aplicacion.comunes.repositorio_base import RepositorioBase

from .modelos import Vendedor


class VendedorRepositorio(RepositorioBase):

    modelo = Vendedor
