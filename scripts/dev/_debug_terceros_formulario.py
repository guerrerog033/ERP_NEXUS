import sys

from PySide6.QtWidgets import QApplication

from aplicacion.maestros.terceros.formulario import TercerosFormulario


app = QApplication(sys.argv)

ventana = TercerosFormulario()
ventana.show()

sys.exit(app.exec())