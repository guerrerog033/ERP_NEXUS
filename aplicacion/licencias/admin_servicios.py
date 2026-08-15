from __future__ import annotations

from datetime import datetime

from aplicacion.licencias.cliente_online import (
    ClienteLicenciaOnline,
    ResultadoValidacionOnline,
)
from aplicacion.licencias.modelos import (
    LicenciaActivacion,
    SerialLicencia,
)
from aplicacion.licencias.servicios import (
    licencias_habilitadas,
    obtener_secreto_validacion,
    preparar_licencia_sistema,
    registrar_serial_catalogo,
)
from aplicacion.licencias.usuarios import (
    resumen_usuarios_licencia,
)
from aplicacion.licencias.validador import (
    generar_serial,
    normalizar_serial,
)
from aplicacion.base_datos.conexion import SessionLocal
from aplicacion.nucleo.licencia import Licencia


def listar_seriales() -> list[SerialLicencia]:

    db = SessionLocal()

    try:

        return (
            db.query(SerialLicencia)
            .order_by(
                SerialLicencia.fecha_creacion.desc(),
            )
            .all()
        )

    finally:

        db.close()


def listar_activaciones() -> list[LicenciaActivacion]:

    db = SessionLocal()

    try:

        return (
            db.query(LicenciaActivacion)
            .order_by(
                LicenciaActivacion.fecha_activacion.desc(),
            )
            .all()
        )

    finally:

        db.close()


def generar_seriales(
    *,
    edicion: str,
    titular: str = "",
    dias_validez: int | None = None,
    max_usuarios: int | None = None,
    cantidad: int = 1,
) -> list[str]:

    cantidad = max(
        1,
        int(cantidad or 1),
    )

    generados: list[str] = []

    secreto = obtener_secreto_validacion()

    for _ in range(cantidad):

        serial = generar_serial(
            edicion,
            dias=dias_validez,
            secreto=secreto,
        )

        serial = normalizar_serial(
            serial,
        )

        registrar_serial_catalogo(
            serial,
            edicion=edicion,
            titular=titular,
            dias_validez=dias_validez,
            max_usuarios=max_usuarios,
        )

        generados.append(
            serial,
        )

    return generados


def revocar_serial(
    serial: str,
) -> None:

    normalizado = normalizar_serial(
        serial,
    )

    if not normalizado:

        raise ValueError(
            "Serial inválido.",
        )

    db = SessionLocal()

    try:

        registro = (
            db.query(SerialLicencia)
            .filter(
                SerialLicencia.serial
                == normalizado,
            )
            .first()
        )

        if registro is None:

            raise ValueError(
                "Serial no encontrado en el catálogo.",
            )

        registro.estado = "revocado"

        activaciones = (
            db.query(LicenciaActivacion)
            .filter(
                LicenciaActivacion.serial
                == normalizado,
                LicenciaActivacion.activa
                == True,  # noqa: E712
            )
            .all()
        )

        for activacion in activaciones:

            activacion.activa = False
            activacion.estado = "revocada"

        db.commit()

    except Exception:

        db.rollback()

        raise

    finally:

        db.close()

    preparar_licencia_sistema()


def revocar_activacion(
    activacion_id: int,
) -> None:

    db = SessionLocal()

    try:

        activacion = (
            db.query(LicenciaActivacion)
            .filter(
                LicenciaActivacion.id
                == activacion_id,
            )
            .first()
        )

        if activacion is None:

            raise ValueError(
                "Activación no encontrada.",
            )

        activacion.activa = False
        activacion.estado = "revocada"

        serial = (
            db.query(SerialLicencia)
            .filter(
                SerialLicencia.serial
                == activacion.serial,
            )
            .first()
        )

        if serial is not None:

            serial.estado = "revocado"

        db.commit()

    except Exception:

        db.rollback()

        raise

    finally:

        db.close()

    preparar_licencia_sistema()


def marcar_serial_disponible(
    serial: str,
) -> None:

    normalizado = normalizar_serial(
        serial,
    )

    db = SessionLocal()

    try:

        registro = (
            db.query(SerialLicencia)
            .filter(
                SerialLicencia.serial
                == normalizado,
            )
            .first()
        )

        if registro is None:

            raise ValueError(
                "Serial no encontrado.",
            )

        if registro.estado == "activado":

            raise ValueError(
                "No se puede reactivar un serial ya utilizado.",
            )

        registro.estado = "disponible"

        db.commit()

    except Exception:

        db.rollback()

        raise

    finally:

        db.close()


def obtener_resumen_sistema() -> dict:

    estado = preparar_licencia_sistema()

    return {

        "licencias_habilitadas": licencias_habilitadas(),

        "licencia_valida": estado.valida,

        "edicion": estado.edicion_nombre
        or Licencia.edicion_nombre(),

        "serial": estado.serial
        or Licencia.serial(),

        "titular": estado.titular
        or Licencia.titular(),

        "fecha_vencimiento": (
            estado.fecha_vencimiento.isoformat()
            if estado.fecha_vencimiento
            else ""
        ),

        "mensaje": estado.mensaje,

        "usuarios": resumen_usuarios_licencia(),

    }


def probar_servidor_online() -> ResultadoValidacionOnline:

    return ClienteLicenciaOnline.probar_conexion()
