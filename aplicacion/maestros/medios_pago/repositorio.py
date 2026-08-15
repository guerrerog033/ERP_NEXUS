from aplicacion.comunes.repositorio_base import RepositorioBase

from .modelos import MedioPago


class MedioPagoRepositorio(RepositorioBase):

    modelo = MedioPago
