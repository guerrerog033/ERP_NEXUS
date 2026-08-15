from __future__ import annotations

from unittest.mock import MagicMock

from sqlalchemy.exc import IntegrityError

from aplicacion.framework.crud.crud_master import CrudMaster


def _instancia_sin_init() -> CrudMaster:
    """
    CrudMaster.__init__ construye toda la UI Qt (tabla, formulario,
    etc.). Para probar eliminar() en aislamiento basta con un
    objeto crudo con los métodos que ese método realmente usa.
    """

    return CrudMaster.__new__(
        CrudMaster,
    )


def test_eliminar_registro_en_uso_muestra_error_amigable():

    instancia = _instancia_sin_init()

    instancia.obtener_id_seleccionado = MagicMock(
        return_value=1,
    )
    instancia.confirmar = MagicMock(
        return_value=True,
    )
    instancia.mostrar_error = MagicMock()
    instancia.cargar_datos = MagicMock()

    backend = MagicMock()
    backend.eliminar.side_effect = IntegrityError(
        "DELETE FROM productos",
        {},
        Exception("fk violation"),
    )

    instancia.backend = MagicMock(
        return_value=backend,
    )

    instancia.eliminar()

    instancia.mostrar_error.assert_called_once()

    mensaje = instancia.mostrar_error.call_args[0][0]

    assert "usado en otros" in mensaje

    instancia.cargar_datos.assert_not_called()


def test_eliminar_con_error_generico_muestra_mensaje():

    instancia = _instancia_sin_init()

    instancia.obtener_id_seleccionado = MagicMock(
        return_value=1,
    )
    instancia.confirmar = MagicMock(
        return_value=True,
    )
    instancia.mostrar_error = MagicMock()
    instancia.cargar_datos = MagicMock()

    backend = MagicMock()
    backend.eliminar.side_effect = RuntimeError(
        "algo salió mal",
    )

    instancia.backend = MagicMock(
        return_value=backend,
    )

    instancia.eliminar()

    instancia.mostrar_error.assert_called_once()

    mensaje = instancia.mostrar_error.call_args[0][0]

    assert "algo salió mal" in mensaje

    instancia.cargar_datos.assert_not_called()


def test_eliminar_exitoso_recarga_datos():

    instancia = _instancia_sin_init()

    instancia.obtener_id_seleccionado = MagicMock(
        return_value=1,
    )
    instancia.confirmar = MagicMock(
        return_value=True,
    )
    instancia.mostrar_error = MagicMock()
    instancia.cargar_datos = MagicMock()

    backend = MagicMock()

    instancia.backend = MagicMock(
        return_value=backend,
    )

    instancia.eliminar()

    backend.eliminar.assert_called_once_with(
        1,
    )
    instancia.mostrar_error.assert_not_called()
    instancia.cargar_datos.assert_called_once()


def test_eliminar_sin_confirmar_no_llama_backend():

    instancia = _instancia_sin_init()

    instancia.obtener_id_seleccionado = MagicMock(
        return_value=1,
    )
    instancia.confirmar = MagicMock(
        return_value=False,
    )
    instancia.backend = MagicMock()
    instancia.cargar_datos = MagicMock()

    instancia.eliminar()

    instancia.backend.assert_not_called()
    instancia.cargar_datos.assert_not_called()
