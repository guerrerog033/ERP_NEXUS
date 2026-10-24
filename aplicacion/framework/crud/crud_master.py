from __future__ import annotations

from sqlalchemy.exc import IntegrityError

from aplicacion.framework.base.maestro_base import MaestroBase
from aplicacion.framework.crud.crud_datos import CrudDatos
from aplicacion.framework.crud.crud_eventos import CrudEventos
from aplicacion.framework.crud.crud_formulario_dialog import (
    CrudFormularioDialog,
)
from aplicacion.framework.crud.crud_navegacion import CrudNavegacion
from aplicacion.framework.crud.crud_tabla import CrudTabla
from aplicacion.framework.table import TableEngine


class CrudMaster(
    MaestroBase,
    CrudTabla,
    CrudDatos,
    CrudEventos,
    CrudFormularioDialog,
    CrudNavegacion,
):
    """
    CRUD Universal del ERP NEXUS.

    Coordina todos los componentes del CRUD
    utilizando mixins especializados.
    """

    titulo = "Maestro"

    controlador = None

    datasource = None

    formulario = None

    usar_table_view = True

    # ==================================================
    # Inicialización
    # ==================================================

    def __init__(self):

        super().__init__()

        self._inicializar()

    # ==================================================
    # Inicializar CRUD
    # ==================================================

    def _inicializar(self):

        if self.formulario is None:

            raise RuntimeError(
                "No existe formulario configurado."
            )

        self.crear_backend()

        # ------------------------------------------
        # Definiciones
        # ------------------------------------------

        self.form_definition = self.formulario.definition

        if self.form_definition is None:

            raise RuntimeError(
                "El formulario no tiene una FormDefinition."
            )

        self.table_definition = (
            self.form_definition.table_definition
        )

        if self.table_definition is None:

            raise RuntimeError(
                "La FormDefinition no tiene table_definition. "
                "Defina columnas en la definición o use una "
                "clase stub de listado para documentos "
                "(ver MaestroComprobantes).",
            )

        if self.table_definition is None:

            raise RuntimeError(
                f"{self.form_definition.__name__} "
                "no tiene table_definition."
            )

        titulo_modulo = type(
            self,
        ).titulo

        if (
            titulo_modulo
            in {
                "Maestro",
                "",
            }
        ):

            self.titulo = (
                self.form_definition.titulo
            )

        # ------------------------------------------
        # Table Engine
        # ------------------------------------------

        self.table_engine = TableEngine(
            self.table_definition,
            usar_table_view=getattr(
                type(self),
                "usar_table_view",
                True,
            ),
        )

        self.tabla = self.table_engine.construir()

        self.table_binding = (
            self.table_engine.binding
        )

        self.grid.reemplazar_tabla(
            self.tabla
        )

        self.conectar_eventos()

        self._pagina_actual = 1

        self._ultimo_total = 0

        self._filtros_consulta = []

        self._filtro_fechas = []

        self._configurar_paginacion()

        self._configurar_filtros()

        self._configurar_busqueda_avanzada()

        self.cargar_datos()

    def _configurar_paginacion(
        self,
    ) -> None:

        if not getattr(
            self,
            "paginacion_habilitada",
            False,
        ):

            self.paginador = None

            return

        from aplicacion.framework.datagrid.paginador import (
            Paginador,
        )

        self.paginador = Paginador(
            self,
        )

        self.paginador.pagina_cambiada.connect(
            self.ir_a_pagina,
        )

        layout_pie = getattr(
            self.grid,
            "layout_pie",
            None,
        )

        if layout_pie is not None:

            layout_pie.addWidget(
                self.paginador,
            )

        else:

            self.grid.layout_principal.addWidget(
                self.paginador,
            )

    # ==================================================
    # Buscar por / rango de fechas
    # ==================================================

    # Nombre de la columna de fecha para el filtro "Desde / Hasta".
    # None = detectarla en la definición de la tabla; "" = sin filtro.
    columna_fecha_filtro: str | None = None

    def _columna_fecha(
        self,
    ) -> str:

        configurada = type(
            self,
        ).columna_fecha_filtro

        if configurada is not None:

            return configurada

        from aplicacion.framework.table.date_column import DateColumn

        for columna in self.table_definition.obtener_columnas():

            if isinstance(
                columna,
                DateColumn,
            ) and columna.nombre in {
                "fecha",
                "fecha_emision",
                "fecha_documento",
                "fecha_elaboracion",
            }:

                return columna.nombre

        return ""

    def _configurar_busqueda_avanzada(
        self,
    ) -> None:

        toolbar = getattr(
            self.grid,
            "toolbar",
            None,
        )

        if toolbar is None or not hasattr(
            toolbar,
            "configurar_columnas_busqueda",
        ):

            return

        toolbar.configurar_columnas_busqueda(
            [
                (
                    columna.nombre,
                    columna.etiqueta,
                )
                for columna in self.table_definition.obtener_visibles()
                if columna.etiqueta
            ],
        )

        toolbar.columna_busqueda_cambiada.connect(
            lambda _c: self._aplicar_filtro_columna(),
        )

        self._campo_fecha = self._columna_fecha()

        if self._campo_fecha:

            toolbar.habilitar_fechas(
                True,
            )

            toolbar.fechas_aplicadas.connect(
                self._aplicar_rango_fechas,
            )

            toolbar.fechas_limpiadas.connect(
                self._limpiar_rango_fechas,
            )

    def _aplicar_rango_fechas(
        self,
        desde,
        hasta,
    ) -> None:

        from aplicacion.framework.datagrid.filtros import FiltroConsulta

        self._filtro_fechas = [
            FiltroConsulta(
                campo=self._campo_fecha,
                operador="gte",
                valor=desde.toPython(),
            ),
            FiltroConsulta(
                campo=self._campo_fecha,
                operador="lte",
                valor=hasta.toPython(),
            ),
        ]

        self._pagina_actual = 1

        self.cargar_datos()

    def _limpiar_rango_fechas(
        self,
    ) -> None:

        self._filtro_fechas = []

        self._pagina_actual = 1

        self.cargar_datos()

    def _aplicar_filtro_columna(
        self,
    ) -> None:
        """
        "Buscar por" una columna: oculta las filas cargadas cuyo valor
        en esa columna no contiene el texto buscado.
        """

        toolbar = getattr(
            self.grid,
            "toolbar",
            None,
        )

        tabla = self.table_engine.widget if self.table_engine else None

        if toolbar is None or tabla is None or not hasattr(
            toolbar,
            "columna_busqueda",
        ):

            return

        modelo = tabla.model()

        if modelo is None:

            return

        columna = toolbar.columna_busqueda()

        texto = (
            self.txt_buscar.text().strip().lower()
            if self.txt_buscar is not None
            else ""
        )

        nombres = self.table_definition.nombres()

        indice_columna = (
            nombres.index(columna)
            if columna in nombres
            else -1
        )

        for fila in range(
            modelo.rowCount(),
        ):

            oculta = False

            if texto and indice_columna >= 0:

                valor = modelo.index(
                    fila,
                    indice_columna,
                ).data()

                oculta = texto not in str(
                    valor if valor is not None else "",
                ).lower()

            tabla.setRowHidden(
                fila,
                oculta,
            )

        self.grid.actualizar_posicion()

    # ==================================================
    # Crear backend
    # ==================================================

    def crear_backend(self):

        if self.datasource is not None:

            self.datasource = self.datasource()

    # ==================================================
    # Obtener backend
    # ==================================================

    def backend(self):

        return (
            self.datasource
            or self.controlador
        )

    # ==================================================
    # Crear formulario
    # ==================================================

    def crear_formulario(
        self,
        id_registro=None,
        parent=None,
        *,
        modo=None,
    ):

        from aplicacion.framework.app_context import (
            AppContext,
        )

        kwargs = {
            "id_registro": id_registro,
        }

        if modo is not None:
            kwargs["modo"] = modo

        if parent is not None:

            kwargs["parent"] = parent

        elif AppContext.area_trabajo is not None:

            kwargs["parent"] = (
                AppContext.area_trabajo
            )

        return self.formulario(
            **kwargs
        )

    # ==================================================
    # Eliminar registro
    # ==================================================

    def eliminar(self):

        id_registro = (
            self.obtener_id_seleccionado()
        )

        if id_registro is None:

            self.mostrar_error(
                "Seleccione un registro."
            )

            return

        if not self.confirmar(
            "¿Desea eliminar este registro?"
        ):

            return

        try:

            self.backend().eliminar(
                id_registro
            )

        except IntegrityError:

            self.mostrar_error(
                "No se puede eliminar este registro "
                "porque está siendo usado en otros "
                "documentos."
            )

            return

        except Exception as error:

            self.mostrar_error(
                f"No se pudo eliminar el registro: {error}"
            )

            return

        self.cargar_datos()