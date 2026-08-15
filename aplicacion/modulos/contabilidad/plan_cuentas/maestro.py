from aplicacion.framework.crud.crud_master import CrudMaster

from .datasource import PlanCuentaDataSource
from .formulario import FormularioPlanCuenta
from .servicios import ServicioPlanCuenta


class MaestroPlanCuentas(CrudMaster):

    titulo = "Plan de cuentas"

    titulo_singular = "Cuenta contable"

    datasource = PlanCuentaDataSource

    formulario = FormularioPlanCuenta

    def __init__(self):

        ServicioPlanCuenta.inicializar()

        super().__init__()
