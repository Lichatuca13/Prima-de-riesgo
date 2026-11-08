"""Peldaño 4: cada cifra con su unidad, su fecha y su fuente. pytest tests/test_4_panel.py"""

import json
from datetime import date

import pytest

import fuentes
import panel

IDS = ["prima", "bono_es", "bono_de", "cambio_mes", "cambio_año", "maximo", "deposito"]
PRIMA = [("2025-09", 56.9), ("2026-08", 45.0), ("2026-09", 45.4)]
ES, DE = [("2026-08", 3.635), ("2026-09", 3.927)], [("2026-08", 3.185), ("2026-09", 3.473)]
DECISIONES = [{"fecha": "2026-06-17", "deposito": 2.25, "refinanciacion": 2.4, "marginal": 2.65},
              {"fecha": "2026-09-16", "deposito": 2.5, "refinanciacion": 2.65, "marginal": 2.9}]


@pytest.fixture(scope="module")
def cifras():
    return {c["id"]: c for c in panel.cifras(PRIMA, ES, DE, DECISIONES)}


def test_las_cifras_y_su_orden():
    assert [c["id"] for c in panel.cifras(PRIMA, ES, DE, DECISIONES)] == IDS


def test_cada_cifra_dice_qué_mide_cuándo_y_de_dónde_sale(cifras):
    for c in cifras.values():
        assert set(c) == {"id", "nombre", "valor", "unidad", "fecha", "fuente", "url"}
        assert c["nombre"] and c["fuente"] and c["url"].startswith("https://")
        assert c["unidad"] in ("%", "puntos básicos")


def test_los_valores_y_las_fechas(cifras):
    assert (cifras["prima"]["valor"], cifras["prima"]["fecha"]) == (45.4, "2026-09")
    assert (cifras["bono_es"]["valor"], cifras["bono_de"]["valor"]) == (3.927, 3.473)
    assert cifras["cambio_mes"]["valor"] == 0.4
    assert cifras["cambio_año"]["valor"] == -11.5
    assert (cifras["maximo"]["valor"], cifras["maximo"]["fecha"]) == (56.9, "2025-09")
    assert (cifras["deposito"]["valor"], cifras["deposito"]["fecha"]) == (2.5, "2026-09-16")


def test_las_unidades(cifras):
    assert [cifras[i]["unidad"] for i in IDS] == ["puntos básicos", "%", "%", "puntos básicos", "puntos básicos",
                                                  "puntos básicos", "%"]


def test_lo_calculado_es_elaboración_propia(cifras):
    for i in ("prima", "cambio_mes", "cambio_año", "maximo"):
        assert cifras[i]["fuente"] == panel.PROPIA
    assert cifras["bono_es"]["fuente"] == "BCE"
    assert cifras["deposito"]["url"] == fuentes.FUENTES["tipos"]["web"]


def test_sin_el_dato_de_hace_un_año_esa_cifra_no_va():
    ids = [c["id"] for c in panel.cifras(PRIMA[1:], ES, DE, DECISIONES)]
    assert "cambio_año" not in ids and "cambio_mes" in ids


def test_el_panel_entero_con_la_copia_de_datos():
    datos = panel.construir(fuentes.recopilar(solo_copia=True), hoy=date(2026, 11, 8))
    json.dumps(datos)
    assert datos["comprobacion"]["coincide"]
    assert [c["id"] for c in datos["cifras"]] == IDS
    assert len(datos["curva"]["plazos"]) == 7
