"""
Puente entre migraciones incrementales legacy y Alembic.

Flujo al iniciar la aplicación:

1. Migraciones legacy (``ejecutar_migraciones``) para bases existentes.
2. ``alembic upgrade head`` para revisiones posteriores al baseline.
"""

from __future__ import annotations


def aplicar_esquema() -> None:
    """
    Aplica migraciones legacy y revisiones Alembic pendientes.
    """

    from aplicacion.nucleo.log import (
        obtener_logger,
    )

    logger = obtener_logger(
        "migraciones",
    )

    from aplicacion.base_datos.migraciones import (
        ejecutar_migraciones,
    )

    ejecutar_migraciones()

    try:

        from alembic import command
        from alembic.config import Config

        config = Config(
            "alembic.ini",
        )

        command.upgrade(
            config,
            "head",
        )

        logger.info(
            "Alembic upgrade head completado.",
        )

    except Exception as error:

        logger.warning(
            "Alembic upgrade omitido: %s",
            error,
        )
