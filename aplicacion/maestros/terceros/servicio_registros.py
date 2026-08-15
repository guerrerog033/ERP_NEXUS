from __future__ import annotations

from .repositorio import (
    TerceroContactoRepositorio,
    TerceroCuentaBancariaRepositorio,
    TerceroDireccionRepositorio,
)


class ServicioRegistroTercero:
    """
    Base para los servicios de registros hijos de un tercero
    (direcciones, contactos, cuentas bancarias): mismo CRUD, más
    la regla de que solo puede haber un registro "principal" por
    tercero.
    """

    repositorio = None

    campos_obligatorios: tuple[str, ...] = ()

    @classmethod
    def listar(
        cls,
        tercero_id: int,
    ) -> list:

        return cls.repositorio.listar_por_tercero(
            tercero_id,
        )

    @classmethod
    def guardar(
        cls,
        datos: dict,
    ):

        cls._validar(
            datos,
        )

        if datos.get(
            "principal",
        ):

            cls.repositorio.limpiar_principal(
                datos["tercero_id"],
            )

        return cls.repositorio.guardar(
            datos,
        )

    @classmethod
    def actualizar(
        cls,
        id_registro: int,
        datos: dict,
    ):

        cls._validar(
            datos,
        )

        if datos.get(
            "principal",
        ):

            cls.repositorio.limpiar_principal(
                datos["tercero_id"],
                excluir_id=id_registro,
            )

        return cls.repositorio.actualizar(
            id_registro,
            datos,
        )

    @classmethod
    def eliminar(
        cls,
        id_registro: int,
    ) -> None:

        cls.repositorio.eliminar(
            id_registro,
        )

    @classmethod
    def _validar(
        cls,
        datos: dict,
    ) -> None:

        if not datos.get(
            "tercero_id",
        ):

            raise ValueError(
                "Falta el tercero al que pertenece el registro.",
            )

        for campo in cls.campos_obligatorios:

            if not str(
                datos.get(
                    campo,
                    "",
                )
                or "",
            ).strip():

                raise ValueError(
                    f"El campo '{campo}' es obligatorio.",
                )


class ServicioDireccionTercero(ServicioRegistroTercero):

    repositorio = TerceroDireccionRepositorio

    campos_obligatorios = ("direccion",)


class ServicioContactoTercero(ServicioRegistroTercero):

    repositorio = TerceroContactoRepositorio

    campos_obligatorios = ("nombre",)


class ServicioCuentaBancariaTercero(ServicioRegistroTercero):

    repositorio = TerceroCuentaBancariaRepositorio

    campos_obligatorios = (
        "banco",
        "numero_cuenta",
    )
