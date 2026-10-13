# -*- coding: utf-8 -*-
"""Tablero HTML de los escenarios de Articulo 6: un solo archivo que funciona sin internet.

Reune las graficas dinamicas de graficar.py con su texto de lectura y, para cada una, la tabla de
datos que la sostiene (alternativa accesible). Abre con las secciones de los Productos 1 a 4 (demanda,
cartera agregada, remociones, puentes y cartera viable), que arma productos.py desde
Art6_motor/datos_productos, y sigue con el modelo. Incluye plotly.js y la tipografia Fira Sans
(licencia SIL OFL, en Art6_motor/fuentes) dentro del archivo.

Salida: docs/_static/tablero_art6.html. Para rehacer solo el tablero, sin correr el modelo ni el
analisis: python tablero.py (regenerar()).
"""
import base64
import html
import io
import re
from pathlib import Path

from plotly.offline import get_plotlyjs

import plotly.graph_objects as go

import comun as C
import graficar as G
import productos as P

FUENTES = Path(__file__).resolve().parent / "fuentes"

# secciones de los Productos 1 a 4 primero (productos.SECCIONES), luego las del modelo
SECCIONES = P.SECCIONES + [
    ("El modelo de la Segunda NDC", ["g18_referencias"]),
    ("El sector energía en la NDC y en el inventario", ["g11_peso_energia", "g03_energia_escenarios"]),
    ("Los escenarios del análisis", []),
    ("Resultados principales", ["g00_indicadores", "g20_escalera", "g19_comparacion", "g04_reduccion_anual", "g02_potencial",
                                "g14_headroom_riesgos", "g13_sobreventa_area", "g07_generacion", "g17_ingresos"]),
    ("Lectura para la decisión", []),
    ("Anexo de gráficas", ["g01_itmos_area", "g05_emisiones_generacion", "g06_subsectores", "g08_capacidad",
                           "g09_ernc", "g12_cascada_headroom", "g15_headroom_trayectoria",
                           "g16_volumenes"]),
]


def _bloques(sec):
    """Bloques HTML (fichas de lectura, mapa, fichas y supuestos) que abren cada seccion: [(ancla, titulo, html)]."""
    import explicacion
    import lectura
    if sec == "El modelo de la Segunda NDC":
        return [("b-ndc", "Tendencial y metas", lectura.ndc_html())]
    if sec == "El sector energía en la NDC y en el inventario":
        return [("b-sector", "Inventario, modelo e iniciativas", lectura.sector_html())]
    if sec == "Los escenarios del análisis":
        return [("b-glosario", "Términos del ejercicio", lectura.glosario_html()),
                ("b-escenarios", "Qué muestra cada escenario", lectura.escenarios_html()),
                ("s-mapa", "Mapa de escenarios", explicacion.mapa_html(fuentes=False)),
                ("s-fichas", "Ficha de cada escenario", explicacion.fichas_html(fuentes=False)),
                ("s-supuestos", "Parámetros de entrada", explicacion.supuestos_html(fuentes=False)),
                ("b-hidro", "Clases hidroeléctricas del modelo", lectura.hidro_html())]
    if sec == "Lectura para la decisión":
        return [("b-decision", "Dos hallazgos y lo pendiente", lectura.decision_html()),
                ("b-riesgo", "Sobreventa, respaldo, oferta y factor desplazado", lectura.riesgo_html())]
    return P.bloques(sec)[0]


def _articulo(gid, cabeza, sub, lectura, fig, tabla, fuente=""):
    """Tarjeta de una grafica: titulo, subtitulo, guia de lectura, grafica, tabla de datos y fuente."""
    return ("<article class='figura' id='%s' aria-labelledby='t-%s'><h3 id='t-%s'>%s</h3>"
            "<p class='sub'>%s</p><div class='lectura'>%s</div><div class='grafica'>%s</div>%s%s</article>"
            % (gid, gid, gid, cabeza, sub, lectura,
               fig.to_html(full_html=False, include_plotlyjs=False, config=G.CONFIG, default_width="100%"),
               tabla, "<p class='fuente'>%s</p>" % html.escape(fuente) if fuente else ""))


def _num(v):
    try:
        return G.miles(float(v)) if abs(float(v)) >= 10 else ("%.1f" % float(v)).replace(".", ",")
    except (TypeError, ValueError):
        return html.escape(str(v))


def _tabla(fig):
    """Tabla de las series visibles por defecto: filas = categoria o ano, columnas = series."""
    series = []
    for tr in fig.data:
        if tr.type not in ("scatter", "bar", "waterfall") or tr.visible is False:
            continue
        if tr.type == "scatter" and (tr.line is None or not tr.line.width or tr.showlegend is False):
            continue
        horizontal = tr.type == "bar" and tr.orientation == "h"
        cats = [re.sub(r"<br>", " ", str(c)) for c in (tr.y if horizontal else tr.x)]
        vals = list(tr.x if horizontal else tr.y)
        series.append((tr.name or "Valor", dict(zip(cats, vals)), cats))
    if not series:
        return ""
    orden = []
    for _, _, cats in series:
        for c in cats:
            if c not in orden:
                orden.append(c)
    cab = "".join("<th scope='col'>%s</th>" % html.escape(n) for n, _, _ in series)
    filas = "".join("<tr><th scope='row'>%s</th>%s</tr>" % (
        html.escape(c), "".join("<td>%s</td>" % (_num(d[c]) if c in d and d[c] is not None else "") for _, d, _ in series))
        for c in orden)
    return ("<details class='datos'><summary>Ver datos de la gráfica</summary><div class='tabla'>"
            "<table><thead><tr><th scope='col'></th>%s</tr></thead><tbody>%s</tbody></table></div></details>"
            % (cab, filas))


def _separar_titulo(fig):
    """Saca el titular y el subtitulo de la grafica para usarlos como encabezado HTML."""
    txt = fig.layout.title.text or ""
    m = re.match(r"<b>(.*?)</b>(?:<br><span[^>]*>(.*)</span>)?", txt, flags=re.S)
    cabeza, sub = (m.group(1), m.group(2) or "") if m else (txt, "")
    g = go.Figure(fig)
    menus = bool(g.layout.updatemenus) or bool(g.layout.sliders)
    g.update_layout(title=None, margin=dict(t=70 if menus else 24))
    return cabeza, sub, g


def _fuentes_css():
    reglas = []
    for peso in (400, 500, 600, 700):
        f = FUENTES / ("FiraSans-%d.woff2" % peso)
        if f.exists():
            reglas.append("@font-face{font-family:'Fira Sans';font-style:normal;font-weight:%d;font-display:swap;"
                          "src:url(data:font/woff2;base64,%s) format('woff2')}"
                          % (peso, base64.b64encode(f.read_bytes()).decode()))
    return "".join(reglas)


CSS = """
:root{--tinta:#1F2937;--tinta-2:#4B5563;--tinta-3:#6B7280;--papel:#FFFFFF;--fondo:#F5F7F6;--linea:#DFE5E3;
--acento:#0E7C6B;--acento-fuerte:#0A5E51;--acento-tinte:#DCEEE9;--alerta:#B42318;
--letra:'Fira Sans','Segoe UI',Arial,sans-serif;color-scheme:light}
*{box-sizing:border-box}
html{-webkit-text-size-adjust:100%}
@media (prefers-reduced-motion:no-preference){html{scroll-behavior:smooth}}
body{margin:0;background:var(--fondo);color:var(--tinta);font-family:var(--letra);font-size:1rem;line-height:1.5;
font-variant-numeric:tabular-nums}
::selection{background:var(--acento-tinte);color:var(--tinta)}
:focus-visible{outline:3px solid var(--acento);outline-offset:2px;border-radius:2px}
a{color:var(--acento-fuerte);text-underline-offset:3px}
a:hover{color:var(--acento)}
html{scrollbar-color:#B8C4C0 var(--fondo)}
.saltar{position:absolute;left:-999px;top:0;background:var(--papel);padding:.5rem 1rem;z-index:10}
.saltar:focus{left:1rem;top:1rem}
.cabecera{background:var(--papel);border-bottom:1px solid var(--linea);padding:2rem 1.5rem 1.75rem}
.cabecera .ancho{max-width:1360px;margin:0 auto}
h1{font-size:1.75rem;line-height:1.2;font-weight:700;margin:0 0 .5rem;letter-spacing:-.01em;text-wrap:balance;
color:var(--acento-fuerte)}
.meta{margin:0 0 1rem;color:var(--tinta-2);font-size:.9375rem}
.pregunta{margin:0;max-width:72ch;font-size:1.0625rem}
.marco{max-width:1360px;margin:0 auto;padding:1.5rem;display:grid;grid-template-columns:15rem minmax(0,1fr);gap:2rem}
.indice{position:sticky;top:1.5rem;align-self:start;font-size:.9375rem;max-height:calc(100vh - 3rem);overflow-y:auto;overscroll-behavior:contain}
.indice summary{font-size:.875rem;font-weight:600;color:var(--tinta-2);margin:0 0 .5rem;cursor:pointer;
min-height:2.75rem;display:flex;align-items:center;list-style:none}
.indice summary::-webkit-details-marker{display:none}
@media (min-width:961px){.indice summary{pointer-events:none;min-height:auto}}
.indice ol{list-style:none;margin:0;padding:0}
.indice li{margin:0}
.indice .grupo{font-weight:600;color:var(--tinta);margin:.875rem 0 .25rem}
.indice a{display:block;padding:.3rem .625rem;border-radius:4px;color:var(--tinta-2);text-decoration:none;
min-height:2rem;transition:background-color .15s ease,color .15s ease}
.indice a:hover{background:var(--acento-tinte);color:var(--tinta)}
.indice a[aria-current="true"]{background:var(--acento);color:#fff}
main{min-width:0}
.seccion{margin:0 0 2.5rem}
.seccion>h2{font-size:1.375rem;line-height:1.25;margin:0 0 1rem;padding-bottom:.5rem;border-bottom:2px solid var(--acento);
text-wrap:balance}
.figura{background:var(--papel);border:1px solid var(--linea);border-radius:6px;padding:1.25rem 1.25rem 1rem;
margin:0 0 1.25rem;box-shadow:0 1px 2px rgba(15,40,35,.05)}
.figura{min-width:0;overflow:hidden}
.figura h3{font-size:1.1875rem;line-height:1.3;margin:0 0 .25rem;text-wrap:balance;max-width:80ch}
.sub{margin:0 0 .75rem;color:var(--tinta-3);font-size:.875rem;max-width:90ch}
.lectura{max-width:75ch;color:var(--tinta-2);font-size:.9688rem}
.lectura p{margin:0 0 .625rem}
.lectura strong{color:var(--tinta);font-weight:600}
.grafica{margin:.5rem 0 .25rem;min-height:12rem;width:100%;overflow:hidden}
.grafica .plotly-graph-div{max-width:100%}
.datos{margin-top:.5rem;border-top:1px solid var(--linea);padding-top:.5rem}
.datos summary{cursor:pointer;color:var(--acento-fuerte);font-weight:500;font-size:.9375rem;padding:.375rem 0;
min-height:2.75rem;display:flex;align-items:center}
.datos summary:hover{color:var(--acento)}
.tabla{overflow-x:auto;margin-top:.5rem}
table{border-collapse:collapse;font-size:.875rem;min-width:100%}
th,td{padding:.375rem .625rem;border-bottom:1px solid var(--linea);text-align:right;white-space:nowrap}
thead th{font-weight:600;color:var(--tinta);border-bottom:2px solid var(--tinta-3);vertical-align:bottom;white-space:normal}
tbody th{text-align:left;font-weight:500;white-space:normal}
tbody tr:hover{background:var(--fondo)}
.pie{max-width:1360px;margin:0 auto;padding:1rem 1.5rem 2.5rem;color:var(--tinta-2);font-size:.875rem}
.pie p{max-width:90ch;margin:.25rem 0}
@media (max-width:960px){
.marco{grid-template-columns:1fr;padding:1rem}
.indice{position:static;max-height:none;overflow:visible;background:var(--papel);border:1px solid var(--linea);border-radius:6px;padding:.75rem 1rem}
.indice ol{columns:2;column-gap:1.5rem}
.cabecera{padding:1.5rem 1rem}
h1{font-size:1.5rem}
.figura{padding:1rem .75rem}
}
@media (max-width:560px){.indice ol{columns:1}}
.ab-h3{font-size:1.1875rem;margin:1.75rem 0 .5rem}
.figura .gl{border:0;padding:0;margin:.25rem 0 .75rem;background:transparent;max-width:none}
@media print{.indice,.datos summary{display:none}.marco{display:block}.figura{break-inside:avoid;box-shadow:none}}
"""

JS = """
(function(){
  var ind = document.getElementById('indice');
  if (ind && window.matchMedia('(max-width:960px)').matches) ind.removeAttribute('open');
  var enlaces = Array.prototype.slice.call(document.querySelectorAll('.indice a[href^="#"]'));
  if (!('IntersectionObserver' in window)) return;
  var porId = {};
  enlaces.forEach(function(a){ porId[a.getAttribute('href').slice(1)] = a; });
  var obs = new IntersectionObserver(function(entradas){
    entradas.forEach(function(e){
      if (e.isIntersecting && porId[e.target.id]) {
        enlaces.forEach(function(a){ a.removeAttribute('aria-current'); });
        porId[e.target.id].setAttribute('aria-current', 'true');
      }
    });
  }, {rootMargin: '-35% 0px -60% 0px'});
  Object.keys(porId).forEach(function(id){ var el = document.getElementById(id); if (el) obs.observe(el); });
})();
"""


def exportar(F, L, destino=None):
    import guias
    PF = P.figuras()                     # graficas de los Productos 1 a 4; vacio sin Art6_motor/datos_productos
    titulos = {g: t for g, t, _ in G.FIGURAS}
    titulos.update({g: x["indice"] for g, x in PF.items()})
    indice, cuerpo = [], []
    for sec, gids in SECCIONES:
        sid = "s-" + re.sub(r"[^a-z0-9]+", "-", sec.lower().encode("ascii", "ignore").decode()).strip("-")
        entradas, figs = [], []
        for ancla, titulo_b, cuerpo_b in _bloques(sec):
            if not cuerpo_b:
                continue
            entradas.append("<li><a href='#%s'>%s</a></li>" % (ancla, html.escape(titulo_b)))
            figs.append("<div id='%s'><h3 class='ab-h3'>%s</h3>%s</div>" % (ancla, html.escape(titulo_b), cuerpo_b))
        for g in gids:
            if g in PF:
                x = PF[g]
                cabeza, sub, fig = _separar_titulo(x["fig"])
                sub = sub.replace("<br>", " ")      # en HTML el subtitulo se ajusta solo al ancho
                figs.append(_articulo(g, cabeza, sub, guias.html(x["guia"], estilo=False), fig, x["tabla"],
                                      x["fuente"]))
            elif g in F:
                cabeza, sub, fig = _separar_titulo(F[g])
                figs.append(_articulo(g, cabeza, sub, guias.html(L[g], estilo=False) if g in L else "", fig,
                                      "" if g == "g00_indicadores" else _tabla(F[g])))
            else:
                continue
            entradas.append("<li><a href='#%s'>%s</a></li>" % (g, html.escape(titulos[g])))
        for ancla, titulo_b, cuerpo_b in P.bloques(sec)[1]:      # bloques que cierran la seccion (registros)
            entradas.append("<li><a href='#%s'>%s</a></li>" % (ancla, html.escape(titulo_b)))
            figs.append(cuerpo_b)
        if not figs and sec in dict(P.SECCIONES):
            continue                     # sin datos de los Productos 1 a 4 la seccion no se publica
        indice.append("<li class='grupo'>%s</li>" % html.escape(sec))
        indice += entradas
        if sec == "Anexo de gráficas" and figs:
            figs = ["<details class='datos anexo'><summary>Ver las %d gráficas del anexo</summary>%s</details>"
                    % (len(figs), "".join(figs))]
        cuerpo.append("<section class='seccion' id='%s' aria-labelledby='h-%s'><h2 id='h-%s'>%s</h2>%s</section>"
                      % (sid, sid, sid, html.escape(sec), "".join(figs)))
    import analizar
    import explicacion
    R = analizar.resultados()
    riesgos = [d for d in R.get("roles", {}).get("estados", []) if d["grupo"] == "Riesgo" and len(d["componentes"]) < 2]
    pregunta = ("¿Cuántas reducciones del sector energía podría transferir el Ecuador como ITMO en %d-%d sin poner en "
                "riesgo su meta incondicional%s?" % (C.VENTANA[0], C.VENTANA[-1], (
                    ", y qué pasa con ese potencial %s" % C.enumerar(["con %s" % (d.get("frase") or G._minus(d["nombre"]))
                                                                      for d in riesgos])) if riesgos else ""))
    doc = """<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Potencial de Artículo 6 · Ecuador</title>
<meta name="description" content="Artículo 6 en el sector energía del Ecuador: demanda de mitigación, cartera de la Segunda NDC, remociones, potencial de ITMO, margen frente a la meta incondicional y riesgo de sobreventa.">
<style>%s%s%s%s</style>
<script>%s</script>
</head>
<body>
<a class="saltar" href="#contenido">Saltar al contenido</a>
<header class="cabecera"><div class="ancho">
<h1>Potencial de Artículo 6 del sector energía del Ecuador</h1>
<p class="meta">PNUD Ecuador, Proyecto 00110180 (Climate Promise) · Dr. Ing. Mario Alejandro Heredia Salgado · Modelo Climate Lead Group de la Segunda NDC (OSeMOSYS) con las referencias corregidas del Artículo 6</p>
<p class="pregunta">%s</p>
</div></header>
<div class="marco">
<nav class="indice" aria-label="Contenido del tablero"><details id="indice" open><summary>Contenido</summary><ol>%s</ol></details></nav>
<main id="contenido">%s</main>
</div>
<footer class="pie">
<p>Fuente de %s: Modelo Climate Lead Group (ECU_NDC, rama art6-escenarios), con los escenarios NDCINC y NDCCON del Modelo CLG, las referencias corregidas INCA6 y CONA6 (correcciones K01-K15) y los escenarios de Artículo 6 definidos en Energy/B1_Scenario_Config.xlsx; resultados de la salida de B1 de cada escenario (Energy/Executables/&lt;ESC&gt;_0/&lt;ESC&gt;_0_Output.csv). Las gráficas son interactivas: el cursor muestra valores, los botones y menús cambian de escenario, riesgo o regla, y el ícono de cámara descarga la imagen.</p>
%s<p>Ejercicio exploratorio con fines analíticos; el tratamiento del ajuste correspondiente es conceptual y no constituye una metodología oficial bajo el Artículo 6. Material de propiedad del PNUD.</p>
</footer>
<script>%s</script>
</body>
</html>""" % (_fuentes_css(), CSS, __import__("guias").CSS, P.CSS if PF else "", get_plotlyjs(), html.escape(pregunta),
       "".join(indice), "".join(cuerpo), "las gráficas del modelo" if PF else "todas las gráficas",
       P.pie_html() if PF else "", JS)
    destino = Path(destino) if destino else C.DOCS / "_static" / "tablero_art6.html"
    destino.parent.mkdir(parents=True, exist_ok=True)
    io.open(destino, "w", encoding="utf-8").write(doc)
    print("  tablero: %s (%.1f MB)" % (destino, destino.stat().st_size / 1e6))
    copia = C.RESULTADOS / "tablero_art6.html"       # sandbox PNUD: el tablero queda también junto a las tablas
    if copia.resolve() != destino.resolve():
        copia.parent.mkdir(parents=True, exist_ok=True)
        io.open(copia, "w", encoding="utf-8").write(doc)
        print("  tablero: %s" % copia)
    return destino


def regenerar(destino=None):
    """Rehace solo el tablero desde B2_Output_Art6 (resultados_art6.json y tablas) y Art6_motor/datos_productos, sin
    correr el modelo ni el analisis. Se niega si el analisis no esta al dia con sus origenes, porque entonces
    graficar.Datos() lo recalcularia: en ese caso corresponde la etapa B3 completa."""
    import analizar
    if not analizar.vigente():
        raise SystemExit("El análisis no está al día con sus orígenes: corra la etapa B3 completa antes de rehacer el "
                         "tablero.")
    F, L = G.generar(png=False)
    return exportar(F, L, destino)


if __name__ == "__main__":          # python tablero.py
    regenerar()
