# AGENTS.md

## Qué es esto

Una web que enseña la prima de riesgo de España con datos oficiales del BCE, publicada en Vercel para que la use alguien que no sabe Python. FastAPI (`app.py`) sirve los datos en `/api/panel` y la página de `web/` los pinta. Es para aprender: quien la usa tiene que entender cada línea.

## Reglas

- Usa FastAPI y la biblioteca estándar de Python. Si hace falta otro paquete, pregunta antes y añádelo a `requirements.txt` con su versión: Vercel instala lo que diga ese archivo y nada más.
- Deja como están `tests/`, `datos/` y las funciones que ya vienen escritas, salvo que te pidan cambiarlas.
- Las cuentas las hace Python en `prima.py` y `panel.py`. La página solo pinta lo que le llega de `/api/panel`. El LLM solo redacta, desde `explicar.py`, y Python comprueba sus números.
- Cada cifra que sale en la página lleva su unidad, su fecha y su fuente.
- Las claves viven en `.env` en el ordenador y en las variables de entorno del proyecto en Vercel. No las escribas en el código ni las muestres por pantalla.

## Cómo trabajar

- Un peldaño cada vez: implementa solo la función que te pidan y ejecuta su test, por ejemplo `pytest tests/test_1_leer.py`.
- Antes de escribir código, di en dos frases qué vas a hacer y espera.
- Para raspar una página, mira primero su HTML en `datos/`. No supongas cómo es.
- Después, explica cada línea en una frase, para alguien que no ha hecho nunca una web.
- Para publicar: `git add`, `git commit` y `git push`. Vercel vuelve a publicar la app sola con cada push.
