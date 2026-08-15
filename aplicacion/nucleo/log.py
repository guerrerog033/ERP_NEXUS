from __future__ import annotations

import logging
import os
from logging.handlers import RotatingFileHandler
from pathlib import Path


_configurado = False


def configurar_logging(
    *,
    nivel: str | None = None,
    directorio: str | Path | None = None,
) -> None:

    global _configurado

    if _configurado:

        return

    nivel_texto = (
        nivel
        or os.getenv(
            "LOG_LEVEL",
            "INFO",
        )
    ).upper()

    nivel_num = getattr(
        logging,
        nivel_texto,
        logging.INFO,
    )

    raiz = Path(
        directorio
        or os.getenv(
            "LOG_DIR",
            "logs",
        ),
    )

    raiz.mkdir(
        parents=True,
        exist_ok=True,
    )

    formato = logging.Formatter(
        "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )

    logger_raiz = logging.getLogger(
        "nexus",
    )

    logger_raiz.setLevel(
        nivel_num,
    )

    if not logger_raiz.handlers:

        consola = logging.StreamHandler()

        consola.setFormatter(
            formato,
        )

        logger_raiz.addHandler(
            consola,
        )

        archivo = RotatingFileHandler(
            raiz
            / "erp.log",
            maxBytes=2_000_000,
            backupCount=5,
            encoding="utf-8",
        )

        archivo.setFormatter(
            formato,
        )

        logger_raiz.addHandler(
            archivo,
        )

        errores = RotatingFileHandler(
            raiz
            / "errores.log",
            maxBytes=2_000_000,
            backupCount=5,
            encoding="utf-8",
        )

        errores.setLevel(
            logging.ERROR,
        )

        errores.setFormatter(
            formato,
        )

        logger_raiz.addHandler(
            errores,
        )

    _configurado = True


def obtener_logger(
    nombre: str,
) -> logging.Logger:

    if not _configurado:

        configurar_logging()

    if not nombre.startswith(
        "nexus.",
    ):

        nombre = f"nexus.{nombre}"

    return logging.getLogger(
        nombre,
    )
