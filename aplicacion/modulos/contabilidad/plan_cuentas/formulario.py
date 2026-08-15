from aplicacion.framework.base.formulario_base import FormularioBase

from .datasource import PlanCuentaDataSource
from .plan_cuenta_definition import PlanCuentaDefinition


class FormularioPlanCuenta(FormularioBase):

    titulo = "Plan de cuentas"

    definition = PlanCuentaDefinition

    datasource = PlanCuentaDataSource
