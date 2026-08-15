from __future__ import annotations

from PySide6.QtWidgets import (
    QMessageBox,
    QVBoxLayout,
    QWidget,
)


def _nombre_tercero(
    nombre_cliente: str,
) -> str:

    return (
        nombre_cliente.strip()
        or "Cliente"
    )


def mostrar_cartera_cliente(
    parent,
    cliente_id: int | None,
    *,
    nombre_cliente: str = "",
) -> None:

    if not cliente_id:

        QMessageBox.warning(
            parent,
            "Cartera cliente",
            "No hay cliente asociado al documento.",
        )

        return

    from aplicacion.modulos.cartera.servicios import (
        ServicioCartera,
    )

    try:

        resumen = ServicioCartera.resumen_cliente_cxc(
            int(
                cliente_id,
            ),
        )

    except ValueError as error:

        QMessageBox.warning(
            parent,
            "Cartera cliente",
            str(
                error,
            ),
        )

        return

    titulo = _nombre_tercero(
        nombre_cliente,
    )

    if resumen["facturas_pendientes"] == 0:

        mensaje = (
            f"{titulo}\n\n"
            "Sin saldo pendiente en cuentas por cobrar."
        )

    else:

        mensaje = (
            f"{titulo}\n\n"
            f"Facturas pendientes: "
            f"{resumen['facturas_pendientes']}\n"
            f"Saldo total: "
            f"${resumen['saldo_total']:,.2f}\n"
            f"Saldo vencido: "
            f"${resumen['saldo_vencido']:,.2f}"
        )

    QMessageBox.information(
        parent,
        "Cartera cliente",
        mensaje,
    )

    if resumen["facturas_pendientes"] > 0:

        detalle = QMessageBox.question(
            parent,
            "Cartera cliente",
            "¿Desea abrir el estado de cuenta detallado?",
            QMessageBox.StandardButton.Yes
            | QMessageBox.StandardButton.No,
        )

        if detalle == QMessageBox.StandardButton.Yes:

            mostrar_estado_cuenta_cliente(
                parent,
                int(
                    cliente_id,
                ),
                nombre_cliente=nombre_cliente,
            )


def mostrar_estado_cuenta_cliente(
    parent,
    cliente_id: int | None,
    *,
    nombre_cliente: str = "",
) -> None:

    if not cliente_id:

        QMessageBox.warning(
            parent,
            "Estado de cuenta",
            "No hay cliente asociado al documento.",
        )

        return

    from PySide6.QtWidgets import (
        QDialog,
    )

    from aplicacion.modulos.cartera.estado_cuenta.vista import (
        CarteraEstadoCuentaPage,
    )

    titulo = _nombre_tercero(
        nombre_cliente,
    )

    dialogo = QDialog(
        parent,
    )
    dialogo.setWindowTitle(
        f"Estado de cuenta — {titulo}",
    )
    dialogo.setModal(
        True,
    )
    dialogo.resize(
        980,
        640,
    )

    layout = QVBoxLayout(
        dialogo,
    )

    vista = CarteraEstadoCuentaPage(
        parent=dialogo,
        bloquear_tercero=True,
    )
    vista.consultar_cliente_cxc(
        int(
            cliente_id,
        ),
    )

    layout.addWidget(
        vista,
    )

    dialogo.exec()


def cartera_desde_documento(
    vista,
    documento,
    *,
    nombre_cliente: str = "",
) -> None:

    if documento is None:

        return

    mostrar_cartera_cliente(
        vista,
        getattr(
            documento,
            "cliente_id",
            None,
        ),
        nombre_cliente=nombre_cliente,
    )


def estado_cuenta_desde_documento(
    vista,
    documento,
    *,
    nombre_cliente: str = "",
) -> None:

    if documento is None:

        return

    mostrar_estado_cuenta_cliente(
        vista,
        getattr(
            documento,
            "cliente_id",
            None,
        ),
        nombre_cliente=nombre_cliente,
    )


def cartera_desde_tercero(
    formulario,
    tercero_id: int | None,
    *,
    nombre: str = "",
) -> None:

    mostrar_cartera_cliente(
        formulario,
        tercero_id,
        nombre_cliente=nombre,
    )


def estado_cuenta_desde_tercero(
    formulario,
    tercero_id: int | None,
    *,
    nombre: str = "",
) -> None:

    mostrar_estado_cuenta_cliente(
        formulario,
        tercero_id,
        nombre_cliente=nombre,
    )
