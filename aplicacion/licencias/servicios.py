from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta

from aplicacion.licencias.ediciones import EDICIONES
from aplicacion.licencias.huella import obtener_huella_equipo
from aplicacion.licencias.modelos import (
    LicenciaActivacion,
    SerialLicencia,
)
from aplicacion.licencias.validador import (
    decodificar_serial,
    normalizar_serial,
)
from aplicacion.base_datos.conexion import SessionLocal
from aplicacion.nucleo.configuracion import Configuracion
from aplicacion.nucleo.licencia import Licencia


def obtener_secreto_validacion() -> str:

    return _secreto_validacion()


def _validar_online_al_inicio() -> bool:

    config = (
        _config_licencias().get(
            "servidor_online",
        )
        or {}
    )

    if not config.get(
        "habilitado",
        False,
    ):

        return False

    return bool(
        config.get(
            "validar_al_inicio",
            True,
        ),
    )


def _validar_online_al_activar() -> bool:

    config = (
        _config_licencias().get(
            "servidor_online",
        )
        or {}
    )

    if not config.get(
        "habilitado",
        False,
    ):

        return False

    return bool(
        config.get(
            "validar_al_activar",
            True,
        ),
    )


def _aplicar_revocacion_online(
    registro: LicenciaActivacion,
    db,
    mensaje: str,
) -> EstadoLicencia:

    registro.activa = False
    registro.estado = "revocada"

    serial = (
        db.query(SerialLicencia)
        .filter(
            SerialLicencia.serial
            == registro.serial,
        )
        .first()
    )

    if serial is not None:

        serial.estado = "revocado"

    db.commit()

    _cargar_licencia_contexto(
        None,
    )

    return EstadoLicencia(

        valida=False,

        requiere_activacion=True,

        mensaje=mensaje
        or "La licencia fue revocada.",

    )


@dataclass(slots=True)
class EstadoLicencia:

    valida: bool = False

    requiere_activacion: bool = False

    mensaje: str = ""

    edicion: str = ""

    edicion_nombre: str = ""

    titular: str = ""

    serial: str = ""

    fecha_vencimiento: datetime | None = None

    dias_restantes: int | None = None

    max_usuarios: int = 0

    proxima_expiracion: bool = False


def _config_licencias() -> dict:

    return (
        Configuracion.obtener(
            "licencias",
        )
        or {}
    )


def licencias_habilitadas() -> bool:

    config = _config_licencias()

    if not config.get(
        "habilitado",
        True,
    ):

        return False

    if config.get(
        "modo_desarrollo",
        False,
    ):

        return False

    return True


def _secreto_validacion() -> str:

    config = _config_licencias()

    return str(
        config.get(
            "secreto_validacion",
            "erp-nexus-dev-secret",
        ),
    )


def _dias_alerta() -> int:

    config = _config_licencias()

    return int(
        config.get(
            "dias_alerta_vencimiento",
            15,
        )
        or 15,
    )


def _calcular_vencimiento(
    *,
    dias_validez: int | None,
    base: datetime | None = None,
) -> datetime | None:

    if not dias_validez:

        return None

    inicio = base or datetime.utcnow()

    return inicio + timedelta(
        days=dias_validez,
    )


def _licencia_vigente(
    registro: LicenciaActivacion,
) -> bool:

    if not registro.activa:

        return False

    if registro.estado != "activa":

        return False

    if (
        registro.fecha_vencimiento
        and registro.fecha_vencimiento
        < datetime.utcnow()
    ):

        return False

    return True


def _estado_desde_registro(
    registro: LicenciaActivacion,
) -> EstadoLicencia:

    edicion = str(
        registro.edicion or "",
    )

    edicion_nombre = EDICIONES.get(
        edicion,
        {},
    ).get(
        "nombre",
        edicion,
    )

    dias_restantes = None

    proxima = False

    if registro.fecha_vencimiento:

        delta = (
            registro.fecha_vencimiento
            - datetime.utcnow()
        )

        dias_restantes = max(
            0,
            delta.days,
        )

        proxima = (
            dias_restantes
            <= _dias_alerta()
        )

    vigente = _licencia_vigente(
        registro,
    )

    mensaje = ""

    if not vigente:

        if (
            registro.fecha_vencimiento
            and registro.fecha_vencimiento
            < datetime.utcnow()
        ):

            mensaje = (
                "La licencia ha expirado. "
                "Contacte a su proveedor para renovar."
            )

        elif registro.estado == "revocada":

            mensaje = (
                "La licencia fue revocada."
            )

        else:

            mensaje = (
                "La licencia no está activa."
            )

    elif proxima:

        mensaje = (
            f"La licencia vence en "
            f"{dias_restantes} día(s)."
        )

    return EstadoLicencia(

        valida=vigente,

        requiere_activacion=not vigente,

        mensaje=mensaje,

        edicion=edicion,

        edicion_nombre=str(
            edicion_nombre,
        ),

        titular=str(
            registro.titular or "",
        ),

        serial=str(
            registro.serial or "",
        ),

        fecha_vencimiento=(
            registro.fecha_vencimiento
        ),

        dias_restantes=dias_restantes,

        max_usuarios=int(
            registro.max_usuarios or 0,
        ),

        proxima_expiracion=proxima,

    )


def _cargar_licencia_contexto(
    registro: LicenciaActivacion | None,
) -> None:

    if registro is None:

        Licencia.limpiar()

        return

    Licencia.cargar(
        modulos=list(
            registro.modulos or [],
        ),
        edicion=str(
            registro.edicion or "",
        ),
        edicion_nombre=EDICIONES.get(
            str(
                registro.edicion or "",
            ),
            {},
        ).get(
            "nombre",
            registro.edicion,
        ),
        serial=str(
            registro.serial or "",
        ),
        titular=str(
            registro.titular or "",
        ),
        max_usuarios=int(
            registro.max_usuarios or 0,
        ),
        fecha_vencimiento=(
            registro.fecha_vencimiento
        ),
        habilitada=licencias_habilitadas(),
    )


def preparar_licencia_sistema() -> EstadoLicencia:

    if not licencias_habilitadas():

        Licencia.cargar_desarrollo()

        return EstadoLicencia(

            valida=True,

            requiere_activacion=False,

            mensaje="Modo desarrollo",

            edicion="desarrollo",

            edicion_nombre="Desarrollo",

        )

    db = SessionLocal()

    try:

        registro = (
            db.query(
                LicenciaActivacion,
            )
            .filter(
                LicenciaActivacion.activa
                == True,  # noqa: E712
            )
            .order_by(
                LicenciaActivacion.id.desc(),
            )
            .first()
        )

        if registro is None:

            _cargar_licencia_contexto(
                None,
            )

            return EstadoLicencia(

                valida=False,

                requiere_activacion=True,

                mensaje=(
                    "Debe activar una licencia "
                    "para usar ERP NEXUS."
                ),

            )

        if not _licencia_vigente(
            registro,
        ):

            registro.estado = (
                "expirada"
                if (
                    registro.fecha_vencimiento
                    and registro.fecha_vencimiento
                    < datetime.utcnow()
                )
                else registro.estado
            )

            registro.activa = False

            db.commit()

            _cargar_licencia_contexto(
                None,
            )

            return _estado_desde_registro(
                registro,
            )

        huella_actual = obtener_huella_equipo()

        if (
            registro.huella_equipo
            and registro.huella_equipo
            != huella_actual
        ):

            _cargar_licencia_contexto(
                None,
            )

            return EstadoLicencia(

                valida=False,

                requiere_activacion=True,

                mensaje=(
                    "Esta licencia está vinculada "
                    "a otro equipo."
                ),

            )

        if _validar_online_al_inicio():

            from aplicacion.licencias.cliente_online import (
                ClienteLicenciaOnline,
            )

            online = (
                ClienteLicenciaOnline.validar_vigencia(
                    registro.serial,
                )
            )

            if (
                online.revocado
                or not online.valido
            ):

                return _aplicar_revocacion_online(
                    registro,
                    db,
                    online.mensaje
                    or (
                        "La licencia fue revocada "
                        "por el servidor."
                    ),
                )

        _cargar_licencia_contexto(
            registro,
        )

        return _estado_desde_registro(
            registro,
        )

    except Exception:

        db.rollback()

        raise

    finally:

        db.close()


def obtener_estado_licencia() -> EstadoLicencia:

    return preparar_licencia_sistema()


def activar_serial(
    serial: str,
    *,
    titular: str = "",
    nit_cliente: str = "",
) -> EstadoLicencia:

    if not licencias_habilitadas():

        return EstadoLicencia(

            valida=True,

            requiere_activacion=False,

            mensaje="Modo desarrollo",

        )

    normalizado = normalizar_serial(
        serial,
    )

    if not normalizado:

        return EstadoLicencia(

            valida=False,

            requiere_activacion=True,

            mensaje="Ingrese un serial válido.",

        )

    try:

        datos_serial = decodificar_serial(
            normalizado,
            secreto=_secreto_validacion(),
        )

    except ValueError as error:

        return EstadoLicencia(

            valida=False,

            requiere_activacion=True,

            mensaje=str(
                error,
            ),

        )

    if _validar_online_al_activar():

        from aplicacion.licencias.cliente_online import (
            ClienteLicenciaOnline,
        )

        online = ClienteLicenciaOnline.activar(
            normalizado,
            titular=titular,
            nit_cliente=nit_cliente,
        )

        if not online.valido:

            return EstadoLicencia(

                valida=False,

                requiere_activacion=True,

                mensaje=(
                    online.mensaje
                    or "El servidor rechazó la activación."
                ),

            )

    db = SessionLocal()

    try:

        existente = (
            db.query(
                LicenciaActivacion,
            )
            .filter(
                LicenciaActivacion.serial
                == normalizado,
            )
            .first()
        )

        if (
            existente
            and _licencia_vigente(
                existente,
            )
        ):

            huella_actual = obtener_huella_equipo()

            if (
                existente.huella_equipo
                != huella_actual
            ):

                return EstadoLicencia(

                    valida=False,

                    requiere_activacion=True,

                    mensaje=(
                        "Este serial ya está "
                        "activado en otro equipo."
                    ),

                )

            _cargar_licencia_contexto(
                existente,
            )

            return _estado_desde_registro(
                existente,
            )

        registro_serial = (
            db.query(
                SerialLicencia,
            )
            .filter(
                SerialLicencia.serial
                == normalizado,
            )
            .first()
        )

        if (
            registro_serial
            and registro_serial.estado
            == "revocado"
        ):

            return EstadoLicencia(

                valida=False,

                requiere_activacion=True,

                mensaje=(
                    "Este serial fue revocado."
                ),

            )

        if (
            registro_serial
            and registro_serial.estado
            == "activado"
            and (
                existente is None
                or not _licencia_vigente(
                    existente,
                )
            )
        ):

            return EstadoLicencia(

                valida=False,

                requiere_activacion=True,

                mensaje=(
                    "Este serial ya fue utilizado."
                ),

            )

        edicion = str(
            datos_serial["edicion"],
        )

        modulos = list(
            datos_serial["modulos"],
        )

        max_usuarios = int(
            datos_serial["max_usuarios"],
        )

        dias_validez = datos_serial.get(
            "dias_validez",
        )

        if registro_serial is not None:

            if registro_serial.edicion:

                edicion = str(
                    registro_serial.edicion,
                )

            if registro_serial.modulos:

                modulos = list(
                    registro_serial.modulos,
                )

            if registro_serial.max_usuarios:

                max_usuarios = int(
                    registro_serial.max_usuarios,
                )

            if (
                registro_serial.dias_validez
                is not None
            ):

                dias_validez = (
                    registro_serial.dias_validez
                )

        ahora = datetime.utcnow()

        vencimiento = _calcular_vencimiento(
            dias_validez=dias_validez,
            base=ahora,
        )

        huella = obtener_huella_equipo()

        db.query(
            LicenciaActivacion,
        ).filter(
            LicenciaActivacion.activa
            == True,  # noqa: E712
        ).update(
            {
                "activa": False,
                "estado": "reemplazada",
            },
            synchronize_session=False,
        )

        activacion = LicenciaActivacion(

            serial=normalizado,

            edicion=edicion,

            titular=titular.strip(),

            nit_cliente=nit_cliente.strip(),

            modulos=modulos,

            max_usuarios=max_usuarios,

            fecha_activacion=ahora,

            fecha_vencimiento=vencimiento,

            huella_equipo=huella,

            estado="activa",

            activa=True,

        )

        db.add(
            activacion,
        )

        db.flush()

        if registro_serial is None:

            registro_serial = SerialLicencia(

                serial=normalizado,

                edicion=edicion,

                modulos=modulos,

                max_usuarios=max_usuarios,

                dias_validez=dias_validez,

                titular_esperado=titular.strip(),

                estado="activado",

            )

            db.add(
                registro_serial,
            )

        else:

            registro_serial.estado = "activado"

            registro_serial.activacion_id = (
                activacion.id
            )

        db.commit()

        db.refresh(
            activacion,
        )

        _cargar_licencia_contexto(
            activacion,
        )

        return _estado_desde_registro(
            activacion,
        )

    except Exception:

        db.rollback()

        raise

    finally:

        db.close()


def registrar_serial_catalogo(
    serial: str,
    *,
    edicion: str,
    titular: str = "",
    dias_validez: int | None = None,
    max_usuarios: int | None = None,
) -> SerialLicencia:

    if edicion not in EDICIONES:

        raise ValueError(
            f"Edición desconocida: {edicion}",
        )

    normalizado = normalizar_serial(
        serial,
    )

    datos = EDICIONES[edicion]

    db = SessionLocal()

    try:

        existente = (
            db.query(
                SerialLicencia,
            )
            .filter(
                SerialLicencia.serial
                == normalizado,
            )
            .first()
        )

        if existente is not None:

            return existente

        registro = SerialLicencia(

            serial=normalizado,

            edicion=edicion,

            modulos=list(
                datos["modulos"],
            ),

            max_usuarios=(
                max_usuarios
                if max_usuarios
                is not None
                else int(
                    datos["max_usuarios"],
                )
            ),

            dias_validez=(
                dias_validez
                if dias_validez
                is not None
                else datos.get(
                    "dias_predeterminados",
                )
            ),

            titular_esperado=titular.strip(),

            estado="disponible",

        )

        db.add(
            registro,
        )

        db.commit()

        db.refresh(
            registro,
        )

        return registro

    except Exception:

        db.rollback()

        raise

    finally:

        db.close()
