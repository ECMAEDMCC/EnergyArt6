# -*- coding: utf-8 -*-
"""Gráfica de portada de la documentación: emisiones del sector energía con la NDC condicional corregida y con los
escenarios de Artículo 6, y lo que el último escalón reduce frente a esa referencia en la ventana de transacciones.

Es la versión apaisada y estática de g01 (oferta de Artículo 6 por tramo) para abrir docs/index.rst: sin botones, sin
bloque de título y sin el tramo condicional, que se discute en las páginas de análisis. Las cifras salen de
resultados_art6.json (Output.csv de cada escenario); ninguna se escribe a mano. Escribe:
- B2_Output_Art6/graficas/portada_impacto.png, que exportar_docs copia a docs/_static/graficas en cada corrida;
- docs/_static/graficas/portada_impacto.png;
- docs/_generado/portada.rst, con el título-mensaje, la imagen y su leyenda.

Uso, desde Energy:  python Art6_motor/portada.py
No recalcula el análisis: si resultados_art6.json no está al día con sus orígenes, se detiene y pide correr B3.
"""
import base64
import json
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

import plotly.graph_objects as go

import analizar
import comun as C
import graficar as G

NOMBRE = "portada_impacto"
ANCHO, ALTO = 1000, 500
FUENTES = Path(__file__).resolve().parent / "fuentes"
VERDE_AREA = "rgba(14,124,107,0.30)"


def _css_fuentes():
    """Fira Sans incrustada, para que la PNG tenga la misma letra que la documentación."""
    reglas = []
    for peso in (400, 600):
        f = FUENTES / ("FiraSans-%d.woff2" % peso)
        if f.exists():
            reglas.append("@font-face{font-family:'Fira Sans';font-weight:%d;font-style:normal;"
                          "src:url(data:font/woff2;base64,%s) format('woff2')}"
                          % (peso, base64.b64encode(f.read_bytes()).decode()))
    return "".join(reglas)


def cifras(D):
    """Reducción del último escalón frente a la referencia condicional en la ventana y oferta del sistema intacto,
    con los bloques que la oferta suma a esa reducción."""
    v = list(C.VENTANA)
    area = sum(max(0.0, D.em[D.con][a] - D.em[D.top][a]) for a in v)
    P = D.R["potencial_art6"]
    intacto = next(f for f in P["tabla"] if f.get("regla") == "condicional" and not f.get("sufijo"))
    bloques = {clave: float(intacto.get(nom) or 0.0) for nom, _, clave in P["bloques"]}
    capas = sum(x for clave, x in bloques.items() if clave.startswith("capa:"))
    # Se informa la suma de las capas, redondeadas como en las tablas del análisis, para que la portada cuadre con
    # la oferta y con las cifras principales; si no coincide con el área de la gráfica, manda el área.
    reduccion = round(capas, 1) if abs(capas - area) < 0.5 else round(area, 1)
    return {"reduccion": reduccion, "oferta": float(intacto["oferta_total"]),
            "firme": bloques.get("firme", 0.0), "declarado": bloques.get("declarado", 0.0)}


def figura(D, k):
    em, v = D.em, list(C.VENTANA)
    x = list(range(2020, v[-1] + 1))
    con, top = D.con, D.top
    escenarios = [c for c in [con] + list(D.esc) if c in em]
    fig = go.Figure()
    cc = [em[con][a] for a in v]
    piso = [min(c, em[top][a]) for c, a in zip(cc, v)]
    for t in G._franja(v, piso, cc, VERDE_AREA, "Reducción frente a la NDC condicional corregida", True,
                       mostrar_leyenda=False):          # la rotula la anotación
        fig.add_trace(t)
    idx = []
    for c in escenarios:
        tr = G.linea(c, x, [em[c][a] for a in x])
        tr.name = ("%s (%s)" % (D.nombre(c), c)) if c == con else ("%s · %s" % (c, D.nombre(c)))
        idx.append(len(fig.data))
        fig.add_trace(tr)
    G.maquetar(fig, "", "", "kt CO2-eq", alto=ALTO)
    fig.update_layout(title=None, width=ANCHO, height=ALTO, margin=dict(t=34, l=72, r=150, b=92),
                      font=dict(family=G.LETRA, size=15, color=G.TINTA),
                      legend=dict(orientation="h", x=0, xanchor="left", y=-0.12, yanchor="top", font=dict(size=14)))
    fig.update_xaxes(range=[x[0] - 0.3, x[-1] + 0.6], tickfont=dict(size=14), title_text="")
    fig.update_yaxes(tickfont=dict(size=14), title_font=dict(size=14))
    medio = v[len(v) // 2]
    y_area = (em[con][medio] + em[top][medio]) / 2.0
    rango = max(em[con][a] for a in x) - min(em[con][a] for a in x)
    y_texto = min(em[c][a] for c in escenarios for a in v) - 0.12 * rango
    fig.add_annotation(x=medio, y=y_area, ax=medio, ay=y_texto, xref="x", yref="y", axref="x", ayref="y",
                       showarrow=True, arrowhead=0, arrowwidth=1.2, arrowcolor=G.TINTA_2, align="center",
                       yanchor="top", font=dict(size=15, color=G.TINTA),
                       text="<b>%s kt CO2-eq</b><br>menos que la NDC condicional<br>corregida en %d-%d"
                       % (G.miles(k["reduccion"], 1), v[0], v[-1]))
    finales = G.etiquetas_finales(fig, idx)
    for a in finales:
        a["font"] = dict(size=13, color=G.TINTA)
    fig.update_layout(annotations=list(fig.layout.annotations) + finales)
    for a in fig.layout.annotations:
        if a.text and a.text.startswith(("Segunda NDC", "transacciones")):
            a.font = dict(size=13, color=G.TINTA_2)
    return fig


def exportar_png(fig, destino):
    """Chrome sin ventana dibuja la figura con Fira Sans ya cargada y guarda la captura a escala 2."""
    nav = G._chrome()
    if not nav:
        raise SystemExit("Sin Chrome ni Edge: no se puede exportar la gráfica de portada.")
    from plotly.offline import get_plotlyjs
    tmp = Path(tempfile.mkdtemp(prefix="art6_portada_"))
    (tmp / "plotly.min.js").write_text(get_plotlyjs(), encoding="utf-8")
    html = tmp / (NOMBRE + ".html")
    html.write_text(
        "<!doctype html><html><head><meta charset='utf-8'><style>%s html,body{margin:0;background:#fff}</style>"
        "<script src='plotly.min.js'></script></head><body><div id='g' style='width:%dpx;height:%dpx'></div><script>"
        "Promise.all([document.fonts.load(\"400 14px 'Fira Sans'\"),document.fonts.load(\"600 14px 'Fira Sans'\")])"
        ".then(function(){var f=%s;Plotly.newPlot('g',f.data,f.layout,{staticPlot:true,displayModeBar:false});});"
        "</script></body></html>" % (_css_fuentes(), ANCHO, ALTO, fig.to_json()), encoding="utf-8")
    destino.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run([nav, "--headless=new", "--disable-gpu", "--hide-scrollbars", "--force-device-scale-factor=2",
                    "--window-size=%d,%d" % (ANCHO, ALTO), "--virtual-time-budget=6000",
                    "--screenshot=%s" % destino, html.as_uri()], timeout=120, capture_output=True)
    if not destino.exists():
        raise SystemExit("Chrome no escribió %s" % destino)


def rst(D, k):
    v = list(C.VENTANA)
    titulo = ("Reducción de %s kt\u00a0CO2\u2011eq frente a la NDC condicional corregida en %d-%d"
              % (G.miles(k["reduccion"], 1), v[0], v[-1]))
    leyenda = ("Emisiones del sector energía con la NDC condicional corregida (%s) y con los escenarios de Artículo 6 %s "
               "(kt CO2-eq). El área verde es lo que %s reduce frente a %s en la ventana de transacciones."
               % (D.con, C.enumerar(D.esc), G._el(D.nombre(D.top)), D.con))
    resto = k["oferta"] - k["reduccion"]
    if k["firme"] > 0 and abs(resto - k["firme"] - k["declarado"]) < 0.5:     # la oferta suma bloques fuera de la capa
        leyenda += (" La oferta transferible, %s kt, suma a esa reducción la línea firme, |firmes| (%s kt), y las líneas "
                    "con potencial declarado (%s kt)." % (G.miles(k["oferta"], 1), G.miles(k["firme"], 1),
                                                          G.miles(k["declarado"], 1)))
    # espacio duro entre grupos de miles, para que ninguna cifra se parta al final de una línea
    titulo, leyenda = (re.sub(r"(?<=\d) (?=\d)", " ", x) for x in (titulo, leyenda))
    return "\n".join([
        ".. Generado por Energy/Art6_motor/portada.py en cada corrida. No se edita a mano.", "",
        ".. container:: ea-impacto", "",
        "   .. rubric:: %s" % titulo, "",
        "   .. image:: /_static/graficas/%s.png" % NOMBRE,
        "      :width: 100%",
        "      :alt: Emisiones del sector energía de 2020 a %d con la NDC condicional corregida y con los escenarios "
        "de Artículo 6. %s" % (v[-1], titulo), "",
        "   .. rst-class:: ea-impacto-leyenda", "",
        "   " + leyenda, ""])


def generar():
    if not analizar.vigente():
        raise SystemExit("El análisis no está al día con sus orígenes: corra B3 antes de rehacer la portada.")
    D = G.Datos()
    if not D.top or D.con not in D.em or D.top not in D.em:
        raise SystemExit("La corrida no trae la referencia condicional y un escalón de Artículo 6: no hay portada.")
    k = cifras(D)
    png = C.GRAFICAS / (NOMBRE + ".png")
    exportar_png(figura(D, k), png)
    img = C.DOCS / "_static" / "graficas"
    img.mkdir(parents=True, exist_ok=True)
    shutil.copy2(png, img / png.name)
    gen = C.DOCS / "_generado"
    gen.mkdir(parents=True, exist_ok=True)
    (gen / "portada.rst").write_text(rst(D, k), encoding="utf-8")
    print("  portada: %s" % json.dumps({c: round(x, 1) for c, x in k.items()}))
    return k


if __name__ == "__main__":
    generar()
    sys.exit(0)
