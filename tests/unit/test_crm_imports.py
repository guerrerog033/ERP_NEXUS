def test_imports_nomina_complementos():

    from aplicacion.modulos.nomina.contratos.maestro import (
        MaestroContratos,
    )
    from aplicacion.modulos.nomina.integracion import (
        IntegracionNomina,
    )
    from aplicacion.modulos.nomina.novedades.maestro import (
        MaestroNovedades,
    )
    from aplicacion.modulos.nomina.prestaciones.vista import (
        PrestacionesNominaPage,
    )
    from aplicacion.integraciones.dian.generador_nomina_electronica import (
        GeneradorNominaElectronica,
    )

    assert MaestroContratos.titulo == "Contratos históricos"
    assert MaestroNovedades.titulo == "Novedades de nómina"
    assert PrestacionesNominaPage.titulo == "Prestaciones sociales"
    assert IntegracionNomina.__name__ == "IntegracionNomina"
    assert GeneradorNominaElectronica.__name__ == "GeneradorNominaElectronica"


def test_imports_crm():

    from aplicacion.modulos.crm.hub import (
        HubCRM,
    )
    from aplicacion.modulos.crm.oportunidades.maestro import (
        MaestroOportunidades,
    )
    from aplicacion.modulos.crm.actividades.maestro import (
        MaestroActividadesCRM,
    )
    from aplicacion.modulos.reportes.nomina.vista import (
        ReporteNominaPage,
    )

    assert HubCRM.titulo == "CRM"
    assert MaestroOportunidades.titulo == "Oportunidades"
    assert MaestroActividadesCRM.titulo == "Actividades CRM"
    assert ReporteNominaPage.titulo == "Resumen de nómina"
