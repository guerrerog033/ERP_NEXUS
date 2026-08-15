from __future__ import annotations

import ast
from dataclasses import dataclass

from PySide6.QtCore import QUrl

from aplicacion.maestros.impuestos.etiquetas import (
    etiqueta_impuesto,
)
from aplicacion.maestros.impuestos.repositorio import (
    RepositorioImpuesto,
)
from aplicacion.maestros.productos.servicios import (
    ServicioProducto,
)
from aplicacion.modulos.ventas.cotizaciones.servicios import (
    ServicioCotizacion,
)
from aplicacion.nucleo.configuracion import Configuracion


FORMATOS_COTIZACION = {
    "carta": {
        "etiqueta": "Carta estándar",
        "descripcion": "Tabla completa con imágenes, ideal para envío formal.",
    },
    "corporativo": {
        "etiqueta": "Corporativo",
        "descripcion": "Encabezado de empresa, bloques cliente y pie legal.",
    },
    "moderno": {
        "etiqueta": "Moderno",
        "descripcion": "Diseño limpio con acentos de color y totales destacados.",
    },
    "compacto": {
        "etiqueta": "Compacto",
        "descripcion": "Resumen breve sin imágenes, una página rápida.",
    },
    "tirilla": {
        "etiqueta": "Tirilla térmica",
        "descripcion": "Formato angosto 80 mm para impresora POS.",
    },
    "estandar": {
        "etiqueta": "Estándar",
        "descripcion": "Formato clásico con empresa, cliente, ítems y totales por IVA.",
    },
    "electronica": {
        "etiqueta": "Factura electrónica",
        "descripcion": "Representación gráfica DIAN con QR, CUFE y diseño ERP NEXUS.",
    },
}


_ALIAS_FORMATOS = {
    "siigo": "estandar",
}


def normalizar_formato_codigo(
    valor,
    predeterminado: str = "carta",
) -> str:

    if valor is None:

        return predeterminado

    if isinstance(
        valor,
        (
            list,
            tuple,
        ),
    ):

        valor = (
            valor[0]
            if valor
            else predeterminado
        )

    texto = str(
        valor,
    ).strip().lower()

    if (
        texto.startswith("(")
        and texto.endswith(")")
    ):

        try:

            parseado = ast.literal_eval(
                texto,
            )

            if isinstance(
                parseado,
                (
                    list,
                    tuple,
                ),
            ) and parseado:

                texto = str(
                    parseado[0],
                ).strip().lower()

            elif isinstance(
                parseado,
                str,
            ):

                texto = parseado.strip().lower()

        except (
            ValueError,
            SyntaxError,
        ):

            pass

    if (
        len(texto) >= 2
        and texto[0] == texto[-1]
        and texto[0] in "\"'"
    ):

        texto = texto[
            1:-1,
        ].strip().lower()

    return _ALIAS_FORMATOS.get(
        texto,
        texto,
    ) or predeterminado


def _resolver_formato_codigo(
    codigo: str,
) -> str:

    codigo = normalizar_formato_codigo(
        codigo,
        "",
    )

    return _ALIAS_FORMATOS.get(
        codigo,
        codigo,
    )


def etiqueta_formato(
    codigo: str,
) -> str:

    codigo = normalizar_formato_codigo(
        codigo,
        "",
    )

    datos = FORMATOS_COTIZACION.get(
        codigo,
    )

    if datos is None:

        return codigo.replace(
            "_",
            " ",
        ).title()

    return str(
        datos["etiqueta"],
    )


def formatos_combo() -> list[
    tuple[
        str,
        str,
    ]
]:

    disponibles = ServicioCotizacion.formatos_disponibles()

    opciones: list[
        tuple[
            str,
            str,
        ]
    ] = []

    for codigo in disponibles:

        codigo_limpio = normalizar_formato_codigo(
            codigo,
        )

        opciones.append(
            (
                etiqueta_formato(
                    codigo_limpio,
                ),
                codigo_limpio,
            ),
        )

    return opciones


def _formatear_moneda(
    valor: float,
) -> str:

    return f"${valor:,.2f}"


def _formatear_numero(
    valor: float,
) -> str:

    return f"{valor:,.2f}"


def _empresa_desde_maestro() -> dict | None:

    from aplicacion.maestros.empresas.repositorio import (
        EmpresaRepositorio,
    )

    empresas = EmpresaRepositorio.obtener_todos(
        ordenar_por=(
            EmpresaRepositorio.modelo.id,
        ),
    )

    if not empresas:

        return None

    activas = [
        empresa
        for empresa in empresas
        if empresa.activo
    ]

    empresa = (
        activas[0]
        if activas
        else empresas[0]
    )

    nombre = (
        empresa.nombre_comercial
        or empresa.razon_social
        or ""
    ).strip()

    nit = (
        empresa.nit
        or ""
    ).strip()

    if (
        nit
        and empresa.dv
    ):

        nit = (
            f"{nit}-{empresa.dv.strip()}"
        )

    telefono = (
        empresa.telefono
        or empresa.celular
        or ""
    )

    return {
        "nombre": nombre,
        "nit": nit,
        "direccion": (
            empresa.direccion
            or ""
        ),
        "telefono": telefono,
        "correo": (
            empresa.correo
            or ""
        ),
        "ciudad": (
            empresa.ciudad
            or ""
        ),
        "pais": (
            empresa.pais
            or "Colombia"
        ),
        "notas_pie": "",
        "vendedor_nombre": "",
        "vendedor_correo": "",
        "vendedor_telefono": "",
        "logo_ruta": getattr(
            empresa,
            "logo_ruta",
            "",
        )
        or "",
    }


def _datos_empresa() -> dict:

    datos = {
        "nombre": (
            Configuracion.obtener(
                "empresa",
                "nombre",
            )
            or ""
        ),
        "nit": Configuracion.obtener(
            "empresa",
            "nit",
        )
        or "",
        "direccion": Configuracion.obtener(
            "empresa",
            "direccion",
        )
        or "",
        "telefono": Configuracion.obtener(
            "empresa",
            "telefono",
        )
        or "",
        "correo": Configuracion.obtener(
            "empresa",
            "correo",
        )
        or "",
        "ciudad": Configuracion.obtener(
            "empresa",
            "ciudad",
        )
        or "",
        "pais": Configuracion.obtener(
            "empresa",
            "pais",
        )
        or "Colombia",
        "notas_pie": Configuracion.obtener(
            "empresa",
            "notas_pie",
        )
        or "",
        "vendedor_nombre": Configuracion.obtener(
            "empresa",
            "vendedor_nombre",
        )
        or "",
        "vendedor_correo": Configuracion.obtener(
            "empresa",
            "vendedor_correo",
        )
        or "",
        "vendedor_telefono": Configuracion.obtener(
            "empresa",
            "vendedor_telefono",
        )
        or "",
    }

    if datos[
        "nombre"
    ].strip():

        return datos

    maestro = _empresa_desde_maestro()

    if maestro is None:

        return datos

    for clave, valor in datos.items():

        if (
            valor
            and str(
                valor,
            ).strip()
        ):

            maestro[
                clave
            ] = valor

    return maestro


def _porcentaje_impuesto_id(
    impuesto_id,
) -> float:

    if not impuesto_id:

        return 0.0

    impuesto = RepositorioImpuesto.obtener_por_id(
        impuesto_id,
    )

    if impuesto is None:

        return 0.0

    return float(
        impuesto.porcentaje
        or 0,
    )


def _etiqueta_impuesto_porcentaje(
    impuesto_id,
) -> str:

    porcentaje = _porcentaje_impuesto_id(
        impuesto_id,
    )

    if porcentaje == 0:

        return "0 %"

    texto = f"{porcentaje:g}"

    if "." in texto:

        texto = texto.rstrip(
            "0",
        ).rstrip(
            ".",
        )

    return f"{texto} %"


def _etiqueta_impuesto_id(
    impuesto_id,
) -> str:

    if not impuesto_id:

        return ""

    impuesto = RepositorioImpuesto.obtener_por_id(
        impuesto_id,
    )

    return etiqueta_impuesto(
        impuesto,
    )


def _unidad_producto(
    producto_id,
    predeterminado: str = "Und",
) -> str:

    if not producto_id:

        return predeterminado

    producto = ServicioProducto.obtener_por_id(
        producto_id,
    )

    if producto is None or not producto.unidad_medida_id:

        return predeterminado

    from aplicacion.maestros.unidades_medida.repositorio import (
        UnidadMedidaRepositorio,
    )

    unidad_medida = UnidadMedidaRepositorio.obtener_por_id(
        producto.unidad_medida_id,
    )

    unidad = str(
        getattr(
            unidad_medida,
            "codigo",
            "",
        )
        or "",
    ).strip()

    return unidad or predeterminado


def _datos_cliente(
    cotizacion,
    nombre_cliente: str,
) -> dict:

    from aplicacion.maestros.terceros.servicio import (
        TerceroServicio,
    )

    cliente_id = getattr(
        cotizacion,
        "cliente_id",
        None,
    )

    cliente = None

    if cliente_id:

        cliente = TerceroServicio.obtener_por_id(
            cliente_id,
        )

    if cliente is None:

        return {
            "nombre": nombre_cliente,
            "nit": "",
            "contacto": nombre_cliente,
            "direccion": "No aplica",
            "ciudad": "",
            "telefono": "",
            "correo": "",
        }

    nit = str(
        cliente.numero_documento
        or "",
    ).strip()

    if getattr(
        cliente,
        "dv",
        None,
    ):

        nit = (
            f"{nit}-{cliente.dv}"
        )

    nombre = (
        cliente.razon_social
        or cliente.nombre_completo
        or nombre_cliente
    )

    contacto = (
        cliente.nombre_comercial
        or cliente.razon_social
        or cliente.nombre_completo
        or nombre_cliente
    )

    telefono = str(
        cliente.telefono
        or cliente.celular
        or "",
    ).strip()

    ciudad = str(
        cliente.ciudad
        or "",
    ).strip()

    return {
        "nombre": nombre,
        "nit": nit,
        "contacto": contacto,
        "direccion": str(
            cliente.direccion
            or "No aplica",
        ).strip(),
        "ciudad": ciudad,
        "telefono": telefono,
        "correo": str(
            cliente.correo
            or "",
        ).strip(),
    }


def _desglose_iva_detalles(
    detalles,
) -> dict[
    float,
    float,
]:

    tasas: dict[
        float,
        float,
    ] = {}

    for detalle in detalles:

        subtotal, total = ServicioCotizacion._calcular_linea(
            detalle.cantidad,
            detalle.precio_unitario,
            detalle.impuesto_id,
            bool(
                getattr(
                    detalle,
                    "precio_incluye_iva",
                    False,
                )
            ),
        )

        iva = round(
            total
            - subtotal,
            2,
        )

        porcentaje = _porcentaje_impuesto_id(
            detalle.impuesto_id,
        )

        tasas[
            porcentaje
        ] = round(
            tasas.get(
                porcentaje,
                0.0,
            )
            + iva,
            2,
        )

    return tasas


def _codigo_producto(
    producto_id,
    descripcion: str,
) -> str:

    if producto_id:

        producto = ServicioProducto.obtener_por_id(
            producto_id,
        )

        if (
            producto is not None
            and producto.codigo
        ):

            return producto.codigo

    if " - " in descripcion:

        return descripcion.split(
            " - ",
            1,
        )[0]

    return ""


def _referencia_producto(
    producto_id,
    descripcion: str,
    *,
    producto_variante_id=None,
) -> str:

    if producto_variante_id:

        variante = ServicioProducto.repositorio.obtener_variante_por_id(
            producto_variante_id,
        )

        if variante is not None:

            codigo_barras = str(
                variante.codigo_barras
                or "",
            ).strip()

            if codigo_barras:

                return codigo_barras

    if producto_id:

        producto = ServicioProducto.obtener_por_id(
            producto_id,
        )

        if producto is not None:

            codigo_barras = str(
                producto.codigo_barras
                or "",
            ).strip()

            if codigo_barras:

                return codigo_barras

            if producto.codigo:

                return str(
                    producto.codigo,
                ).strip()

    return _codigo_producto(
        producto_id,
        descripcion,
    )


def _placeholder_imagen(
    ancho: int,
) -> str:

    return (
        f'<table width="{ancho}" height="{ancho}" '
        f'style="background:#f8fafc;border:1px solid #e2e8f0;">'
        f'<tr><td align="center" valign="middle" '
        f'style="color:#94a3b8;font-size:8pt;">—</td></tr></table>'
    )


def _imagen_html(
    producto_id,
    ancho: int = 52,
) -> str:

    if not producto_id:

        return _placeholder_imagen(
            ancho,
        )

    producto = ServicioProducto.obtener_por_id(
        producto_id,
    )

    if producto is None:

        return _placeholder_imagen(
            ancho,
        )

    ruta = ServicioProducto.resolver_imagen_producto(
        producto,
    )

    if ruta is None:

        return _placeholder_imagen(
            ancho,
        )

    if not ruta.is_file():

        return _placeholder_imagen(
            ancho,
        )

    url_archivo = QUrl.fromLocalFile(
        str(
            ruta.resolve(),
        ),
    ).toString()

    return (
        f'<img src="{url_archivo}" '
        f'width="{ancho}" height="{ancho}" '
        f'style="object-fit:contain;display:block;margin:0 auto;" '
        f'alt="" />'
    )


def _resumen_cotizacion(
    cotizacion,
    detalles,
) -> dict:

    lineas = []

    for detalle in detalles:

        lineas.append(
            {
                "producto_id": detalle.producto_id,
                "descripcion": detalle.descripcion,
                "cantidad": detalle.cantidad,
                "precio_unitario": detalle.precio_unitario,
                "impuesto_id": detalle.impuesto_id,
                "precio_incluye_iva": bool(
                    getattr(
                        detalle,
                        "precio_incluye_iva",
                        False,
                    )
                ),
            },
        )

    return ServicioCotizacion._calcular_resumen(
        lineas,
        getattr(
            cotizacion,
            "retefuente_id",
            None,
        ),
        getattr(
            cotizacion,
            "reteica_id",
            None,
        ),
        getattr(
            cotizacion,
            "reteiva_id",
            None,
        ),
    )


@dataclass
class ContextoFormato:

    cotizacion: object
    detalles: list
    nombre_cliente: str
    resumen: dict
    empresa: dict
    cliente: dict
    fecha: str
    observaciones: str
    etiqueta_documento: str = "COTIZACIÓN"
    titulo_documento: str = "Cotización"
    info_adicional: str = ""
    mostrar_imagenes: bool = True


def _crear_contexto(
    cotizacion,
    detalles,
    nombre_cliente: str,
) -> ContextoFormato:

    from aplicacion.reportes.comunes.datos_documento import (
        cotizacion_a_dto,
    )
    from aplicacion.reportes.comunes.html_documento import (
        contexto_formato_desde_dto,
    )

    observaciones = str(
        cotizacion.observaciones
        or "",
    ).strip()

    info_adicional = ""

    if getattr(
        cotizacion,
        "fecha_vigencia",
        None,
    ):
        info_adicional += (
            f"Vigencia hasta: "
            f"{cotizacion.fecha_vigencia.strftime('%d/%m/%Y')}. "
        )

    condiciones = getattr(
        cotizacion,
        "condiciones_comerciales",
        "",
    )

    if condiciones:
        info_adicional += str(
            condiciones,
        )

    try:
        from aplicacion.modulos.ventas.cotizaciones.servicios import (
            ServicioCotizacion,
        )
        from aplicacion.comunes.qr_util import (
            generar_qr_data_uri,
        )

        datos_aceptacion = (
            ServicioCotizacion.preparar_aceptacion(
                cotizacion.id,
            )
        )

        qr = generar_qr_data_uri(
            datos_aceptacion["url"],
        )

        info_adicional += (
            f"<br/><img src='{qr}' width='120' alt='QR'/> "
            f"Código verificación: "
            f"{datos_aceptacion['codigo_verificacion']}"
        )

    except Exception:
        pass

    dto = cotizacion_a_dto(
        cotizacion,
        detalles,
        nombre_cliente,
    )

    return contexto_formato_desde_dto(
        dto,
        documento=cotizacion,
        detalles=detalles,
        nombre_cliente=nombre_cliente,
        resumen=_resumen_cotizacion(
            cotizacion,
            detalles,
        ),
        fecha=cotizacion.fecha.strftime(
            "%d/%m/%Y",
        ),
        observaciones=observaciones,
        info_adicional=info_adicional,
    )


def _bloque_totales_html(
    ctx: ContextoFormato,
    colspan: int = 6,
) -> str:

    resumen = ctx.resumen

    filas = [
        (
            "Subtotal",
            resumen["subtotal"],
        ),
    ]

    if resumen["retefuente"] > 0:

        filas.append(
            (
                "Retefuente",
                resumen["retefuente"],
            ),
        )

    if resumen["reteica"] > 0:

        filas.append(
            (
                "ReteICA",
                resumen["reteica"],
            ),
        )

    if resumen.get(
        "reteiva",
        0,
    ) > 0:

        filas.append(
            (
                "ReteIVA",
                resumen["reteiva"],
            ),
        )

    if resumen.get(
        "iva",
        0,
    ) > 0:

        filas.append(
            (
                "IVA",
                resumen["iva"],
            ),
        )

    filas.append(
        (
            "Total",
            resumen["total"],
        ),
    )

    html = ""

    for indice, (
        etiqueta,
        valor,
    ) in enumerate(
        filas,
    ):

        negrita = (
            "font-weight:bold;"
            if indice
            == len(
                filas,
            )
            - 1
            else ""
        )

        html += (
            "<tr>"
            f"<td align='right' colspan='{colspan}' "
            f"style='{negrita}'>{etiqueta}:</td>"
            f"<td align='right' style='{negrita}'>"
            f"{_formatear_moneda(valor)}</td>"
            "</tr>"
        )

    return html


def _html_carta(
    ctx: ContextoFormato,
) -> str:

    filas = ""

    for detalle in ctx.detalles:

        codigo = _codigo_producto(
            detalle.producto_id,
            detalle.descripcion,
        )

        filas += (
            "<tr>"
            f"<td class='col-imagen' align='center'>{_imagen_html(detalle.producto_id)}</td>"
            f"<td class='col-codigo'>{codigo}</td>"
            f"<td>{detalle.descripcion}</td>"
            f"<td class='col-cant' align='right'>{detalle.cantidad:,.2f}</td>"
            f"<td class='col-precio' align='right'>"
            f"{_formatear_moneda(detalle.precio_unitario)}</td>"
            f"<td class='col-iva' align='center'>"
            f"{_etiqueta_impuesto_id(detalle.impuesto_id)}</td>"
            f"<td class='col-total' align='right'>"
            f"{_formatear_moneda(detalle.total_linea)}</td>"
            "</tr>"
        )

    obs = ""

    if ctx.observaciones:

        obs = (
            "<p><strong>Observaciones:</strong><br>"
            f"{ctx.observaciones}</p>"
        )

    return f"""
    <html><head><meta charset="utf-8">
    <style>
        body {{ font-family: Arial, sans-serif; font-size: 11pt; color: #1f2937; margin: 0; padding: 20px; }}
        .documento {{ max-width: 820px; margin: 0 auto; }}
        h1 {{ font-size: 16pt; margin-bottom: 4px; color: #1b4f8a; }}
        table {{ width: 100%; border-collapse: collapse; margin-top: 16px; table-layout: fixed; }}
        th, td {{ border: 1px solid #c8d8e8; padding: 8px; vertical-align: middle; }}
        th {{ background: #eef2f6; }}
        .col-imagen {{ width: 64px; text-align: center; }}
        .col-codigo {{ width: 90px; }}
        .col-cant {{ width: 70px; text-align: right; }}
        .col-precio, .col-total {{ width: 95px; text-align: right; }}
        .col-iva {{ width: 70px; text-align: center; }}
    </style></head><body>
    <div class="documento">
        <h1>{ctx.titulo_documento} No. {ctx.cotizacion.numero}</h1>
        <p><strong>Fecha:</strong> {ctx.fecha}<br>
        <strong>Cliente:</strong> {ctx.nombre_cliente}</p>
        {ctx.info_adicional}
        <table>
            <thead><tr>
                <th class="col-imagen">Imagen</th><th class="col-codigo">Código</th><th>Descripción</th>
                <th class="col-cant">Cant.</th><th class="col-precio">Precio</th><th class="col-iva">IVA</th><th class="col-total">Total</th>
            </tr></thead>
            <tbody>{filas}</tbody>
            <tfoot>{_bloque_totales_html(ctx, colspan=6)}</tfoot>
        </table>
        {obs}
    </div>
    </body></html>
    """


def _html_corporativo(
    ctx: ContextoFormato,
) -> str:

    empresa = ctx.empresa

    encabezado_empresa = f"<strong>{empresa['nombre']}</strong>"

    if empresa["nit"]:

        encabezado_empresa += f"<br>NIT: {empresa['nit']}"

    if empresa["direccion"]:

        encabezado_empresa += f"<br>{empresa['direccion']}"

    contacto = []

    if empresa["telefono"]:

        contacto.append(
            f"Tel: {empresa['telefono']}",
        )

    if empresa["correo"]:

        contacto.append(
            empresa["correo"],
        )

    if contacto:

        encabezado_empresa += (
            "<br>"
            + " | ".join(
                contacto,
            )
        )

    filas = ""

    for indice, detalle in enumerate(
        ctx.detalles,
        start=1,
    ):

        codigo = _codigo_producto(
            detalle.producto_id,
            detalle.descripcion,
        )

        filas += (
            "<tr>"
            f"<td align='center'>{indice}</td>"
            f"<td align='center'>{_imagen_html(detalle.producto_id, 44)}</td>"
            f"<td>{codigo}</td>"
            f"<td>{detalle.descripcion}</td>"
            f"<td align='center'>{detalle.cantidad:,.2f}</td>"
            f"<td align='right'>"
            f"{_formatear_moneda(detalle.precio_unitario)}</td>"
            f"<td align='center'>"
            f"{_etiqueta_impuesto_id(detalle.impuesto_id)}</td>"
            f"<td align='right'>"
            f"{_formatear_moneda(detalle.total_linea)}</td>"
            "</tr>"
        )

    obs = ""

    if ctx.observaciones:

        obs = (
            "<p style='margin-top:18px;'><strong>Observaciones:</strong><br>"
            f"{ctx.observaciones}</p>"
        )

    return f"""
    <html><head><meta charset="utf-8">
    <style>
        body {{ font-family: 'Segoe UI', Arial, sans-serif; font-size: 10.5pt; color: #111; margin: 0; padding: 20px; }}
        .documento {{ max-width: 820px; margin: 0 auto; }}
        .cabecera {{ border-bottom: 3px solid #1b4f8a; padding-bottom: 12px; margin-bottom: 16px; }}
        .empresa {{ font-size: 14pt; color: #1b4f8a; }}
        .titulo-doc {{ text-align: right; font-size: 18pt; font-weight: bold; color: #1b4f8a; }}
        .meta {{ width: 100%; margin: 12px 0 18px 0; }}
        .meta td {{ vertical-align: top; padding: 8px; border: 1px solid #d0d7de; }}
        .meta .etq {{ background: #f6f8fa; font-weight: bold; width: 120px; }}
        table.items {{ width: 100%; border-collapse: collapse; table-layout: fixed; }}
        table.items th {{ background: #1b4f8a; color: white; padding: 7px; font-size: 10pt; }}
        table.items td {{ border: 1px solid #d0d7de; padding: 6px; vertical-align: middle; }}
        .col-num {{ width: 32px; }}
        .col-img {{ width: 56px; }}
        .col-cod {{ width: 80px; }}
        .pie {{ margin-top: 24px; font-size: 9pt; color: #555; border-top: 1px solid #ccc; padding-top: 10px; }}
        .firmas {{ margin-top: 40px; }}
        .firmas td {{ text-align: center; padding-top: 40px; border-top: 1px solid #999; width: 45%; }}
    </style></head><body>
    <div class="documento">
        <table width="100%" class="cabecera"><tr>
            <td class="empresa">{encabezado_empresa}</td>
            <td class="titulo-doc">{ctx.etiqueta_documento}<br>No. {ctx.cotizacion.numero}</td>
        </tr></table>
        <table class="meta"><tr>
            <td class="etq">Fecha</td><td>{ctx.fecha}</td>
            <td class="etq">Cliente</td><td>{ctx.nombre_cliente}</td>
        </tr></table>
        <table class="items">
            <thead><tr>
                <th class="col-num">#</th><th class="col-img">Imagen</th><th class="col-cod">Código</th>
                <th>Descripción</th><th>Cant.</th>
                <th>Vr. unitario</th><th>IVA</th><th>Total</th>
            </tr></thead>
            <tbody>{filas}</tbody>
            <tfoot>{_bloque_totales_html(ctx, colspan=7)}</tfoot>
        </table>
        {obs}
        <p class="pie">
            Esta cotización tiene validez comercial según condiciones acordadas con el cliente.
            Los precios pueden variar según disponibilidad. IVA discriminado cuando aplique.
        </p>
        <table width="100%" class="firmas"><tr>
            <td>Elaborado por<br>{empresa['nombre']}</td>
            <td>Aprobado cliente<br>{ctx.nombre_cliente}</td>
        </tr></table>
    </div>
    </body></html>
    """


def _html_moderno(
    ctx: ContextoFormato,
) -> str:

    empresa = ctx.empresa

    filas = ""

    for detalle in ctx.detalles:

        codigo = _codigo_producto(
            detalle.producto_id,
            detalle.descripcion,
        )

        referencia = (
            f"<span style='color:#64748b;font-size:9pt;'>{codigo}</span><br>"
            if codigo
            else ""
        )

        filas += (
            "<tr>"
            f"<td align='center' valign='middle'>{_imagen_html(detalle.producto_id, 44)}</td>"
            f"<td>{referencia}{detalle.descripcion}</td>"
            f"<td align='center'>{detalle.cantidad:,.2f}</td>"
            f"<td align='right'>"
            f"{_formatear_moneda(detalle.precio_unitario)}</td>"
            f"<td align='center'>"
            f"{_etiqueta_impuesto_id(detalle.impuesto_id)}</td>"
            f"<td align='right'>"
            f"{_formatear_moneda(detalle.total_linea)}</td>"
            "</tr>"
        )

    obs = ""

    if ctx.observaciones:

        obs = (
            "<div style='margin-top:16px;padding:10px;background:#f8fafc;"
            "border-left:4px solid #3a7bc5;'>"
            f"<strong>Notas:</strong> {ctx.observaciones}</div>"
        )

    resumen = ctx.resumen

    return f"""
    <html><head><meta charset="utf-8">
    <style>
        body {{ font-family: Calibri, Arial, sans-serif; font-size: 11pt; margin: 0; color: #0f172a; }}
        .banner {{ background: linear-gradient(90deg, #1b4f8a, #3a7bc5); color: white;
                   padding: 20px 24px; }}
        .banner h1 {{ margin: 0; font-size: 22pt; }}
        .banner p {{ margin: 4px 0 0 0; opacity: 0.9; }}
        .contenido {{ padding: 20px 24px; }}
        .tarjetas {{ width: 100%; margin-bottom: 16px; }}
        .tarjetas td {{ background: #f1f5f9; padding: 10px 14px; border-radius: 6px; }}
        .tarjetas .lbl {{ font-size: 9pt; color: #64748b; text-transform: uppercase; }}
        table.items {{ width: 100%; border-collapse: collapse; table-layout: fixed; }}
        table.items th {{ background: #e2e8f0; padding: 8px; text-align: left; }}
        table.items td {{ padding: 8px; border-bottom: 1px solid #e2e8f0; vertical-align: middle; }}
        table.items .col-img {{ width: 58px; text-align: center; }}
        table.items tr:nth-child(even) td {{ background: #f8fafc; }}
        .totales {{ margin-top: 16px; float: right; width: 280px; }}
        .totales td {{ padding: 6px 10px; }}
        .totales .final {{ background: #1b4f8a; color: white; font-weight: bold; font-size: 12pt; }}
    </style></head><body>
        <div class="banner">
            <h1>{ctx.titulo_documento} No. {ctx.cotizacion.numero}</h1>
            <p>{empresa['nombre']} · {ctx.fecha}</p>
        </div>
        <div class="contenido">
            <table class="tarjetas"><tr>
                <td><div class="lbl">Cliente</div>{ctx.nombre_cliente}</td>
                <td width="20"></td>
                <td><div class="lbl">Documento</div>{ctx.cotizacion.numero}</td>
            </tr></table>
            <table class="items">
                <thead><tr>
                    <th class="col-img">Img</th><th>Producto / servicio</th><th>Cant.</th>
                    <th>Precio</th><th>IVA</th><th>Total</th>
                </tr></thead>
                <tbody>{filas}</tbody>
            </table>
            <table class="totales">
                <tr><td align="right">Subtotal</td>
                    <td align="right">{_formatear_moneda(resumen['subtotal'])}</td></tr>
                {_fila_total_moderno('Retefuente', resumen.get('retefuente', 0))}
                {_fila_total_moderno('ReteICA', resumen.get('reteica', 0))}
                {_fila_total_moderno('ReteIVA', resumen.get('reteiva', 0))}
                <tr class="final"><td align="right">Total</td>
                    <td align="right">{_formatear_moneda(resumen['total'])}</td></tr>
            </table>
            <div style="clear:both;"></div>
            {obs}
        </div>
    </body></html>
    """


def _fila_total_moderno(
    etiqueta: str,
    valor: float,
) -> str:

    if not valor:

        return ""

    return (
        f"<tr><td align='right'>{etiqueta}</td>"
        f"<td align='right'>{_formatear_moneda(valor)}</td></tr>"
    )


def _html_compacto(
    ctx: ContextoFormato,
) -> str:

    filas = ""

    for detalle in ctx.detalles:

        filas += (
            "<tr>"
            f"<td align='center'>{_imagen_html(detalle.producto_id, 40)}</td>"
            f"<td>{detalle.descripcion}</td>"
            f"<td align='right'>{detalle.cantidad:g}</td>"
            f"<td align='right'>"
            f"{_formatear_moneda(detalle.precio_unitario)}</td>"
            f"<td align='right'>"
            f"{_formatear_moneda(detalle.total_linea)}</td>"
            "</tr>"
        )

    obs = ""

    if ctx.observaciones:

        obs = f"<p><em>{ctx.observaciones}</em></p>"

    resumen = ctx.resumen

    return f"""
    <html><head><meta charset="utf-8">
    <style>
        body {{ font-family: Arial, sans-serif; font-size: 10pt; color: #222; }}
        h2 {{ margin: 0 0 8px 0; font-size: 13pt; }}
        .info {{ margin-bottom: 12px; line-height: 1.5; }}
        table {{ width: 100%; border-collapse: collapse; table-layout: fixed; }}
        th {{ border-bottom: 2px solid #333; padding: 6px; text-align: left; }}
        td {{ border-bottom: 1px solid #ddd; padding: 6px; vertical-align: middle; }}
        .col-img {{ width: 52px; text-align: center; }}
        .tot {{ text-align: right; margin-top: 10px; }}
        .tot .total {{ font-size: 12pt; font-weight: bold; }}
    </style></head><body>
        <h2>{ctx.etiqueta_documento} {ctx.cotizacion.numero}</h2>
        <div class="info">
            <strong>Fecha:</strong> {ctx.fecha}<br>
            <strong>Cliente:</strong> {ctx.nombre_cliente}
        </div>
        <table>
            <thead><tr>
                <th class="col-img">Img</th><th>Concepto</th><th>Cant.</th><th>Precio</th><th>Total</th>
            </tr></thead>
            <tbody>{filas}</tbody>
        </table>
        <div class="tot">
            Subtotal: {_formatear_moneda(resumen['subtotal'])}<br>
            {_linea_compacto('Retefuente', resumen.get('retefuente', 0))}
            {_linea_compacto('ReteICA', resumen.get('reteica', 0))}
            {_linea_compacto('ReteIVA', resumen.get('reteiva', 0))}
            <span class="total">Total: {_formatear_moneda(resumen['total'])}</span>
        </div>
        {obs}
    </body></html>
    """


def _linea_compacto(
    etiqueta: str,
    valor: float,
) -> str:

    if not valor:

        return ""

    return f"{etiqueta}: {_formatear_moneda(valor)}<br>"


def _html_tirilla(
    ctx: ContextoFormato,
) -> str:

    empresa = ctx.empresa

    lineas = ""

    for detalle in ctx.detalles:

        lineas += (
            "<tr>"
            f"<td colspan='2'>{detalle.descripcion}</td></tr>"
            "<tr>"
            f"<td>{detalle.cantidad:g} x "
            f"{_formatear_moneda(detalle.precio_unitario)}</td>"
            f"<td align='right'>"
            f"{_formatear_moneda(detalle.total_linea)}</td>"
            "</tr>"
        )

    resumen = ctx.resumen

    obs = ""

    if ctx.observaciones:

        obs = (
            f"<p style='font-size:8pt;'>Obs: {ctx.observaciones}</p>"
        )

    return f"""
    <html><head><meta charset="utf-8">
    <style>
        body {{ font-family: 'Courier New', monospace; font-size: 9pt; margin: 0; }}
        .centro {{ text-align: center; }}
        table {{ width: 100%; border-collapse: collapse; }}
        td {{ padding: 2px 0; vertical-align: top; }}
        .sep {{ border-top: 1px dashed #000; margin: 6px 0; }}
        .total {{ font-weight: bold; font-size: 10pt; }}
    </style></head><body>
        <p class="centro"><strong>{empresa['nombre']}</strong><br>
        {('NIT: ' + empresa['nit']) if empresa['nit'] else ''}</p>
        <div class="sep"></div>
        <p class="centro"><strong>{ctx.etiqueta_documento}</strong><br>
        No. {ctx.cotizacion.numero}<br>{ctx.fecha}</p>
        <p><strong>Cliente:</strong><br>{ctx.nombre_cliente}</p>
        {ctx.info_adicional}
        <div class="sep"></div>
        <table>{lineas}</table>
        <div class="sep"></div>
        <table>
            <tr><td>Subtotal</td><td align="right">{_formatear_moneda(resumen['subtotal'])}</td></tr>
            {_fila_tirilla('IVA', resumen.get('iva', 0))}
            {_fila_tirilla('Retefuente', resumen.get('retefuente', 0))}
            {_fila_tirilla('ReteICA', resumen.get('reteica', 0))}
            {_fila_tirilla('ReteIVA', resumen.get('reteiva', 0))}
            <tr class="total"><td>TOTAL</td>
                <td align="right">{_formatear_moneda(resumen['total'])}</td></tr>
        </table>
        {obs}
        <p class="centro" style="font-size:8pt;margin-top:10px;">Gracias por su preferencia</p>
    </body></html>
    """


def _fila_tirilla(
    etiqueta: str,
    valor: float,
) -> str:

    if not valor:

        return ""

    return (
        f"<tr><td>{etiqueta}</td>"
        f"<td align='right'>{_formatear_moneda(valor)}</td></tr>"
    )


def _linea_total_estandar(
    etiqueta: str,
    valor: float,
    *,
    resaltar: bool = False,
) -> str:

    estilo_etiqueta = (
        "font-weight:bold;font-size:11pt;background:#eef2f7;"
        if resaltar
        else "background:#eef2f7;"
    )

    estilo_valor = (
        "font-weight:bold;font-size:11pt;"
        if resaltar
        else ""
    )

    return (
        f"<tr>"
        f"<td align='right' style='padding:5px 8px;border:1px solid #b0b0b0;{estilo_etiqueta}'>"
        f"{etiqueta}</td>"
        f"<td align='right' style='padding:5px 8px;border:1px solid #b0b0b0;{estilo_valor}width:120px;'>"
        f"{_formatear_numero(valor)}</td>"
        f"</tr>"
    )


def _celda_etiqueta_estandar(
    texto: str,
    *,
    ancho: str = "",
) -> str:

    extra = (
        f" width='{ancho}'"
        if ancho
        else ""
    )

    return (
        f"<td{extra} bgcolor='#eef2f7' "
        f"style='padding:5px 8px;border:1px solid #b0b0b0;white-space:nowrap;'>"
        f"<b>{texto}</b></td>"
    )


def _celda_valor_estandar(
    texto: str,
    *,
    ancho: str = "",
    colspan: int = 0,
) -> str:

    extra = (
        f" width='{ancho}'"
        if ancho
        else ""
    )

    span = (
        f" colspan='{colspan}'"
        if colspan > 1
        else ""
    )

    valor = (
        texto
        if texto not in (
            None,
            "",
        )
        else "—"
    )

    return (
        f"<td{extra}{span} "
        f"style='padding:5px 8px;border:1px solid #b0b0b0;'>"
        f"{valor}</td>"
    )


def _encabezado_empresa_estandar(
    empresa: dict,
) -> str:

    lineas: list[str] = []

    logo = str(
        empresa.get(
            "logo_ruta",
            "",
        )
        or "",
    ).strip()

    if logo:
        lineas.append(
            f"<img src='file:///{logo.replace(chr(92), '/')}' "
            f"alt='Logo' style='max-height:70px;margin-bottom:8px;'/>",
        )

    if empresa[
        "nombre"
    ]:

        lineas.append(
            f"<span style='font-size:12pt;font-weight:bold;'>"
            f"{empresa['nombre']}</span>",
        )

    if empresa[
        "nit"
    ]:

        lineas.append(
            f"NIT {empresa['nit']}",
        )

    if empresa[
        "direccion"
    ]:

        lineas.append(
            empresa[
                "direccion"
            ],
        )

    if empresa[
        "telefono"
    ]:

        lineas.append(
            f"Tel: {empresa['telefono']}",
        )

    if empresa[
        "correo"
    ]:

        lineas.append(
            empresa[
                "correo"
            ],
        )

    ubicacion: list[str] = []

    if empresa[
        "ciudad"
    ]:

        ubicacion.append(
            empresa[
                "ciudad"
            ],
        )

    if empresa[
        "pais"
    ]:

        ubicacion.append(
            empresa[
                "pais"
            ],
        )

    if ubicacion and lineas:

        lineas.append(
            " - ".join(
                ubicacion,
            ),
        )

    if lineas:

        return "<br>".join(
            lineas,
        )

    return (
        "<span style='color:#666;font-size:9pt;'>"
        "Configure los datos de la empresa en el maestro Empresas "
        "o en configuracion.json.</span>"
    )


def _bloque_iva_estandar(
    detalles,
) -> str:

    desglose = _desglose_iva_detalles(
        detalles,
    )

    if not desglose:

        return _linea_total_estandar(
            "IVA 0%",
            0.0,
        )

    html = ""

    for tasa in sorted(
        desglose.keys(),
    ):

        etiqueta = (
            "IVA 0%"
            if tasa == 0
            else f"IVA {_etiqueta_impuesto_porcentaje_por_valor(tasa)}"
        )

        html += _linea_total_estandar(
            etiqueta,
            desglose[
                tasa
            ],
        )

    return html


def _etiqueta_impuesto_porcentaje_por_valor(
    porcentaje: float,
) -> str:

    if porcentaje == 0:

        return "0%"

    texto = f"{porcentaje:g}"

    if "." in texto:

        texto = texto.rstrip(
            "0",
        ).rstrip(
            ".",
        )

    return f"{texto}%"


def _html_estandar(
    ctx: ContextoFormato,
) -> str:

    empresa = ctx.empresa
    cliente = ctx.cliente
    resumen = ctx.resumen

    encabezado_empresa = _encabezado_empresa_estandar(
        empresa,
    )

    fecha_texto = ctx.cotizacion.fecha.strftime(
        "%d/%m/%Y",
    )

    ciudad_tel_cliente = (
        cliente[
            "ciudad"
        ]
        or "—"
    )

    if cliente[
        "telefono"
    ]:

        ciudad_tel_cliente += (
            f" / {cliente['telefono']}"
        )

    filas = ""

    for indice, detalle in enumerate(
        ctx.detalles,
        start=1,
    ):

        subtotal_linea, total_linea = ServicioCotizacion._calcular_linea(
            detalle.cantidad,
            detalle.precio_unitario,
            detalle.impuesto_id,
            bool(
                getattr(
                    detalle,
                    "precio_incluye_iva",
                    False,
                )
            ),
        )

        cantidad = float(
            detalle.cantidad
            or 0,
        )

        vr_unitario = (
            subtotal_linea
            / cantidad
            if cantidad
            else 0.0
        )

        celda_imagen = ""

        if ctx.mostrar_imagenes:

            celda_imagen = (
                "<td align='center' valign='middle' "
                "style='padding:3px;border:1px solid #b0b0b0;'>"
                f"{_imagen_html(detalle.producto_id, 40)}</td>"
            )

        filas += (
            "<tr>"
            f"{celda_imagen}"
            f"<td align='center' style='padding:4px;border:1px solid #b0b0b0;"
            f"font-size:8.5pt;word-break:break-all;'>"
            f"{_referencia_producto(detalle.producto_id, detalle.descripcion, producto_variante_id=getattr(detalle, 'producto_variante_id', None)) or '—'}</td>"
            f"<td align='center' style='padding:4px;border:1px solid #b0b0b0;'>{indice}</td>"
            f"<td style='padding:4px 6px;border:1px solid #b0b0b0;'>{detalle.descripcion}</td>"
            f"<td align='right' style='padding:4px;border:1px solid #b0b0b0;'>{detalle.cantidad:,.2f}</td>"
            f"<td align='center' style='padding:4px;border:1px solid #b0b0b0;'>{_unidad_producto(detalle.producto_id)}</td>"
            f"<td align='right' style='padding:4px;border:1px solid #b0b0b0;'>{_formatear_numero(vr_unitario)}</td>"
            f"<td align='center' style='padding:4px;border:1px solid #b0b0b0;'>{_etiqueta_impuesto_porcentaje(detalle.impuesto_id)}</td>"
            f"<td align='right' style='padding:4px;border:1px solid #b0b0b0;'>{_formatear_numero(total_linea)}</td>"
            "</tr>"
        )

    retenciones = ""

    if resumen.get(
        "retefuente",
        0,
    ) > 0:

        retenciones += _linea_total_estandar(
            "Retefuente",
            resumen[
                "retefuente"
            ],
        )

    if resumen.get(
        "reteica",
        0,
    ) > 0:

        retenciones += _linea_total_estandar(
            "ReteICA",
            resumen[
                "reteica"
            ],
        )

    if resumen.get(
        "reteiva",
        0,
    ) > 0:

        retenciones += _linea_total_estandar(
            "ReteIVA",
            resumen[
                "reteiva"
            ],
        )

    notas_pie = ""

    if empresa[
        "notas_pie"
    ]:

        notas_pie = (
            f"<p style='font-size:9.5pt;line-height:1.5;margin:8px 0 0 0;'>"
            f"{empresa['notas_pie']}</p>"
        )

    vendedor = str(
        getattr(
            ctx.cotizacion,
            "vendedor",
            "",
        )
        or empresa.get(
            "vendedor_nombre",
            "",
        )
        or "",
    ).strip()

    texto_observaciones = (
        ctx.observaciones
        or "—"
    )

    bloque_observaciones = (
        "<table width='100%' cellspacing='0' cellpadding='0' "
        "border='0' style='margin-bottom:10px;'>"
        "<tr>"
        "<td bgcolor='#eef2f7' "
        "style='padding:5px 8px;border:1px solid #b0b0b0;"
        "font-weight:bold;'>Observaciones</td>"
        "</tr>"
        "<tr>"
        f"<td style='padding:8px;border:1px solid #b0b0b0;"
        f"min-height:40px;vertical-align:top;line-height:1.45;'>"
        f"{texto_observaciones}</td>"
        "</tr>"
        "</table>"
    )

    contacto_pie = ""

    lineas_contacto: list[
        str,
    ] = []

    if empresa[
        "vendedor_nombre"
    ]:

        lineas_contacto.append(
            f"<b>{empresa['vendedor_nombre']}</b>",
        )

    if empresa[
        "vendedor_correo"
    ]:

        lineas_contacto.append(
            empresa[
                "vendedor_correo"
            ],
        )

    if empresa[
        "vendedor_telefono"
    ]:

        lineas_contacto.append(
            empresa[
                "vendedor_telefono"
            ],
        )

    if lineas_contacto:

        contacto_pie = (
            "<p style='font-size:10pt;line-height:1.5;margin:16px 0 0 0;'>"
            + "<br>".join(
                lineas_contacto,
            )
            + "</p>"
        )

    bloque_totales = (
        _linea_total_estandar(
            "Total Bruto",
            resumen[
                "subtotal"
            ],
        )
        + _linea_total_estandar(
            "Subtotal",
            resumen[
                "subtotal"
            ],
        )
        + _bloque_iva_estandar(
            ctx.detalles,
        )
        + retenciones
        + _linea_total_estandar(
            "Total a Pagar",
            resumen[
                "total"
            ],
            resaltar=True,
        )
    )

    columna_imagen = ""

    if ctx.mostrar_imagenes:

        columna_imagen = (
            "<td width=\"7%\" style=\"padding:5px 2px;"
            "border:1px solid #666;\">Imagen</td>"
        )

    ancho_descripcion = (
        "28%"
        if ctx.mostrar_imagenes
        else "35%"
    )

    return f"""
    <html><head><meta charset="utf-8"></head>
    <body style="font-family:Arial,Helvetica,sans-serif;font-size:10pt;color:#111;margin:0;padding:10px;">
    <table width="100%" cellspacing="0" cellpadding="0" border="0">
    <tr><td>

        <table width="100%" cellspacing="0" cellpadding="0" border="0" style="margin-bottom:10px;">
            <tr>
                <td width="58%" valign="top" style="line-height:1.5;padding-right:12px;">
                    {encabezado_empresa}
                </td>
                <td width="42%" valign="top" align="right">
                    <table cellspacing="0" cellpadding="8" border="1" style="border-color:#666;background:#fafafa;" align="right" width="92%">
                        <tr>
                            <td align="center" style="line-height:1.35;">
                                <span style="font-size:16pt;font-weight:bold;">{ctx.titulo_documento}</span><br>
                                <span style="font-size:12pt;font-weight:bold;">No. {ctx.cotizacion.numero}</span><br>
                                <span style="font-size:9.5pt;color:#444;">Fecha: {fecha_texto}</span>
                            </td>
                        </tr>
                    </table>
                </td>
            </tr>
        </table>

        <table width="100%" cellspacing="0" cellpadding="0" border="0" style="margin-bottom:10px;">
            <tr>
                {_celda_etiqueta_estandar("Para", ancho="12%")}
                {_celda_valor_estandar(cliente['nombre'], ancho="38%")}
                {_celda_etiqueta_estandar("Nit", ancho="10%")}
                {_celda_valor_estandar(cliente['nit'], ancho="40%")}
            </tr>
            <tr>
                {_celda_etiqueta_estandar("Contacto")}
                {_celda_valor_estandar(cliente['contacto'])}
                {_celda_etiqueta_estandar("Dirección")}
                {_celda_valor_estandar(cliente['direccion'])}
            </tr>
            <tr>
                {_celda_etiqueta_estandar("Ciudad/Tel.")}
                {_celda_valor_estandar(ciudad_tel_cliente)}
                {_celda_etiqueta_estandar("Vendedor")}
                {_celda_valor_estandar(vendedor)}
            </tr>
        </table>

        <table width="100%" cellspacing="0" cellpadding="0" border="0" style="margin-bottom:10px;">
            <tr bgcolor="#ececec" align="center" style="font-size:9pt;font-weight:bold;">
                {columna_imagen}
                <td width="9%" style="padding:5px 2px;border:1px solid #666;">Cód. / SKU</td>
                <td width="4%" style="padding:5px 2px;border:1px solid #666;">Ítem</td>
                <td width="{ancho_descripcion}" style="padding:5px 4px;border:1px solid #666;">Descripción</td>
                <td width="8%" style="padding:5px 2px;border:1px solid #666;">Cant.</td>
                <td width="7%" style="padding:5px 2px;border:1px solid #666;">Und.</td>
                <td width="10%" style="padding:5px 2px;border:1px solid #666;">Vr. Unit.</td>
                <td width="7%" style="padding:5px 2px;border:1px solid #666;">IVA</td>
                <td width="20%" style="padding:5px 2px;border:1px solid #666;">Vr. Total</td>
            </tr>
            {filas}
        </table>

        <table width="100%" cellspacing="0" cellpadding="0" border="0">
            <tr valign="top">
                <td width="54%" style="padding-right:10px;">
                    {bloque_observaciones}
                    {notas_pie}
                    {contacto_pie}
                </td>
                <td width="46%" valign="top">
                    <table width="100%" cellspacing="0" cellpadding="0" border="0">
                        {bloque_totales}
                    </table>
                </td>
            </tr>
        </table>

    </td></tr>
    </table>
    </body></html>
    """


_GENERADORES = {
    "carta": _html_carta,
    "corporativo": _html_corporativo,
    "moderno": _html_moderno,
    "compacto": _html_compacto,
    "tirilla": _html_tirilla,
    "estandar": _html_estandar,
}


def generar_html_cotizacion(
    cotizacion,
    detalles,
    nombre_cliente: str,
    *,
    formato: str | None = None,
) -> str:

    formato = _resolver_formato_codigo(
        formato
        or getattr(
            cotizacion,
            "formato_impresion",
            None,
        ),
    )

    if formato not in _GENERADORES:

        formato = _resolver_formato_codigo(
            ServicioCotizacion.formato_predeterminado(),
        )

    if formato not in _GENERADORES:

        formato = "estandar"

    ctx = _crear_contexto(
        cotizacion,
        detalles,
        nombre_cliente,
    )

    generador = _GENERADORES.get(formato)

    if generador is None:

        generador = _GENERADORES["estandar"]

    return generador(
        ctx,
    )


def generar_html_desde_contexto(
    ctx: ContextoFormato,
    formato: str | None = None,
) -> str:

    codigo = _resolver_formato_codigo(
        formato
        or getattr(
            ctx.cotizacion,
            "formato_impresion",
            None,
        ),
    )

    if codigo not in _GENERADORES:

        codigo = _resolver_formato_codigo(
            ServicioCotizacion.formato_predeterminado(),
        )

    if codigo not in _GENERADORES:

        codigo = "estandar"

    generador = _GENERADORES.get(
        codigo,
    )

    if generador is None:

        generador = _GENERADORES["estandar"]

    return generador(
        ctx,
    )
