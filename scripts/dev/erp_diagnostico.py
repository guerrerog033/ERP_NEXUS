"""
Abre el ERP normal, pero anota en logs/diagnostico.txt:
- cada ventana que se muestra (con quién la abrió),
- cada módulo y cada formulario "Nuevo/Editar" que se abre (con quién lo pidió),
- cuánto tarda cada apertura.

Uso (desde la carpeta del proyecto):
    python scripts/dev/erp_diagnostico.py
Reproduzca el problema, cierre el ERP y revise logs/diagnostico.txt.
"""

from __future__ import annotations

import sys
import time
import traceback
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

RUTA_LOG = ROOT / "logs" / "diagnostico.txt"
RUTA_LOG.parent.mkdir(exist_ok=True)
LOG = open(RUTA_LOG, "w", encoding="utf-8")


def log(*partes):
    texto = time.strftime("%H:%M:%S ") + " ".join(str(p) for p in partes)
    LOG.write(texto + "\n")
    LOG.flush()


def pila():
    lineas = traceback.format_stack(limit=18)[:-2]
    return "".join(
        l for l in lineas if "aplicacion" in l or "main.py" in l
    )


def envolver(clase, nombre_metodo, etiqueta):
    original = getattr(clase, nombre_metodo)

    def envoltura(self, *args, **kwargs):
        t0 = time.perf_counter()
        log(f">> {etiqueta} {type(self).__name__}.{nombre_metodo} args={args!r}")
        log(pila())
        try:
            return original(self, *args, **kwargs)
        finally:
            log(f"<< {etiqueta} {nombre_metodo} {time.perf_counter() - t0:.2f}s")

    setattr(clase, nombre_metodo, envoltura)


def main():
    from PySide6.QtCore import QEvent, QObject

    import main as erp_main

    from aplicacion.interfaz.dashboard import Dashboard
    from aplicacion.framework.crud.crud_formulario_dialog import CrudFormularioDialog
    from aplicacion.framework.crud.crud_navegacion import CrudNavegacion
    from aplicacion.framework.modulo_manager import ModuloManager

    envolver(Dashboard, "modulo_seleccionado", "MODULO")
    envolver(ModuloManager, "abrir", "ABRIR")
    envolver(CrudFormularioDialog, "_mostrar_dialogo_formulario", "FORMULARIO")
    envolver(CrudNavegacion, "nuevo", "NUEVO")

    class Espia(QObject):
        def eventFilter(self, obj, ev):
            try:
                if ev.type() == QEvent.Type.Show and obj.isWidgetType() and obj.isWindow():
                    log(
                        "VENTANA visible:",
                        type(obj).__name__,
                        repr(obj.objectName()),
                        repr(obj.windowTitle()[:40]),
                        obj.size().width(),
                        "x",
                        obj.size().height(),
                    )
                    log(pila())
            except Exception:
                pass
            return False

    app = erp_main.crear_aplicacion()
    espia = Espia()
    app.installEventFilter(espia)

    from aplicacion.interfaz.ventana_principal import VentanaPrincipal

    ventana = VentanaPrincipal()
    ventana.show()
    codigo = app.exec()
    LOG.close()
    sys.exit(codigo)


if __name__ == "__main__":
    main()
