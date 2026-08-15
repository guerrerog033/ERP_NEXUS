class CrudController:

    def __init__(self, servicio):

        self.servicio = servicio

    # =============================

    def listar(self):

        return self.servicio.listar()

    # =============================

    def buscar(self, texto):

        return self.servicio.buscar(texto)

    # =============================

    def obtener(self, id_registro):

        return self.servicio.obtener_por_id(
            id_registro
        )

    # =============================

    def guardar(self, datos, id_registro=None):

        return self.servicio.guardar(
            datos,
            id_registro
        )

    # =============================

    def eliminar(self, id_registro):

        return self.servicio.eliminar(
            id_registro
        )