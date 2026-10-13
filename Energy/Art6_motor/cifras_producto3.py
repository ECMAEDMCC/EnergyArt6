# -*- coding: utf-8 -*-
"""Archivo unico de cifras para la redaccion del Producto 3: B2_Output_Art6/cifras_finales_producto3.json.

Lo escribe analizar.main() despues de resultados_art6.json, con las mismas cifras (nada se recalcula aqui salvo sumas y
cocientes de valores ya escritos en las tablas). Cada cifra lleva valor, unidad, periodo, archivo de origen con la fila
que la contiene, escenario (y referencia, cuando es una diferencia) y el md5 del _Output.csv de cada escenario que la
produce. Las lineas declaradas no tienen _Output.csv: llevan el md5 de B1_Scenario_Config.xlsx (hoja Art6_Adicionalidad).

Incluye las decisiones del 13-10-2026 (lineas en reserva fuera de la oferta, autorizacion con el Modelo CLG
y la regla prudente, dos metodos de ajuste, sobreventa por subconjunto, reserva por anada y autorizable ex post).
"""
import csv
import datetime
import io
import json

import comun as C
import configuracion as K

DESTINO = C.RESULTADOS / "cifras_finales_producto3.json"
KT = "kt CO2-eq"
T_ = "tablas/"


def _md5_salidas(escenarios):
    """{escenario: md5 del _Output.csv} de los escenarios con salida en Executables."""
    out = {}
    for e in escenarios:
        p = C.salida(e)
        out[e] = C.md5(p) if p.exists() else None
    return out


def _manifiesto_sensibilidad(ruta):
    """{escenario: md5} de los _Output.csv guardados con la sensibilidad de los pisos del Modelo CLG."""
    m = ruta / "MANIFIESTO_md5.csv"
    out = {}
    if not m.exists():
        return out
    with io.open(m, encoding="utf-8-sig") as f:
        for r in csv.DictReader(f):
            p = r.get("ruta_relativa_a_Energy") or ""
            if p.startswith("Executables/") and p.endswith("_0_Output.csv"):
                out[p.split("/")[1][:-2]] = r["md5"]
    return out


def escribir(out, json_md5, sensibilidad=None):
    """Escribe cifras_finales_producto3.json a partir del diccionario de resultados de analizar.main()."""
    T = out["roles"]
    con, inc, con_clg, inc_clg = T["con"], T["inc"], T["con_clg"], T["inc_clg"]
    esc = T["escalera"]
    top = esc[-1] if esc else None
    base = T["base"]
    V, MC = out["ventana"], out["marco"]["anios"]
    idx = {a: i for i, a in enumerate(out["anios"])}
    md5 = _md5_salidas(out["corrida"]["escenarios"])
    cfg = C.md5(C.ART6_CONFIG)
    nac_md5 = C.md5(C.NACIONAL)
    ofertantes = [con] + esc                                    # escenarios cuyas salidas forman la oferta del modelo
    ref_lectura = {("CLG", "condicional"): con, ("CLG", "prudente"): inc,
                   ("corregida", "condicional"): con_clg, ("corregida", "prudente"): inc_clg}
    cifras = []

    def m5(*escs):
        for e in escs:                    # escenarios fuera de la corrida del analisis (INCA6G, con RE01): se leen aqui
            if e and e not in md5:
                md5.update(_md5_salidas([e]))
        return {e: md5.get(e) for e in escs if e}

    def cifra(tema, id_, descripcion, valor, unidad, archivo, fila, escenario, salidas, periodo=None, referencia=None,
              **extra):
        d = {"id": id_, "tema": tema, "descripcion": descripcion, "valor": valor, "unidad": unidad, "periodo": periodo,
             "archivo": archivo, "fila": fila, "escenario": escenario, "referencia": referencia,
             "output_md5": salidas}
        d.update({k: v for k, v in extra.items() if v is not None})
        cifras.append(d)

    # ------------------------------------------------------------------ capas A, B y C
    marco = {(r["referencia"], r["escenario"]): r for r in out["marco"]["componentes"]}
    for r in out["descomposicion"]:
        if r["escenario"] not in esc or r["referencia"] != base.get(r["escenario"]):
            continue
        c, b = r["escenario"], r["referencia"]
        cifra("capas", "capa_%s_2031_2035" % c, "Capa del %s sobre %s: reducción de emisiones del sector energía" % (c, b),
              r["total_2031_2035"], KT, T_ + "descomposicion_reducciones.csv", "escenario=%s, referencia=%s" % (c, b),
              c, m5(c, b), "%d-%d" % (V[0], V[-1]), b, componente=r["componente"])
        cifra("capas", "capa_%s_2035" % c, "Capa del %s sobre %s en 2035" % (c, b), r["2035"], KT,
              T_ + "descomposicion_reducciones.csv", "escenario=%s, referencia=%s, columna 2035" % (c, b), c, m5(c, b),
              "2035", b)
        mc = marco.get((b, c))
        if mc:
            cifra("capas", "capa_%s_2026_2035" % c, "Capa del %s sobre %s en el marco de la Segunda NDC" % (c, b),
                  mc["total_2026_2035"], KT, T_ + "marco_2026_2035.csv", "escenario=%s, referencia=%s" % (c, b), c,
                  m5(c, b), "%d-%d" % (MC[0], MC[-1]), b)

    # ------------------------------------------------------------------ oferta en tres niveles, sin y con la reserva
    on = out["oferta_niveles"]
    gas = next((d for d in T["estados"] if d["sufijo"] == "GAS"), None)
    sens_md5 = _manifiesto_sensibilidad(sensibilidad) if sensibilidad else {}
    # las salidas de la sensibilidad con los pisos del Modelo CLG estan en la carpeta guardada, no en Executables
    # (correccion del 13-10-2026 tras la verificacion independiente del paso 15): ruta relativa a la raiz del repositorio
    sens_exe = (sensibilidad.relative_to(C.RAIZ).as_posix() + "/Executables") if sensibilidad else None
    sens_arch = {e: "%s/%s_0/%s_0_Output.csv" % (sens_exe, e, e) for e in ofertantes} if sens_exe else {}
    sens_json = sensibilidad / "B2_Output_Art6" / "resultados_art6.json" if sensibilidad else None
    salidas_caso = {"central_K16_con_gas": m5(*ofertantes),
                    "K16_sin_gas": m5(*([gas["referencia"]] + [gas["miembros"].get(c) for c in esc])) if gas else {},
                    "pisos_CLG_12_10": {e: sens_md5.get(e) for e in ofertantes}}
    for clave, filas in (("sin_reserva", on["niveles"]), ("con_reserva", on.get("niveles_con_reserva") or [])):
        for x in filas:
            cifra("oferta_tres_niveles", "oferta_%s_%s" % (x["nivel"], clave),
                  "Oferta 2031-2035, %s (%s); líneas en reserva %s" % (x.get("rotulo", x["nivel"]), x["caso"],
                                                                        x["lineas_en_reserva"]),
                  x["kt_2031_2035"], KT, T_ + "oferta_tres_niveles.csv",
                  "nivel=%s, lineas_en_reserva=%s" % (x["nivel"], x["lineas_en_reserva"].split(" ")[0]),
                  x["caso"], salidas_caso.get(x["caso"], {}), "%d-%d" % (V[0], V[-1]),
                  por_anio={str(a): x[str(a)] for a in V}, supuesto=x["supuesto"], rotulo=x.get("rotulo"),
                  es_nivel_de_oferta=x.get("es_nivel_de_oferta"),
                  nota=("Salidas de la sensibilidad guardada en %s, no en Executables: los md5 de output_md5 son los de "
                        "los _Output.csv de esa carpeta (MANIFIESTO_md5.csv)" % sens_exe)
                  if x["caso"] == "pisos_CLG_12_10" and sensibilidad else None,
                  ruta_salidas=sens_exe if x["caso"] == "pisos_CLG_12_10" else None,
                  archivos_salida=sens_arch if x["caso"] == "pisos_CLG_12_10" and sens_arch else None,
                  resultados_sensibilidad=({"archivo": sens_json.relative_to(C.RAIZ).as_posix(),
                                            "md5": C.md5(sens_json)}
                                           if x["caso"] == "pisos_CLG_12_10" and sens_json and sens_json.exists()
                                           else None))
    for d in on["detalle"]:
        if d["caso"] != "central_K16_con_gas":
            continue
        declarado = d["clave"] in ("firme", "declarado", "en_reserva")
        cifra("oferta_componentes", "oferta_central_%s" % d["clave"].replace(":", "_"),
              "Oferta central 2031-2035: %s" % d["bloque"], d["kt_2031_2035"], KT, T_ + "oferta_por_caso.csv",
              "caso=central_K16_con_gas, clave=%s" % d["clave"],
              "declarado (Art6_Adicionalidad)" if declarado else top, {} if declarado else m5(*ofertantes),
              "%d-%d" % (V[0], V[-1]), art6_configuracion_md5=cfg if declarado or d["clave"].startswith("total") else None)

    # ------------------------------------------------------------------ aporte atribuible
    for r in out["volumenes"]:
        if r["regla"] == "atribuible_por_retiro":
            cifra("aporte_atribuible", "aporte_atribuible_%s_2031_2035" % r["escenario"],
                  "Aporte atribuible por retiro: %s frente a su contrafactual %s" % (r["escenario"], r["referencia"]),
                  r["total_2031_2035"], KT, T_ + "volumenes_por_regla.csv",
                  "escenario=%s, regla=atribuible_por_retiro" % r["escenario"], r["escenario"],
                  m5(r["escenario"], r["referencia"]), "%d-%d" % (V[0], V[-1]), r["referencia"])
    for r in out["marco"]["componentes"]:
        if str(r["componente"]).startswith("Aporte atribuible"):
            cifra("aporte_atribuible", "aporte_atribuible_%s_2026_2035" % r["escenario"], r["componente"],
                  r["total_2026_2035"], KT, T_ + "marco_2026_2035.csv", "componente=%s" % r["componente"],
                  r["escenario"], m5(r["escenario"], r["referencia"]), "%d-%d" % (MC[0], MC[-1]), r["referencia"])

    # ------------------------------------------------------------------ margen de 2035 en las cuatro lecturas
    estados_ref = [("", top)] + [(d["sufijo"], d["miembros"].get(top)) for d in T["estados"]
                                 if d["grupo"] == "Riesgo" and d["miembros"].get(top)]
    for r in out["headroom_proyecciones"]:
        suf = next((s for s, e in estados_ref if e == r["escenario"]), None)
        if suf is None and r["escenario"] not in (con, inc):
            continue
        cifra("margen_2035", "margen_2035_%s_%s_%s" % (r["escenario"], r["proyeccion"], r["regla"]),
              "Margen nacional de 2035 frente a la meta incondicional de la Segunda NDC: %s, proyección %s, regla %s"
              % (r["escenario"], r["proyeccion"], r["regla"]), r["2035"], KT, T_ + "headroom_proyecciones.csv",
              "proyeccion=%s, escenario=%s, regla=%s, columna 2035" % (r["proyeccion"], r["escenario"], r["regla"]),
              r["escenario"], m5(r["escenario"], r["referencia"]), "2035", r["referencia"],
              lectura_de_autorizacion=(r["proyeccion"], r["regla"]) == ("CLG", "prudente"),
              nacional_md5=nac_md5)

    # ------------------------------------------------------------------ sobreventa por estado, regla, metodo y subconjunto
    for r in out.get("sobreventa_metodo_subconjunto", []):
        ref = ref_lectura[(r["proyeccion"], r["regla"])]
        cifra("sobreventa", "sobreventa|%s|%s|%s_%s|%s" % (r["subconjunto"], r["metodo"], r["proyeccion"], r["regla"],
                                                             r["sufijo"] or "intacto"),
              "Sobreventa: %s, método %s, proyección %s, regla %s, %s" % (r["subconjunto_nombre"], r["metodo"],
                                                                           r["proyeccion"], r["regla"], r["estado"]),
              r["sobreventa_kt"], KT, T_ + "sobreventa_por_metodo_y_subconjunto.csv",
              "subconjunto=%s, metodo=%s, proyeccion=%s, regla=%s, escenario=%s"
              % (r["subconjunto"], r["metodo"], r["proyeccion"], r["regla"], r["escenario"]),
              r["escenario"], m5(r["escenario"], ref, *ofertantes), r["anios_evaluados"], ref,
              autorizado_2031_2035=r["autorizado_2031_2035"], ajuste_2035=r["ajuste_2035"], margen_2035=r["margen_2035"],
              margen_2035_tras_ajuste=r["margen_2035_tras_ajuste"],
              incumplimiento_propio_kt=r["incumplimiento_propio_kt"],
              primer_anio_negativo_tras_transferir=r["primer_anio_negativo_tras_transferir"],
              lectura_de_autorizacion=r["lectura_de_autorizacion"], estado_de_referencia=r["estado_de_referencia"],
              art6_configuracion_md5=cfg, nacional_md5=nac_md5)

    # ------------------------------------------------------------------ primer anio negativo (oferta central, regla anual)
    for r in (out.get("sobreventa_anual") or {}).get("resumen", []):
        ref = ref_lectura[(r["proyeccion"], r["regla"])]
        for clave, desc in (("primer_anio_margen_negativo", "sin transferir, 2026-2035"),
                            ("primer_anio_margen_negativo_tras_transferir", "después de transferir lo autorizado, "
                                                                            "2031-2035")):
            cifra("primer_anio_negativo", "%s|%s_%s|%s" % (clave, r["proyeccion"], r["regla"], r["sufijo"] or "intacto"),
                  "Primer año con margen negativo %s: %s, proyección %s, regla %s" % (desc, r["estado"], r["proyeccion"],
                                                                                     r["regla"]),
                  r[clave], "año", T_ + "sobreventa_primer_anio_negativo.csv",
                  "proyeccion=%s, regla=%s, escenario=%s" % (r["proyeccion"], r["regla"], r["escenario"]),
                  r["escenario"], m5(r["escenario"], ref, *ofertantes), referencia=ref,
                  nota="vacío: ningún año negativo" if r[clave] is None else None)

    # ------------------------------------------------------------------ respaldo de emergencia y horas de corte
    rp = out.get("respaldo") or {}
    mw_rot = rp.get("rotulo_MW") or "MW equivalentes"
    for r in rp.get("resumen", []):
        e = r["escenario"]
        rot_e = r.get("rotulo") or e
        for k, u, desc in (("respaldo_max_MW", mw_rot, "Respaldo de emergencia máximo (potencia de PPFOI sobre el tope "
                                                       "K15b; el modelo tiene un solo timeslice y no ve la punta)"),
                           ("primer_anio_con_respaldo", "año", "Primer año con respaldo de emergencia"),
                           ("respaldo_2031_2035_GWh", "GWh", "Energía de respaldo 2031-2035 (generación en barras de "
                                                             "central)"),
                           ("respaldo_2031_2035_kt_CO2e", KT, "Emisiones del respaldo 2031-2035"),
                           ("ENS_2031_2035_GWh", "GWh", "Energía no suministrada equivalente 2031-2035 (respaldo x "
                                                        "eta_T x eta_D)"),
                           ("ENS_max_GWh", "GWh", "Energía no suministrada equivalente, máximo anual"),
                           ("ENS_max_pct_demanda", "% de la demanda eléctrica final",
                            "Energía no suministrada equivalente, máximo anual, en porcentaje de la demanda"),
                           ("horas_corte_max_por_dia", "h/día", "Horas de corte equivalentes, máximo por día (24 x ENS / "
                                                                "demanda eléctrica final)"),
                           ("horas_corte_max_por_anio", "h/año", "Horas de corte equivalentes, máximo por año (8.760 x "
                                                                 "ENS / demanda eléctrica final)"),
                           ("horas_corte_max_por_dia_estiaje_6_meses", "h/día",
                            "Horas de corte equivalentes por día con el déficit concentrado en 6 meses de estiaje "
                            "(supuesto)"),
                           ("horas_formula_anterior_max_por_dia", "h/día",
                            "Fórmula anterior (24 x respaldo / demanda final), superada: excede en 1 / (eta_T x eta_D)")):
            if k not in r:
                continue
            cifra("respaldo", "%s|%s" % (k, e), "%s: %s" % (desc, rot_e), r[k], u, T_ + "respaldo_por_escenario.csv",
                  "escenario=%s (resumen en resultados_art6.json, clave respaldo.resumen)" % e, e, m5(e),
                  anio_respaldo_max=r.get("anio_respaldo_max"), anio_ENS_max=r.get("anio_ENS_max"),
                  rotulo=rot_e if rot_e != e else None, declaracion=rp.get("nota"))

    # ------------------------------------------------------------------ rango del gas
    # puente de la base desde descomposicion_reducciones.csv (sumas sin redondeo anual): CONA6 - NDCCON es el negativo de
    # la correccion de la base; CONA6G - NDCCON resta ademas el efecto de la referencia del estado GAS (CONA6 - CONA6G)
    dd = {(r["referencia"], r["escenario"]): r["total_2031_2035"] for r in out["descomposicion"]}
    if gas and (con_clg, con) in dd:
        g = gas["referencia"]
        p_con = round(-dd[(con_clg, con)], 1)
        p_gas = round(p_con - dd[(con, g)], 1) if (con, g) in dd else None
        for ref_b, nom, v, fila in ((con, "caso central con la expansión a gas declarada", p_con,
                                     "referencia=%s, escenario=%s, con signo cambiado" % (con_clg, con)),
                                    (g, "sin la expansión a gas declarada (G01)", p_gas,
                                     "la fila anterior menos referencia=%s, escenario=%s" % (con, g))):
            cifra("rango_gas", "puente_%s_menos_%s_2031_2035" % (ref_b, con_clg),
                  "Puente de la base condicional, %s: emisiones del sector energía de %s menos %s" % (nom, ref_b, con_clg),
                  v, KT, T_ + "descomposicion_reducciones.csv", fila, ref_b, m5(ref_b, con_clg, con),
                  "%d-%d" % (V[0], V[-1]), con_clg)
        for k in ("central_K16_con_gas", "K16_sin_gas"):
            if k in on["totales"]:
                cifra("rango_gas", "oferta_%s" % k, "Oferta 2031-2035 sin las líneas en reserva: %s" % k,
                      on["totales"][k], KT, T_ + "oferta_por_caso.csv", "caso=%s, clave=total" % k, k,
                      salidas_caso.get(k, {}), "%d-%d" % (V[0], V[-1]))

    # ------------------------------------------------------------------ factor del MWh desplazado frente al OM
    fm = out.get("factor_frente_al_margen") or {}
    per = "%d-%d" % (V[0], V[-1])
    for r in fm.get("tabla") or []:
        if r["periodo"] != per:
            continue
        for k, u, desc in (("factor_CO2_neto_red_t_MWh", "t CO2/MWh netos", "Factor CO2 neto de la red desplazada"),
                           ("razon_frente_al_margen_operacion", "razón", "Factor frente al margen de operación 2025 "
                                                                         "(%s)" % fm.get("margen_operacion_2025")),
                           ("razon_frente_a_media_no_bajo_costo", "razón", "Factor frente a la media de no bajo costo "
                                                                           "2025 (%s)" % fm.get("media_no_bajo_costo_2025")),
                           ("factor_CO2e_bruto_t_MWh", "t CO2-eq/MWh brutos", "Factor CO2-eq bruto de toda la térmica")):
            cifra("factor_desplazado", "%s|%s|%s" % (k, r["caso"], r["escenario"]),
                  "%s: %s sobre %s (%s)" % (desc, r["escenario"], r["base"], r["caso"]), r[k], u,
                  T_ + "factor_desplazado_frente_al_margen.csv",
                  "caso=%s, escenario=%s, periodo=%s" % (r["caso"], r["escenario"], per), r["escenario"],
                  m5(r["escenario"], r["base"]), per, r["base"],
                  margen_operacion_2025=fm.get("margen_operacion_2025"),
                  media_no_bajo_costo_2025=fm.get("media_no_bajo_costo_2025"),
                  fuente_valores_oficiales="MAE, CTFE, Informe del Factor de Emisión de CO2 del S.N.I. 2025, tabla 6, p. 17")

    # ------------------------------------------------------------------ termica desplazable de 2035 y ERNC
    for e, s in out["termica_desplazable_GWh"].items():
        cifra("termica_desplazable_2035", "termica_desplazable_2035|%s" % e,
              "Térmica desplazable de 2035 (generación térmica sobre su piso de despacho): %s" % e, s[idx[2035]], "GWh",
              T_ + "termica_desplazable_GWh.csv", "anio=2035, columna %s" % e, e, m5(e), "2035")
    for e, s in out["ernc_pct"].items():
        for a in (2030, 2035):
            cifra("ernc", "ernc_%d|%s" % (a, e), "Participación ERNC en la generación (sin hidroelectricidad): %s, %d"
                  % (e, a), s[idx[a]], "% de la generación", T_ + "cuota_ernc_pct.csv", "anio=%d, columna %s" % (a, e),
                  e, m5(e), str(a))

    # ------------------------------------------------------------------ ingresos al precio del motor
    precios = K.hoja("Precios")
    dec = out.get("decisiones_13_10") or {}
    for s in dec.get("subconjuntos", []):
        for p in precios:
            usd = float(p["usd_por_t"])
            cifra("ingresos", "ingresos|%s|%s" % (s["clave"], p["escenario_precio"]),
                  "Ingresos potenciales 2031-2035 de lo autorizado (%s) al precio %s" % (s["nombre"],
                                                                                         str(p["escenario_precio"]).lower()),
                  round(s["autorizado_2031_2035"] * 1000.0 * usd / 1e6, 1), "millones de USD", "resultados_art6.json",
                  "clave decisiones_13_10.subconjuntos, clave=%s, campo autorizado_2031_2035; precio: hoja Art6_Precios, "
                  "escenario_precio=%s" % (s["clave"], p["escenario_precio"]), top, m5(*ofertantes),
                  "%d-%d" % (V[0], V[-1]), volumen_kt=s["autorizado_2031_2035"], precio_usd_por_t=usd,
                  archivo_precio="../B1_Scenario_Config.xlsx", hoja_precio="Art6_Precios",
                  fecha_del_precio=p.get("fecha_dato"), estado_del_precio=p.get("estado"),
                  referencia_del_precio=p.get("referencia"), art6_configuracion_md5=cfg)
    for o in out["ingresos"]["oferta"]:
        for p in precios:
            k = "MUSD_" + str(p["escenario_precio"])
            if k in o:
                cifra("ingresos", "ingresos_oferta|%s|%s" % (o["clave"], p["escenario_precio"]),
                      "Ingresos potenciales 2031-2035: %s, precio %s" % (o["oferta"], str(p["escenario_precio"]).lower()),
                      o[k], "millones de USD", T_ + "ingresos_por_oferta.csv", "clave=%s, columna %s" % (o["clave"], k),
                      top, m5(*ofertantes), "%d-%d" % (V[0], V[-1]), volumen_kt=o["kt_2031_2035"],
                      precio_usd_por_t=float(p["usd_por_t"]), fecha_del_precio=p.get("fecha_dato"),
                      estado_del_precio=p.get("estado"), nota=o.get("nota"))

    # ------------------------------------------------------------------ reserva por anada y autorizable ex post
    for r in (out.get("reserva_por_aniada") or {}).get("resumen", []):
        cifra("reserva_por_aniada", "reserva|%s|%s" % (r["subconjunto"], r["sufijo"] or "intacto"),
              "Autorizable 2031-2035 con reserva por añada (Modelo CLG, regla prudente): %s, %s" % (r["subconjunto"],
                                                                                                  r["estado"]),
              r["autorizable_2031_2035"], KT, T_ + "reserva_por_aniada.csv",
              "subconjunto=%s, escenario=%s, anio=%d-%d" % (r["subconjunto"], r["escenario"], V[0], V[-1]),
              r["escenario"], m5(r["escenario"], inc, *ofertantes), "%d-%d" % (V[0], V[-1]), inc,
              reserva_kt=r["reserva_2031_2035"], reserva_pct=r["reserva_pct"],
              reserva_uniforme_equivalente_pct=r["reserva_uniforme_equivalente_pct"],
              autorizable_por_aniada=r["autorizable_por_aniada"], estado_de_referencia=r["estado_de_referencia"])
    for r in (out.get("autorizable_ex_post") or {}).get("resumen", []):
        ref = ref_lectura[(r["proyeccion"], r["regla"])]
        cifra("autorizable_ex_post", "ex_post|%s|%s_%s|%s" % (r["subconjunto"], r["proyeccion"], r["regla"],
                                                                r["sufijo"] or "intacto"),
              "Autorizable ex post 2031-2035 con tope en la oferta de cada añada (valor central): %s, proyección %s, "
              "regla %s, %s" % (r["subconjunto"], r["proyeccion"], r["regla"], r["estado"]),
              r["autorizable_ex_post_2031_2035"], KT, T_ + "autorizable_ex_post.csv",
              "subconjunto=%s, proyeccion=%s, regla=%s, escenario=%s" % (r["subconjunto"], r["proyeccion"], r["regla"],
                                                                         r["escenario"]),
              r["escenario"], m5(r["escenario"], ref, *ofertantes), "%d-%d" % (V[0], V[-1]), ref,
              reduccion_estado_kt=r["reduccion_estado_2031_2035"], autorizado_ex_ante_kt=r["autorizado_ex_ante_2031_2035"],
              ex_post_sin_tope_informativo_kt=r.get("autorizable_ex_post_sin_tope_2031_2035"),
              lectura_de_autorizacion=r["lectura_de_autorizacion"], estado_de_referencia=r["estado_de_referencia"])

    # ------------------------------------------------------------------ estado ACT anclado a 2026 frente a lo observado
    ac = out.get("act_2026") or {}
    for r in ac.get("tabla", []):
        if r["anio"] == 2025 and r["escenario"] == con:
            # 2025 es igual en CONA6 y en los estados ACT: se informa una vez, con su observado del mismo perimetro
            for k, u, desc in (("participacion_termica_SNI_pct", "% de la producción del S.N.I. con importación",
                                "Participación térmica de 2025 del modelo (perímetro S.N.I.)"),
                               ("participacion_termica_observada_pct", "% de la producción neta con importación",
                                "Participación térmica observada de 2025 (CENACE, con importación)"),
                               ("diferencia_termica_modelo_menos_observado_pp", "puntos porcentuales",
                                "Participación térmica de 2025, modelo menos observado")):
                cifra("act_2026", "act_2026|%s|%s|2025" % (k, con), "%s: %s" % (desc, con), r[k], u,
                      T_ + "act_2026_contraste.csv", "escenario=%s, anio=2025" % con, con, m5(con), "2025",
                      observado=ac.get("observado"), perimetro=ac.get("perimetro"))
        if r["anio"] != 2026:
            continue
        e = r["escenario"]
        for k, u, desc in (("crecimiento_demanda_pct", "%", "Crecimiento de la demanda eléctrica final 2026/2025"),
                           ("participacion_termica_SNI_pct", "% de la producción del S.N.I. con importación",
                            "Participación térmica de 2026 (perímetro S.N.I.)"),
                           ("participacion_termica_observada_pct", "% de la producción neta con importación",
                            "Participación térmica observada de enero a agosto de 2026 (CENACE, con importación)"),
                           ("diferencia_termica_modelo_menos_observado_pp", "puntos porcentuales",
                            "Participación térmica de 2026, modelo menos observado de enero a agosto"),
                           ("participacion_hidro_SNI_pct", "% de la producción del S.N.I. con importación",
                            "Participación hidroeléctrica de 2026 (perímetro S.N.I.)"),
                           ("crecimiento_hidro_pct", "%", "Crecimiento de la hidroelectricidad 2026/2025"),
                           ("fp_coca_codo_participacion_2025_pct", "%", "Factor de planta de Coca Codo en 2026 "
                                                                       "(participación de 2025 en PPHRORAB)"),
                           ("importacion_GWh", "GWh", "Importación desde Colombia en 2026")):
            cifra("act_2026", "act_2026|%s|%s" % (k, e), "%s: %s" % (desc, e), r[k], u, T_ + "act_2026_contraste.csv",
                  "escenario=%s, anio=2026" % e, e, m5(e), "2026", observado=ac.get("observado"),
                  perimetro=ac.get("perimetro"))

    # ------------------------------------------------------------------ metas de contexto (Segunda NDC)
    m = out.get("metas_2035") or {}
    for k, desc in (("base", "Tendencial nacional de 2035 (agregación del Modelo CLG)"),
                    ("meta_inc", "Nivel de la meta incondicional de 2035 (tendencial menos 8 800 kt)"),
                    ("meta_con", "Nivel de la meta condicional de 2035 (tendencial menos 19 400 kt)")):
        if k in m:
            cifra("metas_segunda_ndc", "metas_2035|%s" % k, desc, m[k], KT, "resultados_art6.json",
                  "clave metas_2035.%s" % k, "nacional (Segunda NDC)", {}, "2035", nacional_md5=nac_md5,
                  fuente="ECU_NDC/PowerBI/Nacionales/Emisiones Totales.xlsx; metas de la hoja Art6_Headroom")

    inca6g = next((r for r in rp.get("resumen", []) if r["escenario"] == "INCA6G"), None)
    notas = {
        "INCA6G": ("INCA6G, con cierre de fuel oil de emergencia (filas RE01): respaldo 2031-2035 de %s GWh y %s kt CO2-eq. "
                   "RE01 es un supuesto de cierre introducido en la corrida K16, fuera del acuerdo original de respaldo "
                   "solo en los estados de riesgo; se aprobó el 13-10-2026, después de la verificación, "
                   "conservarlo rotulado." % ((inca6g or {}).get("respaldo_2031_2035_GWh"),
                                              (inca6g or {}).get("respaldo_2031_2035_kt_CO2e"))),
        "piso_K16": "En CONA6 y CONA6G la carpeta A2 conserva el piso de PPFOI del Modelo CLG (9,3785 PJ); el valor que "
                    "rige, K16 (5,0567 PJ en 2026-2035), vive en la fila de Electrical K16-PPFOI-CON.",
        "respaldo_MW": mw_rot + "; el modelo tiene un solo timeslice y no ve la punta.",
        "oferta_niveles": on.get("rotulos"),
        "autorizable_ex_post": "Valor central con tope en la oferta de cada añada; el ex post sin tope es informativo."}
    doc = {"titulo": "Cifras finales del Producto 3 (Artículo 6, sector energía)",
           "notas_13_10": notas,
           "generado": datetime.datetime.now().strftime("%Y-%m-%dT%H:%M"),
           "modelo": "Modelo Climate Lead Group (ECU_NDC, rama art6-escenarios) con la base corregida congelada K16",
           "carpeta": "Energy/B2_Output_Art6",
           "resultados_art6_json_md5": json_md5,
           "corrida": out["corrida"], "salidas_md5": md5, "art6_configuracion_md5": cfg, "nacional_md5": nac_md5,
           "decisiones_13_10": out.get("decisiones_13_10"),
           "regla_de_autorizacion": out["potencial_art6"].get("regla_de_autorizacion"),
           "convenciones": {"emisiones": "kt CO2-eq del sector energía (CO2e_DE + CO2e_PP + CO2e_FUG + CO2e_REF del "
                                         "_Output.csv); márgenes y metas nacionales con UTCUTS (agregación del Modelo "
                                         "CLG, PCG AR5)",
                            "ventana": "%d-%d (transacciones)" % (V[0], V[-1]),
                            "marco": "%d-%d (Segunda NDC)" % (MC[0], MC[-1]),
                            "lecturas": "proyección CLG o corregida por regla condicional o prudente; la autorización "
                                        "usa CLG prudente",
                            "redondeo": "se suma sin redondear y se redondea el total (corrección del 13-10-2026): las "
                                        "cifras por año o por añada se muestran con un decimal y su suma puede diferir "
                                        "del total en 0,1 kt; la sobreventa nunca supera lo autorizado ni lo autorizado "
                                        "la oferta",
                            "rutas": "archivo, relativo a Energy/B2_Output_Art6; ruta_salidas, archivos_salida y "
                                     "resultados_sensibilidad, relativos a la raíz del repositorio",
                            "caracter": "Óptimos de mínimo costo con costos de relleno: ejercicio analítico, no pronóstico"},
           "n_cifras": len(cifras), "cifras": cifras}
    io.open(DESTINO, "w", encoding="utf-8").write(json.dumps(doc, ensure_ascii=False, indent=1, default=float))
    return DESTINO
