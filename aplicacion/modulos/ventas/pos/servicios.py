from __future__ import annotations

from datetime import date

from aplicacion.modulos.ventas.facturas.integracion import (
    IntegracionFacturaVenta,
)
from aplicacion.modulos.ventas.facturas.servicios import (
    ServicioFacturaVenta,
)
from aplicacion.modulos.ventas.pos.modelos import (
    PosVentaLog,
)
from aplicacion.nucleo.configuracion import Configuracion
from aplicacion.nucleo.sesion import Sesion
from aplicacion.modulos.ventas.pos.ticket import (
    imprimir_ticket_pos,
)


from aplicacion.modulos.ventas.pos.repositorio import (
    RepositorioPosCierreCaja,
    RepositorioPosVentaLog,
)


class ServicioPOSVenta:

    repositorio_log = RepositorioPosVentaLog

    repositorio_cierre = RepositorioPosCierreCaja

    @classmethod
    def facturar(
        cls,
        *,
        cliente_id: int,
        lineas: list[dict],
        emitir_dian: bool = False,
        recibido: float | None = None,
        cambio: float | None = None,
        metodo_pago: str = "efectivo",
        imprimir_ticket: bool = False,
        cliente_nombre: str = "",
        parent=None,
    ):

        if not cliente_id:

            raise ValueError(
                "Seleccione un cliente.",
            )

        if not lineas:

            raise ValueError(
                "Agregue al menos un producto.",
            )

        lineas_validas = ServicioFacturaVenta.validar_lineas(
            lineas,
        )

        bloqueantes, _avisos = cls.alertas_stock(
            lineas_validas,
        )

        if bloqueantes:

            raise ValueError(
                "\n".join(
                    bloqueantes,
                ),
            )

        secuencia = (
            ServicioFacturaVenta.repositorio.siguiente_secuencia(
                ServicioFacturaVenta._prefijo(),
            )
        )

        cabecera = {
            "numero": ServicioFacturaVenta.generar_numero(),
            "prefijo": Configuracion.obtener(
                "dian",
                "prefijo_factura",
            )
            or "SETP",
            "consecutivo_dian": str(
                secuencia,
            ),
            "fecha": date.today(),
            "cliente_id": cliente_id,
            "observaciones": "Venta POS",
            "estado": "borrador",
            "activo": True,
        }

        ServicioFacturaVenta._aplicar_resumen(
            cabecera,
            lineas_validas,
        )

        factura = ServicioFacturaVenta.repositorio.guardar_completa(
            cabecera,
            lineas_validas,
        )

        factura = IntegracionFacturaVenta.confirmar_venta(
            factura.id,
            emitir_dian=emitir_dian,
        )

        cls._registrar_log_pos(
            factura,
            recibido=recibido,
            cambio=cambio,
            metodo_pago=metodo_pago,
        )

        if imprimir_ticket:

            cls.imprimir_ticket_venta(
                factura=factura,
                lineas=lineas_validas,
                recibido=recibido,
                cambio=cambio,
                metodo_pago=metodo_pago,
                cliente_nombre=cliente_nombre,
                parent=parent,
            )

        return factura

    @classmethod
    def imprimir_ticket_venta(
        cls,
        *,
        factura,
        lineas: list[dict],
        recibido: float | None,
        cambio: float | None,
        metodo_pago: str,
        cliente_nombre: str = "",
        parent=None,
    ) -> bool:

        total = float(
            factura.total or 0,
        )

        if recibido is None:

            recibido = total

        if cambio is None:

            cambio = max(
                0.0,
                float(
                    recibido,
                )
                - total,
            )

        return imprimir_ticket_pos(
            factura_numero=str(
                factura.numero or "",
            ),
            cliente=cliente_nombre,
            lineas=lineas,
            total=total,
            recibido=float(
                recibido,
            ),
            cambio=float(
                cambio,
            ),
            metodo_pago=metodo_pago,
            usuario=(
                Sesion.usuario()
                or "sistema"
            ),
            parent=parent,
        )

    @classmethod
    def _registrar_log_pos(
        cls,
        factura,
        *,
        recibido: float | None,
        cambio: float | None,
        metodo_pago: str,
    ) -> None:

        from aplicacion.base_datos.conexion import (
            SessionLocal,
        )

        total = float(
            factura.total or 0,
        )

        if recibido is None:

            recibido = total

        if cambio is None:

            cambio = max(
                0.0,
                float(
                    recibido,
                )
                - total,
            )

        db = SessionLocal()

        try:

            db.add(
                PosVentaLog(
                    factura_id=factura.id,
                    total=total,
                    recibido=recibido,
                    cambio=cambio,
                    metodo_pago=metodo_pago,
                    usuario=(
                        Sesion.usuario()
                        or "sistema"
                    ),
                ),
            )

            db.commit()

        finally:

            db.close()

    @classmethod
    def listar_historial(
        cls,
        *,
        fecha_desde=None,
        fecha_hasta=None,
        metodo_pago: str | None = None,
        usuario: str | None = None,
        limite: int = 500,
    ) -> list[dict]:

        return cls.repositorio_log.listar_historial(
            fecha_desde=fecha_desde,
            fecha_hasta=fecha_hasta,
            metodo_pago=metodo_pago,
            usuario=usuario,
            limite=limite,
        )

    @classmethod
    def resumen_caja(
        cls,
        *,
        fecha=None,
    ) -> dict:

        return cls.repositorio_log.resumen_caja(
            fecha=fecha,
        )

    @classmethod
    def efectivo_esperado(
        cls,
        *,
        fecha=None,
    ) -> float:

        return cls.repositorio_log.efectivo_esperado(
            fecha=fecha,
        )

    @classmethod
    def obtener_cierre(
        cls,
        *,
        fecha=None,
    ) -> dict | None:

        dia = fecha or date.today()

        return cls.repositorio_cierre.obtener_por_fecha(
            dia,
        )

    @classmethod
    def cerrar_caja(
        cls,
        *,
        efectivo_contado: float,
        fecha=None,
        observaciones: str | None = None,
    ) -> dict:

        dia = fecha or date.today()

        resumen = cls.resumen_caja(
            fecha=dia,
        )

        esperado = cls.efectivo_esperado(
            fecha=dia,
        )

        return cls.repositorio_cierre.registrar(
            fecha=dia,
            usuario=(
                Sesion.usuario()
                or "sistema"
            ),
            efectivo_esperado=esperado,
            efectivo_contado=float(
                efectivo_contado,
            ),
            total_ventas=float(
                resumen.get(
                    "total",
                    0,
                )
                or 0,
            ),
            ventas_count=int(
                resumen.get(
                    "ventas",
                    0,
                )
                or 0,
            ),
            observaciones=observaciones,
        )

    @classmethod
    def alertas_stock(
        cls,
        lineas: list[dict],
    ) -> tuple[
        list[str],
        list[str],
    ]:

        from aplicacion.base_datos.conexion import (
            SessionLocal,
        )
        from aplicacion.maestros.productos.modelos import (
            Producto,
        )
        from aplicacion.modulos.inventario.servicios import (
            ServicioInventario,
        )

        umbral_default = float(
            Configuracion.obtener(
                "pos",
                "stock_minimo_default",
            )
            or 0,
        )

        bloqueantes: list[str] = []
        avisos: list[str] = []

        db = SessionLocal()

        try:

            bodega = ServicioInventario._bodega_operacion(
                db,
                contexto="pos",
            )

            for linea in lineas:

                producto_id = linea.get(
                    "producto_id",
                )

                if not producto_id:

                    continue

                producto = (
                    db.query(
                        Producto,
                    )
                    .filter(
                        Producto.id
                        == producto_id,
                    )
                    .first()
                )

                if producto is None:

                    continue

                variante_id = linea.get(
                    "producto_variante_id",
                )

                cantidad = float(
                    linea.get(
                        "cantidad",
                    )
                    or 0,
                )

                existencia, _variante = (
                    ServicioInventario._obtener_existencia(
                        db,
                        producto,
                        variante_id,
                        bodega_id=bodega.id,
                    )
                )

                descripcion = str(
                    linea.get(
                        "descripcion",
                    )
                    or producto.nombre
                    or "Producto",
                )

                if existencia < cantidad:

                    bloqueantes.append(
                        (
                            f"{descripcion}: stock insuficiente "
                            f"(disponible {existencia:g}, "
                            f"solicitado {cantidad:g})."
                        ),
                    )

                    continue

                minimo = float(
                    getattr(
                        producto,
                        "stock_minimo",
                        0,
                    )
                    or 0,
                )

                if minimo <= 0:

                    minimo = umbral_default

                if (
                    minimo > 0
                    and (
                        existencia - cantidad
                    )
                    < minimo
                ):

                    avisos.append(
                        (
                            f"{descripcion}: quedará bajo el mínimo "
                            f"({minimo:g})."
                        ),
                    )

        finally:

            db.close()

        return bloqueantes, avisos

    @classmethod
    def reimprimir_ticket(
        cls,
        log_id: int,
        parent=None,
    ) -> bool:

        log = cls.repositorio_log.obtener_log_por_id(
            log_id,
        )

        if log is None:

            raise ValueError(
                "Venta POS no encontrada.",
            )

        factura = ServicioFacturaVenta.obtener_completa(
            log["factura_id"],
        )

        if factura is None:

            raise ValueError(
                "Factura no encontrada.",
            )

        lineas = []

        for detalle in factura.detalles:

            lineas.append(
                {
                    "descripcion": detalle.descripcion,
                    "cantidad": float(
                        detalle.cantidad or 0,
                    ),
                    "precio_unitario": float(
                        detalle.precio_unitario or 0,
                    ),
                    "total_linea": float(
                        detalle.total_linea or 0,
                    ),
                },
            )

        cliente_nombre = ""

        if factura.cliente_id:

            from aplicacion.maestros.terceros.repositorio import (
                TerceroRepositorio,
            )

            tercero = TerceroRepositorio.obtener_por_id(
                factura.cliente_id,
            )

            if tercero is not None:

                cliente_nombre = str(
                    tercero.nombre_completo
                    or "",
                )

        return cls.imprimir_ticket_venta(
            factura=factura,
            lineas=lineas,
            recibido=log["recibido"],
            cambio=log["cambio"],
            metodo_pago=log["metodo_pago"],
            cliente_nombre=cliente_nombre,
            parent=parent,
        )

    @classmethod
    def devolver_venta(
        cls,
        *,
        factura_id: int | None = None,
        log_id: int | None = None,
        motivo: str = "Devolución POS",
        emitir_dian: bool = False,
    ):

        if log_id is not None:

            log = cls.repositorio_log.obtener_log_por_id(
                log_id,
            )

            if log is None:

                raise ValueError(
                    "Venta POS no encontrada.",
                )

            factura_id = log["factura_id"]

        if not factura_id:

            raise ValueError(
                "Indique la factura o el log POS.",
            )

        log_pos = cls.repositorio_log.obtener_log_por_factura(
            factura_id,
        )

        if log_pos is None:

            raise ValueError(
                "La factura no proviene de una venta POS.",
            )

        factura = ServicioFacturaVenta.obtener_completa(
            factura_id,
        )

        if factura is None:

            raise ValueError(
                "No se encontró la factura.",
            )

        saldo = float(
            factura.saldo_pendiente or 0,
        )

        if saldo <= 0:

            raise ValueError(
                "La factura no tiene saldo pendiente "
                "para devolver.",
            )

        from aplicacion.modulos.ventas.notas_credito.integracion import (
            IntegracionNotaCreditoVenta,
        )
        from aplicacion.modulos.ventas.notas_credito.servicios import (
            ServicioNotaCreditoVenta,
        )

        nota = ServicioNotaCreditoVenta.crear_desde_factura(
            factura_id,
            motivo=motivo,
        )

        return IntegracionNotaCreditoVenta.confirmar_generacion(
            nota.id,
            emitir_dian=emitir_dian,
        )
