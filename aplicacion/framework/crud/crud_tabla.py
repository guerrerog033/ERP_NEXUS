class CrudTabla:
    """
    Adaptador entre el CRUD y el TableEngine.

    Toda la lógica de sincronización de la tabla
    vive en TableBinding.
    """

    # ==================================================
    # Llenar tabla
    # ==================================================

    def llenar_tabla(
        self,
        registros,
    ):

        self.table_engine.cargar(
            registros
        )

        self.actualizar_total()