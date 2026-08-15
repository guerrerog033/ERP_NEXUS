import psycopg

from aplicacion.base_datos.conexion import (
    obtener_parametros_bd,
)


def conexion_admin():

    params = obtener_parametros_bd()

    conexion = psycopg.connect(
        host=params["host"],
        port=params["port"],
        dbname=params["dbname"],
        user=params["user"],
        password=params["password"],
        connect_timeout=5,
    )

    conexion.autocommit = True

    return conexion
