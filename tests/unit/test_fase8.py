from datetime import date

from aplicacion.comunes.auditoria_documento import (
    _campos_cabecera_auditoria,
    auditar_cabecera_antes,
)
from aplicacion.comunes.exportacion import (
    _html_listado_registros,
)
from aplicacion.comunes.servicio_base import ServicioBase
from aplicacion.framework.table.status_column import (
    StatusColumn,
)
from aplicacion.framework.table.column_factories.status_factory import (
    StatusColumnFactory,
)
from aplicacion.modulos.ventas.pos.servicios import (
    ServicioPOSVenta,
)


class _ServicioCabecera:

    entidad_auditoria = "DocCab"

    auditoria_campos_cabecera_excluir = [
        "fecha_creacion",
    ]

    @classmethod
    def obtener_por_id(
        cls,
        id_registro,
    ):

        class _Registro:

            total = 100
            estado = "borrador"
            fecha_creacion = "2024-01-01"

        return _Registro()


def test_campos_cabecera_auditoria_excluye():

    campos = _campos_cabecera_auditoria(
        _ServicioCabecera,
        {
            "total": 200,
            "estado": "borrador",
            "fecha_creacion": "2025-01-01",
        },
    )

    assert "fecha_creacion" not in campos
    assert "total" in campos


def test_auditar_cabecera_respeta_exclusion():

    cambios = auditar_cabecera_antes(
        _ServicioCabecera,
        1,
        {
            "total": 200,
            "estado": "borrador",
            "fecha_creacion": "2025-01-01",
        },
    )

    assert "total" in cambios
    assert "fecha_creacion" not in cambios


def test_servicio_base_auditoria_campos_cabecera():

    assert (
        ServicioBase.auditoria_campos_cabecera
        is None
    )
    assert (
        ServicioBase.auditoria_campos_cabecera_excluir
        is None
    )


def test_status_etapa_crm():

    factory = StatusColumnFactory()

    columna = StatusColumn(
        nombre="etapa",
        etiqueta="Etapa",
    )

    badge = factory.badge_info(
        "ganada",
        columna,
    )

    assert badge["texto"] == "Ganada"
    assert badge["fondo"] == "#D1FAE5"


def test_html_listado_registros():

    html = _html_listado_registros(
        "Prueba",
        [
            "Col1",
            "Col2",
        ],
        [
            [
                "A",
                "B",
            ],
        ],
    )

    assert "<table>" in html
    assert "Prueba" in html
    assert "<td>A</td>" in html


def test_servicio_pos_listar_historial_delega(
    monkeypatch,
):

    capturado = {}

    def _fake_listar(
        **kwargs,
    ):

        capturado.update(
            kwargs,
        )

        return []

    monkeypatch.setattr(
        ServicioPOSVenta.repositorio_log,
        "listar_historial",
        _fake_listar,
    )

    ServicioPOSVenta.listar_historial(
        fecha_desde=date(
            2026,
            1,
            1,
        ),
        fecha_hasta=date(
            2026,
            1,
            31,
        ),
        limite=100,
    )

    assert capturado["limite"] == 100
