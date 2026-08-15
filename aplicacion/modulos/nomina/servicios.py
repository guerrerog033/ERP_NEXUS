from __future__ import annotations

from datetime import datetime

from aplicacion.base_datos.conexion import SessionLocal
from aplicacion.comunes.servicio_base import ServicioBase

from .modelos import (
    ContratoEmpleado,
    LiquidacionConcepto,
    LiquidacionNomina,
    NovedadNomina,
    PeriodoNomina,
    ProvisionPrestacion,
)
from .motor_liquidacion import (
    NovedadLiquidacion,
    liquidar_con_arl,
    totales_liquidacion,
)
from .motor_prestaciones import (
    calcular_base_prestacional,
    calcular_prima_semestral,
    calcular_provision_mensual,
)
from .pila_calculos import (
    calcular_ibc_legal,
    descomponer_aportes_pila,
)
from .constantes import (
    CODIGO_AFP_DEFECTO,
    CODIGO_ARL_DEFECTO,
    CODIGO_CCF_DEFECTO,
    CODIGO_EPS_DEFECTO,
    TARIFAS_ARL,
)
from .repositorio import (
    RepositorioContratoEmpleado,
    RepositorioEmpleado,
    RepositorioLiquidacionNomina,
    RepositorioNovedadNomina,
    RepositorioPeriodoNomina,
    RepositorioProvisionPrestacion,
)


class ServicioEmpleado(ServicioBase):

    repositorio = RepositorioEmpleado

    @classmethod
    def validar(
        cls,
        datos,
        id_registro=None,
    ):

        codigo = str(
            datos.get(
                "codigo",
                "",
            )
        ).strip().upper()

        tipo_documento = str(
            datos.get(
                "tipo_documento",
                "",
            )
        ).strip()

        numero_documento = str(
            datos.get(
                "numero_documento",
                "",
            )
        ).strip()

        primer_nombre = str(
            datos.get(
                "primer_nombre",
                "",
            )
        ).strip()

        primer_apellido = str(
            datos.get(
                "primer_apellido",
                "",
            )
        ).strip()

        salario_basico = float(
            datos.get(
                "salario_basico",
                0,
            )
            or 0,
        )

        if not codigo:

            raise ValueError(
                "El código del empleado es obligatorio.",
            )

        if (
            not tipo_documento
            or not numero_documento
        ):

            raise ValueError(
                "El documento del empleado es obligatorio.",
            )

        if not primer_nombre or not primer_apellido:

            raise ValueError(
                "Indique al menos primer nombre y primer apellido.",
            )

        if salario_basico <= 0:

            raise ValueError(
                "El salario básico debe ser mayor a cero.",
            )

        if cls.repositorio.existe_codigo(
            codigo,
            id_registro,
        ):

            raise ValueError(
                "Ya existe un empleado con ese código.",
            )

        if cls.repositorio.existe_documento(
            tipo_documento,
            numero_documento,
            id_registro,
        ):

            raise ValueError(
                "Ya existe un empleado con ese documento.",
            )

        datos["codigo"] = codigo
        datos["tipo_documento"] = tipo_documento
        datos["numero_documento"] = numero_documento
        datos["primer_nombre"] = primer_nombre
        datos["primer_apellido"] = primer_apellido
        datos["salario_basico"] = salario_basico

    @classmethod
    def buscar(
        cls,
        texto,
    ):

        texto = str(
            texto or "",
        ).strip()

        if not texto:

            return cls.obtener_todos()

        return cls.repositorio.buscar(
            texto,
        )


class ServicioNomina:

    MESES = [
        "",
        "Enero",
        "Febrero",
        "Marzo",
        "Abril",
        "Mayo",
        "Junio",
        "Julio",
        "Agosto",
        "Septiembre",
        "Octubre",
        "Noviembre",
        "Diciembre",
    ]

    @classmethod
    def nombre_periodo(
        cls,
        periodo: PeriodoNomina,
    ) -> str:

        mes = cls.MESES[
            periodo.mes
        ] if 1 <= periodo.mes <= 12 else str(
            periodo.mes,
        )

        return f"{mes} {periodo.anio}"

    @classmethod
    def listar_periodos(cls):

        return RepositorioPeriodoNomina.listar_ordenados()

    @classmethod
    def crear_periodo(
        cls,
        *,
        anio: int,
        mes: int,
        observaciones: str = "",
    ) -> PeriodoNomina:

        if mes < 1 or mes > 12:

            raise ValueError(
                "El mes debe estar entre 1 y 12.",
            )

        if anio < 2000:

            raise ValueError(
                "Indique un año válido.",
            )

        existente = (
            RepositorioPeriodoNomina
            .obtener_por_anio_mes(
                anio,
                mes,
            )
        )

        if existente is not None:

            raise ValueError(
                "Ya existe un periodo para ese mes y año.",
            )

        db = SessionLocal()

        try:

            periodo = PeriodoNomina(
                anio=anio,
                mes=mes,
                estado="abierto",
                observaciones=observaciones.strip(),
            )

            db.add(periodo)
            db.commit()
            db.refresh(periodo)

            return periodo

        except Exception:

            db.rollback()

            raise

        finally:

            db.close()

    @classmethod
    def liquidar_periodo(
        cls,
        periodo_id: int,
        *,
        dias_trabajados: int = 30,
    ) -> int:

        db = SessionLocal()

        try:

            periodo = (
                db.query(PeriodoNomina)
                .filter(
                    PeriodoNomina.id
                    == periodo_id,
                )
                .first()
            )

            if periodo is None:

                raise ValueError(
                    "Periodo no encontrado.",
                )

            if periodo.estado == "cerrado":

                raise ValueError(
                    "El periodo está cerrado.",
                )

            empleados = (
                RepositorioEmpleado.listar_activos()
            )

            if not empleados:

                raise ValueError(
                    "No hay empleados activos para liquidar.",
                )

            RepositorioLiquidacionNomina.eliminar_por_periodo(
                periodo_id,
            )

            total_liquidaciones = 0

            for empleado in empleados:

                contrato = (
                    RepositorioContratoEmpleado
                    .obtener_vigente(
                        empleado.id,
                        anio=periodo.anio,
                        mes=periodo.mes,
                    )
                )

                salario_basico = float(
                    (
                        contrato.salario
                        if contrato is not None
                        else empleado.salario_basico
                    )
                    or 0,
                )

                novedades_db = (
                    RepositorioNovedadNomina
                    .listar_por_periodo_empleado(
                        periodo_id,
                        empleado.id,
                    )
                )

                novedades = [
                    NovedadLiquidacion(
                        tipo=item.tipo,
                        cantidad=float(
                            item.cantidad or 0,
                        ),
                        valor=float(
                            item.valor or 0,
                        ),
                    )
                    for item in novedades_db
                ]

                conceptos = liquidar_con_arl(
                    salario_basico=salario_basico,
                    dias_trabajados=dias_trabajados,
                    novedades=novedades,
                    clase_riesgo=str(
                        empleado.clase_riesgo
                        or "1",
                    ),
                )

                totales = totales_liquidacion(
                    conceptos,
                )

                liquidacion = LiquidacionNomina(
                    periodo_id=periodo_id,
                    empleado_id=empleado.id,
                    dias_trabajados=dias_trabajados,
                    total_devengado=totales[
                        "devengado"
                    ],
                    total_deducciones=totales[
                        "deducciones"
                    ],
                    neto_pagar=totales["neto"],
                    total_aportes_patronales=totales[
                        "aportes_patronales"
                    ],
                )

                db.add(liquidacion)
                db.flush()

                for orden, concepto in enumerate(
                    conceptos,
                ):

                    db.add(
                        LiquidacionConcepto(
                            liquidacion_id=liquidacion.id,
                            codigo=concepto.codigo,
                            nombre=concepto.nombre,
                            naturaleza=concepto.naturaleza,
                            valor=concepto.valor,
                            orden=orden,
                        ),
                    )

                total_liquidaciones += 1

            periodo.estado = "liquidado"
            periodo.fecha_liquidacion = datetime.now()

            db.commit()

            return total_liquidaciones

        except Exception:

            db.rollback()

            raise

        finally:

            db.close()

    @classmethod
    def listar_resumen_periodo(
        cls,
        periodo_id: int,
    ) -> list[dict]:

        liquidaciones = (
            RepositorioLiquidacionNomina
            .listar_por_periodo(
                periodo_id,
            )
        )

        filas: list[dict] = []

        for item in liquidaciones:

            empleado = item.empleado

            filas.append(
                {
                    "id": item.id,
                    "codigo": empleado.codigo,
                    "empleado": empleado.nombre_completo,
                    "documento": (
                        f"{empleado.tipo_documento} "
                        f"{empleado.numero_documento}"
                    ),
                    "devengado": float(
                        item.total_devengado or 0,
                    ),
                    "deducciones": float(
                        item.total_deducciones or 0,
                    ),
                    "neto": float(
                        item.neto_pagar or 0,
                    ),
                    "aportes": float(
                        item.total_aportes_patronales
                        or 0,
                    ),
                },
            )

        return filas

    @classmethod
    def totales_periodo(
        cls,
        periodo_id: int,
    ) -> dict[str, float]:

        filas = cls.listar_resumen_periodo(
            periodo_id,
        )

        return {
            "devengado": sum(
                fila["devengado"]
                for fila in filas
            ),
            "deducciones": sum(
                fila["deducciones"]
                for fila in filas
            ),
            "neto": sum(
                fila["neto"]
                for fila in filas
            ),
            "aportes": sum(
                fila["aportes"]
                for fila in filas
            ),
        }

    @classmethod
    def obtener_periodo(
        cls,
        periodo_id: int,
    ):

        return RepositorioPeriodoNomina.obtener_por_id(
            periodo_id,
        )

    @classmethod
    def datos_aportante(cls) -> dict:

        from aplicacion.nucleo.configuracion import (
            Configuracion,
        )

        nit = str(
            Configuracion.obtener(
                "empresa",
                "nit",
            )
            or "",
        ).strip()

        razon = str(
            Configuracion.obtener(
                "empresa",
                "nombre",
            )
            or "",
        ).strip()

        dv = str(
            Configuracion.obtener(
                "empresa",
                "dv",
            )
            or "",
        ).strip()

        return {
            "nit": nit,
            "razon_social": razon,
            "dv": dv,
            "arl_codigo": str(
                Configuracion.obtener(
                    "nomina",
                    "arl_codigo",
                )
                or CODIGO_ARL_DEFECTO,
            ),
        }

    @classmethod
    def datos_pila_periodo(
        cls,
        periodo_id: int,
    ) -> list[dict]:

        liquidaciones = (
            RepositorioLiquidacionNomina
            .listar_por_periodo(
                periodo_id,
            )
        )

        novedades_por_empleado: dict[
            int,
            list,
        ] = {}

        for liquidacion in liquidaciones:

            novedades_por_empleado[
                liquidacion.empleado_id
            ] = (
                RepositorioNovedadNomina
                .listar_por_periodo_empleado(
                    periodo_id,
                    liquidacion.empleado_id,
                )
            )

        filas: list[dict] = []

        for liquidacion in liquidaciones:

            empleado = liquidacion.empleado
            conceptos = {
                item.codigo: float(
                    item.valor or 0,
                )
                for item in liquidacion.conceptos
            }

            devengado = sum(
                float(
                    item.valor or 0,
                )
                for item in liquidacion.conceptos
                if item.naturaleza == "devengo"
            )

            salario_basico = float(
                conceptos.get(
                    "001",
                    devengado,
                )
                or devengado,
            )

            ibc = calcular_ibc_legal(
                devengado,
                salario_basico=salario_basico,
            )

            desglose = descomponer_aportes_pila(
                ibc=ibc,
                salario_basico=salario_basico,
                fsp=conceptos.get(
                    "103",
                    0,
                ),
            )

            clase_riesgo = str(
                empleado.clase_riesgo
                or "1",
            )

            novedad_ige = any(
                n.tipo == "incapacidad"
                for n in novedades_por_empleado.get(
                    empleado.id,
                    [],
                )
            )

            filas.append(
                {
                    "tipo_documento": (
                        "CC"
                        if empleado.tipo_documento
                        == "CC"
                        else empleado.tipo_documento[
                            :2
                        ]
                    ),
                    "numero_documento": empleado.numero_documento,
                    "tipo_cotizante": "01",
                    "subtipo_cotizante": "00",
                    "departamento": empleado.departamento_codigo
                    or "11",
                    "municipio": empleado.municipio_codigo
                    or "001",
                    "primer_apellido": empleado.primer_apellido,
                    "segundo_apellido": empleado.segundo_apellido
                    or "",
                    "primer_nombre": empleado.primer_nombre,
                    "segundo_nombre": empleado.segundo_nombre
                    or "",
                    "dias_cotizados": liquidacion.dias_trabajados,
                    "salario_basico": salario_basico,
                    "salario_integral": bool(
                        empleado.salario_integral,
                    ),
                    "ibc": ibc,
                    "eps_codigo": empleado.eps_codigo
                    or CODIGO_EPS_DEFECTO,
                    "afp_codigo": empleado.afp_codigo
                    or CODIGO_AFP_DEFECTO,
                    "arl_codigo": empleado.arl_codigo
                    or CODIGO_ARL_DEFECTO,
                    "ccf_codigo": CODIGO_CCF_DEFECTO,
                    "clase_riesgo": clase_riesgo,
                    "centro_trabajo": empleado.centro_trabajo
                    or "000000001",
                    "tarifa_arl": TARIFAS_ARL.get(
                        clase_riesgo,
                        TARIFAS_ARL["1"],
                    ),
                    "novedad_ige": novedad_ige,
                    "salud_empleado": conceptos.get(
                        "101",
                        desglose[
                            "salud_empleado"
                        ],
                    ),
                    "pension_empleado": conceptos.get(
                        "102",
                        desglose[
                            "pension_empleado"
                        ],
                    ),
                    "salud_patronal": conceptos.get(
                        "201",
                        desglose[
                            "salud_patronal"
                        ],
                    ),
                    "pension_patronal": conceptos.get(
                        "202",
                        desglose[
                            "pension_patronal"
                        ],
                    ),
                    "fsp": conceptos.get(
                        "103",
                        desglose["fsp"],
                    ),
                    "arl_valor": conceptos.get(
                        "206",
                        0,
                    ),
                    "caja": conceptos.get(
                        "203",
                        desglose["caja"],
                    ),
                    "sena": conceptos.get(
                        "205",
                        desglose["sena"],
                    ),
                    "icbf": conceptos.get(
                        "204",
                        desglose["icbf"],
                    ),
                    "devengado": devengado,
                    "neto": float(
                        liquidacion.neto_pagar
                        or 0,
                    ),
                    "empleado": empleado.nombre_completo,
                    "codigo": empleado.codigo,
                },
            )

        return filas

    @classmethod
    def datos_trabajadores_dian(
        cls,
        periodo_id: int,
    ) -> list[dict]:

        return cls.datos_pila_periodo(
            periodo_id,
        )

    @classmethod
    def provisionar_prestaciones(
        cls,
        periodo_id: int,
    ) -> int:

        periodo = cls.obtener_periodo(
            periodo_id,
        )

        if periodo is None:

            raise ValueError(
                "Periodo no encontrado.",
            )

        empleados = RepositorioEmpleado.listar_activos()

        if not empleados:

            raise ValueError(
                "No hay empleados activos.",
            )

        db = SessionLocal()

        try:

            RepositorioProvisionPrestacion.eliminar_por_periodo(
                periodo_id,
            )

            total = 0

            for empleado in empleados:

                contrato = (
                    RepositorioContratoEmpleado
                    .obtener_vigente(
                        empleado.id,
                        anio=periodo.anio,
                        mes=periodo.mes,
                    )
                )

                salario = float(
                    (
                        contrato.salario
                        if contrato is not None
                        else empleado.salario_basico
                    )
                    or 0,
                )

                liquidacion = (
                    db.query(LiquidacionNomina)
                    .filter(
                        LiquidacionNomina.periodo_id
                        == periodo_id,
                        LiquidacionNomina.empleado_id
                        == empleado.id,
                    )
                    .first()
                )

                dias_trabajados = int(
                    liquidacion.dias_trabajados
                    if liquidacion is not None
                    else 30,
                )

                devengado = float(
                    liquidacion.total_devengado
                    if liquidacion is not None
                    else salario,
                )

                base = calcular_base_prestacional(
                    salario=salario,
                    auxilio_transporte=float(
                        empleado.auxilio_transporte
                        or 0,
                    ),
                    salario_integral=bool(
                        empleado.salario_integral,
                    ),
                    promedio_devengos=devengado,
                )

                provisiones = calcular_provision_mensual(
                    base,
                    dias_trabajados=dias_trabajados,
                )

                for tipo, valor in provisiones.items():

                    db.add(
                        ProvisionPrestacion(
                            periodo_id=periodo_id,
                            empleado_id=empleado.id,
                            tipo=tipo,
                            base=base,
                            valor=valor,
                            estado="provisionado",
                        ),
                    )

                    total += 1

            db.commit()

            return total

        except Exception:

            db.rollback()

            raise

        finally:

            db.close()

    @classmethod
    def listar_provisiones_periodo(
        cls,
        periodo_id: int,
    ) -> list[dict]:

        provisiones = (
            RepositorioProvisionPrestacion
            .listar_por_periodo(
                periodo_id,
            )
        )

        agrupado: dict[
            int,
            dict,
        ] = {}

        for item in provisiones:

            fila = agrupado.setdefault(
                item.empleado_id,
                {
                    "codigo": item.empleado.codigo,
                    "empleado": item.empleado.nombre_completo,
                    "prima": 0.0,
                    "cesantias": 0.0,
                    "vacaciones": 0.0,
                    "intereses_cesantias": 0.0,
                    "total": 0.0,
                },
            )

            fila[item.tipo] = float(
                item.valor or 0,
            )

            fila["total"] += float(
                item.valor or 0,
            )

        return list(
            agrupado.values(),
        )

    @classmethod
    def calcular_prima_semestral_periodo(
        cls,
        periodo_id: int,
    ) -> list[dict]:

        periodo = cls.obtener_periodo(
            periodo_id,
        )

        if periodo is None:

            raise ValueError(
                "Periodo no encontrado.",
            )

        if periodo.mes not in (
            6,
            12,
        ):

            raise ValueError(
                "La prima semestral se calcula en junio o diciembre.",
            )

        empleados = RepositorioEmpleado.listar_activos()
        filas: list[dict] = []

        for empleado in empleados:

            contrato = (
                RepositorioContratoEmpleado
                .obtener_vigente(
                    empleado.id,
                    anio=periodo.anio,
                    mes=periodo.mes,
                )
            )

            salario = float(
                (
                    contrato.salario
                    if contrato is not None
                    else empleado.salario_basico
                )
                or 0,
            )

            base = calcular_base_prestacional(
                salario=salario,
                auxilio_transporte=float(
                    empleado.auxilio_transporte
                    or 0,
                ),
                salario_integral=bool(
                    empleado.salario_integral,
                ),
            )

            valor = calcular_prima_semestral(
                base,
                dias_trabajados_semestre=180,
            )

            filas.append(
                {
                    "codigo": empleado.codigo,
                    "empleado": empleado.nombre_completo,
                    "base": base,
                    "prima_semestral": valor,
                },
            )

        return filas


class ServicioContrato(ServicioBase):

    repositorio = RepositorioContratoEmpleado

    @classmethod
    def validar(
        cls,
        datos,
        id_registro=None,
    ):

        empleado_id = int(
            datos.get(
                "empleado_id",
                0,
            )
            or 0,
        )

        salario = float(
            datos.get(
                "salario",
                0,
            )
            or 0,
        )

        fecha_inicio = datos.get(
            "fecha_inicio",
        )

        if empleado_id <= 0:

            raise ValueError(
                "Seleccione un empleado.",
            )

        if salario <= 0:

            raise ValueError(
                "El salario del contrato debe ser mayor a cero.",
            )

        if fecha_inicio is None:

            raise ValueError(
                "Indique la fecha de inicio del contrato.",
            )


class ServicioNovedad(ServicioBase):

    repositorio = RepositorioNovedadNomina

    @classmethod
    def validar(
        cls,
        datos,
        id_registro=None,
    ):

        periodo_id = int(
            datos.get(
                "periodo_id",
                0,
            )
            or 0,
        )

        empleado_id = int(
            datos.get(
                "empleado_id",
                0,
            )
            or 0,
        )

        tipo = str(
            datos.get(
                "tipo",
                "",
            )
        ).strip()

        cantidad = float(
            datos.get(
                "cantidad",
                0,
            )
            or 0,
        )

        if periodo_id <= 0:

            raise ValueError(
                "Seleccione un periodo de nómina.",
            )

        if empleado_id <= 0:

            raise ValueError(
                "Seleccione un empleado.",
            )

        if not tipo:

            raise ValueError(
                "Seleccione el tipo de novedad.",
            )

        if cantidad <= 0 and tipo in (
            "hora_extra",
            "incapacidad",
        ):

            raise ValueError(
                "Indique la cantidad (horas o días).",
            )
