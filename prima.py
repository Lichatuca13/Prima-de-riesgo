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
    
    from csv import DictReader
    from io import StringIO

    lector = DictReader(StringIO(texto.lstrip("\ufeff")))
    columnas = {"KEY", "TIME_PERIOD", "OBS_VALUE"}

    if not lector.fieldnames or not columnas.issubset(lector.fieldnames):
        raise ValueError("Faltan columnas obligatorias")

    claves = set()
    observaciones = []

    for fila in lector:
        clave = (fila["KEY"] or "").strip()
        fecha = (fila["TIME_PERIOD"] or "").strip()
        valor = (fila["OBS_VALUE"] or "").strip()

        if clave:
            claves.add(clave)

        if not fecha or not valor:
            continue

        observaciones.append((fecha, float(valor)))

    if len(claves) != 1:
        raise ValueError("El CSV debe contener una sola serie")

    return sorted(observaciones, key=lambda dato: dato[0])



# ---------- Peldaño 2: calcular ----------

def prima_de_riesgo(es: list[tuple[str, float]], de: list[tuple[str, float]]) -> list[tuple[str, float]]:
    """La prima de riesgo de España: rendimiento del bono español a 10 años menos el del alemán, en puntos básicos.

    Un punto básico es una centésima de punto porcentual: 3,927 % menos 3,473 % son 45,4 puntos. Redondeada a un
    decimal. Solo las fechas que están en las dos series, de la más antigua a la más reciente.
    """
    alemania = dict(de)
    resultado = []

    for fecha, tasa_espana in es:
        if fecha in alemania:
            diferencia_pb = round(
                (tasa_espana - alemania[fecha]) * 100, 1
            )
            resultado.append((fecha, diferencia_pb))

    return sorted(resultado, key=lambda fila: fila[0])


def resumen(prima: list[tuple[str, float]]) -> dict:
    """Lo que hay que saber de la serie mensual de la prima.

    {"ultimo", "hace_un_mes", "hace_un_año", "maximo", "minimo"}, cada uno una tupla (fecha, puntos).
    "hace_un_mes" y "hace_un_año" son la observación del mes anterior a la última y la del mismo mes del año
    anterior; si ese mes no está en la serie, None. "maximo" y "minimo" son los de toda la serie y, si se repite
    el valor, la primera vez que se alcanzó.
    """
    if not prima:
        return {
            "ultimo": None,
            "hace_un_mes": None,
            "hace_un_año": None,
            "maximo": None,
            "minimo": None,
        }

    ordenada = sorted(prima, key=lambda dato: dato[0])
    ultimo = ordenada[-1]
    fecha = ultimo[0]

    anio, mes = map(int, fecha[:7].split("-"))
    mes_previo = 12 if mes == 1 else mes - 1
    anio_previo = anio - 1 if mes == 1 else anio

    fecha_mes = f"{anio_previo:04d}-{mes_previo:02d}"
    fecha_anio = f"{anio - 1:04d}-{mes:02d}"

    por_fecha = {f: (f, v) for f, v in ordenada}

    return {
        "ultimo": ultimo,
        "hace_un_mes": por_fecha.get(fecha_mes),
        "hace_un_año": por_fecha.get(fecha_anio),
        "maximo": max(ordenada, key=lambda dato: dato[1]),
        "minimo": min(ordenada, key=lambda dato: dato[1]),
    }


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

    import html as html_util

    tablas = re.findall(
        r"<table\b[^>]*>.*?</table\s*>",
        html, flags=re.I | re.S
    )

    tabla_bce = None
    for tabla in tablas:
        contenido = html_util.unescape(
            re.sub(r"<[^>]+>", " ", tabla)
        ).lower()
        if "deposit facility" in contenido and "marginal lending facility" in contenido:
            tabla_bce = tabla
            break

    if tabla_bce is None:
        raise ValueError("No se encontró la tabla de tipos del BCE")

    def numero(texto):
        texto = texto.replace("−", "-").strip()
        encontrado = re.search(r"[-+]?\d+(?:[.,]\d+)?", texto)
        if encontrado is None:
            return None
        return float(encontrado.group().replace(",", "."))

    meses = {
        "jan": 1, "feb": 2, "mar": 3, "apr": 4,
        "may": 5, "jun": 6, "jul": 7, "aug": 8,
        "sep": 9, "oct": 10, "nov": 11, "dec": 12
    }

    resultado = []
    anio = None

    filas = re.findall(
        r"<tr\b[^>]*>(.*?)</tr\s*>",
        tabla_bce, flags=re.I | re.S
    )

    for fila in filas:
        celdas_html = re.findall(
            r"<t[dh]\b[^>]*>(.*?)</t[dh]\s*>",
            fila, flags=re.I | re.S
        )
        celdas = [
            html_util.unescape(re.sub(r"<[^>]+>", " ", c)).strip()
            for c in celdas_html
        ]

        if not celdas:
            continue

        coincidencia_anio = re.search(r"\b(?:19|20)\d{2}\b", celdas[0])
        if coincidencia_anio:
            anio = int(coincidencia_anio.group())

        if anio is None or len(celdas) < 5:
            continue

        if len(celdas) >= 6:
            fecha_texto = celdas[1]
            tasas = celdas[2:6]
        else:
            fecha_texto = celdas[0]
            tasas = celdas[1:5]

        fecha_encontrada = re.search(
            r"(\d{1,2})\s+([A-Za-z]{3,9})",
            fecha_texto
        )
        if fecha_encontrada is None:
            continue

        dia = int(fecha_encontrada.group(1))
        mes = meses.get(fecha_encontrada.group(2)[:3].lower())
        if mes is None:
            continue

        fecha = date(anio, mes, dia).isoformat()

        deposito = numero(tasas[0])
        fijo = numero(tasas[1])
        variable = numero(tasas[2])
        marginal = numero(tasas[3])

        refinanciacion = fijo if fijo is not None else variable

        resultado.append({
            "fecha": fecha,
            "deposito": deposito,
            "refinanciacion": refinanciacion,
            "marginal": marginal
        })

    return sorted(resultado, key=lambda dato: dato["fecha"])


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
