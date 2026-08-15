from aplicacion.autenticacion.servicios import crear_usuario_admin
from aplicacion.base_datos.inicializar import crear_tablas

crear_tablas()
crear_usuario_admin()

print("Base de datos inicializada correctamente.")
