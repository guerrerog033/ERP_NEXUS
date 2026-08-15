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
        from alembic.runtime.migration import MigrationContext

        from aplicacion.base_datos.conexion import engine

        config = Config(
            "alembic.ini",
        )

        with engine.connect() as conexion:

            revision_actual = MigrationContext.configure(
                conexion,
            ).get_current_revision()

        if revision_actual is None:

            # Base nueva: el esquema ya lo creó create_all() (o la
            # migración legacy) más arriba, así que no hay DDL que
            # repetir — solo se marca alembic_version en "head" para
            # que futuras revisiones incrementales arranquen desde
            # el punto correcto.
            command.stamp(
                config,
                "head",
            )

            logger.info(
                "Alembic stamp head (base nueva).",
            )

        else:

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
