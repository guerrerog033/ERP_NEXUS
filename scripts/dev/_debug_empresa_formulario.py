import sys

from PySide6.QtWidgets import QApplication

from aplicacion.maestros.empresas.formulario import EmpresaFormulario


app = QApplication(sys.argv)

ventana = EmpresaFormulario()
ventana.show()

sys.exit(app.exec())