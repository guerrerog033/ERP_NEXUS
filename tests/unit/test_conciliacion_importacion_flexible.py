from __future__ import annotations

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
