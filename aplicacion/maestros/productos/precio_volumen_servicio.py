from __future__ import annotations

from .precio_volumen_repositorio import (
    ProductoPrecioVolumenRepositorio,
)


class ServicioPrecioVolumenProducto:
    """
    CRUD de los escalones de precio por volumen de un producto,
    más la resolución del precio vigente para una cantidad dada.
    """

    repositorio = ProductoPrecioVolumenRepositorio

    @classmethod
    def listar(
        cls,
        producto_id: int,
    ) -> list:

        return cls.repositorio.listar_por_producto(
            producto_id,
        )

    @classmethod
    def guardar(
        cls,
        datos: dict,
    ):

        cls._validar(datos)

        return cls.repositorio.guardar(datos)

    @classmethod
    def actualizar(
        cls,
        id_registro: int,
        datos: dict,
    ):

        cls._validar(datos)

        return cls.repositorio.actualizar(
            id_registro,
            datos,
        )

    @classmethod
    def eliminar(
        cls,
        id_registro: int,
    ) -> None:

        cls.repositorio.eliminar(id_registro)

    @classmethod
    def _validar(
        cls,
        datos: dict,
    ) -> None:

        if not datos.get("producto_id"):

            raise ValueError(
                "Falta el producto al que pertenece el escalón "
                "de precio.",
            )

        try:

            cantidad_minima = float(
                datos.get("cantidad_minima") or 0,
            )

        except (TypeError, ValueError):

            cantidad_minima = 0

        if cantidad_minima <= 0:

            raise ValueError(
                "La cantidad mínima debe ser mayor que cero.",
            )

        datos["cantidad_minima"] = cantidad_minima

        try:

            precio = float(
                datos.get("precio") or 0,
            )

        except (TypeError, ValueError):

            raise ValueError(
                "El precio debe ser un valor numérico.",
            ) from None

        if precio <= 0:

            raise ValueError(
                "El precio debe ser mayor que cero.",
            )

        datos["precio"] = precio

    @classmethod
    def precio_para_cantidad(
        cls,
        producto_id: int,
        cantidad: float,
        *,
        precio_base: float = 0,
    ) -> float | None:
        """
        Devuelve el precio vigente para ``cantidad`` unidades según
        los escalones de volumen configurados para el producto, o
        ``None`` si el producto no tiene ninguno definido (en ese
        caso no se debe alterar el precio que ya trae la línea).
        """

        escalones = cls.listar(producto_id)

        if not escalones:

            return None

        mejor = None

        for escalon in escalones:

            if float(escalon.cantidad_minima) <= float(
                cantidad or 0,
            ):

                mejor = escalon

        if mejor is None:

            return float(precio_base or 0)

        return float(mejor.precio)
