# -*- coding: utf-8 -*-
"""Secciones del tablero con los Productos 1 a 4: demanda, cartera, remociones, puentes y cartera viable.

Lee las entradas de datos_productos/ (las escribe extraer_productos.py desde el tablero de los Productos 1 a 4) y
arma, en el estilo del tablero de resultados, las graficas Plotly, su guia de lectura y la tabla de datos de cada
una. La cartera de la Segunda NDC llega solo agregada: numero de iniciativas por sector, veredicto, actividad, tramo
y canal, sin nombres, codigos ni potenciales. Toda cifra de los textos se calcula de esos datos. Si la carpeta no
existe, figuras() y bloques() devuelven vacio y el tablero sale sin estas secciones.
"""
import html as H
import io
import json
import re
import unicodedata
from collections import Counter, OrderedDict
from pathlib import Path

import plotly.graph_objects as go

import comun as C
import graficar as G

DATOS = Path(__file__).resolve().parent / "datos_productos"

# paleta del proyecto
AZUL, VERDE, OCRE, LADRILLO = "#4E5D7E", "#0E7C6B", "#C08A2E", "#9A3B34"
TINTA, GRIS, REGLA, TINTE = "#1F2937", "#5B6470", "#C9D1CE", "#EEF1F5"
GRIS_CLARO, AZUL_CLARO, VERDE_CLARO, OCRE_CLARO = "#B6BCC4", "#8592AD", "#5FA79B", "#D9BC84"

SECCIONES = [
    ("Demanda de mitigación", ["p01_compradores", "p02_escalera", "p03_actividades", "p04_corsia", "p05_perimetro"]),
    ("Cartera de la Segunda NDC", ["p06_sector", "p07_actividad", "p08_tramo"]),
    ("Remociones de carbono", ["p09_filtros", "p10_madurez"]),
    ("Puentes entre la oferta y la demanda", ["p11_puentes", "p11b_puentes_actividad", "p12_puentes_remociones"]),
    ("Cartera viable y condiciones de integridad", ["p13_cartera_viable"]),
]

A6 = ["JCM", "Suiza", "Otros"]
NOMBRE_FUENTE = {"JCM": "JCM (Japón)", "Suiza": "Suiza", "Otros": "Otros compradores", "CORSIA": "CORSIA"}
EN_FRASE = {"JCM": "el JCM", "Suiza": "Suiza", "Otros": "otros compradores", "CORSIA": "CORSIA"}
# paises que la matriz del JCM escribe en ingles, para las frases (las tablas los muestran como vienen)
PAISES = {"Bangladesh": "Bangladés", "Cambodia": "Camboya", "Ethiopia": "Etiopía", "Kenya": "Kenia",
          "Kyrgyz Republic": "Kirguistán", "Lao PDR": "Laos", "Maldives": "Maldivas", "Mexico": "México",
          "Papua New Guinea": "Papúa Nueva Guinea", "Philippines": "Filipinas", "Saudi Arabia": "Arabia Saudita",
          "Thailand": "Tailandia", "Tunisia": "Túnez", "Ukraine": "Ucrania", "United Arab Emirates": "Emiratos Árabes Unidos",
          "Uzbekistan": "Uzbekistán", "Viet Nam": "Vietnam", "Azerbaijan": "Azerbaiyán", "Rwanda": "Ruanda"}
COLOR_CATEGORIA = {"Revelada": VERDE, "Anunciada": OCRE, "Perímetro": AZUL}
COLOR_VEREDICTO = {"Núcleo": VERDE, "Condicionado": OCRE, "Descartar": LADRILLO, "Doméstico": AZUL,
                   "Pendiente": GRIS_CLARO, "Habilitante": GRIS}
PLURAL_VEREDICTO = {"Núcleo": "núcleo", "Condicionado": "condicionadas", "Descartar": "descartadas",
                    "Doméstico": "domésticas", "Pendiente": "pendientes", "Habilitante": "habilitantes"}
SINGULAR_VEREDICTO = {"Núcleo": "núcleo", "Condicionado": "condicionada", "Descartar": "descartada",
                      "Doméstico": "doméstica", "Pendiente": "pendiente", "Habilitante": "habilitante"}
SECTOR = {"IPU": "Procesos industriales"}
ORDEN_SECTOR = ["Energía", "Transporte", "Residuos", "IPU"]
COLOR_TRAMO = {"Incondicional": GRIS, "Condicional": AZUL, "Condicional (duplica una iniciativa de la NDC)": AZUL_CLARO,
               "Por determinar": GRIS_CLARO, "No aplica (habilitante)": "#DDE1E5", "Fuera de la NDC": OCRE_CLARO}
COLOR_CLASE = {"Núcleo": VERDE, "Vigilancia": AZUL, "Condicionado": OCRE, "Fuera de alcance": LADRILLO}
COLOR_ESTADO = {"Elegible": VERDE, "Condicionada": OCRE, "Excluida": LADRILLO, "Requisito": AZUL, "Compuerta": AZUL_CLARO}
NIVEL_SINTESIS = {"Reducción — núcleo": "Reducción del núcleo", "Reducción — condicionada": "Reducción condicionada",
                  "Remoción — núcleo (2.ª pierna)": "Remoción del núcleo"}
COLOR_NIVELES = [VERDE, OCRE, AZUL, GRIS]
MESES = {"ene": "enero", "feb": "febrero", "mar": "marzo", "abr": "abril", "may": "mayo", "jun": "junio",
         "jul": "julio", "ago": "agosto", "sep": "septiembre", "oct": "octubre", "nov": "noviembre", "dic": "diciembre"}
# escala de los filtros de las remociones: 5 favorable, 1 desfavorable; en la intensidad mineral (F4) baja es favorable
ESCALA = ["Alta", "Media-alta", "Media", "Baja-media", "Baja"]
COLOR_ESCALA = [LADRILLO, OCRE, GRIS_CLARO, VERDE_CLARO, VERDE]
T_TABLERO = 24          # margen superior de cada grafica en el tablero, que lleva el titulo en HTML (tablero._separar_titulo)

# graficas que en pantallas angostas conservan un ancho minimo y se desplazan dentro de su tarjeta (px)
ANCHO_MINIMO = OrderedDict([("p09_filtros", 600), ("p11_puentes", 720), ("p11b_puentes_actividad", 720),
                            ("p12_puentes_remociones", 720), ("p13_cartera_viable", 600)])
CSS = """
.figura .fuente{margin:.5rem 0 0;color:var(--tinta-3);font-size:.8125rem;max-width:95ch}
.tabla caption{caption-side:top;text-align:left;color:var(--tinta-3);font-size:.8125rem;padding:0 0 .375rem}
.tabla td.texto,.tabla th.texto{text-align:left;white-space:normal;min-width:9rem}
.figura .datos+.datos{border-top:0;margin-top:0}
#p00_registros .tabla th.texto,#p00_registros .tabla td.texto{min-width:7rem}
#p00_registros .tabla tbody th.texto{min-width:17rem}
""" + "".join("#%s .grafica{overflow-x:auto}#%s .grafica .plotly-graph-div{min-width:%dpx;max-width:none}\n"
              % (g, g, px) for g, px in ANCHO_MINIMO.items())


# ----------------------------------------------------------------------------- datos y utilidades
def _cargar():
    rutas = OrderedDict((k, DATOS / ("%s.json" % k)) for k in ("demanda", "remociones", "cartera_agregada", "sintesis"))
    if not all(r.exists() for r in rutas.values()):
        return None
    return {k: json.load(io.open(r, encoding="utf-8")) for k, r in rutas.items()}


def _e(s):
    return H.escape(str(s))


def _rot(s):
    """Rotulo para mostrar: sin rayas entre palabras."""
    return re.sub(r"\s+[—–]\s+", ", ", str(s)).strip()


def _frase(s):
    """«Sin Registro Formal» -> «Sin registro formal»: minuscula en las palabras capitalizadas salvo la primera."""
    ps = str(s).split(" ")
    return " ".join([ps[0]] + [p.lower() if p[:1].isupper() and p[1:].islower() else p for p in ps[1:]])


def _min(s):
    """Rotulo dentro de una frase: primera letra en minuscula salvo en siglas; un rotulo con todas sus palabras
    capitalizadas («Eficiencia Energética Industrial») pasa antes a mayuscula solo inicial."""
    s = _rot(s)
    palabras = [p for p in re.findall(r"[^\W\d_]+", re.sub(r"\([^)]*\)", " ", s)) if len(p) > 3]
    if len(palabras) > 1 and all(p[0].isupper() and p[1:].islower() for p in palabras):
        s = _frase(s)
    return s[:1].lower() + s[1:] if s[:1].isupper() and s[1:2].islower() else s


def _sin_parentesis(s):
    return re.sub(r"\s*\([^)]*\)", "", str(s)).strip()


def _norm(s):
    return " ".join(re.findall(r"[a-z0-9+]+", unicodedata.normalize("NFKD", str(s)).encode("ascii", "ignore")
                               .decode().lower()))


def _partir(s, ancho=30):
    """Parte un rotulo largo en lineas de unos `ancho` caracteres con <br>."""
    lineas, actual = [], ""
    for p in str(s).split(" "):
        if actual and len(actual) + len(p) + 1 > ancho:
            lineas.append(actual)
            actual = p
        else:
            actual = (actual + " " + p).strip()
    return "<br>".join(lineas + ([actual] if actual else []))


def _pl(n, singular, plural):
    return "%s %s" % (G.miles(n), singular if n == 1 else plural)


def _veredicto(v, n=1):
    """Veredicto como adjetivo de «iniciativa» o «actividad»: «doméstica», «domésticas»."""
    return (SINGULAR_VEREDICTO if n == 1 else PLURAL_VEREDICTO).get(v, str(v).lower())


def _mes(fecha):
    """«jun-2026» -> «junio de 2026»."""
    m = re.match(r"([a-z]{3})-(\d{4})$", str(fecha or ""))
    return "%s de %s" % (MESES.get(m.group(1), m.group(1)), m.group(2)) if m else str(fecha or "")


def _pct(a, b):
    return ("%.0f" % (100.0 * a / b) if b else "0") + " %"


def _y(xs):
    return C.enumerar([x for x in xs if x])


def _y_rotulos(xs):
    """Enumeracion de rotulos que pueden llevar comas: separa con punto y coma."""
    xs = [x for x in xs if x]
    return xs[0] if len(xs) == 1 else "; ".join(xs[:-1]) + " y " + xs[-1] if xs else ""


def _texto_sobre(color):
    """Tinta o blanco segun la luminancia del relleno."""
    r, g, b = (int(color[i:i + 2], 16) / 255.0 for i in (1, 3, 5))
    lum = lambda c: c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4
    return "white" if 0.2126 * lum(r) + 0.7152 * lum(g) + 0.0722 * lum(b) < 0.30 else TINTA


def _rgba(color, a):
    return "rgba(%d,%d,%d,%.2f)" % (int(color[1:3], 16), int(color[3:5], 16), int(color[5:7], 16), a)


def _guia(muestra, leer, analisis, decision):
    return "\n\n".join("%s. %s" % (et, t) for et, t in (("Qué muestra", muestra), ("Cómo leerla", leer),
                                                       ("Qué dice el análisis", analisis),
                                                       ("Para la decisión", decision)) if t)


def _tabla(cabecera, filas, unidad, resumen="Ver datos de la gráfica", texto=(0,)):
    """<details> con la tabla de datos: cabecera [col], filas [[celda]] (la primera es encabezado de fila); `texto`
    marca las columnas de texto, que se alinean a la izquierda."""
    clase = lambda j: " class='texto'" if j in texto else ""
    cab = "".join("<th scope='col'%s>%s</th>" % (clase(j), _e(c)) for j, c in enumerate(cabecera))
    cuerpo = "".join("<tr><th scope='row'%s>%s</th>%s</tr>" % (
        clase(0), _e(f[0]), "".join("<td%s>%s</td>" % (clase(j + 1), _e(v)) for j, v in enumerate(f[1:])))
        for f in filas)
    return ("<details class='datos'><summary>%s</summary><div class='tabla'><table><caption>%s</caption><thead><tr>%s"
            "</tr></thead><tbody>%s</tbody></table></div></details>" % (_e(resumen), _e(unidad), cab, cuerpo))


def _figura(gid, indice, fig, guia, tabla, fuente):
    return OrderedDict([("gid", gid), ("indice", indice), ("fig", fig), ("guia", guia), ("tabla", tabla),
                        ("fuente", fuente)])


def _maquetar(fig, titulo, hallazgo, sub, unidad, alto, horizontal=True, xtitulo=""):
    """Estilo del tablero (graficar.maquetar) con el hallazgo en negrita al inicio del subtitulo, el eje de valores con
    su unidad y rejilla tenue, y la leyenda bajo el eje. Las graficas sin ejes (Sankey) reciben titulo, letra y margenes."""
    hallazgo = hallazgo if hallazgo.endswith(".") else hallazgo + "."
    if any(tr.type == "sankey" for tr in fig.data):
        s = G._envolver("<b>%s</b> %s" % (hallazgo, sub))
        fig.update_layout(template="plotly_white", height=alto, separators=", ", paper_bgcolor="white",
                          font=dict(family=G.LETRA, size=13, color=TINTA),
                          title=dict(text="<b>%s</b><br><span style='font-size:13px;color:%s'>%s</span>"
                                          % (titulo, G.TINTA_2, s), x=0.0, xanchor="left", y=0.975, yanchor="top",
                                     font=dict(size=18)),
                          margin=dict(l=20, r=20, t=88 + 20 * (s.count("<br>") + 1), b=30),
                          hoverlabel=dict(bgcolor="white", bordercolor="#CBD5E1",
                                          font=dict(size=12, family=G.LETRA, color=TINTA)))
        return fig
    G.maquetar(fig, titulo, "<b>%s</b> %s" % (hallazgo, sub), None if horizontal else unidad, alto=alto,
               xtitulo=unidad if horizontal else xtitulo)
    fig.update_layout(hovermode="closest", uniformtext=dict(minsize=10, mode="hide"))
    valores = dict(showgrid=True, gridcolor=G.REJILLA, zeroline=True, zerolinecolor=REGLA, tickformat=",d",
                   rangemode="tozero")
    if horizontal:
        fig.update_xaxes(**valores)
        fig.update_yaxes(autorange="reversed", showgrid=False, ticks="", tickfont=dict(size=12, color=TINTA))
    else:
        fig.update_yaxes(**valores)
    b = fig.layout.margin.b or 80
    util = max((fig.layout.height or alto) - T_TABLERO - b, 120)
    fig.update_layout(legend=dict(y=-min(0.6, 62.0 / util), traceorder="normal"))
    return fig


def _totales(fig, cats, totales, textos=None, horizontal=True):
    """Etiqueta directa con el total al final de cada barra apilada."""
    for i, (c, t) in enumerate(zip(cats, totales)):
        txt = textos[i] if textos else "<b>%s</b>" % G.miles(t)
        if horizontal:
            fig.add_annotation(x=t, y=c, text=txt, xanchor="left", xshift=5, showarrow=False,
                               font=dict(size=12, color=TINTA))
        else:
            fig.add_annotation(x=c, y=t, text=txt, yanchor="bottom", yshift=3, showarrow=False,
                               font=dict(size=12, color=TINTA))


def _barra(fig, cats, vals, nombre, color, unidad, horizontal=True, dentro=True, minimo=0, **extra):
    """Barra con etiqueta directa: dentro del segmento (si mide al menos `minimo`) o al final."""
    vals = [v or 0 for v in vals]
    eje = "%{y}" if horizontal else "%{x}"
    valor = "%{x}" if horizontal else "%{y}"
    fig.add_bar(**dict(dict(
        x=vals if horizontal else cats, y=cats if horizontal else vals, name=nombre,
        orientation="h" if horizontal else "v", marker=dict(color=color, line=dict(color="white", width=1)),
        text=[G.miles(v) if v and v >= minimo else "" for v in vals], textposition="inside" if dentro else "outside",
        insidetextanchor="middle", textfont=dict(color=_texto_sobre(color) if dentro else TINTA, size=12),
        cliponaxis=False, hovertemplate=eje + ": " + valor + " " + unidad + "<extra>" + _e(nombre) + "</extra>"),
        **extra))


def _columna(valores, pad):
    """Centros normalizados (0 a 1) de los nodos de una columna de Sankey, en orden, con alto proporcional al valor."""
    total = float(sum(valores)) or 1.0
    util = 1.0 - pad * (len(valores) - 1)
    ys, y = [], 0.0
    for v in valores:
        h = util * v / total
        ys.append(min(0.999, max(0.001, y + h / 2.0)))
        y += h + pad
    return ys


# ----------------------------------------------------------------------------- 1. demanda
def _fuente(D, que):
    o = D["demanda"]["origen"]
    return ("Fuente: tablero de los Productos 1 a 4 (versión %s), %s; extracción en Energy/Art6_motor/datos_productos."
            % (o["version"], que))


def _compradores_otros(regs):
    """Compradores de la fuente «Otros»: el texto antes de los dos puntos en el rotulo del registro."""
    nombres = []
    for r in regs:
        if r["Fuente"] == "Otros" and ":" in str(r["Proyecto"]):
            n = re.sub(r"\s*\([^)]*\)", "", r["Proyecto"].split(":")[0]).strip()
            if n and n not in nombres:
                nombres.append(n)
    return nombres


def _paises(regs):
    ps = []
    for r in regs:
        for p in re.split(r"\s*[;/]\s*", str(r.get("Pais") or "")):
            p = re.sub(r"\s*\(.*$", "", p).strip()
            if p and p not in ps:
                ps.append(p)
    return ps


def f_compradores(D):
    regs = [r for r in D["demanda"]["registros"] if r["Fuente"] in A6]
    cats = [NOMBRE_FUENTE[f] for f in A6]
    n = {(f, c): sum(1 for r in regs if r["Fuente"] == f and r["Categoria"] == c) for f in A6
         for c in ("Revelada", "Anunciada")}
    fig = go.Figure()
    for c, nombre in (("Revelada", "Demanda revelada"), ("Anunciada", "Demanda anunciada")):
        _barra(fig, cats, [n[(f, c)] for f in A6], nombre, COLOR_CATEGORIA[c], "registros", dentro=False)
    rev = sum(n[(f, "Revelada")] for f in A6)
    tot = len(regs)
    con_rev = sorted([f for f in A6 if n[(f, "Revelada")]], key=lambda f: -n[(f, "Revelada")])
    sin_rev = [f for f in A6 if not n[(f, "Revelada")]]
    hallazgo = "De %d registros bilaterales del Artículo 6, %s demanda revelada" % (
        tot, "%d tienen" % rev if rev != 1 else "1 tiene")
    if con_rev:
        de = lambda f: re.sub(r"^de el ", "del ", "de " + EN_FRASE.get(f, f))
        hallazgo += ": " + _y(["%d %s" % (n[(f, "Revelada")], de(f)) for f in con_rev])
    if sin_rev:
        anun = sum(n[(f, "Anunciada")] for f in sin_rev)
        hallazgo += "; %s %s demanda anunciada" % (
            _y([("los %d del %s" if f == "JCM" else "los %d de %s") % (n[(f, "Anunciada")], f) for f in sin_rev]),
            "es" if anun == 1 else "son")
    _maquetar(fig, "Registros del Artículo 6 por comprador y categoría", hallazgo,
              "Número de registros bilaterales de la matriz de demanda del Capítulo 1. CORSIA va aparte porque usa "
              "otro umbral de demanda revelada.", "número de registros", alto=380)
    fig.update_layout(barmode="group", bargap=0.28, bargroupgap=0.08)
    fig.update_xaxes(range=[0, max(n.values()) * 1.15])
    jcm = sum(n[("JCM", c)] for c in ("Revelada", "Anunciada"))
    ecuador = "Ecuador" in _paises(D["demanda"]["registros"])
    guia = _guia(
        "Los %d registros bilaterales del Artículo 6 en la matriz de demanda del Capítulo 1, por comprador: el Japón con "
        "su Mecanismo de Crédito Conjunto (JCM), Suiza y otros compradores (%s). Cada registro es un proyecto, un "
        "acuerdo o una autorización con un país anfitrión." % (tot, _y(_compradores_otros(regs))),
        "La barra verde cuenta la demanda revelada, que en el Artículo 6.2 bilateral exige contrato de compra (peldaño "
        "N4) o transferencia del ITMO (N5). La ocre cuenta la demanda anunciada: acuerdos bilaterales, proyectos "
        "registrados, créditos emitidos y cartas de autorización sin contrato.",
        "La demanda revelada suma %d registros, el %s del total. El JCM aporta %d registros, el %s, y %s."
        % (rev, _pct(rev, tot), jcm, _pct(jcm, tot),
           "ninguno llega a contrato o transferencia" if not n[("JCM", "Revelada")] else
           "%d llegan a contrato o transferencia" % n[("JCM", "Revelada")]),
        ("Ningún registro tiene al Ecuador como país anfitrión: la demanda revelada de otros países indica qué tipo de "
         "actividad llega a contrato, y el acceso del Ecuador depende de los acuerdos bilaterales que firme."
         if not ecuador else "La matriz registra acuerdos con el Ecuador como anfitrión; su peldaño define si cuentan "
                             "como demanda revelada."))
    tabla = _tabla(["Comprador", "Demanda revelada", "Demanda anunciada", "Total"],
                   [[c, n[(f, "Revelada")], n[(f, "Anunciada")], n[(f, "Revelada")] + n[(f, "Anunciada")]]
                    for f, c in zip(A6, cats)] + [["Total", rev, tot - rev, tot]], "Unidad: número de registros.")
    return _figura("p01_compradores", "Registros por comprador", fig, guia, tabla,
                   _fuente(D, "Capítulo 1, matriz de demanda (bloque DATA)"))


def f_escalera(D):
    regs = [r for r in D["demanda"]["registros"] if r["Fuente"] in A6]
    esc = D["demanda"]["escalera"]
    peld = [e["peldano"] for e in esc]
    etiquetas = ["<b>%s</b> · %s" % (e["peldano"], _partir(_frase(e["descripcion"]), 22)) for e in esc]
    fig = go.Figure()
    tonos = {"JCM": AZUL, "Suiza": AZUL_CLARO, "Otros": "#B9C1D3"}
    cuenta = {(f, p): sum(1 for r in regs if r["Fuente"] == f and "N%d" % int(r["lvl"]) == p) for f in A6 for p in peld}
    tot = [sum(cuenta[(f, p)] for f in A6) for p in peld]
    for f in A6:
        _barra(fig, etiquetas, [cuenta[(f, p)] for p in peld], NOMBRE_FUENTE[f], tonos[f], "registros",
               minimo=0.06 * max(tot))
    _totales(fig, etiquetas, tot)
    rev_p = [p for p, e in zip(peld, esc) if e["lado"] == "revelada"]
    i0 = peld.index(rev_p[0]) if rev_p else len(peld)
    franja = dict(xref="paper", x=0.995, xanchor="right", showarrow=False, font=dict(size=11, color=G.TINTA_2))
    fig.add_hrect(y0=-0.5, y1=i0 - 0.5, fillcolor="#F6EEDF", opacity=0.7, layer="below", line_width=0)
    fig.add_annotation(y=-0.5, yanchor="top", text="demanda anunciada", **franja)    # eje invertido: arriba
    if rev_p:
        fig.add_hrect(y0=i0 - 0.5, y1=len(peld) - 0.5, fillcolor="#DCEEE9", opacity=0.8, layer="below", line_width=0)
        fig.add_annotation(y=len(peld) - 0.5, yanchor="bottom", text="demanda revelada", **franja)
        fig.add_hline(y=i0 - 0.5, line=dict(color=TINTA, width=1.5, dash="dash"))
    n12 = sum(cuenta[(f, p)] for f in A6 for p in ("N1", "N2"))
    nrev = sum(cuenta[(f, p)] for f in A6 for p in rev_p)
    _maquetar(fig, "Escalera N0-N5 de los registros del Artículo 6",
              "%d de %d registros están en N1 y N2, registrados o con créditos emitidos; %s a contrato o transferencia"
              % (n12, len(regs), "solo %d llegan" % nrev if nrev != 1 else "solo 1 llega"),
              "Número de registros bilaterales por peldaño de la escalera y por comprador. La línea discontinua es el "
              "umbral del Artículo 6.2: la demanda se revela con el contrato (N4) o la transferencia (N5).",
              "número de registros", alto=420)
    fig.update_layout(barmode="stack", bargap=0.3)
    fig.update_xaxes(range=[0, max(tot) * 1.15])
    guia = _guia(
        "El peldaño que la matriz del Capítulo 1 asigna a cada registro bilateral, desde el acuerdo sin registro formal "
        "(N0) hasta el ITMO transferido (N5), apilado por comprador.",
        "La franja ocre reúne los peldaños de demanda anunciada y la verde los de demanda revelada. En el Artículo 6.2 "
        "bilateral la carta de autorización con ajuste (N3) es oferta autorizada por el país anfitrión; la demanda se "
        "revela con el contrato o la transferencia. Los registros con un rango de peldaños (N0-N1, N1-N2) van en el "
        "peldaño que les asigna la matriz.",
        "El JCM tiene %d registros en N1 y %d en N2. Suiza suma %d en N3 y %d en N5. Los otros compradores tienen %d en N4."
        % (cuenta[("JCM", "N1")], cuenta[("JCM", "N2")], cuenta[("Suiza", "N3")], cuenta[("Suiza", "N5")],
           cuenta[("Otros", "N4")]),
        "Para el Ecuador, una carta de autorización no basta para contar demanda: el criterio exige contrato o "
        "transferencia.")
    tabla = _tabla(["Peldaño", "Descripción"] + [NOMBRE_FUENTE[f] for f in A6] + ["Total"],
                   [[p, _frase(e["descripcion"])] + [cuenta[(f, p)] for f in A6] + [t]
                    for p, e, t in zip(peld, esc, tot)], "Unidad: número de registros.", texto=(0, 1))
    return _figura("p02_escalera", "Escalera N0-N5", fig, guia, tabla,
                   _fuente(D, "Capítulo 1, matriz de demanda (bloque DATA) y escalera N0-N5"))


def f_actividades(D):
    regs = [r for r in D["demanda"]["registros"] if r["Fuente"] in A6]
    cuenta = Counter((r["Actividad"], r["Categoria"]) for r in regs)
    acts = sorted(set(r["Actividad"] for r in regs),
                  key=lambda a: (-(cuenta[(a, "Revelada")] + cuenta[(a, "Anunciada")]), a))
    creditos = Counter()
    for r in regs:
        creditos[r["Actividad"]] += float(r.get("Creditos") or 0)
    cats = [_partir(_rot(a), 30) for a in acts]
    tot = [cuenta[(a, "Revelada")] + cuenta[(a, "Anunciada")] for a in acts]
    fig = go.Figure()
    for c, nombre in (("Revelada", "Demanda revelada"), ("Anunciada", "Demanda anunciada")):
        _barra(fig, cats, [cuenta[(a, c)] for a in acts], nombre, COLOR_CATEGORIA[c], "registros",
               minimo=0.06 * max(tot))
    textos = ["<b>%d</b>%s" % (t, (" · %s" % _pl(cuenta[(a, "Revelada")], "revelada", "reveladas"))
                                   if cuenta[(a, "Revelada")] and cuenta[(a, "Anunciada")] else "")
              for a, t in zip(acts, tot)]
    _totales(fig, cats, tot, textos)
    top = acts[:2]
    rev_acts = [a for a in acts if cuenta[(a, "Revelada")]]
    hallazgo = "%s y %s reúnen %d de %d registros%s; la demanda revelada está en %s" % (
        _rot(top[0]), _min(top[1]), sum(tot[:2]), len(regs),
        ", todos anunciados" if all(not cuenta[(a, "Revelada")] for a in top) else "",
        _pl(len(rev_acts), "actividad", "actividades"))
    _maquetar(fig, "Registros del Artículo 6 por tipo de actividad", hallazgo,
              "Número de registros bilaterales por actividad, con el rótulo de la matriz de demanda del Capítulo 1. "
              "La etiqueta da el total y, si la actividad tiene las dos categorías, cuántos registros son de demanda "
              "revelada.", "número de registros", alto=150 + 32 * len(acts))
    fig.update_layout(barmode="stack", bargap=0.3)
    fig.update_xaxes(range=[0, max(tot) * 1.22])
    tot_cred = sum(creditos.values())
    mayor = max(regs, key=lambda r: float(r.get("Creditos") or 0))
    afolu = [a for a in rev_acts if _norm(a).startswith("afolu")]
    max_rev = max(cuenta[(a, "Revelada")] for a in rev_acts) if rev_acts else 0
    analisis = "La demanda revelada se reparte en %s%s%s." % (
        _pl(len(rev_acts), "actividad", "actividades"),
        " con 1 registro cada una" if max_rev == 1 else "",
        ("; %d son de uso de la tierra (AFOLU)" % len(afolu)) if len(afolu) > 1 else "")
    if tot_cred:
        analisis += (" Los créditos ya emitidos en estos registros suman %s t CO2e, y un solo registro, de %s en %s, "
                     "aporta %s t, el %s." % (G.miles(tot_cred), _rot(mayor["Actividad"]),
                                              PAISES.get(mayor["Pais"], mayor["Pais"]),
                                              G.miles(float(mayor["Creditos"] or 0)),
                                              _pct(float(mayor["Creditos"] or 0), tot_cred)))
    guia = _guia(
        "Los registros bilaterales del Artículo 6 por tipo de actividad. «Multisectorial (por definir)» reúne los "
        "acuerdos bilaterales que todavía no asignan actividad.",
        "Cada barra suma los registros de una actividad; el verde es demanda revelada y el ocre, anunciada. La tabla "
        "agrega los créditos ya emitidos por actividad.",
        analisis,
        "La afinidad de la cartera del Ecuador con estas actividades se lee en la sección de puentes entre la oferta "
        "y la demanda.")
    tabla = _tabla(["Actividad", "Demanda revelada", "Demanda anunciada", "Total", "Créditos emitidos (t CO2e)"],
                   [[_rot(a), cuenta[(a, "Revelada")], cuenta[(a, "Anunciada")], t, G.miles(creditos[a])]
                    for a, t in zip(acts, tot)], "Unidad: número de registros; créditos emitidos en t CO2e.")
    return _figura("p03_actividades", "Registros por actividad", fig, guia, tabla,
                   _fuente(D, "Capítulo 1, matriz de demanda (bloque DATA)"))


def _decision_corsia(D, top, n_top, regs):
    """Para la decisión de las unidades CORSIA: la actividad con más cartas y su veredicto en la cartera del Ecuador."""
    raiz = _norm(_rot(top)).split(" ")[0]
    par = [a for a in D["cartera_agregada"]["por_actividad"] if _norm(a["actividad"]).startswith(raiz)]
    forestal = sum(1 for r in regs if r["Categoria"] == "Revelada" and re.search(r"(?i)redd|forestal", r["Actividad"]))
    txt = "La actividad con más cartas de autorización es «%s» (%d)" % (_rot(top), n_top)
    if par:
        txt += "; en la cartera del Ecuador, «%s» tiene el veredicto «%s»" % (_rot(par[0]["actividad"]), par[0]["veredicto"])
    txt += "."
    if forestal:
        txt += (" Las %d cartas de REDD+ y forestales no tienen contraparte en la cartera, cuyo alcance excluye lo "
                "forestal." % forestal if forestal > 1 else " La carta de REDD+ no tiene contraparte en la cartera, cuyo "
                                                           "alcance excluye lo forestal.")
    return txt


def f_corsia(D):
    regs = [r for r in D["demanda"]["registros"] if r["Fuente"] == "CORSIA" and r["Categoria"] != "Perímetro"]
    cuenta = Counter((r["Actividad"], r["Categoria"]) for r in regs)
    acts = sorted(set(r["Actividad"] for r in regs), key=lambda a: (-(cuenta[(a, "Revelada")] + cuenta[(a, "Anunciada")]), a))
    cats = [_partir(_rot(a), 28) for a in acts]
    tot = [cuenta[(a, "Revelada")] + cuenta[(a, "Anunciada")] for a in acts]
    fig = go.Figure()
    for c, nombre in (("Revelada", "Carta de autorización del anfitrión (N3)"),
                      ("Anunciada", "Elegible en la Fase I, sin carta de autorización")):
        _barra(fig, cats, [cuenta[(a, c)] for a in acts], nombre, COLOR_CATEGORIA[c], "registros")
    _totales(fig, cats, tot)
    rev = [r for r in regs if r["Categoria"] == "Revelada"]
    paises = _paises(rev)
    top = max(acts, key=lambda a: cuenta[(a, "Revelada")])
    _maquetar(fig, "Unidades CORSIA por actividad y categoría",
              "%s %s cartas de autorización para CORSIA; %d de ellas son de %s"
              % (_pl(len(paises), "país anfitrión", "países anfitriones"), "ya liberó" if len(paises) == 1 else "ya liberaron",
                 cuenta[(top, "Revelada")], _min(top)),
              "Número de registros del canal de aviación. En CORSIA la carta de autorización (N3) es el umbral de demanda "
              "revelada, porque el comprador es la obligación de cancelación de las aerolíneas.",
              "número de registros", alto=150 + 40 * len(acts))
    fig.update_layout(barmode="stack", bargap=0.3)
    fig.update_xaxes(range=[0, max(tot) * 1.15], dtick=1)
    guia = _guia(
        "Las unidades del canal CORSIA en la matriz del Capítulo 1: %s con carta de autorización del país anfitrión y %s "
        "elegibles en la Fase I que aún no la tienen." % (_pl(len(rev), "registro", "registros"),
                                                           _pl(len(regs) - len(rev), "registro", "registros")),
        "El verde es demanda revelada con el criterio de CORSIA (carta de autorización, N3); el ocre, unidades elegibles "
        "sin carta. El criterio difiere del Artículo 6.2 bilateral, que exige contrato o transferencia, y por eso los "
        "dos conteos de demanda revelada no se suman.",
        "Los anfitriones con carta son %s." % _y([PAISES.get(p, p) for p in paises]),
        _decision_corsia(D, top, cuenta[(top, "Revelada")], regs))
    tabla = _tabla(["Actividad", "Con carta de autorización (N3)", "Elegibles sin carta", "Total"],
                   [[_rot(a), cuenta[(a, "Revelada")], cuenta[(a, "Anunciada")], t] for a, t in zip(acts, tot)],
                   "Unidad: número de registros.")
    return _figura("p04_corsia", "Unidades CORSIA", fig, guia, tabla,
                   _fuente(D, "Capítulo 1, canal CORSIA de la matriz de demanda (bloque DATA)"))


def f_perimetro(D):
    regs = [r for r in D["demanda"]["registros"] if r["Fuente"] == "CORSIA" and r["Categoria"] == "Perímetro"]
    grupos = list(OrderedDict.fromkeys(r["Actividad"] for r in regs))
    estados = [e for e in COLOR_ESTADO if any(r["Nivel"] == e for r in regs)]
    estados += sorted(set(r["Nivel"] for r in regs) - set(estados))
    reglas = {(g, e): [r["Proyecto"] for r in regs if r["Actividad"] == g and r["Nivel"] == e] for g in grupos
              for e in estados}
    cats = [_partir(g, 26) for g in grupos]
    fig = go.Figure()
    for e in estados:
        _barra(fig, cats, [len(reglas[(g, e)]) for g in grupos], e, COLOR_ESTADO.get(e, GRIS), "reglas",
               customdata=["<br>".join(_e(_rot(x)) for x in reglas[(g, e)]) for g in grupos],
               hovertemplate="%{y}<br>" + _e(e) + ": %{x}<br>%{customdata}<extra></extra>")
    tot = [sum(len(reglas[(g, e)]) for e in estados) for g in grupos]
    _totales(fig, cats, tot)
    n = Counter(r["Nivel"] for r in regs)
    fuera = [g for g in grupos if all(r["Nivel"] == "Excluida" for r in regs if r["Actividad"] == g)]
    hallazgo = "De %d reglas del perímetro, %d excluyen y %d condicionan" % (
        len(regs), n.get("Excluida", 0), n.get("Condicionada", 0))
    if fuera:
        hallazgo += "; %s fuera por completo" % (("el grupo «%s» queda" % fuera[0]) if len(fuera) == 1 else
                                                  ("los grupos %s quedan" % _y(["«%s»" % g for g in fuera])))
    _maquetar(fig, "Perímetro de elegibilidad de CORSIA", hallazgo,
              "Número de reglas por grupo de actividades y por estado, en la matriz del Capítulo 1. El perímetro dice qué "
              "unidades pueden ofertarse en CORSIA; la demanda está en la gráfica anterior. El cursor muestra cada regla.",
              "número de reglas",
              alto=150 + 40 * len(grupos))
    fig.update_layout(barmode="stack", bargap=0.3)
    fig.update_xaxes(range=[0, max(tot) * 1.15], dtick=1)
    grande = [r for r in regs if re.search(r"(?i)renovables a red\s*>", r["Proyecto"]) and r["Nivel"] == "Excluida"]
    guia = _guia(
        "Las reglas de elegibilidad de la OACI para las unidades de CORSIA que recoge la matriz del Capítulo 1, "
        "agrupadas por tipo de actividad: elegibles, condicionadas, excluidas, y los requisitos y la compuerta que "
        "valen para todas.",
        "Cada barra cuenta las reglas de un grupo. La compuerta es la autorización del anfitrión con el ajuste "
        "correspondiente reportado en el informe bienal de transparencia; sin ella ninguna unidad es elegible.",
        "Son elegibles %s; las excluidas suman %d reglas y las condicionadas %d."
        % (_y_rotulos([_min(r["Proyecto"]) for r in regs if r["Nivel"] == "Elegible"]), n.get("Excluida", 0),
           n.get("Condicionada", 0)),
        ("La renovable conectada a la red con más de 15 MW queda fuera de CORSIA, de modo que la generación renovable a "
         "gran escala del Ecuador no tiene ese canal." if grande else
         "El perímetro define qué parte de la oferta del Ecuador puede llegar al canal de aviación."))
    tabla = _tabla(["Grupo de actividades"] + estados + ["Total"],
                   [[g] + [len(reglas[(g, e)]) for e in estados] + [t] for g, t in zip(grupos, tot)],
                   "Unidad: número de reglas.")
    tabla += _tabla(["Regla", "Grupo", "Estado"], [[_rot(r["Proyecto"]), r["Actividad"], r["Nivel"]] for r in regs],
                    "Reglas del perímetro.", resumen="Ver las %d reglas" % len(regs), texto=(0, 1, 2))
    return _figura("p05_perimetro", "Perímetro de CORSIA", fig, guia, tabla,
                   _fuente(D, "Capítulo 1, perímetro de elegibilidad de CORSIA (bloque DATA)"))


def registros_html(D):
    """Tabla con los registros de la matriz de demanda, en lugar del arbol del componente."""
    regs = D["demanda"]["registros"]
    orden_f = {f: i for i, f in enumerate(A6 + ["CORSIA"])}
    orden_c = {"Revelada": 0, "Anunciada": 1, "Perímetro": 2}
    filas = sorted(regs, key=lambda r: (orden_f.get(r["Fuente"], 9), orden_c.get(r["Categoria"], 9), r["Actividad"],
                                        str(r["Proyecto"])))
    tabla = _tabla(["Registro", "Comprador o canal", "Categoría", "Peldaño o estado", "Actividad", "País anfitrión",
                    "Créditos emitidos (t CO2e)"],
                   [[_rot(r["Proyecto"]), NOMBRE_FUENTE.get(r["Fuente"], r["Fuente"]), r["Categoria"], r["Nivel"],
                     _rot(r["Actividad"]), r["Pais"] or "", G.miles(float(r["Creditos"] or 0)) if r["Creditos"] else ""]
                    for r in filas], "Registros de la matriz de demanda; créditos emitidos en t CO2e.",
                   resumen="Ver los %d registros" % len(regs), texto=(0, 1, 2, 3, 4, 5))
    return ("<article class='figura' id='p00_registros' aria-labelledby='t-p00_registros'><h3 id='t-p00_registros'>"
            "Registros de la matriz de demanda</h3><p class='sub'>Cada registro con su comprador o canal, su categoría, "
            "su peldaño en la escalera (o su estado en el perímetro de CORSIA), su actividad, el país anfitrión y los "
            "créditos ya emitidos.</p>%s<p class='fuente'>%s</p></article>"
            % (tabla, _e(_fuente(D, "Capítulo 1, matriz de demanda (bloque DATA)"))))


# ----------------------------------------------------------------------------- 2. cartera agregada
def f_sector(D):
    K = D["cartera_agregada"]
    acts = K["por_actividad"]
    vers = K["veredictos"]
    sectores = sorted(OrderedDict.fromkeys(a["sector"] for a in acts),
                      key=lambda s: ORDEN_SECTOR.index(s) if s in ORDEN_SECTOR else 9)
    n = Counter()
    por_v = Counter()
    for a in acts:
        n[(a["sector"], a["veredicto"])] += a["iniciativas"]
        por_v[a["veredicto"]] += a["iniciativas"]
    cats = [SECTOR.get(s, s) for s in sectores]
    tot = [sum(n[(s, v)] for v in vers) for s in sectores]
    fig = go.Figure()
    for v in vers:
        _barra(fig, cats, [n[(s, v)] for s in sectores], v, COLOR_VEREDICTO.get(v, GRIS), "iniciativas")
    _totales(fig, cats, tot)
    T = K["totales"]
    hallazgo = "De %d iniciativas, %d son núcleo y %d condicionadas; %d son domésticas y %d se descartan" % (
        T["iniciativas"], por_v["Núcleo"], por_v["Condicionado"], por_v["Doméstico"], por_v["Descartar"])
    _maquetar(fig, "Cartera de la Segunda NDC por sector y veredicto", hallazgo,
              "Número de iniciativas: %d proyectos de la Segunda NDC y del Plan de Inversión del PLANMICC y %d actividades "
              "de cartera del Capítulo 2. El transporte se separa del sector energía como división analítica."
              % (T["proyectos"], T["actividades_de_cartera"]), "número de iniciativas", alto=360)
    fig.update_layout(barmode="stack", bargap=0.3)
    fig.update_xaxes(range=[0, max(tot) * 1.12])
    c = K.get("conciliacion_documento") or {}
    conc = ""
    if c.get("instancias_del_documento") and c.get("proyectos_con_ficha"):
        conc = (" El dictamen del documento cuenta %d instancias, %d de la Segunda NDC y %d del Plan de Inversión; la "
                "base con ficha tiene %d proyectos, y la diferencia son proyectos del Plan de Inversión sin ficha "
                "individual." % (c["instancias_del_documento"], c["segunda_ndc"], c["planmicc_en_el_documento"],
                                 c["proyectos_con_ficha"]))
    guia = _guia(
        "La cartera de mitigación del Capítulo 2 contada por sector y por veredicto. El veredicto es la aptitud de cada "
        "iniciativa para el Artículo 6: núcleo, condicionada, doméstica (aporta a la meta nacional y no se ofrece), "
        "descartada, pendiente de validar su ficha o habilitante (bien público sin crédito)." + conc,
        "Cada barra suma las iniciativas de un sector y cada color es un veredicto. La cartera se publica agregada, sin "
        "nombres, códigos ni potenciales por iniciativa.",
        "Por veredicto: %s." % _y(["%d %s" % (por_v[v], _veredicto(v, por_v[v])) for v in vers if por_v[v]]),
        "El número de iniciativas no mide toneladas: el volumen que podría ofrecerse se estima con el modelo en las "
        "secciones de resultados.")
    tabla = _tabla(["Sector"] + vers + ["Total"], [[c_] + [n[(s, v)] for v in vers] + [t]
                                                   for s, c_, t in zip(sectores, cats, tot)]
                   + [["Total"] + [por_v[v] for v in vers] + [sum(tot)]], "Unidad: número de iniciativas.")
    return _figura("p06_sector", "Cartera por sector", fig, guia, tabla,
                   _fuente(D, "Capítulo 2, cartera de la Segunda NDC agregada (bloque PORT)"))


def f_actividad(D):
    K = D["cartera_agregada"]
    vers = K["veredictos"]
    acts = sorted(K["por_actividad"], key=lambda a: (vers.index(a["veredicto"]) if a["veredicto"] in vers else 9,
                                                     -a["iniciativas"], a["actividad"]))
    etiqueta = lambda a: _partir(_rot(a["actividad"]), 30) + ("" if a["tipo"] == "proyecto" else " ◦")
    fig = go.Figure()
    for v in vers:
        xs = [a for a in acts if a["veredicto"] == v]
        if not xs:
            continue
        fig.add_bar(y=[etiqueta(a) for a in xs], x=[a["iniciativas"] for a in xs], orientation="h", name=v,
                    marker=dict(color=COLOR_VEREDICTO.get(v, GRIS), line=dict(color="white", width=1),
                                pattern=dict(shape=["" if a["tipo"] == "proyecto" else "/" for a in xs],
                                             fgcolor="white", size=6, solidity=0.25)),
                    text=[G.miles(a["iniciativas"]) for a in xs], textposition="outside", cliponaxis=False,
                    textfont=dict(size=12, color=TINTA),
                    customdata=[[SECTOR.get(a["sector"], a["sector"]), a["tipo"], _y(a["canales"])] for a in xs],
                    hovertemplate="%{y}<br>%{x} iniciativas · %{customdata[1]} · %{customdata[0]}<br>canal: "
                                  "%{customdata[2]}<extra>" + _e(v) + "</extra>")
    fig.update_yaxes(categoryorder="array", categoryarray=[etiqueta(a) for a in acts])
    mayores = sorted(acts, key=lambda a: -a["iniciativas"])[:3]
    nucleo = [a for a in acts if a["veredicto"] == "Núcleo"]
    hallazgo = ("Las actividades con más iniciativas son %s, y %s es núcleo; el núcleo reúne %d actividades con %d "
                "iniciativas" % (_y_rotulos(["%s (%d, %s)" % (_min(_sin_parentesis(a["actividad"])), a["iniciativas"],
                                                              _veredicto(a["veredicto"])) for a in mayores]),
                                 "ninguna" if not any(a["veredicto"] == "Núcleo" for a in mayores) else "alguna",
                                 len(nucleo), sum(a["iniciativas"] for a in nucleo)))
    _maquetar(fig, "Cartera de la Segunda NDC por actividad y veredicto", hallazgo,
              "Número de iniciativas por actividad, ordenadas por veredicto. Las barras rayadas, con ◦ en el rótulo, son "
              "actividades de cartera del Capítulo 2 sin proyecto; las lisas, proyectos.", "número de iniciativas",
              alto=170 + 30 * len(acts))
    fig.update_layout(barmode="overlay", bargap=0.25)
    fig.update_xaxes(range=[0, max(a["iniciativas"] for a in acts) * 1.12], dtick=1)
    guia = _guia(
        "Las %d actividades de la cartera del Capítulo 2 con su número de iniciativas y su veredicto. Es el árbol "
        "sector, veredicto y actividad del tablero de los Productos 1 a 4, agregado: no baja al nivel de proyecto."
        % len(acts),
        "Cada barra es una actividad y su color, el veredicto. El cursor muestra el sector, si son proyectos o una "
        "actividad de cartera y el canal de demanda con el que tiene afinidad.",
        "El núcleo lo forman %s." % _y_rotulos(["%s (%d)" % (_min(a["actividad"]), a["iniciativas"]) for a in nucleo]),
        ("Las actividades con más iniciativas quedan fuera de la oferta: la aptitud para el Artículo 6 la da el "
         "veredicto, y el volumen, el modelo." if not any(a["veredicto"] in ("Núcleo", "Condicionado") for a in mayores)
         else "La aptitud para el Artículo 6 la da el veredicto, y el volumen, el modelo."))
    tabla = _tabla(["Actividad", "Veredicto", "Sector", "Tipo", "Iniciativas", "Canal de demanda"],
                   [[_rot(a["actividad"]), a["veredicto"], SECTOR.get(a["sector"], a["sector"]), a["tipo"],
                     a["iniciativas"], _y(a["canales"])] for a in acts],
                   "Unidad: número de iniciativas.", texto=(0, 1, 2, 3, 5))
    return _figura("p07_actividad", "Cartera por actividad", fig, guia, tabla,
                   _fuente(D, "Capítulo 2, cartera de la Segunda NDC agregada (bloque PORT)"))


def f_tramo(D):
    K = D["cartera_agregada"]
    filas = K["por_tramo"]
    portafolios = list(OrderedDict.fromkeys(f["portafolio"] for f in filas))
    tramos = [t for t in COLOR_TRAMO if any(f["tramo"] == t for f in filas)]
    tramos += sorted(set(f["tramo"] for f in filas) - set(tramos))
    n = Counter()
    vers_de = {}
    for f in filas:
        n[(f["portafolio"], f["tramo"])] += f["iniciativas"]
        vers_de.setdefault((f["portafolio"], f["tramo"]), []).append("%s %d" % (f["veredicto"], f["iniciativas"]))
    cats = [_partir(p, 24) for p in portafolios]
    tot = [sum(n[(p, t)] for t in tramos) for p in portafolios]
    fig = go.Figure()
    for t in tramos:
        _barra(fig, cats, [n[(p, t)] for p in portafolios], t, COLOR_TRAMO.get(t, GRIS), "iniciativas",
               customdata=[" · ".join(vers_de.get((p, t), [])) for p in portafolios],
               hovertemplate="%{y}<br>" + _e(t) + ": %{x}<br>%{customdata}<extra></extra>")
    _totales(fig, cats, tot)
    ndc = portafolios[0]
    inc = n[(ndc, "Incondicional")]
    det = [p for p in portafolios[1:] if n[(p, "Por determinar")]]
    hallazgo = "%d de las %d iniciativas de la %s están en el piso incondicional y no se transfieren" % (
        inc, sum(n[(ndc, t)] for t in tramos), ndc)
    if det:
        hallazgo += "; %d del %s esperan el cruce con la NDC" % (n[(det[0], "Por determinar")], det[0])
    _maquetar(fig, "Cartera por tramo de la NDC", hallazgo,
              "Número de iniciativas por origen y por tramo de la Segunda NDC al que pertenece su reducción. El cursor "
              "muestra el veredicto de cada grupo.", "número de iniciativas", alto=340)
    fig.update_layout(barmode="stack", bargap=0.3)
    fig.update_xaxes(range=[0, max(tot) * 1.12])
    en_piso = sorted([f for f in filas if f["portafolio"] == ndc and f["tramo"] == "Incondicional"],
                     key=lambda f: -f["iniciativas"])
    guia = _guia(
        "A qué tramo de la Segunda NDC pertenece la reducción de cada iniciativa: el incondicional, que es base "
        "reservada y no se transfiere; el condicional, candidato a transferencia con prueba de no sobreventa; o ninguno "
        "todavía, cuando falta el cruce entre el Plan de Inversión del PLANMICC y la NDC.",
        "Cada barra es un origen de la cartera y cada color, un tramo. Las actividades de cartera del Capítulo 2 no "
        "tienen proyecto y quedan fuera de la NDC.",
        "En el piso incondicional hay %s." % _y(["%s %s" % (_pl(f["iniciativas"], "iniciativa", "iniciativas"),
                                                             _veredicto(f["veredicto"], f["iniciativas"]))
                                                   for f in en_piso]),
        "Una iniciativa en el piso incondicional no entra en la oferta aunque su veredicto sea favorable; el margen que "
        "deja la meta incondicional se calcula con el modelo en las secciones siguientes.")
    tabla = _tabla(["Origen"] + tramos + ["Total"], [[p] + [n[(p, t)] for t in tramos] + [s]
                                                     for p, s in zip(portafolios, tot)],
                   "Unidad: número de iniciativas.")
    tabla += _tabla(["Origen", "Veredicto", "Tramo", "Iniciativas"],
                    [[f["portafolio"], f["veredicto"], f["tramo"], f["iniciativas"]] for f in filas],
                    "Unidad: número de iniciativas.", resumen="Ver el tramo por veredicto", texto=(0, 1, 2))
    return _figura("p08_tramo", "Cartera por tramo de la NDC", fig, guia, tabla,
                   _fuente(D, "Capítulo 2, cartera de la Segunda NDC agregada (bloque PORT), bandera de piso"))


# ----------------------------------------------------------------------------- 3. remociones
def _nivel(texto):
    t = str(texto or "").strip()
    for k in ("Media-alta", "Baja-media", "Alta", "Media", "Baja"):
        if t.startswith(k):
            return k
    return ""


def _orden_cdr(D):
    regs = D["remociones"]["registros"]
    clases = [c for c in COLOR_CLASE if any(r["Categoria"] == c for r in regs)]
    clases += sorted(set(r["Categoria"] for r in regs) - set(clases))
    rango = lambda r: int(r["Rank"]) if str(r.get("Rank") or "").isdigit() else 99
    return sorted(regs, key=lambda r: (clases.index(r["Categoria"]), rango(r))), clases


def _trl(texto):
    m = re.search(r"TRL\s*(\d)\s*[–-]\s*(\d)", str(texto or ""))
    if m:
        return int(m.group(1)), int(m.group(2))
    m = re.search(r"TRL\s*(\d)", str(texto or ""))
    return (int(m.group(1)), int(m.group(1))) if m else (None, None)


def _transferibles(regs):
    return sum(1 for r in regs if str(r.get("Transferible")).strip().lower() in ("sí", "si"))


def f_filtros(D):
    regs, clases = _orden_cdr(D)
    fil = D["remociones"]["filtros"]
    cols = [("F1", False), ("F2", False), ("F4", True)]
    xs = ["%s %s" % (f, _partir(fil.get(f, f) + (" (baja es favorable)" if inv else ""), 18)) for f, inv in cols]
    etiqueta = lambda r: "%s<br><span style='font-size:11px;color:%s'>%s%s</span>" % (
        _partir(_rot(r["Actividad"]), 30), COLOR_CLASE.get(r["Categoria"], GRIS), _e(r["Categoria"]),
        (" · %s.º" % r["Rank"]) if str(r.get("Rank") or "").isdigit() else "")
    z, txt, hov = [], [], []
    for r in regs:
        fila_z, fila_t, fila_h = [], [], []
        for f, inv in cols:
            k = _nivel(r.get(f))
            fila_t.append(k or "s. d.")
            fila_h.append(_e(r.get(f) or "sin dato"))
            fila_z.append(None if not k else (ESCALA.index(k) + 1 if inv else 5 - ESCALA.index(k)))
        z.append(fila_z)
        txt.append(fila_t)
        hov.append(fila_h)
    escala = []
    for i, col in enumerate(COLOR_ESCALA):
        escala += [[i / 5.0, col], [(i + 1) / 5.0, col]]
    fig = go.Figure(go.Heatmap(z=z, x=xs, y=[etiqueta(r) for r in regs], text=txt, texttemplate="%{text}",
                               textfont=dict(size=12), customdata=hov, colorscale=escala, zmin=0.5, zmax=5.5,
                               showscale=False, xgap=3, ygap=3,
                               hovertemplate="%{y}<br>%{x}: %{customdata}<extra></extra>"))
    transf = _transferibles(regs)
    nuc = [r for r in regs if r["Categoria"] == clases[0]]
    _maquetar(fig, "Filtros de los arquetipos de remoción",
              "%s de los %d arquetipos es transferible como ITMO hoy; encabezan la lista los %d del %s: %s"
              % ("Ninguno" if not transf else str(transf), len(regs), len(nuc), clases[0].lower(),
                 _y_rotulos([_min(r["Actividad"]) for r in nuc])),
              "Nivel cualitativo de cada filtro del Capítulo 3 por arquetipo: verde favorable, gris intermedio, ocre y "
              "ladrillo desfavorable. En la intensidad mineral (F4) la escala se invierte: la intensidad baja es "
              "favorable. Los filtros F3 (adicionalidad) y F5 (pertinencia de la demanda) no ordenan la lista.",
              "", alto=110 + 54 * len(regs), horizontal=False)
    fig.update_xaxes(side="top", showgrid=False, ticks="", tickfont=dict(size=12, color=TINTA), title_text="")
    fig.update_yaxes(autorange="reversed", showgrid=False, ticks="", tickfont=dict(size=12, color=TINTA), title_text="")
    fig.update_layout(margin=dict(b=20))
    guia = _guia(
        "Los %d arquetipos de remoción del Capítulo 3 con su clasificación y el resultado de los tres filtros que "
        "ordenan la lista: %s, %s y %s." % (len(regs), _min(fil.get("F1", "F1")), _min(fil.get("F2", "F2")),
                                            _min(fil.get("F4", "F4"))),
        "Cada fila es un arquetipo, con su clasificación y, en el núcleo, su orden. El color resume el nivel del filtro; "
        "el cursor muestra el texto completo del dictamen.",
        "Por clasificación: %s. La durabilidad opera como condición de integridad de permanencia."
        % _y(["%d %s" % (sum(1 for r in regs if r["Categoria"] == c), c.lower()) for c in clases]),
        "Ninguna remoción se transfiere hoy: exige incorporarla al inventario nacional (INGEI), fijar su frontera "
        "frente al piso y aplicar el ajuste correspondiente." if not transf else
        "Solo %s se transfiere%s hoy; el resto exige pasar antes por el inventario nacional (INGEI)."
        % (_pl(transf, "arquetipo", "arquetipos"), "n" if transf > 1 else ""))
    tabla = _tabla(["Arquetipo", "Clasificación", "Orden en el núcleo", fil.get("F1", "F1"), fil.get("F2", "F2"),
                    fil.get("F4", "F4"), "Madurez", "Durabilidad", "Transferible hoy"],
                   [[_rot(r["Actividad"]), r["Categoria"], r["Rank"] if str(r.get("Rank") or "").isdigit() else "",
                     r.get("F1") or "", r.get("F2") or "", r.get("F4") or "", r.get("TRL") or "",
                     r.get("Durabilidad") or "", r.get("Transferible") or ""] for r in regs],
                   "Nivel cualitativo de cada filtro, madurez tecnológica y durabilidad.", texto=tuple(range(9)))
    return _figura("p09_filtros", "Filtros de las remociones", fig, guia, tabla,
                   _fuente(D, "Capítulo 3, dictamen de remociones con cinco filtros (bloque CDR)"))


def f_madurez(D):
    regs, clases = _orden_cdr(D)
    rotulo = lambda r: _partir(_rot(r["Actividad"]), 34)
    fig = go.Figure()
    for c in clases:
        xs = [r for r in regs if r["Categoria"] == c]
        lo_hi = [_trl(r.get("TRL")) for r in xs]
        fig.add_bar(y=[rotulo(r) for r in xs],
                    x=[(hi - lo) if hi is not None and hi > lo else 0.25 for lo, hi in lo_hi],
                    base=[lo if lo is not None else 0 for lo, _ in lo_hi], orientation="h", name=c,
                    marker=dict(color=COLOR_CLASE.get(c, GRIS), line=dict(color="white", width=1)),
                    text=["TRL %d-%d" % (lo, hi) if lo != hi else "TRL %d" % lo for lo, hi in lo_hi],
                    textposition="outside", cliponaxis=False, textfont=dict(size=12, color=TINTA),
                    customdata=[[r.get("TRL"), r.get("Durabilidad")] for r in xs],
                    hovertemplate="%{y}<br>%{customdata[0]}<br>durabilidad: %{customdata[1]}<extra>" + _e(c) + "</extra>")
    fig.update_yaxes(categoryorder="array", categoryarray=[rotulo(r) for r in regs])
    nuc = [_trl(r.get("TRL")) for r in regs if r["Categoria"] == clases[0]]
    fuera = [_trl(r.get("TRL")) for r in regs if r["Categoria"] == clases[-1]]
    _maquetar(fig, "Madurez tecnológica de los arquetipos de remoción",
              "Los arquetipos del %s van de TRL %d a %d; los de %s, de TRL %d a %d"
              % (clases[0].lower(), min(a for a, _ in nuc), max(b for _, b in nuc), clases[-1].lower(),
                 min(a for a, _ in fuera), max(b for _, b in fuera)),
              "Rango del nivel de madurez tecnológica (TRL, de 1 a 9) que el dictamen del Capítulo 3 asigna a cada "
              "arquetipo, con el color de su clasificación. El cursor muestra la durabilidad del almacenamiento.",
              "nivel de madurez tecnológica (TRL, 1 a 9)", alto=170 + 32 * len(regs))
    fig.update_layout(barmode="overlay", bargap=0.35)
    fig.update_xaxes(range=[0.5, 9.9], tickvals=list(range(1, 10)), tickformat="d")
    maximo = max(b for _, b in (_trl(r.get("TRL")) for r in regs))
    novel = all(str(r.get("TRL") or "").lower().startswith("novel") for r in regs)
    guia = _guia(
        "La madurez tecnológica de cada arquetipo, el cribado secuencial del dictamen de remociones.",
        "Cada barra va del nivel mínimo al máximo de madurez que declara el dictamen; un arquetipo con dos variantes "
        "toma el rango completo.",
        "%sNinguno pasa de TRL %d." % ("Todos los arquetipos se declaran novedosos. " if novel else "", maximo),
        "La madurez sitúa las remociones en el horizonte emergente desde 2031, como segunda línea de la cartera.")
    tabla = _tabla(["Arquetipo", "Clasificación", "TRL mínimo", "TRL máximo", "Madurez según el dictamen", "Durabilidad"],
                   [[_rot(r["Actividad"]), r["Categoria"], _trl(r.get("TRL"))[0], _trl(r.get("TRL"))[1], r.get("TRL"),
                     r.get("Durabilidad")] for r in regs],
                   "Unidad: nivel de madurez tecnológica (TRL, 1 a 9).", texto=(0, 1, 4, 5))
    return _figura("p10_madurez", "Madurez de las remociones", fig, guia, tabla,
                   _fuente(D, "Capítulo 3, dictamen de remociones (bloque CDR)"))


# ----------------------------------------------------------------------------- 4. puentes
def _color_canal(c):
    if c.get("revelada"):
        return "#0A5E51" if c["canal"].startswith("CORSIA") else VERDE
    return OCRE if "Anunciada" in c["canal"] else GRIS_CLARO


def _frase_canal(c):
    """Canal de demanda dentro de una frase."""
    nombre = c["canal"]
    if nombre.startswith("CORSIA") and c.get("revelada"):
        return "hacia cartas de autorización de CORSIA"
    if "Revelada" in nombre:
        return "hacia demanda revelada del Artículo 6"
    if "Anunciada" in nombre:
        return "hacia demanda anunciada del Artículo 6"
    if nombre.lower().startswith("sin canal"):
        return "sin canal actual"
    return "hacia %s" % nombre


def _sankey(etiquetas, colores, datos_nodo, columnas, enlaces, pad_px, alto_util, visible, nombre):
    """Sankey con los nodos fijos en el orden dado: columnas = [(x, [indices])], enlaces = [(origen, destino, valor,
    color, texto)]."""
    entra, sale = Counter(), Counter()
    for s, t, v, _, _ in enlaces:
        sale[s] += v
        entra[t] += v
    xs, ys = [0.5] * len(etiquetas), [0.5] * len(etiquetas)
    pad = pad_px / float(alto_util)
    for x, idx in columnas:
        for i, y in zip(idx, _columna([max(entra[i], sale[i]) for i in idx], pad)):
            xs[i], ys[i] = x, y
    return go.Sankey(arrangement="fixed", valueformat="d", visible=visible, name=nombre,
                     node=dict(label=etiquetas, color=colores, pad=pad_px, thickness=15, x=xs, y=ys,
                               customdata=datos_nodo, line=dict(color="white", width=0.5),
                               hovertemplate="%{label}<br>%{customdata}<extra></extra>"),
                     link=dict(source=[e[0] for e in enlaces], target=[e[1] for e in enlaces],
                               value=[e[2] for e in enlaces], color=[e[3] for e in enlaces],
                               customdata=[e[4] for e in enlaces],
                               hovertemplate="%{source.label} → %{target.label}<br>%{customdata}<extra></extra>"))


def _puentes(D):
    """Datos comunes de los dos Sankey de la cartera: veredictos, canales, actividades y colores."""
    K = D["cartera_agregada"]
    vers = [v for v in K["veredictos"] if any(a["veredicto"] == v for a in K["por_actividad"])]
    canales = [c for c in K["canales"] if any(c["canal"] in a["canales"] for a in K["por_actividad"])]
    n_ver, n_canal = Counter(), Counter()
    for a in K["por_actividad"]:
        n_ver[a["veredicto"]] += a["iniciativas"]
    for f in K["por_canal"]:
        n_canal[f["canal"]] += f["iniciativas"]
    acts = sorted([a for a in K["por_actividad"] if a["veredicto"] in vers],
                  key=lambda a: (vers.index(a["veredicto"]), -a["iniciativas"], a["actividad"]))
    nombres = [c["canal"] for c in canales]
    return dict(K=K, vers=vers, canales=canales, nombres=nombres, acts=acts, n_ver=n_ver, n_canal=n_canal,
                col_canal={c["canal"]: _color_canal(c) for c in canales},
                nodo_canal=["%s<br>%s" % (c["canal"], c["detalle"]) if c.get("detalle") else c["canal"] for c in canales],
                dn_ver=[_pl(n_ver[v], "iniciativa", "iniciativas") for v in vers],
                dn_canal=["%s con afinidad" % _pl(n_canal[c], "iniciativa", "iniciativas") for c in nombres],
                col_ver=[COLOR_VEREDICTO.get(v, GRIS) for v in vers])


def f_puentes(D):
    P = _puentes(D)
    K, vers, canales, nombres, acts = P["K"], P["vers"], P["canales"], P["nombres"], P["acts"]
    nv, alto = len(vers), 540
    enl = [(vers.index(f["veredicto"]), nv + nombres.index(f["canal"]), f["iniciativas"],
            _rgba(P["col_canal"][f["canal"]], 0.45), "%s con afinidad" % _pl(f["iniciativas"], "iniciativa", "iniciativas"))
           for f in K["por_canal"] if f["veredicto"] in vers]
    fig = go.Figure(_sankey(vers + P["nodo_canal"], P["col_ver"] + [P["col_canal"][c] for c in nombres],
                            P["dn_ver"] + P["dn_canal"],
                            [(0.001, list(range(nv))), (0.999, list(range(nv, nv + len(canales))))], enl, 18,
                            alto - 70, True, "Por veredicto"))
    reveladas = [c["canal"] for c in canales if c.get("revelada")]
    rev = [a for a in acts if any(c in reveladas for c in a["canales"])]
    anun = sum(f["iniciativas"] for f in K["por_canal"] if "Anunciada" in f["canal"])
    sin = sum(f["iniciativas"] for f in K["por_canal"] if f["canal"].lower().startswith("sin canal"))
    hallazgo = ("Solo %s %s afinidad con demanda revelada, y %s es núcleo: %s; el resto desemboca en demanda anunciada "
                "(%d iniciativas) o sin canal (%d)" % (
                    _pl(len(rev), "actividad", "actividades"), "tiene" if len(rev) == 1 else "tienen",
                    "ninguna" if not any(a["veredicto"] == "Núcleo" for a in rev) else "alguna",
                    _y(["%s (%s)" % (_min(_sin_parentesis(a["actividad"])), _veredicto(a["veredicto"])) for a in rev]),
                    anun, sin))
    _maquetar(fig, "Cartera de la Segunda NDC hacia los canales de demanda", hallazgo,
              "Ancho de cinta: número de iniciativas de cada veredicto con afinidad de tipo de actividad con cada canal del "
              "Capítulo 1; una actividad con afinidad a dos canales cuenta en ambos.", "", alto=alto, horizontal=False)
    guia = _guia(
        "La afinidad de cada veredicto de la cartera con las formas de demanda del Capítulo 1: Artículo 6 con demanda "
        "revelada o anunciada, CORSIA con carta de autorización, o ningún canal actual. La gráfica siguiente abre el "
        "mismo puente por actividad.",
        "Las cintas salen del veredicto hacia el canal. La afinidad es de tipo de actividad: una cinta hacia demanda "
        "revelada dice que ese tipo de actividad llegó a contrato o transferencia en otro país.",
        "Las afinidades por canal suman %s." % _y(["%s %s" % (_pl(P["n_canal"][c["canal"]], "iniciativa", "iniciativas"), _frase_canal(c))
                                  for c in canales]),
        "Ninguna iniciativa del Ecuador tiene demanda contratada: la demanda revelada exige los acuerdos bilaterales que "
        "el país todavía no firma, y el núcleo depende de demanda anunciada o de canales emergentes.")
    tabla = _tabla(["Veredicto"] + nombres + ["Iniciativas del veredicto"],
                   [[v] + [next((f["iniciativas"] for f in K["por_canal"] if f["veredicto"] == v and f["canal"] == c), 0)
                           for c in nombres] + [P["n_ver"][v]] for v in vers],
                   "Unidad: número de iniciativas con afinidad; una actividad con dos canales cuenta en ambos.")
    return _figura("p11_puentes", "Cartera hacia la demanda", fig, guia, tabla,
                   _fuente(D, "Capítulos 1 y 2, puentes entre la cartera agregada y los canales de demanda"))


def f_puentes_actividad(D):
    P = _puentes(D)
    vers, canales, nombres, acts = P["vers"], P["canales"], P["nombres"], P["acts"]
    nv, na = len(vers), len(acts)
    alto = 90 + 25 * na
    enl = []
    for i, a in enumerate(acts):        # la primera cinta pesa iniciativas x canales, como en el componente
        enl.append((vers.index(a["veredicto"]), nv + i, a["iniciativas"] * len(a["canales"]), _rgba(REGLA, 0.55),
                    _pl(a["iniciativas"], "iniciativa", "iniciativas")))
        for c in a["canales"]:
            enl.append((nv + i, nv + na + nombres.index(c), a["iniciativas"], _rgba(P["col_canal"][c], 0.45),
                        "%s con afinidad" % _pl(a["iniciativas"], "iniciativa", "iniciativas")))
    fig = go.Figure(_sankey(vers + [_rot(a["actividad"]) for a in acts] + P["nodo_canal"],
                            P["col_ver"] + [COLOR_VEREDICTO.get(a["veredicto"], GRIS) for a in acts]
                            + [P["col_canal"][c] for c in nombres],
                            P["dn_ver"] + ["%s · %s" % (_pl(a["iniciativas"], "iniciativa", "iniciativas"), a["tipo"])
                                           for a in acts] + P["dn_canal"],
                            [(0.001, list(range(nv))), (0.40, list(range(nv, nv + na))),
                             (0.999, list(range(nv + na, nv + na + len(canales))))], enl, 6, alto - 70, True,
                            "Por actividad"))
    nuc = [a for a in acts if a["veredicto"] == "Núcleo"]
    por = Counter()
    for a in nuc:
        for c in a["canales"]:
            por[c] += a["iniciativas"]
    hallazgo = "Las %d iniciativas del núcleo se reparten así: %s" % (
        sum(a["iniciativas"] for a in nuc),
        _y(["%d %s" % (por[c["canal"]], _frase_canal(c)) for c in canales if por[c["canal"]]]))
    con_canal = [a for a in nuc if any(not c.lower().startswith("sin canal") for c in a["canales"])]
    _maquetar(fig, "Cartera por actividad hacia los canales de demanda", hallazgo,
              "Las mismas cintas de la gráfica anterior, abiertas por actividad: veredicto, actividad y canal del Capítulo "
              "1. El cursor muestra el número de iniciativas y si son proyectos o una actividad de cartera.", "",
              alto=alto, horizontal=False)
    guia = _guia(
        "Cada actividad de la cartera entre su veredicto y su canal de demanda; es el puente del tablero de los Productos "
        "1 a 4 con todas las actividades abiertas.",
        "La cinta del veredicto a la actividad pesa las iniciativas por el número de canales con que la actividad tiene "
        "afinidad, para que el flujo se conserve; la cinta hacia el canal pesa las iniciativas.",
        "En el núcleo, las actividades con canal actual son %s; las demás del núcleo no tienen canal hoy."
        % _y_rotulos([_min(a["actividad"]) for a in con_canal]) if con_canal else
        "Ninguna actividad del núcleo tiene canal actual.",
        "")
    tabla = _tabla(["Actividad", "Veredicto", "Iniciativas", "Canal de demanda"],
                   [[_rot(a["actividad"]), a["veredicto"], a["iniciativas"], _y(a["canales"])] for a in acts],
                   "Unidad: número de iniciativas con afinidad.", texto=(0, 1, 3))
    return _figura("p11b_puentes_actividad", "Cartera por actividad hacia la demanda", fig, guia, tabla,
                   _fuente(D, "Capítulos 1 y 2, puentes entre la cartera agregada y los canales de demanda"))


def f_puentes_remociones(D):
    regs, clases = _orden_cdr(D)
    hor = list(OrderedDict.fromkeys(r["horizonte"] for r in regs))
    det = {r["horizonte"]: r.get("detalle") for r in regs}
    col_h = {h: (AZUL_CLARO if i == 0 else GRIS_CLARO) for i, h in enumerate(hor)}
    nc, nr = len(clases), len(regs)
    etiquetas = clases + [_rot(r["Actividad"]) for r in regs] + ["%s<br>%s" % (h, det[h]) if det.get(h) else h for h in hor]
    colores = ([COLOR_CLASE.get(c, GRIS) for c in clases] + [COLOR_CLASE.get(r["Categoria"], GRIS) for r in regs]
               + [col_h[h] for h in hor])
    datos = (["%s" % _pl(sum(1 for r in regs if r["Categoria"] == c), "arquetipo", "arquetipos") for c in clases]
             + [r["Categoria"] for r in regs] + [_pl(sum(1 for r in regs if r["horizonte"] == h), "arquetipo", "arquetipos")
                                                for h in hor])
    enl = []
    for i, r in enumerate(regs):
        enl.append((clases.index(r["Categoria"]), nc + i, 1, _rgba(REGLA, 0.55), "1 arquetipo"))
        enl.append((nc + i, nc + nr + hor.index(r["horizonte"]), 1, _rgba(col_h[r["horizonte"]], 0.5), "1 arquetipo"))
    alto = 480
    fig = go.Figure(_sankey(etiquetas, colores, datos, [(0.001, list(range(nc))), (0.45, list(range(nc, nc + nr))),
                                                        (0.999, list(range(nc + nr, nc + nr + len(hor))))],
                            enl, 9, alto - 100, True, "Remociones"))
    n_h = Counter(r["horizonte"] for r in regs)
    hallazgo = "Ningún arquetipo conecta con demanda formalizada: %d tienen horizonte %s" % (n_h[hor[0]], hor[0].lower())
    if len(hor) > 1:
        hallazgo += " y %d quedan %s" % (n_h[hor[-1]], hor[-1].lower())
    _maquetar(fig, "Arquetipos de remoción hacia su horizonte de mercado", hallazgo,
              "Clasificación, arquetipo y horizonte de mercado del Capítulo 3. Los arquetipos son prospectivos y no tienen "
              "proyecto en la cartera de la Segunda NDC; por eso van aparte de la cartera.", "", alto=alto,
              horizontal=False)
    guia = _guia(
        "El horizonte de mercado de cada arquetipo de remoción: %s." % _y(["%s (%s)" % (h.lower(), det[h]) if det.get(h)
                                                                            else h.lower() for h in hor]),
        "Las cintas van de la clasificación al arquetipo y de este a su horizonte; cada cinta es un arquetipo.",
        "Ningún arquetipo llega a la demanda del Artículo 6 ni a la demanda revelada de CORSIA, porque ninguno es "
        "transferible hoy: el ajuste correspondiente es una operación sobre el INGEI que todavía no incluye estas "
        "remociones.",
        "Mezclar las remociones con la cartera igualaría oferta documentada con oferta hipotética; su ruta empieza en el "
        "inventario nacional y llega al mercado después.")
    tabla = _tabla(["Arquetipo", "Clasificación", "Horizonte de mercado", "Detalle"],
                   [[_rot(r["Actividad"]), r["Categoria"], r["horizonte"], r.get("detalle") or ""] for r in regs],
                   "Unidad: arquetipos de remoción.", texto=(0, 1, 2, 3))
    return _figura("p12_puentes_remociones", "Remociones hacia su horizonte", fig, guia, tabla,
                   _fuente(D, "Capítulo 3, puentes entre los arquetipos de remoción y su horizonte (bloque CDR)"))


# ----------------------------------------------------------------------------- 5. cartera viable
def f_cartera_viable(D):
    S = D["sintesis"]
    niveles = S["niveles"]
    acts = S["actividades"]
    total = lambda a: a["proyectos"] + a["actividades_de_cartera"] + a["arquetipos"]
    etiqueta = lambda a: "%s<br>%s" % (_partir(_rot(a["actividad"]), 34), "<br>".join(
        "<span style='font-size:11px;color:%s'>%s</span>" % (GRIS, _e(x))
        for x in _partir(_rot(a["canal"]), 40).split("<br>")))

    def composicion(a):
        partes = []
        if a["proyectos"]:
            partes.append(_pl(a["proyectos"], "proyecto", "proyectos"))
        if a["actividades_de_cartera"]:
            partes.append(_pl(a["actividades_de_cartera"], "actividad de cartera", "actividades de cartera"))
        if a["arquetipos"]:
            partes.append(_pl(a["arquetipos"], "arquetipo de remoción", "arquetipos de remoción"))
        return _y(partes)
    fig = go.Figure()
    for i, nv in enumerate(niveles):
        xs = [a for a in acts if a["nivel"] == nv]
        fig.add_bar(y=[etiqueta(a) for a in xs], x=[total(a) for a in xs], orientation="h",
                    name=NIVEL_SINTESIS.get(nv, _rot(nv)),
                    marker=dict(color=COLOR_NIVELES[i % len(COLOR_NIVELES)], line=dict(color="white", width=1)),
                    text=[G.miles(total(a)) for a in xs], textposition="outside", cliponaxis=False,
                    textfont=dict(size=12, color=TINTA),
                    customdata=[[composicion(a), _e(_rot(a["ejes"])), _e(_rot(a["norma"]))] for a in xs],
                    hovertemplate="%{y}<br>%{customdata[0]}<br>%{customdata[1]}<br>norma: %{customdata[2]}<extra></extra>")
    fig.update_yaxes(categoryorder="array", categoryarray=[etiqueta(a) for a in acts])
    rev = [a for a in acts if "revelada" in a["canal"].lower()]
    cuenta = Counter(a["nivel"] for a in acts)
    if rev:
        sobre_rev = "solo %s %s afinidad con demanda revelada" % (_y(["«%s»" % _rot(a["actividad"]) for a in rev]),
                                                                  "tiene" if len(rev) == 1 else "tienen")
    else:
        sobre_rev = "ninguna tiene afinidad con demanda revelada"
    _maquetar(fig, "Cartera viable por actividad y canal de demanda",
              "%d actividades pasan todos los filtros: %s; %s"
              % (len(acts), _y(["%d de %s" % (cuenta[nv], _min(NIVEL_SINTESIS.get(nv, _rot(nv)))) for nv in niveles]),
                 sobre_rev),
              "Número de iniciativas de la cartera (proyectos o actividades de cartera) o de arquetipos de remoción que "
              "componen cada actividad de la síntesis del Capítulo 4; bajo el nombre va su canal de demanda.",
              "número de iniciativas o arquetipos", alto=170 + 64 * len(acts))
    fig.update_layout(barmode="overlay", bargap=0.3)
    fig.update_xaxes(range=[0, max(total(a) for a in acts) * 1.15], dtick=1)
    guia = _guia(
        "La cartera que pasa el marco común del Capítulo 4, con reducciones del Capítulo 2 y remociones del Capítulo 3: "
        "lo firme, lo adicional, lo de baja huella mineral y la remoción de alto valor.",
        "Cada barra es una actividad y su color, el nivel de la síntesis. La aptitud (el veredicto) y el canal de "
        "demanda son ejes distintos: casi todo desemboca en demanda anunciada o sin canal, porque el Ecuador no está "
        "en las listas de socios bilaterales.",
        "Las reducciones del núcleo son %s; las remociones forman la segunda línea. El Capítulo 4 describe esta cartera "
        "como delgada, propia, defendible y posextractivista." % _y_rotulos([_min(a["actividad"]) for a in acts
                                                                              if a["nivel"] == niveles[0]]),
        "Sin acuerdos bilaterales que le den acceso a la demanda, la cartera viable seguirá sin comprador: el siguiente "
        "paso es diplomático y, en remociones, también contable.")
    tabla = _tabla(["Actividad", "Nivel", "Proyectos", "Actividades de cartera", "Arquetipos de remoción",
                    "Canal de demanda", "Ejes del marco común", "Norma"],
                   [[_rot(a["actividad"]), NIVEL_SINTESIS.get(a["nivel"], _rot(a["nivel"])), a["proyectos"],
                     a["actividades_de_cartera"], a["arquetipos"], _rot(a["canal"]), _rot(a["ejes"]), _rot(a["norma"])]
                    for a in acts], "Unidad: número de iniciativas o de arquetipos.", texto=(0, 1, 5, 6, 7))
    return _figura("p13_cartera_viable", "Cartera viable", fig, guia, tabla,
                   _fuente(D, "Capítulo 4, síntesis de la cartera con los conteos de los Capítulos 2 y 3"))


# ----------------------------------------------------------------------------- bloques de seccion
def _ficha(ident, color, titulo, tipo, textos, cifras, fuente):
    """Ficha en el estilo de los bloques de lectura del tablero (explicacion._ficha), con la fuente al pie."""
    import explicacion as X
    dl = [(t, _e(c)) for t, c in textos]
    der = [X._seccion("Cifras", X._cifras([(_e(et), _e(v), _e(n)) for et, v, n in cifras]))]
    return "<div class='ab es es-lectura'>%s%s</div>" % (
        X._ficha(ident, [color], titulo, [], tipo, "", dl, der),
        "<p class='ab-fuente'>%s</p>" % _e(fuente) if fuente else "")


def _bloque_demanda(D):
    M = D["demanda"]["macroestructura"]
    regs = D["demanda"]["registros"]
    a6 = [r for r in regs if r["Fuente"] in A6]
    rev = sum(1 for r in a6 if r["Categoria"] == "Revelada")
    loa = sum(1 for r in regs if r["Fuente"] == "CORSIA" and r["Categoria"] == "Revelada")
    pct = lambda s: re.sub(r"\s*%", " %", s)
    cifras = [(pct(c["descripcion"].replace(" vs. ", " frente a ")), c["cifra"], "") for c in M["cifras"]]
    fecha = _mes(M.get("fecha"))
    textos = [
        ("Recorrido", "El tablero sigue la cadena de los Productos 1 a 4 y del modelo: quién compra y qué compra, qué "
                      "puede ofrecer el Ecuador, qué actividades pasan todos los filtros y, con el modelo de la Segunda "
                      "NDC, cuánto cabe transferir sin arriesgar la meta incondicional."),
        ("Qué significa", "%sa demanda de mitigación es %s. Es un mercado de compradores: dos adquirientes, el Japón con "
                          "el JCM y Suiza, explican la mayor parte de los proyectos operativos. Las gráficas de esta "
                          "sección cuentan los %d registros de la matriz de demanda del Capítulo 1, un subconjunto curado "
                          "de esos proyectos: %d bilaterales del Artículo 6, de los cuales %d tienen demanda revelada, y "
                          "%d del canal CORSIA, con %d cartas de autorización."
         % (("A %s, l" % fecha) if fecha else "L", re.sub(r"^demanda\s+", "", M["titulo"]),
            len(regs), len(a6), rev, len(regs) - len(a6), loa)),
        ("Criterio de demanda revelada", "En el Artículo 6.2 bilateral la demanda se revela con el contrato de compra "
                                         "(N4) o la transferencia del ITMO (N5); la carta de autorización (N3) es oferta "
                                         "autorizada del país anfitrión. En CORSIA el umbral es la carta de autorización, "
                                         "porque el comprador es la obligación de cancelación de las aerolíneas. Los dos "
                                         "conteos de demanda revelada no se suman."),
    ]
    return _ficha("productos-demanda", VERDE, "Macroestructura de la demanda", "Capítulo 1", textos, cifras,
                  "Fuente de las cifras: %s, según el Capítulo 1 del tablero de los Productos 1 a 4%s."
                  % (M.get("fuente", ""), (", con datos a %s" % fecha) if fecha else ""))


def _bloque_integridad(D):
    K = D["cartera_agregada"]
    regs = D["demanda"]["registros"]
    a6 = [r for r in regs if r["Fuente"] in A6]
    ndc = [f for f in K["por_tramo"] if f["portafolio"] == "Segunda NDC"]
    inc = sum(f["iniciativas"] for f in ndc if f["tramo"] == "Incondicional")
    cdr = D["remociones"]["registros"]
    cifras = [("Iniciativas de la Segunda NDC en el piso incondicional",
               "%d de %d" % (inc, sum(f["iniciativas"] for f in ndc)), "base reservada, no se transfiere"),
              ("Remociones transferibles como ITMO hoy", "%d de %d" % (_transferibles(cdr), len(cdr)),
               "exigen pasar antes por el INGEI"),
              ("Registros bilaterales con demanda revelada",
               "%d de %d" % (sum(1 for r in a6 if r["Categoria"] == "Revelada"), len(a6)), "contrato o transferencia"),
              ("Cartas de autorización para CORSIA",
               str(sum(1 for r in regs if r["Fuente"] == "CORSIA" and r["Categoria"] == "Revelada")), "en otros países")]
    textos = [
        ("Qué significa", "La cartera viable enfrenta tres condiciones de integridad y una brecha institucional. El piso "
                          "incondicional de la NDC es base reservada y ninguna de sus toneladas se transfiere. El ajuste "
                          "correspondiente es una operación contable sobre el inventario nacional (INGEI) que evita el "
                          "doble conteo; en remociones exige antes incorporar el biochar al inventario. La tercera "
                          "condición es no sobrevender: no ofrecer lo que el mercado no compra, como la renovable a red de "
                          "gran escala, el transporte masivo doméstico o el hidrógeno verde."),
        ("Brecha institucional", "El Ecuador no está en las listas de socios bilaterales ni del JCM. Llegar a la demanda "
                                 "revelada exige construir esos acuerdos; el siguiente paso es diplomático y, en "
                                 "remociones, también contable."),
    ]
    return _ficha("productos-integridad", AZUL, "Condiciones de integridad", "Capítulo 4", textos, cifras,
                  _fuente(D, "Capítulo 4, condiciones de integridad, con los conteos de los Capítulos 1 a 3"))


def bloques(sec):
    """(antes, despues): bloques HTML [(ancla, titulo, html)] que abren y cierran cada seccion de los Productos 1 a 4."""
    D = _cargar()
    if D is None:
        return [], []
    if sec == "Demanda de mitigación":
        return [("b-demanda", "Macroestructura de la demanda", _bloque_demanda(D))], \
               [("p00_registros", "Registros de la matriz de demanda", registros_html(D))]
    if sec == "Cartera viable y condiciones de integridad":
        return [("b-integridad", "Condiciones de integridad", _bloque_integridad(D))], []
    return [], []


FUNCIONES = [f_compradores, f_escalera, f_actividades, f_corsia, f_perimetro, f_sector, f_actividad, f_tramo,
             f_filtros, f_madurez, f_puentes, f_puentes_actividad, f_puentes_remociones,
             f_cartera_viable]


def figuras():
    """{gid: {indice, fig, guia, tabla, fuente}} de las secciones de los Productos 1 a 4; vacio sin datos_productos."""
    D = _cargar()
    if D is None:
        return {}
    out = OrderedDict()
    for f in FUNCIONES:
        x = f(D)
        out[x["gid"]] = x
    return out


def pie_html():
    """Linea del pie del tablero con el origen de las secciones de los Productos 1 a 4."""
    D = _cargar()
    if D is None:
        return ""
    o = D["demanda"]["origen"]
    return ("<p>Fuente de las secciones de demanda, cartera, remociones, puentes y cartera viable: tablero de los "
            "Productos 1 a 4 (versión %s, archivo %s, md5 %s), extraído con Energy/Art6_motor/extraer_productos.py a "
            "Energy/Art6_motor/datos_productos. La cartera de la Segunda NDC se presenta agregada, como número de "
            "iniciativas, sin nombres, códigos ni potenciales por iniciativa.</p>" % (_e(o["version"]), _e(o["archivo"]),
                                                                                       _e(o["md5"])))
