"use strict";

// La página solo pinta lo que calcula Python: las cuentas están en prima.py y panel.py, no aquí.

const MESES = ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto", "septiembre",
  "octubre", "noviembre", "diciembre"];
const SVG = "http://www.w3.org/2000/svg";
const estado = { datos: null, desde: "todo", animar: true, indice: null };

const el = (id) => document.getElementById(id);

function numero(valor, decimales = 1) {
  return new Intl.NumberFormat("es-ES", { minimumFractionDigits: decimales, maximumFractionDigits: decimales })
    .format(valor).replace("-", "\u2212");
}

function conSigno(valor, decimales = 1) {
  const texto = numero(Math.abs(valor), decimales);
  return valor > 0 ? "+" + texto : valor < 0 ? "\u2212" + texto : texto;
}

function fecha(iso) {
  const [año, mes, dia] = iso.split("-").map(Number);
  const texto = `${MESES[mes - 1]} de ${año}`;
  return dia ? `${dia} de ${texto}` : texto;
}

const mayuscula = (texto) => texto.charAt(0).toUpperCase() + texto.slice(1);
const enMeses = (iso) => Number(iso.slice(0, 4)) * 12 + Number(iso.slice(5, 7)) - 1 + (Number(iso.slice(8, 10)) || 1) / 31;

function svg(nombre, atributos = {}, padre = null, contenido = null) {
  const nodo = document.createElementNS(SVG, nombre);
  for (const [clave, valor] of Object.entries(atributos)) nodo.setAttribute(clave, valor);
  if (contenido !== null) nodo.textContent = contenido;
  if (padre) padre.appendChild(nodo);
  return nodo;
}

function lienzo(caja, alto) {
  caja.replaceChildren();
  const ancho = caja.clientWidth;
  const dibujo = svg("svg", { viewBox: `0 0 ${ancho} ${alto}`, width: ancho, height: alto, role: "img" }, caja);
  return { dibujo, ancho, alto };
}

// Una escala con 3 a 6 marcas redondas entre el mínimo y el máximo.
function escala(minimo, maximo) {
  const paso = [0.1, 0.25, 0.5, 1, 2, 5, 10, 20, 25, 50, 100, 200, 250, 500]
    .find((p) => (maximo - minimo) / p <= 5) || 1000;
  const desde = Math.floor(minimo / paso) * paso;
  const hasta = Math.ceil(maximo / paso) * paso;
  const marcas = [];
  for (let v = desde; v <= hasta + paso / 2; v += paso) marcas.push(Math.round(v * 100) / 100);
  return { desde, hasta, marcas };
}

function dibujarLinea(dibujo, puntos, clase) {
  const d = puntos.map(([x, y], i) => `${i ? "L" : "M"}${x.toFixed(1)},${y.toFixed(1)}`).join("");
  const linea = svg("path", { d, class: clase }, dibujo);
  if (estado.animar) {
    linea.style.setProperty("--largo", Math.ceil(linea.getTotalLength()));
    linea.classList.add("dibujar");
  }
  return linea;
}

// ---------- La prima, mes a mes ----------

function serieVisible() {
  const serie = estado.datos.prima;
  if (estado.desde === "todo") return serie;
  const ultima = serie[serie.length - 1][0];
  const desde = `${Number(ultima.slice(0, 4)) - 5}${ultima.slice(4)}`;
  return serie.filter(([f]) => f > desde);
}

function graficaPrima() {
  const caja = el("lienzo-prima");
  const { dibujo, ancho, alto } = lienzo(caja, caja.clientHeight);
  const serie = serieVisible();
  const m = { arriba: 34, derecha: 58, abajo: 46, izquierda: 46 };
  const valores = serie.map(([, v]) => v);
  const ey = escala(Math.min(0, ...valores), Math.max(...valores));
  const t0 = enMeses(serie[0][0]);
  const t1 = enMeses(serie[serie.length - 1][0]);
  const x = (iso) => m.izquierda + (enMeses(iso) - t0) / (t1 - t0) * (ancho - m.izquierda - m.derecha);
  const y = (v) => alto - m.abajo - (v - ey.desde) / (ey.hasta - ey.desde) * (alto - m.arriba - m.abajo);
  const base = y(ey.desde);

  const eje = svg("g", { class: "eje" }, dibujo);
  for (const v of ey.marcas) {
    svg("line", { x1: m.izquierda, x2: ancho - m.derecha, y1: y(v), y2: y(v), class: v === 0 ? "cero" : "" }, eje);
    svg("text", { x: m.izquierda - 10, y: y(v) + 4, "text-anchor": "end" }, eje, numero(v, 0));
  }
  svg("text", { x: m.izquierda, y: m.arriba - 16 }, eje, "puntos básicos");
  const años = (t1 - t0) / 12;
  const cada = años > 20 ? 5 : años > 8 ? 2 : 1;
  for (let año = Math.ceil(serie[0][0].slice(0, 4) / cada) * cada; año <= Number(serie.at(-1)[0].slice(0, 4)); año += cada) {
    const xa = x(`${año}-01`);
    if (xa < m.izquierda) continue;
    svg("text", { x: xa, y: base + 34, "text-anchor": "middle" }, eje, año);
  }

  // Las decisiones del BCE: marcas hacia arriba (subidas) o hacia abajo (bajadas) sobre la base.
  const decisiones = estado.datos.decisiones;
  decisiones.forEach((d, i) => {
    if (!i || d.fecha.slice(0, 7) < serie[0][0] || d.deposito === decisiones[i - 1].deposito) return;
    const sube = d.deposito > decisiones[i - 1].deposito;
    svg("line", { x1: x(d.fecha), x2: x(d.fecha), y1: base + (sube ? -1 : 1), y2: base + (sube ? -9 : 9), class: "decision" }, dibujo);
  });

  dibujarLinea(dibujo, serie.map(([f, v]) => [x(f), y(v)]), "linea-prima");

  const [fm, vm] = serie.reduce((a, b) => (b[1] > a[1] ? b : a));
  const [fu, vu] = serie.at(-1);
  if (fm !== fu) {
    svg("circle", { cx: x(fm), cy: y(vm), r: 3.5, class: "punto-prima" }, dibujo);
    const derecha = x(fm) < ancho * 0.66;
    svg("text", { x: x(fm) + (derecha ? 12 : -12), y: y(vm) + 5, "text-anchor": derecha ? "start" : "end", class: "anotacion" },
      dibujo, `${mayuscula(fecha(fm))}: ${numero(vm, 0)} puntos`);
  }
  svg("circle", { cx: x(fu), cy: y(vu), r: 4.5, class: "punto-prima" }, dibujo);
  svg("text", { x: x(fu) + 10, y: y(vu) + 5, class: "lectura-valor", fill: "var(--prima)" }, dibujo, numero(vu, 0));

  dibujo.setAttribute("aria-label", `Prima de riesgo de España de ${fecha(serie[0][0])} a ${fecha(fu)}. ` +
    `Máximo: ${numero(vm, 1)} puntos en ${fecha(fm)}. Último dato: ${numero(vu, 1)} puntos.`);
  lectura(dibujo, serie, x, y, m, alto);
}

// La lectura de un mes: con el ratón, con el dedo o con las flechas del teclado.
function lectura(dibujo, serie, x, y, m, alto) {
  const capa = svg("g", { visibility: "hidden" }, dibujo);
  const guia = svg("line", { y1: m.arriba - 6, y2: alto - m.abajo, class: "guia" }, capa);
  const punto = svg("circle", { r: 4.5, class: "punto-prima" }, capa);
  const fondo = svg("rect", { class: "lectura-fondo" }, capa);
  const textoFecha = svg("text", { class: "lectura-fecha" }, capa);
  const textoValor = svg("text", { class: "lectura-valor" }, capa);
  const porMes = new Map(estado.datos.decisiones.map((d) => [d.fecha.slice(0, 7), d]));

  const ver = (i) => {
    estado.indice = Math.max(0, Math.min(serie.length - 1, i));
    const [f, v] = serie[estado.indice];
    const decision = porMes.get(f);
    capa.setAttribute("visibility", "visible");
    guia.setAttribute("x1", x(f));
    guia.setAttribute("x2", x(f));
    punto.setAttribute("cx", x(f));
    punto.setAttribute("cy", y(v));
    textoFecha.textContent = mayuscula(fecha(f)) + (decision ? `. El BCE deja el depósito en el ${numero(decision.deposito, 2)} %` : "");
    textoValor.textContent = `${numero(v, 1)} puntos`;
    const derecha = x(f) < dibujo.viewBox.baseVal.width * 0.62;
    for (const [texto, alto_] of [[textoFecha, m.arriba - 14], [textoValor, m.arriba + 4]]) {
      texto.setAttribute("x", x(f) + (derecha ? 10 : -10));
      texto.setAttribute("y", alto_);
      texto.setAttribute("text-anchor", derecha ? "start" : "end");
    }
    const caja = textoFecha.getBBox();
    const caja2 = textoValor.getBBox();
    const izquierda = Math.min(caja.x, caja2.x) - 6;
    fondo.setAttribute("x", izquierda);
    fondo.setAttribute("y", caja.y - 4);
    fondo.setAttribute("width", Math.max(caja.x + caja.width, caja2.x + caja2.width) - izquierda + 6);
    fondo.setAttribute("height", caja2.y + caja2.height - caja.y + 8);
  };
  const cercano = (evento) => {
    const punto_ = dibujo.createSVGPoint();
    punto_.x = evento.clientX;
    punto_.y = evento.clientY;
    const px = punto_.matrixTransform(dibujo.getScreenCTM().inverse()).x;
    let mejor = 0;
    serie.forEach(([f], i) => { if (Math.abs(x(f) - px) < Math.abs(x(serie[mejor][0]) - px)) mejor = i; });
    return mejor;
  };
  dibujo.addEventListener("pointermove", (e) => ver(cercano(e)));
  dibujo.addEventListener("pointerdown", (e) => ver(cercano(e)));
  dibujo.addEventListener("pointerleave", () => capa.setAttribute("visibility", "hidden"));
  const caja = el("lienzo-prima");
  caja.onkeydown = (e) => {
    const pasos = { ArrowLeft: -1, ArrowRight: 1, PageDown: -12, PageUp: 12 };
    if (e.key in pasos) ver((estado.indice ?? serie.length - 1) + pasos[e.key]);
    else if (e.key === "Home") ver(0);
    else if (e.key === "End") ver(serie.length - 1);
    else return;
    e.preventDefault();
  };
  caja.onblur = () => capa.setAttribute("visibility", "hidden");
  if (estado.indice !== null && document.activeElement === caja) ver(estado.indice);
}

function tablaPrima() {
  const cuerpo = el("tabla-prima").tBodies[0];
  cuerpo.replaceChildren(...estado.datos.prima.slice(-24).reverse().map(([f, v]) => {
    const fila = document.createElement("tr");
    fila.append(Object.assign(document.createElement("td"), { textContent: mayuscula(fecha(f)) }),
      Object.assign(document.createElement("td"), { textContent: numero(v, 1) }));
    return fila;
  }));
}

// ---------- El tipo de depósito del BCE ----------

function graficaDeposito() {
  const caja = el("lienzo-deposito");
  const { dibujo, ancho, alto } = lienzo(caja, 250);
  const decisiones = estado.datos.decisiones;
  const fin = estado.datos.calculado.slice(0, 10);
  const m = { arriba: 20, derecha: 56, abajo: 30, izquierda: 44 };
  const ey = escala(Math.min(0, ...decisiones.map((d) => d.deposito)), Math.max(...decisiones.map((d) => d.deposito)));
  const t0 = enMeses(decisiones[0].fecha);
  const t1 = enMeses(fin);
  const x = (iso) => m.izquierda + (enMeses(iso) - t0) / (t1 - t0) * (ancho - m.izquierda - m.derecha);
  const y = (v) => alto - m.abajo - (v - ey.desde) / (ey.hasta - ey.desde) * (alto - m.arriba - m.abajo);

  const eje = svg("g", { class: "eje" }, dibujo);
  for (const v of ey.marcas) {
    svg("line", { x1: m.izquierda, x2: ancho - m.derecha, y1: y(v), y2: y(v), class: v === 0 ? "cero" : "" }, eje);
    svg("text", { x: m.izquierda - 8, y: y(v) + 4, "text-anchor": "end" }, eje, numero(v, 0) + " %");
  }
  for (const año of [2000, 2010, 2020]) svg("text", { x: x(`${año}-01-01`), y: alto - 8, "text-anchor": "middle" }, eje, año);

  const puntos = [];
  decisiones.forEach((d, i) => {
    if (i) puntos.push([x(d.fecha), y(decisiones[i - 1].deposito)]);
    puntos.push([x(d.fecha), y(d.deposito)]);
  });
  puntos.push([x(fin), y(decisiones.at(-1).deposito)]);
  dibujarLinea(dibujo, puntos, "linea-tinta");
  svg("text", { x: x(fin) + 8, y: y(decisiones.at(-1).deposito) + 5, class: "lectura-valor" }, dibujo,
    `${numero(decisiones.at(-1).deposito, 2)} %`);

  const negativas = decisiones.filter((d) => d.deposito < 0);
  if (negativas.length) {
    const salida = decisiones.find((d) => d.fecha > negativas.at(-1).fecha);
    const desde = negativas[0].fecha.slice(0, 4);
    const hasta = salida ? salida.fecha.slice(0, 4) : "hoy";
    const centro = (x(negativas[0].fecha) + x(salida ? salida.fecha : fin)) / 2;
    svg("text", { x: centro, y: y(ey.desde) - 8, "text-anchor": "middle", class: "anotacion" }, dibujo,
      `Tipos negativos, ${desde}–${hasta}`);
  }
  dibujo.setAttribute("aria-label", `Tipo de la facilidad de depósito del BCE desde ${fecha(decisiones[0].fecha)}: ` +
    `${decisiones.length} decisiones. Ahora, ${numero(decisiones.at(-1).deposito, 2)} %.`);
}

// ---------- La curva de tipos ----------

function graficaCurva() {
  const caja = el("lienzo-curva");
  const { dibujo, ancho, alto } = lienzo(caja, 250);
  const { plazos } = estado.datos.curva;
  const m = { arriba: 20, derecha: 92, abajo: 30, izquierda: 40 };
  const todos = plazos.flatMap((p) => [p.hoy, p.antes]).filter((v) => v !== null);
  const ey = escala(Math.min(...todos) - 0.1, Math.max(...todos) + 0.1);
  const x = (i) => m.izquierda + i / (plazos.length - 1) * (ancho - m.izquierda - m.derecha);
  const y = (v) => alto - m.abajo - (v - ey.desde) / (ey.hasta - ey.desde) * (alto - m.arriba - m.abajo);
  const nombres = { "3M": "3 meses", "1Y": "1 año", "30Y": "30 años" };

  const eje = svg("g", { class: "eje" }, dibujo);
  for (const v of ey.marcas) {
    svg("line", { x1: m.izquierda, x2: ancho - m.derecha, y1: y(v), y2: y(v) }, eje);
    svg("text", { x: m.izquierda - 8, y: y(v) + 4, "text-anchor": "end" }, eje, numero(v, ey.marcas.some((n) => n % 1) ? 1 : 0) + " %");
  }
  plazos.forEach((p, i) => svg("text", { x: x(i), y: alto - 8, "text-anchor": "middle" }, eje,
    nombres[p.plazo] || p.plazo.replace("Y", "")));

  const antes = plazos.map((p, i) => [x(i), p.antes === null ? null : y(p.antes)]).filter(([, v]) => v !== null);
  const hoy = plazos.map((p, i) => [x(i), y(p.hoy)]);
  if (antes.length) dibujarLinea(dibujo, antes, "linea-antes");
  dibujarLinea(dibujo, hoy, "linea-tinta");
  antes.forEach(([cx, cy]) => svg("circle", { cx, cy, r: 3, class: "punto-antes" }, dibujo));
  hoy.forEach(([cx, cy]) => svg("circle", { cx, cy, r: 3.5, class: "punto-tinta" }, dibujo));

  let yHoy = hoy.at(-1)[1] + 4;
  let yAntes = antes.length ? antes.at(-1)[1] + 4 : null;
  if (yAntes !== null && Math.abs(yHoy - yAntes) < 16) {
    const medio = (yHoy + yAntes) / 2;
    [yHoy, yAntes] = yHoy <= yAntes ? [medio - 8, medio + 8] : [medio + 8, medio - 8];
  }
  svg("text", { x: hoy.at(-1)[0] + 10, y: yHoy, class: "etiqueta", fill: "var(--tinta)" }, dibujo, "Hoy");
  if (yAntes !== null) svg("text", { x: antes.at(-1)[0] + 10, y: yAntes, class: "etiqueta" }, dibujo, "Hace un año");
  dibujo.setAttribute("aria-label", `Curva de tipos AAA de la zona euro el ${fecha(estado.datos.curva.fecha)} y un año antes.`);
}

// ---------- Textos ----------

function pintarTextos(datos) {
  const c = Object.fromEntries(datos.cifras.map((cifra) => [cifra.id, cifra]));
  const { prima, bono_es: es, bono_de: de } = c;

  const titular = el("titular");
  const cifra = Object.assign(document.createElement("span"), { className: "cifra", textContent: `${numero(prima.valor, 0)} puntos` });
  titular.replaceChildren(`En ${fecha(prima.fecha)}, la prima de riesgo de España fue de `, cifra, ".");
  el("entradilla").textContent = `Es lo que paga de más España que Alemania por pedir prestado a diez años: ` +
    `un ${numero(es.valor, 2)} % frente a un ${numero(de.valor, 2)} %, de media en el mes. ` +
    `Se mide en puntos básicos: cada uno es una centésima de punto porcentual.`;
  const partes = [];
  if (c.cambio_año) partes.push(`${c.cambio_año.valor < 0 ? "Ha bajado" : "Ha subido"} ${numero(Math.abs(c.cambio_año.valor), 1)} puntos en un año.`);
  if (c.maximo) partes.push(`El máximo de la serie fue de ${numero(c.maximo.valor, 0)} puntos, en ${fecha(c.maximo.fecha)}.`);
  el("contexto").textContent = partes.join(" ");

  const copias = datos.fuentes.filter((f) => f.origen === "copia");
  el("actualizado").textContent = `Datos del BCE, consultados el ${fecha(datos.calculado.slice(0, 10))}` +
    (copias.length ? `. ${copias.length === datos.fuentes.length ? "Todos salen" : "Alguno sale"} de la copia del ${fecha(datos.guardada.slice(0, 10))}` : "");

  el("cifras").replaceChildren(...datos.cifras.map((cifra_) => {
    const fila = document.createElement("div");
    const nombre = Object.assign(document.createElement("dt"), { textContent: cifra_.nombre });
    const valor = Object.assign(document.createElement("dd"), { className: "valor" });
    const puntos = cifra_.unidad === "puntos básicos";
    valor.append(cifra_.id.startsWith("cambio") ? conSigno(cifra_.valor, 1) : numero(cifra_.valor, puntos ? 1 : 2),
      Object.assign(document.createElement("small"), { textContent: puntos ? "puntos" : "%" }));
    const origen = Object.assign(document.createElement("dd"), { className: "origen" });
    origen.append(`${mayuscula(fecha(cifra_.fecha))}. `,
      Object.assign(document.createElement("a"), { href: cifra_.url, textContent: cifra_.fuente, rel: "noopener" }));
    fila.append(nombre, valor, origen);
    return fila;
  }));

  const d = datos.decisiones;
  const [anterior, ultima] = [d.at(-2), d.at(-1)];
  el("bce-titular").textContent = `El BCE tiene el tipo de depósito en el ${numero(ultima.deposito, 2)} %.`;
  const verbo = ultima.deposito > anterior.deposito ? "Lo subió" : ultima.deposito < anterior.deposito ? "Lo bajó" : "Lo dejó igual";
  el("bce-texto").textContent = `${verbo} el ${fecha(ultima.fecha)}, desde el ${numero(anterior.deposito, 2)} %. ` +
    `Es lo que cobran los bancos por dejarle su dinero, y de ahí parten casi todos los tipos de la zona euro.` +
    (datos.proxima_reunion ? ` La próxima decisión es el ${fecha(datos.proxima_reunion.fecha)}.` : "");
  const comprobacion = datos.comprobacion;
  el("bce-comprobacion").textContent = comprobacion.coincide
    ? `Las ${comprobacion.decisiones} decisiones salen de la tabla de la web del BCE y coinciden, una a una, con la serie oficial de su API.`
    : `Ojo: lo sacado de la web del BCE no coincide con su serie oficial en ${comprobacion.distintas.length} o más fechas.`;

  const curva = datos.curva;
  const pendiente = curva.pendiente;
  el("curva-titular").textContent = pendiente >= 0
    ? `Pedir prestado a diez años cuesta ${numero(pendiente, 0)} puntos más que a dos.`
    : `Pedir prestado a diez años cuesta ${numero(-pendiente, 0)} puntos menos que a dos: la curva está invertida.`;
  el("curva-texto").textContent = `Tipos de la deuda de los países AAA de la zona euro según el plazo, ` +
    `el ${fecha(curva.fecha)} y el ${fecha(curva.fecha_antes)}. Cuanto más largo el préstamo, más se suele pagar.`;

  el("fuentes").replaceChildren(...datos.fuentes.map((f) => {
    const item = document.createElement("li");
    item.append(Object.assign(document.createElement("a"), { href: f.web, textContent: f.nombre, rel: "noopener" }),
      f.origen === "copia" ? `, de la copia del ${fecha(datos.guardada.slice(0, 10))}` : "");
    return item;
  }));
  el("avisos").textContent = datos.avisos.join(" ");
}

function pintarGraficas() {
  graficaPrima();
  graficaDeposito();
  graficaCurva();
}

async function explicacion() {
  const parrafo = el("explicacion");
  const nota = el("explicacion-nota");
  el("bloque-explicacion").hidden = false;
  try {
    const respuesta = await (await fetch("/api/explicacion")).json();
    if (respuesta.texto) {
      parrafo.textContent = respuesta.texto;
      nota.textContent = `Lo ha escrito un modelo de lenguaje, ${respuesta.modelo}, con las cifras de esta página. ` +
        `Antes de enseñarlo, Python ha comprobado que cada número del párrafo está en ellas.`;
      return;
    }
    nota.textContent = respuesta.motivo || "";
  } catch {
    nota.textContent = "";
  }
  parrafo.classList.add("vacio");
  parrafo.textContent = "Hoy no hay explicación. Las cifras de arriba no dependen de ella.";
}

function enObras(pendiente) {
  document.body.classList.add("obras");
  el("titular").textContent = "Esta página está a medio construir.";
  const codigo = Object.assign(document.createElement("code"), { textContent: pendiente.replace(/^Peldaño \d+: /, "") });
  const peldaño = (pendiente.match(/^Peldaño \d+/) || ["Un peldaño"])[0].toLowerCase();
  el("entradilla").replaceChildren(`Falta el ${peldaño}: `, codigo, ".");
  el("contexto").textContent = "Cuando esté hecho y hagas git push, Vercel la vuelve a publicar sola, ya con los datos del BCE.";
}

async function cargar() {
  let datos;
  try {
    datos = await (await fetch("/api/panel")).json();
  } catch {
    el("titular").textContent = "No se han podido cargar los datos.";
    el("entradilla").textContent = "Vuelve a intentarlo dentro de un rato.";
    return;
  }
  if (datos.pendiente) return enObras(datos.pendiente);
  estado.datos = datos;
  for (const id of ["bloque-prima", "bloque-cifras", "bloque-bce", "bloque-curva", "pie"]) el(id).hidden = false;
  pintarTextos(datos);
  tablaPrima();
  pintarGraficas();
  estado.animar = false;

  for (const boton of document.querySelectorAll(".rango button")) {
    boton.addEventListener("click", () => {
      estado.desde = boton.dataset.desde;
      estado.indice = null;
      for (const otro of document.querySelectorAll(".rango button")) otro.setAttribute("aria-pressed", otro === boton);
      estado.animar = true;
      graficaPrima();
      estado.animar = false;
    });
  }
  let ancho = el("contenido").clientWidth;
  new ResizeObserver(() => {
    if (el("contenido").clientWidth === ancho) return;
    ancho = el("contenido").clientWidth;
    requestAnimationFrame(pintarGraficas);
  }).observe(el("contenido"));
  explicacion();
}

cargar();
