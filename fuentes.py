"""Los datos del BCE: cuatro descargas de su API y dos páginas de su web. Ya está escrito.

    python fuentes.py            enseña qué contesta cada fuente
    python fuentes.py --guardar  renueva la copia de datos/

Cada fuente se guarda en datos/ tal cual la sirve el BCE: CSV o HTML. Si el BCE no contesta, sale de esa copia.
Con la variable de entorno SOLO_COPIA=1 no se descarga nada, que es lo que hacen los tests.
"""

import argparse
import os
import ssl
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from pathlib import Path

import certifi

AQUI = Path(__file__).resolve().parent
DATOS = AQUI / "datos"
SSL = ssl.create_default_context(cafile=certifi.where())

API = "https://data-api.ecb.europa.eu/service/data/"
PORTAL = "https://data.ecb.europa.eu/data/datasets/"
PLAZOS = ("3M", "1Y", "2Y", "5Y", "10Y", "20Y", "30Y")


def serie_bce(nombre: str, conjunto: str, clave: str, extra: str = "") -> dict:
    return {
        "nombre": nombre,
        "descarga": f"{API}{conjunto}/{clave}?format=csvdata&detail=dataonly{extra}",
        "web": f"{PORTAL}{conjunto}/{conjunto}.{clave.split('+')[0]}",
        "señal": "KEY,",
    }


def pagina_bce(nombre: str, url: str, señal: str) -> dict:
    return {"nombre": nombre, "descarga": url, "web": url, "señal": señal}


# "señal" es un trozo de texto que tiene que estar en la respuesta: si no está, el BCE ha devuelto otra cosa.
FUENTES = {
    "bono_es": serie_bce("Rendimiento del bono español a 10 años", "IRS", "M.ES.L.L40.CI.0000.EUR.N.Z"),
    "bono_de": serie_bce("Rendimiento del bono alemán a 10 años", "IRS", "M.DE.L.L40.CI.0000.EUR.N.Z"),
    "deposito": serie_bce("Tipo de la facilidad de depósito del BCE", "FM", "B.U2.EUR.4F.KR.DFR.LEV"),
    "curva": serie_bce("Curva de tipos de la deuda AAA de la zona euro", "YC",
                       "B.U2.EUR.4F.G_N_A.SV_C_YM.SR_10Y+" + "+".join(f"SR_{p}" for p in PLAZOS if p != "10Y"),
                       "&lastNObservations=262"),
    "tipos": pagina_bce("Tabla de tipos de interés oficiales del BCE",
                        "https://www.ecb.europa.eu/stats/policy_and_exchange_rates/key_ecb_interest_rates/html/index.en.html",
                        "<table"),
    "calendario": pagina_bce("Calendario de reuniones del Consejo de Gobierno del BCE",
                             "https://www.ecb.europa.eu/press/calendars/mgcgc/html/index.en.html", "<dl"),
}


def archivo(id_: str) -> Path:
    """Dónde está la copia de la fuente: datos/bono_es.csv, datos/tipos.html..."""
    return DATOS / (id_ + (".csv" if FUENTES[id_]["señal"] == "KEY," else ".html"))


def descargar(url: str, segundos: float = 20) -> str:
    peticion = urllib.request.Request(url, headers={"User-Agent": "hesperides-sesion-7"})
    with urllib.request.urlopen(peticion, timeout=segundos, context=SSL) as r:
        return r.read().decode("utf-8")


def en_directo(id_: str) -> str:
    """La fuente descargada ahora. Si no contesta o devuelve otra cosa, lanza una excepción."""
    texto = descargar(FUENTES[id_]["descarga"])
    if FUENTES[id_]["señal"] not in texto:
        raise RuntimeError("la respuesta no es la que se esperaba")
    return texto


def copia(id_: str) -> str:
    return archivo(id_).read_text(encoding="utf-8")


def guardada() -> str:
    """Cuándo se guardó la copia de datos/, en ISO y en UTC."""
    ruta = DATOS / "guardada.txt"
    return ruta.read_text(encoding="utf-8").strip() if ruta.exists() else ""


def recopilar(solo_copia: bool = False) -> dict:
    """Todas las fuentes: {"textos": {id: texto}, "origen": {id: "directo" | "copia"}, "guardada", "avisos"}."""
    solo_copia = solo_copia or os.environ.get("SOLO_COPIA") == "1"

    def una(id_: str) -> tuple[str, str, str, str | None]:
        if solo_copia:
            return id_, copia(id_), "copia", None
        try:
            return id_, en_directo(id_), "directo", None
        except Exception as e:
            aviso = f"{FUENTES[id_]['nombre']}: el BCE no contesta ({e}). Sale de la copia del {guardada()[:10]}."
            return id_, copia(id_), "copia", aviso

    with ThreadPoolExecutor(len(FUENTES)) as hilos:
        resultados = list(hilos.map(una, FUENTES))
    return {
        "textos": {id_: texto for id_, texto, _, _ in resultados},
        "origen": {id_: origen for id_, _, origen, _ in resultados},
        "guardada": guardada(),
        "avisos": [aviso for *_, aviso in resultados if aviso],
    }


def partir_por_serie(texto: str) -> dict[str, str]:
    """Un CSV del BCE con varias series, partido en un CSV por serie. La clave es el final de la columna KEY: «SR_10Y»."""
    cabecera, *filas = texto.strip().splitlines()
    partes: dict[str, list[str]] = {}
    for fila in filas:
        partes.setdefault(fila.split(",", 1)[0].rsplit(".", 1)[-1], []).append(fila)
    return {serie: "\n".join([cabecera, *lineas]) + "\n" for serie, lineas in partes.items()}


def main() -> None:
    parser = argparse.ArgumentParser(description="Las fuentes de datos del BCE")
    parser.add_argument("--guardar", action="store_true", help="renueva la copia de datos/")
    args = parser.parse_args()
    for id_, fuente in FUENTES.items():
        try:
            texto = en_directo(id_)
        except Exception as e:
            print(f"  falta  {fuente['nombre']}: {e}")
            continue
        print(f"  bien   {fuente['nombre']}: {len(texto.splitlines())} líneas")
        if args.guardar:
            DATOS.mkdir(exist_ok=True)
            archivo(id_).write_text(texto, encoding="utf-8", newline="\n")
    if args.guardar:
        ahora = datetime.now(timezone.utc).isoformat(timespec="minutes")
        (DATOS / "guardada.txt").write_text(ahora + "\n", encoding="utf-8")
        print(f"Copia guardada en datos/ el {ahora}.")
    else:
        print(f"La copia de datos/ es del {guardada()[:10] or '(no hay copia)'}.")


if __name__ == "__main__":
    main()
