from __future__ import annotations

from datetime import date

from .lote_serie_repositorio import (
    ExistenciaLoteSerieRepositorio,
    LoteSerieRepositorio,
)


class ServicioLoteSerie:

    repositorio = LoteSerieRepositorio

    @classmethod
    def listar(cls, producto_id: int) -> list:
        """Alias de listar_por_producto (interfaz de ListaRegistrosWidget)."""

        return cls.repositorio.listar_por_producto(
            producto_id,
        )

    @classmethod
    def _validar(
        cls,
        datos: dict,
        id_registro: int | None = None,
    ) -> None:

        from aplicacion.maestros.productos.repositorio import (
            RepositorioProducto,
        )

        producto_id = datos.get("producto_id")

        if not producto_id:

            raise ValueError(
                "Falta el producto al que pertenece el "
                "lote/serie.",
            )

        producto = RepositorioProducto.obtener_por_id(
            producto_id,
        )

        if producto is None:

            raise ValueError(
                "El producto no existe.",
            )

        if not (
            producto.maneja_lote
            or producto.maneja_serie
        ):

            raise ValueError(
                "Este producto no está configurado para "
                "controlar existencia por lote ni por serie.",
            )

        tipo = str(
            datos.get(
                "tipo",
                "",
            )
            or (
                "lote"
                if producto.maneja_lote
                else "serie"
            ),
        ).strip().lower()

        if tipo not in (
            "lote",
            "serie",
        ):

            raise ValueError(
                "El tipo debe ser 'lote' o 'serie'.",
            )

        if tipo == "lote" and not producto.maneja_lote:

            raise ValueError(
                "Este producto no controla existencia por lote.",
            )

        if tipo == "serie" and not producto.maneja_serie:

            raise ValueError(
                "Este producto no controla existencia por "
                "número de serie.",
            )

        datos["tipo"] = tipo

        numero = str(
            datos.get(
                "numero",
                "",
            )
            or "",
        ).strip()

        if not numero:

            etiqueta = (
                "El número de lote"
                if tipo == "lote"
                else "El número de serie"
            )

            raise ValueError(
                f"{etiqueta} es obligatorio.",
            )

        datos["numero"] = numero

        if cls.repositorio.existe_numero(
            producto_id,
            numero,
            excluir_id=id_registro,
        ):

            raise ValueError(
                f"Ya existe un {tipo} '{numero}' para este "
                "producto.",
            )

        fecha_fab = datos.get(
            "fecha_fabricacion",
        )
        fecha_venc = datos.get(
            "fecha_vencimiento",
        )

        if (
            isinstance(fecha_fab, date)
            and isinstance(fecha_venc, date)
            and fecha_venc < fecha_fab
        ):

            raise ValueError(
                "La fecha de vencimiento no puede ser anterior "
                "a la fecha de fabricación.",
            )

    @classmethod
    def guardar(cls, datos: dict):

        cls._validar(
            datos,
        )

        return cls.repositorio.guardar(
            datos,
        )

    @classmethod
    def actualizar(cls, id_registro: int, datos: dict):

        cls._validar(
            datos,
            id_registro,
        )

        return cls.repositorio.actualizar(
            id_registro,
            datos,
        )

    @classmethod
    def eliminar(cls, id_registro: int) -> None:

        cls.repositorio.eliminar(
            id_registro,
        )

    @classmethod
    def existencia_total(cls, lote_serie_id: int) -> float:

        return ExistenciaLoteSerieRepositorio.total_por_lote(
            lote_serie_id,
        )

    @classmethod
    def registrar_movimiento(
        cls,
        *,
        lote_serie_id: int,
        bodega_id: int,
        cantidad: float,
        sumar: bool,
    ) -> None:
        """
        Ajusta la existencia de un lote/serie en una bodega. No
        toca ExistenciaBodega/MovimientoInventario — quien orquesta
        un movimiento de inventario completo (entrada, ajuste...)
        llama aquí además de su propia lógica, no al revés, para no
        acoplar el motor de inventario existente a lote/serie.
        """

        cantidad = float(
            cantidad or 0,
        )

        if cantidad <= 0:

            raise ValueError(
                "La cantidad debe ser mayor a cero.",
            )

        ExistenciaLoteSerieRepositorio.ajustar(
            bodega_id,
            lote_serie_id,
            cantidad,
            sumar=sumar,
        )
