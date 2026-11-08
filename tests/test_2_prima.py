"""Peldaño 2: la prima de riesgo y su resumen. pytest tests/test_2_prima.py"""

import fuentes
from prima import leer_serie, prima_de_riesgo, resumen


def test_en_puntos_básicos_y_con_un_decimal():
    assert prima_de_riesgo([("2026-09", 3.927)], [("2026-09", 3.473)]) == [("2026-09", 45.4)]


def test_solo_las_fechas_de_las_dos_series():
    es = [("2026-07", 3.5), ("2026-08", 3.6), ("2026-09", 3.9)]
    de = [("2026-08", 3.1), ("2026-09", 3.4), ("2026-10", 3.0)]
    assert prima_de_riesgo(es, de) == [("2026-08", 50.0), ("2026-09", 50.0)]


def test_julio_de_2012():
    es, de = leer_serie(fuentes.copia("bono_es")), leer_serie(fuentes.copia("bono_de"))
    assert dict(prima_de_riesgo(es, de))["2012-07"] == 555.4


SERIE = [("2025-09", 56.9), ("2025-10", 61.2), ("2025-11", 58.0), ("2025-12", 52.3), ("2026-01", 50.1),
         ("2026-02", 49.8), ("2026-03", 61.2), ("2026-04", 47.0), ("2026-05", 46.1), ("2026-06", 46.0),
         ("2026-07", 46.4), ("2026-08", 45.0), ("2026-09", 45.4)]


def test_resumen_último_hace_un_mes_y_hace_un_año():
    r = resumen(SERIE)
    assert r["ultimo"] == ("2026-09", 45.4)
    assert r["hace_un_mes"] == ("2026-08", 45.0)
    assert r["hace_un_año"] == ("2025-09", 56.9)


def test_resumen_máximo_y_mínimo_la_primera_vez():
    r = resumen(SERIE)
    assert r["maximo"] == ("2025-10", 61.2)
    assert r["minimo"] == ("2026-08", 45.0)


def test_resumen_en_enero_el_mes_anterior_es_diciembre():
    r = resumen(SERIE[:5])
    assert r["ultimo"] == ("2026-01", 50.1)
    assert r["hace_un_mes"] == ("2025-12", 52.3)


def test_resumen_sin_el_dato_de_antes_es_none():
    r = resumen([("2026-07", 46.4), ("2026-09", 45.4)])
    assert r["hace_un_mes"] is None and r["hace_un_año"] is None
