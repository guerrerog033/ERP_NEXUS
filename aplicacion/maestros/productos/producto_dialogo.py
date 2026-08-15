from __future__ import annotations

from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
)

from aplicacion.framework.lookup.lookup_result import (
    LookupResult,
)
from aplicacion.maestros.productos.formulario import (
    FormularioProducto,
)
from aplicacion.maestros.productos.servicios import (
    ServicioProducto,
)


def abrir_dialogo_nuevo_producto(
    parent=None,
    nombre_inicial: str = "",
):

    from aplicacion.base_datos.migraciones import (
        migrar_atributos_variante_stock,
        migrar_productos,
        migrar_variantes_producto,
    )

    migrar_productos()
    migrar_variantes_producto()
    migrar_atributos_variante_stock()

    ServicioProducto.inicializar_catalogos()

    ventana = QDialog(
        parent,
    )

    ventana.setWindowTitle(
        "Nuevo Producto",
    )

    ventana.setModal(
        True,
    )

    formulario = FormularioProducto(
        parent=ventana,
    )

    ancho = min(
        formulario.ancho,
        920,
    )

    alto = min(
        formulario.alto,
        780,
    )

    ventana.resize(
        ancho,
        alto,
    )

    ventana.setMinimumSize(
        720,
        600,
    )

    if nombre_inicial:

        texto = nombre_inicial.strip()

        widget_nombre = formulario.widget(
            "nombre",
        )

        widget_codigo = formulario.widget(
            "codigo",
        )

        parece_codigo = bool(
            texto
            and " " not in texto
            and len(texto) <= 30
            and all(
                caracter.isalnum()
                or caracter in "-_."
                for caracter in texto
            )
        )

        if (
            parece_codigo
            and widget_codigo is not None
        ):

            widget_codigo.setText(
                texto,
            )

        elif widget_nombre is not None:

            widget_nombre.setText(
                texto,
            )

    producto_guardado = []

    original_exitoso = (
        formulario.guardar_exitoso
    )

    def guardar_exitoso(
        objeto=None,
        mensaje=(
            "Registro guardado "
            "correctamente."
        ),
    ):

        producto_guardado.append(
            objeto,
        )

        original_exitoso(
            objeto,
            mensaje,
        )

    formulario.guardar_exitoso = (
        guardar_exitoso
    )

    layout = QVBoxLayout(
        ventana,
    )

    layout.setContentsMargins(
        6,
        6,
        6,
        6,
    )

    layout.addWidget(
        formulario,
    )

    formulario.cerrar.connect(
        ventana.accept,
    )

    ventana.exec()

    formulario.deleteLater()

    if not producto_guardado:

        return None

    return producto_guardado[0]


def producto_a_lookup_result(
    producto,
) -> LookupResult:

    return LookupResult(

        valor=producto.id,

        codigo=str(
            producto.codigo
            or "",
        ),

        texto=str(
            producto.nombre
            or "",
        ),

        objeto=producto,

    )
