"""La app: dos direcciones de datos con FastAPI y la página de web/. Ya está escrita.

    python servir.py   la abre en tu ordenador
    git push           la publica en Vercel, si conectaste el repositorio con el botón Deploy del README

Mientras falte un peldaño, la página dice cuál falta en vez de romperse.
"""

import time
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

import explicar
import fuentes
import panel

AQUI = Path(__file__).resolve().parent
# Cada copia de la app recalcula el panel como mucho cada seis horas; el CDN de Vercel guarda la respuesta otras
# seis. El BCE publica la prima una vez al mes, así que no hace falta más.
SEIS_HORAS = 6 * 3600
GUARDADO: dict = {}

app = FastAPI(title="Prima de riesgo", docs_url=None, redoc_url=None, openapi_url=None)


def panel_al_dia() -> dict:
    if time.time() - GUARDADO.get("hora", 0) > SEIS_HORAS:
        GUARDADO["panel"] = panel.construir(fuentes.recopilar())
        GUARDADO["hora"] = time.time()
    return GUARDADO["panel"]


def respuesta(datos: dict, segundos: int) -> JSONResponse:
    """La respuesta con su caché: el CDN de Vercel la guarda `segundos`; el navegador pregunta siempre."""
    if not segundos:
        return JSONResponse(datos, headers={"Cache-Control": "no-store"})
    return JSONResponse(datos, headers={
        "Cache-Control": "no-cache",
        "Vercel-CDN-Cache-Control": f"max-age={segundos}, stale-while-revalidate={segundos * 4}",
    })


@app.get("/api/panel")
def api_panel() -> JSONResponse:
    try:
        return respuesta(panel_al_dia(), SEIS_HORAS)
    except NotImplementedError as e:
        return respuesta({"pendiente": str(e)}, 0)


@app.get("/api/explicacion")
def api_explicacion() -> JSONResponse:
    try:
        datos = panel_al_dia()
    except NotImplementedError as e:
        return respuesta({"texto": None, "modelo": None, "motivo": str(e)}, 0)
    resultado = explicar.explicacion(datos)
    return respuesta(resultado, SEIS_HORAS if resultado["texto"] else 0)


app.mount("/", StaticFiles(directory=AQUI / "web", html=True), name="web")
