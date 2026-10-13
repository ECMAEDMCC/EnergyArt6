# -*- coding: utf-8 -*-
"""Bloques de lectura del visualizador, en el orden en que se presentan: el modelo de la Segunda NDC
(ndc_html), el sector energia en la NDC y en el inventario con sus iniciativas (sector_html), que
muestra cada escenario (escenarios_html) y la lectura para la decision (decision_html). html() los
concatena para la documentacion. Todo sale de la corrida y de las hojas Art6_*; cada ficha se omite
cuando la corrida no trae lo que describe."""
import html as H

import pandas as pd

import analizar
import comun as C
import configuracion as K
import explicacion as X

V = C.VENTANA
VENT = "%d-%d" % (V[0], V[-1])


def _n(v, dec=0):
    return X._n(v, dec)


def _e(s):
    return H.escape(str(s))


def _kt(v, dec=0):
    return "%s kt" % _n(v, dec)


def _tabla(cab, filas):
    return ("<table class='es-tabla es-texto'><thead><tr>%s</tr></thead><tbody>%s</tbody></table>"
            % ("".join("<th scope='col'>%s</th>" % _e(c) for c in cab),
               "".join("<tr><th scope='row'>%s</th>%s</tr>" % (f[0], "".join("<td>%s</td>" % c for c in f[1:]))
                       for f in filas)))


def _y(xs):
    xs = [x for x in xs if x]
    return "" if not xs else xs[0] if len(xs) == 1 else ", ".join(xs[:-1]) + " y " + xs[-1]


def _ficha(ident, color, titulo, tipo, izq, der):
    return X._ficha(ident, [color], titulo, [], tipo, "", izq, der)


def _ficha_ancha(ident, color, titulo, tipo, dt, parrafo, cuerpo):
    return ("<article class='es-ficha' id='ficha-%s'><header><span class='ab-punto' style='background:%s'></span>"
            "<h4>%s</h4><span class='es-tipo'>%s</span></header><div class='es-cuerpo' style='grid-template-columns:1fr'>"
            "<dl><dt>%s</dt><dd>%s</dd></dl><div class='es-datos'>%s</div></div></article>"
            % (ident, color, _e(titulo), _e(tipo), _e(dt), _e(parrafo), cuerpo))


def _envolver(fichas):
    return "<div class='ab es es-lectura'>%s</div>" % "".join(fichas)


class _Ctx:
    """Datos comunes de los bloques."""

    def __init__(self):
        self.R = analizar.resultados()
        self.D = X._datos()
        T = self.T = self.R["roles"]
        self.inc, self.con, self.esc = T["inc"], T["con"], list(T["escalera"])
        self.em = self.D["em"]
        self.M = self.R.get("metas_2035", {})
        self.a35 = V[-1]
        self.vol = self.D["vol"]
        self.estados = T["estados"]
        inv = self.R.get("inventario") or {}
        self.inv_energia = {int(k): v for k, v in (inv.get("energia") or {}).items()}
        self.inv_nac = {int(k): v for k, v in (inv.get("nacional_con_utcuts") or {}).items()}
        self.inv_nac_sin = {int(k): v for k, v in (inv.get("nacional_sin_utcuts") or {}).items()}
        self.ult = max(self.inv_energia) if self.inv_energia else None
        self.reporte = [r for r in (self.R.get("reporte") or []) if r.get("entrega") and r.get("anios_cubiertos")]

    def nom(self, c):
        return self.T["nombre"].get(c, c)

    def col(self, c):
        return X.COLOR.get(c, X.NEUTRO)

    def hr(self, c, regla="condicional"):
        h = self.D["hr"].get((c, regla))
        return float(h[str(self.a35)]) if h and str(self.a35) in h else float("nan")

    def contra_de(self, c):
        return next((d["miembros"].get(c) for d in self.estados
                     if d["grupo"] == "Contrafactual" and d["miembros"].get(c) in self.em), None)


# ----------------------------------------------------------------------------- 1. el modelo de la NDC
def ndc_html(fuentes=False):
    k = _Ctx()
    M, a35, con = k.M, k.a35, k.con
    if not M:
        return ""
    p = ("La Segunda NDC fija sus metas de %d como reducciones frente a un tendencial nacional con USCUSS: un tramo "
         "incondicional, que el país cumple con sus propios medios, y un tramo condicional adicional, sujeto a apoyo "
         "internacional. La meta incondicional es la base reservada de la contabilidad del Artículo 6: "
         "contra su nivel se mide el balance de emisiones una vez aplicados los ajustes correspondientes, y ninguna "
         "tonelada de ese tramo se transfiere. El condicional es la oferta del país; el mercado del Artículo 6 es una "
         "forma de ese apoyo, con una consecuencia contable inmediata: la tonelada transferida con ajuste "
         "correspondiente se acredita al comprador y deja de contarse para el Ecuador en cualquiera de los dos tramos."
         % a35)
    p += (" Cada meta es un nivel de emisiones de %d; la senda que une el presente con ese nivel es un supuesto de "
          "cálculo para los años intermedios." % a35)
    if k.ult:
        p += (" El cumplimiento se verifica con el inventario nacional, cuyo último año disponible es %d; hasta que "
              "exista el inventario de un año, el modelo es el instrumento ex ante de la decisión." % k.ult)
    cifras = [("Tendencial nacional, %d" % a35, _kt(M["base"]), "línea sobre la que se definen las metas"),
              ("Nivel de la meta incondicional, %d" % a35, _kt(M["meta_inc"]),
               "base reservada: %s kt de reducción" % _n(M["base"] - M["meta_inc"])),
              ("Nivel de la meta condicional, %d" % a35, _kt(M["meta_con"]),
               "oferta sujeta a apoyo: %s kt adicionales" % _n(M["meta_inc"] - M["meta_con"]))]
    if k.ult and k.inv_nac.get(k.ult) is not None:
        cifras.append(("Inventario nacional con USCUSS, %d" % k.ult, _kt(k.inv_nac[k.ult]), "último año reportado"))
    f = _ficha("lectura-ndc", k.col(con), "Tendencial y metas de la Segunda NDC", "El modelo de la NDC",
               [("Qué significa", _e(p))], [X._seccion("Cifras", X._cifras(cifras))])
    return _envolver([f])


# ----------------------------------------------------------------------------- 2. el sector energia
def sector_html(fuentes=False):
    k = _Ctx()
    fichas = []
    em, con, inc, ult = k.em, k.con, k.inc, k.ult
    ingei = C.ENERGY / "Insumos_Art6" / "INGEI_largo.csv"
    if ult and ingei.exists():
        d = pd.read_csv(ingei)
        d = d[d["anio"] == ult]
        gases = {r.gas: float(r.valor) for r in d[(d["dimension"] == "sector_gas") & (d["codigo"].astype(str) == "1")
                                                   & (~d["gas"].isin(["Total", "CO2eq"]))].itertuples()}
        cats = {str(r.codigo): float(r.valor) for r in d[(d["dimension"] == "energia_categoria") & (d["gas"] == "CO2eq")
                                                         & (d["nivel"] == 2)].itertuples()}
        tot_e = k.inv_energia[ult]
        tot_con, tot_sin = k.inv_nac.get(ult), k.inv_nac_sin.get(ult)
        gas_dom = max(gases, key=gases.get) if gases else None
        mod = float(em[con][ult]) if ult in em.index else float("nan")
        p = ("En %d el sector energía emitió %s kt CO2-eq%s. %s"
             "La categoría 1A, quema de combustibles, concentra %s kt, y las fugitivas (1B) %s kt. "
             "El Modelo Climate Lead Group de la Segunda NDC (OSeMOSYS), con las correcciones K01-K15 de la referencia "
             "corregida %s, cubre el sector completo (demanda final, generación eléctrica, fugitivas y refinación) y "
             "reproduce %d con %s kt, %s %% respecto del inventario; a partir de ahí "
             "proyecta. Los escenarios de Artículo 6 actúan sobre la generación eléctrica (1A1a): la eólica, la "
             "solar, la geotermia y la biomasa sustituyen generación térmica con fuel oil y diésel."
             % (ult, _n(tot_e),
                (", el %s %% del total nacional con USCUSS y el %s %% sin USCUSS" % (
                    _n(100.0 * tot_e / tot_con, 1), _n(100.0 * tot_e / tot_sin, 1))) if tot_con and tot_sin else "",
                ("El gas dominante es el %s, con %s kt (%s %% del sector); el CH4 aporta %s kt y el N2O %s kt. "
                 % (gas_dom, _n(gases[gas_dom]), _n(100.0 * gases[gas_dom] / tot_e, 1), _n(gases.get("CH4", 0)),
                    _n(gases.get("N2O", 0)))) if gas_dom else "",
                _n(cats.get("1A", 0)), _n(cats.get("1B", 0)), con, ult, _n(mod), _n(100.0 * (mod - tot_e) / tot_e, 1)))
        cifras = [("Sector energía, %d" % ult, _kt(tot_e), "inventario nacional (AR5)")]
        if tot_con:
            cifras.append(("Peso en el total con USCUSS", "%s %%" % _n(100.0 * tot_e / tot_con, 1), "%s kt nacionales" % _n(tot_con)))
        if gas_dom:
            cifras.append(("Gas dominante", "%s · %s %%" % (gas_dom, _n(100.0 * gases[gas_dom] / tot_e, 1)), _kt(gases[gas_dom])))
        cifras += [("Quema de combustibles (1A), %d" % ult, _kt(cats.get("1A", 0)), "incluye transporte y generación"),
                   ("Modelo en %d (%s)" % (ult, con), _kt(mod), "diferencia %s %% frente al inventario" % _n(100.0 * (mod - tot_e) / tot_e, 1))]
        fichas.append(_ficha("lectura-sector", k.col(inc), "El sector energía en el inventario y en el modelo", "El sector energía",
                             [("Qué pesa y qué se modela", _e(p))], [X._seccion("Cifras", X._cifras(cifras))]))
    L = [x for x in k.D["AD"] if str(x.get("escenario_NDC") or "") in ("Incondicional", "Condicional")]
    if L:
        def kt(x):
            v = x.get("kt_anio_declarado")
            return float(v) if isinstance(v, (int, float)) else 0.0

        def en_modelo(x):
            v = str(x.get("escenario_art6") or "")
            if v in k.esc:
                return "modelada en %s" % v
            if "fuera del modelo" in v:
                return "declarada, fuera del modelo"
            if v == "fuera":
                return "fuera del portafolio"
            return v
        L = sorted(L, key=lambda x: (0 if x.get("escenario_NDC") == "Incondicional" else 1, str(x.get("codigo"))))
        inc_l = [x for x in L if x.get("escenario_NDC") == "Incondicional"]
        con_l = [x for x in L if x.get("escenario_NDC") == "Condicional"]
        filas = [("<span class='ab-cod'>%s</span> %s" % (_e(x.get("codigo")), _e(x.get("linea"))), _e(x.get("escenario_NDC")),
                  _e(x.get("periodo") or ""), _n(kt(x), 1) if kt(x) else "", _e(en_modelo(x)),
                  _e(x.get("adicionalidad") or "")) for x in L]
        p = ("La Segunda NDC declara en el sector energía %s iniciativas incondicionales, con %s kt por año en su último "
             "año, y %s condicionales, con %s kt por año. Las incondicionales son compromisos propios del país y no "
             "generan unidades transferibles; las condicionales son las candidatas a financiarse con el mercado. "
             "El Escenario A toma las condicionales que el modelo puede representar en la generación eléctrica; las "
             "de transporte y las de Galápagos entran con su cifra declarada, fuera del modelo."
             % (_n(len(inc_l)), _n(sum(kt(x) for x in inc_l)), _n(len(con_l)), _n(sum(kt(x) for x in con_l))))
        fichas.append(_ficha_ancha("lectura-iniciativas", k.col(con), "Iniciativas de la Segunda NDC en el sector energía",
                                   "El sector energía", "Qué declara la NDC", p,
                                   _tabla(["Iniciativa", "Tramo", "Periodo", "kt/año declarado", "En este ejercicio",
                                           "Adicionalidad"], filas)))
    return _envolver(fichas) if fichas else ""


# ----------------------------------------------------------------------------- 3. los escenarios
def escenarios_html(fuentes=False):
    k = _Ctx()
    T, inc, con, esc, em, a35, vol, estados = k.T, k.inc, k.con, k.esc, k.em, k.a35, k.vol, k.estados
    filas = [("%s <span class='ab-cod'>%s</span>" % (_e(k.nom(inc)), inc),
              "referencia corregida del Artículo 6: %s del Modelo CLG con las correcciones K01-K15; el país cumple solo "
              "su tramo incondicional" % (T.get("inc_clg") or "el incondicional"),
              _n(em[inc][a35]), "base reservada; contra ella se mide la sobreventa"),
             ("%s <span class='ab-cod'>%s</span>" % (_e(k.nom(con)), con),
              "referencia corregida del Artículo 6: %s del Modelo CLG con las correcciones K01-K15, con sus techos y "
              "pisos" % (T.get("con_clg") or "el condicional"),
              _n(em[con][a35]), "la proyección de la NDC con apoyo internacional: %s kt bajo el incondicional en %d"
              % (_n(em[inc][a35] - em[con][a35]), a35))]
    for c in esc:
        b = T["base"].get(c, con)
        narr = str(k.D["por"].get(c, {}).get("narrativa") or "").split(". ")[0].rstrip(".")
        sirve = ["capa de %s kt en %s frente %s" % (_n(sum(em[b][a] - em[c][a] for a in V), 1), VENT,
                                                     "al condicional" if b == con else "a " + b)]
        x = k.contra_de(c)
        if x and (c, "atribuible_por_retiro") in vol:
            sirve.append("aporte atribuible por retiro de %s kt (%s menos %s)" % (_n(vol[(c, "atribuible_por_retiro")], 1), x, c))
        filas.append(("%s <span class='ab-cod'>%s</span>" % (_e(k.nom(c)), c), _e(narr) + ".", _n(em[c][a35]), _e("; ".join(sirve))))
        if x:
            filas.append(("%s <span class='ab-cod'>%s</span>" % (_e(k.nom(x)), x),
                          "el sistema de %s sin las actividades que %s financia" % (c, c), _n(em[x][a35]),
                          "escenario de referencia de esas actividades; su diferencia con %s es el aporte atribuible" % c))
    for d in estados:
        if d["grupo"] == "Contrafactual":
            continue
        cods = [m for m in d["miembros"].values() if m in em]
        if not cods:
            continue
        vals = [em[m][a35] for m in cods]
        que = "riesgo sobre el sistema" if d["grupo"] == "Riesgo" else "riesgo de operación, sin actividad de mitigación asociada"
        uso = ("margen de %d entre %s y %s kt con la regla prudente"
               % (a35, _n(min(k.hr(m, "prudente") for m in cods)), _n(max(k.hr(m, "prudente") for m in cods)))
               if d["grupo"] == "Riesgo" else "mide la respuesta del resultado a otro supuesto de despacho")
        filas.append(("%s <span class='ab-cod'>%s</span>" % (_e(d.get("rotulo") or d["nombre"]), _e(", ".join(cods))), que,
                      "%s a %s" % (_n(min(vals)), _n(max(vals))) if len(cods) > 1 else _n(vals[0]), uso))
    frases_r = _y([str(d.get("frase") or X._minus(d["nombre"])) for d in estados if d["grupo"] == "Riesgo"])
    p = ("Los escenarios son óptimos de mínimo costo del modelo de la Segunda NDC y se presentan como ejercicio "
         "analítico. Cada uno responde a una pregunta: qué valen las actividades del condicional "
         "si el mercado las financia (A), hasta dónde llega una ambición mayor fuera de la NDC (B), qué agrega actuar sobre la demanda (C), qué queda de ese "
         "potencial bajo los riesgos (" + _e(frases_r) + ") y cuánto depende de un "
         "supuesto de operación (el riesgo de operación: sin pisos térmicos). En conjunto aproximan una participación potencial del Ecuador en los mercados de "
         "carbono bajo el Artículo 6.")
    f = _ficha_ancha("lectura-escenarios", k.col(esc[0]) if esc else k.col(con), "Qué muestra cada escenario",
                     "Los escenarios", "Para qué están", p,
                     _tabla(["Escenario", "Qué representa", "Emisiones de energía en %d, kt" % a35, "Para qué sirve"], filas))
    return _envolver([f])


# ----------------------------------------------------------------------------- 3b. glosario e hidroelectricas
TERMINOS = [
    ("Palanca", "Una fila de la hoja Electrical del libro de configuración: fija un parámetro de OSeMOSYS para una "
                "tecnología y un periodo (un techo o un piso de capacidad o de generación, una inversión mínima, un "
                "factor de planta). Cada escenario es la copia del condicional más sus palancas; la hoja Art6_Palancas "
                "las documenta una por una."),
    ("Techo y piso", "Límites que el optimizador no puede cruzar: el techo (TotalAnnualMaxCapacity, "
                     "TotalTechnologyAnnualActivityUpperLimit) acota por arriba la capacidad o la generación de una "
                     "tecnología; el piso (…LowerLimit) obliga a un mínimo. En los escenarios A y B los techos son el "
                     "potencial de la capacidad declarada y el despacho lo decide el modelo, salvo el piso geotérmico de "
                     "Chachimbiro (A5) y los pisos térmicos, que fijan una generación mínima: el de fuel oil es K16, el "
                     "mínimo observado 2015-2025, y los de diésel y gas natural son los del Modelo CLG."),
    ("Inversión mínima", "TotalAnnualMinCapacityInvestment: capacidad que el modelo debe construir en un año dado. Así "
                         "entran los proyectos declarados (eólica, solar, geotermia, biomasa) con su año de operación."),
    ("Factor de planta", "CapacityFactor: fracción del año en que una central opera a plena potencia. La eólica del A "
                         "usa el valor observado (0,359) y el año seco aplica a cada clase hidroeléctrica la razón entre "
                         "el caudal de 2024 y su media histórica."),
    ("Capa", "Diferencia de emisiones del sector energía entre un escenario y su base, sumada en el marco 2026-2035 de la Segunda NDC y, para la oferta, en la ventana de transacciones 2031-2035. "
             "La capa del A se mide frente al condicional; la del B, frente al A; la del C, frente al B."),
    ("Contrafactual y aporte atribuible", "El contrafactual es el mismo sistema sin los proyectos del escenario (A sin "
                                         "sus proyectos). La diferencia de emisiones con el escenario es el aporte "
                                         "atribuible por retiro: lo que esos proyectos reducen antes de las pruebas de "
                                         "adicionalidad y de sobreventa."),
    ("Margen", "Distancia, en 2035, entre la meta incondicional y las emisiones nacionales del escenario: lo "
                          "que puede transferirse con ajuste correspondiente sin incumplir la meta. Negativo: incumple."),
    ("Regla base y regla prudente", "Cómo se proyectan los sectores que el modelo no cubre. Regla base: cumplen su "
                                    "tramo condicional. Regla prudente: cumplen solo su tramo incondicional, lo que deja "
                                    "menos margen. Toda cifra de margen se reporta con las dos."),
    ("Riesgo", "Prueba de estrés sobre el sistema. Coca Codo: el derrateo del 20 % de Coca Codo Sinclair desde 2027 "
               "(CCDER), la salida de Coca Codo sola desde 2029 (CCSOLO, caso central) y la salida de la clase de Coca "
               "Codo, Coca Codo Sinclair y Sopladora, desde 2029 (CCOFF). Hidrología: el año seco severo con los caudales "
               "de 2024 todos los años desde 2026 (ANOSECO, cota), un año seco cada tres (ANOSEC3, caso central) y el año "
               "seco moderado (ANOSECM). Además, la salida de la clase y el año seco severo a la vez (CCOFFANOSECO) y la "
               "importación cero desde Colombia (IMP0), y la situación actual anclada a 2026 (ACT y ACT-DEM): en 2026, la demanda, la "
               "hidrología por clase, Coca Codo y la importación observadas; desde 2027, un año seco cada tres e importación "
               "cero; en ACT la demanda vuelve a la del Modelo CLG desde 2027 y en ACT-DEM el nivel de 2026 persiste. Los estados de riesgo llevan un respaldo de emergencia (tope de fuel oil "
               "liberado con potencia nueva cara y STOELE cerrado), supuesto de cierre como la térmica arrendada que el país "
               "contrata hoy. Riesgo de operación: sin pisos térmicos (FOI), "
               "un cambio de operación que no es un proyecto y no genera unidades; por eso queda fuera de los volúmenes "
               "transferibles."),
    ("Adicionalidad", "Condición de que la reducción no ocurriría sin el ingreso del mercado. Firme: proyecto con "
                      "barreras demostradas; por demostrar: pendiente de memoria de cálculo; sin adicionalidad: proyectos "
                      "que se ejecutan de todos modos. El veredicto de compradores (hoja Art6_Adicionalidad) la completa."),
    ("Ajuste correspondiente", "Regla del Artículo 6.2: la tonelada transferida se suma al balance de emisiones del "
                               "Ecuador y se resta al del comprador, de modo que solo una parte la cuenta."),
]


def glosario_html(fuentes=False):
    k = _Ctx()
    filas = [("<b>%s</b>" % _e(a), _e(b)) for a, b in TERMINOS]
    p = ("Los términos que usan las fichas, las gráficas y los parámetros de entrada, en el orden en que aparecen al "
         "construir un escenario y al leer sus resultados.")
    f = _ficha_ancha("lectura-glosario", k.col(k.con), "Términos del ejercicio", "Los escenarios", "Qué significa cada uno",
                     p, _tabla(["Término", "Definición"], filas))
    return _envolver([f])


HIDRO = {"DAM": "embalse", "ROR": "pasada", "A": "amazónica (oriental)", "P": "del Pacífico (occidental)",
         "B": "grande", "M": "mediana", "S": "pequeña"}


def hidro_html(fuentes=False):
    k = _Ctx()
    con = k.con
    try:
        S = X._salida_tec(C.huella(analizar.JSON))
    except Exception:
        return ""
    clases = sorted({t for s, t in zip(S.index.get_level_values(0), S.index.get_level_values(1))
                     if s == con and str(t).startswith("PPH") and len(str(t)) == 8})
    if not clases:
        return ""
    plantas = {}
    try:
        for r in K.hoja("AnoSeco_Centrales"):
            c = str(r.get("Clase del modelo") or "")
            if c and r.get("Central"):
                plantas.setdefault(c, []).append(str(r.get("Central")))
    except Exception:
        pass
    try:
        riesgos = {str(r.get("grupo")): r for r in K.hoja("Riesgos")}
    except Exception:
        riesgos = {}
    a0, a35 = C.VENTANA[0] - 5, C.VENTANA[-1]
    filas = []
    for c in clases:
        tipo, vert, tam = c[3:6], c[6], c[7]
        fila = S.loc[(con, c)]
        cap0 = float(fila["TotalCapacityAnnual"].get(a0, 0.0)) * 1000.0 if "TotalCapacityAnnual" in fila else float("nan")
        cap35 = float(fila["TotalCapacityAnnual"].get(a35, 0.0)) * 1000.0 if "TotalCapacityAnnual" in fila else float("nan")
        gen0 = float(fila["TotalTechnologyAnnualActivity"].get(a0, 0.0)) * 277.78 if "TotalTechnologyAnnualActivity" in fila else float("nan")
        papel = "año seco: caudales de 2024"
        if c == "PPHRORAB" and "CCOFF" in riesgos:
            papel = ("sale de operación desde %s (CCOFF, salida de la clase); Coca Codo sola desde %s (CCSOLO); derrateo "
                     "desde %s (CCDER); año seco: caudales de 2024" % (riesgos["CCOFF"].get("desde"),
                                                                      riesgos.get("CCSOLO", {}).get("desde", "s. f."),
                                                                      riesgos.get("CCDER", {}).get("desde", "s. f.")))
        filas.append(("<span class='ab-cod'>%s</span>" % c, HIDRO.get(tipo, tipo), HIDRO.get(vert, vert), HIDRO.get(tam, tam),
                      _n(cap0), _n(cap35), _n(gen0) if gen0 == gen0 else "",
                      _e(", ".join(plantas.get(c, [])) or "sin centrales de referencia en la hoja"), _e(papel)))
    try:
        mw_cc = float(S.loc[(con, "PPHRORAB")]["TotalCapacityAnnual"].get(int(riesgos["CCOFF"]["desde"]) - 1, 0.0)) * 1000.0
    except Exception:
        mw_cc = float("nan")
    p = ("El modelo agrupa las centrales hidroeléctricas en clases, y el código de cada clase dice qué es: PPH es "
         "hidroeléctrica; DAM, con embalse, o ROR, de pasada (sin embalse de regulación); A, vertiente amazónica, o P, "
         "vertiente del Pacífico; B, M o S, grande, mediana o pequeña. Coca Codo Sinclair es una central de pasada, "
         "grande, de la vertiente amazónica: la clase PPHRORAB, que comparte con Sopladora. Los riesgos actúan sobre las "
         "clases: el derrateo de Coca Codo (CCDER) reduce desde %s la parte de Coca Codo en esa clase; la salida de Coca "
         "Codo sola (CCSOLO, caso central) retira desde %s esa parte; la salida de la clase (CCOFF) retira desde %s la "
         "clase completa%s; y el año seco aplica a cada clase la razón entre el caudal observado de 2024 y su media "
         "histórica, todos los años en la cota (ANOSECO) o uno de cada tres en el caso central (ANOSEC3)."
         % (riesgos.get("CCDER", {}).get("desde", "s. f."), riesgos.get("CCSOLO", {}).get("desde", "s. f."),
            riesgos.get("CCOFF", {}).get("desde", "s. f."),
            (", %s MW en %s" % (_n(mw_cc), con)) if mw_cc == mw_cc and mw_cc > 0 else ""))
    f = _ficha_ancha("lectura-hidro", k.col(con), "Clases hidroeléctricas del modelo", "Los escenarios", "Qué es cada clase",
                     p, _tabla(["Clase", "Tipo", "Vertiente", "Tamaño", "MW %d (%s)" % (a0, con), "MW %d" % a35, "GWh %d" % a0,
                                "Centrales de referencia", "Papel en los riesgos"], filas))
    return _envolver([f])


# ----------------------------------------------------------------------------- 5. lectura para la decision
def decision_html(fuentes=False):
    k = _Ctx()
    T, con, esc, em, a35, estados = k.T, k.con, k.esc, k.em, k.a35, k.estados
    fichas = []
    if esc:
        desp = k.R.get("termica_desplazable_GWh", {})
        base_de = {c: T["base"].get(c, con) for c in esc}
        ceros = [c for c in esc if abs(em[base_de[c]][a35] - em[c][a35]) < 1.0]
        if ceros and con in desp and all(c in desp and base_de[c] in desp for c in ceros):
            gen = pd.read_csv(C.TABLAS / "generacion_familia.csv")
            cap = pd.read_csv(C.TABLAS / "capacidad_familia.csv")

            def gwh(e, fams):
                x = gen[(gen.escenario == e) & (gen.anio == a35) & gen.familia.isin(fams)]["GWh"]
                return float(x.sum())

            def mw(e, fam):
                x = cap[(cap.escenario == e) & (cap.anio == a35) & (cap.familia == fam)]["MW"]
                return float(x.sum())
            termicas = [f for f, _, tt in C.FAMILIAS if tt == "termica"]
            td_con = desp[con][C.IDX[a35]]
            cifras = [("Térmica desplazable en %d, %s" % (a35, con), "%s GWh" % _n(td_con, 1),
                       "generación térmica por encima de los pisos de despacho")]
            cifras += [("Capa de %s en %d" % (c, a35), _kt(em[base_de[c]][a35] - em[c][a35], 1), "frente a %s" % base_de[c])
                       for c in ceros]
            frase_foi = ""
            try:
                piso = float(X._serie(k.D, con, "PPFOI", C.PISO)[a35])
                S = X._salida_tec(C.huella(analizar.JSON))
                foi = {x: float(S.loc[(x, "PPFOI")]["TotalTechnologyAnnualActivity"].get(a35, 0.0)) for x in [con] + ceros}
                if all(abs(v - piso) < 1e-3 for v in foi.values()):
                    frase_foi = (" El fuel oil queda en su piso de despacho de %s PJ en %s." % (_n(piso, 2), _y([con] + ceros)))
                cifras.append(("Fuel oil en %d" % a35, " · ".join("%s PJ" % _n(foi[x], 2) for x in [con] + ceros),
                               "%s; piso de %s PJ" % (" · ".join([con] + ceros), _n(piso, 2))))
            except Exception:
                pass
            ter = {x: gwh(x, termicas) for x in [con] + ceros}
            iguales = all(abs(ter[c] - ter[base_de[c]]) < 0.5 for c in ceros)
            frase_ren = ""
            mas = [c for c in ceros if mw(c, "Eólica") + mw(c, "Solar") > mw(con, "Eólica") + mw(con, "Solar") + 0.5]
            if mas:
                c1 = mas[-1]
                frase_ren = (" La capacidad eólica y solar del %s, %s y %s MW frente a %s y %s MW de %s, genera %s y %s GWh "
                             "frente a %s y %s GWh: la capacidad adicional queda sin despacho."
                             % (c1, _n(mw(c1, "Eólica")), _n(mw(c1, "Solar")), _n(mw(con, "Eólica")), _n(mw(con, "Solar")),
                                con, _n(gwh(c1, ["Eólica"])), _n(gwh(c1, ["Solar"])), _n(gwh(con, ["Eólica"])),
                                _n(gwh(con, ["Solar"]))))
            sens_txt = []
            for c in ceros:
                x = next((r for r in k.R.get("capas_por_estado", []) if r.get("grupo") == "Sensibilidad"
                          and r.get("capa") == c and r.get(str(a35)) is not None), None)
                if x is not None:
                    sens_txt.append("la capa del %s valdría %s kt" % (c, _n(float(x[str(a35)]))))
                    cifras.append(("Capa de %s sin pisos, %d" % (c, a35), _kt(float(x[str(a35)]), 1),
                                   "%s frente a %s" % (x["escenario"], x["base"])))
            otras = [c for c in esc if c not in ceros]
            frase_otras = ""
            if otras:
                egf = k.R.get("emisiones_generacion_familia_kt", {})
                pp = lambda e: sum(v[C.IDX[a35]] for v in egf.get(e, {}).values())
                sub = pd.read_csv(C.TABLAS / "emisiones_subsector_kt.csv")
                sub = sub[sub.anio == a35].pivot_table(index="subsector", columns="escenario", values="kt", aggfunc="sum")
                for c in otras:
                    b_c = base_de[c]
                    if abs(pp(c) - pp(b_c)) < 0.5 and c in sub and b_c in sub:
                        dif = (sub[b_c] - sub[c]).sort_values(ascending=False)
                        donde = [(s, v) for s, v in dif.items() if abs(v) >= 0.5]
                        frase_otras += (" La capa del %s, de %s kt en %d, no sale de la generación eléctrica: sus emisiones "
                                        "de la generación son iguales a las del %s, y la reducción ocurre en %s."
                                        % (c, _n(em[b_c][a35] - em[c][a35]), a35, b_c,
                                           _y(["%s (%s kt)" % (s.lower(), _n(v)) for s, v in donde]) or "otros subsectores"))
            p = ("En %d %s solo tiene %s GWh de generación térmica por encima de sus pisos de despacho (K16 en PPFOI; Modelo CLG en PPDSL y PPNGS): "
                 "el resto de la térmica y la importación quedan en sus pisos, y una renovable adicional solo sustituye "
                 "lo que está por encima de ellos.%s %s %s en %d la misma energía térmica que %s, de modo que %s %s cero en "
                 "%d.%s%s%s El valor de %s en el año meta depende, en consecuencia, de decisiones ajenas al modelo: la "
                 "térmica que debe permanecer en operación por confiabilidad, el crecimiento de la demanda por "
                 "electrificación y la disponibilidad de almacenamiento o exportación, que el modelo no representa."
                 % (a35, con, _n(td_con, 1), frase_foi, _y(ceros), "generan" if len(ceros) > 1 else "genera", a35,
                    "su base" if iguales else "CONA6", "sus capas" if len(ceros) > 1 else "su capa",
                    "valen" if len(ceros) > 1 else "vale", a35, frase_ren,
                    (" Sin pisos térmicos (sensibilidad FOI), %s en %d." % (_y(sens_txt), a35))
                    if sens_txt else "", frase_otras, "esas capas" if len(ceros) > 1 else "esa capa"))
            fichas.append(_ficha("lectura-saturacion", k.col(ceros[-1]),
                                 "Por qué %s no %s emisiones en %d" % (_y(ceros), "reducen" if len(ceros) > 1 else "reduce", a35),
                                 "Lectura para la decisión", [("Hallazgo", _e(p))], [X._seccion("Cifras", X._cifras(cifras))]))
    try:
        it = pd.read_csv(C.TABLAS / "itmos_por_linea.csv")
        tramo = {str(x.get("codigo")): str(x.get("escenario_NDC") or "") for x in k.D["AD"]}
        vered = {str(x.get("codigo")): str(x.get("veredicto_compradores") or "") for x in k.D["AD"]}
        it["tramo"] = it["codigo"].astype(str).map(tramo)
        it["veredicto"] = it["codigo"].astype(str).map(vered)
        cond = it[it["tramo"] == "Condicional"].copy()
        cond["v"] = pd.to_numeric(cond["volumen_declarado_2031_2035"], errors="coerce").fillna(0.0)
        if len(cond):
            tot = cond["v"].sum()
            sin = cond[cond["adicionalidad"] == "Sin adicionalidad"]
            desc = cond[(cond["adicionalidad"] != "Sin adicionalidad") & (cond["veredicto"] == "Descartar")]
            firme = cond[cond["adicionalidad"] == "Firme"]
            resto = cond.drop(sin.index).drop(desc.index).drop(firme.index)
            top = esc[-1] if esc else con
            comb = [d for d in estados if d["grupo"] == "Riesgo" and len(d.get("componentes", [])) >= 2 and d["miembros"].get(top) in em]
            peor = ((" Con %s a la vez, el margen desciende a %s kt y %s kt, respectivamente." % (
                _e(comb[0].get("frase") or X._minus(comb[0]["nombre"])), _n(k.hr(comb[0]["miembros"][top])), _n(k.hr(comb[0]["miembros"][top], "prudente"))))
                    if comb else "")
            p = ("El condicional declarado para %s suma %s kt. De ese total, %s kt carecen de adicionalidad (%s); %s kt "
                 "corresponden a líneas que los compradores descartan (%s); %s kt permanecen por demostrar (%s); y %s kt "
                 "cuentan con adicionalidad firme (%s). Con el sistema intacto, el margen de %d alcanza %s kt si los demás "
                 "sectores cumplen su tramo condicional (regla base) y %s kt si solo cumplen el incondicional (regla prudente).%s El volumen transferible "
                 "queda determinado, en consecuencia, por la adicionalidad que admita el comprador y por la regla de "
                 "autorización bajo riesgo que adopte el país, antes que por el modelo."
                 % (VENT, _n(tot), _n(sin["v"].sum()), _y([str(c) for c in sin["codigo"]]) or "ninguna",
                    _n(desc["v"].sum()), _y([str(c) for c in desc["codigo"]]) or "ninguna", _n(resto["v"].sum()),
                    _y([str(c) for c in resto["codigo"]]) or "ninguna", _n(firme["v"].sum()),
                    _y([str(c) for c in firme["codigo"]]) or "ninguna", a35, _n(k.hr(top)), _n(k.hr(top, "prudente")), peor))
            cifras = [("Condicional declarado, %s" % VENT, _kt(tot), "%s líneas" % _n(len(cond))),
                      ("Sin adicionalidad", _kt(sin["v"].sum()), _y([str(c) for c in sin["codigo"]]) or None),
                      ("Descartar", _kt(desc["v"].sum()), _y([str(c) for c in desc["codigo"]]) or None),
                      ("Por demostrar", _kt(resto["v"].sum()), _y([str(c) for c in resto["codigo"]]) or None),
                      ("Firme", _kt(firme["v"].sum()), _y([str(c) for c in firme["codigo"]]) or None),
                      ("Margen de %d con el sistema intacto" % a35, "%s · %s kt" % (_n(k.hr(top)), _n(k.hr(top, "prudente"))),
                       "regla base · regla prudente")]
            if comb:
                cifras.append(("Margen de %d con %s" % (a35, _e(comb[0].get("frase") or X._minus(comb[0]["nombre"]))),
                               "%s · %s kt" % (_n(k.hr(comb[0]["miembros"][top])), _n(k.hr(comb[0]["miembros"][top], "prudente"))),
                               "regla base · regla prudente"))
            fichas.append(_ficha("lectura-vendible", k.col(top), "Qué parte del condicional puede transferirse",
                                 "Lectura para la decisión", [("Hallazgo", _e(p))],
                                 [X._seccion("Cascada del condicional declarado", X._cifras(cifras))]))
    except Exception as exc:                                   # la seccion es informativa: nunca tumba el tablero
        fichas.append("<p class='es-nota'>Volumen transferible del condicional no disponible: %s</p>" % _e(exc))
    nota = ("<p class='ab-fuente'>Cifras de la corrida (salidas de B1 de cada escenario en Executables del Modelo Climate "
            "Lead Group, rama art6-escenarios, y resultados_art6.json) y de las hojas Art6_* del libro de configuración; "
            "marco de análisis 2026-2035 y ventana de transacciones %s. Los escenarios son óptimos de mínimo costo con costos "
            "de relleno y se presentan como ejercicio analítico.</p>" % VENT)
    return _envolver(fichas + [nota]) if fichas else ""


def riesgo_html(fuentes=False):
    """Sobreventa por año y riesgo, respaldo de emergencia, oferta en tres niveles y factor del MWh desplazado frente al
    margen de operación (tablas del 13-10-2026 de analizar.tablas_13_10). Todo sale de resultados_art6.json."""
    k = _Ctx()
    R = k.R
    fichas = []
    color = k.col(k.esc[-1]) if k.esc else X.NEUTRO
    rot = lambda suf: K.rotulo(suf, "Sistema intacto") if suf else "Sistema intacto"
    sv = (R.get("sobreventa_anual") or {}).get("resumen") or []
    if sv:
        comb = [("CLG", "prudente"), ("CLG", "condicional"), ("corregida", "condicional"), ("corregida", "prudente")]
        estados = list(dict.fromkeys(x["sufijo"] for x in sv))
        filas = []
        for s in estados:
            celdas = []
            for proy, regla in comb:
                x = next((y for y in sv if y["sufijo"] == s and y["proyeccion"] == proy and y["regla"] == regla), None)
                if x is None:
                    celdas.append("–")
                    continue
                a1 = x.get("primer_anio_margen_negativo_tras_transferir")
                a1 = int(a1) if a1 is not None and a1 == a1 else None          # None o NaN: sin año negativo
                celdas.append("%s<span class='es-pj'>%s</span>" % (_kt(x["sobreventa_2031_2035"]),
                                                                   ("primer año negativo %d" % a1) if a1 else "sin año negativo"))
            filas.append([_e(rot(s))] + celdas)
        con_sv = sorted({rot(x["sufijo"]) for x in sv if (x["sobreventa_2031_2035"] or 0) > 0.5})
        aut = next((x["autorizado_2031_2035"] for x in sv if x["sufijo"] == "" and x["proyeccion"] == "CLG"), None)
        regla_a = (R.get("sobreventa_anual") or {}).get("regla_de_autorizacion") or "lo transferible con el sistema intacto"
        p = ("Se autoriza %s: %s en %s. Después ocurre el riesgo y, con ajuste correspondiente, lo transferido se suma a "
             "las emisiones del país. La sobreventa de cada año es lo autorizado que no cabe en el margen de ese año "
             "(regla anual de ajuste); las otras tres lecturas del margen son sensibilidad. %s"
             % (regla_a, _kt(aut) if aut is not None else "s. d.", VENT,
                ("Hay sobreventa en al menos una combinación de regla y proyección con: %s." % _y(con_sv)) if con_sv
                else "Ningún riesgo deja sobreventa con estas reglas."))
        fichas.append(_ficha_ancha("riesgo-sobreventa", color, "Sobreventa por año y por riesgo", "Lectura para la decisión",
                                   "Cómo se lee", p,
                                   _tabla(["Estado", "CLG, regla prudente (autorización)", "CLG, regla condicional",
                                           "Corregida, regla condicional", "Corregida, regla prudente"], filas)
                                   + "<p class='ab-fuente'>Sobreventa acumulada %s y primer año en que el margen, después "
                                     "de transferir lo autorizado, queda negativo. Detalle por año en "
                                     "B2_Output_Art6/tablas/sobreventa_anual_por_riesgo.csv.</p>" % VENT))
    rp = (R.get("respaldo") or {}).get("resumen") or []
    if rp:
        h_ = lambda v, d: _n(v, d) if v is not None else "–"
        filas = [[_e(x.get("rotulo") or x["escenario"]), str(x["primer_anio_con_respaldo"] or "–"),
                  _n(x["respaldo_max_MW"], 1), _n(x["respaldo_2031_2035_GWh"]), _n(x["respaldo_2031_2035_kt_CO2e"]),
                  _n(x["ENS_2031_2035_GWh"]), h_(x["ENS_max_pct_demanda"], 2), h_(x["horas_corte_max_por_dia"], 2),
                  h_(x["horas_corte_max_por_anio"], 1), h_(x["horas_corte_max_por_dia_estiaje_6_meses"], 2),
                  _n(x["STOELE_2026_2035_GWh"])] for x in rp]
        con_r = [x["escenario"] for x in rp if x["respaldo_max_MW"] > 0.5]
        p = ("El respaldo de emergencia es un supuesto de cierre, como la térmica arrendada que el país contrata hoy: en "
             "los estados de riesgo (e INCA6G) el tope de PPFOI se libera desde 2026 con su potencia nueva cara y STOELE "
             "se cierra, de modo que el modelo construye solo la potencia que falta. %s Si ese respaldo no se generara, la "
             "energía no suministrada equivalente sería el respaldo por las eficiencias de transmisión y distribución del "
             "modelo, y las horas de corte equivalentes son 24 por esa energía sobre la demanda eléctrica final del año; "
             "la variante de estiaje concentra el déficit en seis meses. Son indicadores, no un pronóstico de "
             "racionamiento." % (("Lo necesitan %s." % _y(con_r)) if con_r
                                  else "Ningún escenario construye potencia sobre el tope K15b."))
        fichas.append(_ficha_ancha("riesgo-respaldo", color, "Respaldo de emergencia y horas de corte equivalentes",
                                   "Lectura para la decisión", "Cómo se lee", p,
                                   _tabla(["Escenario", "Primer año con respaldo",
                                           "Respaldo máximo, %s" % (R.get("respaldo") or {}).get("rotulo_MW", "MW"),
                                           "Energía de respaldo %s, GWh" % VENT, "Emisiones del respaldo %s, kt CO2-eq" % VENT,
                                           "Energía no suministrada equivalente %s, GWh" % VENT,
                                           "Energía no suministrada, máximo, % de la demanda",
                                           "Horas de corte equivalentes, máximo por día",
                                           "Horas de corte equivalentes, máximo por año",
                                           "Horas por día con estiaje de 6 meses, máximo", "STOELE 2026-2035, GWh"], filas)
                                   + "<p class='ab-fuente'>%s Detalle por año en "
                                     "B2_Output_Art6/tablas/respaldo_por_escenario.csv.</p>"
                                   % _e((R.get("respaldo") or {}).get("nota", ""))))
    ac = R.get("act_2026") or {}
    t26 = [x for x in ac.get("tabla") or [] if x["anio"] == 2026]
    if t26:
        ob = ac["observado"]
        filas = [[_e(x["escenario"]), _n(x["crecimiento_demanda_pct"], 2) + " %",
                  _n(x["participacion_termica_SNI_pct"], 1) + " %", _n(x["crecimiento_hidro_pct"], 2) + " %",
                  _n(x["fp_coca_codo_participacion_2025_pct"], 1) + " %", _n(x["importacion_GWh"], 1)] for x in t26]
        filas.append(["Observado 2026", _n(ob["crecimiento_demanda_ene_ago_pct"], 2) + " % (enero a agosto)",
                      "%s %% (enero a agosto); %s %% al 10-10" % (_n(ob["participacion_termica_ene_ago_pct"], 1),
                                                              _n(ob["participacion_termica_al_10_oct_pct"], 1)),
                      _n(ob["crecimiento_hidro_ene_ago_pct"], 2) + " % (enero a agosto)",
                      "%s %% al 10-10; %s %% estimado del año" % (_n(ob["fp_coca_codo_al_10_oct_pct"], 1),
                                                               _n(ob["fp_coca_codo_2026_estimado_pct"], 1)),
                      _n(ob["importacion_2026_antes_07_09_GWh"], 1) + " (antes del 07-09)"])
        c25 = next((x for x in ac.get("tabla") or [] if x["anio"] == 2025), None)
        base25 = ((" El modelo ya tenía en 2025 %s %% de térmica frente a %s %% observado, los dos con la importación en "
                   "el denominador, y esa diferencia se arrastra a 2026." % (_n(c25["participacion_termica_SNI_pct"], 1),
                                                                            _n(ob["participacion_termica_2025_pct"], 1)))
                  if c25 and ob.get("participacion_termica_2025_pct") is not None else "")
        p = ("La situación actual se ancla a 2026: demanda eléctrica con el crecimiento observado de enero a agosto, "
             "hidrología observada de cada clase, Coca Codo con su factor de planta de 2026 e importación hasta el "
             "06-09-2026. Desde 2027, un año seco cada tres e importación cero; la demanda vuelve a la del Modelo CLG (ACT) "
             "o mantiene el nivel de 2026 (ACT-DEM)." + base25)
        fichas.append(_ficha_ancha("riesgo-act2026", color, "Situación actual 2026 frente a lo observado",
                                   "Lectura para la decisión", "Cómo se lee", p,
                                   _tabla(["Escenario", "Crecimiento de la demanda", "Participación térmica",
                                           "Crecimiento de la hidro", "Factor de planta de Coca Codo",
                                           "Importación, GWh"], filas)
                                   + "<p class='ab-fuente'>%s %s B2_Output_Art6/tablas/act_2026_contraste.csv.</p>"
                                   % (_e(ac.get("perimetro", "")), _e(ac.get("nota", "")))))
    on = R.get("oferta_niveles") or {}
    if on.get("niveles"):
        nombre_caso = {"central_K16_con_gas": "Caso central con K16 y la expansión a gas declarada",
                       "K16_sin_gas": "Con K16, sin la expansión a gas declarada (familia GAS)",
                       "pisos_CLG_12_10": "Con los pisos del Modelo CLG (sensibilidad del 12-10-2026)"}
        con_r = {x["nivel"]: x for x in on.get("niveles_con_reserva") or []}
        filas = [[_e(str(x.get("rotulo") or x["nivel"])[:1].upper() + str(x.get("rotulo") or x["nivel"])[1:]),
                  _kt(x["kt_2031_2035"]),
                  _kt(con_r[x["nivel"]]["kt_2031_2035"]) if x["nivel"] in con_r else "–",
                  _e(nombre_caso.get(x["caso"], x["caso"])), "sí" if x.get("es_nivel_de_oferta", True) else "no"]
                 for x in on["niveles"]]
        filas_c = [[_e(nombre_caso.get(c, c)), _kt(v), _e(on["supuestos"].get(c, ""))] for c, v in on["totales"].items()]
        res = on.get("lineas_en_reserva") or "ninguna"
        p = ("La oferta %s suma las líneas declaradas (firme y condicionadas) y las capas que calcula el modelo; %s queda en "
             "reserva, fuera de la oferta, con %s declarados, mientras no se demuestre su adicionalidad regulatoria "
             "(decisión del 13-10-2026). Cada nivel se nombra por su caso: el central, con K16 y gas declarado; el caso con "
             "los pisos del Modelo CLG (corrida del 12-10), y la sensibilidad sin gas de la capa 1, que mide el volumen "
             "físico sin la expansión a gas declarada y no es un nivel de oferta." % (VENT, res, _kt(on.get("kt_en_reserva", 0.0), 1)))
        fichas.append(_ficha_ancha("riesgo-oferta", color, "Oferta %s por caso" % VENT, "Lectura para la decisión",
                                   "Cómo se lee", p,
                                   _tabla(["Nivel", "Oferta (sin %s)" % res, "Con %s (antes de la decisión)" % res,
                                           "Caso", "Nivel de oferta"], filas)
                                   + _tabla(["Caso", "Oferta", "Supuesto"], filas_c)
                                   + "<p class='ab-fuente'>B2_Output_Art6/tablas/oferta_tres_niveles.csv y oferta_por_caso.csv; "
                                     "sensibilidad con pisos del Modelo CLG desde %s (md5 %s).</p>"
                                   % (_e(on["sensibilidad_pisos_CLG"]["json"].split("_stale_")[-1]),
                                      _e(str(on["sensibilidad_pisos_CLG"]["md5"])[:8]))))
    fichas += _fichas_decisiones(R, color, rot)
    fm = R.get("factor_frente_al_margen") or {}
    tab = [x for x in fm.get("tabla") or [] if x["periodo"] == "%d-%d" % (V[0], V[-1])]
    if tab:
        filas = [[_e("%s sobre %s (%s)" % (x["escenario"], x["base"], x["caso"])),
                  _n(x["red_desplazada_GWh_brutos"]),
                  _n(x["factor_CO2_neto_red_t_MWh"], 4) if x["factor_CO2_neto_red_t_MWh"] is not None else "–",
                  _n(x["razon_frente_al_margen_operacion"], 3) if x["razon_frente_al_margen_operacion"] is not None else "–",
                  _n(x["razon_frente_a_media_no_bajo_costo"], 3) if x["razon_frente_a_media_no_bajo_costo"] is not None
                  else "–",
                  _n(x["factor_CO2e_bruto_t_MWh"], 4) if x["factor_CO2e_bruto_t_MWh"] is not None else "–"] for x in tab]
        p = ("Factor de cada capa en %s: CO2 de la generación de la red (PPFOI, PPDSL y PPNGS) que la capa evita, por MWh "
             "neto que deja de generar esa red, frente al margen de operación oficial de 2025 (%s t CO2/MWh) y frente a la "
             "media de los generadores de no bajo costo (%s), su comparable sin lambda."
             % (VENT, _n(fm["margen_operacion_2025"], 4), _n(fm["media_no_bajo_costo_2025"], 4)))
        fichas.append(_ficha_ancha("riesgo-factor", color, "Factor del MWh desplazado frente al margen de operación",
                                   "Lectura para la decisión", "Cómo se lee", p,
                                   _tabla(["Capa", "Red desplazada, GWh brutos", "Factor CO2 neto de la red, t/MWh",
                                           "Razón frente al margen de operación", "Razón frente a la media de no bajo costo",
                                           "Factor CO2-eq bruto de toda la térmica, t/MWh"], filas)
                                   + "<p class='ab-fuente'>%s B2_Output_Art6/tablas/factor_desplazado_frente_al_margen.csv."
                                     "</p>" % _e(fm.get("perimetro", ""))))
    if not fichas:
        return ""
    nota = ("<p class='ab-fuente'>Cifras de la corrida de B1 (Executables del Modelo Climate Lead Group, rama "
            "art6-escenarios) y de resultados_art6.json. Los escenarios son óptimos de mínimo costo con costos de relleno "
            "y se presentan como ejercicio analítico.</p>")
    return _envolver(fichas + [nota])


def _fichas_decisiones(R, color, rot):
    """Sobreventa por método de ajuste y subconjunto de oferta, reserva por año y autorizable ex post (decisiones del
    13-10-2026). Todo sale de resultados_art6.json; lectura de autorización: Modelo CLG, regla prudente."""
    dec = R.get("decisiones_13_10") or {}
    if not dec:
        return []
    fichas = []
    subs = dec["subconjuntos"]
    central = dec["subconjunto_central"]
    lect = (dec["autorizacion"]["proyeccion"], dec["autorizacion"]["regla"])
    sv = [x for x in R.get("sobreventa_metodo_subconjunto") or [] if (x["proyeccion"], x["regla"]) == lect]
    estados = list(dict.fromkeys(x["sufijo"] for x in sv))
    ref = lambda s: " (referencia)" if s in dec.get("estados_de_referencia", []) else ""
    if sv:
        filas = []
        for s in estados:
            celdas = []
            for sb in subs:
                v = {x["metodo"]: x["sobreventa_kt"] for x in sv if x["sufijo"] == s and x["subconjunto"] == sb["clave"]}
                celdas.append("%s<span class='es-pj'>promedio %s</span>" % (_kt(v.get("anual", 0.0)),
                                                                            _kt(v.get("promedio", 0.0))))
            filas.append([_e(rot(s) + ref(s))] + celdas)
        p = ("Lo autorizado de cada subconjunto es su oferta %s con el sistema intacto (proyección del Modelo CLG, regla "
             "prudente). Regla anual o de trayectoria: cada año de reducción se compara con el margen de ese año. Método de promedio "
             "(Decisión 2/CMA.3, anexo, párr. 7; aritmética del NDC-CAT): el ajuste de %d es la suma transferida en "
             "%d-%d dividida por %d, y la sobreventa es la parte de ese ajuste que no cabe en el margen de %d. Las otras "
             "tres lecturas están en la tabla." % (VENT, V[-1], C.MARCO[0], C.MARCO[-1], dec["anios_periodo_ndc"], V[-1]))
        fichas.append(_ficha_ancha("riesgo-metodos", color, "Sobreventa por método de ajuste y subconjunto de oferta",
                                   "Lectura para la decisión", "Cómo se lee", p,
                                   _tabla(["Estado"] + ["%s (autorizado %s)" % (sb["nombre"], _kt(sb["autorizado_2031_2035"]))
                                                        for sb in subs], filas)
                                   + "<p class='ab-fuente'>Regla anual arriba y método de promedio debajo, kt CO2-eq "
                                     "%s. B2_Output_Art6/tablas/sobreventa_por_metodo_y_subconjunto.csv.</p>" % VENT))
    rv = [x for x in (R.get("reserva_por_aniada") or {}).get("resumen") or [] if x["subconjunto"] == central]
    if rv:
        filas = []
        for x in rv:
            celdas = [_kt(x["autorizable_por_aniada"].get(str(a), 0.0)) for a in V]
            filas.append([_e(rot(x["sufijo"]) + ref(x["sufijo"]))] + celdas
                         + [_kt(x["autorizable_2031_2035"]), "%s<span class='es-pj'>%s %%</span>"
                            % (_kt(x["reserva_2031_2035"]), _n(x["reserva_pct"] or 0.0, 1)),
                            "%s %%" % _n(x["reserva_uniforme_equivalente_pct"], 1)])
        p = ("Para cada estado, lo autorizable de cada año sin dejar negativo su margen con el Modelo CLG y la "
             "regla prudente: el mínimo entre la oferta del año y el margen. La suma es lo transferible sin incumplir "
             "del estado. La reserva uniforme equivalente es el porcentaje que, igual para todos los años, cubriría el "
             "año más expuesto. La situación actual anclada a 2026, con demanda transitoria (ACT) y persistente (ACT-DEM), y "
             "la salida de Coca Codo sola son los estados de referencia.")
        fichas.append(_ficha_ancha("riesgo-reserva", color, "Reserva por año", "Lectura para la decisión", "Cómo se lee", p,
                                   _tabla(["Estado"] + ["Autorizable %d" % a for a in V]
                                          + ["Autorizable %s" % VENT, "Reserva %s" % VENT, "Reserva uniforme equivalente"],
                                          filas)
                                   + "<p class='ab-fuente'>Oferta sin las líneas en reserva. Detalle por subconjunto en "
                                     "B2_Output_Art6/tablas/reserva_por_aniada.csv.</p>"))
    ep = [x for x in (R.get("autorizable_ex_post") or {}).get("resumen") or []
          if x["subconjunto"] == central and x["lectura_de_autorizacion"]]
    if ep:
        filas = [[_e(rot(x["sufijo"]) + ref(x["sufijo"])), _kt(x["reduccion_estado_2031_2035"]),
                  _kt(x["autorizable_ex_post_2031_2035"]), _kt(x["autorizado_ex_ante_2031_2035"]),
                  _kt(x.get("autorizable_ex_post_sin_tope_2031_2035", 0.0))] for x in ep]
        fichas.append(_ficha_ancha("riesgo-expost", color, "Autorización de lo verificado ex post", "Lectura para la decisión",
                                   "Cómo se lee", (R.get("autorizable_ex_post") or {}).get("nota", ""),
                                   _tabla(["Estado", "Reducción que produce el estado",
                                           "Autorizable ex post con tope en la oferta del año (valor central)",
                                           "Autorizado ex ante", "Ex post sin tope (informativo)"], filas)
                                   + "<p class='ab-fuente'>Modelo CLG, regla prudente, %s, oferta sin las líneas en reserva. "
                                     "Detalle por año, subconjunto y lectura en "
                                     "B2_Output_Art6/tablas/autorizable_ex_post.csv.</p>" % VENT))
    return fichas


def html(fuentes=False, glosario=True):
    """Todos los bloques, en el orden de lectura; el glosario va antes de los escenarios. La
    documentacion lo publica aparte, en la introduccion (glosario=False)."""
    bloques = (ndc_html, sector_html) + ((glosario_html,) if glosario else ()) + (escenarios_html, hidro_html,
                                                                                 decision_html, riesgo_html)
    return "".join(x for x in (f() for f in bloques) if x)
