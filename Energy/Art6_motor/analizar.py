# -*- coding: utf-8 -*-
"""Analiza las corridas: emisiones, generacion, capacidad, ERNC, volumenes, headroom, sobreventa e
ingresos. Los resultados se leen de la salida de B1 de cada escenario (Executables/<ESC>_0/<ESC>_0_Output.csv e
_Input.csv) del Modelo Climate Lead Group (CLG) en la rama art6-escenarios.
Escribe tablas CSV en B2_Output_Art6/tablas y B2_Output_Art6/resultados_art6.json.

Los escenarios son los de Art6_Escenarios con solucion optima en la ultima corrida de B1. El papel de cada uno (referencias, escalera de
escenarios de Articulo 6 y pruebas sobre ellos) lo da configuracion.roles() con la definicion que usa
B1; lo que falte en la corrida se omite y se informa en "faltan".

Reglas de contabilidad:

- Volumen adicional a la NDC (regla R2): reduccion del escenario frente a la referencia condicional.
  Se puede transferir sin tocar ninguna de las dos metas.
- Volumen con tramo condicional (regla R1): reduccion frente a la referencia incondicional.
  Venderlo obliga a renunciar a la meta condicional en la misma cuantia.
- Capas: el tramo condicional (incondicional menos condicional) y, por cada escenario de la escalera,
  lo que reduce frente a su base.
- Margen (headroom): meta incondicional nacional del ano menos la trayectoria nacional
  del escenario. La trayectoria nacional es la del condicional mas la diferencia del sector energia
  frente a la referencia condicional (los otros sectores cumplen su condicional). Regla prudente:
  la del incondicional mas la diferencia frente a la referencia incondicional. La hoja Art6_Headroom
  decide si condicional e incondicional son las sendas de las metas publicadas de la Segunda NDC
  (7 % y 8 % adicional sobre el tendencial) o las series modeladas de la agregacion nacional del Modelo CLG
  (PowerBI/Nacionales).
- Sobreventa: lo que se autorizaria con el escenario intacto y no existe bajo el riesgo.
- Termica desplazable: generacion termica por encima de su piso de despacho obligatorio, lo unico
  que una renovable adicional puede sustituir (actividad del _Output.csv frente al piso del
  _Input.csv de cada escenario).
- Oferta por linea (informacion adicional de Art6_Adicionalidad, con el potencial declarado en el
  Plan de Implementacion): firme, las lineas con adicionalidad «Firme»; condicionadas declaradas,
  las lineas «Por demostrar» que la estrategia de actores clasifico como «Condicionada» y tienen
  potencial declarado; sin adicionalidad, las lineas «Sin adicionalidad». Las capas de la escalera
  entran con la reduccion que calcula el modelo.

resultados() es la entrada de las graficas y del cuaderno: si las salidas de B1, el libro
de configuracion, los insumos o el codigo del analisis cambiaron despues del ultimo analisis, lo
recalcula antes de devolverlo.
"""
import datetime
import io
import json
import re
from functools import lru_cache
from pathlib import Path

import pandas as pd

import comun as C
import configuracion as K

JSON = C.RESULTADOS / "resultados_art6.json"

# valores de regla_nacional y regla_prudente (hoja Art6_Headroom) y la columna de nacional() que usan:
# la senda de la meta publicada o la serie modelada de la agregacion nacional del Modelo CLG
TRAYECTORIA = {"meta_condicional": "meta_con", "meta_incondicional": "meta_inc",
               "condicional": "condicional", "incondicional": "incondicional"}

# ------------------------------------------------------------------ decisiones del 13-10-2026
FECHA_DECISIONES = "2026-10-13"
# 1. Lineas fuera de la oferta 2031-2035 mientras no se demuestre su adicionalidad regulatoria. Se informan como linea
#    condicionada en reserva, con su potencial declarado, y no entran en la oferta, la autorizacion ni los ingresos.
LINEAS_EN_RESERVA = {"EN32": "adicionalidad regulatoria por demostrar (decisión del 13-10-2026)"}
# 2. La autorizacion se dimensiona con la proyeccion del Modelo CLG y la regla prudente: lo transferible con el sistema
#    intacto en esa lectura. Las otras tres lecturas del margen quedan como sensibilidad.
AUTORIZACION = ("CLG", "prudente")
LECTURAS = [("CLG", "prudente"), ("CLG", "condicional"), ("corregida", "condicional"), ("corregida", "prudente")]
# 3. Metodos de ajuste correspondiente para una meta de un solo anio (Decision 2/CMA.3, anexo, parr. 7): la regla anual o
#    de trayectoria (cada anada contra el margen de su anio) y el metodo de promedio (NDC-CAT, PNUMA y UNEP-CCC 2026,
#    hoja Step 4: el ajuste del anio meta es la suma transferida en el periodo de la NDC dividida por sus anios).
METODOS = ("anual", "promedio")
ANIOS_PERIODO_NDC = len(C.MARCO)          # 2026-2035: 10
# 5. Estados de referencia de la reserva por anada: situacion actual anclada a 2026 en sus dos variantes de demanda (ACT,
#    choque transitorio; ACTDEM, demanda persistente) y salida de Coca Codo sola
ESTADOS_REFERENCIA = ("ACT", "ACTDEM", "CCSOLO")


def reportados():
    """Escenarios de Art6_Escenarios (el BAU interno de B1 no se reporta)."""
    return [e["codigo"] for e in K.escenarios()]


def estados_solucion():
    return {c: C.estado_solucion(c) for c in reportados()}


def cargar_corridas():
    """Resultados de cada escenario de Art6_Escenarios con solucion optima en la ultima corrida de B1, leidos de
    Executables/<ESC>_0/<ESC>_0_Output.csv. Un escenario sin solucion queda fuera y se informa en «faltan» y en
    solucion_por_escenario.csv como hallazgo de suficiencia."""
    est = estados_solucion()
    ok = [c for c, s in est.items() if s == "optimo"]
    O = C.leer_ecuoutput(ok)
    return {c: C.resultados_de(O, c) for c in ok}


def serie(d):
    return pd.Series(d, index=C.ANIOS, dtype=float)


def energia_clg_kt():
    """Emisiones del sector energia por escenario del Modelo CLG (kt CO2e), desde
    ECU_NDC/PowerBI/Energy/ECUOutput_Energy.csv: suma de AnnualTechnologyEmission de CO2e_DE, CO2e_PP, CO2e_FUG y
    CO2e_REF por 1.000 (la regla con que se armo la copia del sandbox; coincide con ella a 0,05 kt). Se guarda en
    Insumos_Art6/Energia_oficial_por_escenario_kt.csv."""
    destino = C.INSUMOS / "Energia_oficial_por_escenario_kt.csv"
    if destino.exists() and destino.stat().st_mtime >= C.ENERGIA_CLG.stat().st_mtime             and destino.stat().st_mtime >= Path(__file__).stat().st_mtime:
        return pd.read_csv(destino, index_col=0).reindex(C.ANIOS)
    o = pd.read_csv(C.ENERGIA_CLG, usecols=["Strategy", "Emission", "Year", "AnnualTechnologyEmission"],
                    low_memory=False)
    o = o[o["Emission"].isin(C.COMP_ENERGIA)]
    t = (o.groupby(["Year", "Strategy"])["AnnualTechnologyEmission"].sum() * 1000.0).unstack("Strategy")
    t.index = t.index.astype(int)
    t = t.reindex(C.ANIOS).round(1)
    t.index.name = "anio"
    t.to_csv(destino, encoding="utf-8-sig")
    return t


def nacional():
    """Trayectorias nacionales de la agregacion del Modelo CLG y senda lineal de la meta (ECU_NDC/PowerBI/Nacionales/Emisiones Totales.xlsx,
    md5 igual al de la copia del sandbox)."""
    H = {h["parametro"]: h["valor"] for h in K.hoja("Headroom")}
    d = pd.read_excel(C.NACIONAL)
    piv = d.pivot_table(index="Año", columns="Escenario", values="Valor")
    piv.index = piv.index.astype(int)
    base = piv["Tendencial 1era NDC"].reindex(C.ANIOS)
    inc = piv["Incondicional 2da NDC"].reindex(C.ANIOS)
    con = piv["Incondicional y Condicional 2da NDC"].reindex(C.ANIOS)
    a0, a1 = int(H["anio_inicio_senda"]), int(H["anio_meta"])
    frac = pd.Series([(a - a0) / float(a1 - a0) if a >= a0 else float("nan") for a in C.ANIOS],
                     index=C.ANIOS)
    meta_inc = base - float(H["meta_inc_kt"]) * frac
    meta_con = base - (float(H["meta_inc_kt"]) + float(H["meta_con_kt"])) * frac
    return pd.DataFrame({"base": base, "incondicional": inc, "condicional": con,
                         "meta_inc": meta_inc, "meta_con": meta_con}), H


def termica_desplazable_gwh(R):
    """{escenario: [26]} GWh de generacion termica por encima de su piso de despacho obligatorio.
    Por tecnologia termica: produccion electrica x (actividad - piso) / actividad."""
    termicas = sorted({t for r in R.values() for t in r["actividad"]
                       if C.familia(t) and C.tipo_familia(C.familia(t)) == "termica"})
    I = C.leer_ecuinput([C.PISO], list(R))
    piso = I[I["Technology"].isin(termicas)].groupby(["Strategy", "Technology", "Year"])[C.PISO].mean()
    out = {}
    for c, r in R.items():
        tot = [0.0] * len(C.ANIOS)
        for t in termicas:
            act = r["actividad"].get(t)
            if not act:
                continue
            gen = [sum(v[i] for (tec, comb), v in r["produccion"].items() if tec == t and comb in ("E1ELE", "E3ELE"))
                   for i in range(len(C.ANIOS))]
            for i, a in enumerate(C.ANIOS):
                p = piso.get((c, t, a))
                p = 0.0 if p is None or pd.isna(p) else float(p)
                if act[i] > 0:
                    tot[i] += gen[i] * max(0.0, act[i] - p) / act[i] * C.PJ_A_GWH
        out[c] = [round(x, 1) for x in tot]
    return out


def _kt(x):
    """Reduccion anual declarada de una linea de Art6_Adicionalidad, o None si no la declara."""
    v = x.get("kt_anio_declarado")
    try:
        return float(v) if v not in (None, "") else None
    except (TypeError, ValueError):
        return None


def _periodo(x):
    m = re.match(r"\s*(\d{4})\s*-\s*(\d{4})", str(x.get("periodo") or ""))
    return (int(m.group(1)), int(m.group(2))) if m else None


def _declarado(lineas, anio):
    """Suma de la reduccion declarada de las lineas activas en el anio."""
    tot = 0.0
    for x in lineas:
        p, kt = _periodo(x), _kt(x)
        if p and kt is not None and p[0] <= anio <= p[1]:
            tot += kt
    return tot


def _capa(c, b, T, ad):
    """Nombre y nivel de la capa del escenario c sobre su base b, segun donde ubica Art6_Adicionalidad
    las lineas del escenario (escenario_art6): fuera de la NDC o dentro de ella."""
    ndc = {str(x.get("escenario_NDC") or "") for x in ad if str(x.get("escenario_art6") or "").strip() == c}
    nombre = T["nombre"].get(c, c)
    if ndc and ndc <= {"Fuera de la NDC"}:
        largo = "Paquete fuera de la NDC (%s sobre %s)" % (c, b)
        return {"escenario": c, "base": b, "largo": largo, "corto": largo, "fuera_ndc": True,
                "bloque": "Por demostrar: paquete fuera de la NDC, %s sobre %s (modelo)" % (c, b),
                "nivel": "por demostrar fuera NDC"}
    de = ("de la " if str(nombre).startswith("NDC") else "del ") + str(nombre)
    if b == T["con"]:
        largo, corto = "Proyectos %s (sobre el condicional)" % de, "Proyectos %s" % de
    else:
        largo = corto = "Capa %s (sobre %s)" % (de, T["nombre"].get(b, b))
    return {"escenario": c, "base": b, "largo": largo, "corto": corto, "fuera_ndc": False,
            "bloque": "Por demostrar: %s (modelo)" % (corto[:1].lower() + corto[1:]), "nivel": "por demostrar"}


def _origenes():
    """Archivos de los que depende el analisis: la corrida, el libro de configuracion, los insumos
    nacionales y el codigo que calcula."""
    aqui = Path(__file__).resolve().parent
    return (C.origenes_resultados(reportados() + ["INCA6G"])
            + [C.CONFIG, C.ART6_CONFIG, C.NACIONAL, C.ENERGIA_CLG,
               C.ENERGY / "Art6_calibracion" / "calibracion_h_suficiencia_escenarios_art6.csv",
               SENSIBILIDAD_PISOS_CLG / "B2_Output_Art6" / "resultados_art6.json"]
            + sorted(p for p in C.INSUMOS.glob("*.*") if p.name != "Energia_oficial_por_escenario_kt.csv")
            + [aqui / "analizar.py", aqui / "comun.py", aqui / "configuracion.py", aqui / "cifras_producto3.py"])


def vigente():
    """True si resultados_art6.json es posterior a todos sus origenes."""
    if not JSON.exists():
        return False
    return JSON.stat().st_mtime >= max(p.stat().st_mtime for p in _origenes() if p.exists())


def resultados():
    """Resultados de la ultima corrida: si algun origen es mas reciente que resultados_art6.json,
    recalcula el analisis antes de leerlo, de modo que el visualizador nunca muestra una corrida
    anterior a la ultima salida de B1."""
    if not vigente():
        print("Las salidas de B1, la configuración o el código cambiaron: se recalcula el análisis.")
        main(resumen=False)
    return _leer(C.huella(JSON))


@lru_cache(maxsize=2)
def _leer(huella):
    return json.load(io.open(JSON, encoding="utf-8"))


def _fecha(p):
    return datetime.datetime.fromtimestamp(p.stat().st_mtime).strftime("%Y-%m-%dT%H:%M") if p.exists() else None


# ---------------------------------------------------------------------------------------- tablas del 13-10-2026
# Valores de comparacion del factor del MWh desplazado: MAE, Comision Tecnica de Factores de Emision, Informe del Factor
# de Emision de CO2 del S.N.I. 2025, tabla 6, p. 17 (S26-065 y S26-067); perimetro, p. 11: S.N.I. sin Galapagos, Puna,
# Sistema Oriental ni SEIP. El margen de operacion simple ajustado es (1 - lambda) x media de los generadores de no bajo
# costo; el modelo (un timeslice) no tiene lambda, de modo que su factor se compara con los dos valores.
MARGEN_OPERACION_2025 = 0.6364        # t CO2/MWh netos
MEDIA_NO_BAJO_COSTO_2025 = 0.7706     # t CO2/MWh netos (3.836.232 t CO2 / 4.978.520 MWh)
LAMBDA_2025 = 0.1741
NETA_BRUTA = 4952.41 / 5136.35        # CENACE, Informe Anual 2025, Parte 1, figuras 1.10 y 1.7: termica neta / bruta
RED = ("PPFOI", "PPDSL", "PPNGS")     # termicas de la red (S.N.I.) que desplazan A, B y C
DEMANDA_ELE = ("E5COMELE", "E5INDELE", "E5RESELE", "E5TROELE", "E5ALLTRNELE", "E5CONELE")
CAU_PPFOI = 31.536                    # CapacityToActivityUnit de PPFOI en los datafiles (PJ por GW-anio)
# resultados con los pisos de despacho del Modelo CLG (base sin K16), guardados el 13-10-2026 antes de la corrida con K16
# sandbox PNUD: copia de las salidas que la cita necesita (resultados_art6.json y _Output.csv de CONA6, A, B y C), con
# el manifiesto md5 de la carpeta original
SENSIBILIDAD_PISOS_CLG = C.ENERGY / "Art6_calibracion" / "sensibilidad_pisos_CLG_2026-10-12"
SUPUESTOS_OFERTA = {
    "central_K16_con_gas": "Base congelada del 13-10-2026 con K16 (piso de PPFOI 2026-2035 = 5,0567 PJ, mínimo observado "
                           "2015-2025) y la expansión a gas declarada (Anexo A del ajuste del PME, K15d-e); capas A, B y C "
                           "frente a CONA6, A y B; líneas declaradas del Plan de Implementación. En CONA6 y CONA6G la "
                           "carpeta A2 conserva el piso de PPFOI del Modelo CLG (9,3785 PJ): el valor que rige, K16, vive "
                           "en la fila de Electrical (K16-PPFOI-CON).",
    "K16_sin_gas": "La misma base con K16 sin la expansión a gas declarada (CONA6G: PPNGS en su piso CLG, G01); capas A-GAS, "
                   "B-GAS y C-GAS frente a CONA6G, A-GAS y B-GAS; las mismas líneas declaradas.",
    "pisos_CLG_12_10": "Sensibilidad guardada del 12-10-2026: base sin K16, con el piso de despacho de PPFOI del Modelo CLG "
                       "(9,3785 PJ hasta 2030 y 9,0 PJ en 2035, valor de 2022 congelado sin fuente) y la expansión a gas "
                       "declarada (_stale_ECU_NDC_2026-10-11/resultados_con_pisos_CLG_2026-10-12)."}


def _ceros():
    return [0.0] * len(C.ANIOS)


# usos finales de E3ELE que no son SpecifiedAnnualDemand: T4ELE_HEA (E3ELE -> E4ELE_HEA). Con ellos, D = E5*ELE + T4ELE_HEA
# es todo el uso de E3ELE (los demas consumidores, T5ELE* y T5ALLTRNELE, entregan los E5*ELE de DEMANDA_ELE)
USO_FINAL_E3ELE_EXTRA = ("T4ELE_HEA",)


def uso_final_e3ele_extra(escenarios):
    """{(escenario, anio): PJ} de E3ELE que usan las tecnologias de USO_FINAL_E3ELE_EXTRA (UseByTechnology del
    _Output.csv). Correccion del 13-10-2026 tras la verificacion independiente del paso 15: la demanda D de las horas de
    corte equivalentes lo omitia (en C-ACTDEM 2029, 1,19 PJ)."""
    out = {}
    for c in escenarios:
        p = C.salida(c)
        if not p.exists():
            continue
        o = pd.read_csv(p, usecols=["Fuel", "Technology", "Year", "UseByTechnology"], low_memory=False)
        x = o[(o["Fuel"] == "E3ELE") & o["Technology"].isin(USO_FINAL_E3ELE_EXTRA) & o["UseByTechnology"].notna()]
        for a, v in x.groupby("Year")["UseByTechnology"].sum().items():
            out[(c, int(a))] = float(v)
    return out


# rotulo de las referencias que se informan junto a los escenarios (13-10-2026): INCA6G lleva las filas RE01, un supuesto
# de cierre introducido en la corrida K16 que se aprobo conservar rotulado despues de la verificacion
ROTULO_REFERENCIA = {"INCA6G": "INCA6G, con cierre de fuel oil de emergencia"}


def _texto_stoele(R, rs):
    """Frase sobre STOELE para las notas: sin actividad en 2026-2035 en los escenarios con respaldo, y los anios en que la
    base CONA6 si la tiene (herencia del Modelo CLG). Se calcula, no se escribe a mano."""
    con = next((c for c in ("CONA6",) if c in R), None)
    hist = []
    if con:
        sto = R[con]["actividad"].get("STOELE", _ceros())
        hist = [a for a in C.ANIOS if sto[C.IDX[a]] > 1e-6]
    marco = float(rs.STOELE_GWh.sum()) if len(rs) else 0.0
    t = ("STOELE: sin actividad en 2026-2035 en los escenarios con respaldo" if marco < 0.05
         else "STOELE: %s GWh en 2026-2035 en los escenarios con respaldo" % ("%.1f" % marco).replace(".", ","))
    if hist:
        t += " (en CONA6 tiene actividad en %s, heredada del Modelo CLG)" % C.enumerar([str(a) for a in hist])
    return t + "."


def tablas_13_10(R, em, T, doc, base, capa_ok, bloques, V, MC, hr, hr_corr, anual, anual_c, aut, aut_c, en_reserva):
    """Tablas del 13-10-2026: sobreventa por anio y riesgo, respaldo de emergencia con sus horas de
    corte equivalentes, oferta 2031-2035 en tres niveles (sin y con las lineas en reserva) y factor del MWh desplazado
    frente al margen de operacion."""
    out = {}
    con = T["con"]

    # 1. sobreventa por anio y por riesgo, con las dos reglas y las dos proyecciones. Lo autorizado es lo transferible con
    #    el sistema intacto en la proyeccion del Modelo CLG y la regla prudente, sin las lineas en reserva (decisiones 1
    #    y 2 del 13-10-2026), igual en las cuatro lecturas. Primer anio de margen negativo: sin transferir (2026-2035) y
    #    tras transferir (2031-2035).
    sa, sr = [], []
    for proy, hr_p, anual_p, aut_p in (("CLG", hr, anual, aut), ("corregida", hr_corr, anual_c, aut_c)):
        for x in anual_p:
            h = hr_p[(hr_p.escenario == x["escenario"]) & (hr_p.regla == x["regla"])]
            if h.empty:
                continue
            h = h.iloc[0]
            serie_m = {}
            for a in MC:
                m = h.get(str(a))
                m = None if m is None or pd.isna(m) else float(m)
                au = float(aut_p.get(str(a), 0.0)) if a in V else 0.0
                serie_m[a] = (m, au)
                sa.append({"proyeccion": proy, "regla": x["regla"], "estado": x["estado"],
                           "sufijo": x["sufijo"].lstrip("-"), "escenario": x["escenario"], "anio": a,
                           "margen_kt": None if m is None else round(m, 1), "autorizado_kt": round(au, 1),
                           "margen_tras_transferir_kt": None if m is None else round(m - au, 1),
                           "sobreventa_kt": None if m is None else round(max(0.0, au - max(0.0, m)), 1),
                           "incumplimiento_sin_transferir_kt": None if m is None else round(max(0.0, -m), 1)})
            neg = [a for a in MC if serie_m[a][0] is not None and serie_m[a][0] < 0]
            neg_t = [a for a in V if serie_m[a][0] is not None and serie_m[a][0] - serie_m[a][1] < 0]
            sr.append({"proyeccion": proy, "regla": x["regla"], "estado": x["estado"], "sufijo": x["sufijo"].lstrip("-"),
                       "escenario": x["escenario"],
                       "primer_anio_margen_negativo": neg[0] if neg else None,
                       "primer_anio_margen_negativo_tras_transferir": neg_t[0] if neg_t else None,
                       "autorizado_2031_2035": round(sum(serie_m[a][1] for a in V), 1),
                       "sobreventa_2031_2035": round(sum(max(0.0, serie_m[a][1] - max(0.0, serie_m[a][0]))
                                                         for a in V if serie_m[a][0] is not None), 1),
                       "incumplimiento_sin_transferir_2031_2035": round(sum(max(0.0, -serie_m[a][0]) for a in V
                                                                            if serie_m[a][0] is not None), 1),
                       "margen_2035": None if serie_m[2035][0] is None else round(serie_m[2035][0], 1)})
    # el JSON lleva las listas (None y anios enteros); los CSV, anios como enteros con vacio donde no hay
    out["sobreventa_anual"] = {"anual": sa, "resumen": sr,
                               "regla_de_autorizacion": "lo transferible con el sistema intacto en la proyección del "
                                                        "Modelo CLG y la regla %s, sin las líneas en reserva (decisión "
                                                        "del %s)" % (AUTORIZACION[1], FECHA_DECISIONES)}
    pd.DataFrame(sa).to_csv(C.TABLAS / "sobreventa_anual_por_riesgo.csv", index=False, encoding="utf-8-sig")
    sr_df = pd.DataFrame(sr)
    for col in ("primer_anio_margen_negativo", "primer_anio_margen_negativo_tras_transferir"):
        if col in sr_df:
            sr_df[col] = sr_df[col].astype("Int64")
    sr_df.to_csv(C.TABLAS / "sobreventa_primer_anio_negativo.csv", index=False, encoding="utf-8-sig")

    # 2. respaldo de emergencia: potencia de PPFOI sobre el tope K15b, su energia y sus emisiones, la energia no
    #    suministrada equivalente si esa energia no se generara y sus horas de corte equivalentes (correccion del
    #    13-10-2026 tras la verificacion independiente): el respaldo R entra en E1ELE y pierde en ELE_TRANS y ELE_DIST antes
    #    de llegar a la demanda final D, de modo que ENS = R x eta_T x eta_D, H_dia = 24 x ENS / D, H_anio = 8.760 x ENS / D
    #    y, con el deficit concentrado en 6 meses de estiaje (supuesto), H_estiaje = 24 x ENS / (D x 6/12). Las eficiencias
    #    se leen del datafile de cada escenario: OutputActivityRatio / InputActivityRatio de ELE_TRANS y ELE_DIST.
    grupos = lambda c: [g.strip() for g in str((doc.get(c) or {}).get("palancas") or "").split(",")]
    casos = {c: R[c] for c in R if K.RESPALDO in grupos(c)}
    for c in ("INCA6G",):                       # referencia con RE01 (correcciones_K.csv), fuera de Art6_Escenarios
        if c not in R and C.estado_solucion(c) == "optimo":
            casos[c] = C.resultados_de(C.leer_ecuoutput([c]), c)
    rs, fp_resp = [], set()
    if casos:
        tope = C.tabla(C.leer_datafile(C.datafile(con)))[("TotalAnnualMaxCapacity", "PPFOI")][1]
        I = C.leer_ecuinput(["SpecifiedAnnualDemand"], list(casos))
        dem = I[I["Fuel"].isin(DEMANDA_ELE)].groupby(["Strategy", "Year"])["SpecifiedAnnualDemand"].sum()
        # D = demanda E5*ELE mas el uso final de E3ELE que no es SpecifiedAnnualDemand (T4ELE_HEA), correccion del
        # 13-10-2026 tras la verificacion independiente del paso 15
        uso_x = uso_final_e3ele_extra(list(casos))
        for c, r in casos.items():
            Tx = C.tabla(C.leer_datafile(C.datafile(c)))
            cf = Tx[("CapacityFactor", "PPFOI,All")][1]
            af = Tx.get(("AvailabilityFactor", "PPFOI"), (None, [1.0] * len(C.ANIOS)))[1]
            tope_c = Tx[("TotalAnnualMaxCapacity", "PPFOI")][1]
            eta = {}
            for tec, ent, sal in (("ELE_TRANS", "E1ELE", "E2ELE"), ("ELE_DIST", "E2ELE", "E3ELE")):
                iar, oar = Tx[("InputActivityRatio", "%s,%s,1" % (tec, ent))][1], \
                    Tx[("OutputActivityRatio", "%s,%s,1" % (tec, sal))][1]
                eta[tec] = [o_ / i_ for o_, i_ in zip(oar, iar)]
            act, cap = r["actividad"].get("PPFOI", _ceros()), r["capacidad"].get("PPFOI", _ceros())
            epp = r["emis_tec"].get(("PPFOI", "CO2e_PP"), _ceros())
            sto = r["actividad"].get("STOELE", _ceros())
            for a in MC:
                i = C.IDX[a]
                e_pj = max(0.0, act[i] - tope[i] * cf[i] * af[i] * CAU_PPFOI)
                d5_gwh = float(dem.get((c, a), 0.0)) * C.PJ_A_GWH
                ux_gwh = float(uso_x.get((c, a), 0.0)) * C.PJ_A_GWH
                d_gwh = d5_gwh + ux_gwh
                gwh = e_pj * C.PJ_A_GWH
                et, ed = eta["ELE_TRANS"][i], eta["ELE_DIST"][i]
                ens = gwh * et * ed
                resp_mw = max(0.0, cap[i] - tope[i]) * 1000.0
                if resp_mw > 0.5:
                    fp_resp.add(round(cf[i] * af[i], 4))
                rs.append({"escenario": c, "anio": a, "tope_K15b_MW": round(tope[i] * 1000.0, 1),
                           "tope_liberado": bool(tope_c[i] >= 9999), "PPFOI_MW": round(cap[i] * 1000.0, 1),
                           "respaldo_MW": round(resp_mw, 1),
                           "factor_planta_PPFOI": round(cf[i] * af[i], 4),
                           "respaldo_GWh": round(gwh, 1),
                           "respaldo_kt_CO2e": round(1000.0 * epp[i] * e_pj / act[i], 1) if act[i] > 0 else 0.0,
                           "eta_transmision": round(et, 6), "eta_distribucion": round(ed, 6),
                           "ENS_equivalente_GWh": round(ens, 1),
                           "demanda_E5ELE_GWh": round(d5_gwh, 1), "uso_E3ELE_T4ELE_HEA_GWh": round(ux_gwh, 1),
                           "demanda_electrica_final_GWh": round(d_gwh, 1),
                           "ENS_pct_demanda": round(100.0 * ens / d_gwh, 3) if d_gwh > 0 else None,
                           "horas_corte_equivalentes_por_dia": round(24.0 * ens / d_gwh, 2) if d_gwh > 0 else None,
                           "horas_corte_equivalentes_por_anio": round(8760.0 * ens / d_gwh, 1) if d_gwh > 0 else None,
                           "horas_corte_por_dia_estiaje_6_meses": round(24.0 * ens / (d_gwh * 6.0 / 12.0), 2)
                           if d_gwh > 0 else None,
                           "horas_formula_anterior_24RD_por_dia": round(24.0 * gwh / d_gwh, 2) if d_gwh > 0 else None,
                           "STOELE_GWh": round(sto[i] * C.PJ_A_GWH, 1)})
    rs = pd.DataFrame(rs, columns=["escenario", "anio", "tope_K15b_MW", "tope_liberado", "PPFOI_MW", "respaldo_MW",
                                   "factor_planta_PPFOI", "respaldo_GWh", "respaldo_kt_CO2e", "eta_transmision",
                                   "eta_distribucion", "ENS_equivalente_GWh", "demanda_E5ELE_GWh",
                                   "uso_E3ELE_T4ELE_HEA_GWh", "demanda_electrica_final_GWh",
                                   "ENS_pct_demanda", "horas_corte_equivalentes_por_dia",
                                   "horas_corte_equivalentes_por_anio", "horas_corte_por_dia_estiaje_6_meses",
                                   "horas_formula_anterior_24RD_por_dia", "STOELE_GWh"])
    rs.to_csv(C.TABLAS / "respaldo_por_escenario.csv", index=False, encoding="utf-8-sig")
    resumen_r = []
    maxi = lambda s, d: None if s.isna().all() else round(float(s.max()), d)
    for c in rs["escenario"].unique() if len(rs) else []:
        x = rs[rs.escenario == c]
        con_r = x[x.respaldo_MW > 0.5]
        im = x.respaldo_MW.idxmax()
        ih = x.ENS_equivalente_GWh.idxmax()
        resumen_r.append({"escenario": c, "rotulo": ROTULO_REFERENCIA.get(c, c),
                          "primer_anio_con_respaldo": int(con_r.anio.min()) if len(con_r) else None,
                          "respaldo_max_MW": round(float(x.respaldo_MW.max()), 1),
                          "anio_respaldo_max": int(x.loc[im, "anio"]) if float(x.respaldo_MW.max()) > 0.5 else None,
                          "respaldo_2031_2035_GWh": round(float(x[x.anio.isin(V)].respaldo_GWh.sum()), 1),
                          "respaldo_2031_2035_kt_CO2e": round(float(x[x.anio.isin(V)].respaldo_kt_CO2e.sum()), 1),
                          "ENS_2031_2035_GWh": round(float(x[x.anio.isin(V)].ENS_equivalente_GWh.sum()), 1),
                          "ENS_max_GWh": round(float(x.ENS_equivalente_GWh.max()), 1),
                          "anio_ENS_max": int(x.loc[ih, "anio"]) if float(x.ENS_equivalente_GWh.max()) > 0.05 else None,
                          "ENS_max_pct_demanda": maxi(x.ENS_pct_demanda, 3),
                          "horas_corte_max_por_dia": maxi(x.horas_corte_equivalentes_por_dia, 2),
                          "horas_corte_max_por_anio": maxi(x.horas_corte_equivalentes_por_anio, 1),
                          "horas_corte_max_por_dia_estiaje_6_meses": maxi(x.horas_corte_por_dia_estiaje_6_meses, 2),
                          "horas_formula_anterior_max_por_dia": maxi(x.horas_formula_anterior_24RD_por_dia, 2),
                          "STOELE_2026_2035_GWh": round(float(x.STOELE_GWh.sum()), 1)})
    fp_txt = C.enumerar([("%.4f" % v).replace(".", ",") for v in sorted(fp_resp)]) or "0,4254"
    prod_eta = sorted({round(a_ * b_, 4) for a_, b_ in zip(rs.eta_transmision, rs.eta_distribucion)}) if len(rs) else []
    eta_txt = ("producto %s en 2026-2035" % C.enumerar([("%.4f" % v).replace(".", ",") for v in prod_eta])) if prod_eta \
        else "sin escenarios con respaldo"
    exceso_txt = (("%.1f %%" % (100.0 * (1.0 / prod_eta[0] - 1.0))).replace(".", ",")) if prod_eta else "s. d."
    out["respaldo"] = {"anual": rs.astype(object).where(rs.notna(), None).to_dict(orient="records"),
                       "resumen": resumen_r,
                       "rotulo_MW": "MW equivalentes con factor de planta de %s" % fp_txt,
                       "nota": "Respaldo de emergencia R: generación de PPFOI sobre lo que permite el tope K15b (en barras "
                               "de central, E1ELE). Su potencia son MW equivalentes con factor de planta de %s: el modelo "
                               "tiene un solo timeslice y dimensiona la potencia por energía anual, de modo que no ve la "
                               "punta de demanda ni el estiaje. Energía no suministrada equivalente si ese respaldo no se "
                               "generara: ENS = R x eta_T x eta_D, con las eficiencias de ELE_TRANS y ELE_DIST leídas del "
                               "datafile (%s). Horas de corte equivalentes: 24 x ENS / D por día "
                               "y 8.760 x ENS / D por año, con D la demanda eléctrica final: los seis E5*ELE más el uso "
                               "de E3ELE de T4ELE_HEA, que no es SpecifiedAnnualDemand (corrección del 13-10-2026); "
                               "variante de estiaje "
                               "de 6 meses, 24 x ENS / (D x 6/12), con el déficit concentrado en la mitad seca del año "
                               "(supuesto). La fórmula anterior, 24 x R / D, excedía en %s al mezclar energía en barras "
                               "de central con demanda final (columna horas_formula_anterior_24RD_por_dia, solo para "
                               "trazabilidad). %s Indicador, no pronóstico de racionamiento."
                               % (fp_txt, eta_txt, exceso_txt, _texto_stoele(R, rs)),
                       "producto_eta": prod_eta}

    # 3. oferta 2031-2035 por caso (rotulos del 13-10-2026): central (K16 con gas), con pisos del Modelo CLG (corrida del
    #    12-10) y sensibilidad sin gas de la capa 1, que no es un nivel de oferta. Antes: robusta, central y potencial entre el caso
    #    central, el mismo sin la expansion a gas declarada (familia GAS) y la sensibilidad con los pisos del Modelo CLG.
    #    La oferta vigente excluye las lineas en reserva (decision 1 del 13-10-2026); la variante con ellas se informa
    #    aparte, con la cifra anterior a la decision.
    res_a = {a: _declarado(en_reserva, a) for a in V}
    def oferta_de(bls):
        anual_o, comp = {a: 0.0 for a in V}, {}
        for nom, nivel, clave, f in bls:
            v = {a: f(a) for a in V}
            comp[clave] = {"bloque": nom, "kt_2031_2035": round(sum(v.values()), 1)}
            for a in V:
                anual_o[a] += v[a]
        return anual_o, comp
    casos_o = {}
    a_c, c_c = oferta_de(bloques)
    casos_o["central_K16_con_gas"] = (a_c, c_c)
    d_gas = next((d for d in T["estados"] if d["sufijo"] == "GAS"), None)
    if d_gas and all(d_gas["miembros"].get(c) in em for c in capa_ok) and d_gas["referencia"] in em:
        gas_de = lambda c: d_gas["referencia"] if base[c] == con else d_gas["miembros"][base[c]]
        bls_g = []
        for nom, nivel, clave, f in bloques:
            if clave.startswith("capa:"):
                c = clave.split(":", 1)[1]
                e_g, b_g = d_gas["miembros"][c], gas_de(c)
                f = (lambda a, b=b_g, e=e_g: max(0.0, em[b][a] - em[e][a]))
                nom = nom + " [sin gas: %s sobre %s]" % (e_g, b_g)
            bls_g.append((nom, nivel, clave, f))
        casos_o["K16_sin_gas"] = oferta_de(bls_g)
    sens = SENSIBILIDAD_PISOS_CLG / "B2_Output_Art6" / "resultados_art6.json"
    if sens.exists():
        J = json.load(io.open(sens, encoding="utf-8"))
        pa = J["potencial_art6"]
        fila_a = next(x for x in pa["anual"] if x["sufijo"] == "" and x["regla"] == "condicional")
        fila_t = next(x for x in pa["tabla"] if x["sufijo"] == "" and x["regla"] == "condicional")
        # la sensibilidad del 12-10-2026 es anterior a la decision: su bloque declarado trae las lineas en reserva, que
        # se restan con su potencial declarado
        en_sens = set(J.get("grupos_de_lineas", {}).get("condicionadas_declaradas", []))
        quita = [x for x in en_reserva if x["codigo"] in en_sens]
        comp_s = {clave: {"bloque": nom, "kt_2031_2035": float(fila_t.get(nom) or 0.0)} for nom, nivel, clave in pa["bloques"]}
        if quita and "declarado" in comp_s:
            comp_s["declarado"]["kt_2031_2035"] = round(comp_s["declarado"]["kt_2031_2035"]
                                                        - sum(_declarado(quita, a) for a in V), 1)
            comp_s["declarado"]["bloque"] += " [sin %s]" % C.enumerar([x["codigo"] for x in quita])
        casos_o["pisos_CLG_12_10"] = ({a: float(fila_a["oferta"][str(a)]) - _declarado(quita, a) for a in V}, comp_s)
    tot = {k: round(sum(v[0].values()), 1) for k, v in casos_o.items()}
    tot_res = {k: round(sum(v[0][a] + res_a[a] for a in V), 1) for k, v in casos_o.items()}
    kt_res = round(sum(res_a.values()), 1)
    cods_res = C.enumerar([x["codigo"] for x in en_reserva]) or "ninguna"
    # rotulos del 13-10-2026 (despues de la verificacion independiente): cada nivel se nombra por su caso. El antiguo
    # «robusta» es la corrida con los pisos del Modelo CLG del 12-10-2026; el antiguo «potencial» es la sensibilidad sin
    # gas de la capa 1 (volumen fisico que el modelo sostiene) y no es un nivel de oferta
    reglas_n = {"central": "caso central con K16 y la expansión a gas declarada",
                "con_pisos_CLG_12_10": "con pisos del Modelo CLG (corrida del 12-10)",
                "sensibilidad_sin_gas_capa_1": "sensibilidad sin gas de la capa 1; no es un nivel de oferta"}
    es_oferta = {"central": True, "con_pisos_CLG_12_10": True, "sensibilidad_sin_gas_capa_1": False}

    def niveles_de(totales, suma_res):
        filas_n = []
        for nivel, k in (("central", "central_K16_con_gas"), ("con_pisos_CLG_12_10", "pisos_CLG_12_10"),
                         ("sensibilidad_sin_gas_capa_1", "K16_sin_gas")):
            if k not in totales:
                continue
            filas_n.append({"nivel": nivel, "rotulo": reglas_n[nivel], "es_nivel_de_oferta": es_oferta[nivel],
                            "caso": k,
                            "lineas_en_reserva": ("incluidas (%s; cifra anterior a la decisión del %s)"
                                                  % (cods_res, FECHA_DECISIONES)) if suma_res
                            else "excluidas (%s fuera de la oferta; oferta vigente)" % cods_res,
                            "kt_2031_2035": totales[k],
                            **{str(a): round(casos_o[k][0][a] + (res_a[a] if suma_res else 0.0), 1) for a in V},
                            "kt_en_reserva": kt_res, "supuesto": SUPUESTOS_OFERTA[k], "regla": reglas_n[nivel]})
        return filas_n
    niveles, niveles_con = niveles_de(tot, False), niveles_de(tot_res, True)
    detalle = []
    for k, (an, comp) in casos_o.items():
        for clave, d in comp.items():
            detalle.append({"caso": k, "clave": clave, "bloque": d["bloque"], "kt_2031_2035": d["kt_2031_2035"]})
        detalle.append({"caso": k, "clave": "total", "bloque": "Oferta total, sin las líneas en reserva",
                        "kt_2031_2035": tot[k], **{str(a): round(an[a], 1) for a in V}})
        if en_reserva:
            detalle.append({"caso": k, "clave": "en_reserva", "bloque": "En reserva, fuera de la oferta: %s" % cods_res,
                            "kt_2031_2035": kt_res, **{str(a): round(res_a[a], 1) for a in V}})
            detalle.append({"caso": k, "clave": "total_con_reserva",
                            "bloque": "Oferta con las líneas en reserva (anterior a la decisión del %s)" % FECHA_DECISIONES,
                            "kt_2031_2035": tot_res[k], **{str(a): round(an[a] + res_a[a], 1) for a in V}})
    pd.DataFrame(niveles + niveles_con).to_csv(C.TABLAS / "oferta_tres_niveles.csv", index=False, encoding="utf-8-sig")
    pd.DataFrame(detalle).to_csv(C.TABLAS / "oferta_por_caso.csv", index=False, encoding="utf-8-sig")
    out["oferta_niveles"] = {"niveles": niveles, "niveles_con_reserva": niveles_con, "detalle": detalle, "totales": tot,
                             "totales_con_reserva": tot_res, "kt_en_reserva": kt_res, "lineas_en_reserva": cods_res,
                             "supuestos": SUPUESTOS_OFERTA, "rotulos": reglas_n, "es_nivel_de_oferta": es_oferta,
                             "sensibilidad_pisos_CLG": {"json": sens.relative_to(C.RAIZ).as_posix(), "md5": C.md5(sens) if sens.exists() else None}}

    # 4. factor del MWh desplazado de cada capa frente al margen de operacion oficial de 2025 (CO2 neto de la red)
    def gen_red(r):
        return [sum(v[i] for (t, f), v in r["produccion"].items() if t in RED and f in ("E1ELE", "E3ELE"))
                for i in range(len(C.ANIOS))]

    def co2_red(r):
        return [sum(r["co2_pp_tec"].get(t, _ceros())[i] for t in RED) for i in range(len(C.ANIOS))]

    def co2e_pp(r):
        return [sum(v[i] for (t, comp), v in r["emis_tec"].items() if comp == "CO2e_PP") for i in range(len(C.ANIOS))]

    def termica(r):
        g = C.generacion_por_familia_pj(r)
        return [sum(g[f][i] for f in g if C.tipo_familia(f) == "termica") for i in range(len(C.ANIOS))]
    pares = [("intacto", base[c], c) for c in capa_ok]
    if d_gas:
        pares += [("sin gas", d_gas["referencia"] if base[c] == con else d_gas["miembros"].get(base[c]),
                   d_gas["miembros"].get(c)) for c in capa_ok]
    fv = []
    for caso, b_, e_ in pares:
        if b_ not in R or e_ not in R:
            continue
        gb, ge = gen_red(R[b_]), gen_red(R[e_])
        cb, ce = co2_red(R[b_]), co2_red(R[e_])
        pb, pe = co2e_pp(R[b_]), co2e_pp(R[e_])
        tb, te = termica(R[b_]), termica(R[e_])
        for etiqueta, anios in [(str(a), [a]) for a in MC] + [("2031-2035", V)]:
            ix = [C.IDX[a] for a in anios]
            dg = sum(gb[i] - ge[i] for i in ix) * C.PJ_A_GWH                 # GWh brutos de la red
            dc = sum(cb[i] - ce[i] for i in ix) * 1e6                        # t CO2 de la red
            dp = sum(pb[i] - pe[i] for i in ix) * 1e3                        # kt CO2e de toda la generacion
            dt = sum(tb[i] - te[i] for i in ix) * C.PJ_A_GWH                 # GWh de toda la termica e importacion
            f_red = dc / (dg * 1000.0) / NETA_BRUTA if dg > 1.0 else None
            fv.append({"caso": caso, "base": b_, "escenario": e_, "periodo": etiqueta,
                       "reduccion_CO2e_PP_kt": round(dp, 1), "termica_desplazada_GWh": round(dt, 1),
                       "red_desplazada_GWh_brutos": round(dg, 1), "reduccion_CO2_red_kt": round(dc / 1000.0, 1),
                       "factor_CO2e_bruto_t_MWh": round(dp * 1000.0 / (dt * 1000.0), 4) if dt > 1.0 else None,
                       "factor_CO2_neto_red_t_MWh": None if f_red is None else round(f_red, 4),
                       "margen_operacion_2025": MARGEN_OPERACION_2025,
                       "media_no_bajo_costo_2025": MEDIA_NO_BAJO_COSTO_2025,
                       "razon_frente_al_margen_operacion": None if f_red is None
                       else round(f_red / MARGEN_OPERACION_2025, 3),
                       "razon_frente_a_media_no_bajo_costo": None if f_red is None
                       else round(f_red / MEDIA_NO_BAJO_COSTO_2025, 3)})
    fv = pd.DataFrame(fv)
    fv.to_csv(C.TABLAS / "factor_desplazado_frente_al_margen.csv", index=False, encoding="utf-8-sig")

    # 5. estado ACT anclado a 2026 (decision del 13-10-2026): 2026 del modelo frente a lo observado
    out["act_2026"] = contraste_act_2026(R, con)
    out["factor_frente_al_margen"] = {
        "tabla": fv.astype(object).where(fv.notna(), None).to_dict(orient="records"),
        "margen_operacion_2025": MARGEN_OPERACION_2025,
        "media_no_bajo_costo_2025": MEDIA_NO_BAJO_COSTO_2025, "lambda_2025": LAMBDA_2025,
        "neta_bruta": round(NETA_BRUTA, 6),
        "perimetro": "Margen de operación: S.N.I. sin Galápagos, Puná, Sistema Oriental ni SEIP, t CO2 por MWh netos "
                     "(CTFE 2025, tabla 6 y p. 11). Factor del modelo: CO2 (sin CH4 ni N2O) de PPFOI, PPDSL y PPNGS sobre "
                     "su generación bruta llevada a neta con la razón térmica neta/bruta de CENACE 2025; PPFOI incluye el "
                     "fuel oil de autoproductores que K13 le asigna. El modelo no tiene lambda (un timeslice): su "
                     "comparable directo es la media de los generadores de no bajo costo (0,7706)."}
    return out


# perimetro S.N.I. del contraste de 2026 (mismo que CENACE: sin autoproductores PPCRU, PPRNGS, PPRDSL, PPILPG ni PPIHD)
TERMICA_SNI = ("PPFOI", "PPDSL", "PPNGS", "PPDFOI", "PPDDSL")
ERNC_SNI = ("PPWNDON", "PPWNDD", "PPPVT", "PPPVD", "PPPVTS", "PPGEO", "PPBIM", "PPIBIM", "PPBGS")
PARTICIPACION_CC_2025 = 7695.99 / (7695.99 + 2884.03)   # CENACE, Informe Anual 2025, figura 1.4 (S26-008)


def contraste_act_2026(R, con):
    """2025 y 2026 de CONA6 y de los estados ACT y ACTDEM frente a lo observado en 2025 y 2026 (hoja Art6_ACT2026_Datos,
    que situacion_act_2026.py lee de CENACE y XM). Perimetro S.N.I.: hidro (PPH*), termica de la red y de las
    distribuidoras, ERNC e importacion. La participacion termica se calcula igual en el modelo y en lo observado, con la
    importacion en el denominador: termica / (hidro + termica + ERNC + importacion). Observado: 2025 con indicadores.xlsx
    y la importacion del Informe Anual 2025 (14,55 %); 2026 con enero a agosto de indicadores.xlsx, el Informe Ejecutivo
    de agosto de 2026 y su importacion (20,50 %), y acumulado al 10-10-2026 del tablero de CENACE (20,67 %). Correccion
    del 13-10-2026 tras la verificacion independiente del paso 15: antes el observado de enero a agosto (20,68 %) y el de
    2025 (14,8 %) excluian la importacion. Coca Codo: participacion de 2025 en la energia de PPHRORAB por la actividad de
    la clase sobre la potencia efectiva del Informe Anual 2025 (1.500 MW). Escribe act_2026_contraste.csv, con el
    observado de cada anio en sus columnas."""
    obs = {str(f["clave"]): f["valor"] for f in K.hoja("ACT2026_Datos") if f.get("clave")}
    g = lambda k: float(obs[k]) if k in obs and obs[k] is not None else None
    # participacion termica observada con importacion, por anio del contraste: (valor, periodo)
    ter_obs = {2025: (g("termica_participacion_2025"), "2025, producción neta con importación"),
               2026: (g("termica_participacion_ene_ago_2026"), "ene-ago 2026, producción neta con importación")}
    imp_obs = {2025: (g("importacion_2025_GWh"), "2025"),
               2026: (g("importacion_2026_antes_07_09_GWh"), "01-01 a 06-09-2026")}
    escs = [c for c in [con] + [c for c in R if c.split("-", 1)[-1] in ("ACT", "ACTDEM") and "-" in c] if c in R]
    I = C.leer_ecuinput(["SpecifiedAnnualDemand"], escs)
    I = I[I["Fuel"].isin(DEMANDA_ELE)].groupby(["Strategy", "Fuel", "Year"])["SpecifiedAnnualDemand"].sum()
    filas = []
    for c in escs:
        a_ = R[c]["actividad"]
        d_ = {f: [float(I.get((c, f, a), 0.0)) for a in C.ANIOS] for f in DEMANDA_ELE}
        serie_tec = lambda ts: [sum(a_.get(t, _ceros())[i] for t in ts) for i in range(len(C.ANIOS))]
        hid = [sum(v[i] for t, v in a_.items() if str(t).startswith("PPH")) for i in range(len(C.ANIOS))]
        ter, ern, imp = serie_tec(TERMICA_SNI), serie_tec(ERNC_SNI), serie_tec(("IMPELE",))
        hro = a_.get("PPHRORAB", _ceros())
        dem = [sum(d_.get(f, _ceros())[i] for f in DEMANDA_ELE) for i in range(len(C.ANIOS))]
        gw_cc = (g("cc_potencia_efectiva_MW") or 1500.0) / 1000.0
        for a in (2025, 2026, 2027):
            i = C.IDX[a]
            tot = hid[i] + ter[i] + ern[i] + imp[i]
            p_ter = 100.0 * ter[i] / tot if tot else None
            o_ter, per_o = ter_obs.get(a, (None, None))
            o_imp, per_i = imp_obs.get(a, (None, None))
            filas.append({"escenario": c, "anio": a, "demanda_electrica_final_GWh": round(dem[i] * C.PJ_A_GWH, 1),
                          "crecimiento_demanda_pct": round(100.0 * (dem[i] / dem[i - 1] - 1.0), 2) if dem[i - 1] else None,
                          "hidro_GWh": round(hid[i] * C.PJ_A_GWH, 1),
                          "crecimiento_hidro_pct": round(100.0 * (hid[i] / hid[i - 1] - 1.0), 2) if hid[i - 1] else None,
                          "termica_SNI_GWh": round(ter[i] * C.PJ_A_GWH, 1), "ERNC_GWh": round(ern[i] * C.PJ_A_GWH, 1),
                          "importacion_GWh": round(imp[i] * C.PJ_A_GWH, 1),
                          "participacion_termica_SNI_pct": None if p_ter is None else round(p_ter, 2),
                          "participacion_hidro_SNI_pct": round(100.0 * hid[i] / tot, 2) if tot else None,
                          "fp_coca_codo_participacion_2025_pct": round(100.0 * PARTICIPACION_CC_2025 * hro[i]
                                                                       / (gw_cc * CAU_PPFOI), 2),
                          # observado con el mismo perimetro (importacion en el denominador)
                          "participacion_termica_observada_pct": None if o_ter is None else round(100.0 * o_ter, 2),
                          "periodo_observado": per_o,
                          "diferencia_termica_modelo_menos_observado_pp": None if o_ter is None or p_ter is None
                          else round(p_ter - 100.0 * o_ter, 2),
                          "importacion_observada_GWh": None if o_imp is None else round(o_imp, 2),
                          "periodo_importacion_observada": per_i})
    df = pd.DataFrame(filas)
    df.to_csv(C.TABLAS / "act_2026_contraste.csv", index=False, encoding="utf-8-sig")
    observado = {"crecimiento_demanda_ene_ago_pct": round(100.0 * (g("crecimiento_demanda_2026") - 1.0), 2),
                 "crecimiento_hidro_ene_ago_pct": round(100.0 * (g("hidro_ene_ago_razon_2026_2025") - 1.0), 2),
                 "crecimiento_hidro_ene_jul_pct": round(100.0 * (g("hidro_ene_jul_razon_2026_2025") - 1.0), 2),
                 "participacion_termica_ene_ago_pct": round(100.0 * g("termica_participacion_ene_ago_2026"), 2),
                 "participacion_termica_al_10_oct_pct": round(100.0 * g("termica_participacion_2026_al_10_oct"), 2),
                 "participacion_termica_2025_pct": round(100.0 * g("termica_participacion_2025"), 2),
                 "participacion_termica_ene_ago_sin_importacion_pct":
                     round(100.0 * g("termica_participacion_ene_ago_2026_sin_importacion"), 2),
                 "participacion_termica_2025_sin_importacion_pct":
                     round(100.0 * g("termica_participacion_2025_sin_importacion"), 2),
                 "fp_coca_codo_al_10_oct_pct": round(100.0 * g("cc_fp_2026_al_10_oct"), 2),
                 "fp_coca_codo_2026_estimado_pct": round(100.0 * g("cc_fp_2026_estimado"), 2),
                 "fp_coca_codo_2025_pct": round(100.0 * g("cc_fp_2025"), 2),
                 "importacion_2025_GWh": round(g("importacion_2025_GWh"), 2),
                 "importacion_2026_antes_07_09_GWh": round(g("importacion_2026_antes_07_09_GWh"), 2)}
    return {"tabla": df.astype(object).where(df.notna(), None).to_dict(orient="records"), "observado": observado,
            "perimetro": "S.N.I.: hidro (PPH*), térmica de la red y de las distribuidoras (PPFOI, PPDSL, PPNGS, PPDFOI, "
                         "PPDDSL), ERNC (eólica, solar, geotermia, biomasa y biogás) e importación; sin autoproductores. "
                         "Participación térmica = térmica / (hidro + térmica + ERNC + importación) en el modelo y en lo "
                         "observado. Observado: CENACE, producción neta con la importación en el denominador (2025: "
                         "indicadores.xlsx e Informe Anual 2025; enero a agosto de 2026: indicadores.xlsx e Informe "
                         "Ejecutivo de agosto de 2026, secciones 1 y 2; al 10-10-2026: tablero de Información Operativa) "
                         "y XM, hoja Art6_ACT2026_Datos. Las claves *_sin_importacion quedan para la trazabilidad: no son "
                         "comparables con el modelo (corrección del 13-10-2026).",
            "nota": "En el diseño de ACT, Coca Codo entra en 2026 con el factor de planta estimado de 2026 y Sopladora con "
                    "su razón observada; la columna fp_coca_codo_participacion_2025_pct reparte la clase PPHRORAB con la "
                    "participación de Coca Codo en 2025, la lectura que usa el resto del motor."}


def _anio_o_vacio(df, cols):
    """Columnas de anio con vacio donde no hay (Int64), para los CSV."""
    for c in cols:
        if c in df:
            df[c] = df[c].astype("Int64")
    return df


def decisiones_13_10(em, T, bloques, en_reserva, capa_ok, base, V, MC, hr_all, riesgos, top, aut):
    """Decisiones del 13-10-2026 sobre la autorizacion de transferencias (las 1 y 2 se aplican en main y en
    tablas_13_10: lineas en reserva fuera de la oferta y autorizacion con el Modelo CLG y la regla prudente):

    3. sobreventa con los dos metodos de ajuste correspondiente para una meta de un solo anio (Decision 2/CMA.3, anexo,
       parr. 7): la regla anual o de trayectoria (cada anada contra el margen de su anio) y el metodo de promedio
       (NDC-CAT: ajuste de 2035 = suma transferida en 2026-2035 / 10; sobreventa = max(0, ajuste - max(0, margen 2035)));
    4. por subconjunto de oferta: toda, con las lineas en reserva; sin ellas (caso central); lista blanca del Capitulo 5
       (firme, condicionadas declaradas sin las lineas en reserva y capa del ultimo escalon), y solo firme;
    5. reserva por anada: en cada estado, lo autorizable de cada anada 2031-2035 sin dejar el margen negativo en la lectura
       de autorizacion, min(oferta, max(0, margen)); su suma es lo transferible sin incumplir de ese estado;
    6. autorizable ex post: minimo entre la reduccion que el estado produce (lineas declaradas y capas medidas dentro del
       estado) y el margen disponible.

    Lo autorizado de cada subconjunto es lo transferible con el sistema intacto en la lectura de AUTORIZACION y se evalua
    contra los margenes de las cuatro lecturas (headroom_proyecciones.csv). Escribe
    sobreventa_por_metodo_y_subconjunto.csv, reserva_por_aniada.csv y autorizable_ex_post.csv."""
    out = {}
    if top is None or not capa_ok:
        return out
    con = T["con"]
    N = ANIOS_PERIODO_NDC
    cods_res = [x["codigo"] for x in en_reserva]
    suf_res = "_".join(cods_res) or "reserva"
    txt_res = C.enumerar(cods_res) or "líneas en reserva"
    claves = [clave for _, _, clave, _ in bloques]
    f_de = {clave: f for _, _, clave, f in bloques}
    capa_top = "capa:" + capa_ok[-1]
    SUB = [("toda_con_" + suf_res, "Potencial: toda la oferta, con %s" % txt_res, claves, True),
           ("sin_" + suf_res, "Caso central: toda la oferta, sin %s" % txt_res, claves, False),
           ("lista_blanca", "Lista blanca del Capítulo 5: firme, condicionadas declaradas sin %s y capa del %s"
            % (txt_res, capa_ok[-1]), [k for k in claves if k in ("firme", "declarado", capa_top)], False),
           ("solo_firme", "Solo firme", [k for k in claves if k == "firme"], False)]
    central = "sin_" + suf_res

    def margen(proy, esc, regla):
        h = hr_all[(hr_all.proyeccion == proy) & (hr_all.escenario == esc) & (hr_all.regla == regla)]
        return None if h.empty else {a: float(h.iloc[0][str(a)]) for a in MC}

    m_aut = margen(AUTORIZACION[0], top, AUTORIZACION[1])
    of, au = {}, {}
    for sk, _, cl, con_res in SUB:
        of[sk] = {a: sum(f_de[k](a) for k in cl) + (_declarado(en_reserva, a) if con_res else 0.0) for a in V}
        # sin redondear: se suma y se redondea el total (convencion del 13-10-2026, como aut en potencial_y_sobreventa)
        au[sk] = {a: min(of[sk][a], max(0.0, m_aut[a])) for a in V}
    estados = [{"sufijo": "", "etiqueta": "Intacto", "escenario": top, "d": None}] + \
              [{"sufijo": d["sufijo"], "etiqueta": d["etiqueta"], "escenario": d["miembros"][top], "d": d}
               for d in riesgos if d["miembros"].get(top) in em]
    es_ref = lambda e: e["sufijo"] in ESTADOS_REFERENCIA

    # ---------------------------------------------------------------- 3 y 4. sobreventa por metodo y subconjunto
    filas = []
    for sk, snom, cl, con_res in SUB:
        Vt = sum(au[sk].values())
        ca = Vt / N                                     # ajuste anual del metodo de promedio (transferencias 2031-2035)
        for e in estados:
            for proy, regla in LECTURAS:
                m = margen(proy, e["escenario"], regla)
                if m is None:
                    continue
                comun = {"subconjunto": sk, "subconjunto_nombre": snom,
                         "oferta_2031_2035": round(sum(of[sk].values()), 1), "autorizado_2031_2035": round(Vt, 1),
                         "proyeccion": proy, "regla": regla, "lectura_de_autorizacion": (proy, regla) == AUTORIZACION,
                         "estado": e["etiqueta"], "sufijo": e["sufijo"], "escenario": e["escenario"],
                         "estado_de_referencia": es_ref(e), "margen_2035": round(m[2035], 1),
                         "primer_anio_margen_negativo": next((a for a in MC if m[a] < 0), None)}
                s_a = {a: max(0.0, au[sk][a] - max(0.0, m[a])) for a in V}
                sob = sum(s_a.values())
                filas.append(dict(comun, metodo="anual", anios_evaluados="%d-%d" % (V[0], V[-1]),
                                  ajuste_2035=round(au[sk][2035], 1), sobreventa_kt=round(sob, 1),
                                  sobreventa_pct_autorizado=round(100.0 * sob / Vt, 1) if Vt > 0 else None,
                                  incumplimiento_propio_kt=round(sum(max(0.0, -m[a]) for a in V), 1),
                                  margen_2035_tras_ajuste=round(m[2035] - au[sk][2035], 1),
                                  primer_anio_negativo_tras_transferir=next((a for a in V if m[a] - au[sk][a] < 0), None),
                                  **{"sobreventa_%d" % a: round(s_a[a], 1) for a in V}))
                sob_p = max(0.0, ca - max(0.0, m[2035]))
                filas.append(dict(comun, metodo="promedio", anios_evaluados=str(V[-1]),
                                  ajuste_2035=round(ca, 1), sobreventa_kt=round(sob_p, 1),
                                  sobreventa_pct_autorizado=round(100.0 * sob_p / Vt, 1) if Vt > 0 else None,
                                  incumplimiento_propio_kt=round(max(0.0, -m[2035]), 1),
                                  margen_2035_tras_ajuste=round(m[2035] - ca, 1),
                                  primer_anio_negativo_tras_transferir=V[-1] if m[2035] - ca < 0 else None,
                                  **{"sobreventa_%d" % a: (round(sob_p, 1) if a == V[-1] else None) for a in V}))
    cols = (["subconjunto", "subconjunto_nombre", "metodo", "proyeccion", "regla", "lectura_de_autorizacion", "estado",
             "sufijo", "escenario", "estado_de_referencia", "oferta_2031_2035", "autorizado_2031_2035", "ajuste_2035",
             "margen_2035", "margen_2035_tras_ajuste", "sobreventa_kt", "sobreventa_pct_autorizado",
             "incumplimiento_propio_kt", "anios_evaluados", "primer_anio_margen_negativo",
             "primer_anio_negativo_tras_transferir"] + ["sobreventa_%d" % a for a in V])
    sv = _anio_o_vacio(pd.DataFrame(filas, columns=cols),
                       ["primer_anio_margen_negativo", "primer_anio_negativo_tras_transferir"])
    sv.to_csv(C.TABLAS / "sobreventa_por_metodo_y_subconjunto.csv", index=False, encoding="utf-8-sig")
    out["sobreventa_metodo_subconjunto"] = filas

    # ---------------------------------------------------------------- 5. reserva por anada
    rv, rv_res = [], []
    for sk, snom, cl, con_res in SUB:
        for e in estados:
            m = margen(AUTORIZACION[0], e["escenario"], AUTORIZACION[1])
            if m is None:
                continue
            filas_e, exactos = [], []
            for a in V:
                o = of[sk][a]
                ab = min(o, max(0.0, m[a]))                 # sin redondear; se redondea al escribir
                exactos.append((o, ab))
                filas_e.append({"subconjunto": sk, "estado": e["etiqueta"], "sufijo": e["sufijo"],
                                "escenario": e["escenario"], "estado_de_referencia": es_ref(e), "anio": str(a),
                                "oferta_kt": round(o, 1), "margen_kt": round(m[a], 1), "autorizable_kt": round(ab, 1),
                                "reserva_kt": round(o - ab, 1) + 0.0,
                                "reserva_pct": round(100.0 * (o - ab) / o, 1) + 0.0 if o > 0 else None})
            o_t, a_t = sum(x[0] for x in exactos), sum(x[1] for x in exactos)
            pct_u = max([x["reserva_pct"] for x in filas_e if x["reserva_pct"] is not None] or [0.0])
            filas_e.append({"subconjunto": sk, "estado": e["etiqueta"], "sufijo": e["sufijo"], "escenario": e["escenario"],
                            "estado_de_referencia": es_ref(e), "anio": "%d-%d" % (V[0], V[-1]), "oferta_kt": round(o_t, 1),
                            "margen_kt": round(sum(m[a] for a in V), 1), "autorizable_kt": round(a_t, 1),
                            "reserva_kt": round(o_t - a_t, 1) + 0.0,
                            "reserva_pct": round(100.0 * (o_t - a_t) / o_t, 1) + 0.0 if o_t > 0 else None})
            rv += filas_e
            rv_res.append({"subconjunto": sk, "estado": e["etiqueta"], "sufijo": e["sufijo"], "escenario": e["escenario"],
                           "estado_de_referencia": es_ref(e), "oferta_2031_2035": round(o_t, 1),
                           "autorizable_2031_2035": round(a_t, 1), "reserva_2031_2035": round(o_t - a_t, 1) + 0.0,
                           "reserva_pct": round(100.0 * (o_t - a_t) / o_t, 1) + 0.0 if o_t > 0 else None,
                           "reserva_uniforme_equivalente_pct": round(pct_u, 1),
                           "aniadas_con_reserva": [int(x["anio"]) for x in filas_e[:-1] if x["reserva_kt"] > 0.05],
                           "autorizable_por_aniada": {x["anio"]: x["autorizable_kt"] for x in filas_e[:-1]}})
    pd.DataFrame(rv).to_csv(C.TABLAS / "reserva_por_aniada.csv", index=False, encoding="utf-8-sig")
    out["reserva_por_aniada"] = {
        "anual": rv, "resumen": rv_res, "lectura": list(AUTORIZACION), "estados_de_referencia": list(ESTADOS_REFERENCIA),
        "nota": "Autorizable de cada año = min(oferta del año, max(0, margen del año en el estado)), proyección del "
                "Modelo CLG y regla prudente, regla anual de ajuste. La suma 2031-2035 es lo transferible sin incumplir "
                "del estado (potencial_articulo6.csv). Reserva = oferta - autorizable. La reserva uniforme equivalente es "
                "el porcentaje que, aplicado igual a todos los años, evitaría la sobreventa en el año más expuesto."}

    # ---------------------------------------------------------------- 6. autorizable ex post
    def capas_estado(e):
        """{capa: {anio: kt}} que cada escalon reduce dentro del estado, con la fuente de cada una."""
        d, red, fuente = e["d"], {}, {}
        for c in capa_ok:
            e_c = c if d is None else d["miembros"].get(c)
            if base[c] == con:
                ref_e = con if d is None else d["referencia"]
                if d is not None and ref_e == con:
                    # el estado no tiene una referencia CONA6 propia: la capa del primer escalon no se aisla del efecto del
                    # estado, de modo que se toma la capa intacta (supuesto)
                    b_c, e_c = con, c
                    fuente[c] = "capa intacta, %s menos %s: el estado no tiene referencia %s propia [supuesto]" % (con, c, con)
                else:
                    b_c = ref_e
                    fuente[c] = "%s menos %s" % (b_c, e_c)
            else:
                b_c = base[c] if d is None else d["miembros"].get(base[c])
                fuente[c] = "%s menos %s" % (b_c, e_c)
            red[c] = None if b_c not in em or e_c not in em else {a: max(0.0, em[b_c][a] - em[e_c][a]) for a in V}
        return red, fuente

    nombre_comp = lambda k: {"firme": "firme_kt", "declarado": "condicionadas_kt"}.get(k) or "capa_%s_kt" % k.split(":", 1)[-1]
    cols_comp = [nombre_comp(k) for k in claves]
    ep, ep_res = [], []
    for sk, snom, cl, con_res in [s for s in SUB if not s[3]]:
        for e in estados:
            red_c, fuente = capas_estado(e)
            if any(red_c.get(k.split(":", 1)[1]) is None for k in cl if k.startswith("capa:")):
                continue
            for proy, regla in LECTURAS:
                m = margen(proy, e["escenario"], regla)
                if m is None:
                    continue
                tot = {"reduccion": 0.0, "ex_post": 0.0, "ex_ante": 0.0}
                for a in V:
                    comp = {nombre_comp(k):
                            (red_c[k.split(":", 1)[1]][a] if k.startswith("capa:") else f_de[k](a)) for k in cl}
                    red = sum(comp.values())
                    sin_tope = min(red, max(0.0, m[a]))           # informativo: puede superar la oferta de la anada
                    ap = min(sin_tope, of[sk][a])                 # valor central (decision del 13-10-2026)
                    ea = au[sk][a]
                    ep.append({"subconjunto": sk, "proyeccion": proy, "regla": regla,
                               "lectura_de_autorizacion": (proy, regla) == AUTORIZACION, "estado": e["etiqueta"],
                               "sufijo": e["sufijo"], "escenario": e["escenario"], "estado_de_referencia": es_ref(e),
                               "anio": str(a), **{k: round(v, 1) for k, v in comp.items()},
                               "fuente_capa_%s" % capa_ok[0]: fuente[capa_ok[0]] if "capa:" + capa_ok[0] in cl else None,
                               "reduccion_estado_kt": round(red, 1), "margen_kt": round(m[a], 1),
                               "oferta_aniada_kt": round(of[sk][a], 1),
                               "autorizable_ex_post_kt": round(ap, 1), "autorizado_ex_ante_kt": round(ea, 1),
                               "diferencia_ex_post_menos_ex_ante_kt": round(ap - ea, 1) + 0.0,
                               "autorizable_ex_post_sin_tope_kt": round(sin_tope, 1)})
                    tot["reduccion"] += red
                    tot["ex_post"] += ap
                    tot["ex_ante"] += ea
                    tot["sin_tope"] = tot.get("sin_tope", 0.0) + sin_tope
                ep_res.append({"subconjunto": sk, "proyeccion": proy, "regla": regla,
                               "lectura_de_autorizacion": (proy, regla) == AUTORIZACION, "estado": e["etiqueta"],
                               "sufijo": e["sufijo"], "escenario": e["escenario"], "estado_de_referencia": es_ref(e),
                               "reduccion_estado_2031_2035": round(tot["reduccion"], 1),
                               "autorizable_ex_post_2031_2035": round(tot["ex_post"], 1),
                               "autorizado_ex_ante_2031_2035": round(tot["ex_ante"], 1),
                               "diferencia_2031_2035": round(tot["ex_post"] - tot["ex_ante"], 1) + 0.0,
                               "autorizable_ex_post_sin_tope_2031_2035": round(tot.get("sin_tope", 0.0), 1),
                               "fuente_capa_%s" % capa_ok[0]: fuente[capa_ok[0]]})
    cols_ep = (["subconjunto", "proyeccion", "regla", "lectura_de_autorizacion", "estado", "sufijo", "escenario",
                "estado_de_referencia", "anio"] + cols_comp + ["fuente_capa_%s" % capa_ok[0], "reduccion_estado_kt",
                                                               "margen_kt", "oferta_aniada_kt",
                                                               "autorizable_ex_post_kt", "autorizado_ex_ante_kt",
                                                               "diferencia_ex_post_menos_ex_ante_kt",
                                                               "autorizable_ex_post_sin_tope_kt"])
    pd.DataFrame(ep, columns=cols_ep).to_csv(C.TABLAS / "autorizable_ex_post.csv", index=False, encoding="utf-8-sig")
    out["autorizable_ex_post"] = {
        "anual": ep, "resumen": ep_res,
        "nota": "Autorizable ex post de cada año (valor central) = min(reducción "
                "que produce el estado, max(0, margen del año en el estado), oferta del año). La reducción suma las "
                "líneas declaradas (firme y condicionadas, con su potencial declarado, igual en todos los estados) y las "
                "capas medidas dentro del estado: cada escalón frente al escalón previo en el mismo estado; la capa del "
                "%s, frente a la referencia del estado cuando existe (CONA6I en IMP0) y, si no, la capa intacta, porque "
                "sin una referencia %s en el mismo estado no se aísla del efecto del estado, un supuesto declarado. Lo autorizado ex "
                "ante es lo transferible con el sistema intacto en la lectura de autorización. Bajo riesgo hidrológico "
                "las capas renovables desplazan más térmica que con el sistema intacto, de modo que la reducción del "
                "estado puede superar la oferta ex ante del año. El ex post sin tope en la oferta "
                "queda como dato informativo." % (capa_ok[0], con)}

    out["decisiones_13_10"] = {
        "fecha": FECHA_DECISIONES,
        "lineas_en_reserva": {x["codigo"]: {"linea": x["linea"], "motivo": LINEAS_EN_RESERVA[str(x["codigo"])],
                                            "kt_2031_2035": round(sum(_declarado([x], a) for a in V), 1)}
                              for x in en_reserva},
        "autorizacion": {"proyeccion": AUTORIZACION[0], "regla": AUTORIZACION[1],
                         "sensibilidad": ["%s_%s" % l for l in LECTURAS if l != AUTORIZACION]},
        "metodos": {"anual": "regla anual o de trayectoria: cada año de reducción se compara con el margen de ese año (2031-2035)",
                    "promedio": "método de promedio para una meta de un solo año (NDC-CAT, hoja Step 4): ajuste de %d "
                                "= suma transferida en %d-%d / %d" % (V[-1], C.MARCO[0], C.MARCO[-1], N)},
        "anios_periodo_ndc": N, "subconjunto_central": central,
        "subconjuntos": [{"clave": sk, "nombre": snom, "bloques": cl, "incluye_reserva": con_res,
                          "oferta": {str(a): round(of[sk][a], 1) for a in V},
                          "autorizado": {str(a): round(au[sk][a], 4) for a in V},
                          "oferta_2031_2035": round(sum(of[sk].values()), 1),
                          "autorizado_2031_2035": round(sum(au[sk].values()), 1)} for sk, snom, cl, con_res in SUB],
        "estados_de_referencia": list(ESTADOS_REFERENCIA)}
    return out


def main(resumen=True):
    R = cargar_corridas()
    V = list(C.VENTANA)
    em = pd.DataFrame({c: C.emisiones_energia_kt(r) for c, r in R.items()}, index=C.ANIOS)
    T = K.roles(list(R), lambda f, c: float((em[c] - em[f]).loc[V].sum()))
    inc, con = T["inc"], T["con"]
    sin_ref = [c for c in (inc, con) if c not in R]
    if sin_ref:
        raise ValueError("La corrida de B1 no trae solución de %s. El análisis de Artículo 6 mide cada escenario frente a las dos "
                         "referencias de la NDC (%s y %s): corra la cadena con ellas."
                         % (C.enumerar(sin_ref), inc, con))
    R = {c: R[c] for c in T["presentes"]}
    em = em[list(R)]
    esc = [c for c in T["escalera"] if c in R]
    base = T["base"]
    capa_ok = [c for c in esc if base.get(c) in R]           # escalones con su base en la corrida
    estados = [dict(d, miembros={f: c for f, c in d["miembros"].items() if c in R}) for d in T["estados"]]
    estados = [d for d in estados if d["miembros"]]
    riesgos = [d for d in estados if d["grupo"] == "Riesgo"]
    sens = [d for d in estados if d["grupo"] != "Riesgo"]
    ad = K.hoja("Adicionalidad")
    capas = {c: _capa(c, base[c], T, ad) for c in capa_ok}

    doc = {e["codigo"]: e for e in K.escenarios()}
    faltan = [c for c in doc if str(doc[c]["correr"]).upper() == "SI" and c not in R]
    est_sol = estados_solucion()
    C.TABLAS.mkdir(parents=True, exist_ok=True)
    salidas = [C.salida(c) for c in R]
    pd.DataFrame([{"escenario": c, "grupo": doc[c]["grupo"], "base": doc[c]["base"], "estado": est_sol.get(c),
                   "datafile_md5": C.md5(C.datafile(c)) if C.datafile(c).exists() else None,
                   "output_md5": C.md5(C.salida(c)) if c in R else None} for c in doc]).to_csv(
        C.TABLAS / "solucion_por_escenario.csv", index=False, encoding="utf-8-sig")
    con_clg, inc_clg, tend_clg = T["con_clg"], T["inc_clg"], T["tendencial_clg"]
    out = {"faltan": faltan, "anios": C.ANIOS, "ventana": C.VENTANA, "estado_solucion": est_sol,
           "corrida": {"salidas": max(_fecha(p) for p in salidas) if salidas else None,
                       "configuracion": _fecha(C.CONFIG), "art6_configuracion": _fecha(C.ART6_CONFIG),
                       "analisis": datetime.datetime.now().strftime("%Y-%m-%dT%H:%M"),
                       "escenarios": list(R)},
           "escenarios": {c: {k: doc[c][k] for k in ("nombre", "grupo", "palancas", "color", "narrativa")}
                          for c in doc},
           "roles": {"inc": inc, "con": con, "inc_clg": inc_clg, "con_clg": con_clg, "tendencial_clg": tend_clg,
                     "ref_estado": T["ref_estado"], "puentes": T["puentes"],
                     "refs": [c for c in T["refs"] if c in R], "escalera": esc,
                     "orden": T["escalera"], "orden_estados": [d["sufijo"] for d in T["estados"]],
                     "base": {c: b for c, b in base.items() if c in R}, "estados": estados,
                     "nombre": {c: T["nombre"][c] for c in R}, "sin_descripcion": [c for c in R if c not in doc]},
           "capas": capas}

    # ------------------------------------------------------------------ emisiones del sector
    em.index.name = "anio"
    em.round(1).to_csv(C.TABLAS / "emisiones_energia_kt.csv", encoding="utf-8-sig")
    out["emisiones_kt"] = {c: [round(x, 1) for x in em[c]] for c in em}

    filas = []
    for c, r in R.items():
        for s, v in C.emisiones_por_subsector_kt(r).items():
            filas += [{"escenario": c, "subsector": s, "anio": a, "kt": round(v[i], 2)}
                      for i, a in enumerate(C.ANIOS)]
    pd.DataFrame(filas).to_csv(C.TABLAS / "emisiones_subsector_kt.csv", index=False, encoding="utf-8-sig")

    # ------------------------------------------------------------------ generacion y capacidad
    gen, cap = [], []
    ernc = {}
    for c, r in R.items():
        g = C.generacion_por_familia_pj(r)
        k = C.capacidad_por_familia_gw(r)
        for f in g:
            gen += [{"escenario": c, "familia": f, "tipo": C.tipo_familia(f), "anio": a,
                     "PJ": round(g[f][i], 4), "GWh": round(g[f][i] * C.PJ_A_GWH, 1)}
                    for i, a in enumerate(C.ANIOS)]
            cap += [{"escenario": c, "familia": f, "tipo": C.tipo_familia(f), "anio": a,
                     "GW": round(k[f][i], 5), "MW": round(k[f][i] * 1000.0, 1)}
                    for i, a in enumerate(C.ANIOS)]
        tot = [sum(g[f][i] for f in g) for i in range(len(C.ANIOS))]
        er = [sum(g[f][i] for f in g if C.tipo_familia(f) == "ernc") for i in range(len(C.ANIOS))]
        ernc[c] = [round(100.0 * er[i] / tot[i], 2) if tot[i] else 0.0 for i in range(len(C.ANIOS))]
    gen, cap = pd.DataFrame(gen), pd.DataFrame(cap)
    gen.to_csv(C.TABLAS / "generacion_familia.csv", index=False, encoding="utf-8-sig")
    cap.to_csv(C.TABLAS / "capacidad_familia.csv", index=False, encoding="utf-8-sig")
    pd.DataFrame(ernc, index=C.ANIOS).rename_axis("anio").to_csv(
        C.TABLAS / "cuota_ernc_pct.csv", encoding="utf-8-sig")
    out["ernc_pct"] = ernc

    def gwh(c, fam, a):
        x = gen[(gen.escenario == c) & (gen.familia == fam) & (gen.anio == a)]["GWh"]
        return float(x.iloc[0]) if len(x) else 0.0

    out["generacion_2035_GWh"] = {c: {f: gwh(c, f, 2035) for f, _, _ in C.FAMILIAS} for c in R}

    desp = termica_desplazable_gwh(R)
    pd.DataFrame(desp, index=C.ANIOS).rename_axis("anio").to_csv(
        C.TABLAS / "termica_desplazable_GWh.csv", encoding="utf-8-sig")
    out["termica_desplazable_GWh"] = desp

    # emisiones de la generacion electrica (componente CO2e_PP) por tipo de planta
    egf, filas = {}, []
    for c, r in R.items():
        d = {}
        for (tec, comp), v in r["emis_tec"].items():
            if comp == "CO2e_PP":
                f = C.familia(tec) or "Otras"
                d[f] = [a + 1000.0 * b for a, b in zip(d.get(f, [0.0] * len(C.ANIOS)), v)]
        egf[c] = {f: [round(x, 2) for x in s] for f, s in d.items()}
        filas += [{"escenario": c, "familia": f, "anio": a, "kt": round(s[i], 2)}
                  for f, s in d.items() for i, a in enumerate(C.ANIOS)]
    pd.DataFrame(filas, columns=["escenario", "familia", "anio", "kt"]).to_csv(
        C.TABLAS / "emisiones_generacion_familia_kt.csv", index=False, encoding="utf-8-sig")
    out["emisiones_generacion_familia_kt"] = egf

    # ------------------------------------------------------------------ volumenes por regla
    def reduccion(ref, esc_):
        if ref not in em or esc_ not in em:
            return None
        return (em[ref] - em[esc_]).loc[V]

    vol = []
    for c in R:
        if c in T["refs"] and c != con:
            continue
        reglas = [("adicional_a_la_NDC", con), ("con_tramo_condicional", inc)]
        # contrafactual del escenario (grupo Contrafactual de Art6_Escenarios): aporte atribuible por retiro
        contra = next((d["miembros"].get(c) for d in T["estados"]
                       if d.get("grupo") == "Contrafactual" and d["miembros"].get(c)), None)
        if contra in em:
            reglas.append(("atribuible_por_retiro", contra))
        # familias que cambian la referencia (FOI: CONA6P, IMP0: CONA6I): reduccion frente a su referencia
        ref_e = next((d["referencia"] for d in T["estados"] if c in d["miembros"].values()), con)
        if ref_e != con and ref_e in em:
            reglas.append(("frente_a_su_referencia", ref_e))
        for regla, ref in reglas:
            d = reduccion(ref, c)
            vol.append({"escenario": c, "regla": regla, "referencia": ref,
                        **{str(a): round(max(0.0, d[a]), 1) for a in V},
                        "total_2031_2035": round(sum(max(0.0, d[a]) for a in V), 1)})
    vol = pd.DataFrame(vol, columns=["escenario", "regla", "referencia"] + [str(a) for a in V] + ["total_2031_2035"])
    vol.to_csv(C.TABLAS / "volumenes_por_regla.csv", index=False, encoding="utf-8-sig")
    out["volumenes"] = vol.to_dict(orient="records")

    def volumen(c, regla):
        x = vol[(vol.escenario == c) & (vol.regla == regla)]["total_2031_2035"]
        return float(x.iloc[0]) if len(x) else 0.0

    descomp = [("Corrección de la base, condicional (NDCCON del Modelo CLG menos CONA6)", con_clg, con),
               ("Corrección de la base, incondicional (NDCINC del Modelo CLG menos INCA6)", inc_clg, inc),
               ("Tramo condicional de la base corregida (INCA6 menos CONA6)", inc, con),
               ("Tramo condicional del Modelo CLG (NDCINC menos NDCCON)", inc_clg, con_clg)] \
        + [(capas[c]["largo"], base[c], c) for c in capa_ok]
    for suf, ref_e in T["ref_estado"].items():
        descomp.append(("Efecto de la referencia del estado %s (%s menos %s)" % (suf, con, ref_e), con, ref_e))
    for d in sens:
        for fam, cod in d["miembros"].items():
            tipo = ("contrafactual" if d.get("grupo") == "Contrafactual" else
                    "sensibilidad de la base" if d["sufijo"] == "GAS" else "riesgo de operación")
            descomp.append(("%s en el %s (%s)" % (d["etiqueta"], fam, tipo), fam, cod))
    dd = []
    for nom, ref, e in descomp:
        d = reduccion(ref, e)
        if d is None:
            continue
        dd.append({"componente": nom, "referencia": ref, "escenario": e,
                   **{str(a): round(d[a], 1) for a in V}, "total_2031_2035": round(d.sum(), 1)})
    dd = pd.DataFrame(dd, columns=["componente", "referencia", "escenario"] + [str(a) for a in V] + ["total_2031_2035"])
    dd.to_csv(C.TABLAS / "descomposicion_reducciones.csv", index=False, encoding="utf-8-sig")
    out["descomposicion"] = dd.to_dict(orient="records")

    # ------------------------------------------------------------------ marco de referencia 2026-2035
    # las transacciones se miden desde 2031 y el análisis se hace en el marco 2026-2035, la
    # vigencia de la Segunda NDC. Las capas, el aporte atribuible y las emisiones se suman también en
    # 2026-2030 y 2026-2035; la oferta, la sobreventa y los ingresos siguen en la ventana de transacciones.
    MC = list(C.MARCO)
    P1 = [a for a in MC if a < V[0]]
    periodos = [("%d_%d" % (P1[0], P1[-1]), P1), ("%d_%d" % (V[0], V[-1]), V), ("%d_%d" % (MC[0], MC[-1]), MC)]

    def _sumas(serie_, pref):
        return {pref + k: round(float(serie_.loc[an].sum()), 1) for k, an in periodos}

    filas_m = [f for f in descomp if not f[0].endswith("(contrafactual)")]   # el atribuible va en positivo abajo
    for c in R:
        contra_m = next((d_["miembros"].get(c) for d_ in T["estados"]
                         if d_.get("grupo") == "Contrafactual" and d_["miembros"].get(c)), None)
        if contra_m in em:
            n_c = str(T["nombre"].get(c, c))
            filas_m.append(("Aporte atribuible por retiro %s%s" % ("de la " if n_c.startswith("NDC") else "del ", n_c),
                            contra_m, c))
    mc = []
    for nom, ref, e in filas_m:
        if ref not in em or e not in em:
            continue
        dm = em[ref] - em[e]
        mc.append({"componente": nom, "referencia": ref, "escenario": e,
                   **{str(a): round(dm[a], 1) for a in MC}, **_sumas(dm, "total_")})
    mc = pd.DataFrame(mc, columns=["componente", "referencia", "escenario"] + [str(a) for a in MC]
                      + ["total_" + k for k, _ in periodos])
    mc.to_csv(C.TABLAS / "marco_2026_2035.csv", index=False, encoding="utf-8-sig")
    ep = pd.DataFrame([{"escenario": c, **_sumas(em[c], "emisiones_"),
                        **_sumas(em[con] - em[c], "reduccion_frente_al_condicional_")} for c in R])
    ep.to_csv(C.TABLAS / "emisiones_por_periodo.csv", index=False, encoding="utf-8-sig")
    out["marco"] = {"anios": MC, "ventana": V, "componentes": mc.to_dict(orient="records"),
                    "emisiones": ep.to_dict(orient="records")}

    # ------------------------------------------------------------------ margen nacional
    nac, H = nacional()
    out["nacional"] = {k: [None if pd.isna(x) else round(x, 1) for x in nac[k]] for k in nac}
    tray_c, tray_p = TRAYECTORIA[str(H["regla_nacional"])], TRAYECTORIA[str(H["regla_prudente"])]
    out["reglas_headroom"] = {"regla_nacional": str(H["regla_nacional"]), "regla_prudente": str(H["regla_prudente"])}
    # inventario observado (Insumos_Art6/INGEI_largo.csv) y calendario de reporte (Art6_Reporte), si existen
    ingei = C.ENERGY / "Insumos_Art6" / "INGEI_largo.csv"
    if ingei.exists():
        inv = pd.read_csv(ingei)
        inv = inv[(inv["anio"] >= 2010) & (inv["gas"] == "Total")]
        def _serie_inv(dim, cod):
            x = inv[(inv["dimension"] == dim) & (inv["codigo"].astype(str) == cod)]
            return {int(a): round(float(v), 2) for a, v in zip(x["anio"], x["valor"])}
        out["inventario"] = {"energia": _serie_inv("sector", "1"),
                             "nacional_con_utcuts": _serie_inv("total", "TOTAL_CON_UTCUTS"),
                             "nacional_sin_utcuts": _serie_inv("total", "TOTAL_SIN_UTCUTS"),
                             "unidad": "kt CO2-eq (AR5)", "archivo": "Insumos_Art6/INGEI_largo.csv"}
        out["inventario"]["ultimo_anio"] = max(out["inventario"]["energia"]) if out["inventario"]["energia"] else None
    try:
        out["reporte"] = [dict(r) for r in K.hoja("Reporte")]
    except Exception:
        out["reporte"] = []
    # dos proyecciones (decision del 11-10-2026): la del Modelo CLG suma a la senda de la meta la
    # diferencia de energia del escenario frente a la referencia corregida (CONA6 o INCA6), sin el puente de la
    # correccion; la corregida la suma frente al escenario del Modelo CLG (NDCCON o NDCINC), con el puente.
    PROY = {"CLG": {"condicional": con, "prudente": inc}, "corregida": {"condicional": con_clg, "prudente": inc_clg}}
    hr_all = []
    anios_h = [a for a in C.ANIOS if a >= int(H["anio_inicio_senda"])]
    for proy, refs_p in PROY.items():
        for c in R:
            for regla, tray in (("condicional", tray_c), ("prudente", tray_p)):
                ref = refs_p[regla]
                if ref not in em:
                    continue
                nac_c = nac[tray] + (em[c] - em[ref])
                h = nac["meta_inc"] - nac_c
                hr_all.append({"proyeccion": proy, "escenario": c, "regla": regla, "referencia": ref,
                               **{str(a): round(h[a], 1) for a in anios_h},
                               "acumulado_2031_2035": round(float(h.loc[V].sum()), 1),
                               "nacional_2035": round(nac_c[2035], 1)})
    hr_all = pd.DataFrame(hr_all)
    hr_all.to_csv(C.TABLAS / "headroom_proyecciones.csv", index=False, encoding="utf-8-sig")
    out["headroom_proyecciones"] = hr_all.to_dict(orient="records")
    # las graficas y la cascada usan la proyeccion del Modelo CLG: no cuenta como margen la correccion metodologica
    hr = hr_all[hr_all.proyeccion == "CLG"].drop(columns=["proyeccion", "referencia", "acumulado_2031_2035"]) \
        .reset_index(drop=True)
    hr.to_csv(C.TABLAS / "headroom_nacional.csv", index=False, encoding="utf-8-sig")
    out["headroom"] = hr.to_dict(orient="records")
    p_inc = 100.0 * float(H["meta_inc_kt"]) / float(nac["base"][int(H["anio_meta"])])
    p_con = 100.0 * float(H["meta_con_kt"]) / float(nac["base"][int(H["anio_meta"])])
    out["metas_2035"] = {"base": round(nac["base"][2035], 1), "meta_inc": round(nac["meta_inc"][2035], 1),
                         "meta_con": round(nac["meta_con"][2035], 1),
                         "incondicional": round(nac["incondicional"][2035], 1),
                         "condicional": round(nac["condicional"][2035], 1),
                         "pct_meta_inc": round(p_inc, 2), "pct_meta_con": round(p_con, 2)}
    pct = lambda v: ("%.0f %%" % v) if abs(v - round(v)) < 0.05 else ("%.1f %%" % v).replace(".", ",")

    def H35(c, regla="condicional"):
        x = hr[(hr.escenario == c) & (hr.regla == regla)]
        return float(x["2035"].iloc[0]) if len(x) else None

    # ------------------------------------------------------------------ peso del sector energia
    # La agregacion nacional del Modelo CLG usa, para el tendencial, el escenario de energia BAU1NDC
    # (tendencial retroactivo sin las iniciativas de la 1.a NDC); para incondicional y
    # condicional, NDCINC y NDCCON. La serie de energia sale del PowerBI del Modelo CLG.
    eo = energia_clg_kt()          # emisiones de energia por escenario del Modelo CLG (PowerBI de ECU_NDC)
    peso = []
    for tray, ser in (("Tendencial", tend_clg), ("Incondicional", inc_clg), ("Condicional", con_clg)):
        col = {"Tendencial": "base", "Incondicional": "incondicional", "Condicional": "condicional"}[tray]
        for a in C.ANIOS:
            tot, ene = float(nac[col][a]), float(eo[ser][a])
            peso.append({"trayectoria": tray, "anio": a, "nacional_kt": round(tot, 1), "energia_kt": round(ene, 1),
                         "otros_sectores_kt": round(tot - ene, 1), "peso_energia_pct": round(100 * ene / tot, 1)})
    peso = pd.DataFrame(peso)
    peso.to_csv(C.TABLAS / "peso_sector_energia.csv", index=False, encoding="utf-8-sig")
    out["peso_energia"] = peso.to_dict(orient="records")

    # ------------------------------------------------------------------ de donde sale el headroom de 2035
    a35 = 2035
    retro = float(eo[tend_clg][a35] - eo[inc_clg][a35])
    tramo_e = float(em[inc][a35] - em[con][a35])
    otros = float((nac["base"][a35] - nac["condicional"][a35]) - (eo[tend_clg][a35] - eo[con_clg][a35]))
    # la agregacion nacional modelada reduce mas de lo que la NDC compromete (7 % + 8 % sobre el tendencial)
    red_mod = float(nac["base"][a35] - nac["condicional"][a35])
    red_pub = float(nac["base"][a35] - nac["meta_con"][a35])
    out["conciliacion_condicional_2035"] = {
        "tendencial": round(float(nac["base"][a35]), 1), "reduccion_incondicional_publicada": float(H["meta_inc_kt"]),
        "reduccion_condicional_publicada": float(H["meta_con_kt"]), "reduccion_publicada": round(red_pub, 1),
        "reduccion_modelada": round(red_mod, 1), "exceso_modelado": round(red_mod - red_pub, 1),
        "tendencial_retroactivo_energia": round(retro, 1), "tramo_condicional_energia": round(tramo_e, 1),
        "otros_sectores": round(otros, 1)}
    if tray_c == "meta_con":
        cascada = [
            ("Reducción del condicional modelado (agregación nacional del Modelo CLG)", red_mod),
            ("Meta incondicional (%s)" % pct(p_inc), -float(H["meta_inc_kt"])),
            ("Reducción modelada que la NDC no compromete", -(red_mod - red_pub)),
        ]
        total = "Margen del condicional comprometido (%s)" % pct(p_con)
    else:
        cascada = [
            ("Tendencial retroactivo en energía (obras de la 1.ª NDC ya en operación)", retro),
            ("Tramo condicional del sector energía", tramo_e),
            ("Otros sectores, de tendencial a condicional", otros),
            ("Meta incondicional (%s)" % pct(p_inc), -float(H["meta_inc_kt"])),
        ]
        total = "Margen del condicional modelado"
    base_hr = sum(v for _, v in cascada)
    cascada.append((total, None))
    for c in capa_ok:
        cascada.append((capas[c]["corto"], float(em[base[c]][a35] - em[c][a35])))
    out["cascada_headroom_2035"] = [{"componente": n, "kt": None if v is None else round(v, 1)} for n, v in cascada]
    out["cascada_headroom_2035_base"] = round(base_hr, 1)

    # ------------------------------------------------------------------ sobreventa
    sv = []
    for s in esc:
        for d in riesgos:
            cr = d["miembros"].get(s)
            if cr is None:
                continue
            fila = {"escenario": s, "riesgo": d["sufijo"]}
            for regla in ("adicional_a_la_NDC", "con_tramo_condicional"):
                vi, vr = volumen(s, regla), volumen(cr, regla)
                fila[regla + "_intacto"] = vi
                fila[regla + "_bajo_riesgo"] = vr
                fila[regla + "_sobreventa"] = round(vi - vr, 1)
            for regla in ("condicional", "prudente"):
                fila["headroom_2035_%s_intacto" % regla] = H35(s, regla)
                fila["headroom_2035_%s_bajo_riesgo" % regla] = H35(cr, regla)
            fila["aumento_emisiones_2035"] = round(em[cr][2035] - em[s][2035], 1)
            sv.append(fila)
    sv = pd.DataFrame(sv)
    sv.to_csv(C.TABLAS / "sobreventa.csv", index=False, encoding="utf-8-sig")
    out["sobreventa"] = sv.to_dict(orient="records")

    # capa del ultimo escalon frente a su base, intacta y bajo cada riesgo
    pb = []
    if capa_ok and base[capa_ok[-1]] in esc:
        top, b0 = capa_ok[-1], base[capa_ok[-1]]
        for suf, a, b in [("intacto", b0, top)] + [(d["sufijo"], d["miembros"].get(b0), d["miembros"].get(top))
                                                   for d in riesgos]:
            if a in em and b in em:
                d = (em[a] - em[b]).loc[V]
                pb.append({"estado": suf, "escenario": top, "base": b0, "total_2031_2035": round(d.sum(), 1),
                           "2035": round(d[2035], 1)})
    out["portafolio_B_bajo_riesgo"] = pb
    pd.DataFrame(pb).to_csv(C.TABLAS / "portafolio_B_bajo_riesgo.csv", index=False, encoding="utf-8-sig")

    # ------------------------------------------------------------------ ITMO por linea
    lineas = []
    for x in ad:
        p, kt = _periodo(x), _kt(x)
        anios = [a for a in V if p and p[0] <= a <= p[1]] if kt is not None else []
        lineas.append({"codigo": x["codigo"], "linea": x["linea"], "escenario_art6": x["escenario_art6"],
                       "adicionalidad": x["adicionalidad"], "kt_anio_declarado": x.get("kt_anio_declarado"),
                       "anios_en_ventana": len(anios),
                       "volumen_declarado_2031_2035": round(kt * len(anios), 1) if anios else None,
                       "volumen_modelo_2031_2035": None,
                       "en_reserva": str(x["codigo"]) in LINEAS_EN_RESERVA,
                       "motivo_reserva": LINEAS_EN_RESERVA.get(str(x["codigo"]))})
    lineas = pd.DataFrame(lineas)
    lineas.to_csv(C.TABLAS / "itmos_por_linea.csv", index=False, encoding="utf-8-sig")
    out["itmos_por_linea"] = lineas.astype(object).where(lineas.notna(), None).to_dict(orient="records")

    # decision 1 del 13-10-2026: las lineas en reserva salen de la oferta y se informan aparte
    reservada = lambda x: str(x["codigo"]) in LINEAS_EN_RESERVA
    firmes = [x for x in ad if x.get("adicionalidad") == "Firme" and _kt(x) is not None and not reservada(x)]
    condicionadas = [x for x in ad if x.get("adicionalidad") == "Por demostrar" and _kt(x) is not None
                     and x.get("veredicto_compradores") == "Condicionada" and not reservada(x)]
    en_reserva = [x for x in ad if reservada(x) and _kt(x) is not None]
    sin_adic = [x for x in ad if x.get("adicionalidad") == "Sin adicionalidad" and _kt(x) is not None
                and not reservada(x)]
    # el firme declarado de una linea del tramo condicional se vende de ese tramo: se rotula asi y se suma
    # aparte de las capas, que miden solo lo que el escenario agrega sobre su base
    tramo_firme = {str(x.get("escenario_NDC")) for x in firmes}
    rot_firme = ", tramo condicional" if tramo_firme == {"Condicional"} else ""
    nombres = lambda xs: C.enumerar([str(x["linea"]) for x in xs])
    out["grupos_de_lineas"] = {k: [x["codigo"] for x in xs] for k, xs in
                               (("firme", firmes), ("condicionadas_declaradas", condicionadas),
                                ("sin_adicionalidad", sin_adic), ("condicionadas_en_reserva", en_reserva))}
    rotulo_reserva = "En reserva, fuera de la oferta: %s (declarado)" % nombres(en_reserva) if en_reserva else None

    # ------------------------------------------------------------------ ingresos por oferta
    def vol_declarado(xs):
        return round(sum(_declarado(xs, a) for a in V), 1)

    firme_kt = vol_declarado(firmes)
    oferta = []
    if firmes:
        ndc_f = {str(x.get("escenario_NDC")) for x in firmes}
        oferta.append({"clave": "firme", "oferta": "Firme: %s (declarado%s)" % (nombres(firmes), rot_firme), "kt_2031_2035": firme_kt,
                       "nota": "%s con adicionalidad firme%s" % (
                           "única línea" if len(firmes) == 1 else "%d líneas" % len(firmes),
                           "; vende tramo condicional" if ndc_f == {"Condicional"} else "")})
    if capa_ok:
        c0 = capa_ok[0]
        oferta.append({"clave": "firme_capa", "oferta": "Firme más la capa del %s por demostrar (modelo)" % c0,
                       "kt_2031_2035": round(firme_kt + volumen(c0, "adicional_a_la_NDC"), 1)
                       if base[c0] == con else round(firme_kt + float(dd[dd.escenario == c0]["total_2031_2035"].sum()), 1),
                       "nota": "agrega la reducción que el modelo atribuye a las palancas del %s" % c0})
    for c in capa_ok[1:]:
        oferta.append({"clave": "capa:" + c,
                       "oferta": ("Paquete fuera de la NDC, %s sobre %s (modelo)" % (c, base[c])) if capas[c]["fuera_ndc"]
                       else "%s (modelo)" % capas[c]["corto"],
                       "kt_2031_2035": round(float(dd[dd.escenario == c]["total_2031_2035"].sum()), 1),
                       "nota": ("no consume ninguna meta; " if capas[c]["fuera_ndc"] else "") + "adicionalidad por demostrar"})
    if condicionadas:
        oferta.append({"clave": "declarado", "oferta": "Condicionadas por demostrar (declarado)",
                       "kt_2031_2035": vol_declarado(condicionadas),
                       "nota": "potencial declarado en el Plan de Implementación de la Segunda NDC"
                               + ("; sin %s, en reserva" % C.enumerar([x["codigo"] for x in en_reserva])
                                  if en_reserva else "")})
    if en_reserva:                    # informativa: no es oferta (decision 1 del 13-10-2026); las graficas la omiten
        oferta.append({"clave": "en_reserva", "oferta": rotulo_reserva, "kt_2031_2035": vol_declarado(en_reserva),
                       "nota": "fuera de la oferta: " + "; ".join("%s, %s" % (x["codigo"], LINEAS_EN_RESERVA[str(x["codigo"])])
                                                                for x in en_reserva)})
    if esc:
        oferta.append({"clave": "maximo", "oferta": "Máximo teórico con tramo condicional (%s contra %s)" % (esc[0], inc),
                       "kt_2031_2035": volumen(esc[0], "con_tramo_condicional"),
                       "nota": ("incluye %s, sin adicionalidad: " % nombres(sin_adic) if sin_adic else "")
                       + "no es oferta vendible"})
    P = {p["escenario_precio"]: float(p["usd_por_t"]) for p in K.hoja("Precios")}
    for o in oferta:
        for nombre, precio in P.items():
            o["MUSD_" + nombre] = round(o["kt_2031_2035"] * 1000.0 * precio / 1e6, 1)
    oferta = pd.DataFrame(oferta)
    oferta.to_csv(C.TABLAS / "ingresos_por_oferta.csv", index=False, encoding="utf-8-sig")
    out["ingresos"] = {"precios": P, "oferta": oferta.to_dict(orient="records")}

    # ------------------------------------------------------------------ potencial de Articulo 6
    # Oferta anual por nivel de adicionalidad y cuanto de ella se puede transferir sin superar la
    # meta incondicional: con ajuste correspondiente, lo transferido en el ano t se suma a las
    # emisiones del pais, asi que el limite es el headroom H_t del escenario que el pais ejecuta, el
    # ultimo escalon de la escalera que trae la corrida.
    bloques = []
    if firmes:
        bloques.append(("Firme: %s (declarado%s)" % (nombres(firmes), rot_firme), "firme", "firme",
                        lambda a, xs=firmes: _declarado(xs, a)))
    capa_bloques = [(capas[c]["bloque"], capas[c]["nivel"], "capa:" + c,
                     lambda a, b=base[c], c=c: max(0.0, em[b][a] - em[c][a])) for c in capa_ok]
    bloques += capa_bloques[:1]
    if condicionadas:
        bloques.append(("Por demostrar: condicionadas con potencial declarado (declarado)", "por demostrar",
                        "declarado", lambda a, xs=condicionadas: _declarado(xs, a)))
    # la oferta se decide antes del riesgo: se mide siempre con el sistema intacto. Bajo riesgo el
    # paquete del ultimo escalon reduce mas, pero esas reducciones reponen el cumplimiento, no se venden
    bloques += capa_bloques[1:]
    no_vendible = [("Sin adicionalidad: %s (declarado)" % nombres(sin_adic), lambda a, xs=sin_adic: _declarado(xs, a))] \
        if sin_adic else []
    if en_reserva:                    # se informa junto a la oferta, sin sumarse a ella
        no_vendible.append((rotulo_reserva, lambda a, xs=en_reserva: _declarado(xs, a)))
    top = esc[-1] if esc else None

    def potencial_y_sobreventa(hr_p, aut_fijo=None):
        """Oferta, transferible sin incumplir y sobreventa del escenario que el pais ejecuta (top), intacto y bajo
        cada riesgo, con las dos reglas, para un juego de margenes (una proyeccion). aut_fijo: lo autorizado {anio: kt};
        sin el, lo transferible con el sistema intacto y la regla de AUTORIZACION en estos margenes.

        Convencion de redondeo (correccion del 13-10-2026 tras la verificacion independiente del paso 15): se suma sin
        redondear y se redondea el total. Lo autorizado por anio queda sin redondear (aut_); las listas por anio del JSON
        llevan un decimal solo para mostrar. Asi la sobreventa nunca supera lo autorizado ni lo autorizado la oferta."""
        pot_, anual_, exacto_ = [], [], {}
        if top is not None:
            for suf, etiqueta in [("", "Intacto")] + [("-" + d["sufijo"], d["etiqueta"]) for d in riesgos]:
                ejecuta = top if not suf else next((d["miembros"].get(top) for d in riesgos
                                                    if "-" + d["sufijo"] == suf), None)
                if ejecuta is None:
                    continue
                for regla in ("condicional", "prudente"):
                    h = hr_p[(hr_p.escenario == ejecuta) & (hr_p.regla == regla)]
                    if h.empty:
                        continue
                    fila = {"estado": etiqueta, "sufijo": suf, "escenario": ejecuta, "regla": regla}
                    oferta_t = {a: 0.0 for a in V}
                    for nom, nivel, clave, f in bloques:
                        v = {a: f(a) for a in V}
                        fila[nom] = round(sum(v.values()), 1)
                        for a in V:
                            oferta_t[a] += v[a]
                    for nom, f in no_vendible:
                        fila[nom] = round(sum(f(a) for a in V), 1)
                    transf_t = {a: min(oferta_t[a], max(0.0, float(h[str(a)].iloc[0]))) for a in V}
                    fila["oferta_total"] = round(sum(oferta_t.values()), 1)
                    fila["transferible_sin_incumplir"] = round(sum(transf_t.values()), 1)
                    fila["headroom_acumulado_2031_2035"] = round(sum(float(h[str(a)].iloc[0]) for a in V), 1)
                    pot_.append(fila)
                    anual_.append({"estado": etiqueta, "sufijo": suf, "escenario": ejecuta, "regla": regla,
                                   "oferta": {str(a): round(oferta_t[a], 1) for a in V},
                                   "transferible": {str(a): round(transf_t[a], 1) for a in V}})
                    exacto_[(suf, regla)] = {str(a): transf_t[a] for a in V}
        # sobreventa: se autoriza lo transferible con el sistema intacto (proyeccion del Modelo CLG y regla prudente,
        # decision 2 del 13-10-2026) y despues ocurre el riesgo; con ajuste correspondiente, lo transferido se suma a
        # las emisiones nacionales. Lo autorizado va sin redondear (convencion de redondeo, arriba)
        aut_ = dict(aut_fijo) if aut_fijo is not None else dict(exacto_.get(("", AUTORIZACION[1]), {}))
        sobre_ = []
        for x in anual_:
            h = hr_p[(hr_p.escenario == x["escenario"]) & (hr_p.regla == x["regla"])].iloc[0]
            # sobreventa: lo transferido que no cabe en el margen; incumplimiento: lo que el pais ya
            # excede su meta sin vender nada
            exceso = {a: max(0.0, aut_.get(str(a), 0.0) - max(0.0, float(h[str(a)]))) for a in V}
            incump = {a: max(0.0, -float(h[str(a)])) for a in V}
            sobre_.append({"estado": x["estado"], "sufijo": x["sufijo"], "escenario": x["escenario"],
                           "regla": x["regla"], "autorizado_2031_2035": round(sum(aut_.values()), 1),
                           "sobreventa_2031_2035": round(sum(exceso.values()), 1),
                           "incumplimiento_sin_transferir_2031_2035": round(sum(incump.values()), 1),
                           "sobreventa_anual": {str(a): round(exceso[a], 1) for a in V}})
        return pd.DataFrame(pot_), anual_, aut_, sobre_

    hr_corr = hr_all[hr_all.proyeccion == "corregida"]
    hr_por = {"CLG": hr, "corregida": hr_corr}
    # lo autorizado se fija una vez, con la lectura de AUTORIZACION, y se evalua contra los margenes de las cuatro
    _, anual_aut, aut, _ = potencial_y_sobreventa(hr_por[AUTORIZACION[0]])
    pot, anual, _, sobre = potencial_y_sobreventa(hr, aut)
    pot_c, anual_c, aut_c, sobre_c = potencial_y_sobreventa(hr_corr, aut)
    # lo transferible con el sistema intacto en cada lectura, para mostrar si la autorizacion cambiaria con otra
    autorizado_por_lectura = {"%s_%s" % (pr, x["regla"]): x["transferible"]
                              for pr, an in (("CLG", anual), ("corregida", anual_c)) for x in an if x["sufijo"] == ""}
    pd.concat([pot.assign(proyeccion="CLG"), pot_c.assign(proyeccion="corregida")]).to_csv(
        C.TABLAS / "potencial_articulo6.csv", index=False, encoding="utf-8-sig")
    pd.DataFrame([dict({k: v for k, v in s_.items() if k != "sobreventa_anual"}, proyeccion=pr)
                  for pr, ss in (("CLG", sobre), ("corregida", sobre_c)) for s_ in ss]).to_csv(
        C.TABLAS / "sobreventa_por_riesgo.csv", index=False, encoding="utf-8-sig")
    # lo autorizado por anio va al JSON con cuatro decimales (sumable sin arrastrar el redondeo) y su total redondeado
    aut4 = lambda d: {k: round(v, 4) for k, v in d.items()}
    out["potencial_art6_corregida"] = {"tabla": pot_c.to_dict(orient="records"), "anual": anual_c,
                                       "autorizado_intacto": aut4(aut_c),
                                       "autorizado_intacto_2031_2035": round(sum(aut_c.values()), 1),
                                       "sobreventa": sobre_c}
    regla_aut = ("lo transferible con el sistema intacto en la proyección del Modelo CLG y la regla %s (decisión del "
                 "%s), sin las líneas en reserva" % (AUTORIZACION[1], FECHA_DECISIONES))
    out["potencial_art6"] = {"tabla": pot.to_dict(orient="records"), "anual": anual,
                             "autorizado_intacto": aut4(aut), "autorizado_intacto_2031_2035": round(sum(aut.values()), 1),
                             "convencion_de_redondeo": "Se suma sin redondear y se redondea el total. Las "
                                                       "cifras por año se muestran con un "
                                                       "decimal y su suma puede diferir del total en 0,1 kt.",
                             "sobreventa": sobre, "ejecuta": top,
                             "bloques": [(n, nivel, clave) for n, nivel, clave, _ in bloques],
                             "no_vendible": [n for n, _ in no_vendible],
                             "en_reserva": {"bloque": rotulo_reserva, "lineas": [x["codigo"] for x in en_reserva],
                                            "kt_2031_2035": vol_declarado(en_reserva) if en_reserva else 0.0,
                                            "motivo": {str(x["codigo"]): LINEAS_EN_RESERVA[str(x["codigo"])]
                                                       for x in en_reserva}},
                             "regla_de_autorizacion": regla_aut, "lectura_de_autorizacion": list(AUTORIZACION),
                             "autorizado_por_lectura": autorizado_por_lectura}

    # ------------------------------------------------------------------ capas por estado
    # capa de cada escalon frente a su base dentro del mismo estado: el primer escalon frente a la referencia del
    # estado (CONA6, o CONA6P y CONA6I en las familias que cambian la referencia), los demas frente al escalon previo
    MCa = list(C.MARCO)
    cpe = []
    for d in [{"sufijo": "", "etiqueta": "Intacto", "grupo": "Intacto", "referencia": con,
               "miembros": {c: c for c in esc}}] + [x for x in estados if x["grupo"] != "Contrafactual"]:
        for c in esc:
            e_ = d["miembros"].get(c)
            b_ = d["referencia"] if base.get(c) == con else d["miembros"].get(base.get(c))
            if e_ not in em or b_ not in em:
                continue
            dm = em[b_] - em[e_]
            if base.get(c) != con:
                mide = "capa frente al escalón previo en el mismo estado"
            elif d["sufijo"] and d["referencia"] == con:
                mide = "escenario en el estado frente a %s intacto: incluye el efecto del estado (no es capa)" % con
            else:
                mide = "capa frente a la referencia del estado"
            cpe.append({"estado": d["etiqueta"], "sufijo": d["sufijo"], "grupo": d["grupo"], "capa": c,
                        "escenario": e_, "base": b_, "mide": mide, **{str(a): round(dm[a], 1) for a in MCa},
                        "total_2026_2030": round(float(dm.loc[[a for a in MCa if a < 2031]].sum()), 1),
                        "total_2031_2035": round(float(dm.loc[V].sum()), 1),
                        "total_2026_2035": round(float(dm.loc[MCa].sum()), 1)})
    cpe = pd.DataFrame(cpe)
    cpe.to_csv(C.TABLAS / "capas_por_estado.csv", index=False, encoding="utf-8-sig")
    out["capas_por_estado"] = cpe.to_dict(orient="records")

    # ------------------------------------------------------------------ factor del MWh desplazado
    # por capa y anio: cambio de emisiones de la generacion (CO2e_PP) entre el cambio de generacion termica fosil
    def _pp_kt(c):
        return pd.Series([sum(1000.0 * v[i] for (t_, comp), v in R[c]["emis_tec"].items() if comp == "CO2e_PP")
                          for i in range(len(C.ANIOS))], index=C.ANIOS)

    def _termica_gwh(c):
        g = C.generacion_por_familia_pj(R[c])
        return pd.Series([sum(g[f][i] for f in g if C.tipo_familia(f) == "termica") * C.PJ_A_GWH
                          for i in range(len(C.ANIOS))], index=C.ANIOS)
    fmd = []
    pares = [(base[c], c) for c in capa_ok] + [(base[c], c) for c in []]
    for fam_, cod_v in T["puentes"].items():
        b_v = con if base.get(fam_) == con else T["puentes"].get(base.get(fam_))
        if b_v in R and cod_v in R:
            pares.append((b_v, cod_v))
    for b_, e_ in pares:
        dpp, dter, dtot = _pp_kt(b_) - _pp_kt(e_), _termica_gwh(b_) - _termica_gwh(e_), em[b_] - em[e_]
        for a in MCa:
            fmd.append({"base": b_, "escenario": e_, "anio": a, "reduccion_CO2e_PP_kt": round(dpp[a], 1),
                        "reduccion_energia_kt": round(dtot[a], 1), "termica_desplazada_GWh": round(dter[a], 1),
                        "factor_t_por_MWh": round(dpp[a] / dter[a], 4) if abs(dter[a]) > 1.0 else None})
    fmd = pd.DataFrame(fmd)
    fmd.to_csv(C.TABLAS / "factor_mwh_desplazado.csv", index=False, encoding="utf-8-sig")
    out["factor_mwh_desplazado"] = fmd.astype(object).where(fmd.notna(), None).to_dict(orient="records")

    # ------------------------------------------------------------------ suficiencia
    # con el tope K15b activo el LP cubre la falta de potencia pasando energia por STOELE (paso sin perdidas que evita
    # las de ELE_TRANS): su actividad en 2026-2035 y los anios con la termica de la red en su tope son la senal de que
    # el escenario no tiene potencia suficiente y de que sus emisiones quedan subestimadas
    topes = C.leer_ecuinput(["TotalAnnualMaxCapacity"], list(R))
    topes = topes[topes["Technology"].isin(["PPFOI", "PPDSL", "PPNGS"])].groupby(
        ["Strategy", "Technology", "Year"])["TotalAnnualMaxCapacity"].max()
    suf = []
    for c, r in R.items():
        sto = r["actividad"].get("STOELE", [0.0] * len(C.ANIOS))
        for a in MCa:
            i = C.IDX[a]
            fila = {"escenario": c, "anio": a, "STOELE_GWh": round(sto[i] * C.PJ_A_GWH, 1)}
            en_tope = []
            for t in ("PPFOI", "PPDSL", "PPNGS"):
                cap = r["capacidad"].get(t, [0.0] * len(C.ANIOS))[i]
                tope = topes.get((c, t, a))
                fila["%s_MW" % t] = round(cap * 1000.0, 1)
                fila["%s_tope_MW" % t] = None if tope is None or pd.isna(tope) or tope >= 9999 else round(tope * 1000.0, 1)
                if fila["%s_tope_MW" % t] is not None and cap * 1000.0 >= fila["%s_tope_MW" % t] - 0.05:
                    en_tope.append(t)
            fila["en_tope"] = ",".join(en_tope)
            suf.append(fila)
    suf = pd.DataFrame(suf)
    suf.to_csv(C.TABLAS / "suficiencia_por_escenario.csv", index=False, encoding="utf-8-sig")
    out["suficiencia"] = {c: {"STOELE_GWh_2026_2035": round(float(suf[suf.escenario == c]["STOELE_GWh"].sum()), 1),
                              "anios_con_STOELE": [int(a) for a in suf[(suf.escenario == c) & (suf.STOELE_GWh > 0.5)]["anio"]],
                              "anios_en_tope": [int(a) for a in suf[(suf.escenario == c) & (suf.en_tope != "")]["anio"]]}
                          for c in R}

    # ------------------------------------------------------------------ riesgo con la variante de potencia minima
    # diagnostico (Art6_calibracion/suficiencia_escenarios_art6.py, fuera de B1): emisiones de los escenarios sin
    # solucion o con STOELE cuando el modelo puede construir la potencia que le falta; margen y sobreventa de los
    # estados del escalon que ejecuta el pais con esas emisiones
    rv_ruta = C.ENERGY / "Art6_calibracion" / "calibracion_h_suficiencia_escenarios_art6.csv"
    rv = []
    try:
        vh = pd.read_csv(rv_ruta) if rv_ruta.exists() else pd.DataFrame()
    except pd.errors.EmptyDataError:            # sin escenarios sin solucion ni con STOELE: la variante no se corre
        vh = pd.DataFrame()
    if len(vh):
        auts = {"CLG": aut, "corregida": aut_c}
        refs_h = {("CLG", "condicional"): (con, tray_c), ("CLG", "prudente"): (inc, tray_p),
                  ("corregida", "condicional"): (con_clg, tray_c), ("corregida", "prudente"): (inc_clg, tray_p)}
        for esc_v in sorted(vh.escenario.unique()):
            x = vh[vh.escenario == esc_v].set_index("anio")
            fam = esc_v.split("-")[0]
            var = pd.Series(em[fam].to_numpy(copy=True), index=C.ANIOS, dtype=float)   # copia: no tocar em
            for a in x.index:
                var[a] = float(x.loc[a, "energia_variante_kt"])
            fila = {"escenario": esc_v, "estado_B1": x["estado_B1"].iloc[0],
                    "faltante_max_MW": float(x["faltante_MW"].max()),
                    "anios_con_faltante": ",".join(str(a) for a in x.index if x.loc[a, "faltante_MW"] > 0.5),
                    "emisiones_B1_2031_2035": round(float(em[esc_v].loc[V].sum()), 1) if esc_v in em else None,
                    "emisiones_variante_2031_2035": round(float(var.loc[V].sum()), 1),
                    "aumento_frente_al_intacto_2031_2035": round(float((var - em[fam]).loc[V].sum()), 1)}
            if fam == top:
                for (proy, regla), (r_, tray) in refs_h.items():
                    h = nac["meta_inc"] - (nac[tray] + (var - em[r_]))
                    fila["margen_2035_%s_%s" % (proy, regla)] = round(float(h[2035]), 1)
                    fila["sobreventa_2031_2035_%s_%s" % (proy, regla)] = round(
                        sum(max(0.0, auts[proy].get(str(a), 0.0) - max(0.0, float(h[a]))) for a in V), 1)
            rv.append(fila)
    rv = pd.DataFrame(rv)
    rv.to_csv(C.TABLAS / "riesgo_variante_potencia_minima.csv", index=False, encoding="utf-8-sig")
    out["riesgo_variante_potencia_minima"] = rv.to_dict(orient="records")

    # ------------------------------------------------------------------ tablas del 13-10-2026
    out.update(tablas_13_10(R, em, T, doc, base, capa_ok, bloques, V, MCa, hr, hr_corr, anual, anual_c, aut, aut_c,
                            en_reserva))
    # decisiones del 13-10-2026: sobreventa por metodo y subconjunto, reserva por anada y autorizable
    # ex post
    out.update(decisiones_13_10(em, T, bloques, en_reserva, capa_ok, base, V, MCa, hr_all, riesgos, top, aut))

    # ------------------------------------------------------------------ puentes V7 frente a los escenarios nuevos
    # capa del sandbox (sobre NDCCON, 08-10-2026), capa V7 (las mismas palancas sobre CONA6) y capa nueva:
    # efecto de la base = V7 - sandbox; efecto de las decisiones nuevas = nueva - V7
    sb_tab = C.ENERGY / "Art6_calibracion" / "version_2026-10-08" / "B2_Output_Art6" / "tablas"   # sandbox del 08-10
    sb_dd = pd.read_csv(sb_tab / "descomposicion_reducciones.csv") if (sb_tab / "descomposicion_reducciones.csv").exists() \
        else pd.DataFrame(columns=["escenario", "total_2031_2035", "2035"])
    sb_em = pd.read_csv(sb_tab / "emisiones_energia_kt.csv", index_col=0) if (sb_tab / "emisiones_energia_kt.csv").exists() \
        else pd.DataFrame()
    pv = []
    for c in esc:
        cv = T["puentes"].get(c)
        if cv not in em:
            continue
        b_n, b_v = base[c], (con if base[c] == con else T["puentes"].get(base[c]))
        if b_v not in em:
            continue
        capa_n, capa_v = (em[b_n] - em[c]).loc[V], (em[b_v] - em[cv]).loc[V]
        x = sb_dd[sb_dd.escenario == c]
        capa_sb = float(x["total_2031_2035"].iloc[0]) if len(x) else None
        capa_sb35 = float(x["2035"].iloc[0]) if len(x) else None
        em_sb = float(sb_em.loc[2031:2035, c].sum()) if c in sb_em else None
        pv.append({"familia": c, "base_nueva": b_n, "puente": cv, "base_puente": b_v,
                   "capa_sandbox_2031_2035": capa_sb, "capa_V7_2031_2035": round(float(capa_v.sum()), 1),
                   "capa_nueva_2031_2035": round(float(capa_n.sum()), 1),
                   "efecto_base_2031_2035": None if capa_sb is None else round(float(capa_v.sum()) - capa_sb, 1),
                   "efecto_decisiones_2031_2035": round(float(capa_n.sum() - capa_v.sum()), 1),
                   "capa_sandbox_2035": capa_sb35, "capa_V7_2035": round(float(capa_v[2035]), 1),
                   "capa_nueva_2035": round(float(capa_n[2035]), 1),
                   "emisiones_sandbox_2031_2035": None if em_sb is None else round(em_sb, 1),
                   "emisiones_V7_2031_2035": round(float(em[cv].loc[V].sum()), 1),
                   "emisiones_nueva_2031_2035": round(float(em[c].loc[V].sum()), 1)})
    pv = pd.DataFrame(pv)
    pv.to_csv(C.TABLAS / "puente_v7.csv", index=False, encoding="utf-8-sig")
    out["puente_v7"] = pv.to_dict(orient="records")

    # geotermia y biomasa: el piso funciona
    out["geo_bio_GWh"] = {c: {a: {"Geotermia": gwh(c, "Geotermia", a),
                                  "Biomasa y biogás": gwh(c, "Biomasa y biogás", a)}
                              for a in V} for c in R}

    io.open(JSON, "w", encoding="utf-8").write(json.dumps(out, ensure_ascii=False, indent=1, default=float))
    # archivo unico de cifras para la redaccion del Producto 3 (con el md5 de cada _Output.csv)
    import cifras_producto3
    cifras_producto3.escribir(out, C.md5(JSON), SENSIBILIDAD_PISOS_CLG)
    if not resumen:
        return out

    # ------------------------------------------------------------------ resumen en consola
    f0 = lambda v: "{:,.0f}".format(v).replace(",", " ")
    print("  Emisiones del sector energía 2035 (kt CO2e):")
    for c in R:
        print("    %-15s %8s   ERNC %5.1f %%" % (c, f0(em[c][2035]), ernc[c][-1]))
    print("  Descomposición 2031-2035 (kt):")
    for r in out["descomposicion"]:
        print("    %-52s %8s" % (r["componente"], f0(r["total_2031_2035"])))
    print("  Margen 2035 (regla base / regla prudente):")
    for c in R:
        if c in T["refs"] and c != con:
            continue
        print("    %-15s %8s / %8s" % (c, f0(H35(c)), f0(H35(c, "prudente"))))
    dec = out.get("decisiones_13_10") or {}
    if dec:
        print("  Decisiones del %s: autorización con %s %s; líneas en reserva %s"
              % (dec["fecha"], AUTORIZACION[0], AUTORIZACION[1], ", ".join(dec["lineas_en_reserva"]) or "ninguna"))
        for s in dec["subconjuntos"]:
            print("    %-22s oferta %8s  autorizado %8s" % (s["clave"], f0(s["oferta_2031_2035"]),
                                                            f0(s["autorizado_2031_2035"])))
        print("  Sobreventa, lectura de autorización (anual / promedio), por subconjunto:")
        sv_ = [x for x in out["sobreventa_metodo_subconjunto"] if x["lectura_de_autorizacion"]]
        for s in dec["subconjuntos"]:
            for suf in [""] + [d["sufijo"] for d in riesgos]:
                a_ = next((x for x in sv_ if x["subconjunto"] == s["clave"] and x["sufijo"] == suf
                           and x["metodo"] == "anual"), None)
                p_ = next((x for x in sv_ if x["subconjunto"] == s["clave"] and x["sufijo"] == suf
                           and x["metodo"] == "promedio"), None)
                if a_ and p_ and (a_["sobreventa_kt"] > 0.05 or p_["sobreventa_kt"] > 0.05 or suf in ESTADOS_REFERENCIA):
                    print("    %-22s %-14s %8s / %8s" % (s["clave"], suf or "intacto", f0(a_["sobreventa_kt"]),
                                                         f0(p_["sobreventa_kt"])))
    if faltan:
        print("  faltan corridas:", faltan)
    if out["roles"]["sin_descripcion"]:
        print("  escenarios sin descripción en Art6_Escenarios:", out["roles"]["sin_descripcion"])
    return out


if __name__ == "__main__":
    main()
