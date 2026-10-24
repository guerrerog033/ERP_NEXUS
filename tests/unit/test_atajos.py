from __future__ import annotations

from PySide6.QtWidgets import QApplication, QLineEdit, QPushButton, QTextEdit, QVBoxLayout, QWidget

from aplicacion.framework.ui.atajos import (
    TEXTO_AYUDA,
    _enter_avanza,
    pulsar,
    registrar_atajos,
)


def _qapp():
    return QApplication.instance() or QApplication([])


def test_ayuda_lista_atajos_principales():
    for texto in ("Ctrl+S", "F3", "F4", "Ctrl+L", "Ctrl+N"):
        assert texto in TEXTO_AYUDA


def test_registrar_atajos_acepta_varias_secuencias():
    _qapp()
    widget = QWidget()
    creados = registrar_atajos(widget, ((("Ctrl+S", "F10"), lambda: None), ("F3", lambda: None)))
    assert len(creados) == 3


def test_pulsar_ignora_botones_ocultos():
    _qapp()
    contador = []
    boton = QPushButton()
    boton.clicked.connect(lambda: contador.append(1))
    pulsar(boton)
    assert contador == []


def test_enter_avanza_solo_en_formularios_marcados():
    _qapp()
    formulario = QWidget()
    layout = QVBoxLayout(formulario)
    campo = QLineEdit()
    notas = QTextEdit()
    layout.addWidget(campo)
    layout.addWidget(notas)

    assert not _enter_avanza(campo)

    formulario.setProperty("enter_avanza", True)
    assert _enter_avanza(campo)
    assert not _enter_avanza(notas)

    formulario.setProperty("enter_propio", True)
    formulario.setProperty("enter_avanza", False)
    assert not _enter_avanza(campo)
