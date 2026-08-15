"""
Framework NEXUS — capa de UI y orquestación.

Mapa oficial: ``docs/Framework-v1.0.md``

- ``base/`` — Page, FormularioBase, MaestroBase
- ``form/`` — FormEngine, fields, binding, documento
- ``table/`` — TableEngine, column definitions
- ``crud/`` — CrudMaster + mixins (punto único de CRUD)
- ``datagrid/`` — tabla con búsqueda en maestros
- ``documento/`` — DocumentoResult, DocumentoService (DV → ``dominio/documentos``)
- ``datasource/`` — adaptador SQLAlchemy → controlador

Reglas de negocio puras: ``aplicacion.dominio`` (documentos, impuestos, crédito).
Persistencia: ``aplicacion.comunes``.
"""
