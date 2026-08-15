from __future__ import annotations

from dataclasses import dataclass, field

from sqlalchemy.orm import joinedload

from aplicacion.base_datos.conexion import SessionLocal
from aplicacion.modulos.compras.facturas.modelos import (
    FacturaCompra,
    FacturaCompraDetalle,
)
from aplicacion.modulos.compras.facturas.repositorio import (
    RepositorioFacturaCompra,
)
from aplicacion.modulos.compras.ordenes.modelos import (
    OrdenCompra,
    OrdenCompraDetalle,
    RecepcionCompra,
    RecepcionCompraDetalle,
)
from aplicacion.nucleo.configuracion import Configuracion


@dataclass
class ResultadoMatchCompra:

    estado: str = "sin_vinculo"
    mensaje: str = ""
    diferencias: list[str] = field(
        default_factory=list,
    )


class ServicioIntegracionCompras:
    """
    Emparejamiento OC ↔ recepción ↔ factura de compra.
    """

    @classmethod
    def _obtener_factura(
        cls,
        factura_id: int,
    ):

        from aplicacion.modulos.compras.facturas.servicios import (
            ServicioFacturaCompra,
        )

        return ServicioFacturaCompra.obtener_completa(
            factura_id,
        )

    @classmethod
    def _config(
        cls,
        clave: str,
        defecto=False,
    ):

        return Configuracion.obtener(
            "compras",
            clave,
            defecto,
        )

    @classmethod
    def inventario_en_recepcion(
        cls,
    ) -> bool:

        return bool(
            cls._config(
                "inventario_en_recepcion",
                True,
            ),
        )

    @classmethod
    def radian_031_en_recepcion(
        cls,
    ) -> bool:

        return bool(
            cls._config(
                "radian_031_en_recepcion",
                True,
            ),
        )

    @classmethod
    def sugerir_ordenes(
        cls,
        factura_id: int,
    ) -> list[dict]:

        factura = cls._obtener_factura(
            factura_id,
        )

        if (
            factura is None
            or not factura.proveedor_id
        ):

            return []

        db = SessionLocal()

        try:

            ordenes = (
                db.query(OrdenCompra)
                .options(
                    joinedload(
                        OrdenCompra.detalles,
                    ),
                )
                .filter(
                    OrdenCompra.proveedor_id
                    == factura.proveedor_id,
                    OrdenCompra.activo.is_(
                        True,
                    ),
                    OrdenCompra.estado.in_(
                        (
                            "pendiente",
                            "parcial",
                            "recibida",
                        ),
                    ),
                )
                .order_by(
                    OrdenCompra.fecha.desc(),
                    OrdenCompra.numero.desc(),
                )
                .limit(20)
                .all()
            )

            return [
                {
                    "id": orden.id,
                    "numero": orden.numero,
                    "fecha": orden.fecha,
                    "total": float(
                        orden.total or 0,
                    ),
                    "estado": orden.estado,
                }
                for orden in ordenes
            ]

        finally:

            db.close()

    @classmethod
    def vincular_orden(
        cls,
        factura_id: int,
        orden_id: int,
    ) -> ResultadoMatchCompra:

        factura = cls._obtener_factura(
            factura_id,
        )

        if factura is None:

            raise ValueError(
                "Factura no encontrada.",
            )

        db = SessionLocal()

        try:

            orden = (
                db.query(OrdenCompra)
                .options(
                    joinedload(
                        OrdenCompra.detalles,
                    ),
                )
                .filter(
                    OrdenCompra.id == orden_id,
                )
                .first()
            )

            if orden is None:

                raise ValueError(
                    "Orden de compra no encontrada.",
                )

            if (
                factura.proveedor_id
                and orden.proveedor_id
                != factura.proveedor_id
            ):

                raise ValueError(
                    "La orden pertenece a otro proveedor.",
                )

            detalle_map = cls._emparejar_lineas(
                list(
                    factura.detalles or [],
                ),
                list(
                    orden.detalles or [],
                ),
            )

            RepositorioFacturaCompra.vincular_orden_compra(
                factura_id,
                orden_id,
                detalle_map,
            )

        finally:

            db.close()

        return cls.evaluar_match(
            factura_id,
            persistir=True,
        )

    @classmethod
    def _emparejar_lineas(
        cls,
        detalles_factura,
        detalles_orden,
    ) -> dict[int, int]:

        mapa: dict[int, int] = {}
        usados: set[int] = set()

        for detalle in detalles_factura:

            if not detalle.producto_id:

                continue

            for orden_detalle in detalles_orden:

                if orden_detalle.id in usados:

                    continue

                if (
                    orden_detalle.producto_id
                    != detalle.producto_id
                ):

                    continue

                variante_fc = getattr(
                    detalle,
                    "producto_variante_id",
                    None,
                )

                variante_oc = (
                    orden_detalle.producto_variante_id
                )

                if (
                    variante_fc
                    and variante_oc
                    and variante_fc != variante_oc
                ):

                    continue

                mapa[detalle.id] = orden_detalle.id
                usados.add(
                    orden_detalle.id,
                )

                break

        return mapa

    @classmethod
    def evaluar_match(
        cls,
        factura_id: int,
        *,
        persistir: bool = False,
    ) -> ResultadoMatchCompra:

        factura = cls._obtener_factura(
            factura_id,
        )

        if factura is None:

            return ResultadoMatchCompra(
                mensaje="Factura no encontrada.",
            )

        if not factura.orden_compra_id:

            resultado = ResultadoMatchCompra(
                estado="sin_vinculo",
                mensaje=(
                    "Sin orden de compra vinculada."
                ),
            )

            if persistir:

                RepositorioFacturaCompra.actualizar_match(
                    factura_id,
                    estado=resultado.estado,
                    mensaje=resultado.mensaje,
                )

            return resultado

        db = SessionLocal()

        try:

            orden = (
                db.query(OrdenCompra)
                .options(
                    joinedload(
                        OrdenCompra.detalles,
                    ),
                )
                .filter(
                    OrdenCompra.id
                    == factura.orden_compra_id,
                )
                .first()
            )

            if orden is None:

                resultado = ResultadoMatchCompra(
                    estado="error",
                    mensaje=(
                        "La orden vinculada no existe."
                    ),
                )

                if persistir:

                    RepositorioFacturaCompra.actualizar_match(
                        factura_id,
                        estado=resultado.estado,
                        mensaje=resultado.mensaje,
                    )

                return resultado

            diferencias: list[str] = []
            tolerancia = 1.0

            delta_total = abs(
                float(
                    factura.total or 0,
                )
                - float(
                    orden.total or 0,
                ),
            )

            if delta_total > tolerancia:

                diferencias.append(
                    f"Total factura "
                    f"{float(factura.total or 0):,.2f} "
                    f"vs OC "
                    f"{float(orden.total or 0):,.2f}.",
                )

            detalles_oc = {
                detalle.id: detalle
                for detalle in orden.detalles
            }

            for detalle in factura.detalles:

                if not detalle.producto_id:

                    continue

                orden_detalle_id = getattr(
                    detalle,
                    "orden_detalle_id",
                    None,
                )

                if not orden_detalle_id:

                    diferencias.append(
                        f"Línea sin emparejar: "
                        f"{detalle.descripcion}.",
                    )

                    continue

                orden_detalle = detalles_oc.get(
                    orden_detalle_id,
                )

                if orden_detalle is None:

                    continue

                cant_fc = float(
                    detalle.cantidad or 0,
                )

                cant_oc = float(
                    orden_detalle.cantidad or 0,
                )

                if cant_fc > cant_oc + 0.0001:

                    diferencias.append(
                        f"{detalle.descripcion}: "
                        f"cantidad factura {cant_fc:g} "
                        f"> pedido {cant_oc:g}.",
                    )

                recibida = float(
                    orden_detalle.cantidad_recibida
                    or 0,
                )

                if (
                    cls.inventario_en_recepcion()
                    and recibida + 0.0001 < cant_fc
                ):

                    diferencias.append(
                        f"{detalle.descripcion}: "
                        f"recibido {recibida:g} "
                        f"< facturado {cant_fc:g}.",
                    )

                costo_oc = float(
                    orden_detalle.costo_unitario
                    or 0,
                )

                costo_fc = float(
                    detalle.precio_unitario or 0,
                )

                if (
                    costo_oc > 0
                    and abs(
                        costo_fc - costo_oc,
                    )
                    > tolerancia
                ):

                    diferencias.append(
                        f"{detalle.descripcion}: "
                        f"costo factura {costo_fc:,.2f} "
                        f"vs OC {costo_oc:,.2f}.",
                    )

            if diferencias:

                resultado = ResultadoMatchCompra(
                    estado="diferencia",
                    mensaje=(
                        f"{len(diferencias)} "
                        "diferencia(s) detectada(s)."
                    ),
                    diferencias=diferencias,
                )

            else:

                resultado = ResultadoMatchCompra(
                    estado="ok",
                    mensaje=(
                        "Factura alineada con la orden "
                        "de compra."
                    ),
                )

            if persistir:

                RepositorioFacturaCompra.actualizar_match(
                    factura_id,
                    estado=resultado.estado,
                    mensaje=resultado.mensaje,
                )

                if (
                    resultado.estado
                    == "diferencia"
                    and cls._config(
                        "exigir_match_oc",
                        False,
                    )
                ):

                    RepositorioFacturaCompra.actualizar_estado(
                        factura_id,
                        "pendiente_revision",
                    )

            return resultado

        finally:

            db.close()

    @classmethod
    def auto_vincular_orden(
        cls,
        factura_id: int,
    ) -> bool:

        if not cls._config(
            "auto_vincular_orden",
            True,
        ):

            return False

        factura = cls._obtener_factura(
            factura_id,
        )

        if (
            factura is None
            or factura.orden_compra_id
        ):

            return False

        sugerencias = cls.sugerir_ordenes(
            factura_id,
        )

        if len(sugerencias) != 1:

            return False

        cls.vincular_orden(
            factura_id,
            sugerencias[0]["id"],
        )

        return True

    @classmethod
    def omitir_inventario_linea(
        cls,
        db,
        factura,
        detalle,
    ) -> bool:

        if not cls.inventario_en_recepcion():

            return False

        orden_id = getattr(
            factura,
            "orden_compra_id",
            None,
        )

        if not orden_id:

            return False

        cantidad = float(
            detalle.cantidad or 0,
        )

        if cantidad <= 0:

            return False

        orden_detalle_id = getattr(
            detalle,
            "orden_detalle_id",
            None,
        )

        if orden_detalle_id:

            orden_detalle = (
                db.query(
                    OrdenCompraDetalle,
                )
                .filter(
                    OrdenCompraDetalle.id
                    == orden_detalle_id,
                )
                .first()
            )

            if orden_detalle is None:

                return False

            recibida = float(
                orden_detalle.cantidad_recibida
                or 0,
            )

            return recibida + 0.0001 >= cantidad

        if not detalle.producto_id:

            return False

        recibida = cls._cantidad_recibida_producto(
            db,
            orden_id,
            detalle.producto_id,
            getattr(
                detalle,
                "producto_variante_id",
                None,
            ),
        )

        return recibida + 0.0001 >= cantidad

    @classmethod
    def _cantidad_recibida_producto(
        cls,
        db,
        orden_id: int,
        producto_id: int,
        producto_variante_id,
    ) -> float:

        consulta = (
            db.query(
                RecepcionCompraDetalle,
            )
            .join(
                RecepcionCompra,
                RecepcionCompraDetalle.recepcion_id
                == RecepcionCompra.id,
            )
            .filter(
                RecepcionCompra.orden_id
                == orden_id,
                RecepcionCompra.activo.is_(
                    True,
                ),
                RecepcionCompraDetalle.producto_id
                == producto_id,
            )
        )

        if producto_variante_id:

            consulta = consulta.filter(
                RecepcionCompraDetalle.producto_variante_id
                == producto_variante_id,
            )

        else:

            consulta = consulta.filter(
                RecepcionCompraDetalle.producto_variante_id.is_(
                    None,
                ),
            )

        total = 0.0

        for detalle in consulta.all():

            total += float(
                detalle.cantidad or 0,
            )

        return total

    @classmethod
    def procesar_radian_tras_recepcion(
        cls,
        orden_id: int,
    ) -> list[str]:

        if not cls.radian_031_en_recepcion():

            return []

        db = SessionLocal()

        try:

            facturas = (
                db.query(
                    FacturaCompra,
                )
                .filter(
                    FacturaCompra.orden_compra_id
                    == orden_id,
                    FacturaCompra.activo.is_(
                        True,
                    ),
                    FacturaCompra.cufe.isnot(
                        None,
                    ),
                    FacturaCompra.contabilizado.is_(
                        False,
                    ),
                )
                .all()
            )

        finally:

            db.close()

        mensajes: list[str] = []

        from aplicacion.integraciones.dian.servicio_eventos_radian import (
            ServicioEventosRadian,
        )

        for factura in facturas:

            if (
                factura.evento_radian_codigo
                == "031"
                and factura.evento_radian_cude
            ):

                continue

            resultado = ServicioEventosRadian.procesar(
                factura.id,
                "031",
            )

            if resultado.exito:

                mensajes.append(
                    f"RADIAN 031 enviado para "
                    f"{factura.numero}.",
                )

            elif resultado.error:

                mensajes.append(
                    f"{factura.numero}: "
                    f"{resultado.error}",
                )

        return mensajes

    @classmethod
    def validar_contabilizacion(
        cls,
        factura,
    ) -> None:

        if not getattr(
            factura,
            "orden_compra_id",
            None,
        ):

            return

        if not cls._config(
            "exigir_match_oc_contabilizar",
            False,
        ):

            return

        match = cls.evaluar_match(
            factura.id,
        )

        if match.estado != "ok":

            raise ValueError(
                match.mensaje
                or "La factura no coincide con "
                "la orden de compra vinculada.",
            )
