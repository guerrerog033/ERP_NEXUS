from __future__ import annotations

from aplicacion.base_datos.conexion import (
    Base,
    engine,
)
from aplicacion.base_datos.registro_modelos import (
    importar_modelos,
)


def crear_tablas() -> None:
    """
    Crea todas las tablas registradas en ``Base.metadata``.

    Uso previsto: scripts de desarrollo (``crear_bd.py``).
    En producción preferir ``startup.inicializar_sistema()`` + Alembic.
    """

    importar_modelos()

    Base.metadata.create_all(
        bind=engine,
    )

    print(
        "Base de datos creada correctamente.",
    )
