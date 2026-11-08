"""La prima de riesgo de España con datos del BCE. Los peldaños 1, 2 y 3 son tuyos.

Las funciones llevan firma y docstring claros porque en la sesión 8 serán las herramientas de un agente: el
docstring es lo que el agente leerá para saber qué hace cada una y cuándo usarla.
"""

import re
from datetime import date


# ---------- Peldaño 1: leer ----------

def leer_serie(texto: str) -> list[tuple[str, float]]:
    """Una serie del CSV que sirve la API del BCE, como lista de (fecha, valor) de la más antigua a la más reciente.

    La fecha es la columna TIME_PERIOD tal cual («2026-09» o «2026-11-05») y el valor, la columna OBS_VALUE como
    float. Las filas sin valor no van. Si el CSV trae más de una serie, es decir, más de un valor distinto en la
    columna KEY, lanza ValueError: mezclar dos series en silencio da números que parecen buenos y no lo son.
    """
    raise NotImplementedError("Peldaño 1: leer_serie")


# ---------- Peldaño 2: calcular ----------

def prima_de_riesgo(es: list[tuple[str, float]], de: list[tuple[str, float]]) -> list[tuple[str, float]]:
    """La prima de riesgo de España: rendimiento del bono español a 10 años menos el del alemán, en puntos básicos.

    Un punto básico es una centésima de punto porcentual: 3,927 % menos 3,473 % son 45,4 puntos. Redondeada a un
    decimal. Solo las fechas que están en las dos series, de la más antigua a la más reciente.
    """
    raise NotImplementedError("Peldaño 2: prima_de_riesgo")


def resumen(prima: list[tuple[str, float]]) -> dict:
    """Lo que hay que saber de la serie mensual de la prima.

    {"ultimo", "hace_un_mes", "hace_un_año", "maximo", "minimo"}, cada uno una tupla (fecha, puntos).
    "hace_un_mes" y "hace_un_año" son la observación del mes anterior a la última y la del mismo mes del año
    anterior; si ese mes no está en la serie, None. "maximo" y "minimo" son los de toda la serie y, si se repite
    el valor, la primera vez que se alcanzó.
    """
    raise NotImplementedError("Peldaño 2: resumen")


# ---------- Peldaño 3: raspar ----------

def decisiones_bce(html: str) -> list[dict]:
    """Las decisiones de tipos de interés del BCE, sacadas de la tabla de su web, de la más antigua a la más reciente.

    Cada fila de la tabla es una decisión:
    {"fecha": "AAAA-MM-DD", "deposito": float, "refinanciacion": float | None, "marginal": float}.

    Las columnas de la tabla: año, día y mes en inglés («16 Sep.»), facilidad de depósito, operaciones principales
    de financiación a tipo fijo, las mismas a tipo mínimo de puja y facilidad marginal de crédito. "refinanciacion"
    es el tipo fijo si lo hay; si no, el mínimo de puja; si no hay ninguno, None.

    Mira datos/tipos.html antes de empezar: la tabla tiene cuatro trampas y los tests las comprueban. Solo con la
    biblioteca estándar (re o html.parser).
    """
    raise NotImplementedError("Peldaño 3: decisiones_bce")


# ---------- Ya escrito: la próxima reunión del BCE, un raspado de ejemplo ----------

def proxima_reunion(html: str, hoy: date) -> dict | None:
    """La próxima decisión de política monetaria del calendario del BCE, desde `hoy` incluido.

    {"fecha": "AAAA-MM-DD", "texto": "..."}. Es el segundo día de la reunión, el de la rueda de prensa. None si el
    calendario no trae ninguna.
    """
    reuniones = []
    for dia, texto in re.findall(r"<dt>\s*(\d{2}/\d{2}/\d{4})\s*</dt>\s*<dd>(.*?)</dd>", html, re.S):
        texto = " ".join(re.sub(r"<[^>]+>", " ", texto).split())
        d, m, a = map(int, dia.split("/"))
        if date(a, m, d) >= hoy and "monetary policy meeting" in texto and "press conference" in texto:
            reuniones.append({"fecha": date(a, m, d).isoformat(), "texto": texto})
    return min(reuniones, key=lambda r: r["fecha"], default=None)
