from __future__ import annotations

from datetime import date, datetime


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


def _formatear_monto(
    valor,
) -> str:

    return f"{float(valor or 0):,.2f}"


def reporte_tabular_a_dto(
    *,
    titulo: str,
    numero: str,
    subtitulo: str = "",
    columnas: list[str],
    filas: list[list[str]],
    pie: str = "",
) -> dict:

    return {
        "titulo": titulo,
        "numero": numero,
        "subtitulo": subtitulo,
        "columnas": columnas,
        "filas": filas,
        "pie": pie,
    }


def comprobante_contable_a_dto(
    asiento,
) -> dict:

    lineas: list[dict] = []

    for indice, detalle in enumerate(
        asiento.detalles,
        start=1,
    ):

        cuenta = getattr(
            detalle,
            "cuenta",
            None,
        )

        lineas.append(
            {
                "numero": indice,
                "codigo": str(
                    cuenta.codigo
                    if cuenta
                    else "",
                ),
                "cuenta": str(
                    cuenta.nombre
                    if cuenta
                    else "",
                ),
                "debito": float(
                    detalle.debito or 0,
                ),
                "credito": float(
                    detalle.credito or 0,
                ),
                "detalle": str(
                    detalle.descripcion or "",
                ),
            },
        )

    return {
        "numero": str(
            asiento.numero or "",
        ),
        "fecha": _formatear_fecha(
            getattr(
                asiento,
                "fecha",
                None,
            ),
        ),
        "origen": str(
            getattr(
                asiento,
                "origen",
                "",
            )
            or "",
        ),
        "descripcion": str(
            getattr(
                asiento,
                "descripcion",
                "",
            )
            or "",
        ).strip(),
        "lineas": lineas,
        "total_debito": float(
            asiento.total_debito or 0,
        ),
        "total_credito": float(
            asiento.total_credito or 0,
        ),
    }


def balance_prueba_a_dto(
    resultado: dict,
    *,
    periodo: str,
) -> dict:

    columnas = [
        "Código",
        "Cuenta",
        "Débito",
        "Crédito",
        "Saldo",
    ]

    filas_pdf: list[list[str]] = []

    for fila in resultado.get(
        "filas",
        [],
    ):

        filas_pdf.append(
            [
                str(
                    fila.get(
                        "codigo",
                        "",
                    ),
                ),
                str(
                    fila.get(
                        "nombre",
                        "",
                    ),
                ),
                _formatear_monto(
                    fila.get(
                        "debito",
                        0,
                    ),
                ),
                _formatear_monto(
                    fila.get(
                        "credito",
                        0,
                    ),
                ),
                _formatear_monto(
                    fila.get(
                        "saldo",
                        0,
                    ),
                ),
            ],
        )

    total_debito = float(
        resultado.get(
            "total_debito",
            0,
        )
        or 0,
    )

    total_credito = float(
        resultado.get(
            "total_credito",
            0,
        )
        or 0,
    )

    filas_pdf.append(
        [
            "",
            "Totales",
            _formatear_monto(
                total_debito,
            ),
            _formatear_monto(
                total_credito,
            ),
            _formatear_monto(
                total_debito
                - total_credito,
            ),
        ],
    )

    return reporte_tabular_a_dto(
        titulo="Balance de prueba",
        numero=periodo,
        subtitulo="Movimientos por cuenta contable",
        columnas=columnas,
        filas=filas_pdf,
    )


def estado_cuenta_a_dto(
    resultado: dict,
    *,
    titulo: str,
    subtitulo: str,
) -> dict:

    columnas = [
        "Fecha",
        "Documento",
        "Tipo",
        "Débito",
        "Crédito",
        "Saldo",
        "Referencia",
    ]

    filas_pdf: list[list[str]] = []

    for movimiento in resultado.get(
        "movimientos",
        [],
    ):

        filas_pdf.append(
            [
                _formatear_fecha(
                    movimiento.get(
                        "fecha",
                    ),
                ),
                str(
                    movimiento.get(
                        "documento",
                        "",
                    ),
                ),
                str(
                    movimiento.get(
                        "tipo",
                        "",
                    ),
                ),
                _formatear_monto(
                    movimiento.get(
                        "debito",
                        0,
                    ),
                ),
                _formatear_monto(
                    movimiento.get(
                        "credito",
                        0,
                    ),
                ),
                _formatear_monto(
                    movimiento.get(
                        "saldo",
                        0,
                    ),
                ),
                str(
                    movimiento.get(
                        "referencia",
                        "",
                    ),
                ),
            ],
        )

    pie = (
        f"Saldo final: "
        f"{_formatear_monto(resultado.get('saldo_final', 0))}"
    )

    return reporte_tabular_a_dto(
        titulo=titulo,
        numero=str(
            resultado.get(
                "tercero",
                "",
            ),
        ),
        subtitulo=subtitulo,
        columnas=columnas,
        filas=filas_pdf,
        pie=pie,
    )


def libro_mayor_a_dto(
    resultado: dict,
    *,
    periodo: str,
) -> dict:

    cuenta = resultado.get(
        "cuenta",
    )

    codigo = str(
        getattr(
            cuenta,
            "codigo",
            "",
        )
        or "",
    )

    nombre = str(
        getattr(
            cuenta,
            "nombre",
            "",
        )
        or "",
    )

    columnas = [
        "Fecha",
        "Comprobante",
        "Descripción",
        "Débito",
        "Crédito",
        "Saldo",
    ]

    filas_pdf: list[list[str]] = []

    for fila in resultado.get(
        "filas",
        [],
    ):

        filas_pdf.append(
            [
                _formatear_fecha(
                    fila.get(
                        "fecha",
                    ),
                ),
                str(
                    fila.get(
                        "numero",
                        "",
                    ),
                ),
                str(
                    fila.get(
                        "descripcion",
                        "",
                    )
                    or "",
                ),
                _formatear_monto(
                    fila.get(
                        "debito",
                        0,
                    ),
                ),
                _formatear_monto(
                    fila.get(
                        "credito",
                        0,
                    ),
                ),
                _formatear_monto(
                    fila.get(
                        "saldo",
                        0,
                    ),
                ),
            ],
        )

    pie = ""

    filas = resultado.get(
        "filas",
        [],
    )

    if filas:

        pie = (
            f"Saldo final: "
            f"{_formatear_monto(filas[-1].get('saldo', 0))}"
        )

    return reporte_tabular_a_dto(
        titulo="Libro mayor",
        numero=f"{codigo} — {nombre}",
        subtitulo=periodo,
        columnas=columnas,
        filas=filas_pdf,
        pie=pie,
    )


def estado_resultados_a_dto(
    resultado: dict,
    *,
    periodo: str,
) -> dict:

    columnas = [
        "Código",
        "Cuenta",
        "Valor",
    ]

    filas_pdf: list[list[str]] = []

    def _agregar_seccion(
        titulo: str,
        filas: list[dict],
        total: float,
    ) -> None:

        filas_pdf.append(
            [
                "",
                titulo,
                "",
            ],
        )

        for fila in filas:

            filas_pdf.append(
                [
                    str(
                        fila.get(
                            "codigo",
                            "",
                        ),
                    ),
                    str(
                        fila.get(
                            "nombre",
                            "",
                        ),
                    ),
                    _formatear_monto(
                        fila.get(
                            "valor",
                            0,
                        ),
                    ),
                ],
            )

        filas_pdf.append(
            [
                "",
                f"Total {titulo.lower()}",
                _formatear_monto(
                    total,
                ),
            ],
        )

        filas_pdf.append(
            [
                "",
                "",
                "",
            ],
        )

    _agregar_seccion(
        "Ingresos",
        resultado.get(
            "ingresos",
            [],
        ),
        float(
            resultado.get(
                "total_ingresos",
                0,
            )
            or 0,
        ),
    )

    _agregar_seccion(
        "Costos de venta",
        resultado.get(
            "costos_venta",
            [],
        ),
        float(
            resultado.get(
                "total_costos_venta",
                0,
            )
            or 0,
        ),
    )

    utilidad_bruta = float(
        resultado.get(
            "utilidad_bruta",
            0,
        )
        or 0,
    )

    filas_pdf.append(
        [
            "",
            "Utilidad bruta",
            _formatear_monto(
                utilidad_bruta,
            ),
        ],
    )

    filas_pdf.append(
        [
            "",
            "",
            "",
        ],
    )

    _agregar_seccion(
        "Gastos operacionales",
        resultado.get(
            "gastos",
            [],
        ),
        float(
            resultado.get(
                "total_gastos",
                0,
            )
            or 0,
        ),
    )

    if filas_pdf:

        filas_pdf.pop()

    utilidad = float(
        resultado.get(
            "utilidad_neta",
            0,
        )
        or 0,
    )

    filas_pdf.append(
        [
            "",
            "Utilidad neta",
            _formatear_monto(
                utilidad,
            ),
        ],
    )

    pie = (
        f"Ingresos: {_formatear_monto(resultado.get('total_ingresos', 0))} · "
        f"Costos venta: {_formatear_monto(resultado.get('total_costos_venta', 0))} · "
        f"Utilidad bruta: {_formatear_monto(utilidad_bruta)} · "
        f"Gastos: {_formatear_monto(resultado.get('total_gastos', 0))} · "
        f"Utilidad neta: {_formatear_monto(utilidad)}"
    )

    return reporte_tabular_a_dto(
        titulo="Estado de resultados",
        numero=periodo,
        subtitulo="Ingresos y gastos del periodo",
        columnas=columnas,
        filas=filas_pdf,
        pie=pie,
    )
