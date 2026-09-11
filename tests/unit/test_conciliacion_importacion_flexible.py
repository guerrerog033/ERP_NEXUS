from __future__ import annotations

from datetime import date

from aplicacion.modulos.tesoreria.conciliacion.servicios import (
    ServicioConciliacionBancaria,
)


class TestNormalizarEncabezado:

    def test_quita_tildes_y_normaliza_mayusculas(self):

        assert (
            ServicioConciliacionBancaria._normalizar_encabezado(
                "Descripción",
            )
            == "descripcion"
        )

    def test_colapsa_espacios_internos(self):

        assert (
            ServicioConciliacionBancaria._normalizar_encabezado(
                "  Fecha   Transacción ",
            )
            == "fecha transaccion"
        )


class TestResolverValorTipo:

    def test_valor_con_signo_positivo_es_credito(self):

        valor, tipo = ServicioConciliacionBancaria._resolver_valor_tipo(
            {"valor": "150000"},
        )

        assert valor == 150000.0
        assert tipo == "credito"

    def test_valor_con_signo_negativo_es_debito(self):

        valor, tipo = ServicioConciliacionBancaria._resolver_valor_tipo(
            {"valor": "-80000"},
        )

        assert valor == -80000.0
        assert tipo == "debito"

    def test_columnas_debito_credito_separadas_prioriza_credito(self):

        valor, tipo = ServicioConciliacionBancaria._resolver_valor_tipo(
            {"debito": "0", "credito": "200000"},
        )

        assert valor == 200000.0
        assert tipo == "credito"

    def test_columnas_debito_credito_separadas_usa_debito(self):

        valor, tipo = ServicioConciliacionBancaria._resolver_valor_tipo(
            {"debito": "50000", "credito": ""},
        )

        assert valor == 50000.0
        assert tipo == "debito"

    def test_ambas_columnas_vacias_retorna_none(self):

        valor, _tipo = ServicioConciliacionBancaria._resolver_valor_tipo(
            {"debito": "0", "credito": "0"},
        )

        assert valor is None

    def test_alias_valor_debito_con_espacio(self):

        valor, tipo = ServicioConciliacionBancaria._resolver_valor_tipo(
            {"valor debito": "35000", "valor credito": ""},
        )

        assert valor == 35000.0
        assert tipo == "debito"


class TestDetectarDelimitador:

    def test_detecta_punto_y_coma(self):

        contenido = "Fecha;Descripcion;Valor\n2026-01-01;Pago;1000\n"

        assert (
            ServicioConciliacionBancaria._detectar_delimitador(
                contenido,
            )
            == ";"
        )

    def test_detecta_coma_por_defecto(self):

        contenido = "Fecha,Descripcion,Valor\n2026-01-01,Pago,1000\n"

        assert (
            ServicioConciliacionBancaria._detectar_delimitador(
                contenido,
            )
            == ","
        )

    def test_contenido_vacio_no_falla(self):

        assert (
            ServicioConciliacionBancaria._detectar_delimitador("")
            == ","
        )


class TestParsearValor:

    def test_formato_colombiano_punto_miles_coma_decimal(self):

        assert (
            ServicioConciliacionBancaria._parsear_valor("1.234.567,89")
            == 1234567.89
        )

    def test_formato_colombiano_con_prefijo_moneda(self):

        assert (
            ServicioConciliacionBancaria._parsear_valor("$ 1.234.567,89")
            == 1234567.89
        )

    def test_formato_estadounidense_coma_miles_punto_decimal(self):

        assert (
            ServicioConciliacionBancaria._parsear_valor("1,234,567.89")
            == 1234567.89
        )

    def test_entero_sin_separador(self):

        assert (
            ServicioConciliacionBancaria._parsear_valor("200000")
            == 200000.0
        )

    def test_separador_unico_de_tres_digitos_es_miles(self):

        assert (
            ServicioConciliacionBancaria._parsear_valor("1.500") == 1500.0
        )
        assert (
            ServicioConciliacionBancaria._parsear_valor("100.000")
            == 100000.0
        )

    def test_coma_decimal_sin_miles(self):

        assert (
            ServicioConciliacionBancaria._parsear_valor("150,75") == 150.75
        )

    def test_negativo_con_signo(self):

        assert (
            ServicioConciliacionBancaria._parsear_valor("-80.000,50")
            == -80000.5
        )

    def test_negativo_entre_parentesis(self):

        assert (
            ServicioConciliacionBancaria._parsear_valor("(1.234,56)")
            == -1234.56
        )

    def test_negativo_con_signo_al_final(self):

        assert (
            ServicioConciliacionBancaria._parsear_valor("1.234,56-")
            == -1234.56
        )

    def test_texto_no_numerico_retorna_cero(self):

        assert (
            ServicioConciliacionBancaria._parsear_valor("sin valor")
            == 0.0
        )

    def test_none_y_vacio_retornan_cero(self):

        assert ServicioConciliacionBancaria._parsear_valor(None) == 0.0
        assert ServicioConciliacionBancaria._parsear_valor("") == 0.0


class TestParsearFecha:

    def test_formato_iso(self):

        assert ServicioConciliacionBancaria._parsear_fecha(
            "2026-03-01",
        ) == date(2026, 3, 1)

    def test_dia_mes_anio_con_barra_y_guion(self):

        assert ServicioConciliacionBancaria._parsear_fecha(
            "01/03/2026",
        ) == date(2026, 3, 1)
        assert ServicioConciliacionBancaria._parsear_fecha(
            "01-03-2026",
        ) == date(2026, 3, 1)

    def test_anio_de_dos_digitos(self):

        assert ServicioConciliacionBancaria._parsear_fecha(
            "01/03/26",
        ) == date(2026, 3, 1)

    def test_compacto_aaaammdd(self):

        assert ServicioConciliacionBancaria._parsear_fecha(
            "20260301",
        ) == date(2026, 3, 1)

    def test_descarta_componente_de_hora(self):

        assert ServicioConciliacionBancaria._parsear_fecha(
            "01/03/2026 13:04:22",
        ) == date(2026, 3, 1)
        assert ServicioConciliacionBancaria._parsear_fecha(
            "2026-03-01T09:15:00",
        ) == date(2026, 3, 1)

    def test_mes_textual_espanol_e_ingles(self):

        assert ServicioConciliacionBancaria._parsear_fecha(
            "15-ene-2026",
        ) == date(2026, 1, 15)
        assert ServicioConciliacionBancaria._parsear_fecha(
            "15 DIC 25",
        ) == date(2025, 12, 15)
        assert ServicioConciliacionBancaria._parsear_fecha(
            "3/septiembre/2026",
        ) == date(2026, 9, 3)
        assert ServicioConciliacionBancaria._parsear_fecha(
            "07-Aug-2026",
        ) == date(2026, 8, 7)

    def test_valores_no_reconocibles_retornan_none(self):

        assert (
            ServicioConciliacionBancaria._parsear_fecha("") is None
        )
        assert (
            ServicioConciliacionBancaria._parsear_fecha("no es fecha")
            is None
        )
        assert (
            ServicioConciliacionBancaria._parsear_fecha("31/02/2026")
            is None
        )
