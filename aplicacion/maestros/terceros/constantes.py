TIPOS_TERCERO = (
    "Cliente",
    "Proveedor",
    "Empleado",
    "Vendedor",
    "Otro",
)

TIPO_A_ROL = {
    "Cliente": "es_cliente",
    "Proveedor": "es_proveedor",
    "Empleado": "es_empleado",
    "Vendedor": "es_vendedor",
}

ROLES_TERCERO = tuple(
    TIPO_A_ROL.values(),
)

ETIQUETAS_TIPO_TERCERO = {
    "Cliente": "Clientes",
    "Proveedor": "Proveedores",
    "Otro": "Otros",
}

REGIMEN_IVA_OPCIONES = (
    ("No responsable de IVA", "No responsable de IVA"),
    ("Responsable de IVA", "Responsable de IVA"),
    ("Régimen simple de tributación", "Régimen simple de tributación"),
    (
        "No responsable por actividades excluidas",
        "No responsable por actividades excluidas",
    ),
)

RESPONSABILIDAD_FISCAL = (
    (
        "resp_o13",
        "O-13: Gran contribuyente",
    ),
    (
        "resp_o15",
        "O-15: Autorretenedor",
    ),
    (
        "resp_o23",
        "O-23: Agente de retención IVA",
    ),
    (
        "resp_o47",
        "O-47: Régimen simple de tributación",
    ),
    (
        "resp_r99_pn",
        "R-99-PN: No aplica - Otros",
    ),
)

CAMPOS_RESPONSABILIDAD_FISCAL = tuple(
    codigo
    for codigo, _ in RESPONSABILIDAD_FISCAL
)

# Campos exigidos por la DIAN para facturación electrónica (adquiriente).
CAMPOS_DIAN_FACTURACION = (
    "tipo_documento",
    "numero_documento",
    "dv",
    "razon_social",
    "primer_nombre",
    "primer_apellido",
    "direccion",
    "ciudad",
    "departamento",
    "pais",
    "correo",
    "tipo_regimen_iva",
)
