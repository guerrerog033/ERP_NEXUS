"""Diagnóstico: qué ventanas aparecen y qué pestañas se abren al abrir módulos."""
from __future__ import annotations
import sys, time, traceback
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
SALIDA = Path(sys.argv[1] if len(sys.argv) > 1 else "renders")
SALIDA.mkdir(parents=True, exist_ok=True)
LOG = open(SALIDA / "diag.txt", "w", encoding="utf-8")
def log(*p):
    t = " ".join(str(x) for x in p); print(t); LOG.write(t + "\n"); LOG.flush()

from PySide6.QtCore import QEvent, QObject, QEventLoop, QTimer
from PySide6.QtWidgets import QApplication

class Espia(QObject):
    def eventFilter(self, obj, ev):
        if ev.type() == QEvent.Type.Show and getattr(obj, "isWindow", None) and obj.isWindow():
            log("SHOW ventana:", type(obj).__name__, obj.objectName(), obj.windowTitle()[:40])
            log("".join(traceback.format_stack(limit=14)[:-1]))
        return False

def esperar(ms=600):
    b = QEventLoop(); QTimer.singleShot(ms, b.quit); b.exec()

def main():
    from aplicacion.base_datos.registro_modelos import importar_modelos
    importar_modelos()
    app = QApplication(sys.argv)
    from aplicacion.recursos.estilos.tema import aplicar_tema
    aplicar_tema(app)
    from aplicacion.base_datos.startup import aplicar_migraciones, inicializar_sistema
    inicializar_sistema(); aplicar_migraciones()
    from aplicacion.autenticacion.servicios import autenticar, crear_usuario_admin, inicializar_roles
    inicializar_roles(); crear_usuario_admin()
    usuario = autenticar("admin", "Admin123")
    from aplicacion.interfaz.dashboard import Dashboard
    d = Dashboard(usuario, embebido=True); d.resize(1440, 860); d.show(); esperar()
    espia = Espia(); app.installEventFilter(espia)
    from aplicacion.framework.menu_manifest import MODULOS
    fallos = []
    for modulo in MODULOS:
        t0 = time.perf_counter()
        try:
            d.modulos.abrir(modulo)
            esperar(300)
            log(f"OK {modulo} {time.perf_counter()-t0:.2f}s")
        except Exception as exc:
            fallos.append(modulo)
            log(f"FALLA {modulo}: {type(exc).__name__}: {exc}")
            log(traceback.format_exc(limit=6))
        while d.area_trabajo.count() > 1:
            d.area_trabajo.cerrar_pestana(d.area_trabajo.count() - 1)
    log("RESUMEN FALLOS:", fallos)
    LOG.close()

if __name__ == "__main__":
    try:
        main()
    except Exception:
        log(traceback.format_exc())
