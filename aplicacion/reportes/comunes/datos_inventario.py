from __future__ import annotations

from datetime import date, datetime

from aplicacion.modulos.inventario.bodegas.servicios import (
    ServicioBodega,
)
from aplicacion.modulos.ventas.cotizaciones.formatos_impresion import (
    _unidad_producto,
)


def _formatear_fecha(
    valor,
) -> str:

    if valor is None:

        return ""

    if isinstance(
        valor,
        datetime,
    ):

        return valor.strftime(
            "%d/%m/%Y %H:%M",
        )

    if isinstance(
        valor,
        date,
    ):

        return valor.strftime(
            "%d/%m/%Y",
        )

    return str(
        valor,
    )


def _etiqueta_bodega(
    bodega_id,
) -> str:

    if not bodega_id:

        return ""

    bodega = ServicioBodega.obtener_por_id(
        bodega_id,
    )

    if bodega is None:

        return str(
            bodega_id,
        )

    return (
        f"{bodega.codigo} - {bodega.nombre}"
    )


def _linea_producto_movimiento(
    movimiento,
    indice: int,
) -> dict:

    from aplicacion.maestros.productos.servicios import (
        ServicioProducto,
    )

    producto = None

    if getattr(
        movimiento,
        "producto_id",
        None,
    ):

        producto = ServicioProducto.obtener_por_id(
            movimiento.producto_id,
        )

    codigo = ""

    descripcion = ""

    if producto is not None:

        codigo = str(
            producto.codigo or "",
        )

        descripcion = str(
            producto.nombre or "",
        )

    variante_id = getattr(
        movimiento,
        "producto_variante_id",
        None,
    )

    if variante_id:

        from aplicacion.maestros.productos.repositorio import (
            RepositorioProducto,
        )

        variante = RepositorioProducto.obtener_variante_por_id(
            variante_id,
        )

        if variante is not None:

            codigo = str(
                variante.codigo
                or codigo,
            )

            etiqueta = ServicioProducto._etiqueta_variante(
                variante,
                incluir_stock=False,
            )

            if etiqueta:

                descripcion = (
                    f"{descripcion} ({etiqueta})"
                    if descripcion
                    else etiqueta
                )

    cantidad = float(
        getattr(
            movimiento,
            "cantidad",
            0,
        )
        or 0,
    )

    costo = float(
        getattr(
            movimiento,
            "costo_unitario",
            0,
        )
        or 0,
    )

    return {
        "numero": indice,
        "codigo": codigo,
        "descripcion": descripcion
        or str(
            getattr(
                movimiento,
                "observaciones",
                "",
            )
            or "Producto",
        ),
        "cantidad": cantidad,
        "unidad": _unidad_producto(
            getattr(
                movimiento,
                "producto_id",
                None,
            ),
        ),
        "costo": costo,
        "total": cantidad * costo,
    }


def _resolver_referencia_texto(
    referencia: str,
    referencia_id,
) -> str:

    referencia = str(
        referencia or "",
    ).strip()

    if not referencia:

        return ""

    if referencia_id in (
        None,
        "",
    ):

        return referencia.replace(
            "_",
            " ",
        ).title()

    from aplicacion.base_datos.conexion import (
        SessionLocal,
    )

    db = SessionLocal()

    try:

        if referencia == "remision_venta":

            from aplicacion.modulos.ventas.remisiones.modelos import (
                RemisionVenta,
            )

            doc = db.query(
                RemisionVenta,
            ).filter(
                RemisionVenta.id
                == referencia_id,
            ).first()

            if doc is not None:

                return f"Remisión {doc.numero}"

        if referencia == "factura_venta":

            from aplicacion.modulos.ventas.facturas.modelos import (
                FacturaVenta,
            )

            doc = db.query(
                FacturaVenta,
            ).filter(
                FacturaVenta.id
                == referencia_id,
            ).first()

            if doc is not None:

                return f"Factura {doc.numero}"

        if referencia == "factura_compra":

            from aplicacion.modulos.compras.facturas.modelos import (
                FacturaCompra,
            )

            doc = db.query(
                FacturaCompra,
            ).filter(
                FacturaCompra.id
                == referencia_id,
            ).first()

            if doc is not None:

                return f"Factura compra {doc.numero}"

        if referencia == "recepcion_compra":

            from aplicacion.modulos.compras.ordenes.modelos import (
                RecepcionCompra,
            )

            doc = db.query(
                RecepcionCompra,
            ).filter(
                RecepcionCompra.id
                == referencia_id,
            ).first()

            if doc is not None:

                return f"Recepción {doc.numero}"

        if referencia == "nota_credito_venta":

            from aplicacion.modulos.ventas.notas_credito.modelos import (
                NotaCreditoVenta,
            )

            doc = db.query(
                NotaCreditoVenta,
            ).filter(
                NotaCreditoVenta.id
                == referencia_id,
            ).first()

            if doc is not None:

                return f"Nota crédito {doc.numero}"

        if referencia == "nota_credito_compra":

            from aplicacion.modulos.compras.notas_credito.modelos import (
                NotaCreditoCompra,
            )

            doc = db.query(
                NotaCreditoCompra,
            ).filter(
                NotaCreditoCompra.id
                == referencia_id,
            ).first()

            if doc is not None:

                return f"Nota crédito compra {doc.numero}"

        if referencia == "traslado":

            destino = _etiqueta_bodega(
                referencia_id,
            )

            if destino:

                return f"Traslado → {destino}"

        if referencia == "ajuste":

            return "Ajuste manual"

    finally:

        db.close()

    return (
        f"{referencia.replace('_', ' ').title()} "
        f"#{referencia_id}"
    )


def movimientos_inventario_a_dto(
    movimientos,
    *,
    prefijo_numero: str = "MOV",
) -> dict:

    if not movimientos:

        raise ValueError(
            "Se requiere al menos un movimiento.",
        )

    if not isinstance(
        movimientos,
        list,
    ):

        movimientos = [
            movimientos,
        ]

    primero = movimientos[0]

    movimiento_id = getattr(
        primero,
        "id",
        0,
    ) or 0

    observaciones = str(
        getattr(
            primero,
            "observaciones",
            "",
        )
        or "",
    ).strip()

    referencia = _resolver_referencia_texto(
        getattr(
            primero,
            "referencia",
            "",
        ),
        getattr(
            primero,
            "referencia_id",
            None,
        ),
    )

    return {
        "numero": (
            f"{prefijo_numero}-"
            f"{int(movimiento_id):06d}"
        ),
        "fecha": _formatear_fecha(
            getattr(
                primero,
                "fecha",
                None,
            ),
        ),
        "bodega": _etiqueta_bodega(
            getattr(
                primero,
                "bodega_id",
                None,
            ),
        ),
        "tipo": str(
            getattr(
                primero,
                "tipo",
                "",
            )
            or "",
        ),
        "referencia": referencia,
        "observaciones": observaciones,
        "items": [
            _linea_producto_movimiento(
                movimiento,
                indice,
            )
            for indice, movimiento in enumerate(
                movimientos,
                start=1,
            )
        ],
    }


def entrada_inventario_a_dto(
    movimientos,
) -> dict:

    return movimientos_inventario_a_dto(
        movimientos,
        prefijo_numero="ENT",
    )


def salida_inventario_a_dto(
    movimientos,
) -> dict:

    return movimientos_inventario_a_dto(
        movimientos,
        prefijo_numero="SAL",
    )


def ajuste_inventario_a_dto(
    movimiento,
) -> dict:

    dto = movimientos_inventario_a_dto(
        movimiento,
        prefijo_numero="AJU",
    )

    tipo = str(
        dto.get(
            "tipo",
            "",
        )
        or "",
    ).title()

    dto["tipo_ajuste"] = tipo

    return dto


def traslado_inventario_a_dto(
    salida,
    entrada,
) -> dict:

    salida_id = getattr(
        salida,
        "id",
        0,
    ) or 0

    return {
        "numero": f"TR-{int(salida_id):06d}",
        "fecha": _formatear_fecha(
            getattr(
                salida,
                "fecha",
                None,
            )
            or getattr(
                entrada,
                "fecha",
                None,
            ),
        ),
        "bodega_origen": _etiqueta_bodega(
            getattr(
                salida,
                "bodega_id",
                None,
            ),
        ),
        "bodega_destino": _etiqueta_bodega(
            getattr(
                entrada,
                "bodega_id",
                None,
            ),
        ),
        "observaciones": str(
            getattr(
                salida,
                "observaciones",
                "",
            )
            or getattr(
                entrada,
                "observaciones",
                "",
            )
            or "",
        ).strip(),
        "items": [
            _linea_producto_movimiento(
                salida,
                1,
            ),
        ],
    }


def kardex_inventario_a_dto(
    filas: list[dict],
    *,
    numero: str,
    subtitulo: str,
) -> dict:

    columnas = [
        "Fecha",
        "Bodega",
        "Código",
        "Producto",
        "Variante",
        "Tipo",
        "Cantidad",
        "Costo",
        "Referencia",
        "Saldo",
    ]

    filas_pdf: list[list[str]] = []

    for fila in filas:

        filas_pdf.append(
            [
                _formatear_fecha(
                    fila.get(
                        "fecha",
                    ),
                ),
                str(
                    fila.get(
                        "bodega",
                        "",
                    )
                    or "",
                ),
                str(
                    fila.get(
                        "codigo",
                        "",
                    )
                    or "",
                ),
                str(
                    fila.get(
                        "producto",
                        "",
                    )
                    or "",
                ),
                str(
                    fila.get(
                        "variante",
                        "",
                    )
                    or "",
                ),
                str(
                    fila.get(
                        "tipo",
                        "",
                    )
                    or "",
                ),
                f"{float(fila.get('cantidad', 0) or 0):,.2f}",
                f"{float(fila.get('costo_unitario', 0) or 0):,.2f}",
                str(
                    fila.get(
                        "referencia",
                        "",
                    )
                    or "",
                ),
                f"{float(fila.get('saldo', 0) or 0):,.2f}",
            ],
        )

    return {
        "titulo": "KARDEX DE INVENTARIO",
        "numero": numero,
        "subtitulo": subtitulo,
        "columnas": columnas,
        "filas": filas_pdf,
    }
