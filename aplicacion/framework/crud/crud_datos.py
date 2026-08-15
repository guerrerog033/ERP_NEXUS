class CrudDatos:
    """
    Responsable del acceso a los datos.
    """

    paginacion_habilitada = True

    registros_por_pagina = 50

    filtros_ocultos: set[str] = set()

    usar_carga_asincrona = True

    @property
    def servicio(self):

        return self.backend()

    def _parametros_listado(
        self,
    ) -> dict:

        parametros: dict = {}

        if getattr(
            self,
            "paginacion_habilitada",
            False,
        ):

            parametros.update(
                {
                    "pagina": self._pagina_actual,
                    "por_pagina": self.registros_por_pagina,
                },
            )

        filtros = getattr(
            self,
            "_filtros_consulta",
            None,
        )

        if filtros:

            parametros["filtros"] = filtros

        tipo_filtro = getattr(
            self,
            "tipo_filtro",
            None,
        )

        if tipo_filtro:

            parametros["tipo_tercero"] = tipo_filtro

        return parametros

    def _configurar_filtros(
        self,
    ) -> None:

        definiciones = getattr(
            self.table_definition,
            "filtros",
            None,
        ) or []

        if not definiciones:

            self.panel_filtros = None

            return

        from aplicacion.framework.datagrid.panel_filtros import (
            PanelFiltros,
        )

        ocultos = set(
            getattr(
                self,
                "filtros_ocultos",
                set(),
            )
            or set(),
        )

        self.panel_filtros = PanelFiltros(
            definiciones,
            campos_ocultos=ocultos,
        )

        self.panel_filtros.aplicar.connect(
            self._aplicar_filtros,
        )

        self.panel_filtros.limpiar.connect(
            self._limpiar_filtros,
        )

        self.grid.layout_principal.insertWidget(
            1,
            self.panel_filtros,
        )

    def _aplicar_filtros(
        self,
    ) -> None:

        from aplicacion.framework.datagrid.filtros import (
            construir_filtros,
        )

        if self.panel_filtros is None:

            return

        self._filtros_consulta = construir_filtros(
            self.panel_filtros.definiciones,
            self.panel_filtros.valores(),
        )

        self._pagina_actual = 1

        self.cargar_datos()

    def _limpiar_filtros(
        self,
    ) -> None:

        self._filtros_consulta = []

        self._pagina_actual = 1

        self.cargar_datos()

    def _iniciar_carga(
        self,
        mensaje: str,
        consulta,
    ) -> None:

        if getattr(
            self,
            "_carga_en_progreso",
            False,
        ):
            return

        self._carga_en_progreso = True

        if hasattr(
            self,
            "grid",
        ):
            self.grid.mostrar_carga(
                mensaje,
            )
            self.grid.set_toolbar_habilitado(
                False,
            )

        if not getattr(
            self,
            "usar_carga_asincrona",
            True,
        ):
            try:
                self._aplicar_resultado_listado(
                    consulta(),
                )
            except Exception as exc:
                self._finalizar_carga_error(
                    str(
                        exc,
                    ),
                )
            finally:
                self._carga_en_progreso = False
                if hasattr(
                    self,
                    "grid",
                ):
                    self.grid.ocultar_carga()
                    self.grid.set_toolbar_habilitado(
                        True,
                    )
            return

        from PySide6.QtCore import QThread

        from aplicacion.framework.crud.trabajo_listado import (
            TrabajoListado,
        )

        self._detener_carga_asincrona()

        hilo = QThread()
        trabajo = TrabajoListado(
            consulta,
        )
        trabajo.moveToThread(
            hilo,
        )

        hilo.started.connect(
            trabajo.ejecutar,
        )
        trabajo.terminado.connect(
            self._aplicar_resultado_listado,
        )
        trabajo.terminado.connect(
            hilo.quit,
        )
        trabajo.error.connect(
            self._finalizar_carga_error,
        )
        trabajo.error.connect(
            hilo.quit,
        )
        hilo.finished.connect(
            trabajo.deleteLater,
        )
        hilo.finished.connect(
            hilo.deleteLater,
        )
        hilo.finished.connect(
            self._liberar_carga_asincrona,
        )

        self._hilo_carga = hilo
        self._trabajo_carga = trabajo

        hilo.start()

    def _detener_carga_asincrona(
        self,
    ) -> None:
        hilo = getattr(
            self,
            "_hilo_carga",
            None,
        )

        if hilo is not None and hilo.isRunning():
            hilo.quit()
            hilo.wait(
                3000,
            )

        self._hilo_carga = None
        self._trabajo_carga = None

    def _liberar_carga_asincrona(
        self,
    ) -> None:
        self._carga_en_progreso = False
        self._hilo_carga = None
        self._trabajo_carga = None

        if hasattr(
            self,
            "grid",
        ):
            self.grid.ocultar_carga()
            self.grid.set_toolbar_habilitado(
                True,
            )

    def _finalizar_carga_error(
        self,
        mensaje: str,
    ) -> None:
        self._liberar_carga_asincrona()

        if hasattr(
            self,
            "mostrar_error",
        ):
            self.mostrar_error(
                mensaje,
            )

    def _aplicar_resultado_listado(
        self,
        resultado,
    ) -> None:

        registros = (
            resultado.registros
            if hasattr(
                resultado,
                "registros",
            )
            else resultado
        )

        self._ultimo_total = (
            resultado.total
            if hasattr(
                resultado,
                "total",
            )
            and resultado.total
            else len(
                registros,
            )
        )

        self.llenar_tabla(
            registros,
        )

        self.grid.actualizar_total(
            self._ultimo_total,
        )

        if hasattr(
            self,
            "paginador",
        ) and self.paginador is not None:
            self.paginador.configurar(
                getattr(
                    resultado,
                    "pagina",
                    None,
                )
                or self._pagina_actual,
                getattr(
                    resultado,
                    "por_pagina",
                    None,
                )
                or self.registros_por_pagina,
                self._ultimo_total,
            )

    def cargar_datos(
        self,
    ):

        self._iniciar_carga(
            "Cargando registros...",
            lambda: self.servicio.listar(
                **self._parametros_listado(),
            ),
        )

    def ir_a_pagina(
        self,
        pagina: int,
    ) -> None:

        self._pagina_actual = max(
            1,
            pagina,
        )

        self.cargar_datos()

    def buscar(
        self,
    ):

        texto = (
            self.txt_buscar
            .text()
            .strip()
        )

        if not texto:

            self._pagina_actual = 1

            self.cargar_datos()

            return

        parametros = self._parametros_listado()

        self._iniciar_carga(
            "Buscando...",
            lambda: self.servicio.buscar(
                texto,
                **parametros,
            ),
        )

    def actualizar(
        self,
    ):

        self.cargar_datos()

    def _obtener_registros_exportacion(
        self,
    ) -> list:

        parametros = self._parametros_listado()

        parametros.pop(
            "pagina",
            None,
        )

        total = max(
            getattr(
                self,
                "_ultimo_total",
                0,
            ),
            self.registros_por_pagina,
            1,
        )

        parametros["pagina"] = 1
        parametros["por_pagina"] = total

        texto = ""

        if self.txt_buscar is not None:

            texto = (
                self.txt_buscar
                .text()
                .strip()
            )

        if texto:

            resultado = self.servicio.buscar(
                texto,
                **parametros,
            )

        else:

            resultado = self.servicio.listar(
                **parametros,
            )

        if hasattr(
            resultado,
            "registros",
        ):

            return list(
                resultado.registros,
            )

        if isinstance(
            resultado,
            dict,
        ):

            return list(
                resultado.get(
                    "registros",
                    [],
                ),
            )

        return list(
            resultado or [],
        )

    def exportar_excel(
        self,
    ) -> None:

        from aplicacion.comunes.exportacion import (
            exportar_registros,
        )

        registros = (
            self._obtener_registros_exportacion()
        )

        exportar_registros(
            self.table_definition,
            registros,
            parent=self,
            titulo=self.titulo,
        )

    exportar_csv = exportar_excel

    def exportar_pdf(
        self,
    ) -> None:

        from aplicacion.comunes.exportacion import (
            exportar_registros_pdf,
        )

        registros = (
            self._obtener_registros_exportacion()
        )

        exportar_registros_pdf(
            self.table_definition,
            registros,
            parent=self,
            titulo=self.titulo,
        )
