from aplicacion.autenticacion.seguridad import (
    cifrar_password,
    verificar_password,
)

clave = "Admin123"

hash_clave = cifrar_password(clave)

print("Hash:")
print(hash_clave)

print()

print(
    verificar_password(
        "Admin123",
        hash_clave
    )
)

print(
    verificar_password(
        "123456",
        hash_clave
    )
)