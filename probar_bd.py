from aplicacion.base_datos.conexion import ConexionBD

try:
    conexion = ConexionBD.conectar()

    print("===================================")
    print(" CONEXIÓN EXITOSA A POSTGRESQL ")
    print("===================================")

    conexion.close()

except Exception as e:
    print("ERROR")
    print(e)