# -*- coding: utf-8 -*-
"""Descripcion de los escenarios de Articulo 6 para quien decide.

mapa_html()      Como se relacionan los escenarios: la escalera de capas (cada escenario contiene al
                 anterior) y la matriz de los escenarios de Articulo 6 bajo cada prueba de estres y
                 la sensibilidad.
fichas_html()    Una ficha por escenario o prueba, siempre en el mismo orden: que representa, que
                 lineas contiene, que cambia frente a su base, que resulta y que implica para el
                 Articulo 6.
supuestos_html() Matriz tecnica de los parametros de entrada de 2035 por escenario.

Nada se escribe a mano. Las cifras de resultado salen de la salida de B1 de cada escenario
(Executables/<ESC>_0/<ESC>_0_Output.csv) a traves de analizar.resultados(), que recalcula el analisis si la
corrida cambio; los parametros de entrada y el anio desde el que rige cada cambio, del _Input.csv de cada
escenario; los nombres, narrativas, lineas, veredictos, riesgos y fuentes, de las hojas Art6_* de
B1_Scenario_Config.xlsx (hojas Art6_*). Los textos fijos de este modulo definen conceptos; toda frase que depende de
un resultado se arma con la cifra y su condicion.

Los escenarios se clasifican por su definicion en la configuracion: referencias (B1 las genera sin base: los
escenarios del Modelo Climate Lead Group y las referencias corregidas del Articulo 6, INCA6 y CONA6), escenarios
de Articulo 6 (su base es el escenario de Articulo 6 cuyas
palancas contienen, o la referencia de la que parten) y estados aplicados a cada uno, por la
convencion de codigo <escenario>-<estado> (A-CCOFF, B-FOI...).
"""
import html as H
from functools import lru_cache

import pandas as pd

import analizar
import comun as C
import configuracion as K
import graficar
NEUTRO = "#9CA3AF"
FUENTE_SALIDAS = ("salidas de B1 de cada escenario (Energy/Executables/&lt;ESC&gt;_0/&lt;ESC&gt;_0_Output.csv e _Input.csv) del "
                  "Modelo Climate Lead Group en la rama art6-escenarios de ECU_NDC")
VARIANTE = C.ENERGY / "Art6_calibracion" / "calibracion_h_suficiencia_escenarios_art6.csv"


class _Color(dict):
    """Color de cada escenario segun su papel en la corrida (graficar.estilo_escenario)."""
    def get(self, c, defecto=None):
        try:
            return graficar.estilo_escenario(c)[1]
        except Exception:
            return defecto


COLOR = _Color()
FINO = " "
V = C.VENTANA
VENT = "%d-%d" % (V[0], V[-1])
SIN_TECHO = 900.0           # PJ/año: el modelo marca "sin limite" con techos muy por encima de este valor
INF = float("inf")
N = {2: "dos", 3: "tres", 4: "cuatro", 5: "cinco", 6: "seis", 7: "siete", 8: "ocho", 9: "nueve", 10: "diez",
     11: "once", 12: "doce"}
TIPO = {"Referencia NDC": "Referencia de la NDC", "Escenario Art. 6": "Escenario de Artículo 6",
        "Riesgo": "Riesgo", "Sensibilidad": "Riesgo de operación"}
PAR = {C.TECHO: "techo", C.PISO: "piso"}
# vocabulario de presentacion: como se nombra la generacion de cada tecnologia dentro de una frase
GEN_PALANCA = {"Eólica": "eólica", "Solar": "solar", "Geotermia": "geotérmica", "Biomasa y biogás": "con biomasa",
               "Fuel oil": "con fuel oil", "Hidroeléctrica": "hidroeléctrica"}
GEN_FAMILIA = {"Biomasa y biogás": "con biomasa y biogás", "Geotermia": "geotérmica", "Eólica": "eólica",
               "Solar": "solar", "Hidroeléctrica": "hidroeléctrica"}
GWH_DE = {"Hidroeléctrica": "hidroeléctricos", "Gas natural": "de gas natural", "Eólica": "eólicos",
          "Solar": "solares", "Crudo, GLP e importación": "de crudo, GLP e importación",
          "Biomasa y biogás": "de biomasa y biogás", "Geotermia": "geotérmicos",
          "Fuel oil y diésel": "de fuel oil y diésel"}
VEREDICTO = {"Núcleo": "ab-v-nucleo", "Condicionada": "ab-v-cond", "Descartar": "ab-v-desc"}
COMPONENTE = {"CO2e_DE": "demanda final", "CO2e_PP": "generación eléctrica", "CO2e_FUG": "fugitivas",
              "CO2e_REF": "refinación"}


# ----------------------------------------------------------------------------- formato
def _n(v, dec=0):
    """Miles con espacio fino, coma decimal y signo menos tipografico."""
    s = ("{:,.%df}" % dec).format(abs(v)).replace(",", FINO).replace(".", ",")
    return ("−" if round(v, dec) < 0 else "") + s


def _cuantos(n, fem=False):
    return ("una" if fem else "un") if n == 1 else N.get(n, str(n))


_tramos = C.tramos


_y = C.enumerar


def _minus(s):
    """Primera letra en minuscula, salvo que empiece por una sigla (CCOFF, NDC)."""
    return s[:1].lower() + s[1:] if len(s) > 1 and s[1:2].islower() else s


def _cod(c):
    """Codigo del escenario tal como esta en la configuracion y en Executables, sin transliterar."""
    return str(c)


def _esc(s):
    return H.escape(str(s or "")).strip()


def _igual(x, y):
    if pd.isna(x) and pd.isna(y):
        return True
    if pd.isna(x) or pd.isna(y):
        return False
    if x == INF or y == INF:
        return x == y
    return abs(x - y) <= 1e-6 * max(1.0, abs(x), abs(y))


# ----------------------------------------------------------------------------- datos de la corrida
def _datos():
    analizar.resultados()                    # recalcula el analisis si cambio alguna salida de B1
    return _armar(C.huella(analizar.JSON, C.CONFIG, C.ART6_CONFIG))


@lru_cache(maxsize=2)
def _entrada(huella, tecs):
    """Parametros del _Input.csv de cada escenario por tecnologia y anio, y bloques horarios del modelo."""
    I = C.leer_ecuinput([C.PISO, C.TECHO, C.FP, "Season"], list(analizar.resultados()["corrida"]["escenarios"]))
    bloques = tuple(sorted(str(s) for s in I["Season"].dropna().unique()))
    I = I[I["Technology"].isin(tecs)]
    return I.groupby(["Strategy", "Technology", "Year"])[[C.PISO, C.TECHO, C.FP]].mean(), bloques


@lru_cache(maxsize=2)
def _armar(huella):
    R = analizar.resultados()
    E = K.escenarios()
    por = {e["codigo"]: e for e in E}
    hay = set(R["emisiones_kt"])
    D = {"R": R, "por": por,
         "em": pd.DataFrame(R["emisiones_kt"], index=R["anios"]),
         "vol": {(v["escenario"], v["regla"]): float(v["total_2031_2035"]) for v in R["volumenes"]},
         "hr": {(h["escenario"], h["regla"]): h for h in R["headroom"]},
         "desp": R["termica_desplazable_GWh"], "egf": R["emisiones_generacion_familia_kt"],
         "capas": {(d["referencia"], d["escenario"]): d["componente"] for d in R["descomposicion"]},
         "P": K.palancas(), "AD": K.hoja("Adicionalidad"), "RG": K.hoja("Riesgos"),
         "fuentes": K.hoja("Fuentes"), "headroom": {h["parametro"]: h for h in K.hoja("Headroom")}}
    gen = pd.read_csv(C.TABLAS / "generacion_familia.csv")
    cap = pd.read_csv(C.TABLAS / "capacidad_familia.csv")
    D["gen"] = gen.pivot_table(index=["escenario", "anio"], columns="familia", values="GWh", aggfunc="sum")
    D["cap"] = cap.pivot_table(index=["escenario", "anio"], columns="familia", values="MW", aggfunc="sum")

    # clasificacion de los escenarios por su definicion en la configuracion
    D["refs"] = [e["codigo"] for e in E if e["base"] == "B1" and e["codigo"] in hay]
    D["art6"] = [e["codigo"] for e in E if e["grupo"] == "Escenario Art. 6" and e["codigo"] in hay]
    base = {}
    for c in D["art6"]:
        g = set(K.grupos_de(por[c]))
        previos = [x for x in D["art6"] if set(K.grupos_de(por[x])) < g]
        base[c] = max(previos, key=lambda x: len(K.grupos_de(por[x]))) if previos else por[c]["base"]
    estados = []
    for e in E:
        cod = e["codigo"]
        if "-" not in cod or cod not in hay or e["grupo"] == "Puente":
            continue
        fam, est = cod.split("-", 1)
        if fam not in hay:                  # prueba sobre un escenario que la corrida no trae: sin base que comparar
            continue
        d = next((x for x in estados if x["codigo"] == est), None)
        if d is None:
            grupos = set(K.grupos_de(e)) - set(K.grupos_de(por[fam]))
            partes = {p for g in grupos for p in g.split("_")}
            nombre = K.rotulo(est, e["nombre"].split(" · ", 1)[-1])
            d = {"codigo": est, "nombre": nombre[:1].upper() + nombre[1:], "grupo": e["grupo"],
                 "frase": K.FRASES.get(est, _minus(nombre)),
                 "grupos": grupos, "miembros": {}, "riesgos": [r for r in D["RG"] if r["grupo"] in partes]}
            estados.append(d)
        d["miembros"][fam] = cod
        base[cod] = fam
    D["estados"], D["base"] = estados, base

    # tecnologias que mueven las palancas: limites de actividad y factores de planta hidroelectricos
    P = D["P"]
    D["fam_palanca"] = {p["tecnologia"]: p["familia"] for p in P}
    D["tecs_act"] = list(dict.fromkeys(p["tecnologia"] for p in P
                                       if p["familia"] != "Hidroeléctrica" and p["parametro"] in (C.PISO, C.TECHO)))
    D["palancas_act"] = {(p["tecnologia"], p["parametro"]) for p in P}
    D["clases"] = list(K.anoseco()) or list(dict.fromkeys(p["tecnologia"] for p in P
                                                          if p["familia"] == "Hidroeléctrica"))
    D["centrales"] = {f["Clase"]: f["Centrales o clase de origen"] for f in K.hoja("AnoSeco")
                      if str(f.get("Clase") or "").startswith("PP") and f.get("Criterio") == "medida"}
    cf_por_grupo = {}
    for p in P:
        if p["parametro"] == C.FP:
            cf_por_grupo.setdefault(p["grupo"], set()).add(p["tecnologia"])
    D["fp_propias"] = list(dict.fromkeys(t for g in cf_por_grupo.values() if len(g) <= 2 for t in sorted(g)))
    D["G"], D["bloques"] = _entrada(C.huella(analizar.JSON), tuple(D["tecs_act"] + D["clases"]))

    # anios en que el escenario pasa energia por STOELE (falta de potencia con el tope K15b activo: emisiones
    # subestimadas) y variante diagnostica de potencia minima (Art6_calibracion/suficiencia_escenarios_art6.py)
    D["stoele"], D["en_tope"] = {}, {}
    suf = C.TABLAS / "suficiencia_por_escenario.csv"
    if suf.exists():
        s = pd.read_csv(suf, keep_default_na=False, na_values=[""])
        for r in s[s["STOELE_GWh"] > 0.5].itertuples():
            D["stoele"].setdefault(r.escenario, {})[int(r.anio)] = float(r.STOELE_GWh)
            D["en_tope"].setdefault(r.escenario, {})[int(r.anio)] = str(r.en_tope or "")
    D["variante"] = pd.read_csv(VARIANTE) if VARIANTE.exists() else None
    return D


def _serie(D, esc, tec, par):
    try:
        s = D["G"].loc[(esc, tec)][par]
    except KeyError:
        return pd.Series(float("nan"), index=C.ANIOS)
    return s.reindex(C.ANIOS)


def _nombre(D, c):
    e = D["por"].get(c)
    return e["nombre"] if e else c


def _art(D, c):
    """«la NDC condicional», «el A» o «el escenario «Ambición ampliada»»: el nombre con su articulo."""
    n = _nombre(D, c)
    if n.startswith("NDC"):
        return "la " + n
    return ("el " + n) if n == c or len(n) <= 4 else "el escenario «%s»" % n


def _con_prep(D, c, prep):
    """«del Escenario A», «al Escenario A», «en el Escenario A», «de la NDC condicional»..."""
    a = _art(D, c)
    if a.startswith("el ") and prep in ("de", "a"):
        return {"de": "del ", "a": "al "}[prep] + a[3:]
    return prep + " " + a


def _de(D, c):
    return _con_prep(D, c, "de")


def _a(D, c):
    return _con_prep(D, c, "a")


def _en(D, c):
    return _con_prep(D, c, "en")


def _em(D, c, a=2035):
    return float(D["em"][c][a])


def _capa(D, b, c, a=None):
    """Reduccion de c frente a b, un anio o la ventana completa, redondeada como las tablas del analisis."""
    anios = [a] if a else V
    return round(sum(float(D["em"][b][x] - D["em"][c][x]) for x in anios), 1)


def _vol(D, c, regla="adicional_a_la_NDC"):
    return D["vol"].get((c, regla))


def _hr(D, c, regla="condicional", a=2035):
    h = D["hr"].get((c, regla))
    return None if h is None else float(h[str(a)])


def _gen(D, c, fam, anios=(2035,)):
    try:
        return float(sum(D["gen"].loc[(c, a), fam] for a in anios))
    except KeyError:
        return 0.0


def _mw(D, c, fam, a=2035):
    try:
        return float(D["cap"].loc[(c, a), fam])
    except KeyError:
        return 0.0


def _gen_total(D, c, a=2035):
    try:
        return float(D["gen"].loc[(c, a)].sum())
    except KeyError:
        return 0.0


def _desp(D, c, a=2035):
    return float(D["desp"][c][C.IDX[a]]) if c in D["desp"] else 0.0


def _regla(D, prudente=False):
    if prudente:
        return "los otros sectores solo en su tramo incondicional"
    publicadas = D["R"].get("reglas_headroom", {}).get("regla_nacional") == "meta_condicional"
    return ("los otros sectores en el condicional que la NDC compromete" if publicadas else
            "los otros sectores en su condicional modelado")


def _lineas(D, c, exacto=True):
    """Lineas de Art6_Adicionalidad de un escenario de Articulo 6; exacto=False suma las que el
    modelo no representa ("A (fuera del modelo)")."""
    out = []
    for x in D["AD"]:
        v = str(x.get("escenario_art6") or "")
        if v == c or (not exacto and v.split(" ")[0] == c):
            out.append(x)
    return out


def _kt(x):
    v = x.get("kt_anio_declarado")
    return float(v) if isinstance(v, (int, float)) else 0.0


# ----------------------------------------------------------------------------- cambios de entrada
def _cambios(D, c, b):
    """Parametros de entrada de c que difieren de su base b en los _Input.csv: limites de actividad
    que mueven las palancas y factores de planta hidroelectricos."""
    filas = []
    for tec in D["tecs_act"]:
        for par in (C.TECHO, C.PISO):
            if (tec, par) not in D["palancas_act"]:
                continue
            rel = 0.0 if par == C.PISO else INF
            e, s = _serie(D, c, tec, par).fillna(rel), _serie(D, b, tec, par).fillna(rel)
            if par == C.TECHO:
                e, s = e.where(e < SIN_TECHO, INF), s.where(s < SIN_TECHO, INF)
            dif = [a for a in C.ANIOS if not _igual(e[a], s[a])]
            if dif:
                fam = D["fam_palanca"].get(tec, "")
                filas.append(dict(_tiempos(e, dif[0]), tipo="act", tec=tec, par=par, fam=fam, base=s[2035],
                                  esc=e[2035], etiqueta="%s de generación %s" % (
                                      PAR[par].capitalize(), GEN_PALANCA.get(fam, "de " + fam.lower()))))
    fe = pd.DataFrame({k: _serie(D, c, k, C.FP) for k in D["clases"]})
    fb = pd.DataFrame({k: _serie(D, b, k, C.FP) for k in D["clases"]})
    cambian = [k for k in D["clases"] if any(not _igual(fe[k][a], fb[k][a]) for a in C.ANIOS)]
    if cambian:
        propias = [k for k in cambian if k in D["fp_propias"]] or (cambian if len(cambian) <= 2 else [])
        for k in propias:
            dif = [a for a in C.ANIOS if not _igual(fe[k][a], fb[k][a])]
            nom = D["centrales"].get(k)
            filas.append(dict(_tiempos(fe[k], dif[0]), tipo="fp", tec=k, base=fb[k][2035], esc=fe[k][2035],
                              etiqueta="Factor de planta de %s" % ("%s (%s)" % (nom, k) if nom else "la clase " + k)))
        me, mb = fe.mean(axis=1), fb.mean(axis=1)
        dif = [a for a in C.ANIOS if not _igual(me[a], mb[a])]
        if dif:
            filas.append(dict(_tiempos(me, dif[0]), tipo="fp", tec="medio", base=mb[2035], esc=me[2035],
                              etiqueta="Factor de planta medio de las %s clases hidroeléctricas"
                                       % _cuantos(len(D["clases"]), fem=True)))
    return filas


def _tiempos(e, a0):
    """Primer anio con cambio y anio desde el que rige el valor de 2035; rampa si en ese tramo el
    parametro toma mas de dos valores."""
    fin = C.ANIOS[-1]
    a1 = next(a for a in C.ANIOS if a >= a0 and all(_igual(e[x], e[fin]) for x in C.ANIOS if x >= a))
    distintos = []
    for a in range(a0, a1 + 1):
        if not any(_igual(e[a], v) for v in distintos):
            distintos.append(e[a])
    return {"desde": a0, "final": a1, "rampa": len(distintos) > 2}


def _cuando(f):
    a0, a1 = f["desde"], f["final"]
    if a1 <= a0:
        return "%d" % a0
    if f["rampa"]:
        return "%d, en rampa hasta %d" % (a0, a1)
    return "%d; valor final desde %d" % (a0, a1)


def _valor(f, v, corto=False):
    if f["tipo"] == "act":
        if v == INF:
            return "sin techo"
        gwh = "%s GWh" % _n(v * C.PJ_A_GWH)
        return gwh if corto else "%s <span class='es-pj'>%s PJ</span>" % (gwh, _n(v, 2))
    return _n(v, 3)


def _desde(filas):
    return min(f["desde"] for f in filas) if filas else None


def _tabla_cambios(filas, nb, ne):
    if not filas:
        return "<p class='ab-nota'>Sin diferencias en los parámetros que mueven las palancas.</p>"
    cuerpo = "".join("<tr><th scope='row'>%s</th><td>%s</td><td>%s</td><td class='es-cuando'>%s</td></tr>"
                     % (f["etiqueta"], _valor(f, f["base"]), _valor(f, f["esc"]), _cuando(f)) for f in filas)
    return ("<table class='es-tabla'><thead><tr><th scope='col'>Parámetro en 2035</th><th scope='col'>%s</th>"
            "<th scope='col'>%s</th><th scope='col'>Desde</th></tr></thead><tbody>%s</tbody></table>"
            % (_esc(nb), _esc(ne), cuerpo))


def _origen_referencia(D, c):
    """(rotulo de la base, que cambia) de una referencia segun su grupo en Art6_Escenarios: escenario del Modelo
    Climate Lead Group sin cambios, o referencia corregida del Articulo 6 (el escenario del Modelo CLG con las
    correcciones K01-K15)."""
    roles = D["R"].get("roles", {})
    clg = {roles.get("inc"): roles.get("inc_clg"), roles.get("con"): roles.get("con_clg")}
    if str(D["por"].get(c, {}).get("grupo") or "") == "Referencia corregida":
        return ("Referencia corregida del Artículo 6",
                "%s del Modelo CLG con las correcciones K01-K15 (base congelada), sin palancas de Artículo 6."
                % (clg.get(c) or "Escenario"))
    return ("Escenario del Modelo CLG", "Escenario del Modelo Climate Lead Group sin cambios, sin palancas de Artículo 6.")


def _resumen_cambios(D, c):
    """Frase corta de lo que cambia c frente a su base, para la matriz de supuestos."""
    if c in D["refs"]:
        return _origen_referencia(D, c)[1]
    b = D["base"][c]
    filas = _cambios(D, c, b)
    if not filas:
        return "Igual %s." % _a(D, b)
    partes = ["%s a %s desde %d" % (_minus(f["etiqueta"]), _valor(f, f["esc"], corto=True), f["desde"])
              for f in filas]
    return "Frente %s: %s." % (_a(D, b), "; ".join(partes))


# ----------------------------------------------------------------------------- piezas comunes
def _cifras(items):
    """Bloque de cifras: [(etiqueta, valor, nota)]."""
    return "<div class='es-cifras'>%s</div>" % "".join(
        "<div><span>%s</span><b>%s</b>%s</div>" % (et, v, "<small>%s</small>" % nota if nota else "")
        for et, v, nota in items if v is not None)


def _kt_txt(v):
    return "s. d." if v is None else _n(v) + " kt"


def _veredicto(v):
    if not v:
        return "<span class='ab-sello ab-fuera'>Sin veredicto</span>"
    return "<span class='ab-sello %s'>%s</span>" % (VEREDICTO.get(v, "ab-fuera"), _esc(v))


def _bloque_lineas(L, fuera=()):
    """Lineas agrupadas por veredicto y argumento (Art6_Adicionalidad)."""
    grupos = {}
    for x in list(L) + list(fuera):
        clave = (x.get("veredicto_compradores") or "", x.get("argumento") or "", x in fuera)
        grupos.setdefault(clave, []).append(x)
    orden = {"Núcleo": 0, "Condicionada": 1, "Descartar": 2, "": 3}
    items = []
    for (v, arg, fue), xs in sorted(grupos.items(), key=lambda kv: (kv[0][2], orden.get(kv[0][0], 4))):
        nombres = _y(["%s <span class='ab-cod'>%s</span>" % (_esc(x["linea"]), _esc(x["codigo"])) for x in xs])
        items.append("<li>%s%s <span class='es-nombres'>%s</span><p>%s</p></li>" % (
            _veredicto(v), " <span class='es-fuera'>fuera del modelo: volumen declarado</span>" if fue else "",
            nombres, _esc(arg)))
    return "<ul class='es-lineas'>%s</ul>" % "".join(items)


def _ficha(ident, colores, titulo, cods, tipo, base, izq, der):
    puntos = "".join("<span class='ab-punto' style='background:%s'></span>" % col for col in colores)
    chips = "".join("<span class='ab-cod'>%s</span>" % _cod(c) for c in cods)
    dl = "".join("<dt>%s</dt><dd>%s</dd>" % (_esc(t), h) for t, h in izq if h)
    return ("<article class='es-ficha' id='ficha-%s'><header>%s<h4>%s</h4>%s<span class='es-tipo'>%s</span>%s</header>"
            "<div class='es-cuerpo'><dl>%s</dl><div class='es-datos'>%s</div></div></article>"
            % (ident, puntos, _esc(titulo), chips, _esc(tipo),
               "<span class='es-base'>%s</span>" % base if base else "", dl, "".join(der)))


def _seccion(titulo, cuerpo):
    return "<section><h5>%s</h5>%s</section>" % (_esc(titulo), cuerpo) if cuerpo else ""


def _lista(xs):
    return "<ul>%s</ul>" % "".join("<li>%s</li>" % x for x in xs if x)


def _tabla_generacion(D, c, b, fams_palanca):
    tot = _gen_total(D, c) or 1.0
    fams = [f for f, _, _ in C.FAMILIAS
            if f in fams_palanca or abs(_gen(D, c, f) - _gen(D, b, f)) >= 0.005 * tot]
    if not fams:
        return ""
    filas = "".join("<tr><th scope='row'>%s</th><td>%s</td><td>%s</td><td>%s</td><td>%s → %s</td></tr>"
                    % (f, _n(_gen(D, b, f)), _n(_gen(D, c, f)), _n(_gen(D, c, f) - _gen(D, b, f)),
                       _n(_mw(D, b, f)), _n(_mw(D, c, f))) for f in fams)
    return ("<table class='es-tabla'><thead><tr><th scope='col'>Generación en 2035</th><th scope='col'>%s, GWh</th>"
            "<th scope='col'>%s, GWh</th><th scope='col'>Diferencia</th><th scope='col'>Capacidad, MW</th></tr>"
            "</thead><tbody>%s</tbody></table>" % (_esc(_nombre(D, b)), _esc(_nombre(D, c)), filas))


def _detalle_palancas(D, grupos):
    """Palancas del escenario: una fila por palanca, y una por riesgo en los riesgos hidrologicos."""
    P = [p for p in D["P"] if p["grupo"] in grupos]
    if not P:
        return ""
    RA = K.riesgos_agrupados(D["P"])
    filas = []
    for g in dict.fromkeys(p["grupo"] for p in P):
        if g in RA:
            r = RA[g]
            filas.append("<tr><th scope='row'>%s (%d)</th><td>%s. %s</td><td>%s</td></tr>"
                         % (_esc(r["rango"]), r["n"], _esc(r["nombre"]), _esc(r["mecanismo"]), _esc(r["fuente"])))
        else:
            filas += ["<tr><th scope='row'>%s</th><td>%s</td><td>%s</td></tr>"
                      % (_esc(p["id"]), _esc(p["descripcion"]), _esc(p["fuente"])) for p in P if p["grupo"] == g]
    filas = "".join(filas)
    return ("<details class='es-detalle'><summary>Palancas en B1_Scenario_Config.xlsx (%d)</summary>"
            "<table class='es-tabla es-texto'><thead><tr><th scope='col'>Palanca</th><th scope='col'>Qué fija</th>"
            "<th scope='col'>Fuente</th></tr></thead><tbody>%s</tbody></table></details>" % (len(P), filas))


# ----------------------------------------------------------------------------- mapa
def _nivel(D, c):
    """Valor de escenario_NDC (Art6_Adicionalidad) que corresponde a una referencia."""
    return "Incondicional" if "incondicional" in _nombre(D, c).lower() else "Condicional"


def _consecuencia(D, b, c):
    if c in D["refs"]:
        return "ab-consume", "Es la meta condicional"
    ndc = {str(x.get("escenario_NDC") or "") for x in _lineas(D, c, exacto=False)}
    if ndc and ndc <= {"Condicional"}:
        return "ab-consume", "Descuenta de la meta condicional"
    if ndc and ndc <= {"Fuera de la NDC"}:
        return "ab-libre", "No consume metas"
    return "ab-fuera", "Consecuencia mixta"


def _pasos(D):
    return D["refs"] + D["art6"]


def _escalera(D):
    pasos, piezas = _pasos(D), []
    for i, c in enumerate(pasos):
        if i:
            b = pasos[i - 1]
            cls, sello = _consecuencia(D, b, c)
            piezas.append("<div class='es-capa'><span class='es-flecha' aria-hidden='true'>+</span><b>%s</b>"
                          "<span class='es-kt'>%s kt</span><span class='ab-sello %s'>%s</span></div>"
                          % (_esc(D["capas"].get((b, c), "%s frente a %s" % (_cod(c), _cod(b)))),
                             _n(_capa(D, b, c)), cls, sello))
        e = D["por"][c]
        piezas.append("<div class='es-paso' style='border-top-color:%s'><span class='es-tipo'>%s</span><b>%s</b>"
                      "<span class='ab-cod'>%s</span></div>"
                      % (COLOR.get(c, NEUTRO), _esc(TIPO.get(e["grupo"], e["grupo"])), _esc(e["nombre"]), _cod(c)))
    return "<div class='es-escalera'>%s</div>" % "".join(piezas)


def _barra(D):
    pasos = _pasos(D)
    segs = [(D["capas"].get((b, c), _cod(c)), c, max(0.0, _capa(D, b, c))) for b, c in zip(pasos, pasos[1:])]
    tot = sum(s[2] for s in segs) or 1.0
    barra = "".join("<span style='width:%.2f%%;background:%s' title='%s: %s kt'></span>"
                    % (100.0 * kt / tot, COLOR.get(c, NEUTRO), _esc(n), _n(kt)) for n, c, kt in segs)
    ley = "".join("<span><i style='background:%s'></i>%s · %s %%</span>"
                  % (COLOR.get(c, NEUTRO), _esc(n), _n(100.0 * kt / tot)) for n, c, kt in segs)
    return ("<div class='es-barra' role='img' aria-label='Participación de cada capa en la reducción acumulada'>%s"
            "</div><div class='ab-ley'>%s</div>" % (barra, ley))


def _celda(D, c, sens):
    if c is None or c not in D["em"]:
        return "<td class='es-sin'>sin corrida</td>"
    v, h, p = _vol(D, c), _hr(D, c), _hr(D, c, "prudente")
    cls = "es-rojo" if h is not None and h < 0 else ("es-ambar" if p is not None and p < 0 else "")
    return ("<td class='%s%s'><span class='ab-cod'>%s</span><dl><dt>Volumen adicional</dt><dd class='%s'>%s</dd>"
            "<dt>Margen 2035</dt><dd>%s<small><abbr title='regla prudente: los otros sectores solo cumplen su "
            "tramo incondicional'>prudente</abbr>: %s</small></dd></dl></td>"
            % (cls, " es-sens" if sens else "", _cod(c), "es-cero" if v is not None and v < 0.5 else "",
               _kt_txt(v), _kt_txt(h), _kt_txt(p)))


def _matriz(D):
    cab = ["<th scope='col'>Sistema intacto<span>sin choques</span></th>"]
    for d in D["estados"]:
        fam, cod = next(iter(d["miembros"].items()))
        desde = _desde(_cambios(D, cod, fam))
        cab.append("<th scope='col'>%s<span>%s%s</span></th>"
                   % (_esc(d["nombre"]), _esc(TIPO.get(d["grupo"], d["grupo"]).lower()),
                      " · desde %d" % desde if desde else ""))
    filas = []
    for fam in D["art6"]:
        celdas = [_celda(D, fam, False)] + [_celda(D, d["miembros"].get(fam), d["grupo"] == "Sensibilidad")
                                            for d in D["estados"]]
        filas.append("<tr><th scope='row'><span class='ab-punto' style='background:%s'></span> %s</th>%s</tr>"
                     % (COLOR.get(fam, NEUTRO), _esc(_nombre(D, fam)), "".join(celdas)))
    return ("<div class='es-scroll'><table class='es-matriz'><thead><tr><th scope='col'></th>%s</tr></thead>"
            "<tbody>%s</tbody></table></div>" % ("".join(cab), "".join(filas)))


def mapa_html(fuentes=True):
    D = _datos()
    n_esc = len(D["refs"]) + len(D["art6"])
    n_tot = n_esc + sum(len(d["miembros"]) for d in D["estados"])
    n_r = sum(1 for d in D["estados"] if d["grupo"] == "Riesgo")
    n_s = sum(1 for d in D["estados"] if d["grupo"] == "Sensibilidad")
    n_c = sum(1 for d in D["estados"] if d["grupo"] == "Contrafactual")
    pruebas = _y([("%s %s" % (_cuantos(n_r, fem=False), "riesgo" if n_r == 1 else "riesgos"))
                  if n_r else "",
                  ("%s %s" % (_cuantos(n_s, fem=False), "riesgo de operación" if n_s == 1 else "riesgos de operación"))
                  if n_s else "",
                  ("%s %s" % (_cuantos(n_c, fem=False), "contrafactual" if n_c == 1 else "contrafactuales"))
                  if n_c else ""])
    tesis = ("El análisis compara %s escenarios del Modelo Climate Lead Group (OSeMOSYS, Segunda NDC). %s forman una escalera: "
             "cada uno contiene al anterior y le suma una capa de reducción, y de la capa depende qué meta consume "
             "una tonelada vendida. Los otros %s son pruebas sobre los escenarios de Artículo 6 (%s), para medir "
             "cuánto del potencial resiste cuando cambian las condiciones del sistema."
             % (_cuantos(n_tot), _cuantos(n_esc).capitalize(), _cuantos(n_tot - n_esc), pruebas))
    return (_estilo(fuentes) + "<div class='ab es'><p class='ab-tesis'>%s</p>"
            "<h3>Escalera de capas</h3><p class='ab-nota'>Reducción acumulada del sector energía en %s, en kt "
            "CO<sub>2</sub>e. A cada capa se le atribuye solo lo que agrega sobre el escenario anterior.</p>%s%s"
            "<h3>Riesgos</h3><p class='ab-nota'>Cada celda es un escenario del modelo. "
            "Volumen adicional: reducción frente al condicional en %s, sumada en los años en que el escenario emite "
            "menos que él. Margen 2035: meta incondicional menos la trayectoria nacional del escenario, con %s (regla "
            "base); la regla prudente deja %s.</p>%s"
            "<div class='ab-ley'><span><i class='es-rojo'></i>el país excede su meta incondicional aun sin "
            "transferir</span><span><i class='es-ambar'></i>la excede solo en la regla prudente</span>"
            "<span><i class='es-sens'></i>riesgo de operación, sin proyecto detrás</span></div>%s"
            "<p class='ab-fuente'>Fuente: %s; composición de cada escenario en B1_Scenario_Config.xlsx.</p></div>"
            % (tesis, VENT, _escalera(D), _barra(D), VENT, _regla(D), "a " + _regla(D, True), _matriz(D),
               _nota_sin_solucion(D), FUENTE_SALIDAS))


# ----------------------------------------------------------------------------- fichas
def _ficha_referencia(D, c):
    e = D["por"][c]
    nivel = _nivel(D, c)
    L = sorted([x for x in D["AD"] if x.get("escenario_NDC") == nivel], key=_kt, reverse=True)
    adj = nivel.lower() + "es"
    top = [x for x in L if _kt(x) > 0][:3]
    lineas = ""
    if L:
        lista = "".join("<tr><th scope='row'>%s</th><td>%s</td><td>%s</td><td>%s</td><td>%s</td></tr>"
                        % (_esc(x["codigo"]), _esc(x["linea"]), _esc(x.get("periodo")), _n(_kt(x), 1),
                           _esc(x.get("adicionalidad"))) for x in L)
        lineas = ("%s iniciativas %s de energía. Mayor reducción anual declarada: %s."
                  "<details class='es-detalle'><summary>Ver las %d iniciativas</summary>"
                  "<table class='es-tabla es-texto'><thead><tr><th scope='col'>Código</th><th scope='col'>Iniciativa"
                  "</th><th scope='col'>Periodo</th><th scope='col'>kt/año declarados</th><th scope='col'>"
                  "Adicionalidad</th></tr></thead><tbody>%s</tbody></table></details>"
                  % (_n(len(L)), adj, _y(["%s (%s kt/año)" % (_esc(x["linea"]), _n(_kt(x))) for x in top]),
                     len(L), lista))
    tiles = [("Emisiones del sector energía, 2035", _kt_txt(_em(D, c)), None)]
    tramo = _capa(D, D["refs"][0], c) if c != D["refs"][0] else None
    if tramo:
        tiles.append(("Reducción frente %s, %s" % (_a(D, D["refs"][0]), VENT), _kt_txt(tramo),
                      "el tramo condicional"))
    tot = _gen_total(D, c)
    tiles.append(("Generación hidroeléctrica, 2035",
                  _n(100.0 * _gen(D, c, "Hidroeléctrica") / tot if tot else 0.0, 1) + " %",
                  "%s GWh" % _n(_gen(D, c, "Hidroeléctrica"))))
    tiles.append(("Térmica desplazable, 2035", _n(_desp(D, c)) + " GWh",
                  "generación térmica sobre su piso de despacho obligatorio"))
    lect = []
    ads = sorted({str(x.get("adicionalidad") or "") for x in L})
    if len(ads) == 1 and ads[0]:
        args = {str(x.get("argumento") or "") for x in L}
        lect.append("Sus %s iniciativas figuran como «%s».%s"
                    % (_n(len(L)), _esc(ads[0]), " " + _esc(args.pop()) if len(args) == 1 else ""))
    if tramo:
        lect.append("El tramo condicional, la reducción %s frente %s, suma %s kt en %s. Transferirlo obliga a "
                    "renunciar a la meta condicional en la misma cuantía."
                    % (_de(D, c), _a(D, D["refs"][0]), _n(tramo), VENT))
        S = [x for x in L if x.get("adicionalidad") == "Sin adicionalidad"]
        tot_kt = sum(_kt(x) for x in L)
        if S and tot_kt:
            args = {str(x.get("argumento") or "") for x in S}
            lect.append("%s reúnen el %s %% de la reducción anual declarada de las iniciativas %s y figuran como "
                        "«Sin adicionalidad».%s"
                        % (_y([_esc(x["linea"]) for x in S]), _n(100.0 * sum(_kt(x) for x in S) / tot_kt), adj,
                           " " + _esc(args.pop()) if len(args) == 1 else ""))
    izq = [("Qué representa", _esc(e["narrativa"])),
           ("Iniciativas", lineas),
           ("Qué cambia", _esc(_origen_referencia(D, c)[1])),
           ("Lectura para el Artículo 6", _lista(lect))]
    der = [_seccion("Resultado de la corrida", _cifras(tiles))]
    return _ficha(c, [COLOR.get(c, NEUTRO)], e["nombre"], [c], TIPO.get(e["grupo"], e["grupo"]),
                  _esc(_origen_referencia(D, c)[0]), izq, der)


@lru_cache(maxsize=None)
def _salida_tec(huella):
    """Capacidad nueva, capacidad total y actividad por escenario, tecnologia y anio (salidas de Executables)."""
    cols = ["Strategy", "Technology", "Year", "NewCapacity", "TotalCapacityAnnual", "TotalTechnologyAnnualActivity"]
    df = C.leer_ecuoutput(list(analizar.resultados()["corrida"]["escenarios"]))[cols]
    return df.groupby(["Strategy", "Technology", "Year"])[cols[3:]].sum()


def _iniciativas_modeladas(D, c):
    """Tabla de las iniciativas que el escenario representa: linea declarada, tecnologia y palancas que
    la modelan, entrada, capacidad y generacion en la corrida. Las lineas fuera del modelo se declaran."""
    L = _lineas(D, c, exacto=False)
    if not L:
        return ""
    grupos = set(K.grupos_de(D["por"][c]))
    P = [p for p in D["P"] if p["grupo"] in grupos]
    S = _salida_tec(C.huella(analizar.JSON))
    pares = set(S.index.droplevel(2))
    filas = []

    def fila(x, modelo, pal, entrada, mw, gwh):
        return ("<tr><th scope='row'><span class='ab-cod'>%s</span> %s</th><td>%s</td><td>%s</td><td>%s</td>"
                "<td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td></tr>"
                % (_esc(str(x.get("codigo") or "")), _esc(str(x.get("linea") or "")),
                   _esc(str(x.get("escenario_NDC") or "")), _esc(modelo), _esc(pal), entrada, mw, gwh,
                   _n(_kt(x), 1) if _kt(x) else "", _esc("%s; %s" % (x.get("adicionalidad") or "sin dato",
                                                                  x.get("veredicto_compradores") or "sin veredicto"))))

    for x in L:
        cod = str(x.get("codigo") or "")
        pal = [p for p in P if cod and cod in [t.strip() for t in str(p.get("iniciativa") or "").split(",")]]
        tecs = list(dict.fromkeys(p["tecnologia"] for p in pal))
        if not tecs:
            fuera = "fuera" in str(x.get("escenario_art6") or "")
            filas.append(fila(x, "fuera del modelo: entra con su cifra declarada" if fuera else "sin palanca propia",
                              "", "", "", ""))
            continue
        for t in tecs:
            ids = _y(sorted({p["id"] for p in pal if p["tecnologia"] == t}))
            modelo = "%s (%s)" % (D["fam_palanca"].get(t, t), t)
            if (c, t) not in pares:
                filas.append(fila(x, modelo, ids, "", "", ""))
                continue
            s = S.loc[(c, t)]
            nueva = s["NewCapacity"]
            entrada = next((int(a) for a, v in nueva.items() if a >= 2023 and v > 1e-6), None)
            mw = float(s["TotalCapacityAnnual"].get(2035, 0.0)) * 1000.0
            gwh = float(s["TotalTechnologyAnnualActivity"].get(2035, 0.0)) * 277.78
            filas.append(fila(x, modelo, ids, str(entrada) if entrada else "existente", _n(mw), _n(gwh)))
    return ("<table class='es-tabla es-texto'><thead><tr><th scope='col'>Iniciativa</th><th scope='col'>Tramo</th>"
            "<th scope='col'>Tecnología en el modelo</th><th scope='col'>Palancas</th><th scope='col'>Entrada</th>"
            "<th scope='col'>Capacidad 2035, MW</th><th scope='col'>Generación 2035, GWh</th>"
            "<th scope='col'>Declarado, kt/año</th><th scope='col'>Adicionalidad; veredicto</th></tr></thead>"
            "<tbody>%s</tbody></table><p class='es-nota'>Capacidad y generación en 2035 de la tecnología que modela la iniciativa (Output.csv del escenario), "
            "compartidas entre las iniciativas de esa tecnología; entrada: primer año con capacidad nueva en el "
            "escenario. Las cifras declaradas vienen de Art6_Adicionalidad.</p>%s"
            % ("".join(filas), "".join("<p class='es-nota'>%s</p>" % _esc(x["frase"]) for x in _despacho_parcial(D, c))))


def _ficha_art6(D, c):
    e, b = D["por"][c], D["base"][c]
    filas = _cambios(D, c, b)
    grupos = set(K.grupos_de(e)) - set(K.grupos_de(D["por"][b]) if b in D["por"] else [])
    L = _lineas(D, c)
    fuera = [x for x in _lineas(D, c, exacto=False) if x not in L]
    capa, vol = _capa(D, b, c), _vol(D, c)
    cls, sello = _consecuencia(D, b, c)
    tiles = [("Emisiones del sector energía, 2035", _kt_txt(_em(D, c)), None),
             ("Volumen adicional a la NDC, %s" % VENT, _kt_txt(vol),
              ("%s kt de esta capa" % _n(capa)) if b in D["art6"] else None),
             ("Margen nacional, 2035", _kt_txt(_hr(D, c)),
              "regla prudente (los demás sectores cumplen solo su incondicional): %s" % _kt_txt(_hr(D, c, "prudente")))]
    contra = next((d["miembros"].get(c) for d in D["estados"]
                   if d["grupo"] == "Contrafactual" and d["miembros"].get(c)), None)
    if contra and D["vol"].get((c, "atribuible_por_retiro")) is not None:
        tiles.append(("Aporte atribuible por retiro, %s" % VENT, _kt_txt(D["vol"][(c, "atribuible_por_retiro")]),
                      "emisiones de %s (el mismo sistema sin las actividades de %s) menos las de %s" % (contra, c, c)))
    fams_pal = {C.familia(f["tec"]) for f in filas if f["tipo"] == "act"}

    lect = []
    if b in D["art6"]:
        lect.append("La capa %s frente %s suma %s kt en %s; con ella, %s acumula %s kt adicionales a la NDC."
                    % (_de(D, c), _a(D, b), _n(capa), VENT, _art(D, c), _n(vol or 0.0)))
    else:
        lect.append("La capa %s frente %s suma %s kt en %s." % (_de(D, c), _a(D, b), _n(capa), VENT))
    if cls == "ab-consume":
        lect.append("Transferida con ajuste correspondiente, cada tonelada de la capa deja de contar para la meta "
                    "condicional.")
    elif cls == "ab-libre":
        lect.append("Sus líneas están fuera de la NDC: una tonelada de la capa no consume ninguna meta si demuestra "
                    "su adicionalidad.")
    dg = {f: _gen(D, c, f, V) - _gen(D, b, f, V) for f, _, _ in C.FAMILIAS}
    sube = sorted([(f, v) for f, v in dg.items() if v >= 0.5], key=lambda x: -x[1])
    baja = sorted([(f, v) for f, v in dg.items() if v <= -0.5], key=lambda x: x[1])
    if sube:
        frase = "En %s la capa agrega %s" % (VENT, _y(["%s GWh %s" % (_n(v), GWH_DE.get(f, "de " + f.lower()))
                                                       for f, v in sube]))
        if baja:
            frase += " y deja de generar %s" % _y(["%s GWh %s" % (_n(-v), GWH_DE.get(f, "de " + f.lower()))
                                                   for f, v in baja[:2]])
        lect.append(frase + ".")
    for f in sorted(x for x in fams_pal if x):
        if abs(dg.get(f, 0.0)) < 0.5 and _gen(D, b, f, V) > 0.5:
            pal = _y([x["etiqueta"].lower() for x in filas if x["tipo"] == "act" and C.familia(x["tec"]) == f])
            lect.append("El %s no cambia la generación %s, que es la misma que %s: su reducción queda en esa base y "
                        "fuera de la capa." % (pal, GEN_FAMILIA.get(f, "con " + f.lower()), _en(D, b)))
    anual = {a: _capa(D, b, c, a) for a in V}
    pico, a35 = max(anual, key=anual.get), V[-1]
    final = ("aporta %s kt" % _n(anual[a35]) if anual[a35] >= 0 else
             "emite %s kt más que %s" % (_n(-anual[a35]), _art(D, b)))
    if pico != a35:
        lect.append("La capa alcanza su máximo en %d, con %s kt, y en %d %s. La térmica desplazable %s, lo único que "
                    "una renovable nueva puede sustituir, pasa de %s GWh en %d a %s GWh en %d."
                    % (pico, _n(anual[pico]), a35, final, _de(D, b), _n(_desp(D, b, V[0])), V[0],
                       _n(_desp(D, b, a35)), a35))
    if abs(anual[a35]) < 0.5 and capa > 0.5:
        lect.append(_frase_capa_cero(D, c, b, a35))
    lect += [x["corta"] for x in _despacho_parcial(D, c)]
    if anual[a35] < 0:
        cero = [0.0] * len(C.ANIOS)
        de = {f: D["egf"].get(c, {}).get(f, cero)[C.IDX[a35]] - D["egf"].get(b, {}).get(f, cero)[C.IDX[a35]]
              for f in set(D["egf"].get(c, {})) | set(D["egf"].get(b, {}))}
        mas = [(f, v) for f, v in de.items() if v >= 0.5]
        if mas:
            lect.append("La diferencia de %d sale de la generación %s, que emite %s kt más."
                        % (a35, _y([GEN_FAMILIA.get(f, "con " + f.lower()) for f, _ in mas]),
                           _n(sum(v for _, v in mas))))
    bajo = [(d, _capa(D, d["miembros"][b], d["miembros"][c]), d["miembros"][b]) for d in D["estados"]
            if d["grupo"] == "Riesgo" and b in d["miembros"] and c in d["miembros"]]
    if bajo and capa > 0:
        frase = ("Bajo los riesgos la misma capa reduce %s, frente a %s kt con el sistema intacto"
                 % (_y(["%s kt con %s" % (_n(v), d.get("frase") or _minus(d["nombre"])) for d, v, _ in bajo]), _n(capa)))
        dd = [_desp(D, x, a35) for _, _, x in bajo]
        if all(v > capa for _, v, _ in bajo) and min(dd) > _desp(D, b, a35):
            frase += (": vuelve a haber térmica que sustituir, y en %d la térmica desplazable %s va de %s a %s GWh, "
                      "frente a %s GWh con el sistema intacto" % (a35, _de(D, b), _n(min(dd)), _n(max(dd)),
                                                                 _n(_desp(D, b, a35))))
        lect.append(frase + ".")
    contra_c = next((d["miembros"].get(c) for d in D["estados"] if d["grupo"] == "Contrafactual" and d["miembros"].get(c)), None)
    if contra_c and D["vol"].get((c, "atribuible_por_retiro")) is not None:
        lect.append("Sin las actividades que financia, el mismo sistema (escenario %s) emitiría %s kt más en %s: ese es el "
                    "aporte atribuible por retiro, la reducción que esas actividades producen antes de la prueba de "
                    "adicionalidad y de la prueba de sobreventa; la capa frente %s mide solo lo que %s añade a %s, que ya "
                    "incluye esos proyectos." % (contra_c, _n(D["vol"][(c, "atribuible_por_retiro")]), VENT, _a(D, b), c, b))
    cuenta = {}
    for x in L:
        cuenta.setdefault(x.get("veredicto_compradores") or "sin veredicto", []).append(x)
    if L:
        orden = sorted(cuenta.items(), key=lambda kv: list(VEREDICTO).index(kv[0]) if kv[0] in VEREDICTO else 9)
        lect.append("Veredicto de compradores potenciales para las %s líneas que el modelo representa: %s."
                    % (_n(len(L)), _y([("%s sin veredicto" if v == "sin veredicto" else "%s en «" + v + "»")
                                       % _n(len(xs)) for v, xs in orden])))

    izq = [("Qué representa", _esc(e["narrativa"])),
           ("Líneas que contiene", _bloque_lineas(L, fuera)),
           ("Lectura para el Artículo 6", _lista(lect))]
    der = [_seccion("Qué cambia frente %s" % _a(D, b), _tabla_cambios(filas, _nombre(D, b), e["nombre"])
                    + _detalle_palancas(D, grupos)),
           _seccion("Iniciativas modeladas", _iniciativas_modeladas(D, c)),
           _seccion("Resultado de la corrida", _cifras(tiles) + _tabla_generacion(D, c, b, fams_pal))]
    return _ficha(c, [COLOR.get(c, NEUTRO)], e["nombre"], [c], TIPO.get(e["grupo"], e["grupo"]),
                  "<span class='ab-sello %s'>%s</span> Base: %s" % (cls, sello, _esc(_nombre(D, b))), izq, der)


def _ficha_estado(D, d):
    fams = list(d["miembros"])
    fam0, cod0 = fams[0], d["miembros"][fams[0]]
    filas = _cambios(D, cod0, fam0)
    sens = d["grupo"] == "Sensibilidad"
    ad = next((x for x in D["AD"] if x.get("codigo") == d["codigo"]), None)
    if d["riesgos"]:
        partes = "".join("<p><b>%s.</b> %s</p>" % (_esc(r["nombre"]), _esc(r["derivado_de"])) for r in d["riesgos"])
        representa = ("<p>Los dos choques a la vez.</p>" if len(d["riesgos"]) > 1 else "") + partes
        alcance = ("<details class='es-detalle'><summary>Alcance, límites y validación</summary>%s</details>"
                   % "".join("<p><b>%s.</b> %s</p><p>%s</p>" % (_esc(r["nombre"]), _esc(r["nota"]),
                                                                _esc(r["validacion"])) for r in d["riesgos"]))
    else:
        representa = ("%s. %s" % (_esc(ad["linea"]), _esc(ad["argumento"]))) if ad else _esc(D["por"][cod0]["narrativa"])
        alcance = ""

    metricas = [("Emisiones del sector energía, 2035 (kt)", lambda x: _em(D, x)),
                ("Volumen adicional a la NDC, %s (kt)" % VENT, lambda x: _vol(D, x)),
                ("Margen nacional 2035 (kt)", lambda x: _hr(D, x)),
                ("Margen 2035, regla prudente: los demás sectores cumplen solo su incondicional (kt)", lambda x: _hr(D, x, "prudente")),
                ("Generación hidroeléctrica 2035 (GWh)", lambda x: _gen(D, x, "Hidroeléctrica")),
                ("Térmica desplazable 2035 (GWh)", lambda x: _desp(D, x))]
    filas_res = []
    for et, f in metricas:
        vals = []
        for fam in fams:
            a, z = f(fam), f(d["miembros"][fam])
            vals.append(None if a is None or z is None else (a, z))
        if all(v is None or abs(v[1] - v[0]) < 0.5 for v in vals):
            continue
        celdas = "".join("<td>%s → <b class='%s'>%s</b></td>" % (_n(v[0]), "es-neg" if v[1] < 0 else "", _n(v[1]))
                         if v else "<td>s. d.</td>" for v in vals)
        filas_res.append("<tr><th scope='row'>%s</th>%s</tr>" % (et, celdas))
    choque = "el riesgo de operación" if sens else "el choque"
    tabla_res = ("<table class='es-tabla'><thead><tr><th scope='col'>Sistema intacto → con %s</th>%s</tr></thead>"
                 "<tbody>%s</tbody></table>"
                 % (choque, "".join("<th scope='col'>%s</th>" % _esc(_nombre(D, fam)) for fam in fams),
                    "".join(filas_res)))

    lect = []
    if sens:
        lect.append("Frente a su versión intacta, el riesgo de operación reduce %s en %s."
                    % (_y(["%s kt más %s" % (_n(_capa(D, fam, d["miembros"][fam])), _en(D, fam)) for fam in fams]),
                       VENT))
        if ad:
            lect.append("Adicionalidad: «%s». %s" % (_esc(ad["adicionalidad"]), _esc(ad["argumento"])))
        lect.append("El análisis la reporta aparte y no la suma a la oferta de ITMO.")
    else:
        v0 = [(_vol(D, fam) or 0.0, _vol(D, d["miembros"][fam]) or 0.0) for fam in fams]
        if all(z < 0.5 for _, z in v0):
            lect.append("El volumen adicional a la NDC cae a cero %s; con el sistema intacto era de %s."
                        % (_y([_en(D, fam) for fam in fams]), _y(["%s kt" % _n(a) for a, _ in v0])))
        else:
            lect.append("El volumen adicional a la NDC pasa %s."
                        % _y(["de %s a %s kt %s" % (_n(a), _n(z), _en(D, fam)) for (a, z), fam in zip(v0, fams)]))
        h1 = [(_hr(D, d["miembros"][fam]), _hr(D, d["miembros"][fam], "prudente")) for fam in fams]
        lect.append("El margen nacional de 2035 queda en %s, con %s; en la regla prudente (los otros sectores solo "
                    "cumplen su tramo incondicional), en %s."
                    % (_y(["%s kt %s" % (_n(h), _en(D, fam)) for (h, _), fam in zip(h1, fams) if h is not None]),
                       _regla(D), _y(["%s kt" % _n(p) for _, p in h1 if p is not None])))
        if any(x is not None and x < 0 for hp in h1 for x in hp):
            lect.append("Un margen negativo significa que el país excede su meta incondicional aun sin transferir.")
        anual = D["R"]["potencial_art6"]["anual"]
        etiqueta = next((x["estado"] for x in anual if x["sufijo"] == "-" + d["codigo"]), None)
        sv = {s["regla"]: s for s in D["R"]["potencial_art6"]["sobreventa"] if s["estado"] == etiqueta}
        if sv:
            aut = next(iter(sv.values()))["autorizado_2031_2035"]
            c_ = sv.get("condicional", {}).get("sobreventa_2031_2035") or 0.0
            p_ = sv.get("prudente", {}).get("sobreventa_2031_2035") or 0.0
            if c_ < 0.5 and p_ < 0.5:
                lect.append("Lo que el país autorizaría con el sistema intacto, %s kt, sigue cabiendo en el margen."
                            % _n(aut))
            else:
                lect.append("Si el país autoriza los %s kt transferibles con el sistema intacto, quedan sin respaldo "
                            "%s kt con %s y %s kt en la regla prudente." % (_n(aut), _n(c_), _regla(D), _n(p_)))
    sub = _frase_stoele(D, list(d["miembros"].values()))
    if sub:
        lect.append(sub)

    izq = [("Qué representa", representa),
           ("Lectura para el Artículo 6", _lista(lect)),
           ("Origen y alcance", alcance)]
    der = [_seccion("Qué cambia frente al sistema intacto",
                    _tabla_cambios(filas, "Sistema intacto", "Con " + choque) + _detalle_palancas(D, d["grupos"])),
           _seccion("Resultado de la corrida", tabla_res)]
    return _ficha(d["codigo"], [COLOR.get(f, NEUTRO) for f in fams], d["nombre"], list(d["miembros"].values()),
                  TIPO.get(d["grupo"], d["grupo"]), "Se aplica sobre %s" % _esc(_y([_art(D, f) for f in fams])),
                  izq, der)


def _rotulo(et, txt):
    """«Etiqueta: texto», salvo que el texto de la configuracion ya empiece con la etiqueta."""
    t = str(txt or "").strip()
    return _esc(t) if t.lower().startswith(et.lower()) else "%s: %s" % (et, _esc(t))


def _comunes(D):
    comp = _y(["%s (%s)" % (COMPONENTE.get(x, x), x) for x in C.COMP_ENERGIA])
    bl, hd = D["bloques"], D["headroom"]
    items = ["Marco de análisis: %d-%d, vigencia de la Segunda NDC." % (C.MARCO[0], C.MARCO[-1]),
             "Ventana de transacciones: %s." % VENT,
             "Emisiones del sector energía: suma de %s, del Output.csv de cada escenario." % comp,
             ("Resolución temporal: %s por año (Season = %s)."
              % ("un solo bloque horario" if len(bl) == 1 else "%d bloques horarios" % len(bl), ", ".join(bl)))
             if bl else "",
             _rotulo("Margen nacional", hd["regla_nacional"]["descripcion"]) if "regla_nacional" in hd else "",
             _rotulo("Regla prudente", hd["regla_prudente"]["descripcion"]) if "regla_prudente" in hd else "",
             "Térmica desplazable: generación térmica por encima de su piso de despacho obligatorio (pisos del Modelo "
             "CLG), calculada con la actividad del Output.csv y el piso del _Input.csv de cada escenario; es lo único que "
             "una renovable nueva puede sustituir.",
             "Años subestimados: cuando el modelo pasa energía por STOELE con la térmica de la red en su tope (K15b), "
             "falta potencia y las emisiones de ese año quedan subestimadas; la ficha «Escenarios sin solución y años "
             "subestimados» los lista con la variante diagnóstica de potencia mínima.",
             "Ejercicio exploratorio: el tratamiento del ajuste correspondiente es conceptual y no constituye una "
             "metodología oficial del Artículo 6."]
    return "<section class='es-comunes'><h3>Supuestos comunes</h3>%s</section>" % _lista(items)


# ----------------------------------------------------------------------------- limites de la corrida
@lru_cache(maxsize=None)
def _cf_af(cod, tec, huella):
    """{anio: CapacityFactor x AvailabilityFactor} de una tecnologia en el datafile del escenario. El modelo tiene un
    solo bloque horario por anio, asi que la energia de 1 MW en el anio es CF x AF x 8,76 GWh."""
    T = C.tabla(C.leer_datafile(C.datafile(cod)))
    cf = next((v for (p, k), (_, v) in T.items() if p == C.FP and k.split(",")[0] == tec), None)
    af = next((v for (p, k), (_, v) in T.items() if p == "AvailabilityFactor" and k.split(",")[0] == tec), None)
    return {a: (cf[C.IDX[a]] if cf else float("nan")) * (af[C.IDX[a]] if af else 1.0) for a in C.ANIOS}


def _cf_ppfoi(cod):
    return _cf_af(cod, "PPFOI", C.huella(C.datafile(cod)))


def _despacho_parcial(D, c):
    """Lineas del escenario cuya tecnologia tiene techo de generacion en 2026-2035 y que el modelo despacha solo en
    parte de esos anios (B-BIO: techo de PPBIM desde 2031 y despacho solo en 2031). Con los costos de relleno del
    Modelo CLG ese despacho no responde a un costo real: la frase lo dice donde se muestra la linea."""
    L = _lineas(D, c, exacto=False)
    if not L or c not in D["por"]:
        return []
    grupos = set(K.grupos_de(D["por"][c]))
    P = [p for p in D["P"] if p["grupo"] in grupos]
    S = _salida_tec(C.huella(analizar.JSON))
    pares = set(S.index.droplevel(2))
    out = []
    for x in L:
        cod = str(x.get("codigo") or "")
        tecs = list(dict.fromkeys(p["tecnologia"] for p in P
                                  if cod and cod in [t.strip() for t in str(p.get("iniciativa") or "").split(",")]))
        for t in tecs:
            if D["fam_palanca"].get(t) == "Hidroeléctrica" or (c, t) not in pares:
                continue
            techo = _serie(D, c, t, C.TECHO)
            act = S.loc[(c, t)]["TotalTechnologyAnnualActivity"]
            cap = S.loc[(c, t)]["TotalCapacityAnnual"]
            con_techo = [a for a in C.MARCO if not pd.isna(techo[a]) and 0.5 / C.PJ_A_GWH < techo[a] < SIN_TECHO]
            despacha = [a for a in con_techo if float(act.get(a, 0.0)) * C.PJ_A_GWH > 0.5]
            if not con_techo or not despacha or len(despacha) == len(con_techo):
                continue
            ociosos = [a for a in con_techo if a not in despacha]
            frase = ("%s (%s): techo de generación de %s GWh/año desde %d, pero el modelo solo despacha %s en %s (%s GWh) "
                     "y en %s deja sin despacho su capacidad (%s MW). Con los costos de relleno del Modelo CLG, ese "
                     "despacho no responde a un costo real."
                     % (cod, t, _n(techo[con_techo[0]] * C.PJ_A_GWH, 1), con_techo[0], t, _tramos(despacha),
                        _y([_n(float(act.get(a, 0.0)) * C.PJ_A_GWH, 1) for a in despacha]), _tramos(ociosos),
                        _n(float(cap.get(ociosos[-1], 0.0)) * 1000.0, 1)))
            corta = ("%s: techo de %s GWh/año desde %d y despacho solo en %s (costos de relleno del Modelo CLG)."
                     % (cod, _n(techo[con_techo[0]] * C.PJ_A_GWH, 1), con_techo[0], _tramos(despacha)))
            out.append({"codigo": cod, "tec": t, "frase": frase, "corta": corta})
    return out


def _frase_capa_cero(D, c, b, a35):
    """Por que la capa de c vale cero en a35: la base solo tiene la termica que dejan sus pisos de despacho."""
    con = D["R"]["roles"]["con"]
    td_b, td_con = _desp(D, b, a35), _desp(D, con, a35)
    nb = _art(D, b) + ("" if _nombre(D, b) == b else " (%s)" % b)
    txt = ("En %d la capa vale cero: %s solo tiene %s GWh de generación térmica por encima de sus pisos de despacho "
           "(K16 en PPFOI; Modelo CLG en PPDSL y PPNGS)%s, y la renovable adicional no tiene térmica que sustituir."
           % (a35, nb, _n(td_b, 1), "" if b == con else (", lo mismo que %s" % con if abs(td_b - td_con) < 0.05
                                                         else " (%s: %s GWh)" % (con, _n(td_con, 1)))))
    sens = next((x for x in D["R"].get("capas_por_estado", []) if x.get("grupo") == "Sensibilidad"
                 and x.get("capa") == c and x.get(str(a35)) is not None), None)
    if sens is not None and abs(float(sens[str(a35)])) >= 0.5:
        txt += " Sin esos pisos (%s, %s) la capa valdría %s kt en %d." % (
            _minus(K.rotulo(sens["sufijo"], sens["estado"])), sens["escenario"], _n(float(sens[str(a35)])), a35)
    return txt


def _frase_stoele(D, cods):
    """Anios subestimados de los escenarios: los que pasan energia por STOELE con la termica de la red en su tope."""
    v = D["variante"]
    partes = []
    for cod in cods:
        s = D["stoele"].get(cod)
        if not s:
            continue
        anios = sorted(s)
        txt = "%s en %s (STOELE: %s GWh" % (cod, _tramos(anios), _y([_n(s[a]) for a in anios]))
        if v is not None and cod in D["em"]:
            x = v[v.escenario == cod].set_index("anio")
            if all(a in x.index for a in anios):
                dif = sum(float(x.loc[a, "energia_variante_kt"]) - float(D["em"][cod][a]) for a in anios)
                txt += "; la variante diagnóstica de potencia mínima emite %s kt %s" % (
                    _n(abs(dif)), "más" if dif >= 0 else "menos")
        partes.append(txt + ")")
    if not partes:
        return ""
    return ("Años subestimados: %s. En esos años el modelo cubre la falta de potencia pasando energía por STOELE, con la "
            "térmica de la red en su tope (K15b), así que sus emisiones quedan subestimadas." % _y(partes))


def _nota_sin_solucion(D):
    faltan = list(D["R"].get("faltan") or [])
    txt = []
    if faltan:
        txt.append("%s no tienen solución con la inversión térmica limitada a la expansión declarada (K15b) y no figuran "
                   "en la matriz; su variante diagnóstica de potencia mínima está en la ficha «Escenarios sin solución "
                   "y años subestimados»." % _y(faltan))
    if D["stoele"]:
        txt.append("Los escenarios que pasan energía por STOELE tienen años con emisiones subestimadas: %s." % _y(
            ["%s en %s" % (c, _tramos(D["stoele"][c])) for c in sorted(D["stoele"])]))
    return "<p class='ab-nota'>%s</p>" % " ".join(txt) if txt else ""


def _ficha_sin_solucion(D):
    """Escenarios sin solucion de B1 y escenarios con anios subestimados (STOELE), con la variante diagnostica de
    potencia minima: capacidad de PPFOI faltante sobre el tope K15b, su energia equivalente, emisiones y margen."""
    faltan = list(D["R"].get("faltan") or [])
    v = D["variante"]
    if not faltan and not D["stoele"]:
        return ""
    MC = list(C.MARCO)
    rv = {x["escenario"]: x for x in D["R"].get("riesgo_variante_potencia_minima") or []}
    num = lambda x: x is not None and not pd.isna(x)
    partes = []
    if faltan:
        con_sol = [c for c in faltan if v is not None and len(v[v.escenario == c])
                   and bool(v[v.escenario == c]["variante_con_solucion"].all())]
        partes.append("<p>%s %s no %s solución en la corrida de B1: glpsol no encuentra una solución factible. La causa es la "
                      "inversión térmica nueva limitada a la expansión declarada (K15b, tope de capacidad de PPFOI, PPDSL y "
                      "PPNGS en 2026-2035): sin la clase PPHRORAB desde 2029, la potencia térmica permitida no alcanza para "
                      "cubrir la demanda.%s Sus fichas no se muestran.</p>"
                      % (_cuantos(len(faltan)).capitalize(), "escenarios" if len(faltan) > 1 else "escenario",
                         "tienen" if len(faltan) > 1 else "tiene",
                         (" Con el tope de PPFOI liberado, la variante diagnóstica tiene solución en %s, lo que confirma "
                          "la causa." % ("los %s" % _cuantos(len(con_sol)) if len(con_sol) == len(faltan) else _y(con_sol)))
                         if con_sol else ""))
    partes.append("<p>Variante diagnóstica de potencia mínima (Art6_calibracion/suficiencia_escenarios_art6.py, fuera de "
                  "B1): sobre el datafile de cada escenario libera el tope de PPFOI en 2026-2035, encarece su potencia "
                  "nueva y cierra STOELE, de modo que el modelo construye solo la potencia de fuel oil sin la cual no cubre "
                  "la demanda. La diferencia con el tope K15b es la capacidad faltante del año. Es un diagnóstico y no una "
                  "cota: llena el faltante solo con fuel oil y redistribuye el despacho de los años en que no falta "
                  "potencia, así que sus emisiones no acotan las del escenario.</p>")
    if v is None:
        partes.append("<p class='es-aviso'>Falta %s: la variante diagnóstica no se ha corrido.</p>" % VARIANTE.name)
        return _articulo_limites("".join(partes))
    cfs = set()
    resumen, detalle = [], []
    primero = {}
    for cod in faltan:
        x = v[v.escenario == cod].set_index("anio")
        if x.empty:
            continue
        cf = _cf_ppfoi(cod)
        falt = {a: float(x.loc[a, "faltante_MW"]) if a in x.index else 0.0 for a in MC}
        cfs |= {round(cf[a], 4) for a in MC}
        gwh = {a: falt[a] * cf[a] * 8.76 for a in MC}
        anios = [a for a in MC if falt[a] > 0.5]
        primero[cod] = anios[0] if anios else None
        amax = max(MC, key=lambda a: falt[a])
        r = rv.get(cod, {})
        resumen.append("<tr><th scope='row'>%s</th><td>%s</td><td>%s (%d)</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td></tr>"
                       % (cod, primero[cod] or "–", _n(falt[amax], 1), amax, _n(gwh[amax]), _n(falt[MC[-1]], 1),
                          _n(r["emisiones_variante_2031_2035"]) if num(r.get("emisiones_variante_2031_2035")) else "s. d.",
                          _n(r["aumento_frente_al_intacto_2031_2035"]) if num(r.get("aumento_frente_al_intacto_2031_2035"))
                          else "s. d."))
        detalle.append("<tr><th scope='row'>%s</th>%s</tr>" % (cod, "".join(
            "<td>%s</td>" % ("%s<span class='es-pj'>%s GWh</span>" % (_n(falt[a], 1), _n(gwh[a])) if falt[a] > 0.5 else "–")
            for a in MC)))
    if resumen:
        partes.append("<table class='es-tabla'><thead><tr><th scope='col'>Escenario sin solución</th><th scope='col'>Primer "
                      "año con faltante</th><th scope='col'>Faltante máximo, MW (año)</th><th scope='col'>Energía "
                      "equivalente del máximo, GWh/año</th><th scope='col'>Faltante en %d, MW</th><th scope='col'>Emisiones de "
                      "energía de la variante, %s, kt</th><th scope='col'>Aumento frente al escenario intacto, %s, kt</th>"
                      "</tr></thead><tbody>%s</tbody></table>" % (MC[-1], VENT, VENT, "".join(resumen)))
        partes.append("<div class='es-scroll'><table class='es-tabla'><thead><tr><th scope='col'>Capacidad de PPFOI faltante "
                      "sobre el tope K15b, MW, y su energía equivalente</th>%s</tr></thead><tbody>%s</tbody></table></div>"
                      % ("".join("<th scope='col'>%d</th>" % a for a in MC), "".join(detalle)))
        # cuando empieza el faltante: salida de la clase sola frente a los dos choques
        por_estado = {}
        for cod, a in primero.items():
            por_estado.setdefault(cod.split("-", 1)[1], set()).add(a)
        frases = []
        for est, ini in por_estado.items():
            ini = sorted(a for a in ini if a)
            if not ini:
                continue
            frase = "con %s (%s) el faltante empieza en %s" % (K.FRASES.get(est, est), est, _y([str(a) for a in ini]))
            if ini == [2029]:
                cod0 = next(c for c in primero if c.endswith("-" + est))
                x0 = v[v.escenario == cod0].set_index("anio")
                if 2028 in x0.index and 2029 in x0.index and x0.loc[2029, "tope_PPFOI_MW"] < x0.loc[2028, "tope_PPFOI_MW"]:
                    frase += (", cuando el tope de PPFOI baja de %s MW en 2028 a %s MW en 2029 al vencer los arriendos del "
                              "caso central (31-12-2028)" % (_n(x0.loc[2028, "tope_PPFOI_MW"]), _n(x0.loc[2029, "tope_PPFOI_MW"])))
            elif "ANOSECO" in est and est != "ANOSECO" and ini[0] < 2029:
                cod0 = next(c for c in primero if c.endswith("-" + est))
                x0 = v[v.escenario == cod0].set_index("anio")
                frase += (": con los dos choques a la vez, el año seco severo ya deja al sistema sin potencia suficiente "
                          "desde %d (%s MW sobre el tope)" % (ini[0], _n(float(x0.loc[ini[0], "faltante_MW"]), 1)))
            frases.append(frase)
        if frases:
            partes.append("<p>%s.</p>" % ". ".join(_mayus(f) for f in frases))
        cf_txt = _y([_n(x, 4) for x in sorted(cfs)])
        partes.append("<p class='es-nota'>Energía equivalente: MW × CF × AF de PPFOI en el datafile (%s) × 8.760 h. El modelo "
                      "tiene un solo bloque horario por año, así que el faltante se lee como energía anual y no como potencia "
                      "de punta. La potencia que la variante construye en un año sigue disponible en los siguientes: el "
                      "faltante de un año puede ser potencia construida antes.</p>" % cf_txt)
        # margen y sobreventa del escalon que ejecuta el pais con las emisiones de la variante
        filas_m = []
        claves = [("CLG", "condicional"), ("CLG", "prudente"), ("corregida", "condicional"), ("corregida", "prudente")]
        for cod in faltan:
            r = rv.get(cod, {})
            if not any(num(r.get("margen_2035_%s_%s" % k)) for k in claves):
                continue
            filas_m.append("<tr><th scope='row'>%s</th>%s</tr>" % (cod, "".join(
                "<td>%s</td><td>%s</td>" % (_n(r["margen_2035_%s_%s" % k]), _n(r["sobreventa_2031_2035_%s_%s" % k]))
                for k in claves)))
        if filas_m:
            cab = "".join("<th scope='col'>Margen 2035, %s</th><th scope='col'>Sobreventa %s, %s</th>" % (et, VENT, et)
                          for et in ("proyección CLG, regla base", "proyección CLG, regla prudente",
                                     "proyección corregida, regla base", "proyección corregida, regla prudente"))
            partes.append("<p>Margen nacional y sobreventa del escenario que ejecuta el país con las emisiones de la "
                          "variante, si se autoriza lo transferible con el sistema intacto (kt CO<sub>2</sub>e; un margen "
                          "negativo es incumplimiento aun sin transferir):</p><div class='es-scroll'><table class='es-tabla'>"
                          "<thead><tr><th scope='col'>Escenario</th>%s</tr></thead><tbody>%s</tbody></table></div>"
                          % (cab, "".join(filas_m)))
    if D["stoele"]:
        filas_s = []
        for cod in sorted(D["stoele"]):
            s = D["stoele"][cod]
            x = v[v.escenario == cod].set_index("anio")
            anios = sorted(s)
            cf = _cf_ppfoi(cod)
            falt = [float(x.loc[a, "faltante_MW"]) if a in x.index else float("nan") for a in anios]
            b1 = [float(D["em"][cod][a]) if cod in D["em"] else float("nan") for a in anios]
            va = [float(x.loc[a, "energia_variante_kt"]) if a in x.index else float("nan") for a in anios]
            filas_s.append("<tr><th scope='row'>%s</th><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td></tr>"
                           % (cod, _tramos(anios), " · ".join(_n(s[a]) for a in anios),
                              " · ".join("–" if pd.isna(f) else "%s (%s GWh)" % (_n(f, 1), _n(f * cf[a] * 8.76))
                                         for f, a in zip(falt, anios)),
                              " · ".join(_n(e) for e in b1),
                              " · ".join("s. d." if pd.isna(z) else _n(z - e) for z, e in zip(va, b1))))
        partes.append("<p>Escenarios con solución y años subestimados: en los años marcados el modelo cubre la falta de "
                      "potencia pasando energía por STOELE, un paso de la electricidad generada a la transmisión sin "
                      "pérdidas, con la térmica de la red en su tope (K15b). Las emisiones de esos años quedan subestimadas; "
                      "las gráficas los marcan con un círculo abierto.</p>"
                      "<table class='es-tabla'><thead><tr><th scope='col'>Escenario</th><th scope='col'>Años "
                      "subestimados</th><th scope='col'>Energía por STOELE, GWh</th><th scope='col'>Faltante de la "
                      "variante, MW (energía equivalente)</th><th scope='col'>Emisiones de energía en B1, kt</th>"
                      "<th scope='col'>Variante menos B1, kt</th></tr></thead><tbody>%s</tbody></table>"
                      % "".join(filas_s))
    partes.append("<p class='ab-fuente'>Fuente: Art6_calibracion/%s (variante por año), B2_Output_Art6/tablas/"
                  "riesgo_variante_potencia_minima.csv (emisiones, margen y sobreventa) y suficiencia_por_escenario.csv "
                  "(STOELE y topes).</p>" % VARIANTE.name)
    return _articulo_limites("".join(partes))


def _articulo_limites(cuerpo):
    return ("<article class='es-ficha' id='ficha-sin-solucion'><header><span class='ab-punto' style='background:%s'>"
            "</span><h4>Escenarios sin solución y años subestimados</h4><span class='es-tipo'>Variante diagnóstica</span>"
            "</header><div class='es-cuerpo' style='grid-template-columns:1fr'><div class='es-datos'>%s</div></div>"
            "</article>" % (NEUTRO, cuerpo))


def _mayus(s):
    return s[:1].upper() + s[1:] if s else s


def fichas_html(fuentes=True):
    D = _datos()
    intro = ("<p class='ab-tesis'>Cada ficha sigue el mismo orden: qué representa el escenario, qué cambia frente a "
             "su base, qué resulta en la corrida y qué implica para el Artículo 6. Un piso obliga al modelo a generar "
             "al menos esa energía con la tecnología; un techo le impide superarla.</p>")
    fichas = ([_ficha_referencia(D, c) for c in D["refs"]] + [_ficha_art6(D, c) for c in D["art6"]]
              + [_ficha_estado(D, d) for d in D["estados"]])
    faltan = D["R"].get("faltan") or []
    v = D["variante"]
    k15 = [c for c in faltan if v is not None and len(v[v.escenario == c])
           and bool(v[v.escenario == c]["variante_con_solucion"].all())]
    otros = [c for c in faltan if c not in k15]
    aviso = ""
    if k15:
        aviso += ("<p class='es-aviso'>%s no %s solución con la inversión térmica limitada a la expansión declarada (K15b): "
                  "sus fichas no se muestran y la <a href='#ficha-sin-solucion'>variante diagnóstica de potencia mínima"
                  "</a>, al final de las fichas, da su capacidad faltante por año.</p>"
                  % (_y([_cod(x) for x in k15]), "tienen" if len(k15) > 1 else "tiene"))
    if otros:
        aviso += ("<p class='es-aviso'>%s no %s solución óptima en la última corrida de B1 y no %s variante diagnóstica: "
                  "sus fichas no se muestran.</p>" % (_y([_cod(x) for x in otros]), "tienen" if len(otros) > 1 else "tiene",
                                                      "tienen" if len(otros) > 1 else "tiene"))
    return (_estilo(fuentes) + "<div class='ab es'>%s%s%s%s%s<p class='ab-fuente'>Fuente: %s; "
            "B1_Scenario_Config.xlsx (hojas Art6_Escenarios, Art6_Palancas, Art6_Riesgos, "
            "Art6_Adicionalidad y Art6_Headroom).</p></div>"
            % (intro, aviso, "".join(fichas), _ficha_sin_solucion(D), _comunes(D), FUENTE_SALIDAS))


# ----------------------------------------------------------------------------- matriz de supuestos
def columnas():
    """[(clave, encabezado, grupo de encabezado)] de la matriz de supuestos: los parametros que
    mueve alguna palanca de la configuracion."""
    D = _datos()
    cols = []
    for tec in D["tecs_act"]:
        fam = D["fam_palanca"].get(tec, tec)
        for par in (C.TECHO, C.PISO):
            if (tec, par) in D["palancas_act"]:
                cols.append(("act|%s|%s" % (tec, PAR[par]), PAR[par], fam))
    for k in D["fp_propias"]:
        cols.append(("fp|%s" % k, D["centrales"].get(k, k), "Factor de planta"))
    cols.append(("fp|medio", "%d clases hidro" % len(D["clases"]), "Factor de planta"))
    return cols


def _filas_supuestos(D):
    grupos = [("Referencia NDC", D["refs"])]
    for fam in D["art6"]:
        grupos.append(("%s y sus pruebas" % _nombre(D, fam),
                       [fam] + [d["miembros"][fam] for d in D["estados"] if fam in d["miembros"]]))
    return grupos


def supuestos_tabla(anio=2035):
    """Parametros de entrada de cada escenario en el anio dado, leidos del _Input.csv de cada escenario."""
    D = _datos()
    cols = columnas()
    filas = []
    for _, cods in _filas_supuestos(D):
        for e in cods:
            fila = {"codigo": e}
            for clave, _, _ in cols:
                partes = clave.split("|")
                if partes[0] == "act":
                    v = _serie(D, e, partes[1], C.TECHO if partes[2] == "techo" else C.PISO)[anio]
                elif partes[1] == "medio":
                    v = pd.DataFrame({k: _serie(D, e, k, C.FP) for k in D["clases"]}).mean(axis=1)[anio]
                else:
                    v = _serie(D, e, partes[1], C.FP)[anio]
                fila[clave] = None if pd.isna(v) else float(v)
            fila["que_cambia"] = _resumen_cambios(D, e)
            filas.append(fila)
    return pd.DataFrame(filas).set_index("codigo")


def _vacio(v):
    return v is None or (isinstance(v, float) and v != v)


def _celda_sup(v, clave):
    if _vacio(v):
        return "&ndash;"
    if v >= SIN_TECHO:
        return "sin techo"
    return _n(v, 3 if clave.startswith("fp") else 2)


def _tono(D, T, e, clave):
    """Clase de color de una celda segun de donde viene su valor."""
    def val(c):
        x = T.loc[c, clave] if c in T.index else None
        return None if _vacio(x) else round(float(x), 4)
    refs = D["refs"]
    if e in refs:
        return "ab-t-inc" if len(refs) > 1 and e == refs[0] and val(e) != val(refs[-1]) else ""
    if e not in D["art6"]:                      # estado: choque frente a su escenario
        if val(e) != val(D["base"][e]):
            return "ab-t-r"
        e = D["base"][e]
    cadena = [e]
    while cadena[-1] in D["art6"]:
        cadena.append(D["base"][cadena[-1]])
    for x, y in zip(cadena, cadena[1:]):
        if val(x) != val(y):
            return "ab-t-%s" % x.lower()
    return ""


def supuestos_html(fuentes=False):
    D = _datos()
    T = supuestos_tabla()
    cols = columnas()
    grupos, cab2 = [], []
    for _, et, g in cols:
        if grupos and grupos[-1][0] == g:
            grupos[-1][1] += 1
        else:
            grupos.append([g, 1])
        cab2.append("<th scope='col'>%s</th>" % _esc(et))
    cab1 = "".join("<th scope='colgroup' colspan='%d'>%s</th>" % (n, _esc(g)) for g, n in grupos)
    cuerpo = []
    for titulo, cods in _filas_supuestos(D):
        cuerpo.append("<tr class='grupo'><th colspan='%d'>%s</th></tr>" % (len(cols) + 2, _esc(titulo)))
        for e in cods:
            if e not in T.index:
                continue
            celdas = "".join("<td class='%s'>%s</td>" % (_tono(D, T, e, k), _celda_sup(T.loc[e, k], k))
                             for k, _, _ in cols)
            cuerpo.append("<tr><th scope='row'>%s</th>%s<td class='txt'>%s</td></tr>"
                          % (_cod(e), celdas, _esc(T.loc[e, "que_cambia"])))
    tabla = ("<div class='es-scroll'><table class='ab-sup'><thead><tr><th rowspan='2' class='izq' scope='col'>"
             "Escenario</th>%s<th rowspan='2' class='izq' scope='col'>Qué cambia</th></tr><tr>%s</tr></thead>"
             "<tbody>%s</tbody></table></div>" % (cab1, "".join(cab2), "".join(cuerpo)))
    ley = ["<span><i class='ab-t-%s'></i>palanca %s</span>" % (c.lower(), _de(D, c)) for c in D["art6"]]
    ley.append("<span><i class='ab-t-r'></i>choque del riesgo o del riesgo de operación</span>")
    if len(D["refs"]) > 1:
        ley.append("<span><i class='ab-t-inc'></i>%s: valor distinto %s</span>"
                   % (_esc(_nombre(D, D["refs"][0])), _de(D, D["refs"][-1])))
    desde = []
    for c in D["art6"]:
        x = _desde(_cambios(D, c, D["base"][c]))
        if x:
            desde.append("palancas %s desde %d" % (_de(D, c), x))
    for d in D["estados"]:
        fam, cod = next(iter(d["miembros"].items()))
        x = _desde(_cambios(D, cod, fam))
        if x:
            desde.append("%s desde %d" % (_cod(d["codigo"]), x))
    nota = ("<p class='ab-fuente'>Valores de 2035 en el _Input.csv de cada escenario (Executables), la entrada que usó "
            "el modelo. Techos y pisos: "
            "TotalTechnologyAnnualActivityUpperLimit y LowerLimit, en PJ/año (1 PJ = %s GWh). Factor de planta: "
            "CapacityFactor, fracción de la capacidad disponible en el año; la última columna es el promedio simple de "
            "las clases hidroeléctricas. Una celda sin color repite el valor de su base. Primer año con cambio: %s.</p>"
            % (_n(C.PJ_A_GWH, 2), _y(desde)))
    tesis = ("<p class='ab-tesis'>Cada escenario de Artículo 6 se construye sobre su escenario base y modifica solo los "
             "parámetros de sus palancas; cada riesgo modifica, sobre su escalón, solo los parámetros del choque. La "
             "matriz reúne esos valores para 2035 y el color indica si vienen de la base, de una palanca o de un "
             "choque.</p>")
    return (_estilo(fuentes) + "<div class='ab es'>" + tesis + tabla + "<div class='ab-ley'>%s</div>" % "".join(ley)
            + nota + "</div>")


# ----------------------------------------------------------------------------- estilos y salida
# Todas las reglas empiezan por .ab.es (el contenedor lleva las dos clases) para ganar a los estilos
# que JupyterLab y VS Code aplican a tablas, parrafos y listas de las salidas HTML.
CSS = """
.ab.es{--t:#1F2937;--t2:#4B5563;--t3:#6B7280;--l:#E3E8E6;--f:#F6F8F7;font-family:'Fira Sans','Segoe UI',Arial,sans-serif;
color:var(--t);background:#FFFFFF;border:1px solid var(--l);border-radius:8px;padding:24px 28px 20px;max-width:1180px;
line-height:1.55;font-size:15px;font-variant-numeric:tabular-nums;box-sizing:border-box;text-align:left;margin:4px 0 8px}
.ab.es *{box-sizing:border-box}
.ab.es table{table-layout:auto;margin:0;font-size:inherit;border-collapse:collapse;color:inherit;border:0}
.ab.es table th,.ab.es table td{text-align:left;vertical-align:top;white-space:normal;line-height:1.45;max-width:none}
.ab.es table tbody tr,.ab.es table tbody tr:nth-child(odd),.ab.es table tbody tr:hover{background:transparent}
.ab.es h3{margin:26px 0 4px;font-size:17px;line-height:1.3;font-weight:600;color:var(--t);border:0;padding:0}
.ab.es p{margin:0 0 10px;text-align:left}
.ab.es ul{margin:0;padding-left:18px}
.ab.es li{margin:0 0 6px}
.ab.es .ab-nota{color:var(--t3);font-size:13px;max-width:110ch}
.ab.es .ab-tesis{max-width:85ch;font-size:15.5px}
.ab.es .ab-fuente{margin:16px 0 0;color:var(--t3);font-size:12.5px;max-width:115ch}
.ab.es .ab-punto{display:inline-block;width:12px;height:12px;border-radius:50%;vertical-align:middle;margin-right:2px}
.ab.es .ab-cod{display:inline-block;margin-left:4px;padding:0 6px;border:1px solid var(--l);border-radius:4px;
font-size:11.5px;font-weight:500;color:var(--t2);vertical-align:1px;white-space:nowrap}
.ab.es .ab-sello{display:inline-block;padding:1px 9px;border-radius:999px;font-size:12.5px;font-weight:500;white-space:nowrap}
.ab.es .ab-consume{background:#FBEAE7;color:#8A2A1F}
.ab.es .ab-libre{background:#E2F3EC;color:#0B5E48}
.ab.es .ab-fuera{background:#EEF0F2;color:#4B5563}
.ab.es .ab-v-nucleo{background:#0E8F6E;color:#FFFFFF}
.ab.es .ab-v-cond{background:#FBEFD9;color:#7A4B00}
.ab.es .ab-v-desc{background:#EEF0F2;color:#4B5563}
.ab.es .ab-ley{display:flex;flex-wrap:wrap;gap:6px 18px;margin:8px 0 0;font-size:12.5px;color:var(--t2)}
.ab.es .ab-ley span{display:inline-flex;align-items:center;gap:6px}
.ab.es .ab-ley i{display:inline-block;width:14px;height:14px;border-radius:3px;border:1px solid var(--l)}
.ab.es .es-scroll{overflow-x:auto}
.ab.es .es-escalera{display:flex;flex-wrap:wrap;align-items:stretch;gap:8px;margin:10px 0 12px}
.ab.es .es-paso{flex:1 1 0;min-width:112px;border:1px solid var(--l);border-top:4px solid;border-radius:6px;
padding:10px 12px}
.ab.es .es-paso b{display:block;font-size:15px;margin:2px 0 4px}
.ab.es .es-paso .ab-cod{margin-left:0}
.ab.es .es-tipo{display:block;font-size:11.5px;letter-spacing:.06em;text-transform:uppercase;color:var(--t3);font-weight:600}
.ab.es .es-capa{flex:1.3 1 0;min-width:140px;display:flex;flex-direction:column;justify-content:center;
align-items:flex-start;gap:4px;
padding:8px 10px;background:var(--f);border-radius:6px;font-size:13px}
.ab.es .es-capa b{font-weight:600;line-height:1.3}
.ab.es .es-flecha{font-size:18px;font-weight:700;color:var(--t3);line-height:1}
.ab.es .es-kt{font-size:18px;font-weight:600}
.ab.es .es-barra{display:flex;height:16px;border-radius:4px;overflow:hidden;background:var(--f);margin:6px 0 0}
.ab.es .es-barra span{display:block;height:100%}
.ab.es table.es-matriz{width:100%;min-width:860px;font-size:13px;margin:8px 0 0}
.ab.es table.es-matriz thead th{font-size:12.5px;font-weight:600;padding:8px;border-bottom:2px solid #9AA5A1;
vertical-align:bottom}
.ab.es table.es-matriz thead th span{display:block;font-weight:400;color:var(--t3);font-size:12px}
.ab.es table.es-matriz tbody th{padding:10px 8px;font-weight:600;white-space:nowrap;border-bottom:1px solid var(--l)}
.ab.es table.es-matriz td{padding:8px;border-bottom:1px solid var(--l);border-left:1px solid var(--l)}
.ab.es table.es-matriz td .ab-cod{margin-left:0}
.ab.es table.es-matriz dl{margin:6px 0 0;display:grid;grid-template-columns:auto 1fr;gap:2px 8px}
.ab.es table.es-matriz dt{color:var(--t3);font-size:12px;font-weight:400;margin:0}
.ab.es table.es-matriz dd{margin:0;font-weight:600;text-align:right;white-space:nowrap}
.ab.es table.es-matriz dd small{display:block;font-weight:400;color:var(--t3);font-size:11.5px}
.ab.es .es-cero{color:var(--t3)}
.ab.es .es-rojo{background-color:#F9D9D4}
.ab.es .es-ambar{background-color:#FBEFD9}
.ab.es .es-sens{background-image:repeating-linear-gradient(135deg,rgba(107,114,128,.13) 0 6px,transparent 6px 12px)}
.ab.es .es-sin{color:var(--t3)}
.ab.es .es-ficha{border:1px solid var(--l);border-radius:8px;margin:18px 0 0;overflow:hidden}
.ab.es .es-ficha header{display:flex;flex-wrap:wrap;align-items:center;gap:6px 10px;padding:12px 16px;
background:var(--f);border-bottom:1px solid var(--l)}
.ab.es .es-ficha header h4{margin:0;font-size:17px;font-weight:600;color:var(--t)}
.ab.es .es-ficha header .es-tipo{display:inline;margin-left:4px}
.ab.es .es-base{margin-left:auto;font-size:13px;color:var(--t2)}
.ab.es .es-cuerpo{display:grid;grid-template-columns:minmax(0,1fr) minmax(0,1.05fr);gap:8px 24px;padding:14px 16px 16px}
@media (max-width:900px){.ab.es .es-cuerpo{grid-template-columns:1fr}}
.ab.es .es-cuerpo>dl{margin:0;padding:0;display:block}
.ab.es .es-cuerpo>dl>dt{display:block;float:none;width:auto;clear:none;padding:0;font-size:12px;font-weight:600;
letter-spacing:.06em;text-transform:uppercase;color:var(--t2);margin:14px 0 4px}
.ab.es .es-cuerpo>dl>dt:first-child{margin-top:0}
.ab.es .es-cuerpo>dl>dd{display:block;float:none;margin:0;padding:0;font-size:14px}
.ab.es .es-cuerpo dd p{margin:0 0 6px}
.ab.es .es-datos h5{margin:0 0 6px;font-size:12px;font-weight:600;letter-spacing:.06em;text-transform:uppercase;
color:var(--t2)}
.ab.es .es-datos section{margin:0 0 16px}
.ab.es table.es-tabla{width:100%;font-size:13px;margin:4px 0 0}
.ab.es table.es-tabla thead th{font-size:12px;font-weight:600;color:var(--t2);border-bottom:2px solid #9AA5A1;
padding:6px 8px;vertical-align:bottom}
.ab.es table.es-tabla td,.ab.es table.es-tabla tbody th{padding:6px 8px;border-bottom:1px solid var(--l)}
.ab.es table.es-tabla td{text-align:right;white-space:nowrap}
.ab.es table.es-tabla tbody th{font-weight:500}
.ab.es table.es-texto td{white-space:normal;text-align:left}
.ab.es table.es-tabla td.es-cuando{white-space:normal;text-align:left;min-width:92px;color:var(--t2)}
.ab.es .es-pj{display:block;color:var(--t3);font-size:11.5px;font-weight:400}
.ab.es .es-neg{color:#B42318}
.ab.es .es-cifras{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:8px;margin:0 0 10px}
.ab.es .es-cifras div{border:1px solid var(--l);border-radius:6px;padding:8px 10px}
.ab.es .es-cifras span{display:block;font-size:12px;color:var(--t2);line-height:1.3}
.ab.es .es-cifras b{display:block;font-size:19px;font-weight:600;margin:2px 0}
.ab.es .es-cifras small{display:block;font-size:11.5px;color:var(--t3);line-height:1.3}
.ab.es ul.es-lineas{list-style:none;padding:0;margin:0}
.ab.es ul.es-lineas li{margin:0 0 8px}
.ab.es ul.es-lineas p{margin:2px 0 0;color:var(--t2);font-size:13px}
.ab.es .es-fuera{font-size:12px;color:var(--t3)}
.ab.es .es-detalle{margin:8px 0 0;font-size:13px}
.ab.es .es-detalle summary{cursor:pointer;color:#0A5E51;font-weight:500}
.ab.es .es-detalle p{font-size:13px;color:var(--t2)}
.ab.es .es-aviso{background:#FBEFD9;color:#7A4B00;padding:8px 12px;border-radius:6px}
.ab.es .es-comunes{margin-top:22px;padding:4px 18px 10px;background:var(--f);border-radius:8px}
.ab.es .es-comunes h3{margin-top:12px}
.ab.es .es-comunes li{font-size:14px;max-width:110ch}
.ab.es table.ab-sup{width:100%;font-size:13px;margin:8px 0 6px}
.ab.es table.ab-sup th,.ab.es table.ab-sup td{padding:7px 8px;border-bottom:1px solid var(--l);text-align:right}
.ab.es table.ab-sup thead th{font-size:12px;font-weight:600;color:var(--t2);vertical-align:bottom}
.ab.es table.ab-sup thead tr:first-child th{border-bottom:1px solid #9AA5A1;text-align:center}
.ab.es table.ab-sup thead tr:last-child th{border-bottom:2px solid #9AA5A1}
.ab.es table.ab-sup th.izq{text-align:left}
.ab.es table.ab-sup td{white-space:nowrap}
.ab.es table.ab-sup td.txt{text-align:left;color:var(--t2);font-size:12.5px;min-width:300px;white-space:normal}
.ab.es table.ab-sup tbody th{text-align:left;font-weight:600;white-space:nowrap}
.ab.es table.ab-sup tr.grupo th{background:var(--f);font-size:12px;letter-spacing:.06em;text-transform:uppercase;
color:var(--t2);font-weight:600;padding-top:9px;text-align:left}
.ab.es .ab-t-a{background-color:#DDF1E9}
.ab.es .ab-t-b{background-color:#FBE7D3}
.ab.es .ab-t-r{background-color:#F9D9D4}
.ab.es td.ab-t-r{font-weight:600}
.ab.es .ab-t-inc{background-color:#ECEEF1}
"""


def _estilo(fuentes):
    return "<style>%s%s</style>" % (__import__("tablero")._fuentes_css() if fuentes else "", CSS)


def html(fuentes=True):
    """Mapa, fichas y matriz de supuestos en un solo fragmento (tablero)."""
    return mapa_html(fuentes) + fichas_html(False) + supuestos_html(False)


def _mostrar(h):
    from IPython.display import HTML, display
    display(HTML(h))


def mostrar_lectura(bloque=None):
    """Bloques de lectura del cuaderno: ndc, sector, escenarios o decision; sin argumento, todos. Lleva los
    estilos porque el primero abre el cuaderno."""
    import lectura
    f = {"ndc": lectura.ndc_html, "sector": lectura.sector_html, "escenarios": lectura.escenarios_html,
         "glosario": lectura.glosario_html, "hidro": lectura.hidro_html,
         "decision": lectura.decision_html, "riesgo": lectura.riesgo_html}.get(bloque, lectura.html)
    _mostrar(_estilo(fuentes=True) + f())


def mostrar_mapa():
    _mostrar(mapa_html(fuentes=True))


def mostrar_fichas():
    _mostrar(fichas_html(fuentes=False))


def mostrar_supuestos():
    _mostrar(supuestos_html(fuentes=False))


def mostrar():
    mostrar_mapa()
    mostrar_fichas()
