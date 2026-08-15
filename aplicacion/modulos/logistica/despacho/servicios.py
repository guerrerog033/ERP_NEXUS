from __future__ import annotations

from datetime import date

from aplicacion.base_datos.conexion import SessionLocal


class ServicioDespacho:

    PREFIJO = "DES"
    LONGITUD = 6

    ESTADOS = (
        "en_preparacion",
        "listo_despacho",
        "despachado",
        "en_ruta",
        "entregado",
        "parcial",
        "rechazado",
        "devuelto",
    )

    ESTADOS_EXIGEN_GUIA = (
        "entregado",
    )

    @classmethod
    def listar(cls) -> list[dict]:
        from aplicacion.modulos.logistica.despacho.modelos import (
            DespachoPedido,
        )
        from aplicacion.modulos.ventas.remisiones.modelos import (
            RemisionVenta,
        )

        db = SessionLocal()

        try:

            consulta = (
                db.query(
                    DespachoPedido,
                    RemisionVenta.numero.label(
                        "remision_numero",
                    ),
                )
                .outerjoin(
                    RemisionVenta,
                    DespachoPedido.remision_id
                    == RemisionVenta.id,
                )
                .filter(
                    DespachoPedido.activo.is_(
                        True,
                    ),
                )
                .order_by(
                    DespachoPedido.id.desc(),
                )
            )

            filas: list[dict] = []

            for despacho, remision_numero in consulta.all():

                filas.append(
                    {
                        "id": despacho.id,
                        "numero": despacho.numero,
                        "pedido_id": despacho.pedido_id,
                        "remision_id": despacho.remision_id,
                        "remision_numero": remision_numero,
                        "estado": despacho.estado,
                        "ciudad": despacho.ciudad,
                        "transportadora": (
                            despacho.transportadora
                        ),
                        "conductor": despacho.conductor,
                        "fecha_programada": (
                            despacho.fecha_programada
                        ),
                    },
                )

            return filas

        finally:

            db.close()

    @classmethod
    def generar_numero(cls) -> str:
        db = SessionLocal()

        try:
            from aplicacion.modulos.logistica.despacho.modelos import (
                DespachoPedido,
            )

            numeros = (
                db.query(DespachoPedido.numero)
                .filter(
                    DespachoPedido.numero.like(
                        f"{cls.PREFIJO}%",
                    )
                )
                .all()
            )

            maximo = 0

            for (numero,) in numeros:
                sufijo = numero[len(cls.PREFIJO):]

                if sufijo.isdigit():
                    maximo = max(
                        maximo,
                        int(sufijo),
                    )

            return (
                f"{cls.PREFIJO}"
                f"{maximo + 1:0{cls.LONGITUD}d}"
            )

        finally:
            db.close()

    @classmethod
    def _validar_guia_para_estado(
        cls,
        remision_id: int | None,
        estado: str,
    ) -> None:

        if estado not in cls.ESTADOS_EXIGEN_GUIA:

            return

        if remision_id is None:

            raise ValueError(
                "El despacho no está vinculado a una "
                "remisión interna.",
            )

        from aplicacion.modulos.ventas.guias_remision.servicios import (
            ServicioGuiaRemisionElectronica,
        )

        ServicioGuiaRemisionElectronica.validar_guia_emitida_remision(
            remision_id,
        )

    @classmethod
    def obtener_por_remision(
        cls,
        remision_id: int,
    ):
        from aplicacion.modulos.logistica.despacho.modelos import (
            DespachoPedido,
        )

        db = SessionLocal()

        try:

            return (
                db.query(DespachoPedido)
                .filter(
                    DespachoPedido.remision_id
                    == remision_id,
                    DespachoPedido.activo.is_(
                        True,
                    ),
                )
                .order_by(
                    DespachoPedido.id.desc(),
                )
                .first()
            )

        finally:

            db.close()

    @classmethod
    def crear_desde_pedido(
        cls,
        pedido_id: int,
        datos: dict,
    ):
        from aplicacion.modulos.logistica.despacho.modelos import (
            DespachoPedido,
        )

        db = SessionLocal()

        try:
            despacho = DespachoPedido(
                pedido_id=pedido_id,
                numero=cls.generar_numero(),
                **datos,
            )
            db.add(despacho)
            db.commit()
            db.refresh(despacho)

            return despacho

        finally:
            db.close()

    @classmethod
    def obtener_o_crear_por_remision(
        cls,
        remision_id: int,
    ):
        from aplicacion.modulos.logistica.despacho.modelos import (
            DespachoPedido,
        )
        from aplicacion.modulos.ventas.remisiones.servicios import (
            ServicioRemision,
        )

        existente = cls.obtener_por_remision(
            remision_id,
        )

        if existente is not None:

            return existente

        remision = ServicioRemision.obtener_completa(
            remision_id,
        )

        if remision is None:

            raise ValueError(
                "No se encontró la remisión interna.",
            )

        pedido_id = remision.pedido_id or 0

        if not pedido_id:

            raise ValueError(
                "La remisión no tiene pedido asociado "
                "para registrar el despacho.",
            )

        db = SessionLocal()

        try:

            despacho = DespachoPedido(
                pedido_id=pedido_id,
                remision_id=remision_id,
                numero=cls.generar_numero(),
                estado="despachado",
                fecha_programada=date.today(),
                observaciones=(
                    f"Despacho remisión interna "
                    f"{remision.numero}"
                ),
            )

            db.add(despacho)
            db.commit()
            db.refresh(despacho)

            return despacho

        finally:

            db.close()

    @classmethod
    def marcar_entregado_por_remision(
        cls,
        remision_id: int,
    ):
        from aplicacion.modulos.ventas.remisiones.servicios import (
            ServicioRemision,
        )
        from aplicacion.modulos.ventas.remisiones.repositorio import (
            RepositorioRemision,
        )

        remision = ServicioRemision.obtener_completa(
            remision_id,
        )

        if remision is None:

            raise ValueError(
                "No se encontró la remisión interna.",
            )

        if not remision.inventario_aplicado:

            raise ValueError(
                "Debe despachar la remisión interna "
                "(salida de inventario) antes de marcar entregado.",
            )

        if remision.estado == "entregada":

            raise ValueError(
                "La remisión ya fue marcada como entregada.",
            )

        cls._validar_guia_para_estado(
            remision_id,
            "entregado",
        )

        despacho = cls.obtener_o_crear_por_remision(
            remision_id,
        )

        cls.cambiar_estado(
            despacho.id,
            "entregado",
            omitir_validacion_guia=True,
        )

        return RepositorioRemision.actualizar_entrega(
            remision_id,
        )

    @classmethod
    def cambiar_estado(
        cls,
        despacho_id: int,
        estado: str,
        *,
        omitir_validacion_guia: bool = False,
    ) -> None:
        from aplicacion.modulos.logistica.despacho.modelos import (
            DespachoPedido,
        )

        if estado not in cls.ESTADOS:
            raise ValueError(
                f"Estado inválido: {estado}",
            )

        db = SessionLocal()

        try:
            despacho = (
                db.query(DespachoPedido)
                .filter(
                    DespachoPedido.id == despacho_id,
                )
                .first()
            )

            if despacho is None:
                raise ValueError(
                    "Despacho no encontrado.",
                )

            remision_id = despacho.remision_id

            if (
                remision_id is None
                and despacho.pedido_id
            ):
                from aplicacion.modulos.ventas.remisiones.repositorio import (
                    RepositorioRemision,
                )

                remision = (
                    RepositorioRemision
                    .obtener_por_pedido(
                        despacho.pedido_id,
                    )
                )

                if remision is not None:

                    remision_id = remision.id
                    despacho.remision_id = remision_id

            if (
                not omitir_validacion_guia
            ):

                cls._validar_guia_para_estado(
                    remision_id,
                    estado,
                )

            despacho.estado = estado
            db.commit()

        finally:
            db.close()

    @classmethod
    def verificar_alistamiento(
        cls,
        pedido_id: int,
    ) -> dict:
        from aplicacion.modulos.ventas.pedidos.modelos import (
            OrdenPedido,
        )

        db = SessionLocal()

        try:
            pedido = (
                db.query(OrdenPedido)
                .filter(
                    OrdenPedido.id == pedido_id,
                )
                .first()
            )

            if pedido is None:
                return {
                    "listo": False,
                    "motivo": "Pedido no encontrado.",
                }

            for detalle in pedido.detalles:
                if detalle.producto_id:
                    from aplicacion.maestros.productos.modelos import (
                        Producto,
                    )

                    producto = (
                        db.query(Producto)
                        .filter(
                            Producto.id
                            == detalle.producto_id,
                        )
                        .first()
                    )

                    if (
                        producto
                        and producto.existencia
                        < detalle.cantidad
                    ):
                        return {
                            "listo": False,
                            "motivo": (
                                f"Sin stock: "
                                f"{producto.nombre}"
                            ),
                        }

            return {
                "listo": True,
                "motivo": "Listo para despacho.",
            }

        finally:
            db.close()
