"""Peldaño 3: raspar la tabla de tipos del BCE. pytest tests/test_3_raspar.py"""

import re

import pytest

import fuentes
from prima import decisiones_bce, leer_serie

TABLA = """<html><body><table>
<thead><tr><th>Year</th><th>Date</th><th>Deposit facility</th><th>Fixed rate</th><th>Minimum bid rate</th>
<th>Marginal lending facility</th></tr></thead>
<tbody>
<tr><td class="number"><strong>2016</strong></td><td class="number">16 Mar.</td><td class="number">&minus;0.40</td>
<td class="number">0.00</td><td class="number">-</td><td class="number">0.25</td></tr>
<tr><td class="number"></td><td class="number">10 Mar.7</td><td class="number">−0.30</td>
<td class="number">-</td><td class="number">0.05</td><td class="number">0.30</td></tr>
</tbody></table></body></html>"""


@pytest.fixture(scope="module")
def decisiones():
    return {d["fecha"]: d for d in decisiones_bce(fuentes.copia("tipos"))}


def test_una_tabla_pequeña():
    assert decisiones_bce(TABLA) == [
        {"fecha": "2016-03-10", "deposito": -0.3, "refinanciacion": 0.05, "marginal": 0.3},
        {"fecha": "2016-03-16", "deposito": -0.4, "refinanciacion": 0.0, "marginal": 0.25},
    ]


def test_cada_decisión_tiene_fecha_y_tipos(decisiones):
    for fecha, d in decisiones.items():
        assert re.fullmatch(r"\d{4}-\d{2}-\d{2}", fecha)
        assert set(d) == {"fecha", "deposito", "refinanciacion", "marginal"}


def test_la_primera_y_la_de_septiembre_de_2026(decisiones):
    assert min(decisiones) == "1999-01-01"
    assert decisiones["1999-01-01"] == {"fecha": "1999-01-01", "deposito": 2.0, "refinanciacion": 3.0, "marginal": 4.5}
    assert decisiones["2026-09-16"] == {"fecha": "2026-09-16", "deposito": 2.5, "refinanciacion": 2.65, "marginal": 2.9}


def test_de_la_más_antigua_a_la_más_reciente():
    fechas = [d["fecha"] for d in decisiones_bce(fuentes.copia("tipos"))]
    assert fechas == sorted(fechas)


def test_trampa_el_año_solo_en_la_primera_fila_del_año(decisiones):
    assert decisiones["2025-03-12"]["deposito"] == 2.5


def test_trampa_notas_pegadas_a_la_fecha(decisiones):
    assert decisiones["2024-09-18"] == {"fecha": "2024-09-18", "deposito": 3.5, "refinanciacion": 3.65, "marginal": 3.9}
    assert decisiones["1999-01-04"]["deposito"] == 2.75


def test_trampa_el_guion_es_que_no_se_aplica(decisiones):
    assert decisiones["2000-06-28"]["refinanciacion"] == 4.25
    assert decisiones["2008-10-09"]["refinanciacion"] is None


def test_trampa_tipos_negativos(decisiones):
    assert decisiones["2019-09-18"]["deposito"] == -0.5


def test_lo_raspado_coincide_con_la_serie_oficial_del_bce():
    """Usa tu peldaño 1. Es la prueba de que el raspado está bien: el BCE publica el tipo de depósito también en su API."""
    raspado = [(d["fecha"], d["deposito"]) for d in decisiones_bce(fuentes.copia("tipos"))]
    assert raspado == leer_serie(fuentes.copia("deposito"))
