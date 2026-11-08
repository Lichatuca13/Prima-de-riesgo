"""La app en tu ordenador. Ya está escrito.

    python servir.py          la abre en http://127.0.0.1:8000 con los datos del BCE de hoy
    python servir.py --copia  la abre con la copia de datos/, sin conexión

Cada vez que guardas un archivo .py, se recarga sola. Para pararla, Ctrl+C.
"""

import argparse
import os
import threading
import webbrowser

import uvicorn

DIRECCION = "http://127.0.0.1:8000"

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="La app en tu ordenador")
    parser.add_argument("--copia", action="store_true", help="usa solo la copia de datos/")
    if parser.parse_args().copia:
        os.environ["SOLO_COPIA"] = "1"
    threading.Timer(1.5, webbrowser.open, [DIRECCION]).start()
    uvicorn.run("app:app", host="127.0.0.1", port=8000, reload=True)
