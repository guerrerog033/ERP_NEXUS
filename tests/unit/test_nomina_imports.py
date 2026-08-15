def test_imports_nomina():

    from aplicacion.modulos.nomina.empleados.maestro import (
        MaestroEmpleados,
    )
    from aplicacion.modulos.nomina.hub import (
        HubNomina,
    )
    from aplicacion.modulos.nomina.liquidacion.vista import (
        LiquidacionNominaPage,
    )
    from aplicacion.framework.menu_manifest import (
        MODULOS,
    )

    assert MaestroEmpleados.titulo == "Empleados"
    assert HubNomina.titulo == "Nómina"
    assert LiquidacionNominaPage.titulo == "Liquidación de nómina"
    assert "NominaContratos" in MODULOS
    assert "CRM" in MODULOS
    assert "ReporteNomina" in MODULOS
