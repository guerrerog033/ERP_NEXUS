from __future__ import annotations

from contextlib import contextmanager
from typing import Iterator

from sqlalchemy.orm import Session

from aplicacion.base_datos.conexion import (
    SessionLocal,
)


@contextmanager
def transaccion_negocio(
    *,
    sesion: Session | None = None,
) -> Iterator[Session]:

    db = sesion or SessionLocal()

    propia = sesion is None

    try:

        yield db

        if propia:

            db.commit()

    except Exception:

        if propia:

            db.rollback()

        raise

    finally:

        if propia:

            db.close()
