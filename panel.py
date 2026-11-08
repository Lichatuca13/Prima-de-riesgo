"""Lo que enseña la página. El peldaño 4 es tuyo; lo demás ya está escrito.

Cada cifra que sale en pantalla lleva su unidad, su fecha y su fuente. Sin eso, quien la lea no sabe qué mide, de
cuándo es ni de dónde sale, y no la puede usar.
"""

from datetime import date, datetime, timedelta, timezone

import fuentes
import prima

PROPIA = "Elaboración propia con datos del BCE"
PLAZOS_EN_AÑOS = {"3M": 0.25, "1Y": 1, "2Y": 2, "5Y": 5, "10Y": 10, "20Y": 20, "30Y": 30}


# ---------- Peldaño 4: enseñar ----------

def cifras(prima_mensual: list[tuple[str, float]], es: list[tuple[str, float]], de: list[tuple[str, float]],
           decisiones: list[dict]) -> list[dict]:
    """Las cifras de la cabecera de la página, en este orden de ids:

    - "prima": la última prima de riesgo, en "puntos básicos".
    - "bono_es" y "bono_de": el último rendimiento de cada bono, en "%".
    - "cambio_mes" y "cambio_año": la última prima menos la de hace un mes y la de hace un año, en "puntos
      básicos", redondeado a un decimal. Si falta la de antes, esa cifra no va.
    - "maximo": la prima más alta de la serie, en "puntos básicos".
    - "deposito": el tipo de la facilidad de depósito de la última decisión del BCE, en "%".

    Cada cifra es un dict con id, nombre (para personas, en español), valor, unidad, fecha, fuente y url.
    - fecha: la de la observación («2026-09»); la del máximo es la del máximo y la del depósito, la de la decisión.
    - fuente: lo calculado aquí (la prima, los cambios y el máximo) es PROPIA; los bonos, "BCE"; el depósito,
      "BCE, tabla de tipos oficiales".
    - url: la "web" de su fuente en fuentes.FUENTES; para lo calculado, la del bono español.
    Usa prima.resumen del peldaño 2.
    """
    raise NotImplementedError("Peldaño 4: cifras")


# ---------- Ya escrito ----------

def curva(texto: str) -> dict:
    """La curva de tipos AAA de la zona euro el último día y un año antes, con la pendiente de 10 menos 2 años."""
    series = {plazo.removeprefix("SR_"): prima.leer_serie(csv) for plazo, csv in fuentes.partir_por_serie(texto).items()}
    diez = series["10Y"]
    hoy = diez[-1][0]
    un_año_antes = (date.fromisoformat(hoy) - timedelta(days=365)).isoformat()
    antes = max((f for f, _ in diez if f <= un_año_antes), default=diez[0][0])
    plazos = []
    for plazo, años in PLAZOS_EN_AÑOS.items():
        valores = dict(series[plazo])
        plazos.append({"plazo": plazo, "años": años, "hoy": round(valores[hoy], 3),
                       "antes": round(valores[antes], 3) if antes in valores else None})
    return {"fecha": hoy, "fecha_antes": antes, "plazos": plazos,
            "pendiente": round((dict(series["10Y"])[hoy] - dict(series["2Y"])[hoy]) * 100, 1)}


def comprobar_raspado(decisiones: list[dict], deposito: list[tuple[str, float]]) -> dict:
    """Lo raspado de la web contra la serie oficial del tipo de depósito: tienen que ser las mismas fechas y tipos."""
    distintas = sorted(set((d["fecha"], d["deposito"]) for d in decisiones) ^ set(deposito))
    return {"coincide": not distintas, "decisiones": len(decisiones), "distintas": distintas[:5]}


def construir(datos: dict, hoy: date | None = None) -> dict:
    """Todo lo que la página necesita, a partir de lo que devuelve fuentes.recopilar()."""
    textos = datos["textos"]
    es, de = prima.leer_serie(textos["bono_es"]), prima.leer_serie(textos["bono_de"])
    mensual = prima.prima_de_riesgo(es, de)
    decisiones = prima.decisiones_bce(textos["tipos"])
    return {
        "cifras": cifras(mensual, es, de, decisiones),
        "prima": mensual,
        "decisiones": decisiones,
        "curva": curva(textos["curva"]),
        "proxima_reunion": prima.proxima_reunion(textos["calendario"], hoy or date.today()),
        "comprobacion": comprobar_raspado(decisiones, prima.leer_serie(textos["deposito"])),
        "fuentes": [{"id": id_, "nombre": f["nombre"], "web": f["web"], "origen": datos["origen"][id_]}
                    for id_, f in fuentes.FUENTES.items()],
        "guardada": datos["guardada"],
        "avisos": datos["avisos"],
        "calculado": datetime.now(timezone.utc).isoformat(timespec="minutes"),
    }
