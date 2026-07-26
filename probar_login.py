from aplicacion.autenticacion.servicios import autenticar

usuario = autenticar(
    "admin",
    "Admin123"
)

if usuario:
    print("LOGIN CORRECTO")
    print(usuario.nombre)
else:
    print("LOGIN INCORRECTO")