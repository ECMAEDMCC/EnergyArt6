# -*- coding: utf-8 -*-
"""Graficas dinamicas (Plotly) de los escenarios de Articulo 6 para B3_Visualizador_Art6.ipynb.

Cada funcion devuelve una figura con titulo que enuncia la conclusion, subtitulo con lo que se
muestra y sus unidades, informacion al pasar el cursor y, donde ayuda, selectores de escenario,
de regla o de precio. generar() las arma todas y guarda una copia PNG en B2_Output_Art6/graficas
para el informe Word.

Los datos vienen de analizar.resultados(), que recalcula el analisis si cambio alguna salida de B1 (Executables).
Las graficas muestran los escenarios con solucion de la corrida, cada uno por su papel: las dos referencias
de la NDC, la escalera de escenarios de Articulo 6 y las pruebas de estres y de sensibilidad sobre
cada escalon. Si un escenario no esta en la corrida, se omite. Todo titulo que afirma un resultado se
arma con la cifra de la corrida y su condicion.

Paletas validadas para daltonismo (skill dataviz, validate_palette.js): referencia condicional
#3B6FD8, primer escalon #0E8F6E y segundo #D97A1F; la referencia incondicional va en gris con trazo
discontinuo.
"""
import math
from collections import Counter

import re

import pandas as pd
import plotly.graph_objects as go

import analizar
import comun as C
import configuracion as K

# ----------------------------------------------------------------------------- estilo
TINTA, TINTA_2, REJILLA = "#1F2937", "#4B5563", "#ECEFEE"
LETRA = "Fira Sans, Segoe UI, Arial, sans-serif"
ROJO_META = "#B42318"
NEUTRO = "#9CA3AF"
INC = ("#6B7280", "dash")               # referencia incondicional
CON = ("#4E5D7E", "solid")              # referencia condicional (azul pizarra del proyecto)
ESCALONES = ["#0E7C6B", "#C08A2E", "#2F5597", "#9A3B34", "#6B4C9A"]   # verde petroleo, ocre, ladrillo, azul, violeta
SOMBRA = ("Segunda NDC %d-%d sombreada, con la ventana de transacciones %d-%d más oscura"
          % (C.MARCO[0], C.MARCO[-1], C.VENTANA[0], C.VENTANA[-1]))
TRAZOS = ["dash", "dot", "dashdot", "longdash", "longdashdot"]
FUENTE = ("Fuente: Modelo Climate Lead Group (ECU_NDC, rama art6-escenarios), salidas de B1 de cada escenario en "
          "Executables y escenarios de B1_Scenario_Config.xlsx.")
NOTA_STOELE = ("Círculo abierto: año con emisiones subestimadas, en que el modelo pasa energía por STOELE por falta de "
               "potencia.")
SUPUESTO_PRUDENTE = "los demás sectores cumplen solo su tramo incondicional"
REGLA_C = "Si los demás sectores cumplen su condicional"
REGLA_P = "Si los demás sectores cumplen solo su incondicional"
CONFIG = {"displaylogo": False, "responsive": True,
          "toImageButtonOptions": {"format": "png", "scale": 2},
          "modeBarButtonsToRemove": ["lasso2d", "select2d", "autoScale2d"]}


def miles(v, dec=0):
    if v is None or (isinstance(v, float) and math.isnan(v)):
        return "s. d."
    return ("{:,.%df}" % dec).format(v).replace(",", " ").replace(".", ",") if dec else "{:,.0f}".format(v).replace(",", " ")


def _minus(s):
    """Primera letra en minuscula, salvo que empiece por una sigla (CCOFF, NDC)."""
    s = str(s)
    return s[:1].lower() + s[1:] if len(s) > 1 and s[1:2].islower() else s


def _roles():
    return analizar.resultados()["roles"]


def _orden(T):
    return T.get("orden") or T["escalera"]


def estilo_escenario(cod):
    """(nombre, color, trazo) de cualquier escenario de la corrida segun su papel. El nombre sale de
    Art6_Escenarios o de la hoja Scenarios; el color, del escalon de origen; el trazo, del estado."""
    T = _roles()
    nombre = T["nombre"].get(cod, cod)
    orden = _orden(T)
    if cod == T["inc"]:
        return nombre, INC[0], INC[1]
    if cod == T["con"]:
        return nombre, CON[0], CON[1]
    if cod in orden:
        return nombre, ESCALONES[orden.index(cod) % len(ESCALONES)], "solid"
    sufijos = T.get("orden_estados") or [d["sufijo"] for d in T["estados"]]
    for d in T["estados"]:
        for fam, c in d["miembros"].items():
            if c == cod:
                col = ESCALONES[orden.index(fam) % len(ESCALONES)] if fam in orden else NEUTRO
                nombre = "%s · %s" % (T["nombre"].get(fam, fam), _rot(d))     # rotulo de presentacion del estado
                return nombre, col, TRAZOS[sufijos.index(d["sufijo"]) % len(TRAZOS)]
    return nombre, NEUTRO, "solid"


def _envolver(texto, ancho=150):
    """Parte un subtitulo largo en lineas de unos `ancho` caracteres con <br>, porque Plotly no ajusta
    el titulo al ancho de la figura y lo corta por la derecha."""
    lineas, actual = [], ""
    for palabra in str(texto).split(" "):
        if actual and len(actual) + len(palabra) + 1 > ancho:
            lineas.append(actual)
            actual = palabra
        else:
            actual = (actual + " " + palabra).strip()
    if actual:
        lineas.append(actual)
    return "<br>".join(lineas)


def maquetar(fig, titular, subtitulo, ytitulo=None, alto=520, xtitulo="Año"):
    if any(getattr(tr, "meta", None) == "stoele" for tr in fig.data) and NOTA_STOELE not in str(subtitulo):
        subtitulo = ("%s %s" % (subtitulo, NOTA_STOELE)).strip()
    sub = _envolver(subtitulo)
    n_sub = sub.count("<br>") + 1
    nombres = [tr.name for tr in fig.data if tr.showlegend is not False and tr.name]
    filas_leyenda = max(1, int(math.ceil(sum(len(n) * 6.5 + 46 for n in nombres) / 820.0)))   # ancho util de unos 820 px
    fig.update_layout(
        template="plotly_white", height=alto + 18 * (n_sub - 1) + 24 * (filas_leyenda - 1),
        font=dict(family=LETRA, size=13, color=TINTA),
        title=dict(text="<b>%s</b><br><span style='font-size:13px;color:%s'>%s</span>" % (titular, TINTA_2, sub),
                   x=0.0, xanchor="left", y=0.975, yanchor="top", font=dict(size=18)),
        margin=dict(l=64, r=30, t=88 + 20 * n_sub, b=62 + 24 * filas_leyenda),
        legend=dict(orientation="h", yanchor="top", y=-0.15, xanchor="left", x=0, font=dict(size=12),
                    title_text="", itemwidth=30, tracegroupgap=4),
        hovermode="x unified",
        hoverlabel=dict(bgcolor="white", bordercolor="#CBD5E1", font=dict(size=12, family=LETRA, color=TINTA)),
        paper_bgcolor="white", plot_bgcolor="white",
    )
    fig.update_xaxes(showgrid=False, linecolor="#C9D1CE", ticks="outside", tickcolor="#C9D1CE", title_text=xtitulo,
                     title_font=dict(size=12, color=TINTA_2), tickfont=dict(size=12))
    fig.update_yaxes(gridcolor=REJILLA, gridwidth=1, zeroline=False, showline=False, title_text=ytitulo,
                     title_font=dict(size=12, color=TINTA_2), tickfont=dict(size=12),
                     separatethousands=True, tickformat=",.0f")
    fig.update_layout(separators=", ")
    if xtitulo == "Año":                     # marco de la Segunda NDC y ventana de transacciones, iguales en toda serie
        fig.add_vrect(x0=C.MARCO[0] - 0.5, x1=C.MARCO[-1] + 0.5, fillcolor="#F3F4F6", opacity=0.6,
                      layer="below", line_width=0, annotation_text="Segunda NDC %d-%d" % (C.MARCO[0], C.MARCO[-1]),
                      annotation_position="top left", annotation_font=dict(size=11, color=TINTA_2))
        fig.add_vrect(x0=C.VENTANA[0] - 0.5, x1=C.VENTANA[-1] + 0.5, fillcolor="#E5E7EB", opacity=0.6,
                      layer="below", line_width=0, annotation_text="transacciones %d-%d" % (C.VENTANA[0], C.VENTANA[-1]),
                      annotation_position="top left", annotation_font=dict(size=11, color=TINTA_2))
    return fig


def subestimados(cod):
    """Anios en que el escenario pasa energia por STOELE con la termica de la red en su tope (K15b): le falta
    potencia y sus emisiones de ese anio quedan subestimadas (analizar: suficiencia)."""
    s = (analizar.resultados().get("suficiencia") or {}).get(cod) or {}
    return {int(a) for a in s.get("anios_con_STOELE", [])}


def marcar_subestimados(tr, cod, col):
    """Circulo abierto en los anios subestimados de cod, con aviso al pasar el cursor."""
    sub = subestimados(cod)
    xs = [int(a) for a in tr.x] if tr.x is not None else []
    if not sub or not any(a in sub for a in xs):
        return tr
    tr.mode = "lines+markers"
    tr.marker = dict(size=[11 if a in sub else 0 for a in xs], symbol="circle-open", color=col,
                     line=dict(width=2.2, color=col))
    tr.customdata = [" · año subestimado (STOELE)" if a in sub else "" for a in xs]
    tr.hovertemplate = (tr.hovertemplate or "%{y:,.0f}<extra></extra>").replace("<extra>", "%{customdata}<extra>", 1)
    tr.meta = "stoele"
    return tr


def linea(cod, x, y, ancho=None, grupo=None, mostrar=True, fin=True):
    nom, col, trazo = estilo_escenario(cod)
    if ancho is None:
        T = _roles()
        ancho = 2.2 if cod in (T["inc"], T["con"]) else 3.0 if cod in T["escalera"] else 2.4
    tr = go.Scatter(x=x, y=y, name=nom, mode="lines", line=dict(color=col, dash=trazo, width=ancho),
                    legendgroup=grupo or cod, visible=mostrar,
                    hovertemplate="%{y:,.0f} kt<extra>" + nom + "</extra>")
    return marcar_subestimados(tr, cod, col)


def etiquetas_finales(fig, idx):
    """Etiqueta directa al final de cada linea visible del grupo (nombre y ultimo valor), con
    separacion minima para que no se encimen. El texto va en tinta; el punto lleva el color."""
    trazas = [fig.data[i] for i in idx if fig.data[i].type == "scatter" and fig.data[i].fill in (None, "none")
              and fig.data[i].line.width and fig.data[i].showlegend is not False and fig.data[i].name
              and fig.data[i].legendgroup != "comun"]
    if not trazas:
        return []
    puntos = sorted(((float(tr.y[-1]), tr) for tr in trazas), key=lambda p: p[0])
    ys = [y for i in idx if fig.data[i].y is not None for y in list(fig.data[i].y)
          if y is not None]                                   # rango del eje, con la trayectoria comun
    m = fig.layout.margin
    alto_util = (fig.layout.height or 520) - ((m.t if m and m.t else 90) + (m.b if m and m.b else 100))
    paso = (max(ys) - min(ys)) * (16.0 / max(alto_util, 120.0)) or 1.0
    anots, previo = [], None
    for y, tr in puntos:
        yy = y if previo is None or y - previo >= paso else previo + paso
        previo = yy
        anots.append(dict(x=tr.x[-1], y=yy, xref="x", yref="y", xanchor="left", xshift=8, showarrow=False,
                          align="left", font=dict(size=11, color=TINTA),
                          text="<span style='color:%s'>●</span> %s · %s" % (tr.line.color, nombre_corto(tr), miles(y))))
    return anots


def nombre_corto(tr):
    """Nombre breve para la etiqueta final: referencia, codigo del escalon o escalon y estado."""
    T = _roles()
    g = tr.legendgroup or ""
    if g == T["inc"]:
        return "Incondicional"
    if g == T["con"]:
        return "Condicional"
    if g in T["escalera"]:
        return g
    for d in T["estados"]:
        for fam, c in d["miembros"].items():
            if c == g:
                return c
    return tr.name


def botones_visibilidad(grupos, n_trazas, etiquetas, y=1.16, fig=None):
    """grupos: lista de listas de indices visibles por boton. Con fig, cada boton cambia tambien
    las etiquetas finales de las lineas."""
    bot = []
    base = [a.to_plotly_json() for a in fig.layout.annotations] if fig is not None else []
    for idx, et in zip(grupos, etiquetas):
        vis = [i in idx for i in range(n_trazas)]
        if fig is not None:
            bot.append(dict(label=et, method="update",
                            args=[{"visible": vis}, {"annotations": base + etiquetas_finales(fig, idx)}]))
        else:
            bot.append(dict(label=et, method="update", args=[{"visible": vis}]))
    if fig is not None and grupos:
        fig.update_layout(annotations=base + etiquetas_finales(fig, grupos[0]))
        fig.update_layout(margin=dict(r=200))
    if len(bot) < 2:
        return []
    return [dict(type="buttons", direction="right", x=0, xanchor="left", y=y, yanchor="bottom",
                 buttons=bot, showactive=True, bgcolor="#F3F4F6", bordercolor="#D1D5DB",
                 font=dict(size=12), pad=dict(r=6, t=2))]


def sin_datos(texto, subtitulo=""):
    """Figura vacia con el motivo, para cuando la corrida no trae los escenarios que la grafica usa."""
    fig = go.Figure()
    maquetar(fig, texto, subtitulo or "La gráfica se completa cuando la corrida de B1 trae esos escenarios con solución.", None,
             alto=320, xtitulo="")
    fig.update_xaxes(visible=False)
    fig.update_yaxes(visible=False)
    return fig


# ----------------------------------------------------------------------------- datos
class Datos:
    def __init__(self):
        self.R = analizar.resultados()          # recalcula si alguna salida de B1 es posterior al ultimo analisis
        T = self.T = self.R["roles"]
        self.inc, self.con = T["inc"], T["con"]
        self.esc = list(T["escalera"])          # escenarios de Articulo 6 de la corrida, del primero al ultimo
        self.base = T["base"]
        self.riesgos = [d for d in T["estados"] if d["grupo"] == "Riesgo"]
        self.sens = [d for d in T["estados"] if d["grupo"] == "Sensibilidad"]
        self.contra = [d for d in T["estados"] if d["grupo"] == "Contrafactual"]   # escenarios sin las actividades del escalon
        self.capas = [c for c in self.esc if c in self.R.get("capas", {})]
        self.top = self.R["potencial_art6"].get("ejecuta")
        self.em = pd.DataFrame(self.R["emisiones_kt"], index=C.ANIOS)
        self.sub = pd.read_csv(C.TABLAS / "emisiones_subsector_kt.csv")
        self.gen = pd.read_csv(C.TABLAS / "generacion_familia.csv")
        self.cap = pd.read_csv(C.TABLAS / "capacidad_familia.csv")
        self.ernc = pd.DataFrame(self.R["ernc_pct"], index=C.ANIOS)
        self.nac = pd.DataFrame(self.R["nacional"], index=C.ANIOS)
        self.hr = pd.DataFrame(self.R["headroom"])
        self.vol = pd.DataFrame(self.R["volumenes"])
        self.peso = pd.DataFrame(self.R["peso_energia"])

    def nombre(self, c):
        return self.T["nombre"].get(c, c)

    def hr35(self, cod, regla="condicional"):
        if cod is None:
            return float("nan")
        x = self.hr[(self.hr.escenario == cod) & (self.hr.regla == regla)]
        return float(x["2035"].iloc[0]) if len(x) else float("nan")

    def miembro(self, fam, d):
        return d["miembros"].get(fam) if d and fam else None

    def contrafactual(self, c):
        """Codigo del contrafactual del escalon c (el mismo sistema sin sus actividades), si la corrida lo trae."""
        return next((self.miembro(c, d) for d in self.contra if self.miembro(c, d) in self.em), None)

    def combinado(self, fam=None):
        """La prueba de estres que combina otras (la de mas componentes) y, si ninguna combina, la de
        menor margen prudente de 2035 sobre fam (por omision, el escalon que el pais ejecuta)."""
        fam = fam or self.top
        con_fam = [d for d in self.riesgos if self.miembro(fam, d)]
        if not con_fam:
            return None
        comb = [d for d in con_fam if len(d["componentes"]) >= 2]
        if comb:
            return max(comb, key=lambda d: len(d["componentes"]))
        return min(con_fam, key=lambda d: self.hr35(self.miembro(fam, d), "prudente"))

    def capa(self, c):
        return self.R["capas"][c]

    def sobre(self, c):
        """'el condicional' o 'el A': la base de la capa del escenario c, para las frases."""
        b = self.base.get(c)
        return "el condicional" if b == self.con else "el %s" % b


def _con_nombre(d):
    """«Con el año seco severo»: el nombre del estado dentro de una frase."""
    return "Con %s" % (d.get("frase") or _minus(d["nombre"]))


def _rot(d):
    """Rotulo de presentacion del estado (configuracion.ROTULOS): «Año seco severo (cota)»."""
    return d.get("rotulo") or K.rotulo(d.get("sufijo"), d.get("nombre") or d.get("etiqueta"))


def _el(nombre):
    """«la NDC condicional», «el A» o «el escenario «Ambición integral»»."""
    n = str(nombre)
    if n.startswith("NDC"):
        return "la " + n
    return ("el " + n) if len(n) <= 4 else "el escenario «%s»" % n


def _o(xs):
    """«A, B o C»: enumeracion disyuntiva."""
    xs = [str(x) for x in xs if x]
    return "" if not xs else xs[0] if len(xs) == 1 else ", ".join(xs[:-1]) + " o " + xs[-1]


def _frase(D, etiqueta):
    """Como se nombra un riesgo dentro de una frase («la salida de Coca Codo»), a partir de su etiqueta."""
    for d in D.riesgos + D.sens:
        if (_minus(d["etiqueta"]) == _minus(etiqueta) or d.get("nombre") == etiqueta
                or _minus(_rot(d)) == _minus(etiqueta)):
            return d.get("frase") or _minus(etiqueta)
    return _minus(etiqueta)


# ----------------------------------------------------------------------------- 0. potencial de Articulo 6
def _franja(x, abajo, arriba, color, nombre, visible, mostrar_leyenda=True):
    """Dos trazas que sombrean entre 'abajo' y 'arriba' (la segunda rellena hasta la primera)."""
    t1 = go.Scatter(x=x, y=abajo, mode="lines", line=dict(width=0), hoverinfo="skip", showlegend=False,
                    visible=visible)
    t2 = go.Scatter(x=x, y=arriba, mode="lines", line=dict(width=0), fill="tonexty", fillcolor=color,
                    name=nombre, hoverinfo="skip", showlegend=mostrar_leyenda, visible=visible)
    return [t1, t2]


def f_itmos_area(D):
    em = D.em
    v = list(C.VENTANA)
    x = list(range(2020, 2036))
    inc, con, top = D.inc, D.con, D.top
    estados = [(None, "Sistema intacto")]
    if top:
        estados += [(d, _rot(d)) for d in D.riesgos if D.miembro(top, d)]
    fig, grupos, etiquetas = go.Figure(), [], []
    for d, etiqueta in estados:
        b = top if d is None else D.miembro(top, d)
        g = []
        vis = not grupos
        ii = [em[inc][a] for a in v]
        cc = [em[con][a] for a in v]
        for t in _franja(v, cc, ii, "rgba(217,122,31,0.22)",
                         "Tramo condicional: transferible solo renunciando a la meta condicional", vis, True):
            g.append(len(fig.data)); fig.add_trace(t)
        if b:
            bb = [em[b][a] for a in v]
            piso = [min(c, y) for c, y in zip(cc, bb)]
            techo = [max(c, y) for c, y in zip(cc, bb)]
            for t in _franja(v, piso, cc, "rgba(14,143,110,0.35)",
                             "ITMO adicionales a la NDC: no consumen ninguna meta", vis, True):
                g.append(len(fig.data)); fig.add_trace(t)
            for t in _franja(v, cc, techo, "rgba(180,35,24,0.30)",
                             "Emisiones por encima del condicional: el potencial desaparece", vis, True):
                g.append(len(fig.data)); fig.add_trace(t)
        for c in [inc, con] + [c if d is None else D.miembro(c, d) for c in D.esc]:
            if c and c in em:
                g.append(len(fig.data))
                tr = linea(c, x, [em[c][a] for a in x], mostrar=vis)
                tr.showlegend = True
                fig.add_trace(tr)
        grupos.append(g)
        etiquetas.append(etiqueta)
    tramo = round(sum(em[inc][a] - em[con][a] for a in v), 1)
    if top:
        adic = round(sum(max(0.0, em[con][a] - em[top][a]) for a in v), 1)     # redondeo de las tablas del analisis
        titular = ("Potencial de Artículo 6, 2031-2035: %s kt adicionales a la NDC y %s kt del tramo condicional"
                   % (miles(adic), miles(tramo)))
        subt = ("Emisiones del sector energía (kt CO2e). Verde: lo que %s reduce bajo el condicional. Ámbar: el tramo "
                "condicional.%s" % (_el(D.nombre(top)), " Con los botones de riesgo, el rojo muestra cuánto se pierde."
                                    if len(grupos) > 1 else ""))
    else:
        titular = "Tramo condicional 2031-2035: %s kt; la corrida no trae escenarios de Artículo 6" % miles(tramo)
        subt = "Emisiones del sector energía (kt CO2e). Ámbar: el tramo condicional."
    maquetar(fig, titular, subt, "kt CO2e", alto=600)
    fig.update_layout(updatemenus=botones_visibilidad(grupos, len(fig.data), etiquetas, fig=fig),
                      margin=dict(t=140, b=150), legend=dict(y=-0.14))
    fig.update_xaxes(range=[2020, 2035.5])
    return fig


def _lineas_de(D, c):
    """Lineas de Art6_Adicionalidad que el escenario c lleva en su capa del modelo: las de su
    escenario_art6 que no entran en la oferta con su volumen declarado."""
    usadas = {x for xs in D.R.get("grupos_de_lineas", {}).values() for x in xs}
    return [x for x in K.hoja("Adicionalidad")
            if str(x.get("escenario_art6") or "").strip() == c and x["codigo"] not in usadas]


def _etiqueta_bloque(D, nombre, clave):
    """Rotulo del bloque de oferta para quien compra, con el veredicto de la estrategia de actores
    (Art6_Adicionalidad) de las lineas que lo forman."""
    grupos = D.R.get("grupos_de_lineas", {})
    ad = {x["codigo"]: x for x in K.hoja("Adicionalidad")}
    if clave == "firme":
        xs = [ad[c] for c in grupos.get("firme", []) if c in ad]
        return "%s: %s" % (C.enumerar([str(x["linea"]) for x in xs]),
                           "única línea con adicionalidad firme" if len(xs) == 1 else "adicionalidad firme")
    if clave == "declarado":
        n = len(grupos.get("condicionadas_declaradas", []))
        return "Condicionadas con potencial declarado (%d %s)" % (n, "línea" if n == 1 else "líneas")
    if clave.startswith("capa:"):
        c = clave.split(":", 1)[1]
        cuenta = Counter(str(x.get("veredicto_compradores") or "sin veredicto") for x in _lineas_de(D, c))
        partes = [("%d %s" % (n, "línea" if n == 1 else "líneas") if i == 0 else "%d" % n)
                  + (" sin veredicto" if v == "sin veredicto" else " «%s»" % v)
                  for i, (v, n) in enumerate(cuenta.most_common())]
        return "Capa del %s (modelo)%s" % (c, (": " + C.enumerar(partes)) if partes else "")
    return nombre


def _rayado(D, clave):
    """Capas del modelo cuyas lineas la estrategia de actores clasifico en su mayoria como «Descartar»."""
    if not clave.startswith("capa:"):
        return False
    cuenta = Counter(str(x.get("veredicto_compradores") or "") for x in _lineas_de(D, clave.split(":", 1)[1]))
    return bool(cuenta) and cuenta.get("Descartar", 0) > sum(cuenta.values()) / 2.0


def f_potencial(D):
    """Dos paneles: de que se compone la oferta (por nivel de adicionalidad) y cuanto de ella cabe en
    el margen de la meta incondicional con el sistema intacto y bajo cada riesgo."""
    from plotly.subplots import make_subplots
    P = D.R["potencial_art6"]
    t = pd.DataFrame(P["tabla"])
    if t.empty:
        return sin_datos("La corrida no trae escenarios de Artículo 6: no hay oferta que medir")
    bloques = P["bloques"]
    color = {"firme": "#0E8F6E", "por demostrar": "#7FC8A9", "por demostrar fuera NDC": "#D97A1F"}
    tono = {"declarado": "#B9E2D0"}
    intacto = t[(t.regla == "condicional") & (t.sufijo == "")].iloc[0]
    oferta = float(intacto.oferta_total)
    fig = make_subplots(rows=1, cols=2, column_widths=[0.40, 0.60], horizontal_spacing=0.09,
                        subplot_titles=("De qué se compone la oferta", "Cuánto cabe en el margen, según el riesgo"))
    hay_rayado = False
    for nom, nivel, clave in bloques:
        v = float(intacto[nom])
        et = _etiqueta_bloque(D, nom, clave)
        raya = _rayado(D, clave)
        hay_rayado |= raya
        patron = dict(shape="/", fgcolor="rgba(255,255,255,0.75)", size=7, solidity=0.35) if raya else None
        oscuro = clave in ("firme", "capa:B")
        fig.add_bar(x=[v], y=["Oferta 2031-2035"], orientation="h", name=et,
                    marker_color=tono.get(clave, color.get(nivel, NEUTRO)), marker_pattern=patron,
                    text=(miles(v) + " kt") if v >= 0.05 * oferta else "", textposition="inside", insidetextanchor="middle",
                    textfont=dict(size=12, color="white" if oscuro else TINTA), cliponaxis=False,
                    hovertemplate="%{x:,.0f} kt<extra>" + et + "</extra>", showlegend=True, row=1, col=1)
    n1 = len(fig.data)
    grupos = []
    for regla in ("condicional", "prudente"):
        s = t[t.regla == regla]
        cols = ["#0E8F6E" if v >= oferta - 0.5 else ("#C08A2E" if v > 0.5 else ROJO_META) for v in s.transferible_sin_incumplir]
        g = list(range(n1)) + [len(fig.data)]
        rot = {"-" + d["sufijo"]: _rot(d) for d in D.riesgos + D.sens}
        fig.add_bar(x=[rot.get(sf, e) for sf, e in zip(s.sufijo, s.estado)], y=list(s.transferible_sin_incumplir), marker_color=cols,
                    name="Transferible sin incumplir la meta incondicional", showlegend=False,
                    text=[miles(v) + " kt" for v in s.transferible_sin_incumplir], textposition="outside",
                    textfont=dict(size=12, color=TINTA), cliponaxis=False, visible=(regla == "condicional"),
                    hovertemplate="%{y:,.0f} kt transferibles<extra>%{x}</extra>", row=1, col=2)
        grupos.append(g)
    fig.add_hline(y=oferta, line=dict(color=TINTA, width=1.4, dash="dash"), row=1, col=2,
                  annotation_text="oferta: %s kt" % miles(oferta), annotation_position="bottom right",
                  annotation_font=dict(size=11, color=TINTA_2))
    col_sin = next((c for c in t.columns if str(c).startswith("Sin adicionalidad")), None)
    fuera = ""
    if col_sin is not None and float(intacto[col_sin]) > 0:
        quien = str(col_sin).split(":", 1)[-1].replace("(declarado)", "").strip()
        fuera = " Fuera de la oferta quedan %s kt sin adicionalidad (%s)." % (miles(float(intacto[col_sin])), quien)
    firme_nom = next((n for n, _, clave in bloques if clave == "firme"), None)
    firme = float(intacto[firme_nom]) if firme_nom else 0.0
    ad = {x["codigo"]: x for x in K.hoja("Adicionalidad")}
    nombres_firmes = C.enumerar([str(ad[c]["linea"]) for c in D.R.get("grupos_de_lineas", {}).get("firme", []) if c in ad])
    comb = D.combinado()
    peor = ""
    if comb is not None:
        s = t[(t.sufijo == "-" + comb["sufijo"]) & (t.regla == "prudente")]
        if len(s):
            peor = "; con %s y la regla prudente caben %s kt" % (comb.get("frase") or _minus(comb["etiqueta"]),
                                                                 miles(float(s.transferible_sin_incumplir.iloc[0])))
    if firme > 0:
        titular = ("De %s kt ofertables en 2031-2035, %s%s kt tienen adicionalidad firme (%s)%s"
                   % (miles(oferta), "solo " if firme < oferta - 0.5 else "", miles(firme), nombres_firmes, peor))
    else:
        titular = "De %s kt ofertables en 2031-2035, ninguno tiene adicionalidad firme%s" % (miles(oferta), peor)
    maquetar(fig, titular,
             "Izquierda: la oferta por nivel de adicionalidad (kt CO2e)%s.%s Derecha: lo que cabe en el margen de la "
             "meta incondicional con el sistema intacto y bajo cada riesgo; la línea punteada es la oferta completa."
             % ("; rayado: líneas que los compradores descartan" if hay_rayado else "", fuera),
             None, alto=560, xtitulo="")
    fig.update_xaxes(title_text="kt CO2e", tickformat=",.0f", row=1, col=1)
    fig.update_yaxes(showticklabels=False, row=1, col=1)
    fig.update_yaxes(title_text="kt CO2e 2031-2035", row=1, col=2)
    fig.update_layout(barmode="stack", bargap=0.35, hovermode="closest", margin=dict(t=150, b=190), height=660,
                      legend=dict(orientation="v", x=0, y=-0.14, yanchor="top", xanchor="left"),
                      updatemenus=botones_visibilidad(grupos, len(fig.data), [REGLA_C, REGLA_P]))
    return fig


# ----------------------------------------------------------------------------- 1. escenarios en energia
def _vistas_riesgo(D, con_sensibilidad=True):
    """Vistas de los botones: escenarios, riesgos sobre cada escalon y, si hay, sensibilidades."""
    contras = [D.contrafactual(c) for c in D.esc if D.contrafactual(c)]
    vistas = [("Escenarios", [D.inc, D.con] + D.esc + contras)]
    for c in D.esc:
        ms = [D.miembro(c, d) for d in D.riesgos if D.miembro(c, d)]
        if ms:
            vistas.append(("Riesgos sobre %s" % c, [D.con, c] + ms))
    for c in D.esc:
        x = D.contrafactual(c)
        if x:
            vistas.append(("Atribuible por retiro, %s" % c, [D.con, x, c]))
    if con_sensibilidad:
        for i, d in enumerate(D.sens):
            cods = [D.con] + [x for c in D.esc if D.miembro(c, d) for x in (c, D.miembro(c, d))]
            if len(cods) > 1:
                vistas.append(("Riesgo de operación" if len(D.sens) == 1 else "Riesgo de operación %d" % (i + 1), cods))
    return vistas


def f_energia_escenarios(D):
    em = D.em.loc[2015:]
    vistas = _vistas_riesgo(D)
    todos = [c for c in vistas[0][1] if c in em and c != D.con]
    y0 = next((a for a in em.index if any(abs(em[c][a] - em[D.con][a]) > 1.0 for c in todos)), em.index[-1])
    fig, idx, grupos = go.Figure(), {}, []
    comun = go.Scatter(x=em.index[em.index < y0], y=em[D.con].loc[:y0 - 1], name="Trayectoria común (historia y calibración)",
                       mode="lines", line=dict(color=NEUTRO, width=2.4), legendgroup="comun",
                       hovertemplate="%{y:,.0f} kt<extra>trayectoria común</extra>")
    fig.add_trace(comun)
    fijas = [0]
    inv = {int(k): v for k, v in ((D.R.get("inventario") or {}).get("energia") or {}).items()}
    if inv:                                  # linea observada del inventario: base del balance de emisiones
        xs = sorted(a for a in inv if a >= em.index[0])
        fig.add_trace(go.Scatter(x=xs, y=[inv[a] for a in xs], name="INGEI, sector energía (inventario observado)",
                                 mode="lines+markers", line=dict(color="#111827", width=1.6), marker=dict(size=5),
                                 legendgroup="comun", hovertemplate="%{y:,.0f} kt<extra>inventario</extra>"))
        fijas.append(len(fig.data) - 1)
    for _, cods in vistas:
        g = list(fijas)
        for c in cods:
            if c not in em:
                continue
            if c not in idx:
                idx[c] = len(fig.data)
                fig.add_trace(linea(c, em.index[em.index >= y0 - 1], em[c].loc[y0 - 1:], mostrar=(c in vistas[0][1])))
            g.append(idx[c])
        grupos.append(g)
    n35 = D.em[D.con][2035]
    vals = [D.em[c][2035] for c in D.esc]
    if D.esc and len(D.esc) > 1 and max(vals) - min(vals) < 1.0:
        titular = ("En 2035 %s coinciden en %s kt de emisiones de energía, %s kt bajo el condicional"
                   % (C.enumerar(D.esc), miles(vals[0]), miles(n35 - vals[0])))
    elif D.esc:
        titular = ("En 2035 %s llega%s a %s kt de emisiones de energía, frente a %s kt del condicional"
                   % (C.enumerar(D.esc), "n" if len(D.esc) > 1 else "",
                      C.enumerar([miles(v) for v in vals]), miles(n35)))
    else:
        titular = "En 2035 el condicional llega a %s kt de emisiones de energía" % miles(n35)
    maquetar(fig, titular,
             "Emisiones del sector energía (kt CO2e). El incondicional llega a %s kt.%s"
             % (miles(D.em[D.inc][2035]), " Use los botones para ver los riesgos." if len(vistas) > 1 else ""),
             "kt CO2e")
    fig.update_layout(updatemenus=botones_visibilidad(grupos, len(fig.data), [v[0] for v in vistas], fig=fig),
                      margin=dict(t=135))
    fig.update_xaxes(range=[2015, 2035])
    return fig


def f_reduccion_anual(D):
    anios = list(range(2026, 2036))
    if not D.capas:
        return sin_datos("La corrida no trae escenarios de Artículo 6 junto con su base: no hay capas que mostrar")
    fig = go.Figure()
    serie = {}
    for c in D.capas:
        b = D.base[c]
        y = [D.em[b][a] - D.em[c][a] for a in anios]
        serie[c] = y
        nom = "%s sobre %s%s" % (D.nombre(c), D.sobre(c), " (paquete fuera de la NDC)" if D.capa(c)["fuera_ndc"] else "")
        corto = "%s sobre %s" % (c, "el condicional" if b == D.con else b)
        fig.add_bar(x=anios, y=y, name=nom, marker_color=estilo_escenario(c)[1],
                    hovertemplate="%{y:,.0f} kt<extra>" + corto + "</extra>")
    for c in D.capas:                       # aporte atribuible por retiro: contrafactual menos escenario
        x = D.contrafactual(c)
        if x:
            ya = [D.em[x][a] - D.em[c][a] for a in anios]
            fig.add_scatter(x=anios, y=ya, mode="lines+markers",
                            name="Aporte atribuible por retiro: %s menos %s" % (x, c),
                            line=dict(color=estilo_escenario(c)[1], width=2, dash="dot"),
                            hovertemplate="%{y:,.0f} kt<extra>atribuible " + c + "</extra>")
    u = D.capas[-1]
    y = serie[u]
    pico, fin = anios[y.index(max(y))], anios[-1]
    if max(y) > 0:
        cierre = ("en %d aporta %s kt" % (fin, miles(y[-1])) if y[-1] >= 0 else
                  "en %d emite %s kt más que %s" % (fin, miles(-y[-1]), D.sobre(u)))
        titular = ("La capa %s llega a su máximo en %d, con %s kt, y %s" % (u, pico, miles(max(y)), cierre)
                   if pico != fin else "La capa %s crece hasta %d, cuando aporta %s kt" % (u, fin, miles(y[-1])))
    else:
        titular = "La capa %s no reduce emisiones en 2026-2035: en %d emite %s kt más que %s" % (
            u, fin, miles(-y[-1]), D.sobre(u))
    b_u = D.base[u]
    desp = D.R["termica_desplazable_GWh"].get(b_u)
    nota_contra = (" Línea punteada: aporte atribuible por retiro, emisiones del contrafactual menos las del "
                   "escenario." if any(D.contrafactual(c) for c in D.capas) else "")
    quien_d = "del condicional" if b_u == D.con else "del %s" % b_u
    if not desp:
        td = ""
    elif pico != fin:
        td = " Térmica desplazable %s: %s GWh en %d y %s GWh en %d." % (
            quien_d, miles(desp[C.IDX[pico]]), pico, miles(desp[C.IDX[fin]]), fin)
    else:
        td = " Térmica desplazable %s en %d: %s GWh." % (quien_d, fin, miles(desp[C.IDX[fin]]))
    maquetar(fig, titular,
             "Reducción anual de emisiones del sector energía (kt CO2e). " + SOMBRA + "." + td + nota_contra, "kt CO2e")
    fig.update_layout(barmode="group", bargap=0.25, bargroupgap=0.08)
    sumas = "<br>".join("Suma %d-%d: %s" % (p[0], p[-1], " · ".join(
        "%s %s kt" % (c, miles(sum(v for a, v in zip(anios, serie[c]) if a in p))) for c in D.capas))
        for p in (C.MARCO, C.VENTANA))
    fig.add_annotation(x=C.MARCO[0] - 0.4, y=0.86, xref="x", yref="paper", xanchor="left", yanchor="top",
                       showarrow=False, align="left", font=dict(size=12, color=TINTA), bgcolor="rgba(255,255,255,.85)",
                       text=sumas)
    fig.add_hline(y=0, line_color="#9CA3AF", line_width=1)
    return fig


def _solo_generacion(D):
    """True si todas las palancas de la escalera (filas de Electrical que B1 cambia) son de centrales."""
    tecs = {t for c in D.esc for _, t in K.filas_palanca(c)}
    return bool(tecs) and all(C.familia(t) for t in tecs)


def f_emisiones_generacion(D):
    s = D.sub[D.sub.subsector == "Generación eléctrica"].pivot_table(index="anio", columns="escenario", values="kt")
    s = s.loc[2015:]
    vistas = _vistas_riesgo(D, con_sensibilidad=False)
    fig, idx, grupos = go.Figure(), {}, []
    for _, cods in vistas:
        g = []
        for c in cods:
            if c in s:
                if c not in idx:
                    idx[c] = len(fig.data)
                    fig.add_trace(linea(c, s.index, s[c], mostrar=(c in vistas[0][1])))
                g.append(idx[c])
        grupos.append(g)
    top = D.top
    quedan = C.enumerar(D.esc)
    if top and top in s:
        red = {a: s[D.con][a] - s[top][a] for a in range(2026, 2036)}
        pico = max(red, key=red.get)
        cierre = "en 2035 %s queda%s en %s kt" % (quedan, "n" if len(D.esc) > 1 else "",
                                                 C.enumerar([miles(s[c][2035]) for c in D.esc if c in s]))
        titular = (("El %s reduce más la generación eléctrica en %d, %s kt bajo el condicional; %s"
                    % (top, pico, miles(red[pico]), cierre)) if red[pico] > 0 else
                   ("El %s no reduce las emisiones de la generación bajo el condicional; %s" % (top, cierre)))
    else:
        titular = "Las emisiones de la generación del condicional llegan a %s kt en 2035" % miles(s[D.con][2035])
    alcance = (", el único subsector donde actúan las palancas de %s" % quedan) if D.esc and _solo_generacion(D) else ""
    botones = [v[0].replace("Riesgos sobre ", "") for v in vistas[1:] if v[0].startswith("Riesgos sobre ")]
    retiro = any(v[0].startswith("Atribuible por retiro") for v in vistas[1:])
    maquetar(fig, titular,
             "Emisiones de las centrales eléctricas (CO2e_PP, kt CO2e, Output.csv de cada escenario)%s.%s%s" % (
                 alcance, (" Botones: riesgos sobre %s" % _o(botones)) if botones else "",
                 (" y aporte atribuible por retiro." if botones else " Botones: aporte atribuible por retiro.") if retiro
                 else ("." if botones else "")), "kt CO2e")
    fig.update_layout(updatemenus=botones_visibilidad(grupos, len(fig.data), [v[0] for v in vistas], fig=fig),
                      margin=dict(t=135))
    return fig


def f_subsectores(D):
    orden = [x for x in C.SUBSECTORES]
    col = dict(zip(C.SUBSECTORES, ["#e34948", "#2a78d6", "#4a3aa7", "#1baf7a", "#eda100", "#008300",
                                   "#eb6834", "#e87ba4"]))
    escs = [D.inc, D.con] + D.esc
    fig, grupos = go.Figure(), []
    for e in escs:
        p = D.sub[D.sub.escenario == e].pivot_table(index="anio", columns="subsector", values="kt", aggfunc="sum")
        g = []
        for s in orden:
            if s in p and p[s].abs().sum() > 0:
                g.append(len(fig.data))
                fig.add_trace(go.Scatter(x=p.index, y=p[s], name=s, stackgroup="uno", mode="lines",
                                         line=dict(width=0.8, color=col[s]), fillcolor=col[s],
                                         legendgroup=s, showlegend=True, visible=(e == escs[0]),
                                         hovertemplate="%{y:,.0f} kt<extra>" + s + "</extra>"))
        grupos.append(g)
    s35 = D.sub[(D.sub.escenario == D.con) & (D.sub.anio == 2035)].groupby("subsector")["kt"].sum()
    s35 = s35.sort_values(ascending=False)
    if len(s35) >= 2:
        titular = "%s y %s suman el %s %% de las emisiones de energía del condicional en 2035" % (
            s35.index[0], s35.index[1].lower(), miles(100.0 * s35.iloc[:2].sum() / s35.sum()))
    else:
        titular = "Emisiones del sector energía del condicional en 2035 por subsector"
    if D.top:
        dif = (D.sub[(D.sub.escenario == D.con) & D.sub.anio.isin(C.MARCO)].groupby("subsector")["kt"].sum()
               - D.sub[(D.sub.escenario == D.top) & D.sub.anio.isin(C.MARCO)].groupby("subsector")["kt"].sum())
        if dif.sum() > 0.5:
            titular += "; el %s %% de lo que reduce el %s en 2026-2035 ocurre en la generación eléctrica" % (
                miles(100.0 * dif.get("Generación eléctrica", 0.0) / dif.sum()), D.top)
        else:
            titular += "; el %s no reduce las emisiones del sector frente al condicional en 2026-2035" % D.top
    maquetar(fig, titular,
             "Emisiones del sector energía por subsector (kt CO2e). Elija el escenario con los botones.", "kt CO2e")
    fig.update_layout(updatemenus=botones_visibilidad(grupos, len(fig.data), [D.nombre(e) for e in escs]),
                      margin=dict(t=135))
    return fig


# ----------------------------------------------------------------------------- 2. mezcla electrica
def f_mezcla(D, tabla, campo, unidad, que):
    fams = [f for f, _, _ in C.FAMILIAS]
    escs = [D.inc, D.con] + D.esc
    fig, grupos = go.Figure(), []
    for e in escs:
        p = tabla[tabla.escenario == e].pivot_table(index="anio", columns="familia", values=campo, aggfunc="sum")
        g = []
        for f in fams:
            if f in p and p[f].abs().sum() > 1e-6:
                g.append(len(fig.data))
                fig.add_trace(go.Scatter(x=p.index, y=p[f], name=f, stackgroup="uno", mode="lines",
                                         line=dict(width=0.8, color=C.COLORES_FAMILIA[f]), fillcolor=C.COLORES_FAMILIA[f],
                                         legendgroup=f, showlegend=True, visible=(e == escs[0]),
                                         hovertemplate="%{y:,.0f} " + unidad + "<extra>" + f + "</extra>"))
        grupos.append(g)
    n = len(fig.data)
    bot_esc = [dict(label=D.nombre(e), method="restyle", args=[{"visible": [i in g for i in range(n)]}])
               for e, g in zip(escs, grupos)]
    bot_modo = [dict(label=unidad, method="update", args=[{"groupnorm": ""}, {"yaxis.title.text": unidad,
                                                                              "yaxis.ticksuffix": ""}]),
                dict(label="% del total", method="update", args=[{"groupnorm": "percent"},
                                                                 {"yaxis.title.text": "% del total",
                                                                  "yaxis.ticksuffix": " %"}])]
    menus = [dict(type="buttons", direction="right", x=0, xanchor="left", y=1.16, yanchor="bottom",
                  buttons=bot_esc, bgcolor="#F3F4F6", bordercolor="#D1D5DB", font=dict(size=12)),
             dict(type="buttons", direction="right", x=1, xanchor="right", y=1.16, yanchor="bottom",
                  buttons=bot_modo, bgcolor="#F3F4F6", bordercolor="#D1D5DB", font=dict(size=12))]
    return fig, menus


def f_generacion(D):
    fig, menus = f_mezcla(D, D.gen, "GWh", "GWh", "generación")
    g = D.R["generacion_2035_GWh"]
    tot = lambda e: sum(g[e].values())
    hid = lambda e: 100 * g[e]["Hidroeléctrica"] / tot(e) if tot(e) else 0.0
    maquetar(fig, ("La hidroelectricidad sostiene la matriz: %.0f %% de la generación del condicional en 2035"
                   if hid(D.con) >= 50 else
                   "La hidroelectricidad aporta el %.0f %% de la generación del condicional en 2035") % hid(D.con),
             "Generación eléctrica por tipo de planta. Botones: escenario (izquierda) y valor absoluto o "
             "participación (derecha).", "GWh")
    fig.update_layout(updatemenus=menus, margin=dict(t=135))
    return fig


def f_capacidad(D):
    fig, menus = f_mezcla(D, D.cap, "MW", "MW", "capacidad")
    ve = lambda e: float(D.cap[(D.cap.escenario == e) & (D.cap.anio == 2035)
                               & D.cap.familia.isin(["Solar", "Eólica"])]["MW"].sum())
    if D.esc:
        titular = ("La capacidad solar y eólica llega en 2035 a %s, frente a %s MW del condicional"
                   % (C.enumerar(["%s MW en el %s" % (miles(ve(c)), c) for c in D.esc]), miles(ve(D.con))))
    else:
        titular = "La capacidad solar y eólica del condicional llega a %s MW en 2035" % miles(ve(D.con))
    maquetar(fig, titular, "Capacidad instalada por tipo de planta. Botones: escenario y valor absoluto o participación.",
             "MW")
    fig.update_layout(updatemenus=menus, margin=dict(t=135))
    return fig


def f_ernc(D):
    er = D.ernc.loc[2020:]
    fig = go.Figure([linea(c, er.index, er[c]) for c in [D.inc, D.con] + D.esc if c in er])
    fig.update_traces(hovertemplate="%{y:.1f} %")
    pct = lambda v: ("%.1f %%" % v).replace(".", ",")
    if D.esc:
        titular = "La ERNC llega a %s en 2035, frente a %s del condicional" % (
            C.enumerar(["%s en el %s" % (pct(er[c][2035]), c) for c in D.esc]), pct(er[D.con][2035]))
    else:
        titular = "La ERNC del condicional llega a %s en 2035" % pct(er[D.con][2035])
    maquetar(fig, titular,
             "Participación de solar, eólica, geotermia y biomasa en la generación (%). La ERNC excluye toda la "
             "hidroelectricidad.", "% de la generación")
    fig.update_yaxes(ticksuffix=" %", tickformat=".0f")
    return fig


def f_escalera(D):
    """Reducción acumulada frente al condicional en la ventana de transacciones, escalón por escalón: cada
    barra apila las capas de los escalones que contiene y la cifra superior dice cuánto añade el último."""
    if not D.capas:
        return sin_datos("La corrida no trae escenarios de Artículo 6 junto con su base: no hay escalera que mostrar")
    V = C.VENTANA
    capa = {c: sum(D.em[D.base[c]][a] - D.em[c][a] for a in V) for c in D.capas}
    x = [D.nombre(D.con)] + [D.nombre(c) for c in D.capas]
    fig = go.Figure()
    for j, c in enumerate(D.capas):
        y = [0.0] + [capa[c] if k >= j else 0.0 for k in range(len(D.capas))]
        fig.add_bar(x=x, y=y, name="Capa del %s" % c, marker_color=estilo_escenario(c)[1],
                    marker_line=dict(color="white", width=1),
                    hovertemplate="%{y:,.0f} kt<extra>capa del " + c + "</extra>")
    acum = 0.0
    for k, c in enumerate(D.capas):
        previo, acum = acum, acum + capa[c]
        fig.add_annotation(x=x[k + 1], y=acum, yshift=30, showarrow=False, font=dict(size=12, color=TINTA),
                           text="<b>%s kt</b><br>+%s kt de la capa del %s" % (miles(acum), miles(capa[c]), c))
        fig.add_shape(type="line", xref="x", yref="y", x0=k + 0.33, x1=k + 0.67, y0=previo, y1=previo,
                      line=dict(color=TINTA_2, width=1, dash="dash"))
    fig.add_annotation(x=x[0], y=0, yshift=12, showarrow=False, text="base", font=dict(size=12, color=TINTA_2))
    fig.update_layout(barmode="stack", bargap=0.35)
    fig.update_yaxes(range=[0, acum * 1.25])
    u = D.capas[-1]
    partes = C.enumerar(["el %s %s kt" % (c, miles(capa[c])) for c in D.capas])
    maquetar(fig, "El %s reduce %s kt frente al condicional en %d-%d" % (D.nombre(u), miles(acum), V[0], V[-1]),
             "Reducción acumulada del sector energía frente a la NDC condicional en la ventana de transacciones "
             "(kt CO2e). Cada barra apila las capas de los escalones que contiene: %s." % partes,
             "kt CO2e", xtitulo="")
    fig.update_layout(legend=dict(traceorder="normal"))
    return fig


# ----------------------------------------------------------------------------- 3. contexto nacional
def _pct_meta(D):
    """Porcentaje de las metas sobre el tendencial de 2035, de Art6_Headroom y la agregacion nacional del Modelo CLG."""
    m = D.R.get("metas_2035", {})
    f = lambda v: ("%.0f %%" % v) if abs(v - round(v)) < 0.05 else ("%.1f %%" % v).replace(".", ",")
    return f(m.get("pct_meta_inc", float("nan"))), f(m.get("pct_meta_con", float("nan")))


def f_nacional(D):
    n = D.nac.loc[2010:]
    p_inc, p_con = _pct_meta(D)
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=n.index, y=n["base"], name="Tendencial nacional", mode="lines",
                             line=dict(color="#374151", dash="dot", width=2.4),
                             hovertemplate="%{y:,.0f} kt<extra>Tendencial</extra>"))
    fig.add_trace(go.Scatter(x=n.index, y=n["incondicional"], name="Incondicional modelado", mode="lines",
                             line=dict(color="#6B7280", dash="dash", width=2.4),
                             hovertemplate="%{y:,.0f} kt<extra>Incondicional modelado</extra>"))
    fig.add_trace(go.Scatter(x=n.index, y=n["condicional"], name="Condicional modelado", mode="lines",
                             line=dict(color=CON[0], width=2.8),
                             hovertemplate="%{y:,.0f} kt<extra>Condicional modelado</extra>"))
    m = n["meta_inc"].dropna()
    fig.add_trace(go.Scatter(x=m.index, y=m, name="Meta incondicional (%s)" % p_inc, mode="lines",
                             line=dict(color=ROJO_META, width=2),
                             hovertemplate="%{y:,.0f} kt<extra>Meta " + p_inc + "</extra>"))
    mc = n["meta_con"].dropna()
    fig.add_trace(go.Scatter(x=mc.index, y=mc, name="Meta condicional (%s + %s)" % (p_inc, p_con), mode="lines",
                             line=dict(color=ROJO_META, width=2, dash="dot"),
                             hovertemplate="%{y:,.0f} kt<extra>Meta " + p_inc + " + " + p_con + "</extra>"))
    exceso = mc[2035] - n["condicional"][2035]
    maquetar(fig, "La NDC deja %s kt entre sus dos metas en 2035; el condicional modelado %s"
             % (miles(m[2035] - mc[2035]), ("baja %s kt más de lo comprometido" % miles(exceso)) if exceso >= 0 else
                ("queda %s kt por encima de lo comprometido" % miles(-exceso))),
             "Emisiones nacionales de los cinco sectores (kt CO2e): series modeladas de la agregación nacional del "
             "Modelo CLG y metas publicadas de la NDC.", "kt CO2e")
    d20 = n["base"][2020] - n["condicional"][2020]
    fig.add_annotation(x=2020, y=n["base"][2020], text="2020: el tendencial está %s kt %s el condicional"
                       % (miles(abs(d20)), "sobre" if d20 >= 0 else "bajo"), showarrow=True, arrowhead=0,
                       ax=-150, ay=-120, font=dict(size=11, color=TINTA_2))
    return fig


def f_peso_energia(D):
    p = D.peso[D.peso.anio.isin([2020, 2025, 2030, 2035])]
    x = [[str(a) for a in p.anio], list(p.trayectoria)]
    fig = go.Figure()
    fig.add_bar(x=x, y=p.energia_kt, name="Sector energía", marker_color="#2a78d6",
                text=[("%.0f %%" % v).replace(".", ",") for v in p.peso_energia_pct], textposition="inside",
                insidetextanchor="middle", textfont=dict(color="white", size=11),
                hovertemplate="%{y:,.0f} kt<extra>Energía</extra>")
    fig.add_bar(x=x, y=p.otros_sectores_kt, name="Otros cuatro sectores", marker_color="#B6BCC4",
                hovertemplate="%{y:,.0f} kt<extra>Otros sectores</extra>")
    e35 = p[(p.anio == 2035)].set_index("trayectoria")["peso_energia_pct"]
    maquetar(fig, ("La energía pesa el %.1f %% de las emisiones nacionales del tendencial y el %.1f %% del condicional "
                   "en 2035" % (e35["Tendencial"], e35["Condicional"])).replace(".", ","),
             "Emisiones nacionales por trayectoria de la agregación nacional del Modelo CLG, sector energía frente al "
             "resto (kt CO2e). La etiqueta es el peso de energía.", "kt CO2e", xtitulo="")
    fig.update_layout(barmode="stack", bargap=0.18, hovermode="closest")
    return fig


def _camino_riesgo(D):
    """Pasos del margen de 2035 del escalon que el pais ejecuta, de intacto a la prueba combinada: el
    primer componente que la corrida trae y luego la combinada (o, si ninguna combina, la peor
    prueba). [(rotulo, codigo)]."""
    top, comb = D.top, D.combinado()
    if not top or comb is None:
        return []
    comps = [d for d in D.riesgos if d is not comb and d["sufijo"] in comb["componentes"] and D.miembro(top, d)]
    if not comps:
        return [("%s, sobre %s" % (_rot(comb), top), D.miembro(top, comb))]
    resto = C.enumerar([_minus(_rot(d)) for d in D.riesgos
                        if d is not comb and d is not comps[0] and d["sufijo"] in comb["componentes"]])
    resto = resto or _minus(_rot(comb))
    return [("%s, sobre %s" % (_rot(comps[0]), top), D.miembro(top, comps[0])),
            ("%s además, sobre %s" % (resto[:1].upper() + resto[1:], top), D.miembro(top, comb))]


def f_cascada(D):
    cas = D.R["cascada_headroom_2035"]
    base = D.R["cascada_headroom_2035_base"]
    nombres, valores, medidas = [], [], []
    for c in cas:
        nombres.append(c["componente"])
        if c["kt"] is None:
            valores.append(base)
            medidas.append("total")
        else:
            valores.append(c["kt"])
            medidas.append("relative")
    top, comb = D.top, D.combinado()
    pasos = _camino_riesgo(D)
    previo = D.hr35(top)
    if top and D.capas:
        nombres.append("Margen " + _el(D.nombre(top)).replace("el ", "del ", 1).replace("la ", "de la ", 1))
        valores.append(previo)
        medidas.append("total")
    for rot, cod in pasos:
        h = D.hr35(cod)
        nombres.append(rot)
        valores.append(h - previo)
        medidas.append("relative")
        previo = h
    if pasos:
        nombres.append("Margen del %s con %s" % (top, comb.get("frase") or _minus(comb["etiqueta"])))
        valores.append(previo)
        medidas.append("total")
    import textwrap
    cortos = {"Tendencial retroactivo en energía (obras de la 1.ª NDC ya en operación)": "Tendencial retroactivo en energía",
              "Otros sectores, de tendencial a condicional": "Otros sectores",
              "Reducción del condicional modelado (agregación nacional del Modelo CLG)": "Reducción del condicional modelado",
              "Reducción modelada que la NDC no compromete": "Modelado sin compromiso en la NDC"}
    for c in D.capas:
        if D.capa(c)["fuera_ndc"]:
            cortos[D.capa(c)["corto"]] = "Paquete del %s" % c
    for c in cas:
        if c["kt"] is None:
            cortos[c["componente"]] = c["componente"].replace("Margen del condicional comprometido",
                                                              "Margen del condicional")
    etiquetas = ["<br>".join(textwrap.wrap(cortos.get(n, n), 14)) for n in nombres]
    fig = go.Figure(go.Waterfall(x=etiquetas, y=valores, measure=medidas,
                                 text=[("= %s" % miles(v)) if m == "total" else ("▲ +%s" % miles(v) if v >= 0 else "▼ −%s" % miles(-v))
                                       for v, m in zip(valores, medidas)],
                                 textposition="outside", textfont=dict(size=12, color=TINTA),
                                 connector=dict(line=dict(color="#D1D5DB", width=1)),
                                 increasing=dict(marker=dict(color="#0E8F6E")),
                                 decreasing=dict(marker=dict(color="#B42318")),
                                 totals=dict(marker=dict(color="#3B6FD8")),
                                 hovertemplate="%{x}: %{y:,.0f} kt<extra></extra>"))
    p_inc, p_con = _pct_meta(D)
    if D.R.get("reglas_headroom", {}).get("regla_nacional") == "meta_condicional":
        titular = "El margen del condicional en 2035 es el %s comprometido, %s kt" % (p_con, miles(base))
        if pasos:
            fr = comb.get("frase") or _minus(comb["etiqueta"])
            titular += ("; con %s, al %s le quedan %s kt" % (fr, top, miles(previo)) if previo >= 0
                        else "; con %s, el %s queda %s kt sobre la meta" % (fr, top, miles(-previo)))
        maquetar(fig, titular,
                 "Margen de 2035 frente a la meta incondicional (kt CO2e), con las metas publicadas: %s y %s "
                 "adicional sobre el tendencial." % (p_inc, p_con), "kt CO2e", alto=620, xtitulo="")
    else:
        maquetar(fig, "De los %s kt de margen del condicional modelado en 2035, %s kt vienen del tendencial retroactivo"
                 % (miles(base), miles(cas[0]["kt"])),
                 "Cascada del margen nacional de 2035 frente a la meta incondicional (kt CO2e); otros sectores en su "
                 "condicional modelado.", "kt CO2e", alto=620, xtitulo="")
    fig.update_layout(showlegend=False, margin=dict(b=150), hovermode="closest")
    fig.update_xaxes(tickfont=dict(size=11), tickangle=0)
    return fig


# ----------------------------------------------------------------------------- 4. riesgo y mercado
def f_headroom_riesgos(D):
    if not D.esc:
        return sin_datos("La corrida no trae escenarios de Artículo 6: no hay margen por escenario que comparar")
    cols = [(None, "Intacto")] + [(d, _rot(d)) for d in D.riesgos]
    titulos = [t for _, t in cols]
    fig = go.Figure()
    for regla, vis in (("condicional", True), ("prudente", False)):
        for s in D.esc:
            v = [D.hr35(s if d is None else D.miembro(s, d), regla) for d, _ in cols]
            nom, color, _ = estilo_escenario(s)
            fig.add_bar(x=titulos, y=v, name=nom, marker_color=color, visible=vis,
                        legendgroup=s, showlegend=True,
                        text=["" if math.isnan(x) else ("▼ " if x < 0 else "") + miles(x) for x in v],
                        textposition="outside", textfont=dict(size=12, color=TINTA),
                        hovertemplate="%{x}: %{y:,.0f} kt<extra>" + nom + "</extra>")
    fig.add_hline(y=0, line_color=ROJO_META, line_width=1.5,
                  annotation_text="meta incondicional: por debajo de cero el país la incumple",
                  annotation_position="bottom left", annotation_font=dict(size=11, color=ROJO_META))
    a0 = D.esc[0]
    comb = D.combinado(a0)
    if comb is not None:
        peor = D.hr35(D.miembro(a0, comb), "prudente")
        titular = (("%s el margen de 2035 se agota: en la regla prudente el %s queda %s kt sobre la meta"
                    % (_con_nombre(comb), a0, miles(-peor))) if peor < 0 else
                   ("%s el margen de 2035 del %s baja a %s kt en la regla prudente" % (_con_nombre(comb), a0, miles(peor))))
    else:
        titular = "Margen nacional de 2035 de %s; la corrida no trae riesgos" % C.enumerar(D.esc)
    maquetar(fig, titular,
             "Margen nacional de 2035 frente a la meta incondicional (kt CO2e), por escenario y riesgo. Regla "
             "prudente: %s. Botones: regla para los otros sectores." % SUPUESTO_PRUDENTE, "kt CO2e", alto=520, xtitulo="")
    k = len(D.esc)
    fig.update_layout(barmode="group", bargap=0.3, margin=dict(t=135), hovermode="closest",
                      updatemenus=botones_visibilidad([list(range(k)), list(range(k, 2 * k))], 2 * k,
                                                      [REGLA_C,
                                                       REGLA_P]))
    return fig


def f_sobreventa_area(D):
    P = D.R["potencial_art6"]
    aut = P["autorizado_intacto"]
    top = D.top
    if not top or not aut:
        return sin_datos("La corrida no trae escenarios de Artículo 6: no hay autorización que evaluar")
    nac = D.nac
    x = list(range(2026, 2036))
    meta = [float(nac["meta_inc"][a]) for a in x]
    casos = []
    for regla, rot in (("condicional", "regla base"), ("prudente", "regla prudente")):
        casos.append((top, regla, "Intacto · %s" % rot))
        casos += [(D.miembro(top, d), regla, "%s · %s" % (_rot(d), rot)) for d in D.riesgos if D.miembro(top, d)]
    fig, grupos, sobre = go.Figure(), [], {}
    for cod, regla, etiqueta in casos:
        h = D.hr[(D.hr.escenario == cod) & (D.hr.regla == regla)]
        if not len(h):
            continue
        h = h.iloc[0]
        nat = [float(nac["meta_inc"][a]) - float(h[str(a)]) for a in x]
        ajust = [n + (aut[str(a)] if str(a) in aut else 0.0) for n, a in zip(nat, x)]
        g = []
        tope_propio = [max(m, n) for m, n in zip(meta, nat)]
        for t in _franja(x, ajust, [max(m, y) for m, y in zip(meta, ajust)], "rgba(14,143,110,0.20)",
                         "Margen que sigue disponible", False, True):
            g.append(len(fig.data)); fig.add_trace(t)
        for t in _franja(x, meta, tope_propio, "rgba(127,29,29,0.55)",
                         "Incumplimiento propio: el país excede la meta aun sin vender", False, True):
            g.append(len(fig.data)); fig.add_trace(t)
        for t in _franja(x, tope_propio, [max(tp, y) for tp, y in zip(tope_propio, ajust)], "rgba(220,80,70,0.40)",
                         "Sobreventa: ITMO transferidos que no caben en el margen", False, True):
            g.append(len(fig.data)); fig.add_trace(t)
        for nom, y, col, dash, w in (("Meta incondicional", meta, ROJO_META, "solid", 2.4),
                                     ("Emisiones nacionales del %s en ese estado" % top, nat, estilo_escenario(top)[1], "dot", 2.4),
                                     ("Emisiones ajustadas: más los ITMO ya autorizados", ajust, TINTA, "solid", 2.8)):
            g.append(len(fig.data))
            tr = go.Scatter(x=x, y=y, name=nom, mode="lines", line=dict(color=col, dash=dash, width=w),
                            showlegend=True, legendgroup=nom, visible=False,
                            hovertemplate="%{y:,.0f} kt<extra>" + nom + "</extra>")
            if nom.startswith("Emisiones nacionales del"):
                tr = marcar_subestimados(tr, cod, col)
            fig.add_trace(tr)
        grupos.append((g, etiqueta))
        sobre[etiqueta] = sum(max(0.0, y - tp) for y, tp in zip(ajust, tope_propio))
    peor = max(sobre.items(), key=lambda kv: kv[1])
    total_aut = sum(aut.values())
    if peor[1] >= 0.5:
        titular = ("Si se autorizan %s kt con el sistema intacto, en el peor caso %s kt no caben en el margen: %s"
                   % (miles(total_aut), miles(peor[1]), peor[0]))
    else:
        titular = "Si se autorizan %s kt con el sistema intacto, caben en el margen en todos los casos" % miles(total_aut)
    maquetar(fig, titular,
             "Emisiones nacionales (kt CO2e). Con ajuste correspondiente, lo transferido se suma al balance del país. "
             "Rojo claro: sobreventa; rojo oscuro: incumplimiento sin vender. Regla prudente: %s. Elija riesgo y "
             "regla en el menú." % SUPUESTO_PRUDENTE, "kt CO2e", alto=600)
    n = len(fig.data)
    activo = [e for _, e in grupos].index(peor[0])
    for i in grupos[activo][0]:
        fig.data[i].visible = True
    fig.update_layout(updatemenus=[dict(type="dropdown", x=0, xanchor="left", y=1.17, yanchor="bottom", active=activo,
                                        buttons=[dict(label=e, method="update",
                                                      args=[{"visible": [i in g for i in range(n)]}])
                                                 for g, e in grupos],
                                        bgcolor="#F3F4F6", bordercolor="#D1D5DB", font=dict(size=12))],
                      margin=dict(t=140, b=150), legend=dict(y=-0.14))
    return fig


def f_headroom_trayectoria(D):
    anios = [str(a) for a in range(2026, 2036)]
    cods = [D.con] + D.esc + [D.miembro(c, d) for d in D.riesgos for c in D.esc if D.miembro(c, d)]
    fig, g = go.Figure(), {"condicional": [], "prudente": []}
    for regla in ("condicional", "prudente"):
        h = D.hr[D.hr.regla == regla].set_index("escenario")
        for c in cods:
            if c in h.index:
                g[regla].append(len(fig.data))
                t = linea(c, [int(a) for a in anios], h.loc[c, anios].astype(float), mostrar=(regla == "condicional"))
                t.showlegend = True
                fig.add_trace(t)
    fig.add_hline(y=0, line_color=ROJO_META, line_width=1.5,
                  annotation_text="cumplimiento justo de la meta", annotation_position="bottom right",
                  annotation_font=dict(size=11, color=ROJO_META))
    top, comb = D.top, D.combinado()
    if top and comb is not None:
        hB, hBc = D.hr35(top), D.hr35(D.miembro(top, comb))
        titular = ("%s, el margen del %s en 2035 pasa de %s a %s kt%s"
                   % (_con_nombre(comb), top, miles(hB), miles(hBc),
                      (": se consume el %s %%" % miles(100.0 * (hB - hBc) / hB)) if hB > 0 and hBc < hB else ""))
    elif top:
        titular = "El margen del %s en 2035 es de %s kt; la corrida no trae riesgos" % (top, miles(D.hr35(top)))
    else:
        titular = "El margen del condicional en 2035 es de %s kt" % miles(D.hr35(D.con))
    maquetar(fig, titular,
             "Margen nacional por año frente a la meta incondicional (kt CO2e). Regla prudente: %s. Botones: regla "
             "para los otros sectores." % SUPUESTO_PRUDENTE, "kt CO2e")
    fig.update_layout(updatemenus=botones_visibilidad([g["condicional"], g["prudente"]], len(fig.data), fig=fig, etiquetas=
                                                      [REGLA_C,
                                                       REGLA_P]), margin=dict(t=135))
    return fig


def f_volumenes(D):
    if not D.esc:
        return sin_datos("La corrida no trae escenarios de Artículo 6: no hay volúmenes que comparar")
    cols = [(None, "Intacto")] + [(d, _rot(d)) for d in D.riesgos]
    titulos = [t for _, t in cols]
    fig = go.Figure()
    vol = {}
    for regla, vis in (("adicional_a_la_NDC", True), ("con_tramo_condicional", False)):
        for s in D.esc:
            vals = []
            for d, t in cols:
                cod = s if d is None else D.miembro(s, d)
                x = D.vol[(D.vol.escenario == cod) & (D.vol.regla == regla)]["total_2031_2035"]
                vals.append(float(x.iloc[0]) if cod and len(x) else float("nan"))
                vol[(regla, s, t)] = vals[-1]
            nom, color, _ = estilo_escenario(s)
            fig.add_bar(x=titulos, y=vals, name=nom, marker_color=color, visible=vis,
                        text=["" if math.isnan(v) else miles(v) for v in vals], textposition="outside",
                        hovertemplate="%{x}: %{y:,.0f} kt<extra>" + nom + "</extra>")
    ad = lambda s, t: vol[("adicional_a_la_NDC", s, t)]
    medidos = [t for _, t in cols[1:] if any(not math.isnan(ad(s, t)) for s in D.esc)]
    ceros = [t for t in medidos if all(ad(s, t) < 0.5 for s in D.esc if not math.isnan(ad(s, t)))]
    top = D.top
    if medidos and len(ceros) == len(medidos):
        titular = ("Con cualquiera de los riesgos, el volumen adicional a la NDC cae a cero" if len(medidos) > 1 else
                   "Con %s, el volumen adicional a la NDC cae a cero" % _frase(D, medidos[0]))
    elif ceros:
        titular = "Con %s, el volumen adicional a la NDC cae a cero" % _o([_frase(D, t) for t in ceros])
    elif medidos:
        bajo = [ad(top, t) for t in medidos if not math.isnan(ad(top, t))]
        rango = (("%s kt" % miles(min(bajo))) if round(min(bajo)) == round(max(bajo)) else
                 ("entre %s y %s kt" % (miles(min(bajo)), miles(max(bajo))))) if bajo else "s. d."
        titular = ("Bajo riesgo, el volumen adicional a la NDC del %s pasa de %s kt a %s"
                   % (top, miles(ad(top, "Intacto")), rango))
    else:
        titular = "Volumen adicional a la NDC 2031-2035: %s" % C.enumerar(
            ["%s kt del %s" % (miles(ad(s, "Intacto")), s) for s in D.esc])
    maquetar(fig, titular,
             "Reducción acumulada 2031-2035 que podría ofrecerse (kt CO2e). Botones: adicional a la NDC (frente al "
             "condicional) o con tramo condicional (frente al incondicional; venderlo implica renunciar a la meta "
             "condicional).", "kt CO2e 2031-2035", xtitulo="")
    k = len(D.esc)
    fig.update_layout(barmode="group", hovermode="closest", updatemenus=botones_visibilidad(
        [list(range(k)), list(range(k, 2 * k))], 2 * k, ["Adicional a la NDC", "Con tramo condicional"]), margin=dict(t=150))
    return fig


def f_ingresos(D):
    of = pd.DataFrame(D.R["ingresos"]["oferta"])
    if of.empty:
        return sin_datos("La corrida y la configuración no dan ninguna oferta que valorar")
    of = of[~of.clave.isin(["maximo", "en_reserva"])]          # la linea en reserva no es oferta (13-10-2026)
    etiquetas = [o.replace(" (", "<br>(") for o in of.oferta]
    P = D.R["ingresos"]["precios"]              # hoja Art6_Precios: Bajo, Central, Alto
    tope = 5 * int(-(-1.5 * max(P.values()) // 5))
    precios = sorted(set(range(5, tope + 5, 5)) | {int(round(v)) for v in P.values()})
    inicial = int(round(P.get("Central", sorted(P.values())[len(P) // 2])))
    refs = C.enumerar(["%s %s" % (k.lower(), miles(v)) for k, v in sorted(P.items(), key=lambda kv: kv[1])])
    paleta = ["#4a3aa7", "#0E8F6E", "#D97A1F", "#1baf7a", "#2a78d6", "#e34948"]
    colores = [paleta[i % len(paleta)] for i in range(len(of))]
    fig = go.Figure(go.Bar(x=list(of.kt_2031_2035 * inicial / 1000.0), y=etiquetas, orientation="h",
                           marker_color=colores, text=[miles(v * inicial / 1000.0, 1) + " M US$" for v in of.kt_2031_2035],
                           textposition="outside", hovertemplate="%{y}: %{x:,.1f} M US$<extra></extra>"))
    pasos = [dict(method="update", label=str(p),
                  args=[{"x": [list(of.kt_2031_2035 * p / 1000.0)],
                         "text": [[miles(v * p / 1000.0, 1) + " M US$" for v in of.kt_2031_2035]]}])
             for p in precios]
    maquetar(fig, "Ingresos potenciales 2031-2035 según el precio por tonelada",
             "Millones de US$ por oferta hipotética (volumen del modelo o declarado × precio), cálculo externo al "
             "modelo. Mueva el deslizador; precios de referencia de la configuración: %s US$/t." % refs,
             None, alto=520, xtitulo="millones de US$")
    fig.update_layout(sliders=[dict(active=precios.index(inicial), steps=pasos, x=0, len=1, y=-0.18,
                                    currentvalue=dict(prefix="Precio: ", suffix=" US$/t", font=dict(size=13)),
                                    pad=dict(t=30))],
                      showlegend=False, margin=dict(l=260, b=150), hovermode="closest")
    fig.update_yaxes(autorange="reversed", gridcolor="white")
    fig.update_xaxes(showgrid=True, gridcolor=REJILLA)
    return fig


def f_indicadores(D):
    P = D.R["potencial_art6"]
    t = pd.DataFrame(P["tabla"])
    fig = go.Figure()
    fig.update_layout(height=360, template="plotly_white", separators=", ",
                      font=dict(family=LETRA, color=TINTA), margin=dict(l=20, r=40, t=50, b=20),
                      title=dict(text="<b>Indicadores para la decisión</b>", x=0, font=dict(size=18)))
    if t.empty:
        fig.add_annotation(x=0, y=0.5, xref="paper", yref="paper", xanchor="left", showarrow=False,
                           text="La corrida no trae escenarios de Artículo 6: no hay oferta ni margen que resumir.",
                           font=dict(size=15, color=TINTA_2))
        return fig

    def sel(suf, reg, col):
        x = t[(t.sufijo == suf) & (t.regla == reg)][col]
        return float(x.iloc[0]) if len(x) else float("nan")
    oferta = sel("", "condicional", "oferta_total")
    firme_nom = next((n for n, _, clave in P["bloques"] if clave == "firme"), None)
    firme = sel("", "condicional", firme_nom) if firme_nom else 0.0
    ad = {x["codigo"]: x for x in K.hoja("Adicionalidad")}
    firmes = [str(ad[c]["linea"]) for c in D.R.get("grupos_de_lineas", {}).get("firme", []) if c in ad]
    top, comb = D.top, D.combinado()
    fig.add_trace(go.Indicator(mode="number", value=oferta,
                               number=dict(valueformat=",.0f", suffix=" kt", font=dict(size=36, color=TINTA)),
                               title=dict(text="<b>Oferta potencial de ITMO</b><br><span style='font-size:13px;color:%s'>"
                                          "2031-2035, sector energía</span>" % TINTA_2, font=dict(size=16)),
                               domain=dict(x=[0, 0.30], y=[0.58, 1])))
    fig.add_trace(go.Indicator(mode="number", value=firme,
                               number=dict(valueformat=",.0f", suffix=" kt", font=dict(size=36, color="#0E8F6E")),
                               title=dict(text="<b>Con adicionalidad firme</b><br><span style='font-size:13px;color:%s'>"
                                          "%s</span>" % (TINTA_2, C.enumerar(firmes) if firmes else "ninguna línea"),
                                          font=dict(size=16)),
                               domain=dict(x=[0.35, 0.65], y=[0.58, 1])))
    medidores = [("", "condicional", "Transferible, sistema intacto")]
    if comb is not None:
        h_peor = D.hr35(D.miembro(top, comb), "prudente")
        fig.add_trace(go.Indicator(mode="number", value=h_peor,
                                   number=dict(valueformat=",.0f", suffix=" kt",
                                               font=dict(size=36, color=ROJO_META if h_peor < 0 else TINTA)),
                                   title=dict(text="<b>Margen de 2035 con %s</b><br><span style='font-size:13px;"
                                              "color:%s'>%s, regla prudente (otros sectores solo en su incondicional); "
                                              "negativo: incumple</span>"
                                              % (_minus(_rot(comb)), TINTA_2, D.nombre(top)), font=dict(size=16)),
                                   domain=dict(x=[0.70, 1], y=[0.58, 1])))
        medidores.append(("-" + comb["sufijo"], "prudente", "Transferible con %s, regla prudente" % _minus(_rot(comb))))
    for (suf, reg, et), (y0, y1) in zip(medidores, ((0.27, 0.40), (0.02, 0.15))):
        v = sel(suf, reg, "transferible_sin_incumplir")
        fig.add_trace(go.Indicator(
            mode="number+gauge", value=v,
            number=dict(valueformat=",.0f", suffix=" kt", font=dict(size=20, color=TINTA)),
            title=dict(text="<span style='font-size:13px'>%s</span>" % et),
            domain=dict(x=[0.30, 0.88], y=[y0, y1]),
            gauge=dict(shape="bullet", axis=dict(range=[0, max(oferta, 1.0)], tickformat=",.0f"),
                       bar=dict(color="#0E8F6E", thickness=0.6), bgcolor="#F3F4F6", borderwidth=0,
                       threshold=dict(line=dict(color=TINTA, width=3), thickness=0.9, value=oferta))))
    return fig


def f_referencias(D):
    """Las referencias de la contabilidad en el ambito nacional: tendencial de la NDC, nivel de las dos
    metas de 2035 con su senda e inventario observado (INGEI)."""
    nac = D.nac
    M = D.R.get("metas_2035", {})
    a35 = C.VENTANA[-1]
    x = list(nac.index)
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=x, y=nac["base"], name="Tendencial de la NDC", mode="lines",
                             line=dict(color=NEUTRO, width=2.4, dash="dash"), legendgroup="base",
                             hovertemplate="%{y:,.0f} kt<extra>tendencial</extra>"))
    mi, mc = nac["meta_inc"].dropna(), nac["meta_con"].dropna()
    fig.add_trace(go.Scatter(x=list(mi.index), y=mi, name="Meta incondicional", mode="lines",
                             line=dict(color=ROJO_META, width=2.8), legendgroup="m_inc",
                             hovertemplate="%{y:,.0f} kt<extra>meta incondicional</extra>"))
    fig.add_trace(go.Scatter(x=list(mc.index), y=mc, name="Meta condicional", mode="lines",
                             line=dict(color=CON[0], width=2.4, dash="dot"), legendgroup="m_con",
                             hovertemplate="%{y:,.0f} kt<extra>meta condicional</extra>"))
    inv = {int(k): v for k, v in ((D.R.get("inventario") or {}).get("nacional_con_utcuts") or {}).items()}
    ult = max(inv) if inv else None
    if inv:
        xs = sorted(a for a in inv if a >= x[0])
        fig.add_trace(go.Scatter(x=xs, y=[inv[a] for a in xs], name="Inventario observado (INGEI)",
                                 mode="lines+markers", line=dict(color="#111827", width=1.6), marker=dict(size=5),
                                 legendgroup="comun", hovertemplate="%{y:,.0f} kt<extra>inventario</extra>"))
    if ult:
        titular = ("La meta incondicional de %d es %s kt nacionales y la condicional %s kt; el último inventario, de %d, "
                   "registra %s kt" % (a35, miles(M.get("meta_inc", 0)), miles(M.get("meta_con", 0)), ult, miles(inv[ult])))
    else:
        titular = ("La meta incondicional de %d es %s kt nacionales y la condicional %s kt"
                   % (a35, miles(M.get("meta_inc", 0)), miles(M.get("meta_con", 0))))
    sub = ("Emisiones nacionales con USCUSS (kt CO2e). Las metas son niveles de %d: la incondicional queda %s kt bajo el "
           "tendencial de %s kt y la condicional %s kt más abajo. La senda que une %d con cada meta es un supuesto de "
           "cálculo para los años intermedios. El inventario es el dato con el que se verifica el cumplimiento."
           % (a35, miles(M.get("base", 0) - M.get("meta_inc", 0)), miles(M.get("base", 0)),
              miles(M.get("meta_inc", 0) - M.get("meta_con", 0)), int(mi.index[0]) if len(mi) else a35))
    maquetar(fig, titular, sub, "kt CO2e")
    fig.update_layout(annotations=list(fig.layout.annotations) + etiquetas_finales(fig, range(len(fig.data))),
                      margin=dict(r=190))
    fig.update_xaxes(range=[x[0], a35 + 0.5])
    return fig


def f_comparacion(D):
    """Cuatro paneles con los escenarios lado a lado: emisiones de energia en el anio meta, reduccion
    acumulada en el marco 2026-2035 frente al condicional, margen nacional del anio meta con las dos reglas y
    participacion de la ERNC."""
    from plotly.subplots import make_subplots
    a35 = C.VENTANA[-1]
    vent = "%d-%d" % (C.MARCO[0], C.MARCO[-1])
    cods = [c for c in [D.inc, D.con] + D.esc if c in D.em]
    fig = make_subplots(rows=2, cols=2, horizontal_spacing=0.26, vertical_spacing=0.17,
                        subplot_titles=("Emisiones del sector energía en %d, kt CO2e" % a35,
                                        "Reducción %s frente al condicional, kt CO2e" % vent,
                                        "Margen nacional en %d frente a la meta incondicional, kt CO2e" % a35,
                                        "ERNC en la generación eléctrica de %d, %%" % a35))

    def barra(xs, ys, cols, row, col, textos, name="", showlegend=False, opacity=1.0, suf=" kt"):
        fig.add_bar(x=xs, y=ys, orientation="h", marker_color=cols, text=textos, textposition="outside",
                    textfont=dict(size=12, color=TINTA), cliponaxis=False, showlegend=showlegend, name=name,
                    opacity=opacity, hovertemplate="%{x:,.1f}" + suf + "<extra>%{y}</extra>", row=row, col=col)
    ys = [D.nombre(c) for c in cods]
    cols = [estilo_escenario(c)[1] for c in cods]
    barra([D.em[c][a35] for c in cods], ys, cols, 1, 1, [miles(D.em[c][a35]) for c in cods])
    xs2, ys2, cols2 = [], [], []
    for c in D.esc:
        v = sum(D.em[D.con][a] - D.em[c][a] for a in C.MARCO)
        xs2.append(v); ys2.append(D.nombre(c)); cols2.append(estilo_escenario(c)[1])
        x = D.contrafactual(c)
        if x:
            w = sum(D.em[x][a] - D.em[c][a] for a in C.MARCO)
            xs2.append(w); ys2.append("Atribuible por retiro, %s" % c); cols2.append(NEUTRO)
    barra(xs2, ys2, cols2, 1, 2, [miles(v) for v in xs2])
    con_esc = [c for c in [D.con] + D.esc if c in D.em]
    for regla, et, op in (("condicional", REGLA_C, 1.0), ("prudente", REGLA_P, 0.5)):
        vals = [D.hr35(c, regla) for c in con_esc]
        barra(vals, [D.nombre(c) for c in con_esc], [estilo_escenario(c)[1] for c in con_esc], 2, 1,
              [miles(v) for v in vals], name=et, showlegend=True, opacity=op)
    ern = [float(D.ernc[c][a35]) if c in D.ernc else float("nan") for c in cods]
    barra(ern, ys, cols, 2, 2, ["%s %%" % miles(v, 1) for v in ern], suf=" %")
    iguales = len(D.esc) > 1 and max(D.em[c][a35] for c in D.esc) - min(D.em[c][a35] for c in D.esc) < 1.0
    if D.esc:
        top = D.esc[-1]
        red_top = sum(D.em[D.con][a] - D.em[top][a] for a in C.MARCO)
        titular = ("%s en %d: %s; %s reduce %s kt acumulados en 2026-2035 frente al condicional y su margen de %d va de %s a %s kt según la regla"
                   % ("Emisiones iguales" if iguales else "Emisiones por escenario", a35,
                      ("%s kt en %s" % (miles(D.em[top][a35]), C.enumerar([D.nombre(c) for c in D.esc]))) if iguales else
                      C.enumerar(["%s kt en %s" % (miles(D.em[c][a35]), D.nombre(c)) for c in D.esc]),
                      D.nombre(top), miles(red_top), a35, miles(D.hr35(top, "prudente")), miles(D.hr35(top, "condicional"))))
    else:
        titular = "Comparación de las referencias de la NDC"
    maquetar(fig, titular,
             "Barras con el color de cada escenario. Margen: distancia entre la meta incondicional y las emisiones "
             "nacionales del escenario; la barra clara aplica la regla prudente. La ERNC excluye la hidroelectricidad.",
             None, alto=700, xtitulo="")
    fig.update_layout(barmode="group", bargap=0.30, legend=dict(y=-0.07))
    fig.update_yaxes(autorange="reversed", tickfont=dict(size=12))
    fig.update_xaxes(showgrid=True, gridcolor=REJILLA, zeroline=True, zerolinecolor="#C9D1CE", tickformat=",.0f")
    for a in fig.layout.annotations:
        a.font = dict(size=13, color=TINTA)
    return fig


# ----------------------------------------------------------------------------- versiones de impresion (informe Word)
# Guia de graficas de la skill disenocarbono (13-10-2026): Arial, paleta del proyecto (azul pizarra, verde petroleo, ocre;
# ladrillo solo para incumplimiento), sin titulo incrustado, etiquetas directas en lugar de leyenda, rejilla tenue, lienzo
# de 900 px con letra de 15 a 16 px. Reemplazan, solo en graficas/informe, a las versiones interactivas de arriba, que
# siguen en el visualizador y en el tablero. Las cifras salen de resultados_art6.json; ninguna se escribe a mano.
I_LETRA = "Arial"
I_ANCHO = 900
I_ACENTO, I_VERDE, I_OCRE, I_LADRILLO = "#4E5D7E", "#0E7C6B", "#C08A2E", "#9A3B34"
I_TINTA, I_GRIS, I_REGLA, I_REJILLA = "#1F2937", "#5B6470", "#C9D1CE", "#ECEFEE"
I_ESCALONES = [I_VERDE, I_OCRE, I_ACENTO]                      # A, B y C, como en el resto de las graficas
I_RAMPA_BLANCA = [I_VERDE, "#5FA79B", "#A8D0C8"]                  # bloques de la lista blanca
I_RAMPA_GRIS = ["#A3A9B1", "#C8CCD2", "#DDE1E5"]                  # bloques fuera de la lista blanca
I_FANTASMA = {"central": "#E3E7EE", "blanca": "#DCEBE8"}          # oferta completa detras de lo transferible
I_FAMILIAS = {"Hidroeléctrica": I_ACENTO, "Geotermia": "#6FAFA5", "Biomasa y biogás": "#D9BC84", "Eólica": I_VERDE,
              "Solar": I_OCRE, "Gas natural": "#A3A9B1", "Crudo, GLP e importación": "#C8CCD2",
              "Fuel oil y diésel": "#6E7681"}                     # renovables en color, fosiles en gris
I_ORDEN_FAMILIAS = ["Hidroeléctrica", "Geotermia", "Biomasa y biogás", "Eólica", "Solar", "Gas natural",
                    "Crudo, GLP e importación", "Fuel oil y diésel"]


def _num(v, dec=1):
    """11.674,4: punto de miles, coma decimal, signo menos tipografico y redondeo de la mitad hacia arriba (3.450,5 da
    3.451, no 3.450 como el redondeo al par de format)."""
    from decimal import Decimal, ROUND_HALF_UP
    if v is None or (isinstance(v, float) and math.isnan(v)):
        return "s. d."
    q = Decimal(str(abs(v))).quantize(Decimal(1).scaleb(-dec), rounding=ROUND_HALF_UP)
    s = ("{:,.%df}" % dec).format(q).replace(",", "#").replace(".", ",").replace("#", ".")
    return ("−" if v < 0 and q != 0 else "") + s


def _es_impresion(fig):
    return getattr(fig.layout, "meta", None) == "impresion"


def _base_impresion(fig, alto, l, r, t, b):
    fig.update_layout(template="plotly_white", width=I_ANCHO, height=alto, meta="impresion", showlegend=False,
                      font=dict(family=I_LETRA, size=15, color=I_TINTA), separators=",.",
                      paper_bgcolor="white", plot_bgcolor="white", margin=dict(l=l, r=r, t=t, b=b),
                      hovermode=False, title_text="")
    return fig


def _rotulo_impreso(d, ancho=26):
    """Rotulo del estado para el eje de las graficas impresas: el de presentacion (configuracion.ROTULOS) sin el codigo
    final o, si pasa de 42 caracteres, la etiqueta corta de Art6_Riesgos; en lineas de unos `ancho` caracteres y el
    codigo del estado en gris al final."""
    import textwrap
    if d is None:
        return "Sistema intacto"
    rot = _rot(d)
    m = re.search(r"\s*\(([A-Z0-9-]+)\)$", rot)
    codigo = m.group(1) if m else d["sufijo"]
    if m:
        rot = rot[:m.start()]
    if len(rot) > 42:
        rot = d["etiqueta"]
    lineas = textwrap.wrap(rot, ancho)
    cod = "<span style='color:%s;font-size:13px'>%s</span>" % (I_GRIS, codigo)
    if len(lineas[-1]) + len(codigo) + 3 <= ancho + 4:
        lineas[-1] += " · " + cod
    else:
        lineas.append(cod)
    return "<br>".join(lineas)


def _estados_impresion(D):
    """[(sufijo, d)] del sistema intacto y de las pruebas de estres (grupo Riesgo), en el orden de la configuracion."""
    return [("", None)] + [(d["sufijo"], d) for d in D.riesgos]


def _nota_eje(fig, texto, x_paper, y_paper, yanchor="bottom"):
    fig.add_annotation(x=x_paper, y=y_paper, xref="paper", yref="paper", xanchor="left", yanchor=yanchor,
                       showarrow=False, align="left", text=texto, font=dict(size=15, color=I_TINTA))


def i_potencial(D):
    """Grafica 7.5 del informe: composicion de la oferta central (sin las lineas en reserva) y de la lista blanca, y lo
    transferible sin incumplir la meta incondicional en cada estado con la lectura de autorizacion (proyeccion del
    Modelo CLG y regla prudente, decision del 13-10-2026). La regla condicional queda como marca
    secundaria sobre la oferta central."""
    from plotly.subplots import make_subplots
    P = D.R["potencial_art6"]
    dec = D.R.get("decisiones_13_10") or {}
    t = pd.DataFrame(P["tabla"])
    proy, regla = P.get("lectura_de_autorizacion", ["CLG", "prudente"])
    otra = "condicional" if regla == "prudente" else "prudente"
    if t.empty or not dec or proy != "CLG":
        return sin_datos("La corrida no trae la oferta y los subconjuntos de la decisión del 13-10-2026")
    subs = {s["clave"]: s for s in dec["subconjuntos"]}
    sk_c, sk_b = dec["subconjunto_central"], "lista_blanca"
    of_c, of_b = float(subs[sk_c]["oferta_2031_2035"]), float(subs[sk_b]["oferta_2031_2035"])
    en_blanca = set(subs[sk_b]["bloques"])
    intacto = t[(t.sufijo == "") & (t.regla == regla)].iloc[0]
    bloques = [(clave, float(intacto[nom])) for nom, _, clave in P["bloques"]]
    if abs(sum(v for _, v in bloques) - of_c) > 0.15:
        raise ValueError("La suma de los bloques no da la oferta central: %.1f frente a %.1f"
                         % (sum(v for _, v in bloques), of_c))
    rv = pd.DataFrame(D.R["reserva_por_aniada"]["resumen"])
    sv = {s["sufijo"]: s for s in P["sobreventa"] if s["regla"] == regla}

    def autorizable(sk, suf):
        x = rv[(rv.subconjunto == sk) & (rv.sufijo == suf)]["autorizable_2031_2035"]
        return float(x.iloc[0]) if len(x) else float("nan")

    def transferible(suf, rg):
        x = t[(t.sufijo == ("-" + suf if suf else "")) & (t.regla == rg)]["transferible_sin_incumplir"]
        return float(x.iloc[0]) if len(x) else float("nan")

    estados = [(suf, d) for suf, d in _estados_impresion(D) if not math.isnan(autorizable(sk_c, suf))]
    filas = []
    for suf, d in estados:
        c, b = autorizable(sk_c, suf), autorizable(sk_b, suf)
        if abs(c - transferible(suf, regla)) > 0.15:          # la reserva por anada y el potencial deben coincidir
            raise ValueError("Transferible de %s no coincide: %.1f frente a %.1f" % (suf or "intacto", c,
                                                                                     transferible(suf, regla)))
        inc = float((sv.get("-" + suf if suf else "") or {}).get("incumplimiento_sin_transferir_2031_2035") or 0.0)
        filas.append({"suf": suf, "rot": _rotulo_impreso(d), "central": c, "blanca": b,
                      "otra": transferible(suf, otra), "incumple": inc})

    n = len(filas)
    alto_fila, alto_sup = 52, 118
    l, r, t_m, b_m = 215, 34, 44, 64
    alto_inf = alto_fila * n
    sep = 70
    alto = t_m + alto_sup + sep + alto_inf + b_m
    util = alto - t_m - b_m
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=sep / float(util),
                        row_heights=[alto_sup / float(alto_sup + alto_inf), alto_inf / float(alto_sup + alto_inf)])
    xmax = of_c * 1.085
    ancho_util = I_ANCHO - l - r
    px = ancho_util / xmax                                   # px por kt

    # ---- panel superior: composicion de la oferta central y de la lista blanca
    i_b = i_g = 0
    color, x0 = {}, 0.0
    for clave, v in bloques:
        if clave in en_blanca:
            color[clave] = I_RAMPA_BLANCA[i_b % len(I_RAMPA_BLANCA)]; i_b += 1
        else:
            color[clave] = I_RAMPA_GRIS[i_g % len(I_RAMPA_GRIS)]; i_g += 1
    nombre = {"firme": "Firme", "declarado": "Declaradas"}
    oscuro = {I_VERDE, I_RAMPA_GRIS[0]}
    arriba = []
    for clave, v in bloques:
        nom = nombre.get(clave) or ("Capa %s" % clave.split(":", 1)[1] if clave.startswith("capa:") else clave)
        ancho_px = v * px
        if ancho_px >= 112:
            txt = "%s · %s" % (nom, _num(v))
        elif ancho_px >= 70:
            txt = "%s<br>%s" % (nom, _num(v))
        else:
            txt = ""
            arriba.append((x0 + v / 2.0, x0, "%s %s" % (nom, _num(v))))
        fig.add_bar(x=[v], y=[0], base=[x0], orientation="h", width=0.62, marker_color=color[clave],
                    marker_line=dict(color="white", width=1.2), text=[txt], textposition="inside",
                    insidetextanchor="middle", textangle=0, cliponaxis=False, constraintext="none",
                    textfont=dict(size=13, color="white" if color[clave] in oscuro and clave in en_blanca else I_TINTA),
                    row=1, col=1)
        x0 += v
    x0 = 0.0
    for clave, v in bloques:
        if clave not in en_blanca:
            continue
        fig.add_bar(x=[v], y=[1], base=[x0], orientation="h", width=0.62, marker_color=color[clave],
                    marker_line=dict(color="white", width=1.2), row=1, col=1)
        x0 += v
    for y_, tot in ((0, of_c), (1, of_b)):
        fig.add_annotation(x=tot, y=y_, xref="x", yref="y", xanchor="left", xshift=6, showarrow=False,
                           text="<b>%s</b>" % _num(tot), font=dict(size=15, color=I_TINTA))
    previo = -1e9
    for xc, xi, txt in arriba:                               # bloques angostos: rotulo arriba con guia
        dx = max(0.0, previo - xi * px + 12)
        fig.add_annotation(x=xc, y=-0.31, xref="x", yref="y", ax=(xi - xc) * px + dx + 2, ay=-24, axref="pixel",
                           ayref="pixel", showarrow=True, arrowhead=0, arrowwidth=1, arrowcolor=I_GRIS,
                           xanchor="left", yanchor="bottom", text=txt, font=dict(size=13, color=I_TINTA))
        previo = xi * px + dx + 8 * len(txt)
    fig.update_yaxes(tickvals=[0, 1], ticktext=["Oferta central<br><span style='color:%s;font-size:13px'>sin EN32"
                                                 "</span>" % I_GRIS,
                                                 "Lista blanca<br><span style='color:%s;font-size:13px'>bloques en color"
                                                 "</span>" % I_GRIS],
                     range=[1.55, -0.95], showgrid=False, zeroline=False, ticks="", tickfont=dict(size=15), ticklabelstandoff=8,
                     row=1, col=1)

    # ---- panel inferior: transferible sin incumplir por estado
    ys_c = [i - 0.19 for i in range(n)]
    ys_b = [i + 0.19 for i in range(n)]
    fig.add_bar(x=[of_c] * n, y=ys_c, orientation="h", width=0.34, marker_color=I_FANTASMA["central"], row=2, col=1)
    fig.add_bar(x=[of_b] * n, y=ys_b, orientation="h", width=0.34, marker_color=I_FANTASMA["blanca"], row=2, col=1)
    vc = [f["central"] for f in filas]
    vb = [f["blanca"] for f in filas]
    dentro = [v * px >= 80 for v in vc]
    fig.add_bar(x=vc, y=ys_c, orientation="h", width=0.34, marker_color=I_ACENTO,
                text=[_num(v) if v >= 0.05 else "" for v in vc],
                textposition=["inside" if x else "outside" for x in dentro], insidetextanchor="end",
                constraintext="none",
                textfont=dict(size=14, color=["white" if x else I_TINTA for x in dentro]), cliponaxis=False,
                row=2, col=1)
    fig.add_bar(x=vb, y=ys_b, orientation="h", width=0.34, marker_color=I_VERDE, row=2, col=1)
    for i, v in enumerate(vb):                                # valores en columna, al final de la oferta
        if v >= 0.05:
            fig.add_annotation(x=max(v, of_b), y=ys_b[i], xref="x2", yref="y2", xanchor="left", xshift=6,
                               showarrow=False, text=_num(v), font=dict(size=14, color=I_TINTA))
    # nombres de las series en la primera fila, dentro de la barra
    for y_, txt in ((ys_c[0], "Oferta central"), (ys_b[0], "Lista blanca")):
        fig.add_annotation(x=0, y=y_, xref="x2", yref="y2", xanchor="left", xshift=6, showarrow=False, text=txt,
                           font=dict(size=13, color="white"))
    # ceros: en ladrillo y, si el pais excede la meta sin transferir, dicho en la fila
    for i, f in enumerate(filas):
        if f["central"] < 0.05:
            fig.add_annotation(x=0, y=ys_c[i], xref="x2", yref="y2", xanchor="left", xshift=4, showarrow=False,
                               text="0", font=dict(size=14, color=I_LADRILLO))
        if f["blanca"] < 0.05:
            fig.add_annotation(x=0, y=ys_b[i], xref="x2", yref="y2", xanchor="left", xshift=4, showarrow=False,
                               text="0" + (" · el país excede la meta aun sin transferir" if f["incumple"] > 0.05 else ""),
                               font=dict(size=14, color=I_LADRILLO))
    # regla condicional como marca secundaria sobre la oferta central
    marcas = [(f["otra"], ys_c[i], f) for i, f in enumerate(filas)
              if not math.isnan(f["otra"]) and abs(f["otra"] - f["central"]) > 0.5]
    if marcas:
        fig.add_scatter(x=[m[0] for m in marcas], y=[m[1] for m in marcas], mode="markers",
                        marker=dict(symbol="line-ns", size=21, line=dict(width=2.6, color=I_GRIS)),
                        cliponaxis=False, row=2, col=1)
        xm, ym, fm = max(marcas, key=lambda m: m[0] - m[2]["central"])
        fig.add_annotation(x=xm, y=ym, xref="x2", yref="y2", xanchor="right", xshift=-7, showarrow=False,
                           text="regla %s" % otra, font=dict(size=13, color=I_GRIS))
    fig.update_yaxes(tickvals=list(range(n)), ticktext=[f["rot"] for f in filas], range=[n - 0.45, -0.6],
                     showgrid=False, zeroline=False, ticks="", tickfont=dict(size=15), ticklabelstandoff=8, row=2, col=1)
    fig.update_xaxes(range=[0, xmax], showgrid=True, gridcolor=I_REJILLA, zeroline=True, zerolinecolor=I_REGLA,
                     showline=False, tickformat=",.0f", tickfont=dict(size=15), row=1, col=1)
    fig.update_xaxes(range=[0, xmax], showgrid=True, gridcolor=I_REJILLA, zeroline=True, zerolinecolor=I_REGLA,
                     showline=True, linecolor=I_REGLA, ticks="outside", tickcolor=I_REGLA, tickformat=",.0f",
                     tickfont=dict(size=15), title_text="kt CO2-eq, suma 2031-2035", title_font=dict(size=15, color=I_GRIS),
                     row=2, col=1)
    fig.update_layout(barmode="overlay", bargap=0)
    _base_impresion(fig, alto, l, r, t_m, b_m)
    # encabezados de los paneles, alineados al borde izquierdo del lienzo
    x_borde = -float(l - 8) / ancho_util
    dom1, dom2 = fig.layout.yaxis.domain, fig.layout.yaxis2.domain
    _nota_eje(fig, "<b>Oferta 2031-2035 por bloque</b>", x_borde, dom1[1] + 8.0 / util)
    _nota_eje(fig, "<b>Transferible sin incumplir la meta incondicional, por estado</b> "
                   "<span style='color:%s'>(Modelo CLG, regla %s)</span>" % (I_GRIS, regla),
              x_borde, dom2[1] + 8.0 / util)
    return fig


def i_headroom_riesgos(D):
    """Grafica 7.6 del informe: margen nacional de 2035 frente a la meta incondicional de cada escenario de Articulo 6
    en cada estado, con la proyeccion del Modelo CLG y la regla prudente. La regla condicional suma la misma cantidad a
    todos los margenes; queda como una linea secundaria: a su izquierda se incumple tambien con ella."""
    if not D.esc:
        return sin_datos("La corrida no trae escenarios de Artículo 6: no hay margen por escenario que comparar")
    regla = (D.R["potencial_art6"].get("lectura_de_autorizacion") or ["CLG", "prudente"])[1]
    otra = "condicional" if regla == "prudente" else "prudente"
    estados = _estados_impresion(D)
    esc = list(D.esc)
    k = len(esc)
    paso = 0.80 / k
    off = [(j - (k - 1) / 2.0) * paso for j in range(k)]
    val, dif = {}, []
    for i, (suf, d) in enumerate(estados):
        for j, s in enumerate(esc):
            cod = s if d is None else D.miembro(s, d)
            v, w = D.hr35(cod, regla), D.hr35(cod, otra)
            val[(i, j)] = v
            if not (math.isnan(v) or math.isnan(w)):
                dif.append(w - v)
    vs = [v for v in val.values() if not math.isnan(v)]
    n = len(estados)
    alto_fila = 64
    l, r, t_m, b_m = 215, 34, 86, 66
    alto = t_m + b_m + alto_fila * n
    lo, hi = min(vs + [0.0]), max(vs)
    delta = (sum(dif) / len(dif)) if dif else float("nan")
    constante = bool(dif) and max(dif) - min(dif) < 0.3
    if constante and regla == "prudente":
        lo = min(lo, -delta)
    span = hi - lo
    x0, x1 = lo - 0.13 * span, hi + 0.11 * span
    ancho_util = I_ANCHO - l - r
    fig = go.Figure()
    fig.add_vrect(x0=x0, x1=0, fillcolor="#FAF0EF", opacity=1.0, layer="below", line_width=0)
    px = (I_ANCHO - l - r) / float(x1 - x0)                     # px por kt
    for j, s in enumerate(esc):
        ys = [i + off[j] for i in range(n)]
        xs = [val[(i, j)] for i in range(n)]
        dentro = [(not math.isnan(v)) and v < 0 and -v * px >= 75 for v in xs]   # negativos largos: cifra dentro
        fig.add_bar(x=xs, y=ys, orientation="h", width=paso * 0.92, marker_color=I_ESCALONES[j % len(I_ESCALONES)],
                    text=["" if math.isnan(v) else _num(v) for v in xs],
                    textposition=["inside" if d_ else "outside" for d_ in dentro], insidetextanchor="end",
                    constraintext="none",
                    textfont=dict(size=13, color=["white" if d_ else (I_LADRILLO if v < 0 else I_TINTA)
                                                  for v, d_ in zip(xs, dentro)]), cliponaxis=False)
        fig.add_annotation(x=0, y=ys[0], xref="x", yref="y", xanchor="left", xshift=6, showarrow=False,
                           text="<b>%s</b> · %s" % (s, D.nombre(s)), font=dict(size=13, color="white"))
    fig.add_vline(x=0, line=dict(color=I_LADRILLO, width=1.6))
    fig.add_annotation(x=0, y=1, xref="x", yref="paper", xanchor="left", yanchor="bottom", xshift=4, yshift=4,
                       showarrow=False, text="Meta incondicional con la regla %s" % regla,
                       font=dict(size=13, color=I_LADRILLO))
    if constante and regla == "prudente":
        fig.add_vline(x=-delta, line=dict(color=I_GRIS, width=1.4, dash="dash"), layer="below")
        fig.add_annotation(x=-delta, y=1, xref="x", yref="paper", xanchor="left", yanchor="bottom", xshift=4,
                           yshift=28, showarrow=False,
                           text="Umbral con la regla %s: todos los márgenes suben %s kt"
                                % (otra, _num(delta)), font=dict(size=13, color=I_GRIS))
    elif dif:                                                    # si la diferencia no es constante: marca por barra
        for j, s in enumerate(esc):
            xs, ys = [], []
            for i, (suf, d) in enumerate(estados):
                cod = s if d is None else D.miembro(s, d)
                w = D.hr35(cod, otra)
                if not math.isnan(w):
                    xs.append(w); ys.append(i + off[j])
            fig.add_scatter(x=xs, y=ys, mode="markers", cliponaxis=False,
                            marker=dict(symbol="line-ns", size=14, line=dict(width=2.2, color=I_GRIS)))
    fig.update_yaxes(tickvals=list(range(n)), ticktext=[_rotulo_impreso(d) for _, d in estados],
                     range=[n - 0.5, -0.5], showgrid=False, zeroline=False, ticks="", tickfont=dict(size=15),
                     ticklabelstandoff=8)
    fig.update_xaxes(range=[x0, x1], showgrid=True, gridcolor=I_REJILLA, zeroline=False, showline=True,
                     linecolor=I_REGLA, ticks="outside", tickcolor=I_REGLA, tickformat=",.0f", tickfont=dict(size=15),
                     title_text="Margen nacional de %d frente a la meta incondicional, kt CO2-eq" % C.VENTANA[-1],
                     title_font=dict(size=15, color=I_GRIS))
    fig.update_layout(barmode="overlay", bargap=0)
    return _base_impresion(fig, alto, l, r, t_m, b_m)


def i_generacion(D, cod=None):
    """Grafica 7.8 del informe: generacion electrica por tipo de planta de la referencia de los escenarios de Articulo 6
    (la NDC condicional con calibracion propia, CONA6), en GWh, con etiquetas directas al final."""
    cod = cod or D.con
    g = D.gen[D.gen.escenario == cod].pivot_table(index="anio", columns="familia", values="GWh", aggfunc="sum")
    if g.empty:
        return sin_datos("La corrida no trae la generación de %s" % cod)
    fams = [f for f in I_ORDEN_FAMILIAS if f in g and g[f].abs().sum() > 1e-6] + \
           [f for f in g.columns if f not in I_ORDEN_FAMILIAS and g[f].abs().sum() > 1e-6]
    a0, a1 = int(g.index.min()), int(g.index.max())
    l, r, t_m, b_m, alto = 78, 252, 70, 50, 580
    fig = go.Figure()
    for f in fams:
        fig.add_scatter(x=list(g.index), y=list(g[f]), mode="lines", stackgroup="uno",
                        line=dict(width=0.6, color="white"), fillcolor=I_FAMILIAS.get(f, "#B8BEC6"))
    tot = g[fams].sum(axis=1)
    ymax = float(tot.max()) * 1.08
    alto_util = alto - t_m - b_m
    pxv = alto_util / ymax                                       # px por GWh
    centros, acum = [], 0.0
    for f in fams:
        v = float(g.loc[a1, f])
        centros.append((acum + v / 2.0, f, v))
        acum += v
    # separacion minima de 19 px entre etiquetas, de abajo hacia arriba
    pos, previo = [], -1e9
    for c, f, v in centros:
        y = max(c * pxv, previo + 19)
        pos.append((c, y / pxv, f, v))
        previo = y
    exceso = previo - alto_util
    if exceso > 0:
        pos = [(c, y - exceso / pxv, f, v) for c, y, f, v in pos]
    for c, y, f, v in pos:
        fig.add_annotation(x=a1, y=c, xref="x", yref="y", ax=16, ay=-(y - c) * pxv, axref="pixel", ayref="pixel",
                           showarrow=True, arrowhead=0, arrowwidth=1, arrowcolor=I_GRIS, xanchor="left",
                           text="<span style='color:%s'>■</span> %s · %s" % (I_FAMILIAS.get(f, "#B8BEC6"), f, _num(v, 0)),
                           font=dict(size=14, color=I_TINTA))
    fig.add_annotation(x=a1, y=float(tot[a1]), xref="x", yref="y", xanchor="right", yanchor="bottom", yshift=4,
                       showarrow=False, text="<b>%s GWh en %d</b>" % (_num(float(tot[a1]), 0), a1),
                       font=dict(size=14, color=I_TINTA))
    for (v0, v1), txt in (((C.MARCO[0], C.MARCO[-1]), "Segunda NDC %d-%d" % (C.MARCO[0], C.MARCO[-1])),
                          ((C.VENTANA[0], C.VENTANA[-1]), "transacciones %d-%d" % (C.VENTANA[0], C.VENTANA[-1]))):
        fig.add_vrect(x0=v0 - 0.5, x1=min(v1 + 0.5, a1), fillcolor="#EEF1F5" if v0 == C.MARCO[0] else "#E2E6EC",
                      opacity=1.0, layer="below", line_width=0)
        fig.add_annotation(x=v0 - 0.5, y=1, xref="x", yref="paper", xanchor="left", yanchor="bottom", xshift=2,
                           yshift=4 if v0 == C.MARCO[0] else 24, showarrow=False, text=txt,
                           font=dict(size=13, color=I_GRIS))
    fig.update_xaxes(range=[a0, a1], showgrid=False, showline=True, linecolor=I_REGLA, ticks="outside",
                     tickcolor=I_REGLA, dtick=5, tickfont=dict(size=15))
    fig.update_yaxes(range=[0, ymax], showgrid=True, gridcolor=I_REJILLA, zeroline=True, zerolinecolor=I_REGLA,
                     tickformat=",.0f", tickfont=dict(size=15), title_text="GWh", title_font=dict(size=15, color=I_GRIS))
    return _base_impresion(fig, alto, l, r, t_m, b_m)


IMPRESION = {"g02_potencial": i_potencial, "g14_headroom_riesgos": i_headroom_riesgos, "g07_generacion": i_generacion}


TITULOS = {
    "g00_indicadores": "Indicadores para la decisión",
    "g01_itmos_area": "Oferta de Artículo 6 por tramo, 2031-2035",
    "g02_potencial": "Composición de la oferta y volumen transferible bajo riesgo",
    "g03_energia_escenarios": "Emisiones del sector energía por escenario",
    "g04_reduccion_anual": "Reducción anual frente al condicional",
    "g20_escalera": "Escalera de capas frente al condicional",
    "g05_emisiones_generacion": "Emisiones de la generación eléctrica por escenario",
    "g06_subsectores": "Emisiones de energía por subsector",
    "g07_generacion": "Generación eléctrica por tipo de planta",
    "g08_capacidad": "Capacidad instalada por tipo de planta",
    "g09_ernc": "Participación de la ERNC en la generación",
    "g10_nacional": "Emisiones nacionales por trayectoria del Modelo CLG",
    "g11_peso_energia": "Peso del sector energía en las emisiones nacionales",
    "g12_cascada_headroom": "Cascada del margen nacional en 2035",
    "g13_sobreventa_area": "Balance nacional con la transferencia autorizada",
    "g14_headroom_riesgos": "Margen de 2035 por escenario y riesgo",
    "g15_headroom_trayectoria": "Margen nacional por año y riesgo",
    "g16_volumenes": "Volúmenes transferibles por escenario y riesgo",
    "g17_ingresos": "Ingresos potenciales según el precio",
    "g18_referencias": "Tendencial, metas de 2035 e inventario observado",
    "g19_comparacion": "Comparación de escenarios en 2035",
}


def retitular(fig, gid):
    """Titulo limpio (sintagma nominal) y el hallazgo con sus cifras como primera frase del subtitulo."""
    limpio = TITULOS.get(gid)
    texto = fig.layout.title.text or ""
    if not limpio or not texto:
        return fig
    marca = "<br><span"
    if marca not in texto:
        fig.update_layout(title_text="<b>%s</b>" % limpio)
        return fig
    cabeza, resto = texto.split(marca, 1)
    hallazgo = cabeza.replace("<b>", "").replace("</b>", "").strip()
    sub = resto.split(">", 1)[1].rsplit("</span>", 1)[0].replace("<br>", " ").strip()
    n_antes = resto.count("<br>") + 1
    if hallazgo and hallazgo[-1] not in ".:;":
        hallazgo += "."
    T = _roles()
    for cod in T.get("escalera", []):
        nom = T["nombre"].get(cod, cod)
        if nom != cod and len(cod) <= 2:
            hallazgo = re.sub("(?<![A-Za-z0-9-])" + cod + "(?![A-Za-z0-9-])", "%s «%s»" % (cod, nom), hallazgo, count=1)
    nuevo = _envolver(("<b>%s</b> %s" % (hallazgo, sub)).strip())
    n_despues = nuevo.count("<br>") + 1
    delta = n_despues - n_antes
    fig.update_layout(title_text="<b>%s</b><br><span style='font-size:13px;color:%s'>%s</span>" % (limpio, TINTA_2, nuevo))
    alto = fig.layout.height or 520
    m = fig.layout.margin
    t_actual = (m.t if m and m.t else 108) + 20 * delta
    subpaneles = any(a.yref == "paper" and (a.y or 0) >= 0.98 for a in fig.layout.annotations)
    t_necesario = 88 + 22 * (n_despues + 1) + (34 if subpaneles else 0)
    fig.update_layout(height=alto + 18 * delta + max(0, t_necesario - t_actual), margin=dict(t=max(t_actual, t_necesario)))
    return fig


FIGURAS = [
    ("g00_indicadores", "Indicadores para la decisión", f_indicadores),
    ("g19_comparacion", "Comparación de escenarios", f_comparacion),
    ("g01_itmos_area", "Oferta de Artículo 6 por tramo", f_itmos_area),
    ("g02_potencial", "Composición de la oferta y volumen transferible", f_potencial),
    ("g03_energia_escenarios", "Emisiones del sector energía", f_energia_escenarios),
    ("g04_reduccion_anual", "Reducción anual frente al condicional", f_reduccion_anual),
    ("g05_emisiones_generacion", "Emisiones de la generación eléctrica", f_emisiones_generacion),
    ("g06_subsectores", "Emisiones por subsector", f_subsectores),
    ("g07_generacion", "Generación por tipo de planta", f_generacion),
    ("g08_capacidad", "Capacidad por tipo de planta", f_capacidad),
    ("g09_ernc", "Participación de la ERNC", f_ernc),
    ("g11_peso_energia", "Peso del sector energía", f_peso_energia),
    ("g12_cascada_headroom", "Cascada del margen nacional", f_cascada),
    ("g13_sobreventa_area", "Balance nacional con la transferencia", f_sobreventa_area),
    ("g14_headroom_riesgos", "Margen por escenario y riesgo", f_headroom_riesgos),
    ("g15_headroom_trayectoria", "Margen por año y riesgo", f_headroom_trayectoria),
    ("g16_volumenes", "Volúmenes transferibles por riesgo", f_volumenes),
    ("g17_ingresos", "Ingresos potenciales", f_ingresos),
    ("g18_referencias", "Tendencial, metas e inventario", f_referencias),
    ("g20_escalera", "Escalera de capas", f_escalera),
]


def lecturas(D):
    """Guia de lectura de cada grafica (guias.py), con las cifras de la corrida."""
    import guias
    return guias.guias(D)


def estado_corrida():
    """Linea para el cuaderno: que corrida de B1 se esta mostrando (salidas de Executables)."""
    R = analizar.resultados()
    c = R.get("corrida", {})
    txt = ("Corrida mostrada: salidas de B1 en Executables (última: %s) con %d escenarios con solución óptima; el "
           "análisis está al día con ellas." % (c.get("salidas"), len(c.get("escenarios", []))))
    if R.get("faltan"):
        txt += " Sin solución óptima en la corrida: %s." % C.enumerar(R["faltan"])
    sin = R.get("roles", {}).get("sin_descripcion")
    if sin:
        txt += " Sin descripción en Art6_Escenarios (se muestran con su código): %s." % C.enumerar(sin)
    return txt


def _chrome():
    import os
    import shutil
    for p in (r"C:\Program Files\Google\Chrome\Application\chrome.exe",
              r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
              r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
              r"C:\Program Files\Microsoft\Edge\Application\msedge.exe"):
        if os.path.exists(p):
            return p
    return shutil.which("chrome") or shutil.which("msedge")


def exportar_png(figs):
    """PNG de cada grafica para el informe Word: Chrome sin ventana captura una copia estatica (sin
    botones ni deslizadores). Se usa Chrome porque kaleido 0.2.1 se cuelga en Windows."""
    import subprocess
    import tempfile
    from pathlib import Path
    from plotly.offline import get_plotlyjs
    nav = _chrome()
    if not nav:
        print("  sin Chrome ni Edge: no se generan PNG (las gráficas siguen en el cuaderno)")
        return
    C.GRAFICAS.mkdir(parents=True, exist_ok=True)
    tmp = Path(tempfile.mkdtemp(prefix="art6_png_"))
    (tmp / "plotly.min.js").write_text(get_plotlyjs(), encoding="utf-8")
    hechas = 0
    for gid, fig in figs.items():
        lay = fig.layout.to_plotly_json()
        for k in ("updatemenus", "sliders"):
            lay.pop(k, None)
        g = go.Figure(data=fig.data, layout=lay)
        m = g.layout.margin
        franja = 36 if fig.layout.updatemenus else 0
        g.update_layout(width=1200, margin=dict(t=max(95, int(m.t or 108) - franja), l=m.l, r=m.r, b=m.b))
        alto = int(g.layout.height or 520)
        g.update_xaxes(rangeslider_visible=False)
        html = tmp / (gid + ".html")
        g.write_html(str(html), include_plotlyjs="plotly.min.js", full_html=True,
                     config={"displayModeBar": False, "staticPlot": True})
        destino = C.GRAFICAS / (gid + ".png")
        try:
            subprocess.run([nav, "--headless=new", "--disable-gpu", "--hide-scrollbars",
                            "--force-device-scale-factor=2", "--window-size=1220,%d" % (alto + 20),
                            "--virtual-time-budget=4000", "--screenshot=%s" % destino, html.as_uri()],
                           timeout=90, capture_output=True)
            hechas += destino.exists()
        except subprocess.TimeoutExpired:
            print("  PNG no generado (%s): Chrome tardó demasiado" % gid)
    print("  %d gráficas PNG en %s" % (hechas, C.GRAFICAS))


def exportar_png_informe(figs, ancho=900, fuente=16):
    """PNG para el informe Word (guia de graficas de la skill diseno-informes): sin bloque de titulo
    ni botones, ancho de impresion, letra mayor, leyenda abajo. Salida en graficas/informe/<gid>.png."""
    import subprocess
    import tempfile
    from pathlib import Path
    from plotly.offline import get_plotlyjs
    nav = _chrome()
    if not nav:
        print("  sin Chrome ni Edge: no se generan PNG de informe")
        return
    dest = C.GRAFICAS / "informe"
    dest.mkdir(parents=True, exist_ok=True)
    tmp = Path(tempfile.mkdtemp(prefix="art6_inf_"))
    (tmp / "plotly.min.js").write_text(get_plotlyjs(), encoding="utf-8")
    hechas = 0
    for gid, fig in figs.items():
        if _es_impresion(fig):              # version de impresion (IMPRESION): ya trae ancho, alto, letra y margenes
            g = fig
            ancho_g, alto = int(fig.layout.width or ancho), int(fig.layout.height or 520)
        else:
            lay = fig.layout.to_plotly_json()
            for k in ("updatemenus", "sliders", "title"):
                lay.pop(k, None)
            g = go.Figure(data=fig.data, layout=lay)
            m = g.layout.margin
            alto_base = int(fig.layout.height or 520)
            t_viejo = int(m.t or 108)
            extra = 20 if (g.layout.annotations and any(a.yref == "paper" and (a.y or 0) >= 0.98 for a in g.layout.annotations)) else 0
            alto = alto_base - t_viejo + 30 + extra
            ancho_g = ancho
            g.update_layout(width=ancho, height=alto, margin=dict(t=30 + extra, l=m.l, r=m.r, b=m.b),
                            font=dict(size=fuente), title_text="", legend=dict(font=dict(size=fuente - 1)))
            g.update_xaxes(rangeslider_visible=False, tickfont=dict(size=fuente - 1), title_font=dict(size=fuente - 1))
            g.update_yaxes(tickfont=dict(size=fuente - 1), title_font=dict(size=fuente - 1))
        html = tmp / (gid + ".html")
        g.write_html(str(html), include_plotlyjs="plotly.min.js", full_html=True,
                     config={"displayModeBar": False, "staticPlot": True})
        destino = dest / (gid + ".png")
        try:
            subprocess.run([nav, "--headless=new", "--disable-gpu", "--hide-scrollbars",
                            "--force-device-scale-factor=2", "--window-size=%d,%d" % (ancho_g + 20, alto + 20),
                            "--virtual-time-budget=4000", "--screenshot=%s" % destino, html.as_uri()],
                           timeout=90, capture_output=True)
            hechas += destino.exists()
        except subprocess.TimeoutExpired:
            print("  PNG de informe no generado (%s): Chrome tardó demasiado" % gid)
    print("  %d gráficas PNG de informe en %s" % (hechas, dest))


def generar(png=True):
    D = Datos()
    figs = {gid: retitular(f(D), gid) for gid, _, f in FIGURAS}
    if png:
        exportar_png(figs)
        exportar_png_informe({gid: (IMPRESION[gid](D) if gid in IMPRESION else fig) for gid, fig in figs.items()})
    return figs, lecturas(D)


def exportar_informe(gids=None):
    """Regenera solo las PNG de informe de `gids` (por omision, las versiones de impresion de IMPRESION) sin recalcular el
    analisis: lee resultados_art6.json y las tablas tal como estan y no escribe nada fuera de graficas/informe. Se niega
    si el analisis no esta al dia con sus origenes, porque entonces Datos() lo rehaceria."""
    if not analizar.vigente():
        raise SystemExit("El análisis no está al día con sus orígenes: corra B3 completo antes de regenerar las PNG.")
    D = Datos()
    por_gid = {gid: f for gid, _, f in FIGURAS}
    figs = {}
    for gid in (gids or list(IMPRESION)):
        figs[gid] = IMPRESION[gid](D) if gid in IMPRESION else retitular(por_gid[gid](D), gid)
    exportar_png_informe(figs)
    return figs


def exportar_html(F, L):
    """docs/_static/interactivas/<gid>.html: cada grafica sola, para incrustarla en la documentacion.
    El tablero completo lo arma tablero.py."""
    dest = C.DOCS / "_static" / "interactivas"
    dest.mkdir(parents=True, exist_ok=True)
    for gid, _, _ in FIGURAS:
        F[gid].write_html(str(dest / (gid + ".html")), include_plotlyjs="cdn", full_html=True, config=CONFIG)


def mostrar(F, L, gid):
    from IPython.display import HTML, display
    import guias
    if gid in L:
        display(HTML(guias.html(L[gid])))
    F[gid].show(config=CONFIG)


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "--informe":     # python graficar.py --informe [gid ...]
        exportar_informe(sys.argv[2:] or None)
    else:
        generar()
