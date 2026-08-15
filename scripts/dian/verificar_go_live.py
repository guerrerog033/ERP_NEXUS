#!/usr/bin/env python
from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from aplicacion.integraciones.dian.go_live import (  # noqa: E402
    ValidadorGoLiveDian,
)


def main() -> int:

    parser = argparse.ArgumentParser(
        description=(
            "Verifica requisitos DIAN antes del go-live."
        ),
    )

    parser.add_argument(
        "--ambiente",
        choices=(
            "habilitacion",
            "produccion",
        ),
        default="produccion",
        help="Ambiente objetivo a validar",
    )

    args = parser.parse_args()

    if args.ambiente == "habilitacion":

        resultado = (
            ValidadorGoLiveDian.verificar_habilitacion()
        )

    else:

        resultado = (
            ValidadorGoLiveDian.verificar_produccion()
        )

    print(
        ValidadorGoLiveDian.resumen_texto(
            resultado,
        ),
    )

    return 0 if resultado["listo"] else 1


if __name__ == "__main__":

    raise SystemExit(
        main(),
    )
