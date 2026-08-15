from __future__ import annotations

# Valores de referencia Colombia — actualizar anualmente.
SMMLV = 1_750_905

TASA_SALUD_EMPLEADO = 0.04
TASA_PENSION_EMPLEADO = 0.04
TASA_SALUD_EMPLEADOR = 0.085
TASA_PENSION_EMPLEADOR = 0.12
TASA_CAJA_COMPENSACION = 0.04
TASA_ICBF = 0.03
TASA_SENA = 0.02

AUXILIO_TRANSPORTE = 200_000
TOPE_IBC_SMMLV = 25
DIAS_SEMESTRE = 180
DIAS_ANIO = 360
DIAS_VACACIONES_ANIO = 15

TARIFAS_ARL = {
    "1": 0.00522,
    "2": 0.01044,
    "3": 0.02436,
    "4": 0.04350,
    "5": 0.06960,
}

CODIGO_EPS_DEFECTO = "EPS037"
CODIGO_AFP_DEFECTO = "230201"
CODIGO_ARL_DEFECTO = "140099"
CODIGO_CCF_DEFECTO = "CCF001"

TIPOS_CONTRATO = [
    ("Indefinido", "indefinido"),
    ("Término fijo", "fijo"),
    ("Obra o labor", "obra_labor"),
    ("Aprendizaje", "aprendizaje"),
]

ESTADOS_PERIODO = [
    ("Abierto", "abierto"),
    ("Liquidado", "liquidado"),
    ("Cerrado", "cerrado"),
]

TIPOS_NOVEDAD = [
    ("Horas extra", "hora_extra"),
    ("Incapacidad", "incapacidad"),
    ("Licencia no remunerada", "licencia"),
    ("Bonificación", "bonificacion"),
]

TIPOS_PRESTACION = [
    ("Prima", "prima"),
    ("Cesantías", "cesantias"),
    ("Vacaciones", "vacaciones"),
    ("Intereses cesantías", "intereses_cesantias"),
]
