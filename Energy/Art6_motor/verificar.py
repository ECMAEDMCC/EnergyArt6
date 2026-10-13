# -*- coding: utf-8 -*-
"""Verifica los escenarios del Articulo 6 que B1 genero desde B1_Scenario_Config.xlsx (ECU_NDC, rama
art6-escenarios). Corre en B3, despues de B1; informa cada falla en la terminal y en verificacion.txt.

1. B1 genero el datafile de cada escenario activo de Art6_Escenarios.
2. Configuracion. Cada escenario basado tiene la base que dice la hoja Scenarios (la de Art6_Roles para A, B y C);
   copia las filas de su base en Electrical, SmartGrid y Efficiency, salvo las que reemplazan sus palancas; trae
   exactamente las palancas de su composicion (Art6_Escenarios), y una misma palanca se define igual en todos sus
   escenarios.
3. Datafile. Cada escenario difiere de su base solo en las filas de sus palancas, y una misma palanca produce la misma
   fila en todos sus escenarios.
4. Historia. Ninguna fila cambia en 2010-2025 frente a la base, salvo las excepciones declaradas en Art6_Palancas
   (redondeo de la hoja Efficiency y retiro de la inversion solar de 2025 en el contrafactual); se informa el maximo.
5. Ningun piso de actividad supera a su techo.
6. Riesgos hidrologicos: en cada clase, factor de planta, piso y techo son los de la base por la razon de Art6_AnoSeco
   en los anios del estado (ANOSECO desde 2026; ANOSEC3 en 2026, 2029, 2032 y 2035; ANOSECM por 0,908 desde 2026) e
   iguales en los demas. ACT y ACTDEM, anclados a 2026: por el factor de 2026 de Art6_ACT2026 en 2026 y por la razon de
   Art6_AnoSeco en 2029, 2032 y 2035.
7. contabilidad() corre despues del analisis: lineas en reserva fuera de la oferta, autorizacion con el Modelo CLG y la
   regla prudente, sobreventa por metodo y subconjunto, reserva por anada, autorizable ex post y archivo de cifras
   (decisiones del 13-10-2026). Su seccion se agrega a verificacion.txt.
La familia GAS se construye sobre CONA6G (su referencia de estado en Art6_Roles, que es una referencia de B1): su base
esperada es CONA6G y no CONA6.

Escribe B2_Output_Art6/verificacion.txt.
"""
import io

import comun as C
import configuracion as K

LOW = "TotalTechnologyAnnualActivityLowerLimit"
UPP = "TotalTechnologyAnnualActivityUpperLimit"
SECOS3 = (2026, 2029, 2032, 2035)
MODERADO = 0.908
# filas cuya historia (2010-2025) puede cambiar, con su motivo
HISTORIA_PERMITIDA = {
    ("SpecifiedAnnualDemand", None): "la hoja Efficiency de B1 redondea a 4 decimales todo el vector (C-EI y C-EM)",
    ("TotalAnnualMinCapacityInvestment", "PPPVT"): "el contrafactual retira la inversion solar de 2025 (SIN5)",
}


def _firma(fila):
    return tuple(sorted((k, str(v)) for k, v in fila.items()))


def main():
    rep, errores = [], 0

    def linea(ok, texto):
        nonlocal errores
        rep.append(("OK     " if ok else "ERROR  ") + texto)
        errores += 0 if ok else 1

    E = [e for e in K.escenarios() if e["correr"] == "SI"]
    P = K.palancas()
    roles = K.roles_fijos()
    con = roles["con"]
    clave_de = {p["id"]: (p["parametro"], str(p["clave"])) for p in P}
    for e in E:
        linea(C.datafile(e["codigo"]).exists(), "B1 generó %s" % e["codigo"])
    if errores:
        return _cerrar(rep, errores)

    datos = {}

    def dat(cod):
        if cod not in datos:
            datos[cod] = C.leer_datafile(C.datafile(cod))
        return datos[cod]

    definicion, fila_dato = {}, {}
    es_b1 = {x["codigo"] for x in E if x["base"] == "B1"}
    for e in E:
        if e["base"] == "B1":
            continue
        cod, base = e["codigo"], e["base"]
        # la base es CONA6, salvo en las familias cuya referencia de estado es a su vez una referencia de B1 (GAS sobre
        # CONA6G): esas se construyen sobre su referencia
        suf = cod.split("-", 1)[1] if "-" in cod else ""
        ref_e = roles.get("ref_estado:" + suf)
        esperada = ref_e if ref_e in es_b1 else con
        if base != esperada:
            linea(False, "%s: se esperaba Based_On = %s y la hoja Scenarios dice %s" % (cod, esperada, base))
            continue
        esperadas = K.esperadas(e, P)
        tiene = K.palancas_en(cod)
        ok = set(tiene) == set(esperadas.values())
        linea(ok, "%s: trae las %d palancas de su composición (%s)%s"
              % (cod, len(esperadas), e["palancas"], "" if ok else "; sobran %s, faltan %s"
                 % (sorted(set(tiene) - set(esperadas.values())), sorted(set(esperadas.values()) - set(tiene)))))
        ef_pal = {k: r for k, r in tiene.items() if r.get("_hoja") == "Efficiency"}
        tocadas = {(r["Parameter"], str(r["Tech_Set"])) for k, r in tiene.items() if k not in ef_pal}
        copia = [r for r in K.filas_de("Electrical", cod) if r not in tiene.values()]
        ref = [r for r in K.filas_de("Electrical", base) if (r["Parameter"], str(r["Tech_Set"])) not in tocadas]
        linea(sorted(map(_firma, copia)) == sorted(map(_firma, ref)),
              "%s: Electrical copia las %d filas de %s que sus palancas no reemplazan" % (cod, len(ref), base))
        a, b = K.filas_de("SmartGrid", cod), K.filas_de("SmartGrid", base)
        linea(sorted(map(_firma, a)) == sorted(map(_firma, b)),
              "%s: SmartGrid copia las %d filas de %s" % (cod, len(b), base))
        toc_ef = {(r["Parameter"], str(r["Set"])) for r in ef_pal.values()}
        a = [r for r in K.filas_de("Efficiency", cod) if not str(r.get("Description_Set") or "").startswith("[")]
        b = [r for r in K.filas_de("Efficiency", base) if (r["Parameter"], str(r["Set"])) not in toc_ef]
        linea(sorted(map(_firma, a)) == sorted(map(_firma, b)),
              "%s: Efficiency copia las %d filas de %s que sus palancas no reemplazan" % (cod, len(b), base))
        for pid, r in tiene.items():
            definicion.setdefault(pid, {})[cod] = _firma({k: v for k, v in r.items() if k != "_hoja"})

        ls = dat(cod)
        declaradas = {clave_de[pid] for pid in tiene if pid in clave_de}
        dif = C.diferencias(dat(base), ls)
        extra = {(d[0], d[1]) for d in dif} - declaradas
        linea(not extra, "%s: el datafile difiere de %s en %d filas, todas de sus palancas%s"
              % (cod, base, len(dif), "" if not extra else "; ajenas: %s" % sorted(extra)[:5]))
        hist = []
        for par, cl, anios in dif:
            if anios == "solo en uno":
                continue
            h = [a for a in anios if a <= 2025]
            if h:
                hist.append((par, cl, h))
        no_perm = [x for x in hist if (x[0], None) not in HISTORIA_PERMITIDA
                   and (x[0], x[1].split(",")[0]) not in HISTORIA_PERMITIDA]
        T, Tb = C.tabla(ls), C.tabla(dat(base))
        dmax = max([max(abs(T[(p_, c_)][1][C.IDX[a]] - Tb[(p_, c_)][1][C.IDX[a]]) for a in h) for p_, c_, h in hist]
                   or [0.0])
        linea(not no_perm, "%s: historia 2010-2025 igual a %s%s%s"
              % (cod, base, "" if not hist else " salvo %d filas permitidas (máx. %.6g)" % (len(hist), dmax),
                 "" if not no_perm else "; cambian sin permiso: %s" % [(p_, c_) for p_, c_, _ in no_perm][:5]))
        for pid in tiene:
            if pid in clave_de and clave_de[pid] in T:
                fila_dato.setdefault(pid, {})[cod] = T[clave_de[pid]][1]
        malos = []
        for (par, cl), (_, v) in T.items():
            if par == LOW and (UPP, cl) in T:
                techo = T[(UPP, cl)][1]
                malos += [(cl, C.ANIOS[i]) for i in range(len(C.ANIOS)) if v[i] > techo[i] + 1e-9]
        linea(not malos, "%s: pisos de actividad bajo sus techos%s" % (cod, "" if not malos else ": %s" % malos[:5]))

    for pid in sorted(definicion):
        d = definicion[pid]
        linea(len(set(d.values())) == 1, "palanca %s: misma definición en sus %d escenarios" % (pid, len(d)))
        v = list(fila_dato.get(pid, {}).values())
        iguales = all(max(abs(a - b) for a, b in zip(v[0], x)) < 1e-9 for x in v[1:]) if v else False
        linea(iguales, "palanca %s: misma fila en el datafile de sus %d escenarios" % (pid, len(v)))

    # riesgos hidrologicos: cociente frente a la base por la razon de Art6_AnoSeco en los anios del estado. ACT y ACTDEM
    # (anclados a 2026): en 2026 el factor de Art6_ACT2026 de la clase; en 2029, 2032 y 2035 la razon de Art6_AnoSeco
    razon = K.anoseco()
    f26 = K.act2026()
    Tb = C.tabla(dat(con))
    for e in E:
        cod = e["codigo"]
        suf = cod.split("-", 1)[1] if "-" in cod else ""
        if suf not in ("ANOSECO", "ANOSEC3", "ANOSECM", "CCOFFANOSECO", "ACT", "ACTDEM"):
            continue
        es_act = suf in ("ACT", "ACTDEM")
        if es_act and set(f26) != set(razon):
            linea(False, "%s: Art6_ACT2026 no trae el factor de 2026 de las %d clases" % (cod, len(razon)))
            continue
        T = C.tabla(dat(cod))
        malos = []
        for clase, rz in razon.items():
            if suf == "CCOFFANOSECO" and clase == "PPHRORAB":
                continue
            for par, cl in (("CapacityFactor", clase + ",All"), (LOW, clase), (UPP, clase)):
                if (par, cl) not in Tb or (par, cl) not in T:
                    malos.append((clase, par, "sin fila"))
                    continue
                b, v = Tb[(par, cl)][1], T[(par, cl)][1]
                for i, a in enumerate(C.ANIOS):
                    if es_act:
                        factor = f26[clase] if a == 2026 else (rz if a in SECOS3 else None)
                    else:
                        seco = a >= 2026 and (suf != "ANOSEC3" or a in SECOS3)
                        factor = (MODERADO if suf == "ANOSECM" else rz) if seco else None
                    if factor is None:
                        fuera = abs(v[i] - b[i]) > 1e-9 * max(1.0, abs(b[i]))
                    else:
                        # B1 redondea a 4 decimales: tolerancia relativa de 2e-3 o la del redondeo
                        fuera = b[i] > 1e-6 and abs(v[i] - b[i] * factor) > max(2e-3 * b[i] * factor, 6e-5)
                    if fuera:
                        malos.append((clase, par, a))
                        break
        linea(bool(razon) and not malos,
              "%s: cada clase hidroeléctrica es la de %s por %s%s"
              % (cod, con, "su factor de 2026 (Art6_ACT2026) y su razón de Art6_AnoSeco en 2029, 2032 y 2035" if es_act
                 else "su razón de Art6_AnoSeco en los años del estado", "" if not malos else ": %s" % malos[:4]))
    return _cerrar(rep, errores)


def contabilidad():
    """Comprobaciones de la contabilidad del Articulo 6 con las decisiones del 13-10-2026. Corre despues del
    analisis (B3, paso 9) y recalcula cada cifra desde las tablas de B2_Output_Art6/tablas y la hoja Art6_Adicionalidad,
    sin usar el codigo de analizar.py:

    1. Las lineas en reserva (EN32) quedan fuera de la oferta: la oferta central es la suma de sus bloques, sin ellas, y la
       oferta con ellas la supera exactamente en su potencial declarado.
    2. Lo autorizado es lo transferible con el sistema intacto en la proyeccion del Modelo CLG y la regla prudente, igual en
       las cuatro lecturas de sobreventa_por_riesgo.csv.
    3. Oferta de cada subconjunto desde las emisiones de cada escenario y las lineas declaradas; subconjuntos anidados.
    4. Sobreventa con la regla anual y con el metodo de promedio (ajuste de 2035 = suma transferida / 10) recalculada desde
       headroom_proyecciones.csv; monotona en el subconjunto.
    5. Reserva por anada: autorizable = min(oferta, max(0, margen)); su suma es lo transferible sin incumplir del estado.
    6. Autorizable ex post = min(reduccion del estado, max(0, margen)); con el sistema intacto, igual a lo autorizado.
    7. cifras_finales_producto3.json: cada cifra con valor, unidad, archivo, escenario y md5; cada md5 igual al del
       _Output.csv vigente (o, en la sensibilidad con los pisos del Modelo CLG, al de la carpeta guardada que cita) y cada
       archivo citado existe.
    8. Convencion de redondeo (13-10-2026): se suma sin redondear y se redondea el total; la sobreventa nunca supera lo
       autorizado ni lo autorizado la oferta, y el autorizado central es el mismo en todas las tablas.
    9. Respaldo: la demanda D de las horas de corte es todo el uso final de E3ELE (E5*ELE mas T4ELE_HEA). Estado ACT:
       participacion termica del modelo y observada con el mismo perimetro (importacion en el denominador).
    Agrega su seccion a verificacion.txt."""
    import json
    import pandas as pd
    rep, errores = [], 0

    def linea(ok, texto):
        nonlocal errores
        rep.append(("OK     " if ok else "ERROR  ") + texto)
        errores += 0 if ok else 1

    TB = C.TABLAS
    J = json.load(io.open(C.RESULTADOS / "resultados_art6.json", encoding="utf-8"))
    dec = J.get("decisiones_13_10")
    if not dec:
        linea(False, "resultados_art6.json no trae decisiones_13_10")
        return _anexar(rep, errores)
    V = list(C.VENTANA)
    N = len(C.MARCO)
    tol = 0.15
    pa = J["potencial_art6"]
    T = J["roles"]
    top = pa["ejecuta"]
    em = pd.read_csv(TB / "emisiones_energia_kt.csv", index_col=0)
    em.columns = [str(c) for c in em.columns]
    hr = pd.read_csv(TB / "headroom_proyecciones.csv")

    def margen(proy, esc, regla):
        h = hr[(hr.proyeccion == proy) & (hr.escenario == esc) & (hr.regla == regla)]
        return None if h.empty else {a: float(h.iloc[0][str(a)]) for a in C.MARCO}

    # 1. lineas en reserva fuera de la oferta
    ad = {str(x["codigo"]): x for x in K.hoja("Adicionalidad")}
    res = list(dec["lineas_en_reserva"])
    import re as _re

    def declarado(cods, a):
        tot = 0.0
        for c in cods:
            x = ad[c]
            m = _re.match(r"\s*(\d{4})\s*-\s*(\d{4})", str(x.get("periodo") or ""))
            if m and int(m.group(1)) <= a <= int(m.group(2)) and isinstance(x.get("kt_anio_declarado"), (int, float)):
                tot += float(x["kt_anio_declarado"])
        return tot
    kt_res = sum(declarado(res, a) for a in V)
    grupos = J["grupos_de_lineas"]
    linea(not set(res) & set(grupos["condicionadas_declaradas"]) and set(res) == set(grupos["condicionadas_en_reserva"]),
          "líneas en reserva (%s) fuera de las condicionadas declaradas de la oferta" % ", ".join(res))
    pot = pd.read_csv(TB / "potencial_articulo6.csv")
    fila = pot[(pot.proyeccion == "CLG") & (pot.sufijo.fillna("") == "") & (pot.regla == "prudente")].iloc[0]
    suma_bloques = sum(float(fila[n]) for n, _, _ in pa["bloques"])
    linea(abs(suma_bloques - float(fila["oferta_total"])) <= 0.3 and pa["en_reserva"]["bloque"] in pot.columns
          and pa["en_reserva"]["bloque"] not in [n for n, _, _ in pa["bloques"]],
          "oferta central %.1f kt = suma de sus bloques (%.1f); la línea en reserva va en columna aparte (%.1f kt)"
          % (float(fila["oferta_total"]), suma_bloques, float(fila[pa["en_reserva"]["bloque"]])))
    niv = pd.read_csv(TB / "oferta_tres_niveles.csv")
    linea(set(niv.nivel) == {"central", "con_pisos_CLG_12_10", "sensibilidad_sin_gas_capa_1"}
          and not niv[niv.nivel == "sensibilidad_sin_gas_capa_1"].es_nivel_de_oferta.any(),
          "niveles rotulados por caso (central, con pisos del Modelo CLG, sensibilidad sin gas de la capa 1, que no es "
          "nivel de oferta)")
    for nivel in ("central", "con_pisos_CLG_12_10", "sensibilidad_sin_gas_capa_1"):
        s_ = niv[(niv.nivel == nivel) & niv.lineas_en_reserva.str.startswith("excluidas")]
        c_ = niv[(niv.nivel == nivel) & niv.lineas_en_reserva.str.startswith("incluidas")]
        ok = len(s_) == 1 and len(c_) == 1 and abs(float(c_.kt_2031_2035.iloc[0]) - float(s_.kt_2031_2035.iloc[0])
                                                    - kt_res) <= 0.15
        linea(ok, "oferta %s: con %s (%.1f) menos sin %s (%.1f) = %.1f kt declarados"
              % (nivel, ", ".join(res), float(c_.kt_2031_2035.iloc[0]) if len(c_) else float("nan"), ", ".join(res),
                 float(s_.kt_2031_2035.iloc[0]) if len(s_) else float("nan"), kt_res))
    cen = niv[(niv.nivel == "central") & niv.lineas_en_reserva.str.startswith("excluidas")]
    linea(len(cen) == 1 and abs(float(cen.kt_2031_2035.iloc[0]) - float(fila["oferta_total"])) <= 0.15,
          "la oferta central de oferta_tres_niveles.csv es la de potencial_articulo6.csv")

    # 2. autorizacion con el Modelo CLG y la regla prudente
    m_aut = margen("CLG", top, "prudente")
    sub = {s["clave"]: s for s in dec["subconjuntos"]}
    central = dec["subconjunto_central"]
    aut = {int(a): float(v) for a, v in pa["autorizado_intacto"].items()}
    ok = all(abs(aut[a] - min(sub[central]["oferta"][str(a)], max(0.0, m_aut[a]))) <= 0.06 for a in V)
    linea(ok, "autorizado = min(oferta, max(0, margen CLG prudente del %s intacto)) en cada año: %.1f kt"
          % (top, sum(aut.values())))
    spr = pd.read_csv(TB / "sobreventa_por_riesgo.csv")
    linea(bool(len(spr)) and (spr.autorizado_2031_2035 - sum(aut.values())).abs().max() <= 0.15,
          "sobreventa_por_riesgo.csv usa ese autorizado en las %d filas (dos proyecciones y dos reglas)" % len(spr))

    # 3. oferta de cada subconjunto desde las emisiones y las lineas declaradas
    def capa(b, c, a):
        return max(0.0, float(em.loc[a, b]) - float(em.loc[a, c]))
    base = T["base"]
    comp = {"firme": lambda a: declarado(grupos["firme"], a),
            "declarado": lambda a: declarado(grupos["condicionadas_declaradas"], a)}
    for c in T["escalera"]:
        comp["capa:" + c] = (lambda a, b=base[c], c=c: capa(b, c, a))
    for s in dec["subconjuntos"]:
        rec = {a: sum(comp[k](a) for k in s["bloques"]) + (declarado(res, a) if s["incluye_reserva"] else 0.0) for a in V}
        d = max(abs(rec[a] - s["oferta"][str(a)]) for a in V)
        linea(d <= 0.35, "oferta de %s recalculada desde emisiones_energia_kt.csv y Art6_Adicionalidad: %.1f kt "
                         "(diferencia máxima %.2f kt por redondeo)" % (s["clave"], sum(rec.values()), d))
    orden = [k for k in ("solo_firme", "lista_blanca", central) if k in sub] + [k for k in sub if k.startswith("toda")]
    ok = all(sub[x]["oferta"][str(a)] <= sub[y]["oferta"][str(a)] + 0.05 for x, y in zip(orden, orden[1:]) for a in V)
    linea(ok, "subconjuntos anidados en cada año: %s" % " ⊂ ".join(orden))

    # 4. sobreventa por metodo y subconjunto
    sv = pd.read_csv(TB / "sobreventa_por_metodo_y_subconjunto.csv")
    malos, n = [], 0
    for _, r in sv.iterrows():
        m = margen(r.proyeccion, r.escenario, r.regla)
        au = {a: float(sub[r.subconjunto]["autorizado"][str(a)]) for a in V}
        if r.metodo == "anual":
            esperado = sum(max(0.0, au[a] - max(0.0, m[a])) for a in V)
            ajuste = au[2035]
        else:
            ajuste = sum(au.values()) / N
            esperado = max(0.0, ajuste - max(0.0, m[2035]))
        n += 1
        if abs(esperado - float(r.sobreventa_kt)) > tol or abs(ajuste - float(r.ajuste_2035)) > 0.06:
            malos.append((r.subconjunto, r.metodo, r.proyeccion, r.regla, r.escenario))
    linea(not malos and n > 0, "sobreventa recalculada desde headroom_proyecciones.csv en %d filas (regla anual y método "
                               "de promedio con ajuste de 2035 = autorizado / %d)%s"
          % (n, N, "" if not malos else ": difieren %s" % malos[:4]))
    malos = []
    for (est, proy, regla, met), g in sv.groupby(["escenario", "proyeccion", "regla", "metodo"]):
        v = {r.subconjunto: float(r.sobreventa_kt) for r in g.itertuples()}
        if any(v.get(x, 0.0) > v.get(y, 0.0) + 0.05 for x, y in zip(orden, orden[1:])):
            malos.append((est, proy, regla, met))
    linea(not malos, "la sobreventa no crece al pasar a un subconjunto menor%s" % ("" if not malos else ": %s" % malos[:4]))
    linea(set(sv.metodo) == {"anual", "promedio"} and len(set(zip(sv.proyeccion, sv.regla))) == 4
          and set(sv.subconjunto) == set(sub),
          "la matriz trae los dos métodos, las cuatro lecturas y los %d subconjuntos" % len(sub))
    # convencion de redondeo (13-10-2026): se suma sin redondear y se redondea el total, de modo que la sobreventa nunca
    # supera lo autorizado ni lo autorizado la oferta, y el autorizado central es el mismo en todas las tablas
    malos = [(r.subconjunto, r.metodo, r.escenario) for r in sv.itertuples()
             if not (r.sobreventa_kt <= r.autorizado_2031_2035 <= r.oferta_2031_2035)]
    malos += [("sobreventa_por_riesgo", r.escenario, r.regla) for r in spr.itertuples()
              if not r.sobreventa_2031_2035 <= r.autorizado_2031_2035]
    sp1 = pd.read_csv(TB / "sobreventa_primer_anio_negativo.csv")
    malos += [("primer_anio", r.escenario, r.regla) for r in sp1.itertuples()
              if not r.sobreventa_2031_2035 <= r.autorizado_2031_2035]
    totales_aut = {round(float(pa["autorizado_intacto_2031_2035"]), 1), round(float(sub[central]["autorizado_2031_2035"]), 1)} \
        | {round(float(v), 1) for v in spr.autorizado_2031_2035} \
        | {round(float(v), 1) for v in sv[sv.subconjunto == central].autorizado_2031_2035}
    linea(not malos and len(totales_aut) == 1,
          "redondeo: sobreventa <= autorizado <= oferta en las %d filas de la matriz y en las tablas de sobreventa por "
          "riesgo; autorizado central único (%s kt)%s"
          % (len(sv), ", ".join("%.1f" % v for v in sorted(totales_aut)), "" if not malos else ": %s" % malos[:4]))

    # 5. reserva por anada
    rv = pd.read_csv(TB / "reserva_por_aniada.csv", dtype={"anio": str})
    malos = []
    for _, r in rv[rv.anio.str.len() == 4].iterrows():
        m = margen("CLG", r.escenario, "prudente")[int(r.anio)]
        # la reserva se redondea desde los valores exactos (convencion del 13-10-2026): frente a la resta de dos valores
        # ya redondeados puede diferir en 0,1
        if abs(float(r.autorizable_kt) - min(float(r.oferta_kt), max(0.0, m))) > 0.06 \
                or abs(float(r.reserva_kt) - (float(r.oferta_kt) - float(r.autorizable_kt))) > 0.11:
            malos.append((r.subconjunto, r.escenario, r.anio))
    linea(not malos, "reserva por añada: autorizable = min(oferta, max(0, margen CLG prudente)) y reserva = oferta - "
                     "autorizable en %d filas%s" % (int((rv.anio.str.len() == 4).sum()), "" if not malos else ": %s" % malos[:4]))
    tot = rv[(rv.subconjunto == central) & (rv.anio.str.len() > 4)]
    pp = pot[(pot.proyeccion == "CLG") & (pot.regla == "prudente")].set_index("escenario")
    malos = [(r.escenario, float(r.autorizable_kt), float(pp.loc[r.escenario, "transferible_sin_incumplir"]))
             for r in tot.itertuples() if r.escenario in pp.index
             and abs(float(r.autorizable_kt) - float(pp.loc[r.escenario, "transferible_sin_incumplir"])) > 0.35]
    linea(not malos and len(tot) > 0, "reserva por añada: lo autorizable 2031-2035 de cada estado es su transferible sin "
                                      "incumplir (potencial_articulo6.csv) en %d estados%s"
          % (len(tot), "" if not malos else ": %s" % malos[:3]))
    refs = set(rv[rv.estado_de_referencia].sufijo.dropna())
    linea({"ACT", "ACTDEM", "CCSOLO"} <= refs, "ACT, ACTDEM y CCSOLO marcados como estados de referencia de la reserva")

    # 6. autorizable ex post: valor central con tope en la oferta de la anada; sin tope, informativo (decision del 13-10-2026)
    ep = pd.read_csv(TB / "autorizable_ex_post.csv", dtype={"anio": str})
    cols_c = [c for c in ep.columns if c in ("firme_kt", "condicionadas_kt") or (c.startswith("capa_") and c.endswith("_kt"))]
    malos = []
    for _, r in ep.iterrows():
        red = sum(float(r[c]) for c in cols_c if pd.notna(r[c]))
        sin_tope = min(float(r.reduccion_estado_kt), max(0.0, float(r.margen_kt)))
        if abs(red - float(r.reduccion_estado_kt)) > 0.3 \
                or abs(float(r.autorizable_ex_post_sin_tope_kt) - sin_tope) > 0.06 \
                or abs(float(r.autorizable_ex_post_kt) - min(sin_tope, float(r.oferta_aniada_kt))) > 0.11:
            malos.append((r.subconjunto, r.escenario, r.proyeccion, r.regla, r.anio))
    linea(not malos and len(ep) > 0, "autorizable ex post = min(reducción del estado, max(0, margen), oferta de la añada) y "
                                     "sin tope = min(reducción, max(0, margen)) en %d filas%s"
          % (len(ep), "" if not malos else ": %s" % malos[:4]))
    linea((ep.autorizable_ex_post_kt <= ep.oferta_aniada_kt + 0.05).all(),
          "el autorizable ex post central nunca supera la oferta de su añada")
    i0 = ep[(ep.subconjunto == central) & (ep.sufijo.fillna("") == "")]
    linea(len(i0) > 0 and (i0.autorizable_ex_post_kt - i0.autorizado_ex_ante_kt).abs().max() <= 0.15,
          "con el sistema intacto lo autorizable ex post es lo autorizado ex ante")
    # capa del ultimo escalon en cada estado, recalculada desde las emisiones
    ult = T["escalera"][-1]
    col_u = "capa_%s_kt" % ult
    malos = []
    for _, r in ep[(ep.subconjunto == central) & (ep.proyeccion == "CLG") & (ep.regla == "prudente")].iterrows():
        suf = r.sufijo if isinstance(r.sufijo, str) else ""
        e_ = ult + ("-" + suf if suf else "")
        b_ = base[ult] + ("-" + suf if suf else "")
        if e_ in em.columns and b_ in em.columns and abs(capa(b_, e_, int(r.anio)) - float(r[col_u])) > 0.15:
            malos.append((e_, r.anio))
    linea(not malos, "capa del %s en cada estado = emisiones del escalón previo menos las del %s en el mismo estado%s"
          % (ult, ult, "" if not malos else ": %s" % malos[:4]))

    # 7. archivo de cifras
    p = C.RESULTADOS / "cifras_finales_producto3.json"
    if not p.exists():
        linea(False, "falta cifras_finales_producto3.json")
        return _anexar(rep, errores)
    F = json.load(io.open(p, encoding="utf-8"))
    cif = F.get("cifras") or []
    faltan = [c.get("id") for c in cif if any(k not in c for k in ("valor", "unidad", "archivo", "escenario", "output_md5"))]
    linea(bool(cif) and not faltan, "cifras_finales_producto3.json: %d cifras con valor, unidad, archivo, escenario y md5%s"
          % (len(cif), "" if not faltan else "; incompletas: %s" % faltan[:4]))
    vigentes, malos = {}, []
    for c in cif:
        for e, m5 in (c.get("output_md5") or {}).items():
            if c.get("tema") == "oferta_tres_niveles" and "pisos_CLG" in str(c.get("escenario")):
                continue                                   # salidas de la sensibilidad guardada: se comprueban abajo
            if e not in vigentes:
                vigentes[e] = C.md5(C.salida(e)) if C.salida(e).exists() else None
            if m5 != vigentes[e]:
                malos.append((c["id"], e))
    linea(not malos, "cada md5 de las cifras es el del _Output.csv vigente (%d escenarios)%s"
          % (len(vigentes), "" if not malos else ": %s" % malos[:4]))
    # sensibilidad con los pisos del Modelo CLG: ruta de la carpeta guardada y md5 de cada _Output.csv que cita
    raiz = C.RAIZ
    sens = [c for c in cif if c.get("tema") == "oferta_tres_niveles" and "pisos_CLG" in str(c.get("escenario"))]
    malos = []
    for c in sens:
        arch = c.get("archivos_salida") or {}
        if not c.get("ruta_salidas") or set(arch) != set(c.get("output_md5") or {}):
            malos.append((c["id"], "sin ruta_salidas o archivos_salida"))
            continue
        for e, ruta in arch.items():
            f = raiz / ruta
            if not f.exists() or C.md5(f) != c["output_md5"][e]:
                malos.append((c["id"], e))
    linea(bool(sens) and not malos, "oferta con pisos del Modelo CLG: %d cifras citan %s y el md5 de cada _Output.csv "
                                    "coincide (%s)%s"
          % (len(sens), sens[0].get("ruta_salidas") if sens else "-",
             ", ".join("%s %s" % (e, m[:8]) for e, m in (sens[0].get("output_md5") or {}).items()) if sens else "-",
             "" if not malos else ": difieren %s" % malos[:4]))
    # cada archivo citado existe (rutas relativas a B2_Output_Art6)
    citados = {c["archivo"] for c in cif} | {c["archivo_precio"] for c in cif if c.get("archivo_precio")}
    faltan = sorted(a for a in citados if not (C.RESULTADOS / a).exists())
    linea(not faltan, "los %d archivos citados en «archivo» existen (rutas relativas a B2_Output_Art6)%s"
          % (len(citados), "" if not faltan else "; no son rutas: %s" % faltan[:3]))
    temas = {c["tema"] for c in cif}
    pedidos = {"capas", "oferta_tres_niveles", "aporte_atribuible", "margen_2035", "sobreventa", "primer_anio_negativo",
               "respaldo", "rango_gas", "factor_desplazado", "termica_desplazable_2035", "ernc", "ingresos",
               "reserva_por_aniada", "autorizable_ex_post"}
    linea(pedidos <= temas, "cifras_finales_producto3.json trae los temas pedidos%s"
          % ("" if pedidos <= temas else "; faltan %s" % sorted(pedidos - temas)))
    # rango del gas: puentes recalculados desde las emisiones por escenario
    malos = []
    for c in cif:
        if c["tema"] == "rango_gas" and c["id"].startswith("puente_"):
            e_, r_ = c["escenario"], c["referencia"]
            v = float(sum(em.loc[a, e_] - em.loc[a, r_] for a in V))
            if c["valor"] is None or abs(v - float(c["valor"])) > 0.35:
                malos.append((c["id"], c["valor"], round(v, 1)))
    linea(not malos, "rango del gas: puentes de la base recalculados desde emisiones_energia_kt.csv%s"
          % ("" if not malos else ": %s" % malos))
    # respaldo (correccion del 13-10-2026): ENS = R x eta_T x eta_D; horas = 24 x ENS / D, 8.760 x ENS / D y, en 6 meses
    # de estiaje, el doble de las diarias; eta leidas del datafile de cada escenario
    rs = pd.read_csv(TB / "respaldo_por_escenario.csv")
    x = rs[rs.demanda_electrica_final_GWh > 0]
    malos, eta = [], {}
    for r in x.itertuples():
        if r.escenario not in eta:
            Tx = C.tabla(C.leer_datafile(C.datafile(r.escenario)))
            eta[r.escenario] = [Tx[("OutputActivityRatio", "ELE_TRANS,E2ELE,1")][1],
                                Tx[("InputActivityRatio", "ELE_TRANS,E1ELE,1")][1],
                                Tx[("OutputActivityRatio", "ELE_DIST,E3ELE,1")][1],
                                Tx[("InputActivityRatio", "ELE_DIST,E2ELE,1")][1]]
        i = C.IDX[int(r.anio)]
        ot, it, od, id_ = (v[i] for v in eta[r.escenario])
        et, ed = ot / it, od / id_
        ens = r.respaldo_GWh * et * ed
        d = r.demanda_electrica_final_GWh
        if abs(r.ENS_equivalente_GWh - ens) > 0.1 + 1e-3 * ens or abs(r.horas_corte_equivalentes_por_dia - 24 * ens / d) > 0.011 \
                or abs(r.horas_corte_equivalentes_por_anio - 8760 * ens / d) > 0.11 \
                or abs(r.horas_corte_por_dia_estiaje_6_meses - 48 * ens / d) > 0.011 \
                or abs(r.eta_transmision - et) > 1e-5 or abs(r.eta_distribucion - ed) > 1e-5:
            malos.append((r.escenario, int(r.anio)))
    linea(not malos and len(x) > 0, "respaldo: ENS = R x eta_T x eta_D (eficiencias del datafile) y horas 24 x ENS / D, "
                                    "8.760 x ENS / D y 48 x ENS / D recalculadas en %d filas%s"
          % (len(x), "" if not malos else ": difieren %s" % malos[:4]))
    con_r = x[x.horas_corte_equivalentes_por_dia >= 0.5]        # con menos, el redondeo a 0,01 h domina la razón
    linea(len(con_r) == 0 or ((con_r.horas_formula_anterior_24RD_por_dia / con_r.horas_corte_equivalentes_por_dia
                               - 1.0 / (con_r.eta_transmision * con_r.eta_distribucion)).abs() <= 0.02).all(),
          "respaldo: la fórmula anterior (24 x R / D) excede a la corregida en 1 / (eta_T x eta_D) en %d años con al "
          "menos 0,5 h de corte equivalente" % len(con_r))
    # D es todo el uso final de E3ELE del _Output.csv: los E5*ELE mas T4ELE_HEA (correccion del 13-10-2026)
    malos = []
    for esc_r in x.escenario.unique():
        o_ = pd.read_csv(C.salida(esc_r), usecols=["Fuel", "Year", "UseByTechnology"], low_memory=False)
        uso = o_[(o_.Fuel == "E3ELE") & o_.UseByTechnology.notna()].groupby("Year").UseByTechnology.sum()
        for r in x[x.escenario == esc_r].itertuples():
            u = float(uso.get(int(r.anio), 0.0)) * C.PJ_A_GWH
            if abs(u - r.demanda_electrica_final_GWh) > 0.15 \
                    or abs(r.demanda_E5ELE_GWh + r.uso_E3ELE_T4ELE_HEA_GWh - r.demanda_electrica_final_GWh) > 0.11:
                malos.append((esc_r, int(r.anio), round(u, 1), r.demanda_electrica_final_GWh))
    linea(not malos and len(x) > 0, "respaldo: la demanda D de las horas es todo el uso final de E3ELE del _Output.csv "
                                    "(E5*ELE más T4ELE_HEA) en %d filas%s"
          % (len(x), "" if not malos else ": difieren %s" % malos[:4]))
    # estado ACT anclado a 2026: demanda e importacion de 2026 iguales a lo observado (A y B; C lleva ademas su demanda)
    ac = pd.read_csv(TB / "act_2026_contraste.csv")
    obs = {str(f["clave"]): f["valor"] for f in K.hoja("ACT2026_Datos") if f.get("clave")}
    g26 = 100.0 * (float(obs["crecimiento_demanda_2026"]) - 1.0)
    imp26 = float(obs["importacion_2026_antes_07_09_GWh"])
    x = ac[(ac.anio == 2026) & ac.escenario.str.contains("-ACT")]
    ab = x[x.escenario.str[0].isin(["A", "B"])]
    linea(len(x) == 6 and (ab.crecimiento_demanda_pct - g26).abs().max() <= 0.02
          and (x.importacion_GWh - imp26).abs().max() <= 0.5,
          "ACT y ACT-DEM: demanda eléctrica de 2026 con el crecimiento observado (%.2f %% en A y B) e importación de 2026 "
          "igual a la anterior al 07-09-2026 (%.1f GWh) en %d escenarios" % (g26, imp26, len(x)))
    # mismo perimetro en el modelo y en lo observado (correccion del 13-10-2026): la participacion termica del modelo es
    # termica / (hidro + termica + ERNC + importacion) y la observada lleva la importacion en el denominador
    tot_m = ac.hidro_GWh + ac.termica_SNI_GWh + ac.ERNC_GWh + ac.importacion_GWh
    ok_m = ((100.0 * ac.termica_SNI_GWh / tot_m - ac.participacion_termica_SNI_pct).abs() <= 0.01).all()
    o25, o26 = float(obs["termica_participacion_2025"]), float(obs["termica_participacion_ene_ago_2026"])
    s25, s26 = float(obs["termica_participacion_2025_sin_importacion"]), \
        float(obs["termica_participacion_ene_ago_2026_sin_importacion"])
    ok_o = all(abs(r.participacion_termica_observada_pct - round(100.0 * {2025: o25, 2026: o26}[r.anio], 2)) <= 1e-6
               and abs(r.diferencia_termica_modelo_menos_observado_pp
                       - (r.participacion_termica_SNI_pct - r.participacion_termica_observada_pct)) <= 0.011
               for r in ac[ac.anio.isin([2025, 2026])].itertuples())
    ok_i = o25 < s25 and o26 < s26                 # con la importacion en el denominador la fraccion es menor
    linea(ok_m and ok_o and ok_i and ac[ac.anio == 2027].participacion_termica_observada_pct.isna().all(),
          "ACT: participación térmica del modelo = térmica / (hidro + térmica + ERNC + importación) en %d filas y "
          "observada con el mismo perímetro: %.2f %% en 2025 y %.2f %% en enero a agosto de 2026 (sin importación, "
          "%.2f %% y %.2f %%, solo trazabilidad)" % (len(ac), 100.0 * o25, 100.0 * o26, 100.0 * s25, 100.0 * s26))
    md5_json = C.md5(C.RESULTADOS / "resultados_art6.json")
    linea(F.get("resultados_art6_json_md5") == md5_json, "el archivo de cifras corresponde a resultados_art6.json %s"
          % md5_json[:8])
    return _anexar(rep, errores)


def _anexar(rep, errores):
    """Agrega la seccion de contabilidad a verificacion.txt y la informa en la terminal."""
    rep = ["", "Contabilidad del Artículo 6 con las decisiones del 13-10-2026 (después del análisis)"] + rep
    rep.append("")
    rep.append("Resultado de la contabilidad: %d errores" % errores)
    C.RESULTADOS.mkdir(parents=True, exist_ok=True)
    with io.open(C.RESULTADOS / "verificacion.txt", "a", encoding="utf-8") as f:
        f.write("\n".join(rep) + "\n")
    for r in rep:
        if r.startswith("ERROR"):
            print("  " + r)
    print("  contabilidad: %d comprobaciones OK, %d errores (detalle en B2_Output_Art6/verificacion.txt)"
          % (sum(1 for r in rep if r.startswith("OK")), errores))
    return errores == 0


def _cerrar(rep, errores):
    rep.append("")
    rep.append("Resultado: %d errores" % errores)
    C.RESULTADOS.mkdir(parents=True, exist_ok=True)
    io.open(C.RESULTADOS / "verificacion.txt", "w", encoding="utf-8").write("\n".join(rep) + "\n")
    for r in rep:
        if r.startswith("ERROR"):
            print("  " + r)
    print("  %d comprobaciones OK, %d errores (detalle en B2_Output_Art6/verificacion.txt)"
          % (sum(1 for r in rep if r.startswith("OK")), errores))
    return errores == 0


if __name__ == "__main__":
    import sys
    if "--contabilidad" in sys.argv:
        raise SystemExit(0 if contabilidad() else 1)
    raise SystemExit(0 if main() else 1)
