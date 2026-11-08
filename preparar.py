"""Deja todo listo antes de clase. Ejecútalo las veces que haga falta.

    python preparar.py

1. Comprueba Python y los paquetes de requirements.txt.
2. Comprueba que esta carpeta es tu copia del repositorio, la que creó el botón Deploy, y no la de Juanjo.
3. Con cada clave de LLM que encuentre en .env, prueba el servicio.
4. Prueba cada fuente del BCE. Si alguna falla, la app usará su copia de datos/, así que no es grave.
"""

import importlib
import importlib.util
import subprocess
import sys
import time
from pathlib import Path

AQUI = Path(__file__).resolve().parent
PAQUETES = ("fastapi", "uvicorn", "certifi", "pytest", "httpx2")


def linea(bien: bool, texto: str) -> None:
    print(f"  {'bien ' if bien else 'falta'}  {texto}")


def paquetes() -> bool:
    print("Instalación")
    version = sys.version_info >= (3, 10)
    linea(version, f"Python {sys.version.split()[0]} (hace falta 3.10 o más)")
    faltan = [p for p in PAQUETES if importlib.util.find_spec(p) is None]
    linea(not faltan, "paquetes: " + (f"faltan {', '.join(faltan)}. pip install -r requirements.txt" if faltan
                                      else ", ".join(PAQUETES)))
    return version and not faltan


def repositorio() -> None:
    print("\nTu copia en GitHub")
    try:
        origen = subprocess.run(["git", "remote", "get-url", "origin"], cwd=AQUI, capture_output=True, text=True,
                                check=True).stdout.strip()
    except FileNotFoundError:
        linea(False, "no encuentro git. Instálalo desde https://git-scm.com")
        return
    except subprocess.CalledProcessError:
        linea(False, "esta carpeta no es un repositorio de git con origin. Clona tu copia: mira el README.")
        return
    if "SimplyJuanjo/hesperides-sesion-7" in origen:
        linea(False, f"has clonado el repositorio de Juanjo ({origen}). Para publicar hace falta tu copia: "
                     "pulsa el botón Deploy del README y clona la que te crea en tu GitHub.")
        return
    linea(True, f"origin es {origen}. Cada git push vuelve a publicar tu app en Vercel.")


def llms(modelos) -> None:
    print("\nEl LLM que explica la prima")
    alguno = False
    for nombre, (_, variable, modelo, _) in modelos.LLMS.items():
        if not modelos.clave(variable):
            linea(False, f"{nombre}: no hay {variable} en .env")
            continue
        try:
            inicio = time.time()
            texto = modelos.llamar_llm(nombre, "Contesta solo con la palabra: listo")
            linea(True, f"{nombre} ({modelo}) contesta «{texto[:30]}» en {time.time() - inicio:.1f} s")
            alguno = True
        except Exception as e:
            linea(False, f"{nombre} ({modelo}): {e}")
    if not alguno:
        print("  Sin clave, la app funciona igual, pero sin el párrafo del LLM. Mira .env.ejemplo.")


def datos(fuentes) -> None:
    print("\nLas fuentes del BCE")
    for id_, fuente in fuentes.FUENTES.items():
        try:
            texto = fuentes.en_directo(id_)
            linea(True, f"{fuente['nombre']}: {len(texto.splitlines())} líneas")
        except Exception as e:
            linea(False, f"{fuente['nombre']}: {e}")
    print(f"  Lo que falle saldrá de la copia del {fuentes.guardada()[:10]}.")


def main() -> None:
    if not paquetes():
        sys.exit("\nArregla la instalación y vuelve a ejecutar python preparar.py")
    # modelos y fuentes importan certifi: solo se pueden importar después de comprobar que está instalado.
    modelos = importlib.import_module("modelos")
    fuentes = importlib.import_module("fuentes")
    repositorio()
    if not (AQUI / ".env").exists():
        print("\nNo hay .env: copia .env.ejemplo como .env y pon tu clave de Groq.")
    llms(modelos)
    datos(fuentes)


if __name__ == "__main__":
    main()
