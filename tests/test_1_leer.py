"""Peldaño 1: leer las series del BCE. pytest tests/test_1_leer.py"""

import pytest

import fuentes
from prima import leer_serie

CSV = """KEY,FREQ,REF_AREA,TIME_PERIOD,OBS_VALUE
IRS.M.ES.L.L40.CI.0000.EUR.N.Z,M,ES,2026-08,3.635
IRS.M.ES.L.L40.CI.0000.EUR.N.Z,M,ES,2026-07,3.534
IRS.M.ES.L.L40.CI.0000.EUR.N.Z,M,ES,2026-09,
IRS.M.ES.L.L40.CI.0000.EUR.N.Z,M,ES,2026-06,3.413
"""


def test_fecha_y_valor_de_la_más_antigua_a_la_más_reciente():
    assert leer_serie(CSV) == [("2026-06", 3.413), ("2026-07", 3.534), ("2026-08", 3.635)]


def test_el_valor_es_un_número():
    assert all(isinstance(valor, float) for _, valor in leer_serie(CSV))


def test_dos_series_mezcladas_son_un_error():
    with pytest.raises(ValueError):
        leer_serie(CSV + "IRS.M.DE.L.L40.CI.0000.EUR.N.Z,M,DE,2026-08,3.2\n")


def test_el_bono_español_y_el_alemán_de_verdad():
    es, de = dict(leer_serie(fuentes.copia("bono_es"))), dict(leer_serie(fuentes.copia("bono_de")))
    assert es["2012-07"] == 6.794 and de["2012-07"] == 1.24
    assert min(es) == "1991-11" and min(de) == "1990-01"


def test_la_curva_trae_siete_series():
    with pytest.raises(ValueError):
        leer_serie(fuentes.copia("curva"))
