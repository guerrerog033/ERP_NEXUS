from pathlib import Path

from aplicacion.dominio.documentos.dv import CalculadoraDV, DVCalculator
from aplicacion.framework.documento.dv import (
    DVCalculator as FrameworkDV,
)
from aplicacion.maestros.terceros.documento.calculadora_dv import (
    CalculadoraDV as TercerosDV,
)


def test_dv_en_dominio():
    assert DVCalculator.calcular("900123456") == FrameworkDV.calcular(
        "900123456",
    )
    assert CalculadoraDV is DVCalculator
    assert TercerosDV is DVCalculator


def test_rutas_legacy_eliminadas():
    raiz = Path(__file__).resolve().parents[2]

    prohibidas = [
        raiz / "aplicacion" / "interfaz" / "estilos.py",
        raiz / "aplicacion" / "framework" / "controles",
        raiz / "aplicacion" / "framework" / "kernel",
        raiz / "aplicacion" / "framework" / "formulario_crud.py",
        raiz / "aplicacion" / "framework" / "maestro_crud.py",
        raiz / "aplicacion" / "framework" / "navegacion.py",
        raiz / "aplicacion" / "base_datos" / "modelos.py",
        raiz / "aplicacion" / "comunes" / "maestro_base.py",
        raiz / "aplicacion" / "comunes" / "formulario_base.py",
        raiz / "init_db.py",
    ]

    for ruta in prohibidas:
        assert not ruta.exists(), f"Legacy no eliminado: {ruta}"


def test_estilos_usa_tokens():
    from aplicacion.recursos.estilos import colores, dimensiones
    from aplicacion.recursos.estilos.estilos import Estilos

    assert hasattr(Estilos, "boton_guardar")
    assert colores.PRIMARY
    assert dimensiones.CONTROL_MD
