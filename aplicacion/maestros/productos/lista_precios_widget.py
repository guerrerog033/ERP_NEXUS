from __future__ import annotations



from PySide6.QtCore import Qt

from PySide6.QtWidgets import (

    QDoubleSpinBox,

    QHBoxLayout,

    QHeaderView,

    QLabel,

    QTableWidget,

    QVBoxLayout,

    QWidget,

)



from aplicacion.framework.lookup import LookupDialog

from aplicacion.maestros.listas_precio.lista_precio_lookup import (

    ListaPrecioLookup,

)

from aplicacion.maestros.impuestos.celda_impuesto_iva import (
    CeldaImpuestoIVA,
)

from aplicacion.recursos.ui.botones import Botones





COL_IMPUESTO = 0

COL_LISTA = 1

COL_PRECIO = 2





class ListaPreciosProductoWidget(QWidget):



    def __init__(

        self,

        parent=None,

    ):



        super().__init__(

            parent,

        )



        self._crear_ui()



    def _crear_ui(self):



        layout = QVBoxLayout(

            self,

        )



        layout.setContentsMargins(

            0,

            0,

            0,

            0,

        )



        self.tabla = QTableWidget(

            0,

            3,

        )



        self.tabla.setMinimumHeight(

            130,

        )



        self.tabla.setHorizontalHeaderLabels(

            [

                "Impuesto",

                "Lista de precio",

                "Precio",

            ],

        )



        self.tabla.horizontalHeader().setSectionResizeMode(

            COL_IMPUESTO,

            QHeaderView.Stretch,

        )



        self.tabla.horizontalHeader().setSectionResizeMode(

            COL_LISTA,

            QHeaderView.Stretch,

        )



        self.tabla.setColumnWidth(

            COL_PRECIO,

            140,

        )



        self.tabla.verticalHeader().setDefaultSectionSize(

            40,

        )



        layout.addWidget(

            self.tabla,

        )



        acciones = QHBoxLayout()



        self.btn_agregar = Botones.nuevo()



        self.btn_agregar.setText(

            "Agregar lista",

        )



        self.btn_quitar = Botones.eliminar()



        self.btn_quitar.setText(

            "Quitar",

        )



        acciones.addWidget(

            self.btn_agregar,

        )



        acciones.addWidget(

            self.btn_quitar,

        )



        acciones.addStretch()



        layout.addLayout(

            acciones,

        )



        self.btn_agregar.clicked.connect(

            self.agregar_fila,

        )



        self.btn_quitar.clicked.connect(

            self.quitar_fila,

        )



    def _crear_celda_lista(

        self,

        descripcion: str = "",

        lista_precio_id=None,

    ) -> QWidget:



        contenedor = QWidget()



        layout = QHBoxLayout(

            contenedor,

        )



        layout.setContentsMargins(

            4,

            4,

            4,

            4,

        )



        etiqueta = QLabel(

            descripcion

            or "Seleccione lista",

        )



        etiqueta.setWordWrap(

            True,

        )



        btn_buscar = Botones.buscar()



        layout.addWidget(

            etiqueta,

            1,

        )



        layout.addWidget(

            btn_buscar,

        )



        contenedor.etiqueta = etiqueta

        contenedor.lista_precio_id = lista_precio_id



        btn_buscar.clicked.connect(

            lambda _checked=False,

            celda=contenedor: self._buscar_lista(

                celda,

            ),

        )



        return contenedor



    def _fila_de_celda_lista(

        self,

        celda: QWidget,

    ) -> int:



        for fila in range(

            self.tabla.rowCount(),

        ):



            if self.tabla.cellWidget(

                fila,

                COL_LISTA,

            ) is celda:



                return fila



        return -1



    def _buscar_lista(

        self,

        celda: QWidget,

    ):



        dlg = LookupDialog(

            ListaPrecioLookup(),

            titulo="Buscar lista de precio",

            parent=self,

        )



        if not dlg.exec():



            return



        resultado = dlg.resultado



        if resultado is None:



            return



        if self._lista_duplicada(

            resultado.valor,

            self._fila_de_celda_lista(

                celda,

            ),

        ):



            return



        celda.lista_precio_id = resultado.valor



        celda.etiqueta.setText(

            f"{resultado.codigo} - {resultado.texto}",

        )



    def _lista_duplicada(

        self,

        lista_precio_id,

        fila_actual: int,

    ) -> bool:



        for fila in range(

            self.tabla.rowCount(),

        ):



            if fila == fila_actual:



                continue



            celda = self.tabla.cellWidget(

                fila,

                COL_LISTA,

            )



            if (

                celda is not None

                and getattr(

                    celda,

                    "lista_precio_id",

                    None,

                )

                == lista_precio_id

            ):



                return True



        return False



    def agregar_fila(

        self,

        lista_precio_id=None,

        descripcion="",

        precio=0.0,

        impuesto_id=None,

        impuesto_texto="",

    ):



        fila = self.tabla.rowCount()



        self.tabla.insertRow(

            fila,

        )



        celda_impuesto = CeldaImpuestoIVA(
            impuesto_id=impuesto_id,
        )



        self.tabla.setCellWidget(

            fila,

            COL_IMPUESTO,

            celda_impuesto,

        )



        celda_lista = self._crear_celda_lista(

            descripcion,

            lista_precio_id,

        )



        self.tabla.setCellWidget(

            fila,

            COL_LISTA,

            celda_lista,

        )



        spin = QDoubleSpinBox()



        spin.setRange(

            0,

            999999999,

        )



        spin.setDecimals(

            2,

        )



        spin.setValue(

            float(

                precio

                or 0,

            ),

        )



        self.tabla.setCellWidget(

            fila,

            COL_PRECIO,

            spin,

        )



    def quitar_fila(self):



        fila = self.tabla.currentRow()



        if fila < 0:



            return



        self.tabla.removeRow(

            fila,

        )



    def cargar_filas(

        self,

        filas: list[dict],

    ):



        self.tabla.setRowCount(

            0,

        )



        for fila in filas:



            self.agregar_fila(

                lista_precio_id=fila.get(

                    "lista_precio_id",

                ),

                descripcion=fila.get(

                    "descripcion",

                    "",

                ),

                precio=fila.get(

                    "precio",

                    0,

                ),

                impuesto_id=fila.get(

                    "impuesto_id",

                ),

                impuesto_texto=fila.get(

                    "impuesto_texto",

                    "",

                ),

            )



    def obtener_filas(self) -> list[dict]:



        filas = []



        for fila in range(

            self.tabla.rowCount(),

        ):



            celda_impuesto = self.tabla.cellWidget(

                fila,

                COL_IMPUESTO,

            )



            celda_lista = self.tabla.cellWidget(

                fila,

                COL_LISTA,

            )



            spin = self.tabla.cellWidget(

                fila,

                COL_PRECIO,

            )



            lista_precio_id = getattr(

                celda_lista,

                "lista_precio_id",

                None,

            )



            if (

                lista_precio_id is None

                or spin is None

            ):



                continue



            impuesto_id = None



            if isinstance(
                celda_impuesto,
                CeldaImpuestoIVA,
            ):



                impuesto_id = (

                    celda_impuesto.valor()

                )



            filas.append(

                {

                    "lista_precio_id": lista_precio_id,

                    "precio": spin.value(),

                    "impuesto_id": impuesto_id,

                },

            )



        return filas


