from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from decimal import Decimal


@dataclass
class EmpresaDatos:

    nombre: str = ""
    razon_social: str = ""
    nit: str = ""
    dv: str = ""

    direccion: str = ""
    ciudad: str = ""
    departamento: str = ""

    telefono: str = ""
    celular: str = ""
    correo: str = ""
    sitio_web: str = ""

    logo: str | None = None


@dataclass
class TerceroDatos:

    nombre: str = ""
    documento: str = ""
    dv: str = ""

    direccion: str = ""
    ciudad: str = ""
    departamento: str = ""

    telefono: str = ""
    correo: str = ""


@dataclass
class ItemDocumento:

    codigo: str = ""
    descripcion: str = ""

    cantidad: Decimal = Decimal("0")
    unidad: str = ""
    precio: Decimal = Decimal("0")

    descuento: Decimal = Decimal("0")
    impuesto: Decimal = Decimal("0")

    total: Decimal = Decimal("0")


@dataclass
class TotalesDocumento:

    subtotal: Decimal = Decimal("0")
    descuento: Decimal = Decimal("0")

    base_gravable: Decimal = Decimal("0")
    impuesto: Decimal = Decimal("0")

    total: Decimal = Decimal("0")
    total_letras: str = ""


@dataclass
class DocumentoDatos:

    tipo: str = ""
    codigo_catalogo: str = ""

    numero: str = ""

    fecha: date | None = None
    vencimiento: date | None = None

    empresa: EmpresaDatos = field(
        default_factory=EmpresaDatos,
    )

    tercero: TerceroDatos = field(
        default_factory=TerceroDatos,
    )

    items: list[ItemDocumento] = field(
        default_factory=list,
    )

    totales: TotalesDocumento = field(
        default_factory=TotalesDocumento,
    )

    forma_pago: str = ""
    medio_pago: str = ""

    observaciones: str = ""
    condiciones: str = ""

    moneda: str = "COP"

    cufe: str = ""
    qr_url: str = ""
    autorizacion: str = ""

    estado_dian: str = ""
    fecha_validacion_dian: str = ""

    resolucion: str = ""

    metadata: dict = field(
        default_factory=dict,
    )


def _decimal(
    valor,
) -> Decimal:

    if valor is None:

        return Decimal("0")

    return Decimal(
        str(
            valor,
        ),
    )


def dict_a_documento_datos(
    payload: dict,
    *,
    tipo: str = "",
    codigo_catalogo: str = "",
) -> DocumentoDatos:

    empresa_raw = payload.get(
        "empresa",
        {},
    ) or {}

    if not isinstance(
        empresa_raw,
        dict,
    ):

        empresa_raw = {}

    cliente_raw = payload.get(
        "cliente",
        payload.get(
            "tercero",
            {},
        ),
    ) or {}

    if not isinstance(
        cliente_raw,
        dict,
    ):

        cliente_raw = {}

    items_raw = payload.get(
        "items",
        [],
    ) or []

    items: list[ItemDocumento] = []

    for fila in items_raw:

        if not isinstance(
            fila,
            dict,
        ):

            continue

        items.append(
            ItemDocumento(
                codigo=str(
                    fila.get(
                        "codigo",
                        fila.get(
                            "numero",
                            "",
                        ),
                    )
                    or "",
                ),
                descripcion=str(
                    fila.get(
                        "descripcion",
                        "",
                    )
                    or "",
                ),
                cantidad=_decimal(
                    fila.get(
                        "cantidad",
                        0,
                    ),
                ),
                unidad=str(
                    fila.get(
                        "unidad",
                        "",
                    )
                    or "",
                ),
                precio=_decimal(
                    fila.get(
                        "precio",
                        0,
                    ),
                ),
                descuento=_decimal(
                    fila.get(
                        "descuento",
                        0,
                    ),
                ),
                impuesto=_decimal(
                    fila.get(
                        "impuestos",
                        fila.get(
                            "impuesto",
                            0,
                        ),
                    ),
                ),
                total=_decimal(
                    fila.get(
                        "total",
                        0,
                    ),
                ),
            ),
        )

    subtotal = _decimal(
        payload.get(
            "subtotal",
            0,
        ),
    )

    descuento = _decimal(
        payload.get(
            "descuento",
            0,
        ),
    )

    impuestos = _decimal(
        payload.get(
            "impuestos",
            payload.get(
                "impuesto",
                0,
            ),
        ),
    )

    total = _decimal(
        payload.get(
            "total",
            0,
        ),
    )

    return DocumentoDatos(
        tipo=tipo
        or str(
            payload.get(
                "tipo",
                "",
            )
            or "",
        ),
        codigo_catalogo=codigo_catalogo,
        numero=str(
            payload.get(
                "numero",
                "",
            )
            or "",
        ),
        empresa=EmpresaDatos(
            nombre=str(
                empresa_raw.get(
                    "nombre",
                    "",
                )
                or empresa_raw.get(
                    "razon_social",
                    "",
                )
                or "",
            ),
            razon_social=str(
                empresa_raw.get(
                    "razon_social",
                    empresa_raw.get(
                        "nombre",
                        "",
                    ),
                )
                or "",
            ),
            nit=str(
                empresa_raw.get(
                    "nit",
                    "",
                )
                or "",
            ),
            dv=str(
                empresa_raw.get(
                    "dv",
                    "",
                )
                or "",
            ),
            direccion=str(
                empresa_raw.get(
                    "direccion",
                    "",
                )
                or "",
            ),
            ciudad=str(
                empresa_raw.get(
                    "ciudad",
                    "",
                )
                or "",
            ),
            departamento=str(
                empresa_raw.get(
                    "departamento",
                    "",
                )
                or "",
            ),
            telefono=str(
                empresa_raw.get(
                    "telefono",
                    "",
                )
                or "",
            ),
            correo=str(
                empresa_raw.get(
                    "correo",
                    "",
                )
                or "",
            ),
            logo=empresa_raw.get(
                "logo",
            ),
        ),
        tercero=TerceroDatos(
            nombre=str(
                cliente_raw.get(
                    "nombre",
                    "",
                )
                or "",
            ),
            documento=str(
                cliente_raw.get(
                    "documento",
                    cliente_raw.get(
                        "nit",
                        "",
                    ),
                )
                or "",
            ),
            dv=str(
                cliente_raw.get(
                    "dv",
                    "",
                )
                or "",
            ),
            direccion=str(
                cliente_raw.get(
                    "direccion",
                    "",
                )
                or "",
            ),
            ciudad=str(
                cliente_raw.get(
                    "ciudad",
                    "",
                )
                or "",
            ),
            departamento=str(
                cliente_raw.get(
                    "departamento",
                    "",
                )
                or "",
            ),
            telefono=str(
                cliente_raw.get(
                    "telefono",
                    "",
                )
                or "",
            ),
            correo=str(
                cliente_raw.get(
                    "correo",
                    "",
                )
                or "",
            ),
        ),
        items=items,
        totales=TotalesDocumento(
            subtotal=subtotal,
            descuento=descuento,
            base_gravable=subtotal - descuento,
            impuesto=impuestos,
            total=total,
            total_letras=str(
                payload.get(
                    "total_letras",
                    "",
                )
                or "",
            ),
        ),
        forma_pago=str(
            payload.get(
                "forma_pago",
                "",
            )
            or "",
        ),
        medio_pago=str(
            payload.get(
                "medio_pago",
                "",
            )
            or "",
        ),
        observaciones=str(
            payload.get(
                "observaciones",
                "",
            )
            or "",
        ),
        condiciones=str(
            payload.get(
                "condiciones",
                payload.get(
                    "condiciones_comerciales",
                    "",
                ),
            )
            or "",
        ),
        cufe=str(
            payload.get(
                "cufe",
                "",
            )
            or "",
        ),
        qr_url=str(
            payload.get(
                "qr_url",
                "",
            )
            or "",
        ),
        autorizacion=str(
            payload.get(
                "autorizacion",
                payload.get(
                    "resolucion",
                    "",
                ),
            )
            or "",
        ),
        estado_dian=str(
            payload.get(
                "estado_dian",
                "",
            )
            or "",
        ),
        fecha_validacion_dian=str(
            payload.get(
                "fecha_validacion_dian",
                "",
            )
            or "",
        ),
        metadata={
            key: value
            for key, value in payload.items()
            if key
            not in {
                "empresa",
                "cliente",
                "tercero",
                "items",
            }
        },
    )


def documento_datos_a_dict(
    datos: DocumentoDatos,
) -> dict:

    return {
        "tipo": datos.tipo,
        "numero": datos.numero,
        "fecha": datos.metadata.get(
            "fecha_generacion",
            datos.metadata.get(
                "fecha",
                "",
            ),
        ),
        "fecha_generacion": datos.metadata.get(
            "fecha_generacion",
            "",
        ),
        "fecha_vencimiento": datos.metadata.get(
            "fecha_vencimiento",
            "",
        ),
        "forma_pago": datos.forma_pago,
        "medio_pago": datos.medio_pago,
        "subtotal": float(
            datos.totales.subtotal,
        ),
        "descuento": float(
            datos.totales.descuento,
        ),
        "impuestos": float(
            datos.totales.impuesto,
        ),
        "total": float(
            datos.totales.total,
        ),
        "total_letras": datos.totales.total_letras,
        "observaciones": datos.observaciones,
        "condiciones_comerciales": datos.condiciones,
        "cufe": datos.cufe,
        "qr_url": datos.qr_url,
        "autorizacion": datos.autorizacion,
        "estado_dian": datos.estado_dian,
        "fecha_validacion_dian": datos.fecha_validacion_dian,
        "empresa": {
            "nombre": datos.empresa.nombre,
            "razon_social": datos.empresa.razon_social,
            "nit": datos.empresa.nit,
            "dv": datos.empresa.dv,
            "direccion": datos.empresa.direccion,
            "ciudad": datos.empresa.ciudad,
            "departamento": datos.empresa.departamento,
            "telefono": datos.empresa.telefono,
            "correo": datos.empresa.correo,
            "logo": datos.empresa.logo,
        },
        "cliente": {
            "nombre": datos.tercero.nombre,
            "documento": datos.tercero.documento,
            "dv": datos.tercero.dv,
            "direccion": datos.tercero.direccion,
            "ciudad": datos.tercero.ciudad,
            "departamento": datos.tercero.departamento,
            "telefono": datos.tercero.telefono,
            "correo": datos.tercero.correo,
        },
        "items": [
            {
                "numero": indice,
                "codigo": item.codigo,
                "descripcion": item.descripcion,
                "cantidad": float(
                    item.cantidad,
                ),
                "unidad": item.unidad,
                "precio": float(
                    item.precio,
                ),
                "descuento": float(
                    item.descuento,
                ),
                "impuestos": float(
                    item.impuesto,
                ),
                "total": float(
                    item.total,
                ),
            }
            for indice, item in enumerate(
                datos.items,
                start=1,
            )
        ],
        **datos.metadata,
    }
