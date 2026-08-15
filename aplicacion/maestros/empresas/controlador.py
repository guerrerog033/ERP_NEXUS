from aplicacion.comunes.controlador_base import ControladorBase
from aplicacion.maestros.empresas.servicios import EmpresaServicio


class EmpresaControlador(ControladorBase):

    servicio = EmpresaServicio