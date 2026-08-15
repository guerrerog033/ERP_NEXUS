from __future__ import annotations

import argparse

from aplicacion.licencias.servicios import (
    registrar_serial_catalogo,
)
from aplicacion.licencias.validador import (
    generar_serial,
    normalizar_serial,
)
from aplicacion.nucleo.configuracion import Configuracion


def _secreto() -> str:

    config = (
        Configuracion.obtener(
            "licencias",
        )
        or {}
    )

    return str(
        config.get(
            "secreto_validacion",
            "erp-nexus-dev-secret",
        ),
    )


def main() -> None:

    parser = argparse.ArgumentParser(
        description=(
            "Genera seriales de licencia ERP NEXUS."
        ),
    )

    parser.add_argument(
        "--edicion",
        required=True,
        choices=[
            "trial",
            "starter",
            "profesional",
            "empresarial",
        ],
    )

    parser.add_argument(
        "--dias",
        type=int,
        help=(
            "Días de validez desde la activación "
            "(0 = perpetua)."
        ),
    )

    parser.add_argument(
        "--titular",
        default="",
        help="Nombre del cliente.",
    )

    parser.add_argument(
        "--cantidad",
        type=int,
        default=1,
        help="Cantidad de seriales a generar.",
    )

    parser.add_argument(
        "--registrar",
        action="store_true",
        help=(
            "Registra el serial en la base de datos."
        ),
    )

    args = parser.parse_args()

    secreto = _secreto()

    for _ in range(
        max(
            1,
            args.cantidad,
        ),
    ):

        serial = generar_serial(
            args.edicion,
            dias=args.dias,
            secreto=secreto,
        )

        serial = normalizar_serial(
            serial,
        )

        print(serial)

        if args.registrar:

            registrar_serial_catalogo(
                serial,
                edicion=args.edicion,
                titular=args.titular,
                dias_validez=args.dias,
            )


if __name__ == "__main__":

    main()
