from PySide6.QtCore import QObject, QThread, Signal


class TrabajoInicioSesion(QObject):

    terminado = Signal(
        object,
        str,
    )

    def __init__(
        self,
        usuario: str,
        password: str,
    ):

        super().__init__()

        self.usuario = usuario

        self.password = password

    def ejecutar(
        self,
    ):

        try:

            from aplicacion.base_datos.conexion import (
                probar_conexion,
            )

            from aplicacion.base_datos.startup import (
                inicializar_sistema,
            )

            from aplicacion.autenticacion.servicios import (
                autenticar,
                inicializar_roles,
            )

            from aplicacion.licencias.servicios import (
                preparar_licencia_sistema,
            )

            probar_conexion()

            inicializar_sistema()

            from aplicacion.base_datos.startup import (
                aplicar_migraciones,
            )

            aplicar_migraciones()

            inicializar_roles()

            estado_licencia = preparar_licencia_sistema()

            if estado_licencia.requiere_activacion:

                self.terminado.emit(
                    {
                        "licencia": estado_licencia,
                    },
                    "",
                )

                return

            resultado = autenticar(
                self.usuario,
                self.password,
            )

            if resultado is not None:

                from aplicacion.licencias.usuarios import (
                    validar_limite_para_login,
                )

                error_limite = (
                    validar_limite_para_login(
                        resultado,
                    )
                )

                if error_limite:

                    self.terminado.emit(
                        {
                            "error_login": error_limite,
                        },
                        "",
                    )

                    return

            self.terminado.emit(
                resultado,
                "",
            )

        except Exception as error:

            self.terminado.emit(
                None,
                str(
                    error,
                ),
            )
