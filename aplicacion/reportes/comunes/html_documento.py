"""Puente HTML comercial: DTOs canónicos → plantillas de vista previa."""

from __future__ import annotations

from aplicacion.framework.reportes.plantilla_comercial import (
    html_documento_comercial,
)
from aplicacion.recursos.estilos import colores


def _formatear_moneda(
    valor,
) -> str:

    return f"${float(valor or 0):,.2f}"


def dto_a_cliente_html(
    cliente: dict,
) -> dict:

    nombre = str(
        cliente.get(
            "nombre",
            "",
        )
        or "",
    ).strip()

    documento = str(
        cliente.get(
            "documento",
            "",
        )
        or cliente.get(
            "nit",
            "",
        )
        or "",
    ).strip()

    return {
        "nombre": nombre,
        "nit": documento,
        "contacto": nombre,
        "direccion": str(
            cliente.get(
                "direccion",
                "",
            )
            or "No aplica",
        ).strip(),
        "ciudad": str(
            cliente.get(
                "ciudad",
                "",
            )
            or "",
        ).strip(),
        "telefono": str(
            cliente.get(
                "telefono",
                "",
            )
            or "",
        ).strip(),
        "correo": str(
            cliente.get(
                "correo",
                "",
            )
            or "",
        ).strip(),
    }


def dto_a_empresa_html(
    empresa: dict,
) -> dict:

    return {
        "nombre": (
            empresa.get(
                "razon_social",
            )
            or empresa.get(
                "nombre",
                "",
            )
            or ""
        ),
        "nit": str(
            empresa.get(
                "nit",
                "",
            )
            or "",
        ),
        "direccion": str(
            empresa.get(
                "direccion",
                "",
            )
            or "",
        ),
        "telefono": str(
            empresa.get(
                "telefono",
                "",
            )
            or "",
        ),
        "correo": str(
            empresa.get(
                "correo",
                "",
            )
            or "",
        ),
        "ciudad": str(
            empresa.get(
                "ciudad",
                "",
            )
            or "",
        ),
        "pais": str(
            empresa.get(
                "pais",
                "Colombia",
            )
            or "Colombia",
        ),
        "notas_pie": str(
            empresa.get(
                "notas_pie",
                "",
            )
            or "",
        ),
        "vendedor_nombre": str(
            empresa.get(
                "vendedor_nombre",
                "",
            )
            or "",
        ),
        "vendedor_correo": str(
            empresa.get(
                "vendedor_correo",
                "",
            )
            or "",
        ),
        "vendedor_telefono": str(
            empresa.get(
                "vendedor_telefono",
                "",
            )
            or "",
        ),
        "logo_ruta": str(
            empresa.get(
                "logo_ruta",
                "",
            )
            or empresa.get(
                "logo",
                "",
            )
            or "",
        ),
    }


def dto_a_resumen_html(
    dto: dict,
) -> dict:

    return {
        "subtotal": float(
            dto.get(
                "subtotal",
                0,
            )
            or 0,
        ),
        "iva": float(
            dto.get(
                "impuestos",
                dto.get(
                    "iva",
                    0,
                ),
            )
            or 0,
        ),
        "total": float(
            dto.get(
                "total",
                0,
            )
            or 0,
        ),
        "retefuente": float(
            dto.get(
                "retefuente",
                0,
            )
            or 0,
        ),
        "reteica": float(
            dto.get(
                "reteica",
                0,
            )
            or 0,
        ),
        "reteiva": float(
            dto.get(
                "reteiva",
                0,
            )
            or 0,
        ),
    }


def contexto_formato_desde_dto(
    dto: dict,
    *,
    documento,
    detalles,
    nombre_cliente: str,
    resumen: dict | None = None,
    empresa: dict | None = None,
    fecha: str = "",
    observaciones: str = "",
    etiqueta_documento: str = "DOCUMENTO",
    titulo_documento: str = "Documento",
    info_adicional: str = "",
    mostrar_imagenes: bool = True,
):

    from aplicacion.modulos.ventas.cotizaciones.formatos_impresion import (
        ContextoFormato,
    )
    from aplicacion.reportes.comunes.datos_documento import (
        empresa_reporte,
    )

    if empresa is None:

        empresa = empresa_reporte()

    if resumen is None:

        resumen = dto_a_resumen_html(
            dto,
        )

    if not fecha:

        fecha = str(
            dto.get(
                "fecha",
                "",
            )
            or dto.get(
                "fecha_generacion",
                "",
            )
            or "",
        )

    if not observaciones:

        observaciones = str(
            dto.get(
                "observaciones",
                "",
            )
            or "",
        ).strip()

    return ContextoFormato(
        cotizacion=documento,
        detalles=detalles,
        nombre_cliente=nombre_cliente,
        resumen=resumen,
        empresa=dto_a_empresa_html(
            empresa,
        ),
        cliente=dto_a_cliente_html(
            dto.get(
                "cliente",
                {},
            ),
        ),
        fecha=fecha,
        observaciones=observaciones,
        etiqueta_documento=etiqueta_documento,
        titulo_documento=titulo_documento,
        info_adicional=info_adicional,
        mostrar_imagenes=mostrar_imagenes,
    )


def filas_tabla_items_comerciales(
    items: list[dict],
) -> str:

    filas = ""

    for indice, item in enumerate(
        items,
        start=1,
    ):

        descripcion = str(
            item.get(
                "descripcion",
                "",
            )
            or "",
        )

        cantidad = float(
            item.get(
                "cantidad",
                0,
            )
            or 0,
        )

        precio = float(
            item.get(
                "precio",
                item.get(
                    "precio_unitario",
                    0,
                ),
            )
            or 0,
        )

        total = float(
            item.get(
                "total",
                cantidad * precio,
            )
            or 0,
        )

        filas += (
            f"<tr>"
            f"<td style='padding:5px 6px;border:1px solid {colores.BORDER};'>"
            f"{indice}</td>"
            f"<td style='padding:5px 6px;border:1px solid {colores.BORDER};'>"
            f"{descripcion}</td>"
            f"<td style='padding:5px 6px;border:1px solid {colores.BORDER};"
            f"text-align:right;'>{cantidad:g}</td>"
            f"<td style='padding:5px 6px;border:1px solid {colores.BORDER};"
            f"text-align:right;'>{_formatear_moneda(precio)}</td>"
            f"<td style='padding:5px 6px;border:1px solid {colores.BORDER};"
            f"text-align:right;'>{_formatear_moneda(total)}</td>"
            f"</tr>"
        )

    return filas


def filas_tabla_logistica_html(
    items: list[dict],
) -> str:

    filas = ""

    for indice, item in enumerate(
        items,
        start=1,
    ):

        solicitada = float(
            item.get(
                "cantidad_solicitada",
                item.get(
                    "cantidad",
                    0,
                ),
            )
            or 0,
        )

        entregada = float(
            item.get(
                "cantidad_entregada",
                item.get(
                    "cantidad",
                    0,
                ),
            )
            or 0,
        )

        descripcion = str(
            item.get(
                "descripcion",
                "",
            )
            or "",
        )

        unidad = str(
            item.get(
                "unidad",
                "UND",
            )
            or "UND",
        )

        filas += (
            f"<tr>"
            f"<td style='padding:5px 6px;border:1px solid {colores.BORDER};'>"
            f"{indice}</td>"
            f"<td style='padding:5px 6px;border:1px solid {colores.BORDER};'>"
            f"{descripcion}</td>"
            f"<td style='padding:5px 6px;border:1px solid {colores.BORDER};"
            f"text-align:right;'>{solicitada:g}</td>"
            f"<td style='padding:5px 6px;border:1px solid {colores.BORDER};"
            f"text-align:right;'>{entregada:g}</td>"
            f"<td style='padding:5px 6px;border:1px solid {colores.BORDER};'>"
            f"{unidad}</td>"
            f"</tr>"
        )

    return filas


def filas_tabla_cartera_html(
    lineas: list[dict],
) -> str:

    filas = ""

    for linea in lineas:

        filas += (
            f"<tr>"
            f"<td style='padding:5px 6px;border:1px solid {colores.BORDER};'>"
            f"{linea.get('documento', '')}</td>"
            f"<td style='padding:5px 6px;border:1px solid {colores.BORDER};"
            f"text-align:right;'>{_formatear_moneda(linea.get('saldo_anterior', 0))}</td>"
            f"<td style='padding:5px 6px;border:1px solid {colores.BORDER};"
            f"text-align:right;'>{_formatear_moneda(linea.get('valor_aplicado', linea.get('valor', 0)))}</td>"
            f"<td style='padding:5px 6px;border:1px solid {colores.BORDER};"
            f"text-align:right;'>{_formatear_moneda(linea.get('saldo_restante', 0))}</td>"
            f"</tr>"
        )

    return filas


def html_comercial_desde_dto(
    dto: dict,
    *,
    titulo_documento: str,
    contraparte_titulo: str = "CLIENTE",
    meta_derecha: str = "",
    info_adicional: str = "",
    columnas_tabla: tuple[str, ...] | None = None,
    filas_tabla: str | None = None,
    empresa: dict | None = None,
) -> str:

    from aplicacion.reportes.comunes.datos_documento import (
        empresa_reporte,
    )

    if empresa is None:

        empresa = dto.get(
            "empresa",
        ) or empresa_reporte()

    cliente = dto.get(
        "cliente",
        {},
    )

    beneficiario = dto.get(
        "beneficiario",
        cliente,
    )

    items = dto.get(
        "items",
        [],
    )

    lineas = dto.get(
        "lineas",
        [],
    )

    if filas_tabla is None:

        if lineas:

            filas_tabla = filas_tabla_cartera_html(
                lineas,
            )

            if columnas_tabla is None:

                columnas_tabla = (
                    "Documento",
                    "Saldo anterior",
                    "Aplicado",
                    "Saldo restante",
                )

        else:

            filas_tabla = filas_tabla_items_comerciales(
                items,
            )

            if columnas_tabla is None:

                columnas_tabla = (
                    "#",
                    "Descripción",
                    "Cant.",
                    "Precio",
                    "Total",
                )

    subtotal = float(
        dto.get(
            "subtotal",
            dto.get(
                "valor",
                0,
            ),
        )
        or 0,
    )

    impuestos = float(
        dto.get(
            "impuestos",
            dto.get(
                "iva",
                0,
            ),
        )
        or 0,
    )

    total = float(
        dto.get(
            "total",
            dto.get(
                "valor",
                0,
            ),
        )
        or 0,
    )

    return html_documento_comercial(
        empresa=dto_a_empresa_html(
            empresa,
        ),
        titulo_documento=titulo_documento,
        numero_documento=str(
            dto.get(
                "numero",
                "",
            )
            or "",
        ),
        fecha=str(
            dto.get(
                "fecha",
                "",
            )
            or dto.get(
                "fecha_generacion",
                "",
            )
            or "",
        ),
        estado=str(
            dto.get(
                "estado",
                "",
            )
            or "",
        ),
        contraparte_titulo=contraparte_titulo,
        contraparte_nombre=str(
            beneficiario.get(
                "nombre",
                "",
            )
            or "",
        ),
        contraparte_documento=str(
            beneficiario.get(
                "documento",
                "",
            )
            or "",
        ),
        contraparte_direccion=str(
            beneficiario.get(
                "direccion",
                "",
            )
            or "",
        ),
        contraparte_telefono=str(
            beneficiario.get(
                "telefono",
                "",
            )
            or "",
        ),
        contraparte_correo=str(
            beneficiario.get(
                "correo",
                "",
            )
            or "",
        ),
        meta_derecha=meta_derecha,
        filas_tabla=filas_tabla,
        subtotal=_formatear_moneda(
            subtotal,
        ),
        iva=_formatear_moneda(
            impuestos,
        ),
        total=_formatear_moneda(
            total,
        ),
        valor_letras=str(
            dto.get(
                "total_letras",
                "",
            )
            or "",
        ),
        observaciones=str(
            dto.get(
                "observaciones",
                dto.get(
                    "concepto",
                    "",
                ),
            )
            or "",
        ),
        info_adicional=info_adicional,
        notas_pie=str(
            dto_a_empresa_html(
                empresa,
            ).get(
                "notas_pie",
                "",
            )
            or "",
        ),
        columnas_tabla=columnas_tabla,
    )
