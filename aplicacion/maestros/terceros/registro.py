from aplicacion.dominio.documentos import registrar as registrar_consulta_documento

from .documento.manager import DocumentoManager


def registrar():

    registrar_consulta_documento(
        DocumentoManager.buscar,
    )
