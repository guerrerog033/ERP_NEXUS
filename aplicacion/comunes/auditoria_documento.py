from __future__ import annotations

from aplicacion.nucleo.auditoria_campos import (
    AuditoriaCampos,
)
from aplicacion.nucleo.sesion import Sesion

CAMPOS_LINEA_DEFAULT = [
    "producto_id",
    "descripcion",
    "cantidad",
    "precio_unitario",
    "total_linea",
]


def _campos_cabecera_auditoria(
    servicio,
    cabecera: dict,
) -> list[str]:

    incluir = getattr(
        servicio,
        "auditoria_campos_cabecera",
        None,
    )

    excluir = set(
        getattr(
            servicio,
            "auditoria_campos_cabecera_excluir",
            None,
        )
        or [],
    )

    if incluir is not None:

        return [
            campo
            for campo in incluir
            if campo in cabecera
        ]

    return [
        campo
        for campo in cabecera.keys()
        if campo not in excluir
    ]


def _linea_a_dict(
    linea,
    campos: list[str] | None = None,
) -> dict:

    nombres = campos or CAMPOS_LINEA_DEFAULT

    if isinstance(
        linea,
        dict,
    ):

        return {
            campo: linea.get(
                campo,
            )
            for campo in nombres
            if campo in linea
        }

    return {
        campo: getattr(
            linea,
            campo,
            None,
        )
        for campo in nombres
        if hasattr(
            linea,
            campo,
        )
    }


def auditar_cabecera_antes(
    servicio,
    id_registro: int | None,
    cabecera: dict,
) -> dict:

    if (
        id_registro is None
        or not getattr(
            servicio,
            "entidad_auditoria",
            "",
        )
    ):

        return {}

    registro = servicio.obtener_por_id(
        id_registro,
    )

    if registro is None:

        return {}

    return AuditoriaCampos.detectar_cambios(
        registro,
        cabecera,
        campos=_campos_cabecera_auditoria(
            servicio,
            cabecera,
        ),
    )


def auditar_lineas_antes(
    servicio,
    id_registro: int | None,
    lineas_nuevas: list,
    *,
    campos: list[str] | None = None,
) -> dict:

    if (
        id_registro is None
        or not getattr(
            servicio,
            "entidad_auditoria",
            "",
        )
        or not hasattr(
            servicio,
            "obtener_completa",
        )
    ):

        return {}

    completo = servicio.obtener_completa(
        id_registro,
    )

    if completo is None:

        return {}

    lineas_viejas = getattr(
        completo,
        "detalles",
        None,
    ) or []

    nombres = (
        campos
        or getattr(
            servicio,
            "auditoria_campos_linea",
            None,
        )
        or CAMPOS_LINEA_DEFAULT
    )

    cambios: dict = {}

    max_filas = max(
        len(
            lineas_viejas,
        ),
        len(
            lineas_nuevas or [],
        ),
    )

    for indice in range(
        max_filas,
    ):

        vieja = (
            _linea_a_dict(
                lineas_viejas[
                    indice
                ],
                nombres,
            )
            if indice
            < len(
                lineas_viejas,
            )
            else {}
        )

        nueva = (
            _linea_a_dict(
                lineas_nuevas[
                    indice
                ],
                nombres,
            )
            if indice
            < len(
                lineas_nuevas or [],
            )
            else {}
        )

        if (
            not vieja
            and nueva
        ):

            cambios[
                f"linea[{indice}]"
            ] = (
                None,
                "agregada",
            )

            continue

        if (
            vieja
            and not nueva
        ):

            cambios[
                f"linea[{indice}]"
            ] = (
                "existente",
                "eliminada",
            )

            continue

        for campo in nombres:

            clave = (
                f"linea[{indice}].{campo}"
            )

            anterior = vieja.get(
                campo,
            )

            nuevo = nueva.get(
                campo,
            )

            if anterior != nuevo:

                cambios[
                    clave
                ] = (
                    anterior,
                    nuevo,
                )

    return cambios


def auditar_documento_antes(
    servicio,
    id_registro: int | None,
    cabecera: dict,
    lineas: list | None = None,
) -> dict:

    cambios = auditar_cabecera_antes(
        servicio,
        id_registro,
        cabecera,
    )

    if lineas is not None:

        campos_linea = getattr(
            servicio,
            "auditoria_campos_linea",
            None,
        )

        cambios.update(
            auditar_lineas_antes(
                servicio,
                id_registro,
                lineas,
                campos=campos_linea,
            ),
        )

    return cambios


def registrar_auditoria_cabecera(
    servicio,
    id_registro: int,
    cambios: dict,
) -> None:

    if (
        not cambios
        or not getattr(
            servicio,
            "entidad_auditoria",
            "",
        )
    ):

        return

    AuditoriaCampos.registrar_cambios(
        usuario=Sesion.usuario(),
        entidad=servicio.entidad_auditoria,
        entidad_id=id_registro,
        cambios=cambios,
        modulo=getattr(
            servicio,
            "modulo_auditoria",
            "",
        ),
    )
