import importlib


def test_comunes_exporta_bases():
    comunes = importlib.import_module(
        "aplicacion.comunes",
    )

    assert hasattr(
        comunes,
        "ServicioBase",
    )
    assert hasattr(
        comunes,
        "RepositorioBase",
    )
    assert hasattr(
        comunes,
        "ControladorBase",
    )


def test_framework_form_engine():
    engine = importlib.import_module(
        "aplicacion.framework.form.engine",
    )

    assert hasattr(
        engine,
        "FormEngine",
    )
