from aplicacion.base_datos.conexion import engine
from aplicacion.base_datos.modelos import Base


def crear_tablas():
    Base.metadata.create_all(bind=engine)