from aplicacion.framework.crud.crud_master import CrudMaster

from aplicacion.maestros.empresas.datasource import (
    EmpresaDataSource,
)

from aplicacion.maestros.empresas.formulario import (
    EmpresaFormulario,
)


class MaestroEmpresas(CrudMaster):

    titulo = "Empresas"

    titulo_singular = "Empresa"

    datasource = EmpresaDataSource

    formulario = EmpresaFormulario