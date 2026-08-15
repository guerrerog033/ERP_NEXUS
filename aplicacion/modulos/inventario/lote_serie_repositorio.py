from aplicacion.base_datos.conexion import SessionLocal
from aplicacion.comunes.repositorio_base import RepositorioBase

from .modelos import ExistenciaLoteSerie, LoteSerie


class LoteSerieRepositorio(RepositorioBase):

    modelo = LoteSerie

    @classmethod
    def listar_por_producto(cls, producto_id: int) -> list:

        db = SessionLocal()

        try:

            return (
                db.query(LoteSerie)
                .filter(
                    LoteSerie.producto_id == producto_id,
                )
                .order_by(
                    LoteSerie.numero,
                )
                .all()
            )

        finally:

            db.close()

    @classmethod
    def existe_numero(
        cls,
        producto_id: int,
        numero: str,
        excluir_id: int | None = None,
    ) -> bool:

        db = SessionLocal()

        try:

            consulta = db.query(LoteSerie).filter(
                LoteSerie.producto_id == producto_id,
                LoteSerie.numero == numero,
            )

            if excluir_id is not None:

                consulta = consulta.filter(
                    LoteSerie.id != excluir_id,
                )

            return consulta.first() is not None

        finally:

            db.close()


class ExistenciaLoteSerieRepositorio(RepositorioBase):

    modelo = ExistenciaLoteSerie

    @classmethod
    def obtener(
        cls,
        bodega_id: int,
        lote_serie_id: int,
    ):

        db = SessionLocal()

        try:

            return (
                db.query(ExistenciaLoteSerie)
                .filter(
                    ExistenciaLoteSerie.bodega_id == bodega_id,
                    ExistenciaLoteSerie.lote_serie_id
                    == lote_serie_id,
                )
                .first()
            )

        finally:

            db.close()

    @classmethod
    def listar_por_lote(cls, lote_serie_id: int) -> list:

        db = SessionLocal()

        try:

            return (
                db.query(ExistenciaLoteSerie)
                .filter(
                    ExistenciaLoteSerie.lote_serie_id
                    == lote_serie_id,
                )
                .all()
            )

        finally:

            db.close()

    @classmethod
    def total_por_lote(cls, lote_serie_id: int) -> float:

        db = SessionLocal()

        try:

            filas = (
                db.query(
                    ExistenciaLoteSerie.cantidad,
                )
                .filter(
                    ExistenciaLoteSerie.lote_serie_id
                    == lote_serie_id,
                )
                .all()
            )

            return sum(
                float(fila[0] or 0)
                for fila in filas
            )

        finally:

            db.close()

    @classmethod
    def ajustar(
        cls,
        bodega_id: int,
        lote_serie_id: int,
        cantidad: float,
        *,
        sumar: bool,
    ) -> None:
        """
        Crea o actualiza la fila de existencia (bodega, lote/serie)
        sumando o restando ``cantidad``. Lanza ValueError si una
        salida dejaría la existencia en negativo.
        """

        db = SessionLocal()

        try:

            existencia = (
                db.query(ExistenciaLoteSerie)
                .filter(
                    ExistenciaLoteSerie.bodega_id == bodega_id,
                    ExistenciaLoteSerie.lote_serie_id
                    == lote_serie_id,
                )
                .with_for_update()
                .first()
            )

            if existencia is None:

                if not sumar:

                    raise ValueError(
                        "No hay existencia de ese lote/serie "
                        "en esta bodega.",
                    )

                existencia = ExistenciaLoteSerie(
                    bodega_id=bodega_id,
                    lote_serie_id=lote_serie_id,
                    cantidad=0,
                )

                db.add(existencia)

                db.flush()

            actual = float(existencia.cantidad or 0)

            nueva = (
                actual + cantidad
                if sumar
                else actual - cantidad
            )

            if nueva < 0:

                raise ValueError(
                    "La existencia de ese lote/serie en esta "
                    f"bodega quedaría negativa ({nueva:g}).",
                )

            existencia.cantidad = nueva

            db.commit()

        except Exception:

            db.rollback()

            raise

        finally:

            db.close()
