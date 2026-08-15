from __future__ import annotations

from aplicacion.autenticacion.modelos import Usuario
from aplicacion.base_datos.conexion import SessionLocal
from aplicacion.licencias.servicios import licencias_habilitadas
from aplicacion.nucleo.licencia import Licencia


def contar_usuarios_activos() -> int:

    db = SessionLocal()

    try:

        return (
            db.query(Usuario)
            .filter(
                Usuario.activo
                == True,  # noqa: E712
            )
            .count()
        )

    finally:

        db.close()


def limite_usuarios_licencia() -> int | None:

    if not licencias_habilitadas():

        return None

    maximo = int(
        Licencia.max_usuarios() or 0,
    )

    if maximo <= 0:

        return None

    return maximo


def validar_limite_para_login(
    usuario,
) -> str | None:

    maximo = limite_usuarios_licencia()

    if maximo is None:

        return None

    activos = contar_usuarios_activos()

    if activos <= maximo:

        return None

    rol = getattr(
        usuario,
        "rol",
        None,
    )

    if (
        rol is not None
        and str(
            rol.codigo or "",
        )
        == "admin"
    ):

        return None

    return (
        f"La licencia permite hasta {maximo} "
        f"usuario(s) activo(s). Actualmente hay "
        f"{activos}. Desactive usuarios o renueve "
        f"la licencia."
    )


def validar_puede_activar_usuario(
    *,
    excluir_id: int | None = None,
) -> str | None:

    maximo = limite_usuarios_licencia()

    if maximo is None:

        return None

    db = SessionLocal()

    try:

        consulta = db.query(Usuario).filter(
            Usuario.activo == True,  # noqa: E712
        )

        if excluir_id is not None:

            consulta = consulta.filter(
                Usuario.id != excluir_id,
            )

        activos = consulta.count()

    finally:

        db.close()

    if activos >= maximo:

        return (
            f"No puede activar más usuarios. "
            f"Límite de licencia: {maximo}."
        )

    return None


def resumen_usuarios_licencia() -> dict:

    maximo = limite_usuarios_licencia()

    activos = contar_usuarios_activos()

    return {
        "activos": activos,
        "maximo": maximo,
        "disponibles": (
            None
            if maximo is None
            else max(
                maximo - activos,
                0,
            )
        ),
    }
