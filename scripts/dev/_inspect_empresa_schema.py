from sqlalchemy import inspect

from aplicacion.base_datos.conexion import engine

inspector = inspect(engine)

for columna in inspector.get_columns("empresa"):
    print(
        columna["name"],
        "-",
        columna["type"]
    )