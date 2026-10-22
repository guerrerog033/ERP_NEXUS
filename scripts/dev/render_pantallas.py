"""
Genera capturas PNG de pantallas clave del ERP en modo offscreen
(QT_QPA_PLATFORM=offscreen). Uso de desarrollo para revisar el
diseño sin abrir la aplicación:

    python scripts/dev/render_pantallas.py renders/
"""

from __future__ import annotations

import sys
import traceback
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

SALIDA = Path(sys.argv[1] if len(sys.argv) > 1 else "renders")
SALIDA.mkdir(parents=True, exist_ok=True)
LOG = open(SALIDA / "log.txt", "w", encoding="utf-8")


def log(*partes):
    texto = " ".join(str(p) for p in partes)
    print(texto)
    LOG.write(texto + "\n")
    LOG.flush()


def main():
    from PySide6.QtWidgets import QApplication, QWidget

    from aplicacion.base_datos.registro_modelos import importar_modelos

    importar_modelos()

    app = QApplication(sys.argv)

    from aplicacion.recursos.estilos.tema import aplicar_tema

    aplicar_tema(app)

    from aplicacion.base_datos.startup import (
        aplicar_migraciones,
        inicializar_sistema,
    )

    inicializar_sistema()
    aplicar_migraciones()

    from aplicacion.autenticacion.servicios import (
        autenticar,
        crear_usuario_admin,
        inicializar_roles,
    )

    inicializar_roles()
    crear_usuario_admin()
    usuario = autenticar("admin", "Admin123")
    log("usuario", usuario)

    from aplicacion.interfaz.dashboard import Dashboard

    dashboard = Dashboard(usuario, embebido=True)
    dashboard.resize(1440, 860)
    dashboard.show()

    def esperar(ms=400):
        from PySide6.QtCore import QEventLoop, QTimer

        bucle = QEventLoop()
        QTimer.singleShot(ms, bucle.quit)
        bucle.exec()

    def capturar(nombre):
        esperar()
        ruta = SALIDA / f"{nombre}.png"
        dashboard.grab().save(str(ruta))
        log("captura", ruta)

    def paso(nombre, funcion):
        try:
            funcion()
            capturar(nombre)
        except Exception:
            log("ERROR en", nombre)
            log(traceback.format_exc())

    area = dashboard.area_trabajo

    def maestro_actual():
        actual = area.currentWidget()
        candidatos = [actual] + actual.findChildren(QWidget)
        for widget in candidatos:
            if callable(getattr(widget, "nuevo", None)) and hasattr(
                widget,
                "crear_formulario",
            ):
                return widget
        return None

    def abrir_nuevo(modulo):
        dashboard.modulo_seleccionado(modulo)
        esperar()
        maestro = maestro_actual()
        if maestro is None:
            raise RuntimeError(f"Sin maestro para {modulo}")
        maestro.nuevo()

    paso("01_inicio", lambda: None)

    def expandir_ventas():
        barra = dashboard.barra_lateral
        for boton in barra._botones:
            if boton._titulo_base == "Ventas":
                boton.clicked.emit()
                break

    paso("02_menu_ventas", expandir_ventas)
    paso("03_lista_cotizaciones", lambda: dashboard.modulo_seleccionado("Cotizaciones"))
    paso("04_nueva_cotizacion", lambda: abrir_nuevo("Cotizaciones"))
    paso("05_nueva_factura", lambda: abrir_nuevo("FacturasVenta"))
    paso("06_nuevo_cliente", lambda: abrir_nuevo("Clientes"))
    paso("07_nuevo_producto", lambda: abrir_nuevo("Productos"))
    paso("08_lista_facturas", lambda: dashboard.modulo_seleccionado("FacturasVenta"))

    LOG.close()


if __name__ == "__main__":
    try:
        main()
    except Exception:
        log(traceback.format_exc())
        sys.exit(1)
