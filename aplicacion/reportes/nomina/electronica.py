from __future__ import annotations

from aplicacion.reportes.comunes.datos_contabilidad import (
    _formatear_monto,
    reporte_tabular_a_dto,
)
from aplicacion.reportes.comunes.datos_documento import (
    _autorizacion_dian,
    url_qr_dian,
)


def nomina_electronica_a_dto(
    *,
    numero: str,
    periodo: str,
    cune: str,
    totales: dict,
    trabajadores: list[dict],
    estado_dian: str = "",
) -> dict:

    columnas = [
        "Documento",
        "Empleado",
        "Devengado",
        "Deducciones",
        "Neto",
    ]

    filas_pdf: list[list[str]] = []

    for fila in trabajadores:

        filas_pdf.append(
            [
                str(
                    fila.get(
                        "documento",
                        "",
                    ),
                ),
                str(
                    fila.get(
                        "empleado",
                        "",
                    ),
                ),
                _formatear_monto(
                    fila.get(
                        "devengado",
                        0,
                    ),
                ),
                _formatear_monto(
                    fila.get(
                        "deducciones",
                        0,
                    ),
                ),
                _formatear_monto(
                    fila.get(
                        "neto",
                        0,
                    ),
                ),
            ],
        )

    filas_pdf.append(
        [
            "",
            "Totales",
            _formatear_monto(
                totales.get(
                    "devengado",
                    0,
                ),
            ),
            _formatear_monto(
                totales.get(
                    "deducciones",
                    0,
                ),
            ),
            _formatear_monto(
                totales.get(
                    "neto",
                    0,
                ),
            ),
        ],
    )

    cune_limpio = str(
        cune or "",
    ).strip()

    pie_partes = [
        f"CUNE: {cune_limpio}",
        f"Valor total nómina: {_formatear_monto(totales.get('neto', 0))}",
        f"Aportes patronales: {_formatear_monto(totales.get('aportes', 0))}",
    ]

    if estado_dian:

        pie_partes.append(
            f"Estado DIAN: {estado_dian}",
        )

    qr_url = url_qr_dian(
        cune_limpio,
    )

    if qr_url:

        pie_partes.append(
            f"Consulta: {qr_url}",
        )

    autorizacion = _autorizacion_dian(
        None,
    )

    if autorizacion:

        pie_partes.insert(
            1,
            f"Autorización DIAN: {autorizacion}",
        )

    return reporte_tabular_a_dto(
        titulo="Nómina electrónica",
        numero=numero,
        subtitulo=(
            f"Periodo {periodo} · "
            f"{len(trabajadores)} trabajador(es)"
        ),
        columnas=columnas,
        filas=filas_pdf,
        pie=" · ".join(
            pie_partes,
        ),
    )
