# -*- coding: utf-8 -*-
"""Guia de lectura de cada grafica: que muestra, como leerla, que dice el modelo y que implica para
la decision. Las cifras salen de la corrida (salidas de B1 de cada escenario en Executables, a traves del
analisis) y cada frase que depende de un resultado se escribe solo si la corrida trae los escenarios que la
sostienen, con su condicion (sube o baja, alcanza o no). Las series de la NDC que no produce el modelo de energia
(agregacion nacional del Modelo CLG, metas publicadas, inventario) y la informacion adicional de las hojas Art6_*
(nombres de lineas, veredictos, precios, fuentes) se identifican como tales.

guias(D) devuelve {gid: texto} con cuatro parrafos "Etiqueta. texto"; partes(texto) los separa y
html(texto) los dibuja como una ficha para el cuaderno y el tablero.
"""
import html as H
import math
import re
from collections import Counter

import pandas as pd

import comun as C
import configuracion as K
import graficar as G

N = {2: "dos", 3: "tres", 4: "cuatro", 5: "cinco", 6: "seis", 7: "siete", 8: "ocho", 9: "nueve", 10: "diez"}
SUBSECTOR = {"Generación eléctrica": "la generación eléctrica", "Transporte": "el transporte", "Industria": "la industria",
             "Residencial": "el sector residencial", "Comercial y público": "el sector comercial y público",
             "Agro, construcción y otros": "agro, construcción y otros", "Refinación": "la refinación",
             "Fugitivas de petróleo y gas": "las fugitivas de petróleo y gas"}
COLOR_TXT = ["verdes", "ocre", "moradas", "rojas", "verde claro"]       # nombres de graficar.ESCALONES


def _m(v, dec=0):
    if v is None or (isinstance(v, float) and math.isnan(v)):
        return "s. d."
    s = ("{:,.%df}" % dec).format(abs(v)).replace(",", " ").replace(".", ",")
    return ("−" if round(v, dec) < 0 else "") + s


def _pct(v, dec=1):
    return _m(v, dec) + " %"


PRUDENTE = "regla prudente (los demás sectores cumplen solo su tramo incondicional)"


ETIQUETAS = ("Qué muestra", "Cómo leerla", "Qué dice el modelo", "Qué dicen las series de la NDC",
             "Qué dice el análisis", "Para la decisión")
_ETIQUETA = re.compile(r"(%s)\.\s+(.*)" % "|".join(re.escape(e) for e in ETIQUETAS), re.S)


def partes(texto):
    """[(etiqueta, cuerpo)] de una guia; etiqueta vacia si el parrafo no empieza con una de ETIQUETAS."""
    out = []
    for p in [x.strip() for x in texto.split("\n\n") if x.strip()]:
        m = _ETIQUETA.match(p)
        out.append((m.group(1), m.group(2)) if m else ("", p))
    return out


def _g(et_modelo="Qué dice el modelo", **partes):
    orden = (("muestra", "Qué muestra"), ("leer", "Cómo leerla"), ("modelo", et_modelo),
             ("decision", "Para la decisión"))
    texto = (chr(10) * 2).join("%s. %s" % (et, partes[k]) for k, et in orden if partes.get(k))
    # la regla prudente se declara con su supuesto la primera vez que aparece en cada guia
    if "regla prudente" in texto and "cumplen solo su tramo incondicional" not in texto:
        texto = texto.replace("regla prudente", PRUDENTE, 1)
    return texto


def _y(xs):
    return C.enumerar([x for x in xs if x])


def _mayus(s):
    return s[:1].upper() + s[1:] if s else s


def _minus(s):
    s = str(s)
    return s[:1].lower() + s[1:] if len(s) > 1 and s[1:2].islower() else s


def _cuantos(n):
    return N.get(n, str(n))


def _con_verbo(items, verbo, prep):
    """«el A queda en X kt y el B en Y kt»: el verbo solo en el primer elemento."""
    return _y(["%s %s %s %s" % (suj, verbo, prep, resto) if i == 0 else "%s %s %s" % (suj, prep, resto)
               for i, (suj, resto) in enumerate(items)])


def _al(D, c):
    """«al condicional» o «al A»: la base de la capa del escenario c, con contracción."""
    b = D.base.get(c)
    return "al condicional" if b == D.con else "al %s" % b


def _con(d):
    """«con CCOFF y año seco»: el nombre del estado precedido de «con», en minuscula salvo siglas."""
    return "con %s" % (d.get("frase") or _minus(d["nombre"])) if d else ""


def _una(n):
    return "una" if n == 1 else _cuantos(n)


def _leer_stoele(cods):
    """Frase de los circulos abiertos: anios en que el escenario pasa energia por STOELE (emisiones subestimadas)."""
    sub = {c: G.subestimados(c) for c in dict.fromkeys(c for c in cods if c)}
    sub = {c: s for c, s in sub.items() if s}
    if not sub:
        return ""
    return (" Los círculos abiertos marcan años con emisiones subestimadas: el modelo pasa energía por STOELE por falta "
            "de potencia, con la térmica de la red en su tope (K15b): %s." % _y(["%s en %s" % (c, C.tramos(s))
                                                                                  for c, s in sorted(sub.items())]))


def _lineas_modelo(D):
    """Lineas de Art6_Adicionalidad de las capas del modelo (escenario_art6 igual a un escalon) y las
    que entran fuera del modelo con su potencial declarado."""
    ad = K.hoja("Adicionalidad")
    esc = set(D.esc)
    modelo = [x for x in ad if str(x.get("escenario_art6") or "").strip() in esc]
    fuera = [x for x in ad if "fuera del modelo" in str(x.get("escenario_art6") or "")]
    return modelo, fuera


def _frase_lineas(D):
    """Conteo de las lineas por adicionalidad firme y veredicto de compradores potenciales, calculado
    desde Art6_Adicionalidad."""
    modelo, fuera = _lineas_modelo(D)
    if not modelo:
        return ""
    firmes = [x for x in modelo if str(x.get("adicionalidad")) == "Firme"]
    resto = [x for x in modelo if x not in firmes]
    partes = []
    if firmes:
        partes.append("%s %s adicionalidad firme (%s)" % (_una(len(firmes)), "tiene" if len(firmes) == 1 else "tienen",
                                                          _y([str(x["linea"]) for x in firmes])))
    cuenta = Counter(str(x["veredicto_compradores"]) for x in resto if x.get("veredicto_compradores"))
    primero = True
    for v, n in sorted(cuenta.items(), key=lambda kv: (-kv[1], kv[0])):
        if primero:
            partes.append("%s %s como «%s»" % (_una(n), "figura" if n == 1 else "figuran", v))
            primero = False
        else:
            partes.append("%s como «%s»" % (_una(n), v))
    sin = [x for x in resto if not x.get("veredicto_compradores")]
    if sin:
        escs = sorted({str(x["escenario_art6"]).strip() for x in sin})
        todas = len(escs) == 1 and len(sin) == len([x for x in modelo if str(x["escenario_art6"]).strip() == escs[0]])
        if todas:
            partes.append("%s del %s no %s veredicto" % ("la" if len(sin) == 1 else "las " + _una(len(sin)), escs[0],
                                                       "tiene" if len(sin) == 1 else "tienen"))
        else:
            partes.append("%s no %s veredicto" % (_una(len(sin)), "tiene" if len(sin) == 1 else "tienen"))
    txt = "De las %s líneas de las capas del modelo, %s." % (_una(len(modelo)), _y(partes))
    if fuera:
        cf = Counter(str(x.get("veredicto_compradores") or "sin veredicto") for x in fuera)
        transporte = all(re.search(r"Tranv|Metro|Monorriel|Transporte", str(x["linea"])) for x in fuera)
        tipo = " de transporte" if transporte else ""
        if len(cf) == 1:
            v = next(iter(cf))
            txt += " Fuera del modelo, %s %s%s %s como «%s» y %s con su potencial declarado." % (
                "la" if len(fuera) == 1 else "las " + _una(len(fuera)), "línea" if len(fuera) == 1 else "líneas", tipo,
                "figura" if len(fuera) == 1 else "figuran", v, "entra" if len(fuera) == 1 else "entran")
        else:
            txt += " Fuera del modelo entran %s líneas%s con su potencial declarado: %s." % (
                _una(len(fuera)), tipo, _y(["%s como «%s»" % (_una(n), v) for v, n in cf.most_common()]))
    return txt


def _veredictos_capas(D):
    """Veredicto de compradores de las lineas que llevan las capas del modelo (sin las que entran con
    su volumen declarado): Counter {veredicto: lineas}."""
    return Counter(str(x.get("veredicto_compradores") or "sin veredicto")
                   for c in D.capas for x in G._lineas_de(D, c))


def guias(D):
    em, R = D.em, D.R
    V = C.VENTANA
    inc, con, top, esc = D.inc, D.con, D.top, D.esc
    a0 = esc[0] if esc else None
    comb = D.combinado()
    comb_a0 = D.combinado(a0) if a0 else None
    t = pd.DataFrame(R["potencial_art6"]["tabla"])
    nom = D.nombre

    def sel(suf, reg, col):
        if t.empty or col is None:
            return float("nan")
        x = t[(t.sufijo == suf) & (t.regla == reg)][col]
        return float(x.iloc[0]) if len(x) else float("nan")

    def sub35(e, s):
        x = D.sub[(D.sub.escenario == e) & (D.sub.subsector == s) & (D.sub.anio == 2035)]["kt"]
        return float(x.sum())

    gen = R["generacion_2035_GWh"]

    def gtot(e):
        return sum(gen[e].values())

    def mw(e, f, a=2035):
        x = D.cap[(D.cap.escenario == e) & (D.cap.familia == f) & (D.cap.anio == a)]["MW"]
        return float(x.iloc[0]) if len(x) else 0.0

    def vol(e, regla):
        x = D.vol[(D.vol.escenario == e) & (D.vol.regla == regla)]["total_2031_2035"]
        return float(x.iloc[0]) if e and len(x) else float("nan")

    def genv(e, f, anios=V):
        x = D.gen[(D.gen.escenario == e) & (D.gen.familia == f) & D.gen.anio.isin(anios)]["GWh"]
        return float(x.sum())

    def adic(e):
        return round(sum(max(0.0, em[con][a] - em[e][a]) for a in V), 1)     # redondeo de las tablas

    tramo = round(sum(em[inc][a] - em[con][a] for a in V), 1)
    anios = list(range(2026, 2036))
    pp = "Generación eléctrica"
    desp = R["termica_desplazable_GWh"]
    cero = [0.0] * len(C.ANIOS)
    ad = K.hoja("Adicionalidad")
    por_cod = {x["codigo"]: x for x in ad}
    grupos = R.get("grupos_de_lineas", {})
    firmes = [por_cod[c] for c in grupos.get("firme", []) if c in por_cod]
    nombres_firmes = _y([str(x["linea"]) for x in firmes])
    condicionadas = [x for x in ad if x.get("veredicto_compradores") == "Condicionada"]
    declaradas = [por_cod[c] for c in grupos.get("condicionadas_declaradas", []) if c in por_cod]
    fuera_modelo = [x for x in declaradas if "fuera del modelo" in str(x.get("escenario_art6") or "")]
    kt = lambda x: float(x["kt_anio_declarado"]) if isinstance(x.get("kt_anio_declarado"), (int, float)) else 0.0
    cond = sorted([x for x in ad if x.get("escenario_NDC") == "Condicional"], key=kt, reverse=True)
    mayores = cond[:2]
    inicios = [int(m.group(1)) for x in mayores for m in [re.match(r"\s*(\d{4})", str(x.get("periodo") or ""))] if m]
    entrada = max(inicios) if inicios else None
    nombres_mayores = ("las iniciativas " + _y([str(x["linea"]) for x in mayores])) if mayores else ""
    kt_cond = sum(kt(x) for x in cond)
    p_mayores = 100.0 * sum(kt(x) for x in mayores) / kt_cond if kt_cond else 0.0
    vered = _veredictos_capas(D)

    # participacion de la eolica y la solar en la generacion renovable que agrega el ultimo escalon
    if top:
        agrega = {f: genv(top, f) - genv(con, f) for f, _, tt in C.FAMILIAS if tt == "ernc"}
        pos = sum(v for v in agrega.values() if v > 0)
        p_ws = 100.0 * sum(max(0.0, agrega.get(f, 0.0)) for f in ("Eólica", "Solar")) / pos if pos else 0.0
    else:
        p_ws = 0.0

    # firme y oferta con el sistema intacto, y lo transferible
    of_i = sel("", "condicional", "oferta_total")
    firme_nom = next((n for n, _, clave in R["potencial_art6"]["bloques"] if clave == "firme"), None)
    firme = sel("", "condicional", firme_nom) if firme_nom else 0.0
    tr_i = sel("", "condicional", "transferible_sin_incumplir")
    transferible_txt = ("pueden transferirse los %s kt CO₂e ofertables" % _m(of_i) if abs(tr_i - of_i) < 0.5
                        else "pueden transferirse %s de los %s kt CO₂e ofertables" % (_m(tr_i), _m(of_i)))
    suf_c = "-" + comb["sufijo"] if comb else None
    tr_c = sel(suf_c, "prudente", "transferible_sin_incumplir") if comb else float("nan")
    m_comb = D.miembro(top, comb) if comb else None
    riesgo_baja = comb is not None and not math.isnan(tr_c) and tr_c < tr_i - 0.5

    # oraciones sobre la firme y los veredictos (informacion adicional de Art6_Adicionalidad)
    if firme > 0:
        frase_firme = "%s%s kt de la oferta tienen adicionalidad firme: %s." % (
            "Solo " if firme < of_i - 0.5 else "", _m(firme), nombres_firmes)
    else:
        frase_firme = "Ninguna línea de la oferta tiene adicionalidad firme."
    frase_vered = _frase_lineas(D)
    frase_ws = ("La eólica y la solar aportan el %s de la generación renovable que el %s%s agrega en 2031-2035 frente "
                "al condicional." % (_pct(p_ws, 0), top, ", último escalón de la escalera," if len(esc) > 1
                                     else "")) if top else ""

    L = {}
    L["g00_indicadores"] = _g(
        muestra="Cifras de la corrida que resumen la decisión: la oferta potencial de ITMO del sector energía en "
                "2031-2035, la parte con adicionalidad firme%s y el volumen que puede transferirse sin incumplir la "
                "meta incondicional, con el sistema intacto%s." % (
                    (", el margen de 2035 %s" % _con(comb)) if comb else "", (" y %s" % _con(comb)) if comb else ""),
        leer="Las barras horizontales comparan el volumen transferible con la oferta total, que marca la raya "
             "negra. Un margen en rojo es negativo: el país quedaría por encima de su meta incondicional aun sin "
             "transferir.",
        modelo=("La corrida no trae escenarios de Artículo 6: no hay oferta que resumir." if t.empty else
                "Con el sistema intacto %s.%s" % (transferible_txt, (
                    " %s, en la regla prudente, el volumen transferible %s %s kt y el margen de 2035 del %s es de "
                    "%s kt." % (_mayus(_con(comb)), "cae a" if riesgo_baja else "queda en", _m(tr_c), top,
                                _m(D.hr35(m_comb, "prudente")))) if comb else "")),
        decision=" ".join(x for x in (
            frase_firme, frase_ws, frase_vered,
            "El potencial depende además de que el sistema hidroeléctrico opere como prevé la NDC." if riesgo_baja else "")
            if x))

    leer01 = "El área ámbar, entre el incondicional y el condicional, es el tramo condicional."
    riesgos_top = [d for d in D.riesgos if D.miembro(top, d)] if top else []
    if top:
        leer01 = "El área verde, entre el condicional y el %s, es la reducción adicional a toda la NDC. %s" % (top, leer01)
        if riesgos_top:
            leer01 += (" Los botones aplican %s sobre %s; el área roja marca los años en que el escenario emite más que "
                       "el condicional." % (_y([d.get("frase") or _minus(d["nombre"]) for d in riesgos_top]), _y(esc)))
    modelo01 = "El tramo condicional suma %s kt en 2031-2035." % _m(tramo)
    if top:
        modelo01 = ("Con el sistema intacto, la reducción adicional a la NDC suma %s kt en 2031-2035%s. %s"
                    % (_m(adic(top)), (", de los cuales %s kt corresponden al %s" % (_m(adic(a0)), a0))
                       if a0 and a0 != top else "", modelo01))
        bajo = [(d, adic(D.miembro(top, d))) for d in riesgos_top]
        if bajo and all(v < 0.5 for _, v in bajo):
            modelo01 += " Con %s, la reducción adicional del %s se anula." % (
                "cualquiera de los riesgos" if len(bajo) > 1 else _minus(bajo[0][0]["nombre"]), top)
        elif bajo:
            modelo01 += " Bajo riesgo, la reducción adicional del %s queda en %s." % (
                top, _y(["%s kt %s" % (_m(v), _con(d)) for d, v in bajo]))
    leer01 += _leer_stoele([D.miembro(top, d) for d in riesgos_top])
    L["g01_itmos_area"] = _g(
        muestra="Emisiones del sector energía en kt CO₂e (Output.csv de cada escenario) de %s entre 2020 y 2035, con la ventana "
                "de transacciones 2031-2035 sombreada dentro de la Segunda NDC 2026-2035." % _y([G._el(nom(c)) for c in [inc, con] + esc]),
        leer=leer01,
        modelo=modelo01,
        decision=" ".join(x for x in (
            "El área verde es lo único que el país podría transferir sin renunciar a ninguna meta." if top else "",
            ("Bajo riesgo hidroeléctrico se reduce, y el %s de la generación renovable que la sostiene es eólica y solar."
             % _pct(p_ws, 0)) if riesgo_baja else "",
            ("El ámbar solo se transfiere renunciando a la meta condicional e incluye %s, las condicionales de mayor "
             "reducción declarada, que figuran como «%s»." % (
                 nombres_mayores, _y(sorted({str(x["adicionalidad"]) for x in mayores})))) if mayores else "") if x))

    bloques = R["potencial_art6"]["bloques"]
    partes02 = []
    for n, nivel, clave in bloques:
        if clave == "firme":
            partes02.append("Verde oscuro: %s, con adicionalidad firme y el potencial que declara el Plan de "
                            "Implementación de la Segunda NDC." % nombres_firmes)
        elif clave == "declarado":
            partes02.append("Verde pálido: %s %s condicionadas con su potencial declarado." % (
                _cuantos(len(declaradas)), "línea" if len(declaradas) == 1 else "líneas"))
        elif clave.startswith("capa:"):
            c = clave.split(":", 1)[1]
            b = D.base.get(c)
            suma = {f: genv(c, f) - genv(b, f) for f, _, tt in C.FAMILIAS if tt == "ernc"} if b else {}
            pos = sum(v for v in suma.values() if v > 0)
            princ = [f.lower() for f, v in sorted(suma.items(), key=lambda kv: -kv[1]) if pos and v / pos >= 0.1]
            partes02.append("%s: la capa del %s calculada por el modelo%s%s." % (
                "Ocre" if D.capa(c)["fuera_ndc"] else "Verde claro", c,
                ", fuera de la NDC" if D.capa(c)["fuera_ndc"] else "",
                (", con generación nueva sobre todo %s" % _y(princ)) if princ else ""))
    if any(G._rayado(D, clave) for _, _, clave in bloques):
        partes02.append("El rayado marca las capas en las que la mayoría de las líneas tiene veredicto de compradores "
                        "potenciales «Descartar».")
    partes02.append("Los botones cambian la regla para los otros cuatro sectores.")
    if firmes:
        dec02 = "Para un comprador, la oferta realista es la de adicionalidad firme, %s" % nombres_firmes
    else:
        dec02 = "Para un comprador no hay oferta con adicionalidad firme"
    modelo_l, fuera_l = _lineas_modelo(D)
    cond_m = [x for x in modelo_l if x.get("veredicto_compradores") == "Condicionada"]
    cond_f = [x for x in fuera_l if x.get("veredicto_compradores") == "Condicionada"]
    if condicionadas:
        dec02 += (", a la que pueden sumarse, si demuestran su adicionalidad, las líneas con veredicto «Condicionada»: "
                  "%s." % _y([x for x in ("%s de las capas del modelo" % _una(len(cond_m)) if cond_m else "",
                                          "%s fuera del modelo" % _una(len(cond_f)) if cond_f else "") if x]))
    else:
        dec02 += "."
    L["g02_potencial"] = _g(
        muestra="A la izquierda, de qué se compone la oferta potencial de ITMO 2031-2035 por nivel de adicionalidad "
                "(kt CO₂e); a la derecha, cuánto de esa oferta cabe en el margen de la meta incondicional con el "
                "sistema intacto y bajo cada riesgo, según la regla para los sectores que el modelo no cubre.",
        leer=" ".join(partes02),
        modelo=("La corrida no trae escenarios de Artículo 6: no hay oferta que medir." if t.empty else
                "Con el sistema intacto %s.%s La adicionalidad firme suma %s kt, el %s de la oferta." % (
                    transferible_txt, (" %s, en la regla prudente, %s kt." % (_mayus(_con(comb)), _m(tr_c))) if comb else "",
                    _m(firme), _pct(100.0 * firme / of_i if of_i else 0.0))),
        decision=" ".join(x for x in (
            dec02, frase_vered, frase_ws,
            "El ICVCM no aprobó metodologías de renovables conectadas a red bajo sus principios de alta calidad."
            if vered.get("Descartar") else "") if x))

    vista_riesgos = [c for c in esc if any(D.miembro(c, d) for d in D.riesgos)]
    sens_txt = _y([_minus(G._rot(d)) for d in D.sens if any(D.miembro(c, d) for c in esc)])
    modelo03 = "En 2035 el incondicional llega a %s kt y el condicional a %s kt%s." % (
        _m(em[inc][2035]), _m(em[con][2035]),
        ("; %s" % _con_verbo([("el %s" % c, "%s kt" % _m(em[c][2035])) for c in esc], "queda", "en")) if esc else "")
    if comb and esc:
        sube = [(c, em[D.miembro(c, comb)][2035]) for c in esc if D.miembro(c, comb)]
        if sube:
            modelo03 += " %s, %s%s." % (_mayus(_con(comb)), _con_verbo([("el %s" % c, "%s kt" % _m(v)) for c, v in sube], "llega", "a"),
                                        ", por encima del incondicional" if all(v > em[inc][2035] for _, v in sube) else "")
    leer03 = "Cada línea es un escenario y la etiqueta final da su valor de 2035."
    if vista_riesgos or sens_txt:
        leer03 += " Los botones agregan %s%s." % (
            ("los riesgos sobre %s" % G._o(vista_riesgos)) if vista_riesgos else "",
            ((" y " if vista_riesgos else "") + "el riesgo de operación (%s)" % sens_txt) if sens_txt else "")
    leer03 += " El deslizador inferior acota los años."
    leer03 += _leer_stoele([D.miembro(c, d) for d in D.riesgos for c in esc])
    L["g03_energia_escenarios"] = _g(
        muestra="Emisiones totales del sector energía en kt CO₂e: demanda final, generación eléctrica, fugitivas y "
                "refinación, según el Output.csv de cada escenario.",
        leer=leer03,
        modelo=modelo03,
        decision=_caidas(D, nombres_mayores, p_mayores))

    capas = D.capas
    serie = {c: {a: em[D.base[c]][a] - em[c][a] for a in anios} for c in capas}
    orden = D.T.get("orden") or esc
    if capas:
        u = capas[-1]
        cu = serie[u]
        pico = max(cu, key=cu.get)
        b_u = D.base[u]
        dpico, dfin = desp.get(b_u, cero)[C.IDX[pico]], desp.get(b_u, cero)[C.IDX[2035]]
        quien = "del condicional" if b_u == con else "del %s" % b_u
        if cu[pico] > 0 and pico == 2035:
            modelo04 = "La capa %s crece hasta 2035, cuando aporta %s kt." % (u, _m(cu[2035]))
        elif cu[pico] > 0:
            modelo04 = "La capa %s alcanza su máximo en %d, con %s kt, y en 2035 %s." % (
                u, pico, _m(cu[pico]), ("aporta %s kt" % _m(cu[2035])) if cu[2035] >= 0 else
                ("emite %s kt más que %s" % (_m(-cu[2035]), D.sobre(u))))
        else:
            modelo04 = "La capa %s no reduce emisiones en 2026-2035: en 2035 emite %s kt más que %s." % (
                u, _m(-cu[2035]), D.sobre(u))
        otras = [c for c in capas if c != u]
        if otras:
            modelo04 += " %s." % _mayus(_y(["la capa %s suma %s kt en la ventana 2031-2035" % (
                c, _m(adic(c) if D.base[c] == con else sum(serie[c][a] for a in V))) for c in otras]))
        ceros = [c for c in capas if abs(serie[c][2035]) < 0.5]
        if ceros:
            modelo04 += (" En 2035 %s %s cero: %s solo tiene %s GWh de generación térmica por encima de los pisos de "
                         "despacho del Modelo CLG, y la renovable adicional no tiene térmica que sustituir." % (
                             "las capas " + _y(ceros) if len(ceros) > 1 else "la capa " + ceros[0],
                             "valen" if len(ceros) > 1 else "vale", con, _m(desp.get(con, cero)[C.IDX[2035]], 1)))
        cae = bool(entrada) and pico < entrada <= 2035 and dfin < dpico
        decision04 = ("%s rinde mientras haya térmica que desplazar. La térmica desplazable %s, la generación térmica "
                      "por encima de su piso de despacho obligatorio, pasa de %s GWh en %d a %s GWh en 2035%s; en ese "
                      "tramo la reducción de la capa %s pasa de %s a %s kt." % (
                          "El paquete fuera de la NDC" if D.capa(u)["fuera_ndc"] else "La capa del %s" % u, quien,
                          _m(dpico), pico, _m(dfin),
                          (", con la entrada en operación de %s en %d" % (nombres_mayores, entrada)) if cae else "",
                          u, _m(cu[pico]), _m(cu[2035])))
        if pico == 2035:
            decision04 = ("%s crece hasta 2035, cuando aporta %s kt; ese año la térmica desplazable %s es de %s GWh."
                          % ("El paquete fuera de la NDC" if D.capa(u)["fuera_ndc"] else "La capa del %s" % u,
                             _m(cu[2035]), quien, _m(dfin)))
    else:
        modelo04 = "La corrida no trae escenarios de Artículo 6 junto con su base: no hay capas que medir."
        decision04 = ""
    L["g20_escalera"] = _g(
        muestra="Reducción acumulada del sector energía frente a la NDC condicional en la ventana de "
                "transacciones %d-%d (kt CO₂e), escalón por escalón: %s." % (
                    C.VENTANA[0], C.VENTANA[-1], _y(["el %s" % c for c in capas]) or "sin escalones en la corrida"),
        leer="Cada barra apila las capas de los escalones que contiene, con el color de cada capa. La cifra en negrita "
             "es la reducción total del escalón frente al condicional y la línea inferior, lo que añade su última capa. "
             "La línea discontinua marca el nivel del escalón anterior.",
        modelo="%s." % _y(["el %s suma %s kt" % (c, _m(sum(em[con][a] - em[c][a] for a in C.VENTANA)))
                            for c in capas]) if capas else "",
        decision="Cada capa tiene su propia consecuencia contable: la del A pertenece al tramo condicional y "
                 "descuenta de esa meta si se transfiere; las del B y del C están fuera de la NDC y no consumen "
                 "ninguna meta si demuestran su adicionalidad.")

    L["g04_reduccion_anual"] = _g(
        muestra="Reducción anual de emisiones del sector energía (kt CO₂e) de cada capa: %s." % (
            _y(["el %s frente %s" % (c, _al(D, c)) for c in capas]) or "sin capas en la corrida"),
        leer=("%s Una barra bajo cero indica que la capa emite más que su referencia ese año." % " ".join(
            "Barras %s: capa %s." % (COLOR_TXT[orden.index(c) % len(COLOR_TXT)] if c in orden else "grises", c)
            for c in capas)) + (" La línea punteada es el aporte atribuible por retiro: emisiones del "
                                "contrafactual, el escenario sin sus actividades, menos las del escenario."
                                if getattr(D, "contra", None) else ""),
        modelo=modelo04,
        decision=decision04)

    # primer anio en que se separan las emisiones de la generacion de los escenarios de la vista inicial
    vista = [c for c in [inc, con] + esc if c in em]
    gsub = D.sub[(D.sub.subsector == pp) & D.sub.escenario.isin(vista)]
    gsub = gsub.pivot_table(index="anio", columns="escenario", values="kt", aggfunc="sum")
    distintos = [a for a in gsub.index if gsub.loc[a].max() - gsub.loc[a].min() > 0.5]
    separa = distintos[0] if distintos else None
    if separa is None:
        leer05 = "Las %s líneas de la vista inicial coinciden en todo el periodo." % _cuantos(len(vista))
    elif separa > C.ANIOS[0]:
        leer05 = ("Hasta %d las %s líneas de la vista inicial coinciden; desde %d cada una refleja cuánta "
                  "electricidad térmica necesita el escenario." % (separa - 1, _cuantos(len(vista)), separa))
    else:
        leer05 = ("Las líneas de la vista inicial difieren desde %d, según cuánta electricidad térmica necesita cada "
                  "escenario." % separa)
    if vista_riesgos:
        leer05 += " Los botones muestran los riesgos sobre %s." % G._o(vista_riesgos)
    leer05 += _leer_stoele([D.miembro(c, d) for d in D.riesgos for c in esc])
    modelo05 = ("Sin el tramo condicional, las emisiones de la generación llegan a %s kt en 2035. El condicional las "
                "baja a %s kt." % (_m(sub35(inc, pp)), _m(sub35(con, pp))))
    if esc:
        modelo05 += " %s." % _mayus(_con_verbo([("el %s" % c, "%s kt" % _m(sub35(c, pp))) for c in esc], "queda", "en"))
    decision05 = ""
    if capas:
        u = capas[-1]
        b_u = D.base[u]
        dif = sub35(u, pp) - sub35(b_u, pp)
        egf = R["emisiones_generacion_familia_kt"]
        dfam = {f: egf.get(u, {}).get(f, cero)[C.IDX[2035]] - egf.get(b_u, {}).get(f, cero)[C.IDX[2035]]
                for f in set(egf.get(u, {})) | set(egf.get(b_u, {}))}
        if dif >= 0.5:
            suben = [_minus(f) for f, v in sorted(dfam.items(), key=lambda kv: -kv[1]) if v >= 0.5]
            modelo05 += " En 2035 la generación del %s emite %s kt más que la del %s%s." % (
                u, _m(dif), b_u, (", por la generación con %s" % _y(suben)) if suben else "")
        elif dif <= -0.5:
            modelo05 += " En 2035 la generación del %s emite %s kt menos que la del %s." % (u, _m(-dif), b_u)
        else:
            modelo05 += " En 2035 la generación del %s y la del %s emiten lo mismo." % (u, b_u)
        modelo05 += " La térmica desplazable %s en 2035 es de %s GWh." % (
            "del condicional" if b_u == con else "del %s" % b_u, _m(desp.get(b_u, cero)[C.IDX[2035]]))
        cu = serie[u]
        pico = max(cu, key=cu.get)
        fuertes = [a for a in anios if cu[pico] > 0 and cu[a] >= 0.4 * cu[pico]]
        pb = [x for x in R.get("portafolio_B_bajo_riesgo", []) if x.get("escenario") == u]
        intacta = next((x["total_2031_2035"] for x in pb if x["estado"] == "intacto"), None)
        crece = intacta is not None and any(x["total_2031_2035"] > intacta + 0.5 for x in pb if x["estado"] != "intacto")
        if fuertes:
            decision05 = ("El valor de la capa %s se concentra en %s%s; en 2035, con el sistema intacto, su efecto sobre "
                          "las emisiones del sector es de %s kt." % (
                              u, ("%d-%d" % (fuertes[0], fuertes[-1])) if len(fuertes) > 1 else str(fuertes[0]),
                              " y crece en los años de estrés hidroeléctrico" if crece else "", _m(cu[2035])))
        else:
            decision05 = "La capa %s no reduce las emisiones del sector en 2026-2035." % u
    if comb and m_comb:
        modelo05 += " %s, la generación del %s emite %s kt en 2035." % (_mayus(_con(comb)), top, _m(sub35(m_comb, pp)))
    L["g05_emisiones_generacion"] = _g(
        muestra="Emisiones de las centrales eléctricas (componente CO2e_PP del Output.csv de cada escenario, kt CO₂e).%s" % (
            (" Es el único subsector sobre el que actúan las palancas de %s." % _y(esc))
            if esc and G._solo_generacion(D) else ""),
        leer=leer05,
        modelo=modelo05,
        decision=decision05)

    s35 = D.sub[(D.sub.escenario == con) & (D.sub.anio == 2035)].groupby("subsector")["kt"].sum().sort_values(ascending=False)
    tot35 = float(em[con][2035])
    mayores_sub = [(s, float(v)) for s, v in s35.items()][:3]
    L["g06_subsectores"] = _g(
        muestra="Emisiones del sector energía por subsector del inventario (kt CO₂e, áreas apiladas), calculadas "
                "con las emisiones por tecnología del Output.csv de cada escenario.",
        leer="Cada franja es un subsector y la altura total es la emisión del sector. Los botones cambian de "
             "escenario.",
        modelo="En 2035, en el condicional, %s." % _y(["%s emite %s kt (%s del sector)" % (
            SUBSECTOR.get(s, s.lower()), _m(v), _pct(100.0 * v / tot35 if tot35 else 0.0)) for s, v in mayores_sub]),
        decision=_alcance_subsectores(D, fuera_modelo))

    hid = 100.0 * gen[con]["Hidroeléctrica"] / gtot(con) if gtot(con) else 0.0
    L["g07_generacion"] = _g(
        muestra="Generación eléctrica por tipo de planta (GWh, áreas apiladas), desde ProductionByTechnology del "
                "Output.csv de cada escenario.",
        leer="Botones de la izquierda: escenario. Botones de la derecha: valor absoluto o participación en el "
             "total.",
        modelo="En 2035 la hidroelectricidad produce el %s de la generación del condicional y el fuel oil y el "
               "diésel, el %s.%s" % (
                   _pct(hid), _pct(100.0 * gen[con]["Fuel oil y diésel"] / gtot(con) if gtot(con) else 0.0),
                   (" La solar y la eólica suman %s GWh en el %s, frente a %s GWh en el condicional." % (
                       _m(gen[top]["Solar"] + gen[top]["Eólica"]), top, _m(gen[con]["Solar"] + gen[con]["Eólica"])))
                   if top else ""),
        decision=("La matriz depende de la hidroelectricidad; de ahí el peso de los riesgos hidrológicos en el resultado."
                  if hid >= 50 else
                  "La hidroelectricidad aporta menos de la mitad de la generación del condicional en 2035."))

    donde = lambda c: "el condicional" if c == con else "el %s" % c
    L["g08_capacidad"] = _g(
        muestra="Capacidad instalada por tipo de planta (MW), desde TotalCapacityAnnual del Output.csv de cada escenario.",
        leer="Botones de la izquierda: escenario. Botones de la derecha: valor absoluto o participación.",
        modelo="En 2035 la capacidad solar llega a %s; la eólica, a %s." % (
            _y(["%s MW en %s" % (_m(mw(c, "Solar")), donde(c)) for c in [con] + esc]),
            _y(["%s MW en %s" % (_m(mw(c, "Eólica")), donde(c)) for c in [con] + esc])),
        decision=_techo_eolico(D, gen, mw))

    er = D.ernc
    L["g09_ernc"] = _g(
        muestra="Participación de la ERNC (solar, eólica, biomasa y geotermia) en la generación eléctrica, en %. "
                "La hidroelectricidad no se cuenta como ERNC.",
        leer="Cada línea es un escenario; el cursor muestra el valor de cada año.",
        modelo="En 2035 la ERNC llega al %s en el condicional%s." % (
            _pct(er[con][2035]), ("; %s" % _y(["al %s en el %s" % (_pct(er[c][2035]), c) for c in esc])) if esc else ""),
        decision=("Aun con %s, la ERNC no supera el %s de la generación en 2035." % (
            _y(["el %s" % c for c in esc]), _pct(max(er[c][2035] for c in esc)))) if esc else "")

    cc = R.get("conciliacion_condicional_2035", {})
    hd = {h["parametro"]: h["valor"] for h in K.hoja("Headroom")}
    p_inc, p_con = G._pct_meta(D)
    publicadas = R.get("reglas_headroom", {}).get("regla_nacional") == "meta_condicional"
    nac = D.nac
    exceso = cc.get("exceso_modelado", 0.0)
    L["g10_nacional"] = _g(
        et_modelo="Qué dicen las series de la NDC",
        muestra="Emisiones nacionales de los cinco sectores del inventario (kt CO₂e) en las tres trayectorias "
                "modeladas de la agregación nacional del Modelo CLG para la Segunda NDC y las sendas de sus metas "
                "publicadas. Fuente: %s y Segunda NDC, sec. 4.2.4; el modelo de energía cubre solo uno de los cinco "
                "sectores." % hd.get("archivo_nacional", "agregación nacional del Modelo CLG"),
        leer="Punteada gris oscuro: tendencial. Discontinua gris: incondicional modelado. Azul: condicional "
             "modelado. Rojas: metas publicadas, incondicional (%s) y condicional (%s más %s adicional, ambos "
             "sobre el tendencial). La NDC fija una sola meta, en %s; la senda lineal que parte de reducción "
             "cero en %s es un supuesto de cálculo para medir el margen de cada año." % (
                 p_inc, p_inc, p_con, hd.get("anio_meta", 2035), hd.get("anio_inicio_senda", "s. f.")),
        modelo="La NDC compromete en %s una reducción incondicional de %s kt (%s) y %s kt adicionales en el "
               "condicional (%s), ambas sobre un tendencial de %s kt. El condicional modelado reduce %s kt, %s kt "
               "%s de lo comprometido." % (
                   hd.get("anio_meta", 2035), _m(cc.get("reduccion_incondicional_publicada", 0.0)), p_inc,
                   _m(cc.get("reduccion_condicional_publicada", 0.0)), p_con, _m(cc.get("tendencial", 0.0)),
                   _m(cc.get("reduccion_modelada", 0.0)), _m(abs(exceso)), "más" if exceso >= 0 else "menos"),
        decision=("El margen se mide con las metas publicadas: entre ellas quedan %s kt en 2035 y la reducción "
                  "modelada que la NDC no compromete no se cuenta. El tendencial es retroactivo: excluye obras de la "
                  "primera NDC que ya operan." % _m(nac["meta_inc"][2035] - nac["meta_con"][2035])) if publicadas else
                 "El margen se mide con la serie modelada del condicional.")

    peso = D.peso[D.peso.anio == 2035].set_index("trayectoria")["peso_energia_pct"]
    L["g11_peso_energia"] = _g(
        et_modelo="Qué dicen las series de la NDC",
        muestra="Emisiones nacionales de cada trayectoria de la Segunda NDC en 2020, 2025, 2030 y 2035 (kt CO₂e), "
                "separadas en sector energía y otros cuatro sectores. Fuente: agregación nacional y salida del sector "
                "energía del Modelo CLG (PowerBI de ECU_NDC: escenarios BAU1NDC, NDCINC y NDCCON).",
        leer="La parte azul es el sector energía y su etiqueta da el peso en el total nacional; la gris, los otros "
             "cuatro sectores.",
        modelo="En 2035 la energía representa el %s del tendencial y el %s del condicional." % (
            _pct(peso["Tendencial"]), _pct(peso["Condicional"])),
        decision="La energía pesa el %s del balance nacional del condicional en 2035, y el análisis traslada a la "
                 "trayectoria nacional cada tonelada que el sector sube o baja: un riesgo hidroeléctrico pesa sobre la "
                 "meta del país en la misma cuantía." % _pct(peso["Condicional"]))

    cas = R["cascada_headroom_2035"]
    base_cas = R["cascada_headroom_2035_base"]
    pasos = G._camino_riesgo(D)
    hT = D.hr35(top) if top else float("nan")
    tramos, previo = [], hT
    for rot, cod in pasos:
        h = D.hr35(cod)
        tramos.append((rot, h - previo))
        previo = h
    if pasos:
        partes = []
        frases = {_minus(G._rot(d)): d.get("frase") for d in D.riesgos}
        for i, (rot, dv) in enumerate(tramos):
            nombre = _minus(re.sub(r"\s+además$", "", re.sub(r",\s*sobre [^,]*$", "", rot)))
            nombre = frases.get(nombre) or nombre
            if i == 0:
                partes.append("%s %s %s kt al margen del %s" % (nombre, "resta" if dv < 0 else "suma", _m(abs(dv)), top))
            elif (dv < 0) == (tramos[0][1] < 0):
                partes.append("%s, %s kt más" % (nombre, _m(abs(dv))))
            else:
                partes.append("%s %s %s kt" % (nombre, "resta" if dv < 0 else "suma", _m(abs(dv))))
        texto_pasos = "; " + "; ".join(partes)
        if previo < 0:
            cierre = "%s, el %s quedaría %s kt por encima de la meta incondicional aun sin transferir." % (
                _mayus(_con(comb)), top, _m(-previo))
        elif hT > 0 and previo < 0.1 * hT:
            cierre = ("%s, el margen del %s en 2035 queda en %s kt, el %s del margen intacto: casi nada que transferir "
                      "sin tocar la meta incondicional." % (_mayus(_con(comb)), top, _m(previo),
                                                            _pct(100.0 * previo / hT, 0)))
        else:
            cierre = "%s, el margen del %s en 2035 queda en %s kt." % (_mayus(_con(comb)), top, _m(previo))
    else:
        texto_pasos, cierre = "", ""
    capas_txt = ("Las capas %s le %s %s kt" % (_y(capas), "suman" if hT - base_cas >= 0 else "restan",
                                               _m(abs(hT - base_cas)))) if capas and top else ""
    if publicadas:
        L["g12_cascada_headroom"] = _g(
            et_modelo="Qué dice el análisis",
            muestra="Descomposición del margen nacional de 2035 frente a la meta incondicional (kt CO₂e): de la "
                    "reducción del condicional modelado al margen que la NDC compromete%s. Combina la agregación nacional "
                    "del Modelo CLG y las metas publicadas de la NDC con los resultados del modelo." % (
                        (", y de ahí al margen del %s %s" % (top, _con(comb))) if pasos else ""),
            leer="Barras azules: totales. Verdes: componentes que agregan margen. Rojas: componentes que lo restan. Se "
                 "lee de izquierda a derecha.",
            modelo="El condicional modelado reduce %s kt en 2035. Descontadas la meta incondicional (%s kt) y la "
                   "reducción que la NDC no compromete (%s kt), el margen del condicional es de %s kt, el %s "
                   "adicional.%s" % (
                       _m(cas[0]["kt"]), _m(-cas[1]["kt"]), _m(-cas[2]["kt"]), _m(base_cas), p_con,
                       (" %s%s." % (capas_txt, texto_pasos)) if capas_txt else ""),
            decision=cierre)
    else:
        L["g12_cascada_headroom"] = _g(
            et_modelo="Qué dice el análisis",
            muestra="Descomposición del margen nacional de 2035 frente a la meta incondicional (kt CO₂e) con la "
                    "serie condicional modelada.",
            leer="Barras azules: totales. Verdes: componentes que agregan margen. Rojas: componentes que lo restan.",
            modelo="De los %s kt de margen del condicional modelado en 2035, %s kt provienen del tendencial "
                   "retroactivo del sector energía.%s" % (_m(base_cas), _m(cas[0]["kt"]),
                                                          (" %s%s." % (capas_txt, texto_pasos)) if capas_txt else ""),
            decision=cierre)

    sob = {(s["sufijo"], s["regla"]): s for s in R["potencial_art6"]["sobreventa"]}
    aut = R["potencial_art6"].get("autorizado_intacto_2031_2035",
                                  round(sum(R["potencial_art6"]["autorizado_intacto"].values()), 1))
    if top and comb:
        s_pru, s_con = sob.get((suf_c, "prudente"), {}), sob.get((suf_c, "condicional"), {})
        modelo13 = ("Con el sistema intacto se autorizan %s kt en 2031-2035 (%s). %s, en la regla prudente, la "
                    "sobreventa es de %s kt y el exceso propio, de %s kt; con los otros sectores en su condicional "
                    "comprometido, la sobreventa es de %s kt." % (
                        _m(aut), R["potencial_art6"].get("regla_de_autorizacion") or "regla del análisis",
                        _mayus(_con(comb)), _m(s_pru.get("sobreventa_2031_2035", 0.0)),
                        _m(s_pru.get("incumplimiento_sin_transferir_2031_2035", 0.0)),
                        _m(s_con.get("sobreventa_2031_2035", 0.0))))
    elif top:
        modelo13 = "Con el sistema intacto se autorizan %s kt en 2031-2035; la corrida no trae riesgos." % _m(aut)
    else:
        modelo13 = "La corrida no trae escenarios de Artículo 6: no hay autorización que evaluar."
    L["g13_sobreventa_area"] = _g(
        muestra="Emisiones nacionales 2026-2035 (kt CO₂e) frente a la meta incondicional cuando el país autoriza "
                "ITMO con el sistema intacto y después ocurre un riesgo.",
        leer=("Línea roja: meta incondicional. Punteada: emisiones nacionales del %s en el estado elegido. Línea "
              "negra: esas emisiones más los ITMO ya autorizados, que con ajuste correspondiente se suman al "
              "balance del país. Rojo claro: sobreventa, lo transferido que ya no cabe en el margen. Rojo oscuro: "
              "exceso sobre la meta aun sin transferir. Verde: margen disponible. El menú elige riesgo y regla."
              % (top or "escenario")) + _leer_stoele([D.miembro(top, d) for d in D.riesgos] if top else []),
        modelo=modelo13,
        decision="Autorizar con el sistema intacto expone al país a transferir reducciones que después necesita. "
                 "Una autorización prudente se limita a resultados verificados ex post, de líneas con adicionalidad "
                 "firme, y conserva una reserva sin autorizar.")

    if a0 and comb_a0:
        mA = D.miembro(a0, comb_a0)
        h_c, h_p = D.hr35(mA), D.hr35(mA, "prudente")
        modelo14 = ("Con los otros sectores en su condicional comprometido, el margen del %s pasa de %s kt intacto a "
                    "%s kt %s; en la regla prudente, a %s kt." % (a0, _m(D.hr35(a0)), _m(h_c), _con(comb_a0), _m(h_p)))
        if h_c < 0 and h_p < 0:
            decision14 = ("%s, el %s queda por encima de su meta incondicional con las dos reglas: ninguna transferencia "
                          "sería compatible con ella." % (_mayus(_con(comb_a0)), a0))
        elif h_p < 0:
            decision14 = ("En la regla prudente, %s deja al país por encima de su meta incondicional: ninguna "
                          "transferencia sería compatible con ella." % _minus(comb_a0["nombre"]))
        elif h_c < 0:
            decision14 = ("Con los otros sectores en su condicional comprometido, %s deja al país por encima de su meta "
                          "incondicional." % _minus(comb_a0["nombre"]))
        else:
            decision14 = ("%s, el %s conserva margen frente a la meta incondicional con las dos reglas: %s y %s kt."
                          % (_mayus(_con(comb_a0)), a0, _m(h_c), _m(h_p)))
    elif a0:
        modelo14 = "El margen de 2035 del %s es de %s kt; la corrida no trae riesgos." % (a0, _m(D.hr35(a0)))
        decision14 = ""
    else:
        modelo14, decision14 = "La corrida no trae escenarios de Artículo 6.", ""
    L["g14_headroom_riesgos"] = _g(
        muestra="Margen nacional de 2035 (kt CO₂e) de %s, con el sistema intacto y bajo cada riesgo." % (
            _y(esc) or "la corrida"),
        leer="Una barra sobre cero es margen frente a la meta incondicional; bajo cero, el país excede su meta aun "
             "sin transferir. Los botones cambian la regla para los otros cuatro sectores.",
        modelo=modelo14,
        decision=decision14)

    if top:
        modelo15 = "En 2035 el margen del %s es de %s kt intacto%s, con los otros sectores en su condicional comprometido." % (
            top, _m(hT), ("; %s" % _y(["%s kt %s" % (_m(D.hr35(D.miembro(top, d))), _con(d))
                                      for d in riesgos_top])) if riesgos_top else "")
        if hT > 0 and riesgos_top:
            pcts = [_pct(100.0 * (hT - D.hr35(D.miembro(top, d))) / hT, 0) for d in riesgos_top]
            fr = lambda d: d.get("frase") or _minus(d["nombre"])
            partes = (["%s se lleva el %s" % (fr(riesgos_top[0]), pcts[0])]
                      + ["%s, el %s" % (fr(d), p) for d, p in zip(riesgos_top[1:], pcts[1:])])
            union = partes[0] if len(partes) == 1 else (
                " y ".join(partes) if len(partes) == 2 else "; ".join(partes[:-1]) + " y " + partes[-1])
            decision15 = "Del margen del %s en 2035, %s." % (top, union)
        elif hT <= 0:
            decision15 = "El %s no tiene margen frente a la meta incondicional en 2035 aun con el sistema intacto." % top
        else:
            decision15 = ""
    else:
        modelo15 = "En 2035 el margen del condicional es de %s kt." % _m(D.hr35(con))
        decision15 = ""
    st15 = _leer_stoele([D.miembro(c, d) for d in D.riesgos for c in esc])
    L["g15_headroom_trayectoria"] = _g(
        muestra="Margen nacional año por año, 2026-2035 (kt CO₂e), del condicional%s." % (
            (", %s y sus riesgos" % _y(esc)) if esc else ""),
        leer="Sobre la línea roja hay margen; debajo, incumplimiento. Los botones cambian la regla para los otros "
             "sectores.%s" % ((" En los años subestimados el margen queda sobrestimado." + st15) if st15 else ""),
        modelo=modelo15,
        decision=decision15)

    if esc:
        a_ad, a_tc = vol(a0, "adicional_a_la_NDC"), vol(a0, "con_tramo_condicional")
        br = _bajo_riesgo(D, vol)
        modelo16 = "Adicional a la NDC, con el sistema intacto: %s.%s Con tramo condicional, intacto: %s." % (
            _y(["%s %s kt" % (c, _m(vol(c, "adicional_a_la_NDC"))) for c in esc]),
            (" %s" % _mayus(br)) if br else "",
            _y(["%s %s kt" % (c, _m(vol(c, "con_tramo_condicional"))) for c in esc]))
        decision16 = (("La regla de contabilidad multiplica por %s el volumen del %s." % (_m(a_tc / a_ad, 0), a0))
                      if a_ad >= 0.5 else "Sin tramo condicional, el %s no tiene volumen adicional a la NDC." % a0)
    else:
        modelo16, decision16 = "La corrida no trae escenarios de Artículo 6.", ""
    L["g16_volumenes"] = _g(
        muestra="Reducción acumulada 2031-2035 (kt CO₂e) de %s, con el sistema intacto y bajo cada riesgo, según "
                "dos reglas de contabilidad." % (_y(esc) or "los escenarios de Artículo 6"),
        leer="Adicional a la NDC: reducción frente al condicional; transferirla no toca ninguna meta. Con tramo "
             "condicional: reducción frente al incondicional; transferirla obliga a renunciar a la meta condicional "
             "en la misma cuantía. Los botones cambian de regla.",
        modelo=modelo16,
        decision=decision16)

    of = pd.DataFrame(R["ingresos"]["oferta"])
    of = of[~of.clave.isin(["maximo", "en_reserva"])] if not of.empty else of
    precios = {p["escenario_precio"]: p for p in K.hoja("Precios")}
    P = R["ingresos"]["precios"]
    central = float(P.get("Central", sorted(P.values())[len(P) // 2])) if P else float("nan")
    alto = max(precios.values(), key=lambda p: float(p["usd_por_t"])) if precios else None

    def ofv(clave):
        if of.empty:
            return None
        x = of[of.clave == clave]["kt_2031_2035"]
        return float(x.iloc[0]) if len(x) else None
    firme_of = ofv("firme")
    top_of = ofv("capa:%s" % top) if top else None
    if not of.empty:
        mayor = of.loc[of.kt_2031_2035.idxmax()]
        partes17 = ["La oferta mayor es «%s», con %s kt" % (mayor.oferta, _m(mayor.kt_2031_2035))]
        if firme_of is not None:
            partes17.append("la firme, «%s», suma %s kt y es el ingreso que hoy sostendría una negociación" % (
                of[of.clave == "firme"].oferta.iloc[0], _m(firme_of)))
        decision17 = "; ".join(partes17) + "."
    else:
        decision17 = "La corrida y la configuración no dan ninguna oferta que valorar."
    if alto:
        decision17 += " Referencia del precio alto (%s US$/t): %s." % (
            _m(float(alto["usd_por_t"])), str(alto["referencia"])[:1].lower() + str(alto["referencia"])[1:])
    decision17 += " Los precios de mercado cambian rápido y deben actualizarse antes de cualquier decisión%s." % (
        (" (fecha del dato en la configuración: %s)" % alto["fecha_dato"]) if alto and alto.get("fecha_dato") else "")
    rinde = _y([("la oferta firme rinde %s millones de US$" % _m(firme_of * central / 1000.0, 1))
                if firme_of is not None else "",
                ("la capa del %s, %s millones" % (top, _m(top_of * central / 1000.0, 1))) if top_of is not None else ""])
    L["g17_ingresos"] = _g(
        muestra="Ingresos potenciales 2031-2035 (millones de US$) de cada oferta hipotética: volumen × precio. Es "
                "un cálculo externo al modelo sobre sus volúmenes; las líneas con potencial declarado usan ese valor.",
        leer="Cada barra es una oferta; el deslizador cambia el precio por tonelada. Los precios de referencia vienen "
             "de la hoja Art6_Precios: %s US$/t." % _y(["%s %s" % (k.lower(), _m(float(p["usd_por_t"])))
                                                       for k, p in precios.items()]),
        modelo=("A %s US$/t, %s." % (_m(central), rinde)) if rinde else "",
        decision=decision17)
    M = D.R.get("metas_2035", {})
    inv_nac = {int(k): v for k, v in ((D.R.get("inventario") or {}).get("nacional_con_utcuts") or {}).items()}
    ult = max(inv_nac) if inv_nac else None
    a35 = C.VENTANA[-1]
    senda = D.nac["meta_inc"].dropna()
    a_senda = int(senda.index[0]) if len(senda) else a35
    L["g18_referencias"] = _g(
        muestra="Las referencias de la contabilidad del Artículo 6 en el ámbito nacional con USCUSS: el tendencial de "
                "la NDC (%s kt en %d), los niveles de las dos metas (%s y %s kt en %d, con senda lineal desde %d)%s."
                % (_m(M.get("base", 0)), a35, _m(M.get("meta_inc", 0)), _m(M.get("meta_con", 0)), a35, a_senda,
                   " y el inventario observado hasta %d" % ult if ult else ""),
        leer="La meta incondicional, la línea roja continua, es la base reservada: el balance de emisiones de %d, "
             "inventario más ajustes correspondientes, no puede superarla. La condicional, punteada, es la oferta "
             "sujeta a apoyo, y el espacio entre ambas es el margen del condicional. Cada meta es un nivel de %d; la "
             "senda que la une con %d es un supuesto de cálculo para los años intermedios. El inventario, en negro, es "
             "el dato con el que se verifica el cumplimiento; el modelo cubre los años que aún no tienen inventario."
             % (a35, a35, a_senda),
        modelo="El tendencial proviene de la agregación nacional del Modelo CLG para los cinco sectores; los niveles de las metas son el "
               "tendencial menos %s y %s kt, con senda lineal desde %d, supuesto de cálculo.%s"
               % (_m(M.get("base", 0) - M.get("meta_inc", 0)), _m(M.get("base", 0) - M.get("meta_con", 0)), a_senda,
                  (" En %d el inventario registra %s kt frente a %s kt de la agregación nacional del Modelo CLG para ese año: las "
                   "dos series parten de bases distintas y requieren conciliación." % (ult, _m(inv_nac[ult]), _m(float(D.nac["incondicional"].get(ult, float("nan")))))
                  if ult and ult in D.nac.index else "")),
        decision="Toda cifra de margen y de sobreventa se mide contra el nivel incondicional. La base del margen "
                 "(modelada, publicada o prorrata) y el método de ajuste correspondiente son decisiones abiertas.")
    L["g19_comparacion"] = _g(
        muestra="Los escenarios lado a lado en cuatro paneles: emisiones del sector energía en %d, reducción acumulada "
                "%s frente al condicional (y el aporte atribuible por retiro cuando la corrida trae el contrafactual), "
                "margen nacional de %d con las dos reglas para los sectores que el modelo no cubre y participación de "
                "la ERNC." % (a35, "%d-%d" % (C.MARCO[0], C.MARCO[-1]), a35),
        leer="Cada barra lleva el color de su escenario y la cifra al final. En el panel del margen, la barra clara "
             "aplica la regla prudente; un margen negativo significa que el escenario incumple la meta incondicional.",
        modelo=("En %d %s. %s reduce %s kt acumulados en 2026-2035 frente al condicional%s; su margen de %d es de %s kt con la regla "
                "base y %s kt con la regla prudente."
                % (a35, _y(["%s emite %s kt" % (D.nombre(c), _m(em[c][a35])) for c in esc]) if esc else "no hay escenarios",
                   D.nombre(esc[-1]) if esc else "", _m(sum(em[con][a] - em[esc[-1]][a] for a in C.MARCO)) if esc else "",
                   (" y %s %s kt" % (D.nombre(esc[0]), _m(sum(em[con][a] - em[esc[0]][a] for a in C.MARCO)))) if len(esc) > 1 else "",
                   a35, _m(D.hr35(esc[-1])) if esc else "", _m(D.hr35(esc[-1], "prudente")) if esc else "")),
        decision="La comparación separa lo que el país controla (la capa de cada escenario) de lo que depende de los "
                 "demás sectores (la regla del margen): la decisión de autorizar transferencias se toma sobre el margen "
                 "prudente y la adicionalidad que admita el comprador.")
    return L


def _caidas(D, nombres_mayores, p_mayores):
    """Compara en 2035 el tramo condicional, las capas y lo que suma la prueba combinada."""
    em, a = D.em, 2035
    tramo = em[D.inc][a] - em[D.con][a]
    capas = [(c, em[D.base[c]][a] - em[c][a]) for c in D.capas]
    txt = "En 2035 el tramo condicional baja %s kt%s." % (
        _m(tramo), ("; %s" % _y(["la capa %s, %s kt" % (c, _m(v)) for c, v in capas])) if capas else "")
    a0 = D.esc[0] if D.esc else None
    comb = D.combinado(a0) if a0 else None
    if comb is not None:
        dv = em[D.miembro(a0, comb)][a] - em[a0][a]
        txt += " %s, las emisiones del %s %s %s kt." % (_mayus(_con(comb)), a0, "suben" if dv >= 0 else "bajan",
                                                         _m(abs(dv)))
    if capas and tramo > max(v for _, v in capas) and nombres_mayores:
        txt += (" La mayor caída la produce el tramo condicional, con %s, que reúnen el %s de la reducción anual "
                "declarada de las condicionales." % (nombres_mayores, _pct(p_mayores, 0)))
    return txt


def _alcance_subsectores(D, fuera):
    s, V = D.sub, C.MARCO
    txt = ""
    if D.top:
        dif = (s[(s.escenario == D.con) & s.anio.isin(V)].groupby("subsector")["kt"].sum()
               - s[(s.escenario == D.top) & s.anio.isin(V)].groupby("subsector")["kt"].sum())
        if dif.sum() > 0.5:
            txt = "El %s de lo que reduce el %s frente al condicional en 2026-2035 ocurre en la generación eléctrica." % (
                _pct(100.0 * dif.get("Generación eléctrica", 0.0) / dif.sum(), 0), D.top)
        else:
            txt = "El %s no reduce las emisiones del sector frente al condicional en 2026-2035." % D.top
    s35 = s[(s.escenario == D.con) & (s.anio == 2035)].groupby("subsector")["kt"].sum().sort_values(ascending=False)
    if len(s35) and s35.index[0] != "Generación eléctrica" and D.esc and G._solo_generacion(D):
        txt += " El mayor emisor del sector en 2035 es %s, fuera del alcance de las palancas de %s." % (
            SUBSECTOR.get(s35.index[0], s35.index[0].lower()), _y(D.esc))
    if fuera:
        txt += " Las %s iniciativas de la NDC que el modelo no representa se cuentan con su volumen declarado." % (
            _cuantos(len(fuera)))
    return txt.strip()


def _bajo_riesgo(D, vol):
    """Volumen adicional a la NDC del ultimo escalon bajo cada prueba de estres que trae la corrida."""
    top = D.top
    v = [(d, vol(D.miembro(top, d), "adicional_a_la_NDC")) for d in D.riesgos if D.miembro(top, d)] if top else []
    if not v:
        return ""
    if all(x < 0.5 for _, x in v):
        return ("con cualquiera de los riesgos, el %s queda en cero." % top) if len(v) > 1 else \
            ("con %s, el %s queda en cero." % (_minus(v[0][0]["nombre"]), top))
    vals = [x for _, x in v]
    if round(min(vals)) == round(max(vals)):
        return "bajo riesgo, el %s queda en %s kt." % (top, _m(min(vals)))
    return "bajo riesgo, el %s queda entre %s y %s kt." % (top, _m(min(vals)), _m(max(vals)))


def _techo_eolico(D, gen, mw):
    """Factor de planta eolico del condicional en 2035 y, si su techo de actividad del _Input.csv lo
    limita, si el primer escalon lo levanta."""
    con = D.con
    if mw(con, "Eólica") <= 0:
        return ""
    fp = 100.0 * gen[con]["Eólica"] / (mw(con, "Eólica") * 8.76)
    texto = ("Capacidad instalada y generación son cosas distintas: en el condicional, la eólica instalada genera con "
             "un factor de planta de %s" % _pct(fp))
    I = C.leer_ecuinput([C.TECHO], list(D.R["corrida"]["escenarios"]))
    eol = [t for t in I["Technology"].dropna().unique() if C.familia(t) == "Eólica"]
    techo = lambda e: float(I[(I.Strategy == e) & (I.Technology.isin(eol)) & (I.Year == 2035)][C.TECHO].sum())
    t_con = techo(con)
    if 0 < t_con < 900 and gen[con]["Eólica"] / C.PJ_A_GWH >= 0.98 * t_con:
        texto += " porque su techo de actividad la limita"
        a0 = D.esc[0] if D.esc else None
        if a0 and techo(a0) > t_con * 1.01:
            texto += ", y el %s levanta ese techo" % a0
    return texto + "."


CSS = """
.gl{font-family:'Fira Sans','Segoe UI',Arial,sans-serif;color:#1F2937;background:#FFFFFF;border:1px solid #E3E8E6;
border-radius:8px;padding:14px 18px;margin:6px 0 10px;max-width:1180px;font-size:14px;line-height:1.55;
font-variant-numeric:tabular-nums;box-sizing:border-box;display:grid;grid-template-columns:150px minmax(0,1fr);
gap:8px 18px}
.gl dt{margin:0;font-size:12px;font-weight:600;letter-spacing:.06em;text-transform:uppercase;color:#4B5563;padding-top:2px}
.gl dd{margin:0;max-width:105ch}
.gl dd.gl-dec{color:#0B5E48;font-weight:500}
"""


def html(texto, estilo=True):
    filas = []
    for et, cuerpo in partes(texto):
        clase = " class='gl-dec'" if et == "Para la decisión" else ""
        cuerpo = cuerpo.replace(" %", " %")
        filas.append("<dt>%s</dt><dd%s>%s</dd>" % (H.escape(et), clase, H.escape(cuerpo)))
    return ("<style>%s</style>" % CSS if estilo else "") + "<dl class='gl'>%s</dl>" % "".join(filas)
