from logging.config import fileConfig

from alembic import context
from sqlalchemy import engine_from_config, pool

from aplicacion.base_datos.conexion import (
    Base,
    URL_BD,
)

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

config.set_main_option(
    "sqlalchemy.url",
    URL_BD.replace(
        "%",
        "%%",
    ),
)

target_metadata = Base.metadata


def importar_modelos() -> None:
    """
    Registra todos los modelos ORM para autogenerate.

    Mantener alineado con ``aplicacion.base_datos.registro_modelos``.
    """

    from aplicacion.base_datos.registro_modelos import (
        importar_modelos as registrar,
    )

    registrar()


def run_migrations_offline() -> None:

    importar_modelos()

    url = config.get_main_option(
        "sqlalchemy.url",
    )

    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={
            "paramstyle": "named",
        },
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:

    importar_modelos()

    connectable = engine_from_config(
        config.get_section(
            config.config_ini_section,
            {},
        ),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
