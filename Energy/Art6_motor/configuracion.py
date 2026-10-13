# -*- coding: utf-8 -*-
"""Lee la definicion de los escenarios de Articulo 6 en ECU_NDC (rama art6-escenarios).

B1 genera todos los escenarios desde B1_Scenario_Config.xlsx: BAU, BAU1NDC, NDCINC y NDCCON (Modelo Climate Lead
Group) e INCA6, CONA6, INCA6G y CONA6G (base corregida congelada) son escenarios de referencia; A, B, C, sus estados,
las referencias de estado CONA6P y CONA6I y los puentes V7 son escenarios basados en CONA6 (hoja Scenarios), con sus
palancas en las hojas Electrical y Efficiency. Cada fila de palanca empieza su descripcion con el codigo entre
corchetes, por ejemplo [A1]. Las filas las escribe Art6_calibracion/generar_escenarios_art6.py.

Las hojas Art6_* (al final de B1_Scenario_Config.xlsx, el unico libro de configuracion del sandbox) documentan escenarios y palancas (narrativa, iniciativa,
adicionalidad, fuente), fijan los roles (Art6_Roles) y guardan los parametros del analisis. B1 no las lee.
"""
import re
from functools import lru_cache

import openpyxl

import comun as C

FRASES = {"CCOFF": "la salida de la clase de Coca Codo", "CCSOLO": "la salida de Coca Codo sola",
          "ANOSECO": "el año seco severo", "ANOSEC3": "un año seco cada tres", "ANOSECM": "el año seco moderado",
          "CCOFFANOSECO": "la salida de la clase de Coca Codo y el año seco severo",
          "FOI": "la retirada de los pisos térmicos",
          "IMP0": "la importación cero desde Colombia", "SIN": "el retiro de sus proyectos",
          "CCDER": "el derrateo de Coca Codo", "V7": "la definición del 08-10-2026",
          "ACT": "la situación actual anclada a 2026 con choque de demanda transitorio",
          "ACTDEM": "la situación actual anclada a 2026 con demanda persistente",
          "GAS": "la ausencia de la expansión a gas declarada"}

# Rotulo de presentacion de cada estado en el tablero, el cuaderno y la documentacion. No reemplaza el nombre ni la
# etiqueta de Art6_Escenarios, que el analisis escribe en las tablas (capas_por_estado, sobreventa_por_riesgo): solo
# cambia como se muestran. ANOSECO es la cota del riesgo hidrologico y ANOSEC3 su caso central; CCSOLO es el caso
# central del riesgo de la central y CCOFF retira la clase PPHRORAB completa (Coca Codo Sinclair y Sopladora).
ROTULOS = {"ANOSECO": "Año seco severo (cota)", "ANOSEC3": "Un año seco cada tres (caso central)",
           "ANOSECM": "Año seco moderado", "CCSOLO": "Salida de Coca Codo sola (caso central)",
           "CCOFF": "Salida de la clase de Coca Codo (Coca Codo Sinclair y Sopladora)",
           "CCOFFANOSECO": "Salida de la clase de Coca Codo y año seco severo",
           "CCDER": "Derrateo de Coca Codo", "FOI": "Sin pisos térmicos (K16 en PPFOI; Modelo CLG en PPDSL y PPNGS)",
           "IMP0": "Importación cero desde Colombia", "SIN": "Sin sus proyectos (contrafactual)",
           "ACT": "Situación actual 2026, demanda transitoria (ACT)",
           "ACTDEM": "Situación actual 2026, demanda persistente (ACT-DEM)",
           "GAS": "Sin la expansión a gas declarada (sobre CONA6G)"}
# estados con respaldo de emergencia (grupo de palancas RESP, decision del 13-10-2026)
RESPALDO = "RESP"


def rotulo(sufijo, defecto=None):
    """Rotulo de presentacion de un estado por su sufijo (ANOSECO, CCSOLO...)."""
    return ROTULOS.get(str(sufijo or ""), defecto if defecto is not None else str(sufijo or ""))

PALANCA = re.compile(r"^\[([^\]]+)\]")


def _filas(nombre):
    """Hojas de B1 y hojas Art6_*, todas desde B1_Scenario_Config.xlsx (un solo libro de configuracion)."""
    libro = C.CONFIG
    return _leer_hoja(nombre, str(libro), C.huella(libro))


@lru_cache(maxsize=64)
def _leer_hoja(nombre, libro, huella):
    """La huella (fecha del libro) es parte de la llave: si el libro cambia, la hoja se vuelve a leer."""
    wb = openpyxl.load_workbook(libro, data_only=True, read_only=True)
    filas = list(wb[nombre].iter_rows(values_only=True))
    wb.close()
    cab = [str(x).strip() if x is not None else "" for x in filas[0]]
    return tuple(dict(zip(cab, f)) for f in filas[1:] if f and f[0] is not None)


def hoja(nombre):
    """Filas de la hoja documental Art6_<nombre>."""
    return [dict(f) for f in _filas("Art6_" + nombre)]


def escenarios():
    """Escenarios que se reportan, en el orden de Art6_Escenarios. La base y la activacion se leen
    de la hoja Scenarios, que es la que usa B1: base = "B1" para los de referencia."""
    sc = {r["Name"]: r for r in _filas("Scenarios")}
    out = []
    for e in hoja("Escenarios"):
        r = sc.get(e["codigo"])
        if r is None:
            raise ValueError("Art6_Escenarios nombra %s, que no está en la hoja Scenarios" % e["codigo"])
        out.append(dict(e, base="B1" if r["Based_On"] == "ref" else r["Based_On"],
                        correr="SI" if r["Activated"] == "YES" else "NO"))
    return out


def grupos_de(e):
    return [x.strip() for x in str(e["palancas"] or "").split(",") if x.strip()]


def palancas():
    """Documentacion de cada palanca (Art6_Palancas)."""
    return hoja("Palancas")


def filas_de(hoja_b1, esc):
    """Filas de una hoja de B1 (Electrical, SmartGrid, Efficiency) para un escenario, sin la
    columna Scenario."""
    return [{k: v for k, v in r.items() if k != "Scenario"} for r in _filas(hoja_b1) if r["Scenario"] == esc]


def palancas_en(esc):
    """{codigo de palanca: fila de Electrical} del escenario."""
    out = {}
    for r in filas_de("Electrical", esc):
        m = PALANCA.match(str(r.get("Description Parameter-Set") or ""))
        if m:
            out[m.group(1)] = r
    for r in filas_de("Efficiency", esc):            # palancas de demanda (demandas exogenas por combustible)
        m = PALANCA.match(str(r.get("Description_Set") or ""))
        if m:
            out[m.group(1)] = dict(r, Tech_Set=r.get("Set"), _hoja="Efficiency")
    return out


def filas_palanca(esc):
    """(parametro, tecnologia) de las filas de Electrical que B1 cambia en el escenario: las que llevan
    codigo de palanca en la descripcion."""
    return {(r["Parameter"], str(r["Tech_Set"])) for r in palancas_en(esc).values()}


def _nombre_b1(r):
    """Nombre del escenario en la descripcion de la hoja Scenarios: el texto antes del primer punto."""
    return str(r.get("Description") or r["Name"]).split(". ")[0].strip()


def roles_fijos():
    """{rol: escenario} de la hoja Art6_Roles (inc, con, inc_clg, con_clg, tendencial_clg, ref_estado:<sufijo>)."""
    return {str(r["rol"]): str(r["escenario"]) for r in hoja("Roles")}


def roles(presentes, efecto=None):
    """Papel de cada escenario de la corrida, con los roles explicitos de Art6_Roles.

    inc, con        referencias corregidas (INCA6 y CONA6); con es la base de A, B y C y la referencia de sus capas.
    inc_clg, con_clg, tendencial_clg
                    escenarios del Modelo CLG para la proyeccion del Modelo CLG y la agregacion nacional.
    ref_estado      {sufijo: referencia} de las familias que cambian la referencia (FOI: CONA6P, IMP0: CONA6I).
    escalera        escenarios del grupo «Escenario Art. 6» de Art6_Escenarios (A, B y C), ordenados por cuantas filas
                    de palanca tienen; base[c] es el escalon cuyas filas contiene o, para el primero, con.
    estados         pruebas sobre la escalera por la convencion <escenario>-<estado> (A-CCOFF, B-FOI), con su grupo de
                    Art6_Escenarios (Riesgo, Sensibilidad o Contrafactual), su referencia, sus componentes y sus
                    miembros {escenario: codigo}.
    puentes         {escenario: codigo del puente V7} (grupo Puente): las palancas del sandbox del 08-10-2026 sobre CONA6.
    """
    sc = {r["Name"]: r for r in _filas("Scenarios")}
    doc = {e["codigo"]: e for e in hoja("Escenarios")}
    R = roles_fijos()
    universo = [n for n in sc if n in presentes or n in doc] + sorted(set(presentes) - set(sc))
    nombre = {c: (doc[c]["nombre"] if c in doc else (_nombre_b1(sc[c]) if c in sc else c)) for c in universo}
    inc, con = R["inc"], R["con"]
    ref_estado = {k.split(":", 1)[1]: v for k, v in R.items() if k.startswith("ref_estado:")}
    refs = [c for c in (R.get("inc_clg"), R.get("con_clg"), inc, con) + tuple(ref_estado.values()) if c in universo]
    esc = [c for c in universo if doc.get(c, {}).get("grupo") == "Escenario Art. 6"]
    filas = {c: filas_palanca(c) for c in esc}
    esc.sort(key=lambda c: len(filas[c]))
    base = {}
    for c in esc:
        previos = [x for x in esc if filas[x] < filas[c]]
        base[c] = max(previos, key=lambda x: len(filas[x])) if previos else con
    estados, puentes = [], {}
    for cod in universo:
        if "-" not in cod or cod.split("-", 1)[0] not in esc:
            continue
        fam, suf = cod.split("-", 1)
        grupo = doc.get(cod, {}).get("grupo")
        if grupo == "Puente":
            puentes[fam] = cod
            continue
        d = next((x for x in estados if x["sufijo"] == suf), None)
        if d is None:
            nom = nombre[cod].split(" · ", 1)[-1].strip()
            et = re.sub(r"\s*\([^)]*\)\s*$", "", nom).strip() or suf
            d = {"sufijo": suf, "nombre": nom[:1].upper() + nom[1:], "etiqueta": et[:1].upper() + et[1:],
                 "grupo": grupo if grupo in ("Riesgo", "Sensibilidad", "Contrafactual") else "Riesgo",
                 "referencia": ref_estado.get(suf, con), "miembros": {}}
            estados.append(d)
        d["miembros"][fam] = cod
        base[cod] = fam
    for d in estados:
        otros = [x["sufijo"] for x in estados if x is not d and x["grupo"] == d["grupo"] and x["sufijo"] in d["sufijo"]]
        d["componentes"] = otros if len(otros) >= 2 else [d["sufijo"]]
        d["frase"] = FRASES.get(d["sufijo"], d["nombre"][:1].lower() + d["nombre"][1:])
        d["rotulo"] = rotulo(d["sufijo"], d["nombre"])
    return {"inc": inc, "con": con, "inc_clg": R.get("inc_clg"), "con_clg": R.get("con_clg"),
            "tendencial_clg": R.get("tendencial_clg"), "ref_estado": ref_estado, "refs": refs, "escalera": esc,
            "base": base, "estados": estados, "puentes": puentes, "nombre": nombre,
            "presentes": [c for c in universo if c in presentes]}


def act2026():
    """{clase hidroeléctrica: factor de 2026 del estado ACT y ACT-DEM} de la hoja Art6_ACT2026."""
    return {str(f["clase"]): float(f["factor_2026"]) for f in hoja("ACT2026")
            if str(f.get("clase") or "").startswith("PP") and isinstance(f.get("factor_2026"), (int, float))}


def anoseco():
    """{clase hidroeléctrica: razón de caudales 2024} de la hoja Art6_AnoSeco."""
    out = {}
    for f in hoja("AnoSeco"):
        clase, razon = str(f.get("Clase") or ""), f.get("Razón aplicada")
        if clase.startswith("PP") and isinstance(razon, (int, float)):
            out[clase] = float(razon)
    return out


PARAMETRO_TXT = {"CapacityFactor": "factor de planta", "TotalTechnologyAnnualActivityLowerLimit": "piso",
                 "TotalTechnologyAnnualActivityUpperLimit": "techo"}


def riesgos_agrupados(P=None):
    """Palancas de los riesgos hidrologicos (codigos R-), una entrada por grupo: nombre del riesgo,
    rango y numero de palancas, tecnologias, parametros, mecanismo y fuente. Las tablas y fichas
    muestran una fila por riesgo en lugar de una por palanca."""
    P = palancas() if P is None else P
    R = {r["grupo"]: r for r in hoja("Riesgos")}
    out = {}
    for g in dict.fromkeys(p["grupo"] for p in P):
        xs = [p for p in P if p["grupo"] == g]
        if not xs or not all(str(p["id"]).startswith("R-") for p in xs):
            continue
        partes = g.split("_")
        r0 = R.get(partes[0], {})
        nombre = str(r0.get("nombre") or g)
        mecanismo = str(r0.get("mecanismo") or xs[0]["descripcion"] or "")
        if len(partes) > 1:
            nombre += ", sobre " + " y ".join(FRASES.get(x, x) for x in partes[1:])
            mecanismo = (mecanismo.rstrip(".") + ", aplicado sobre los valores de " + " y ".join(
                FRASES.get(x, x) for x in partes[1:]) + ".").replace(" de el ", " del ")
        tecs = list(dict.fromkeys(str(p["tecnologia"]) for p in xs))
        pars = list(dict.fromkeys(PARAMETRO_TXT.get(p["parametro"], p["parametro"]) for p in xs))
        pars_txt = C.enumerar(pars)
        if "piso" in pars or "techo" in pars:
            pars_txt += " de actividad"
        tecs_txt = ("las %d clases hidroeléctricas" % len(tecs)) if len(tecs) > 1 else "la clase %s" % tecs[0]
        rango = xs[0]["id"] if len(xs) == 1 else "%s a %s" % (xs[0]["id"], xs[-1]["id"])
        fuentes = list(dict.fromkeys(str(p["fuente"]) for p in xs if p.get("fuente")))
        out[g] = {"grupo": g, "nombre": nombre, "n": len(xs), "rango": rango, "tecnologias": tecs,
                  "tecnologias_txt": tecs_txt, "parametros_txt": pars_txt, "mecanismo": mecanismo,
                  "fuente": "; ".join(fuentes),
                  "resumen": "%s: %s de %s (%d palancas, %s). %s" % (nombre, pars_txt, tecs_txt, len(xs), rango,
                                                                     mecanismo)}
    return out


def esperadas(e, P):
    """Palancas que la composicion de Art6_Escenarios asigna al escenario. Los grupos se aplican en
    orden y, si dos palancas tocan la misma fila, manda la ultima: {(parametro, clave): codigo}."""
    final = {}
    for g in grupos_de(e):
        for p in P:
            if p["grupo"] == g:
                final[(p["parametro"], str(p["clave"]))] = p["id"]
    return final
