from aplicacion.base_datos.conexion import SessionLocal
from aplicacion.autenticacion.modelos import Usuario
from aplicacion.autenticacion.seguridad import (
    cifrar_password,
    verificar_password,
)


def crear_usuario_admin():
    db = SessionLocal()

    usuario = db.query(Usuario).filter(
        Usuario.usuario == "admin"
    ).first()

    if usuario:
        db.close()
        return

    admin = Usuario(
        usuario="admin",
        nombre="Administrador",
        correo="admin@erpnexus.com",
        password=cifrar_password("Admin123"),
        activo=True
    )

    db.add(admin)
    db.commit()
    db.close()


def autenticar(usuario, password):
    db = SessionLocal()

    registro = (
        db.query(Usuario)
        .filter(Usuario.usuario == usuario)
        .first()
    )

    if registro is None:
        db.close()
        return None

    if not verificar_password(password, registro.password):
        db.close()
        return None

    db.close()

    return registro