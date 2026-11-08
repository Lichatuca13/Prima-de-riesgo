"""Un párrafo para quien no sabe finanzas, escrito por un LLM con las cifras del panel. Ya está escrito.

El modelo no calcula: recibe las cifras que ha hecho Python y las cuenta con palabras. Antes de enseñar el párrafo,
Python comprueba que cada número que trae está en esas cifras. Si no hay clave, si el modelo no contesta o si pone
un número que no está, la página sale igual, sin el párrafo.
"""

import re

import modelos

MESES = ("enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto", "septiembre", "octubre",
         "noviembre", "diciembre")
# Un párrafo por cada juego de cifras: hasta que el BCE publique un mes nuevo, no se vuelve a llamar al modelo.
GUARDADOS: dict[str, dict] = {}


def fecha_legible(fecha: str) -> str:
    """«2026-09» es «septiembre de 2026» y «2026-09-16», «16 de septiembre de 2026»."""
    partes = [int(p) for p in fecha.split("-")]
    texto = f"{MESES[partes[1] - 1]} de {partes[0]}"
    return f"{partes[2]} de {texto}" if len(partes) == 3 else texto


def lineas_de(panel: dict) -> list[str]:
    """Las cifras del panel, una por línea y escritas para personas: «Prima de riesgo...: 45,4 puntos básicos (...)»."""
    lineas = [f"- {c['nombre']}: {c['valor']:g} {c['unidad']} ({fecha_legible(c['fecha'])})".replace(".", ",")
              for c in panel["cifras"]]
    if panel.get("proxima_reunion"):
        lineas.append(f"- Próxima decisión de tipos del BCE: {fecha_legible(panel['proxima_reunion']['fecha'])}")
    return lineas


def prompt(lineas: list[str]) -> str:
    return "\n".join([
        "Explica en un solo párrafo de tres a cinco frases, en español y para alguien que no sabe nada de finanzas, "
        "cómo está la prima de riesgo de España. Empieza contando qué es en una frase sencilla.",
        "Reglas:",
        "- Usa solo las cifras de abajo. Escribe los números como están o redondeados a entero; ni cuentas ni "
        "números que no estén.",
        "- Ni consejos de inversión ni predicciones.",
        "- Sin títulos, listas ni negritas: solo el párrafo.",
        "Cifras:",
        *lineas,
    ])


def numeros_de(texto: str) -> list[str]:
    """Los números del texto escritos de una sola forma, para poder compararlos.

    Con un solo separador, es el decimal: «3,25» y «3.25» salen «3,25». Con los dos, el último es el decimal y el
    otro separa los miles: «19.336,30» sale «19336,3». Sin ceros que sobren: «2,50» sale «2,5».
    """
    texto = re.sub(r"(?<=\d)[ \u00a0\u202f](?=\d{3}(?!\d))", "", texto)
    numeros = []
    for n in re.findall(r"\d+(?:[.,]\d+)*", texto):
        separadores = [s for s in n if s in ".,"]
        if len(set(separadores)) == 2:
            decimal = separadores[-1]
            entero, _, parte = n.rpartition(decimal)
            entero = entero.replace("." if decimal == "," else ",", "")
        elif len(separadores) == 1:
            entero, _, parte = n.replace(",", ".").partition(".")
        else:
            entero, parte = n.replace(".", "").replace(",", ""), ""
        entero, parte = entero.lstrip("0") or "0", parte.rstrip("0")
        numeros.append(f"{entero},{parte}" if parte else entero)
    return numeros


def sin_respaldo(texto: str, lineas: list[str]) -> list[str]:
    """Los números del párrafo que no están en las cifras, ni tal cual ni redondeados a entero."""
    validos = set(numeros_de("\n".join(lineas)))
    validos |= {str(round(float(n.replace(",", ".")))) for n in validos}
    return list(dict.fromkeys(n for n in numeros_de(texto) if n not in validos))


def explicacion(panel: dict) -> dict:
    """{"texto", "modelo", "motivo"}: el párrafo comprobado, o texto None y el motivo por el que no hay párrafo."""
    lineas = lineas_de(panel)
    clave = "\n".join(lineas)
    if clave in GUARDADOS:
        return GUARDADOS[clave]
    if not modelos.proveedores():
        return {"texto": None, "modelo": None, "motivo": "No hay clave de LLM."}
    pedido = prompt(lineas)
    try:
        for _ in range(2):
            texto, modelo = modelos.redactar(pedido)
            fallan = sin_respaldo(texto, lineas)
            if not fallan:
                GUARDADOS[clave] = {"texto": texto, "modelo": modelo, "motivo": None}
                return GUARDADOS[clave]
            pedido = (prompt(lineas) + "\n\nTu respuesta anterior tenía números que no están en las cifras: "
                      + ", ".join(fallan) + ". Escríbela otra vez sin ellos:\n" + texto)
    except RuntimeError as e:
        return {"texto": None, "modelo": None, "motivo": str(e)[:200]}
    return {"texto": None, "modelo": modelo, "motivo": f"El modelo usó números que no están en las cifras: {', '.join(fallan)}."}
