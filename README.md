# Sesión 7 · Quant Data: del dato al producto

Repositorio de partida del laboratorio del 11 de noviembre de 2026. Es una web que enseña la prima de riesgo de España con datos oficiales del BCE, publicada en internet para que la use alguien que no sabe Python ni tiene tu ordenador. Máster en Finanzas Cuantitativas y Métodos Computacionales, Universidad de las Hespérides.

Mi app: (pega aquí la dirección de tu app en Vercel)

## Antes de clase: preparar

Unos 15 minutos. Hazlo antes del miércoles, no en clase.

**1. Cuenta de Vercel.** Entra en [vercel.com/signup](https://vercel.com/signup) con tu cuenta de GitHub y elige el plan Hobby: es gratis, para proyectos personales, y no pide tarjeta.

**2. Tu copia de la app.** Pulsa este botón:

[![Deploy with Vercel](https://vercel.com/button)](https://vercel.com/new/clone?repository-url=https%3A%2F%2Fgithub.com%2FSimplyJuanjo%2Fhesperides-sesion-7&project-name=prima-de-riesgo&repository-name=prima-de-riesgo&env=GROQ_API_KEY&envDescription=La%20clave%20de%20Groq%20de%20las%20sesiones%205%20y%206%2C%20para%20el%20p%C3%A1rrafo%20que%20escribe%20el%20LLM.&envLink=https%3A%2F%2Fconsole.groq.com%2Fkeys)

Vercel copia este repositorio en tu GitHub con el nombre `prima-de-riesgo`, te pide la clave de Groq (la de las sesiones 5 y 6) y publica tu app. Al terminar te da su dirección: ábrela. Dice «Esta página está a medio construir», y es lo que tiene que decir: en clase la terminas.

**3. Tu copia en tu ordenador.** Clona la tuya, no la de Juanjo. Cambia `TU_USUARIO` por tu usuario de GitHub:

```text
git clone https://github.com/TU_USUARIO/prima-de-riesgo.git
cd prima-de-riesgo
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.ejemplo .env
```

En Mac o Linux, `source .venv/bin/activate` y `cp .env.ejemplo .env`. Pon tu clave de Groq en `.env`; si tienes el `.env` de la sesión 6, cópialo aquí. Después:

```text
python preparar.py
```

Para llegar a clase hace falta «bien» en la instalación y en tu copia en GitHub. Sin clave de Groq la app funciona igual, pero sin el párrafo que escribe el LLM.

## En clase

```text
pytest
```

Casi todo en rojo: es el punto de partida. Abre tu agente dentro de esta carpeta. Cinco peldaños, uno cada vez, cada uno con su test:

1. Leer, `leer_serie` en `prima.py`: `pytest tests/test_1_leer.py`
2. Calcular, `prima_de_riesgo` y `resumen`: `pytest tests/test_2_prima.py`
3. Raspar, `decisiones_bce`: `pytest tests/test_3_raspar.py`. Antes, abre `datos/tipos.html` en el navegador y mira la tabla.
4. Enseñar, `cifras` en `panel.py`: `pytest tests/test_4_panel.py`. Después, `python servir.py` y mira tu app en tu ordenador.
5. Publicar: `git add .`, `git commit -m "Peldaños 1 a 4"` y `git push`. En un minuto Vercel la vuelve a publicar. Pega su dirección en la línea «Mi app:» de arriba, haz otro push y `pytest tests/test_5_publicar.py`, que abre tu app en internet.

Con todo en verde, hazla tuya:

- Cambia la página: los textos, los colores, otra gráfica. Está en `web/`.
- Añade la prima de Italia, Francia o Portugal: en `fuentes.py`, la misma clave del bono español cambiando `ES` por `IT`, `FR` o `PT`.
- Cambia el lector del párrafo del LLM en `explicar.py`.
- Añade otra serie del [portal de datos del BCE](https://data.ecb.europa.eu).

## Qué hay

- `prima.py`: los peldaños 1, 2 y 3, y un raspado ya escrito de ejemplo, la próxima reunión del BCE.
- `panel.py`: el peldaño 4 y lo que junta todo para la página.
- `app.py`: la app con FastAPI. `/api/panel` da los datos y `/api/explicacion`, el párrafo del LLM.
- `web/`: la página. Solo pinta lo que le llega de `/api/panel`.
- `fuentes.py`: las descargas del BCE. `python fuentes.py --guardar` renueva la copia de `datos/`.
- `explicar.py` y `modelos.py`: el párrafo del LLM y la comprobación de sus números, ya escritos.
- `servir.py`: la app en tu ordenador. `--copia` usa solo la copia de `datos/`.
- `preparar.py`: la comprobación de antes de clase.
- `AGENTS.md`: las reglas para tu agente.

## Los datos

- [Portal de datos del BCE](https://data.ecb.europa.eu): rendimiento de los bonos de España y Alemania a 10 años (media mensual), tipo de la facilidad de depósito y curva de tipos de la deuda AAA de la zona euro.
- Dos páginas de la web del BCE, raspadas: la [tabla de tipos de interés oficiales](https://www.ecb.europa.eu/stats/policy_and_exchange_rates/key_ecb_interest_rates/html/index.en.html) y el [calendario de reuniones](https://www.ecb.europa.eu/press/calendars/mgcgc/html/index.en.html).

El BCE permite reutilizar sus estadísticas citando la fuente y pide que se diga cuándo una cifra es un cálculo propio: lo son la prima, sus cambios y su máximo. Si el BCE no contesta, la app usa la copia de `datos/` y lo dice en la página.

## Reglas

- Las claves van en `.env`, que no se sube a git, y en las variables de entorno del proyecto en Vercel. Nunca en el código.
- El plan Hobby de Vercel es para uso personal y no comercial.
- La app es un ejercicio de clase, no una recomendación de inversión.
