class ServicioBase:

    repositorio = None

    entidad_auditoria = ""

    modulo_auditoria = ""

    auditoria_campos_habilitada = True

    auditoria_campos_linea: list[str] | None = None

    auditoria_campos_cabecera: list[str] | None = None

    auditoria_campos_cabecera_excluir: list[str] | None = None

    # ==================================================
    # Repositorio
    # ==================================================

    @classmethod
    def obtener_repositorio(cls):

        if cls.repositorio is None:

            raise RuntimeError(
                f"{cls.__name__} debe definir 'repositorio'."
            )

        return cls.repositorio

    # ==================================================
    # Consultas
    # ==================================================

    @classmethod
    def obtener_todos(
        cls,
        **kwargs,
    ):

        pagina = kwargs.get(
            "pagina",
        )

        por_pagina = kwargs.get(
            "por_pagina",
            0,
        )

        filtros = kwargs.get(
            "filtros",
        )

        ordenar_por = kwargs.get(
            "ordenar_por",
        )

        if (
            pagina
            and por_pagina
        ):

            return cls.obtener_repositorio().consultar(
                pagina=pagina,
                por_pagina=por_pagina,
                ordenar_por=ordenar_por,
                filtros=filtros,
            )

        return cls.obtener_repositorio().obtener_todos(
            ordenar_por=ordenar_por,
        )

    @classmethod
    def obtener_por_id(
        cls,
        id_registro,
    ):

        return cls.obtener_repositorio().obtener_por_id(
            id_registro
        )

    @classmethod
    def obtener_primero(cls):

        return cls.obtener_repositorio().obtener_primero()

    @classmethod
    def contar(cls):

        return cls.obtener_repositorio().contar()

    @classmethod
    def existe(
        cls,
        id_registro,
    ):

        return cls.obtener_repositorio().existe(
            id_registro
        )

    # ==================================================
    # Persistencia
    # ==================================================

    @classmethod
    def guardar(
        cls,
        datos,
    ):

        cls.validar(datos)

        return cls.obtener_repositorio().guardar(
            datos
        )

    @classmethod
    def actualizar(
        cls,
        id_registro,
        datos,
    ):

        cls.validar(
            datos,
            id_registro,
        )

        registro = cls.obtener_por_id(
            id_registro,
        )

        cambios = {}

        if (
            cls.auditoria_campos_habilitada
            and registro is not None
            and cls.entidad_auditoria
        ):

            from aplicacion.nucleo.auditoria_campos import (
                AuditoriaCampos,
            )

            cambios = AuditoriaCampos.detectar_cambios(
                registro,
                datos,
            )

        resultado = cls.obtener_repositorio().actualizar(
            id_registro,
            datos,
        )

        if cambios:

            from aplicacion.nucleo.auditoria_campos import (
                AuditoriaCampos,
            )

            from aplicacion.nucleo.sesion import (
                Sesion,
            )

            AuditoriaCampos.registrar_cambios(
                usuario=Sesion.usuario(),
                entidad=cls.entidad_auditoria,
                entidad_id=id_registro,
                cambios=cambios,
                modulo=cls.modulo_auditoria,
            )

        return resultado

    @classmethod
    def eliminar(
        cls,
        id_registro,
    ):

        return cls.obtener_repositorio().eliminar(
            id_registro
        )

    # ==================================================
    # Reglas de negocio
    # ==================================================

    @classmethod
    def validar(
        cls,
        datos,
        id_registro=None,
    ):
        """
        Sobrescribir en los servicios
        que requieran reglas de negocio.
        """
        pass

    @classmethod
    def auditar_cabecera(
        cls,
        id_registro,
        cabecera,
    ) -> dict:

        from aplicacion.comunes.auditoria_documento import (
            auditar_cabecera_antes,
        )

        return auditar_cabecera_antes(
            cls,
            id_registro,
            cabecera,
        )

    @classmethod
    def confirmar_auditoria_cabecera(
        cls,
        id_registro,
        cambios,
    ) -> None:

        from aplicacion.comunes.auditoria_documento import (
            registrar_auditoria_cabecera,
        )

        registrar_auditoria_cabecera(
            cls,
            id_registro,
            cambios,
        )

    @classmethod
    def auditar_documento(
        cls,
        id_registro,
        cabecera,
        lineas=None,
    ) -> dict:

        from aplicacion.comunes.auditoria_documento import (
            auditar_documento_antes,
        )

        return auditar_documento_antes(
            cls,
            id_registro,
            cabecera,
            lineas,
        )