from PySide6.QtCore import QObject


class ControladorMaestro(QObject):

    def __init__(self, formulario, servicio):
        super().__init__()

        self.formulario = formulario
        self.servicio = servicio

        self.conectar_eventos()

    def conectar_eventos(self):

        if hasattr(self.formulario, "btn_nuevo"):
            self.formulario.btn_nuevo.clicked.connect(
                self.nuevo
            )

        if hasattr(self.formulario, "btn_guardar"):
            self.formulario.btn_guardar.clicked.connect(
                self.guardar
            )

        if hasattr(self.formulario, "txt_busqueda"):
            self.formulario.txt_busqueda.textChanged.connect(
                self.buscar
            )

    # ---------------------------------

    def nuevo(self):
        pass

    def guardar(self):
        pass

    def buscar(self):
        pass

    def cargar_tabla(self):
        pass