from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv
from urllib.parse import quote_plus
import os

load_dotenv()


def _parametro(
    nombre_env: str,
    valor_defecto,
):

    valor = os.getenv(
        nombre_env,
    )

    if (
        valor is not None
        and str(
            valor,
        ).strip()
    ):

        return valor

    return valor_defecto


def obtener_parametros_bd() -> dict:

    from aplicacion.base_datos import (
        configuracion as cfg,
    )

    return {
        "host": _parametro(
            "DB_HOST",
            cfg.DB_HOST,
        ),
        "port": int(
            _parametro(
                "DB_PORT",
                cfg.DB_PORT,
            ),
        ),
        "dbname": _parametro(
            "DB_NAME",
            cfg.DB_NAME,
        ),
        "user": _parametro(
            "DB_USER",
            cfg.DB_USER,
        ),
        "password": _parametro(
            "DB_PASSWORD",
            cfg.DB_PASSWORD,
        ),
    }


_params = obtener_parametros_bd()

DB_HOST = _params["host"]
DB_PORT = _params["port"]
DB_NAME = _params["dbname"]
DB_USER = _params["user"]
DB_PASSWORD = quote_plus(
    _params["password"] or "",
)

URL_BD = (
    f"postgresql+psycopg://{DB_USER}:{DB_PASSWORD}"
    f"@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)

engine = create_engine(
    URL_BD,
    echo=False,
    future=True,
    connect_args={
        "connect_timeout": 10,
    },
    pool_pre_ping=True,
    pool_timeout=10,
    pool_reset_on_return="rollback",
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)

Base = declarative_base()


def probar_conexion() -> None:

    import psycopg

    params = obtener_parametros_bd()

    try:

        with psycopg.connect(
            host=params["host"],
            port=params["port"],
            dbname=params["dbname"],
            user=params["user"],
            password=params["password"],
            connect_timeout=5,
        ) as conexion:

            conexion.execute(
                "SELECT 1",
            )

    except Exception as error:

        raise RuntimeError(
            "No se pudo conectar con PostgreSQL "
            f"({params['host']}:{params['port']}/"
            f"{params['dbname']}).\n\n"
            "Verifique que el servicio PostgreSQL "
            "esté activo y que el archivo .env "
            "tenga los datos correctos."
        ) from error
