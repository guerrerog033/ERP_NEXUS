import sys

from PySide6.QtWidgets import QApplication

from aplicacion.framework.lookup.lookup_dialog import LookupDialog
from aplicacion.maestros.marcas.marca_lookup import MarcaLookup


app = QApplication(sys.argv)

dlg = LookupDialog(
    datasource=MarcaLookup(),
    titulo="Buscar Marca",
)

dlg.exec()