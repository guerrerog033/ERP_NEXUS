from aplicacion.comunes.repositorio_base import RepositorioBase
from aplicacion.maestros.empresas.modelos import Empresa


class EmpresaRepositorio(RepositorioBase):

    modelo = Empresa

    @classmethod
    def obtener_por_nit(cls, nit):

        db = cls.obtener_sesion()

        try:

            return (
                db.query(cls.modelo)
                .filter(
                    cls.modelo.nit == nit
                )
                .first()
            )

        finally:

            db.close()