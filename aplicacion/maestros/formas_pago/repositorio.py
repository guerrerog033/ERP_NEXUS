from aplicacion.comunes.repositorio_base import RepositorioBase

from .modelos import FormaPago


class FormaPagoRepositorio(RepositorioBase):

    modelo = FormaPago
