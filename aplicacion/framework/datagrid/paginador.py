from __future__ import annotations

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QPushButton,
    QWidget,
)


class Paginador(QWidget):
    """
    Control de paginación para DataGrid / CRUD.
    """

    pagina_cambiada = Signal(
        int,
    )

    def __init__(
        self,
        parent=None,
    ):

        super().__init__(
            parent,
        )

        self._pagina = 1
        self._por_pagina = 50
        self._total = 0

        layout = QHBoxLayout(
            self,
        )

        layout.setContentsMargins(
            0,
            0,
            0,
            0,
        )

        self.btn_anterior = QPushButton(
            "◀ Anterior",
        )

        self.btn_siguiente = QPushButton(
            "Siguiente ▶",
        )

        self.lbl_estado = QLabel(
            "Página 1 de 1",
        )

        self.lbl_estado.setStyleSheet(
            "color: #475569; padding: 0 8px;",
        )

        layout.addStretch()

        layout.addWidget(
            self.btn_anterior,
        )

        layout.addWidget(
            self.lbl_estado,
        )

        layout.addWidget(
            self.btn_siguiente,
        )

        layout.addStretch()

        self.btn_anterior.clicked.connect(
            self._anterior,
        )

        self.btn_siguiente.clicked.connect(
            self._siguiente,
        )

        self.configurar(
            1,
            50,
            0,
        )

    @property
    def pagina(
        self,
    ) -> int:

        return self._pagina

    @property
    def por_pagina(
        self,
    ) -> int:

        return self._por_pagina

    def configurar(
        self,
        pagina: int,
        por_pagina: int,
        total: int,
    ) -> None:

        self._pagina = max(
            1,
            pagina,
        )

        self._por_pagina = max(
            1,
            por_pagina,
        )

        self._total = max(
            0,
            total,
        )

        paginas = self._total_paginas()

        self.lbl_estado.setText(
            f"Página {self._pagina} de {paginas}"
            + (
                f" · {self._total} registros"
                if self._total
                else ""
            ),
        )

        self.btn_anterior.setEnabled(
            self._pagina > 1,
        )

        self.btn_siguiente.setEnabled(
            self._pagina
            < paginas,
        )

        self.setVisible(
            self._total
            > self._por_pagina,
        )

    def _total_paginas(
        self,
    ) -> int:

        if self._total <= 0:

            return 1

        return max(
            1,
            (
                self._total
                + self._por_pagina
                - 1
            )
            // self._por_pagina,
        )

    def _anterior(
        self,
    ) -> None:

        if self._pagina <= 1:

            return

        self.pagina_cambiada.emit(
            self._pagina - 1,
        )

    def _siguiente(
        self,
    ) -> None:

        if (
            self._pagina
            >= self._total_paginas()
        ):

            return

        self.pagina_cambiada.emit(
            self._pagina + 1,
        )
