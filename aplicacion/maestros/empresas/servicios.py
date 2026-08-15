from aplicacion.comunes.servicio_base import ServicioBase
from aplicacion.maestros.empresas.repositorio import EmpresaRepositorio


class EmpresaServicio(ServicioBase):

    repositorio = EmpresaRepositorio

    @classmethod
    def validar(cls, datos, id_registro=None):

        nit = datos["nit"].strip()

        if not nit:
            raise Exception(
                "El NIT es obligatorio."
            )

        razon = datos["razon_social"].strip()

        if not razon:
            raise Exception(
                "La razón social es obligatoria."
            )

        empresa = cls.repositorio.obtener_por_nit(
            nit
        )

        # Nuevo registro
        if id_registro is None:

            if empresa is not None:

                raise Exception(
                    "Ya existe una empresa con ese NIT."
                )

            return

        # Edición

        if (
            empresa is not None
            and empresa.id != id_registro
        ):

            raise Exception(
                "Ya existe otra empresa con ese NIT."
            )