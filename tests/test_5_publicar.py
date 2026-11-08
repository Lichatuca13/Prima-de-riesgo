"""Peldaño 5: publicar. pytest tests/test_5_publicar.py

Los tres primeros miran la app en tu ordenador. Los dos últimos, la que está en internet: hacen falta git push y tu
dirección de Vercel en la línea «Mi app:» del README.
"""

import json
import re
import ssl
import subprocess
import urllib.request
from pathlib import Path

import certifi
import pytest
from fastapi.testclient import TestClient

import app as aplicacion
import explicar

AQUI = Path(__file__).resolve().parent.parent
CLAVES = re.compile(r"gsk_[A-Za-z0-9]{20,}|AIza[0-9A-Za-z_-]{30,}|sk-[A-Za-z0-9_-]{20,}")


@pytest.fixture
def cliente(monkeypatch):
    monkeypatch.setenv("SOLO_COPIA", "1")
    aplicacion.GUARDADO.clear()
    return TestClient(aplicacion.app)


def test_la_página_y_el_panel_en_tu_ordenador(cliente):
    assert "<html" in cliente.get("/").text
    datos = cliente.get("/api/panel").json()
    assert "pendiente" not in datos, datos.get("pendiente")
    assert len(datos["cifras"]) >= 6


def test_sin_clave_de_llm_la_página_funciona_igual(cliente, monkeypatch):
    monkeypatch.delenv("GROQ_API_KEY", raising=False)
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    explicar.GUARDADOS.clear()
    assert "pendiente" not in cliente.get("/api/panel").json()
    respuesta = cliente.get("/api/explicacion").json()
    assert respuesta["texto"] is None and respuesta["motivo"]


def test_no_hay_claves_en_lo_que_subes_a_git():
    archivos = subprocess.run(["git", "ls-files"], cwd=AQUI, capture_output=True, text=True, check=True).stdout.split()
    assert ".env" not in archivos, "Has subido .env a git: bórralo con git rm --cached .env y cambia tus claves."
    for archivo in archivos:
        ruta = AQUI / archivo
        if ruta.suffix in (".py", ".md", ".txt", ".json", ".js", ".html", ".css", ".toml", ".ini", ".ejemplo"):
            assert not CLAVES.search(ruta.read_text(encoding="utf-8", errors="ignore")), f"Hay una clave en {archivo}"


def mi_app() -> str:
    linea = re.search(r"^Mi app: *(\S*)", (AQUI / "README.md").read_text(encoding="utf-8"), re.M)
    url = linea.group(1).rstrip("/") if linea else ""
    assert re.fullmatch(r"https://[a-z0-9-]+(\.[a-z0-9-]+)*\.vercel\.app", url), \
        "Pon en el README la dirección de tu app en Vercel, así: «Mi app: https://prima-de-riesgo-tunombre.vercel.app»"
    return url


def leer(url: str) -> str:
    peticion = urllib.request.Request(url, headers={"User-Agent": "hesperides-sesion-7"})
    contexto = ssl.create_default_context(cafile=certifi.where())
    with urllib.request.urlopen(peticion, timeout=60, context=contexto) as r:
        return r.read().decode("utf-8")


def test_tu_dirección_de_vercel_está_en_el_readme():
    mi_app()


def test_tu_app_en_internet_tiene_todos_los_peldaños():
    url = mi_app()
    assert "<html" in leer(url)
    datos = json.loads(leer(url + "/api/panel"))
    assert "pendiente" not in datos, f"Tu app en internet dice: {datos.get('pendiente')}. ¿Has hecho git push?"
    assert len(datos["cifras"]) >= 6
