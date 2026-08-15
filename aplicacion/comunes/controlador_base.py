class ControladorBase:

    servicio = None

    # ==================================================
    # Servicio
    # ==================================================

    @classmethod
    def obtener_servicio(cls):

        if cls.servicio is None:

            raise RuntimeError(
                f"{cls.__name__} debe definir 'servicio'."
            )

        return cls.servicio

    # ==================================================
    # Listar
    # ==================================================

    @classmethod
    def listar(
        cls,
        **kwargs,
    ):

        return cls.obtener_servicio().obtener_todos(
            **kwargs
        )

    # ==================================================
    # Buscar
    # ==================================================

    @classmethod
    def buscar(
        cls,
        texto,
        **kwargs,
    ):

        servicio = cls.obtener_servicio()

        if hasattr(
            servicio,
            "buscar",
        ):

            return servicio.buscar(
                texto,
                **kwargs,
            )

        return servicio.obtener_todos(
            **kwargs,
        )

    # ==================================================
    # Obtener
    # ==================================================

    @classmethod
    def obtener(
        cls,
        id_registro,
    ):

        return cls.obtener_servicio().obtener_por_id(
            id_registro
        )

    # Alias

    obtener_por_id = obtener

    # ==================================================
    # Guardar
    # ==================================================

    @classmethod
    def guardar(
        cls,
        datos,
        id_registro=None,
    ):

        servicio = cls.obtener_servicio()

        if id_registro is None:

            resultado = servicio.guardar(
                datos,
            )

            accion = "crear"

        else:

            resultado = servicio.actualizar(
                id_registro,
                datos,
            )

            accion = "actualizar"

        cls._auditar_persistencia(
            accion,
            servicio,
            resultado,
            id_registro,
        )

        return resultado

    # ==================================================
    # Eliminar
    # ==================================================

    @classmethod
    def eliminar(
        cls,
        id_registro,
    ):

        servicio = cls.obtener_servicio()

        cls._auditar_persistencia(
            "eliminar",
            servicio,
            None,
            id_registro,
        )

        return servicio.eliminar(
            id_registro,
        )

    @classmethod
    def _auditar_persistencia(
        cls,
        accion,
        servicio,
        resultado,
        id_registro,
    ):

        try:

            from aplicacion.nucleo.auditoria import (
                Auditoria,
            )

            entidad = servicio.__name__

            if entidad.startswith(
                "Servicio",
            ):

                entidad = entidad[
                    len(
                        "Servicio",
                    ):
                ]

            registro_id = id_registro

            if (
                resultado is not None
                and getattr(
                    resultado,
                    "id",
                    None,
                )
                is not None
            ):

                registro_id = resultado.id

            Auditoria.registrar_sesion(
                accion,
                entidad=entidad,
                entidad_id=registro_id,
            )

        except Exception:

            pass