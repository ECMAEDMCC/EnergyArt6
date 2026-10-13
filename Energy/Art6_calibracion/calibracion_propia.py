# -*- coding: utf-8 -*-
"""Calibración propia de INCA6 y CONA6 frente a la Tabla 5 de la ficha, al BEN 2025 y puente 2026-2035.

Uso, desde ECU_NDC/Energy, después de correr B1:
    python Art6_calibracion/calibracion_propia.py [--anterior <carpeta con CONA6 (o CONA6_0)/CONA6_0_Output.csv previo>]

Rótulos: «CLG» es el Modelo Climate Lead Group (ECU_NDC main f19d6b1, sin cambios); NDCINC y NDCCON son escenarios del
Modelo CLG. «ficha publicada» es la columna MODELO de la Tabla 5 de la ficha (corrida no conservada). INCA6G y CONA6G
son la sensibilidad de gas. Versión vigente: base con K16 (corrida de B1 del 13-10-2026; CONA6 0410ba4f, con INCA6G
resuelto con las filas RE01, «con cierre de fuel oil de emergencia»). La versión anterior de cada tabla lleva el sufijo
_v3 (versión K15 con arriendos, corrida del 12-10-2026, 16:46-16:50, CONA6 331e5665); las _v3 previas (corrida de las
15:45) y las _v2 están en _stale_ECU_NDC_2026-10-11.

Lee los _Output.csv y los datafiles de Executables/{NDCINC,INCA6,INCA6G,NDCCON,CONA6,CONA6G}_0 y escribe en
Art6_calibracion:
- calibracion_a_tabla5.csv: CO2e_PP (kt CO2-eq) del CLG (NDCCON), INCA6 y CONA6 frente a la fila 1A1 (1A1a + 1A1cii)
  de la Tabla 5 (tabla5_ficha_p19.csv), con el error (INGEI - modelo)/INGEI por año y el CONA6 de la versión anterior.
- calibracion_b_generacion_ben.csv: generación por fuente (GWh) 2010-2025 de NDCCON, INCA6 y CONA6 frente al BEN 2025,
  tabla 2.20 (2015-2025; la tabla no cubre 2010-2014).
- calibracion_b_combustible_ben.csv: combustible por tipo (PJ) 2015-2025 de NDCCON, INCA6 y CONA6 (UseByTechnology de las
  ocho térmicas fósiles; actividad de PPILPG para el GLP) frente al BEN 2025, tabla 2.28 (kBEP x 5,8102 TJ/kBEP).
- calibracion_b_rendimientos.csv: InputActivityRatio y rendimiento de cada térmica fósil 2010-2035 (CLG y CONA6) con
  el IAR del grupo del BEN (tablas 3.12-3.15).
- calibracion_b_combustible_ingei_2022.csv: CO2 de 1A1 por combustible del INGEI 2022 (inventario_gei_largo.csv del
  módulo de inventario, solo contraste) frente al modelo; comparable en crudo y gas natural.
- calibracion_b_potencia_ben.csv: potencia por fuente (MW, TotalCapacityAnnual) 2015-2025 frente al BEN 2025, tabla 2.23
  (y SGDA de la tabla 2.25), con biomasa y biogás frente a capacidad_bio_fuentes.csv.
- calibracion_c_vertido.csv: vertido de electricidad (producción - uso - demanda de E1ELE, E2ELE y E3ELE) por año y su
  contraste con la tabla 2.19 del BEN (exportación, consumo propio, pérdidas y consumo final que el modelo no tiene).
  La generación al balance excluye PPIBIM y PPILPG, que no tienen OutputActivityRatio.
- calibracion_d_puente.csv: CO2e_PP 2026-2035 de NDCINC, INCA6, INCA6G, NDCCON, CONA6 y CONA6G, diferencias de cada
  referencia con su escenario CLG, tramo 2026-2028 aparte de 2029-2035, rango (caso central y sensibilidad de gas) y
  descomposición contable en actividad y factores; calibracion_d_generacion_2026_2035.csv de apoyo;
  calibracion_d_discontinuidad_termica.csv: actividad térmica observada 2023-2025 frente a 2026-2035 (K14 ancla la de
  los autoproductores y PPILPG).
- calibracion_f_factor_desplazado.csv: factor de emisión del MWh desplazado (marginal: térmica de la red que despacha
  sobre su piso) y promedio de la generación fósil de la red, 2025-2035, en CO2 y CO2-eq, bruto y neto, frente al
  margen de operación oficial de 2025 (MAE-CTFE, Informe del Factor de Emisión de CO2 del S.N.I. 2025, tabla 6, p. 17).
- calibracion_g_suficiencia_termica.csv: potencia de las térmicas de la red (PPFOI, PPDSL, PPNGS) frente al tope K15b
  (residual K15c + expansión declarada), inversión de cada año frente a la declarada para ese año, en los cuatro clones.
- calibracion_d_termica_red_2026_2035.csv: trayectoria de PPFOI, PPDSL y PPNGS (potencia nueva, potencia total,
  actividad, razón frente a la media observada 2023-2025).
- calibracion_resumen.json: md5 de cada insumo.
El desglose del puente por corrección (tabla e) lo escribe desglose_puente.py.
CO2e_PP = suma de AnnualTechnologyEmission de la emisión CO2e_PP x 1000. Generación = TotalTechnologyAnnualActivity de
las tecnologías PP e IMPELE (nunca los buses) x 277,78 GWh/PJ; la térmica no incluye PPILPG (sin OutputActivityRatio, su
actividad es combustible), cambio de definición frente a las tablas _v1.
"""
import hashlib
import json
import re
import sys
from pathlib import Path

import pandas as pd

ENERGIA = Path(__file__).resolve().parents[1]
AQUI = Path(__file__).resolve().parent
EX = ENERGIA / "Executables"
PJ = 277.78
ESC = ["NDCINC", "INCA6", "INCA6G", "NDCCON", "CONA6", "CONA6G"]
PARES = (("INCA6", "NDCINC"), ("INCA6G", "NDCINC"), ("CONA6", "NDCCON"), ("CONA6G", "NDCCON"))
FOSILES = ("PPFOI", "PPDSL", "PPNGS", "PPCRU", "PPRNGS", "PPRDSL", "PPDFOI", "PPDDSL")  # generación térmica
# PPILPG no tiene OutputActivityRatio y su actividad es combustible (GLP, EAR por unidad de combustible): no cuenta como
# generación; sí cuenta en la potencia térmica.
FOSILES_CAP = FOSILES + ("PPILPG",)
FAMILIAS = {
    "hidraulica": lambda t: t.startswith("PPH") or t == "PPIHD",
    "termica": lambda t: t in FOSILES,
    "biomasa": lambda t: t in ("PPBIM", "PPIBIM"),
    "biogas": lambda t: t == "PPBGS",
    "eolica": lambda t: t.startswith("PPWND"),
    "solar": lambda t: t.startswith("PPPV"),
    "geotermia": lambda t: t == "PPGEO",
    "importaciones": lambda t: t == "IMPELE",
}
CONSUMO = ("T4ELE_HEA", "T5ELECOM", "T5ELECON", "T5ELEIND", "T5ELERES", "T5ELETRO")
ARC_TIPO = {"hidraulica": ("nominal", "hidraulica"), "termica_fosil": ("nominal", "termica_no_renovable"),
            "eolica": ("efectiva", "eolica"), "solar_centrales_PPPVT": ("efectiva", "fotovoltaica"),
            "biomasa_PPIBIM": ("efectiva", "biomasa"), "biogas_PPBGS": ("efectiva", "biogas")}


def md5(ruta):
    return hashlib.md5(Path(ruta).read_bytes()).hexdigest()


def leer_output(esc):
    ruta = EX / f"{esc}_0" / f"{esc}_0_Output.csv"
    o = pd.read_csv(ruta, usecols=["Fuel", "Technology", "Emission", "Year", "Demand", "TotalTechnologyAnnualActivity",
                                   "ProductionByTechnology", "UseByTechnology", "AnnualTechnologyEmission",
                                   "TotalCapacityAnnual", "NewCapacity"], low_memory=False)
    e = o[o.Emission == "CO2e_PP"]
    nz = e[e.AnnualTechnologyEmission.fillna(0) != 0]
    if nz.duplicated(["Technology", "Year"]).any():
        raise SystemExit(f"{esc}: AnnualTechnologyEmission repetida por tecnología y año")
    co2 = e.groupby("Year").AnnualTechnologyEmission.sum() * 1000
    act = o.groupby(["Technology", "Year"]).TotalTechnologyAnnualActivity.max().unstack().fillna(0)
    cap = o.groupby(["Technology", "Year"]).TotalCapacityAnnual.max().unstack().fillna(0)
    nue = o.groupby(["Technology", "Year"]).NewCapacity.max().unstack().fillna(0)
    pp = [t for t in act.index if t.startswith("PP") or t == "IMPELE"]
    gen = pd.DataFrame({f: act.loc[[t for t in pp if fn(t)]].sum() * PJ for f, fn in FAMILIAS.items()})
    prod = o.dropna(subset=["ProductionByTechnology"]).groupby(["Fuel", "Technology", "Year"]).ProductionByTechnology \
        .sum().unstack().fillna(0)
    uso = o.dropna(subset=["UseByTechnology"]).groupby(["Fuel", "Technology", "Year"]).UseByTechnology.sum() \
        .unstack().fillna(0)
    dem = o.dropna(subset=["Demand"]).groupby(["Fuel", "Year"]).Demand.max().unstack().fillna(0)
    bal = {}
    for f in ("E1ELE", "E2ELE", "E3ELE"):
        p_ = prod.loc[f].sum() if f in prod.index.get_level_values(0) else 0
        u_ = uso.loc[f].sum() if f in uso.index.get_level_values(0) else 0
        d_ = dem.loc[f] if f in dem.index else 0
        bal[f] = (p_ - u_ - d_) * PJ
    vert = pd.DataFrame(bal).fillna(0)
    perd = ((uso.loc["E1ELE"].loc["ELE_TRANS"] - prod.loc["E2ELE"].loc["ELE_TRANS"]) +
            (uso.loc["E2ELE"].loc["ELE_DIST"] - prod.loc["E3ELE"].loc["ELE_DIST"])) * PJ
    cons = uso.loc["E3ELE"].reindex([t for t in CONSUMO if t in uso.loc["E3ELE"].index]).sum() * PJ
    gen_bal = sum(prod.loc[f].reindex([t for t in prod.loc[f].index if t.startswith("PP") or t == "IMPELE"]).sum()
                  for f in ("E1ELE", "E3ELE")) * PJ
    hid = [t for t in act.index if FAMILIAS["hidraulica"](t)]
    return {"co2": co2, "act": act, "cap": cap, "nueva": nue, "gen": gen, "vertido": vert, "perdidas": perd,
            "consumo": cons, "gen_balance": gen_bal, "hidro": act.loc[hid].sum() * PJ, "md5": md5(ruta)}


def pisos_hidro(esc):
    """Suma de los pisos de actividad hidro (GWh) por año, leída del datafile."""
    texto = (EX / f"{esc}_0" / f"{esc}_0.txt").read_text(encoding="utf-8")
    bloque = texto.split("param TotalTechnologyAnnualActivityLowerLimit")[1].split("\n;")[0].split("\n")
    anios = [int(a) for a in bloque[2].replace(":=", "").split()]
    tot = dict.fromkeys(anios, 0.0)
    for ln in bloque[3:]:
        p_ = ln.split()
        if p_ and FAMILIAS["hidraulica"](p_[0]):
            for a, v in zip(anios, p_[1:]):
                tot[a] += float(v) * PJ
    return tot


def ear_co2e(esc):
    """EmissionActivityRatio de CO2e_PP (modo 1) por tecnología y año, leído del datafile."""
    texto = (EX / f"{esc}_0" / f"{esc}_0.txt").read_text(encoding="utf-8")
    bloque = texto.split("param EmissionActivityRatio")[1].split("\n;")[0]
    filas = {}
    for m in re.finditer(r"\[ECU,(\w+),CO2e_PP,\*,\*\]:\n([^\n]+):=\n1 ([^\n]+)", bloque):
        anios = [int(a) for a in m.group(2).split()]
        filas[m.group(1)] = dict(zip(anios, (float(v) for v in m.group(3).split())))
    return pd.DataFrame(filas).T


def anterior_tabla(nombre):
    """Tabla de la versión anterior (sufijo _v2), si existe."""
    ruta = AQUI / nombre
    return pd.read_csv(ruta) if ruta.exists() else None


def output_anterior(carpeta, esc):
    for sub in (esc, f"{esc}_0"):
        ruta = Path(carpeta) / sub / f"{esc}_0_Output.csv"
        if ruta.exists():
            return ruta
    raise SystemExit(f"no está el {esc}_0_Output.csv de la versión anterior en {carpeta}")


COMB_TEC = {"PPFOI": "E1FO1", "PPDFOI": "E1FO1", "PPDSL": "E1DSL", "PPRDSL": "E1DSL", "PPDDSL": "E1DSL",
            "PPNGS": "E1NGS", "PPRNGS": "E1NGS", "PPCRU": "E1CRU"}
NOMBRE_COMB = {"E1CRU": "crudo (petróleo)", "E1NGS": "gas natural", "E1DSL": "diésel",
               "E1FO1": "fuel oil y crudo reducido", "GLP": "gas licuado (PPILPG)"}
BEN_COMB = {"E1CRU": ["petroleo"], "E1NGS": ["gas_natural"], "E1DSL": ["diesel_oil"],
            "E1FO1": ["fuel_oil", "crudo_reducido"], "GLP": ["gas_licuado"]}
CO2_TJ = {"E1CRU": 73.3, "E1NGS": 56.1, "E1DSL": 74.1, "E1FO1": 77.4, "GLP": 63.1}  # IPCC 2006, cuadro 2.2, t CO2/TJ
# sandbox PNUD: la copia del módulo inventario_gei que ya está en el repositorio (mismo md5)
INGEI_LARGO = ENERGIA / "Insumos_Art6" / "INGEI_largo.csv"
INGEI_COMB = {"Petróleo crudo": "E1CRU", "Gas Natural (seco)": "E1NGS", "Gas / Diesel Oil": "E1DSL",
              "Fuelóleo residual": "E1FO1", "Gases licuados de petróleo": "GLP"}
PJ_KBEP = 3.6 / 0.6196 / 1000  # BEN 2025, anexo de factores de conversión, p. 178: 10^3 kWh = 0,6196 BEP


def uso_combustible(ruta_output):
    """Combustible (PJ) por tipo y año: UseByTechnology de las ocho térmicas fósiles y actividad de PPILPG (GLP)."""
    o = pd.read_csv(ruta_output, usecols=["Technology", "Fuel", "Year", "UseByTechnology",
                                          "TotalTechnologyAnnualActivity"], low_memory=False)
    u = o[o.Technology.isin(COMB_TEC)].dropna(subset=["UseByTechnology"])
    por_tec = u.groupby(["Technology", "Year"]).UseByTechnology.sum().to_dict()
    u = u.groupby(["Fuel", "Year"]).UseByTechnology.sum()
    glp = o[o.Technology == "PPILPG"].groupby("Year").TotalTechnologyAnnualActivity.max()
    out = {(f, y): float(u.get((f, y), 0.0)) for f in ("E1CRU", "E1NGS", "E1DSL", "E1FO1") for y in range(2010, 2036)}
    out.update({("GLP", y): float(glp.get(y, 0.0)) for y in range(2010, 2036)})
    return out, por_tec


def tablas_combustible(r, anterior):
    """Combustible por tipo frente al BEN 2.28 (2015-2025), rendimientos por tecnología y contraste con el INGEI 2022."""
    sys.path.insert(0, str(AQUI))
    from verificar_correcciones import leer_datafile  # noqa: E402
    b28 = pd.read_csv(AQUI / "ben2025_tabla_2_28.csv", index_col="anio")
    uso = {e: uso_combustible(EX / f"{e}_0" / f"{e}_0_Output.csv") for e in ESC
           if (EX / f"{e}_0" / f"{e}_0_Output.csv").exists()}
    ant = uso_combustible(output_anterior(anterior, "CONA6"))[0] if anterior else None
    filas = []
    for y in range(2015, 2026):
        tot = {k: 0.0 for k in ("BEN", "NDCCON", "INCA6", "CONA6", "ant")}
        for f in ("E1CRU", "E1NGS", "E1DSL", "E1FO1", "GLP"):
            kbep = float(sum(b28.loc[y, c] for c in BEN_COMB[f]))
            v = {"BEN": kbep * PJ_KBEP, **{e: uso[e][0][(f, y)] for e in ("NDCCON", "INCA6", "CONA6")},
                 "ant": ant[(f, y)] if ant else None}
            for k in tot:
                tot[k] += v[k] or 0.0
            filas.append({"anio": y, "combustible": NOMBRE_COMB[f], "BEN_kBEP": kbep, **{f"{k}_PJ": v[k] for k in v}})
        filas.append({"anio": y, "combustible": "total fósil", "BEN_kBEP": None, **{f"{k}_PJ": tot[k] for k in tot}})
    t = pd.DataFrame(filas).rename(columns={"ant_PJ": "CONA6_version_anterior_PJ", "NDCCON_PJ": "CLG_NDCCON_PJ"})
    for c, col in (("CLG", "CLG_NDCCON_PJ"), ("INCA6", "INCA6_PJ"), ("CONA6", "CONA6_PJ"),
                   ("CONA6_version_anterior", "CONA6_version_anterior_PJ")):
        t[f"desvio_{c}_pct"] = (t[col] - t.BEN_PJ) / t.BEN_PJ * 100
    if not anterior:
        t = t.drop(columns=["CONA6_version_anterior_PJ", "desvio_CONA6_version_anterior_pct"])
    t["nota"] = t.combustible.map({"gas licuado (PPILPG)": "modelo: actividad de PPILPG (sin IAR; el EAR trata la "
                                                             "actividad como combustible)",
                                   "fuel oil y crudo reducido": "BEN: fuel oil + crudo reducido (E1FO1 del modelo)"}) \
        .fillna("")
    t.round(4).to_csv(AQUI / "calibracion_b_combustible_ben.csv", index=False)
    # rendimientos
    ins = json.loads((AQUI / "correcciones_K_insumos.json").read_text(encoding="utf-8"))["derivaciones"]["K13"]
    grupo_de = {"PPNGS": "centrales", "PPDSL": "centrales", "PPDDSL": "centrales", "PPDFOI": "centrales",
                "PPRNGS": "autoproductores", "PPRDSL": "autoproductores", "PPCRU": "mezcla", "PPFOI": "mezcla"}
    d_c = leer_datafile(EX / "CONA6_0" / "CONA6_0.txt")
    d_o = leer_datafile(EX / "NDCCON_0" / "NDCCON_0.txt")
    filas = []
    for tec, f in COMB_TEC.items():
        for y in range(2010, 2036):
            i_o = d_o[("InputActivityRatio", tec, f, "1", str(y))][0]
            i_c = d_c[("InputActivityRatio", tec, f, "1", str(y))][0]
            g = ins["IAR_grupo"].get(grupo_de[tec], {}).get(str(y)) if grupo_de[tec] != "mezcla" else None
            filas.append({"tecnologia": tec, "combustible": f, "anio": y, "IAR_CLG": i_o, "IAR_CONA6": i_c,
                          "rendimiento_CLG_pct": round(100 / i_o, 2), "rendimiento_CONA6_pct": round(100 / i_c, 2),
                          "grupo_BEN": grupo_de[tec], "IAR_grupo_BEN": g,
                          "generacion_CONA6_GWh": round(float(r["CONA6"]["act"].loc[tec, y]) * PJ, 1),
                          "combustible_CONA6_PJ": round(uso["CONA6"][1].get((tec, y), 0.0), 4),
                          "origen_IAR_CONA6": "CLG (2010 intacto)" if y == 2010 else
                          "K13g: IAR diésel de PPDSL del CLG" if (tec == "PPDDSL" and y < 2015) else
                          "CLG (sin BEN antes de 2015)" if y < 2015 else
                          ("K13a: BEN 3.12-3.15 y 2.28" if y <= 2025 else "K13a: medio observado 2023-2025")})
    pd.DataFrame(filas).to_csv(AQUI / "calibracion_b_rendimientos.csv", index=False)
    # INGEI 2022, 1A1 por combustible (incluye refinación, 1A1b): contraste
    filas = []
    md5_ingei = None
    if INGEI_LARGO.exists():
        md5_ingei = md5(INGEI_LARGO)
        g = pd.read_csv(INGEI_LARGO, encoding="utf-8-sig")
        g = g[(g.dimension == "categoria_principal_energia") & (g.codigo == "1A1") & (g.anio == 2022) & (g.gas == "CO2")]
        for _, x in g.iterrows():
            comb = x.nombre.split(" / ", 1)[1]
            f = INGEI_COMB.get(comb)
            fila = {"combustible_INGEI": comb, "INGEI_1A1_CO2_kt": round(float(x.valor), 2), "fuente_INGEI": x.fuente}
            if f:
                ben = float(sum(b28.loc[2022, c] for c in BEN_COMB[f])) * PJ_KBEP * CO2_TJ[f]
                fila.update({"BEN_2_28_x_factor_CO2_kt": round(ben, 2),
                             "CONA6_CO2_kt": round(uso["CONA6"][0][(f, 2022)] * CO2_TJ[f], 2),
                             "CLG_NDCCON_CO2_kt": round(uso["NDCCON"][0][(f, 2022)] * CO2_TJ[f], 2),
                             "comparable": "sí" if f in ("E1CRU", "E1NGS") else
                             "no: el INGEI 1A1 incluye la refinación (1A1b, 1.249 kt CO2-eq en 2022)"})
                if f in ("E1CRU", "E1NGS"):
                    fila["desvio_CONA6_pct"] = round((fila["CONA6_CO2_kt"] - fila["INGEI_1A1_CO2_kt"]) /
                                                     fila["INGEI_1A1_CO2_kt"] * 100, 2)
                    fila["desvio_CLG_NDCCON_pct"] = round((fila["CLG_NDCCON_CO2_kt"] - fila["INGEI_1A1_CO2_kt"]) /
                                                      fila["INGEI_1A1_CO2_kt"] * 100, 2)
            else:
                fila["comparable"] = "no: combustible sin térmica en el modelo (refinación u otros)"
            filas.append(fila)
    pd.DataFrame(filas).to_csv(AQUI / "calibracion_b_combustible_ingei_2022.csv", index=False)
    return t, filas, md5_ingei


RED = ("PPFOI", "PPDSL", "PPNGS")          # térmicas de la red (S.N.I.) que desplazan A, B y C
DISTRIBUIDA = ("PPDFOI", "PPDDSL")          # térmica de las distribuidoras (S.N.I.)
# MAE, Comisión Técnica de Factores de Emisión, Informe del Factor de Emisión de CO2 del S.N.I. 2025, tabla 6, p. 17
# (S26-065): lambda, emisiones y generación neta de los generadores de no bajo costo, margen de operación simple ajustado
CTFE = {"lambda": 0.1741, "t_CO2": 3836232.0, "MWh_neta": 4978520.0, "OM": 0.6364}
# CENACE, Informe Anual 2025, Parte 1: térmica neta por combustible (figura 1.10, p. 40: 4.952,41 GWh) y bruta por
# combustible (figura 1.7, p. 34: 5.136,35 GWh); la razón pasa el factor del modelo (generación bruta del BEN) a neto
NETA_BRUTA = 4952.41 / 5136.35
T_MWH = 1e6 / (PJ * 1000)  # Mt/PJ -> t/MWh (1 PJ = 277.780 MWh)


def valores_df(esc):
    sys.path.insert(0, str(AQUI))
    from verificar_correcciones import leer_datafile  # noqa: E402
    return {k: v for k, (v, _) in leer_datafile(EX / f"{esc}_0" / f"{esc}_0.txt").items()}


def tablas_termica_red(r, ins):
    """Suficiencia de la expansión térmica declarada (K15b) y trayectoria de las térmicas de la red 2026-2035."""
    Y = list(range(2026, 2036))
    obs = {t: sum(ins["K13"]["generacion_PJ"][t][str(y)] for y in (2023, 2024, 2025)) / 3 for t in RED}
    decl = ins.get("K15b", {}).get("declarada_por_anio_MW", {})
    # potencia arrendada vigente en cada año (K15c, caso central): MW x fracción del año de contrato
    arr = {}
    for a_ in ins.get("K15c", {}).get("arriendos", []):
        for y, v in a_.get("MW_equivalentes_fin_" + ins["K15c"]["variante_central"], {}).items():
            arr[(a_["tecnologia"], int(y))] = arr.get((a_["tecnologia"], int(y)), 0.0) + v
    suf, tray = [], []
    for e in ("CONA6", "CONA6G", "INCA6", "INCA6G", "NDCCON", "NDCINC"):
        if "act" not in r[e]:  # sin salida de B1 (variante de suficiencia)
            continue
        d = valores_df(e)
        for t in RED:
            acum_n = acum_d = 0.0
            for y in Y:
                cap = float(r[e]["cap"].loc[t, y]) if t in r[e]["cap"].index else 0.0
                nue = float(r[e]["nueva"].loc[t, y]) if t in r[e]["nueva"].index else 0.0
                act = float(r[e]["act"].loc[t, y]) if t in r[e]["act"].index else 0.0
                cf = d.get(("CapacityFactor", t, "All", str(y)), 1.0)
                lim = cap * cf * 31.536
                acum_n += nue
                fila_t = {"escenario": ("CLG_" + e) if e in ("NDCCON", "NDCINC") else e, "tecnologia": t, "anio": y,
                          "potencia_nueva_MW": round(nue * 1000, 2), "potencia_total_MW": round(cap * 1000, 2),
                          "residual_MW": round(d.get(("ResidualCapacity", t, str(y)), 0.0) * 1000, 2),
                          "CF": cf, "actividad_PJ": round(act, 4), "actividad_GWh": round(act * PJ, 1),
                          "limite_potencia_x_CF_PJ": round(lim, 4),
                          "piso_PJ": d.get(("TotalTechnologyAnnualActivityLowerLimit", t, str(y))),
                          "techo_PJ": d.get(("TotalTechnologyAnnualActivityUpperLimit", t, str(y))),
                          "media_observada_2023_2025_PJ": round(obs[t], 4),
                          "actividad_sobre_observado": round(act / obs[t], 3) if obs[t] else None}
                tray.append(fila_t)
                if e in ("NDCCON", "NDCINC"):
                    continue
                tope = d.get(("TotalAnnualMaxCapacity", t, str(y)))
                dec_y = float(decl.get(t, {}).get(str(y), decl.get(t, {}).get(y, 0.0)))
                acum_d += dec_y
                sto = float(r[e]["act"].loc["STOELE", y]) if "STOELE" in r[e]["act"].index else 0.0
                suf.append({"escenario": e, "tecnologia": t, "anio": y, "declarada_propia_del_anio_MW": dec_y,
                            "declarada_propia_acumulada_MW": acum_d, "potencia_nueva_MW": round(nue * 1000, 2),
                            "potencia_nueva_acumulada_MW": round(acum_n * 1000, 2),
                            "residual_MW": fila_t["residual_MW"],
                            "de_ello_arrendada_vigente_MW": round(arr.get((t, y), 0.0), 2),
                            "tope_K15b_MW": round(tope * 1000, 2) if tope else None,
                            "potencia_total_MW": fila_t["potencia_total_MW"],
                            "holgura_MW": round((tope - cap) * 1000, 2) if tope else None,
                            "tope_activo": bool(tope is not None and tope - cap < 5e-5),
                            "inversion_del_anio_dentro_de_lo_declarado": bool(nue * 1000 <= dec_y + 0.05),
                            "inversion_acumulada_dentro_de_lo_declarado": bool(acum_n * 1000 <= acum_d + 0.05),
                            "actividad_PJ": fila_t["actividad_PJ"], "limite_potencia_x_CF_PJ": fila_t["limite_potencia_x_CF_PJ"],
                            "techo_actividad_PJ": fila_t["techo_PJ"], "CF": cf,
                            "STOELE_del_escenario_GWh": round(sto * PJ, 1)})
    pd.DataFrame(tray).to_csv(AQUI / "calibracion_d_termica_red_2026_2035.csv", index=False)
    s = pd.DataFrame(suf)
    s.to_csv(AQUI / "calibracion_g_suficiencia_termica.csv", index=False)
    return pd.DataFrame(tray), s


def tabla_factor(r, ins):
    """Factor de emisión del MWh desplazado (térmica de la red sobre su piso) y promedio de la generación fósil de la red
    (S.N.I.: PPFOI, PPDSL, PPNGS y la térmica de las distribuidoras), 2025-2035, frente al margen de operación de 2025."""
    b3 = pd.read_csv(AQUI / "ben2025_tablas_3_12_a_3_15.csv")
    B25 = b3[(b3.grupo == "autoproductores") & (b3.anio == 2025)].iloc[0]
    ib25 = ins["K13"]["IAR_grupo"]["autoproductores"]["2025"]
    fo_b = (B25.fuel_oil_kBEP + B25.crudo_reducido_kBEP) * PJ_KBEP  # PJ de combustible de autoproductores en PPFOI
    gen_b = fo_b / ib25
    ef_ctfe = CTFE["t_CO2"] / CTFE["MWh_neta"]
    ruta_p = AQUI / "calibracion_f_desplazado_perturbacion.csv"
    pert = pd.read_csv(ruta_p) if ruta_p.exists() else None
    filas = []
    for e in ("CONA6", "CONA6G", "NDCCON", "INCA6"):
        d = valores_df(e)
        for y in range(2025, 2036):
            act = {t: float(r[e]["act"].loc[t, y]) if t in r[e]["act"].index else 0.0 for t in RED + DISTRIBUIDA}
            ear = {(t, g): d[("EmissionActivityRatio", t, g, "1", str(y))] for t in RED + DISTRIBUIDA
                   for g in ("CO2_PP", "CO2e_PP")}
            piso = {t: d.get(("TotalTechnologyAnnualActivityLowerLimit", t, str(y)), 0.0) for t in RED}
            techo = {t: d.get(("TotalTechnologyAnnualActivityUpperLimit", t, str(y)), 999.0) for t in RED}
            lim = {t: (float(r[e]["cap"].loc[t, y]) if t in r[e]["cap"].index else 0.0) *
                   d.get(("CapacityFactor", t, "All", str(y)), 1.0) * d.get(("AvailabilityFactor", t, str(y)), 1.0) * 31.536
                   for t in RED}
            sobre = {t: max(0.0, act[t] - piso[t]) for t in RED}
            sobre = {t: v for t, v in sobre.items() if v > 1e-5}
            # el marginal ponderado mezcla las térmicas sobre su piso; el que el modelo desplaza
            # de verdad lo mide la perturbación (calibracion_f_desplazado_perturbacion.csv, variante_suficiencia.py
            # --desplazado): demanda eléctrica -1 % y caída de CO2e_PP sobre caída de la generación
            en_techo = [t for t in sobre if act[t] >= min(techo[t], lim[t]) - 1e-4]
            fila = {"escenario": ("CLG_" + e) if e == "NDCCON" else e, "anio": y,
                    "tecnologias_sobre_su_piso": "; ".join(f"{t} {v * PJ:.0f} GWh" for t, v in sobre.items()),
                    "sobre_su_piso_en_su_techo_o_potencia": "; ".join(en_techo) or "ninguna"}
            pt = pert[(pert.escenario == e) & (pert.anio == y)] if pert is not None else None
            if pt is not None and len(pt):
                fila.update({"perturbacion_factor_CO2_t_MWh_neto": float(pt.factor_CO2_t_MWh_neto.iloc[0]),
                             "perturbacion_factor_CO2e_t_MWh_neto": float(pt.factor_CO2e_t_MWh_neto.iloc[0]),
                             "perturbacion_tecnologias_que_bajan_GWh": pt.cambio_por_tecnologia_GWh.iloc[0]})
            for g, et in (("CO2_PP", "CO2"), ("CO2e_PP", "CO2e")):
                if sobre:
                    m = sum(v * ear[(t, g)] for t, v in sobre.items()) / sum(sobre.values()) * T_MWH
                    fila[f"marginal_{et}_t_MWh_bruto"] = round(m, 4)
                    fila[f"marginal_{et}_t_MWh_neto"] = round(m / NETA_BRUTA, 4)
                tot = RED + DISTRIBUIDA
                prom = sum(act[t] * ear[(t, g)] for t in tot) / sum(act[t] for t in tot) * T_MWH
                fila[f"promedio_red_{et}_t_MWh_bruto"] = round(prom, 4)
                fila[f"promedio_red_{et}_t_MWh_neto"] = round(prom / NETA_BRUTA, 4)
            for t in RED:
                fila[f"factor_{t}_CO2_t_MWh_bruto"] = round(ear[(t, "CO2_PP")] * T_MWH, 4)
            if y == 2025:
                # perímetro S.N.I.: PPFOI incluye el fuel oil y el crudo reducido de autoproductores (K13); se retira
                em = sum(act[t] * ear[(t, "CO2_PP")] for t in RED + DISTRIBUIDA) - fo_b * 77.4 / 1000
                gen = sum(act[t] for t in RED + DISTRIBUIDA) - gen_b
                p_sni = em / gen * T_MWH
                fila["promedio_SNI_sin_autoproductores_CO2_t_MWh_bruto"] = round(p_sni, 4)
                fila["promedio_SNI_sin_autoproductores_CO2_t_MWh_neto"] = round(p_sni / NETA_BRUTA, 4)
                fila["parte_de_PPFOI_de_autoproductores"] = round(gen_b / act["PPFOI"], 4) if act["PPFOI"] else None
                fila["OM_equivalente_modelo_t_CO2_MWh"] = round((1 - CTFE["lambda"]) * p_sni / NETA_BRUTA, 4)
            fila.update({"CTFE_promedio_no_bajo_costo_2025_t_CO2_MWh_neto": round(ef_ctfe, 4),
                         "CTFE_lambda_2025": CTFE["lambda"], "CTFE_OM_2025_t_CO2_MWh": CTFE["OM"]})
            filas.append(fila)
    f = pd.DataFrame(filas)
    f.to_csv(AQUI / "calibracion_f_factor_desplazado.csv", index=False)
    return f


def main():
    import argparse
    p_ = argparse.ArgumentParser()
    p_.add_argument("--anterior", help="carpeta con CONA6 (o CONA6_0)/CONA6_0_Output.csv de la versión anterior")
    anterior = p_.parse_args().anterior
    # una referencia sin _Output.csv es una corrida de B1 sin solución factible (K15b: hallazgo de suficiencia); su CO2e_PP
    # 2026-2035 sale de la variante de mínima inversión extra (variante_suficiencia.py) y se rotula así
    sin_salida = [e for e in ESC if not (EX / f"{e}_0" / f"{e}_0_Output.csv").exists()]
    if any(e in ("NDCINC", "NDCCON", "INCA6", "CONA6") for e in sin_salida):
        raise SystemExit(f"falta la salida de {sin_salida}")
    r = {e: leer_output(e) for e in ESC if e not in sin_salida}
    ear = {e: ear_co2e(e) for e in ESC}
    variante_co2 = {}
    if sin_salida:
        sv = pd.read_csv(AQUI / "calibracion_g_suficiencia_variante.csv")
        for e in sin_salida:
            x = sv[(sv.escenario == e) & (sv.vigencia_arriendos.astype(str) == "2028")].set_index("anio")
            if x.empty or x.CO2e_PP_variante_kt.isna().any():
                raise SystemExit(f"{e}: sin salida de B1 ni variante de suficiencia resuelta")
            variante_co2[e] = x.CO2e_PP_variante_kt.astype(float)
            base = {"INCA6G": "INCA6", "CONA6G": "CONA6"}[e]
            # 2010-2025 iguales a la referencia central (la sensibilidad de gas solo cambia 2026-2035)
            r[e] = {"co2": pd.concat([r[base]["co2"].loc[:2025], variante_co2[e]]), "variante": True}
    t5 = pd.read_csv(AQUI / "tabla5_ficha_p19.csv", index_col="anio")
    ben = pd.read_csv(AQUI / "ben2025_tabla_2_20.csv", index_col="anio")
    pot = pd.read_csv(AQUI / "ben2025_tabla_2_23.csv", index_col="anio")
    sgda = pd.read_csv(AQUI / "ben2025_tabla_2_25_sgda.csv", index_col="anio").sgda_MW
    b19 = pd.read_csv(AQUI / "ben2025_tabla_2_19.csv", index_col="anio")
    for e in ESC:  # control: actividad x EAR reproduce AnnualTechnologyEmission
        if e in sin_salida:
            continue
        calc = (r[e]["act"].reindex(ear[e].index).fillna(0) * ear[e].reindex(columns=r[e]["act"].columns)).sum() * 1000
        dmax = (calc - r[e]["co2"].reindex(calc.index).fillna(0)).abs().max()
        if dmax > 1.0:
            raise SystemExit(f"{e}: actividad x EAR no reproduce CO2e_PP (dif. {dmax:.2f} kt)")
    # la sensibilidad de gas solo cambia 2026-2035: en 2010-2025 INCA6G y CONA6G deben ser INCA6 y CONA6
    for g_, b_ in (("INCA6G", "INCA6"), ("CONA6G", "CONA6")):
        if g_ in sin_salida:
            continue
        dif = (r[g_]["co2"] - r[b_]["co2"]).loc[2010:2025].abs().max()
        if dif > 0.05:
            raise SystemExit(f"{g_} difiere de {b_} en 2010-2025 ({dif:.2f} kt)")
    # (a) Tabla 5
    a = pd.DataFrame(index=t5.index)
    a["ingei_kt"] = t5.ingei_kt
    a["ficha_publicada_kt"] = t5.modelo_publicado_kt
    a["CLG_NDCCON_kt"] = r["NDCCON"]["co2"].reindex(a.index)
    a["INCA6_kt"] = r["INCA6"]["co2"].reindex(a.index)
    a["CONA6_kt"] = r["CONA6"]["co2"].reindex(a.index)
    for c_, col in (("ficha_publicada", "ficha_publicada_kt"), ("CLG", "CLG_NDCCON_kt"), ("INCA6", "INCA6_kt"),
                    ("CONA6", "CONA6_kt")):
        a[f"error_{c_}_pct"] = (a.ingei_kt - a[col]) / a.ingei_kt * 100
    ant = anterior_tabla("calibracion_a_tabla5_v3.csv")
    if ant is not None:
        ant = ant.set_index("anio")
        a["CONA6_version_anterior_kt"] = ant.CONA6_kt
        a["error_CONA6_version_anterior_pct"] = ant.error_CONA6_pct
    a["NDCINC_igual_NDCCON"] = (r["NDCINC"]["co2"] - r["NDCCON"]["co2"]).reindex(a.index).abs() < 0.05
    a["INCA6G_y_CONA6G_iguales_a_INCA6_y_CONA6"] = True  # comprobado arriba para 2010-2025
    a.round(2).to_csv(AQUI / "calibracion_a_tabla5.csv", index_label="anio")
    # (b) generación por fuente frente al BEN 2.20
    filas = []
    for y in range(2010, 2026):
        for f in list(FAMILIAS) + ["total"]:
            b = (float(ben.loc[y].sum()) if f == "total" else float(ben.loc[y, f])) \
                if (y in ben.index and (f == "total" or f in ben.columns)) else None
            val = {e: float(r[e]["gen"].loc[y].sum() if f == "total" else r[e]["gen"].loc[y, f]) for e in ESC
                   if "gen" in r[e]}
            filas.append({"anio": y, "fuente": f, "BEN_GWh": b, "CLG_NDCCON_GWh": round(val["NDCCON"], 1),
                          "INCA6_GWh": round(val["INCA6"], 1), "CONA6_GWh": round(val["CONA6"], 1),
                          "desvio_CLG_pct": round((val["NDCCON"] - b) / b * 100, 2) if b else None,
                          "desvio_CONA6_pct": round((val["CONA6"] - b) / b * 100, 2) if b else None,
                          "nota": "" if y >= 2015 else "la tabla 2.20 del BEN 2025 empieza en 2015"})
    gen_b = pd.DataFrame(filas)
    gen_b.to_csv(AQUI / "calibracion_b_generacion_ben.csv", index=False)
    # (b) potencia por fuente frente al BEN 2.23
    fu = pd.read_csv(AQUI / "capacidad_bio_fuentes.csv")
    # ARCONEL, Estadística Anual y Multianual 2025, tablas 18 (nominal) y 19 (efectiva), p. 33: potencia nominal del
    # modelo con nominal (hidro y térmica fósil) y efectiva con efectiva (eólica, solar, biomasa y biogás, que el modelo
    # toma del BEN 2.23 o de la tabla 19)
    a18 = pd.read_csv(AQUI / "arconel2025_tablas_18_19.csv")
    arc1819 = {}
    for r_ in a18.itertuples():
        arc1819[(r_.anio, r_.tipo, "nominal")] = r_.nominal_MW
        arc1819[(r_.anio, r_.tipo, "efectiva")] = r_.efectiva_MW
    mw_fuente = {(f.tecnologia, y): f.MW for f in fu.itertuples() for y in range(f.anio_desde, f.anio_hasta + 1)}
    filas = []
    for e in ("NDCCON", "CONA6", "INCA6"):
        cap, nue = r[e]["cap"] * 1000, r[e]["nueva"] * 1000
        techs = list(cap.index)
        for y in range(2015, 2026):
            def s(fn):
                return float(cap.loc[[t for t in techs if fn(t)], y].sum())
            fam = {"hidraulica": s(FAMILIAS["hidraulica"]), "eolica": s(FAMILIAS["eolica"]),
                   "solar": s(FAMILIAS["solar"]),
                   "termica_fosil_mas_biomasa_y_biogas": s(lambda t: t in FOSILES_CAP or t in ("PPIBIM", "PPBIM", "PPBGS")),
                   "biomasa_PPIBIM": s(lambda t: t == "PPIBIM"), "biogas_PPBGS": s(lambda t: t == "PPBGS"),
                   "termica_fosil": s(lambda t: t in FOSILES_CAP), "solar_centrales_PPPVT": s(lambda t: t == "PPPVT")}
            bp = pot.loc[y]
            ref = {"hidraulica": bp.hidraulica, "eolica": bp.eolica, "solar": bp.solar,
                   "termica_fosil_mas_biomasa_y_biogas": bp.termica_turbovapor + bp.termica_turbogas + bp.termica_mci,
                   "biomasa_PPIBIM": mw_fuente.get(("PPIBIM", y)), "biogas_PPBGS": mw_fuente.get(("PPBGS", y)),
                   "termica_fosil": None, "solar_centrales_PPPVT": None}
            for f, v in fam.items():
                b = ref[f]
                tipo_arc, clave_arc = ARC_TIPO.get(f, (None, None))
                b_arc = arc1819.get((y, clave_arc, tipo_arc)) if tipo_arc else None
                nota = ""
                if f == "solar":
                    nota = (f"BEN incluye SGDA ({sgda[y]:g} MW, tabla 2.25); capacidad nueva de PPPVT en el año "
                            f"{float(nue.loc['PPPVT', y]) if 'PPPVT' in nue.index else 0:.1f} MW")
                if f == "eolica" and y == 2022:
                    nota = ("el BEN 2.23 suma en 2022 29 MW de Huascachaca; la capa CENTRALES la registra con inicio el "
                            "31-03-2023 y el modelo la cuenta desde 2023 (K11a)")
                if f == "termica_fosil_mas_biomasa_y_biogas":
                    nota = (f"BEN: turbovapor (incluye bagazo) + turbogas + MCI (incluye biogás); sin grupos "
                            f"electrógenos de emergencia ({bp.grupos_electrogenos_emergencia:g} MW)")
                if f == "hidraulica":
                    nota = f"PPHD (hidro distribuida) aporta {float(cap.loc['PPHD', y]) if 'PPHD' in cap.index else 0:.1f} MW"
                if f.startswith(("biomasa", "biogas")):
                    nota = ("fuente: capacidad_bio_fuentes.csv, potencia efectiva de ARCONEL (Estadística Anual y "
                            "Multianual 2025, tabla 19); el BEN 2.23 las incluye en térmica")
                if f == "termica_fosil":
                    nota = ("potencia nominal del modelo (Energy.xlsx y altas de la capa, K15c desde 2023) frente a la "
                            "nominal no renovable de ARCONEL (tabla 18), que incluye sistemas no incorporados")
                if f == "solar_centrales_PPPVT":
                    nota = "PPPVT (centrales del SNI, potencia efectiva del BEN 2.23 sin SGDA) frente a la fotovoltaica efectiva de ARCONEL (tabla 19)"
                filas.append({"escenario": ("CLG_" + e) if e == "NDCCON" else e, "anio": y, "fuente": f,
                              "modelo_MW": round(v, 1), "BEN_o_fuente_MW": b,
                              "desvio_pct": round((v - b) / b * 100, 2) if b else None,
                              "tipo_ARCONEL": tipo_arc, "ARCONEL_2025_MW": b_arc,
                              "desvio_ARCONEL_pct": round((v - b_arc) / b_arc * 100, 2) if b_arc else None,
                              "nota": nota})
    pd.DataFrame(filas).to_csv(AQUI / "calibracion_b_potencia_ben.csv", index=False)
    # (c) vertido por año y su contraste con la tabla 2.19
    ph = pisos_hidro("CONA6")
    filas = []
    for y in range(2010, 2036):
        fila = {"anio": y}
        for e in ("NDCCON", "INCA6", "CONA6", "CONA6G"):
            vt = r[e]["vertido"].loc[y] if y in r[e]["vertido"].index else pd.Series(dtype=float)
            fila[f"vertido_{'CLG_' if e == 'NDCCON' else ''}{e}_GWh"] = round(float(vt.sum()), 1)
        fila["vertido_CONA6_E1ELE_GWh"] = round(float(r["CONA6"]["vertido"].loc[y, "E1ELE"]), 1)
        if y in b19.index:
            g_m = float(r["CONA6"]["gen_balance"][y])
            g_b = float(b19.loc[y, "produccion"] + b19.loc[y, "importacion"])
            fila["CONA6_hidro_GWh"] = round(float(r["CONA6"]["hidro"][y]), 1)
            fila["CONA6_suma_pisos_hidro_GWh"] = round(ph[y], 1)
            fila["BEN_hidro_GWh"] = float(ben.loc[y, "hidraulica"])
            fila["CONA6_generacion_fuera_del_balance_GWh"] = round(float(r["CONA6"]["gen"].loc[y].sum()) - g_m, 1)
            fila.update({
                "BEN_exportacion_GWh": b19.loc[y, "exportacion"], "BEN_consumo_propio_GWh": b19.loc[y, "consumo_propio"],
                "BEN_perdidas_GWh": b19.loc[y, "perdidas"], "CONA6_perdidas_GWh": round(float(r["CONA6"]["perdidas"][y]), 1),
                "BEN_consumo_final_GWh": b19.loc[y, "consumo_energetico"],
                "CONA6_consumo_final_GWh": round(float(r["CONA6"]["consumo"][y]), 1),
                "BEN_ajuste_GWh": b19.loc[y, "ajuste"],
                "CONA6_generacion_al_balance_menos_BEN_GWh": round(g_m - g_b, 1)})
            fila["explicacion_GWh"] = round(fila["BEN_exportacion_GWh"] + fila["BEN_consumo_propio_GWh"] +
                                            (fila["BEN_perdidas_GWh"] - fila["CONA6_perdidas_GWh"]) +
                                            (fila["BEN_consumo_final_GWh"] - fila["CONA6_consumo_final_GWh"]) +
                                            fila["BEN_ajuste_GWh"] + fila["CONA6_generacion_al_balance_menos_BEN_GWh"],
                                            1)
        filas.append(fila)
    vert = pd.DataFrame(filas)
    vert.to_csv(AQUI / "calibracion_c_vertido.csv", index=False)
    # (d) puente 2026-2035 con descomposición actividad / factores; tramo 2026-2028 aparte; rango central-gas
    Y = list(range(2026, 2036))
    c = pd.DataFrame(index=Y)
    c["tramo"] = ["2026-2028" if y <= 2028 else "2029-2035" for y in Y]
    for e in ESC:
        c[f"{e}_kt"] = r[e]["co2"].reindex(Y)
    for clon, of in PARES:
        c[f"{clon}_menos_{of}_kt"] = c[f"{clon}_kt"] - c[f"{of}_kt"]
        if clon in sin_salida:
            c[f"{clon}_fuente"] = ("variante de suficiencia: B1 sin solución factible con la expansión declarada; tope de "
                                   "PPFOI liberado en 2026-2035 (calibracion_g_suficiencia_variante.csv)")
            continue
        if clon == "INCA6G":
            # filas RE01 (13-10-2026): supuesto de cierre aprobado después de la verificación
            c[f"{clon}_fuente"] = ("salida de B1 con las filas RE01: con cierre de fuel oil de emergencia (respaldo de "
                                   "PPFOI sobre el tope K15b; peso en B2_Output_Art6/tablas/respaldo_por_escenario.csv)")
        act = r[clon]["act"].reindex(ear[of].index).fillna(0)[Y]
        con_fac_of = (act * ear[of][Y]).sum() * 1000
        c[f"{clon}_efecto_actividad_kt"] = con_fac_of - c[f"{of}_kt"]
        c[f"{clon}_efecto_factores_kt"] = c[f"{clon}_kt"] - con_fac_of
    ant = anterior_tabla("calibracion_d_puente_v3.csv")
    if ant is not None:
        ant = ant.set_index(ant.anio.astype(str))
        for col in ("CONA6_menos_NDCCON_kt", "INCA6_menos_NDCINC_kt"):
            c[col.replace("_kt", "_version_anterior_kt")] = [float(ant[col].get(str(y))) for y in Y]
    sumas = []
    for nombre, ys in (("suma 2026-2028", [2026, 2027, 2028]), ("suma 2029-2035", list(range(2029, 2036))),
                       ("suma 2031-2035", list(range(2031, 2036))), ("suma 2026-2035", Y)):
        s_ = c.loc[ys].drop(columns=[k for k in c.columns if c[k].dtype == object]).sum()
        s_["tramo"] = nombre
        sumas.append(s_.rename(nombre))
    d = pd.concat([c, pd.DataFrame(sumas)])
    for fam, (cen, gas) in (("INC", ("INCA6_menos_NDCINC_kt", "INCA6G_menos_NDCINC_kt")),
                            ("CON", ("CONA6_menos_NDCCON_kt", "CONA6G_menos_NDCCON_kt"))):
        d[f"rango_{fam}_min_kt"] = d[[cen, gas]].min(axis=1)
        d[f"rango_{fam}_max_kt"] = d[[cen, gas]].max(axis=1)
    d.round(2).to_csv(AQUI / "calibracion_d_puente.csv", index_label="anio")
    g = pd.concat({e: r[e]["gen"].loc[Y] for e in ESC if "gen" in r[e]}, axis=1).round(1)
    g.to_csv(AQUI / "calibracion_d_generacion_2026_2035.csv", index_label="anio")
    # (b) combustible por tipo frente al BEN 2.28, rendimientos y contraste con el INGEI 2022 por combustible
    comb_b, ingei_b, md5_ingei = tablas_combustible(r, anterior)
    # (d) actividad térmica observada 2023-2025 frente a 2026-2035 (K14 ancla la de los autoproductores y PPILPG)
    ins = json.loads((AQUI / "correcciones_K_insumos.json").read_text(encoding="utf-8"))["derivaciones"]
    obs = {t: [ins["K13"]["generacion_PJ"][t][str(y)] for y in (2023, 2024, 2025)] for t in FOSILES}
    obs["PPILPG"] = [ins["K13"]["GLP_autoproductores_PJ"][str(y)] for y in (2023, 2024, 2025)]
    k14 = set(ins.get("K14", {}))
    k15a = {t for t, v in ins.get("K15a", {}).items() if v.get("aplica")}
    d_c, d_o = valores_df("CONA6"), valores_df("NDCCON")
    disc = []
    for t in FOSILES + ("PPILPG",):
        fila = {"tecnologia": t}
        for y in (2023, 2024, 2025, 2026):
            fila[f"CF_CONA6_{y}"] = d_c.get(("CapacityFactor", t, "All", str(y)))
        fila["CF_CLG_2026"] = d_o.get(("CapacityFactor", t, "All", "2026"))
        fila["residual_CONA6_2025_MW"] = round(d_c.get(("ResidualCapacity", t, "2025"), 0.0) * 1000, 2)
        fila["residual_CLG_2025_MW"] = round(d_o.get(("ResidualCapacity", t, "2025"), 0.0) * 1000, 2)
        fila["potencia_nueva_CONA6_2026_MW"] = round(float(r["CONA6"]["nueva"].loc[t, 2026]) * 1000, 2)             if t in r["CONA6"]["nueva"].index else 0.0
        m = sum(obs[t]) / 3
        fila["observado_media_2023_2025_PJ"] = round(m, 4)
        for e in ("CONA6", "CONA6G", "NDCCON"):
            for y in (2023, 2024, 2025, 2026, 2030, 2035):
                fila[f"{'CLG_' if e == 'NDCCON' else ''}{e}_{y}_PJ"] = \
                    round(float(r[e]["act"].loc[t, y]) if t in r[e]["act"].index else 0.0, 4)
        fila["CONA6_2026_sobre_observado"] = round(fila["CONA6_2026_PJ"] / m, 3) if m else None
        fila["CLG_NDCCON_2026_sobre_observado"] = round(fila["CLG_NDCCON_2026_PJ"] / m, 3) if m else None
        fila["piso_CONA6_2026_PJ"] = d_c.get(("TotalTechnologyAnnualActivityLowerLimit", t, "2026"))
        fila["techo_CONA6_2026_PJ"] = d_c.get(("TotalTechnologyAnnualActivityUpperLimit", t, "2026"))
        if t == "PPILPG":
            nota = "actividad = combustible (GLP); desde 2026 K14 la ancla a la media observada 2023-2025"
        elif t == "PPCRU":
            k = ins["K14"]["PPCRU_crudo_de_centrales"]
            nota = (f"2015-2025 observado (K13); desde 2026 K14 la ancla a {k['ancla_PPCRU_PJ']:.4f} PJ: media 2023-2025 "
                    f"del crudo de autoproductores ({k['media_B_PJ']:.4f}) más el crudo de centrales eléctricas de 2025 "
                    f"({k['A_anclada_PJ']:.4f}); el exceso de 2023-2024 ({k['A_al_despacho_respecto_de_la_media_PJ']:.4f} "
                    "PJ sobre la media) queda al despacho de la red")
        elif t in k14:
            nota = "2015-2025 observado (K13); desde 2026 K14 la ancla a la media observada 2023-2025"
        elif t in ("PPFOI", "PPDSL"):
            nota = ("2015-2025 observado (K13); desde 2026 la optimiza el modelo (techo CLG 999) con el CF medio "
                    "observado 2023-2025 (K15a), la residual K15c con los arriendos vigentes y el tope de potencia K15b"
                    if t in k15a else "2015-2025 observado (K13); desde 2026 la optimiza el modelo (techo CLG 999)")
        elif t == "PPNGS":
            nota = ("2015-2025 observado (K13); desde 2026 piso CLG y techo K15d (1,02 x media observada 2023-2025 + "
                    "energía declarada de la expansión a gas, Anexo A) con el CF K15e; en CONA6G va a su piso (G01)")
        else:
            nota = "2015-2025 observado (K13); desde 2026 piso y techo CLG"
        fila["nota"] = nota
        disc.append(fila)
    pd.DataFrame(disc).to_csv(AQUI / "calibracion_d_discontinuidad_termica.csv", index=False)
    tray, suf = tablas_termica_red(r, ins)
    fac = tabla_factor(r, ins)
    res = {"insumos": {e: {"output_md5": r[e].get("md5", "sin salida de B1: variante de suficiencia"),
                           "datafile_md5": md5(EX / f"{e}_0" / f"{e}_0.txt")} for e in ESC},
           "sin_salida_de_B1": sin_salida,
           "tablas_md5": {p.name: md5(p) for p in sorted(AQUI.glob("ben2025_tabla*.csv"))},
           "inventario_gei_largo_md5": md5_ingei, "version_anterior": anterior,
           "tabla5_md5": md5(AQUI / "tabla5_ficha_p19.csv"),
           "capacidad_bio_fuentes_md5": md5(AQUI / "capacidad_bio_fuentes.csv"),
           "correcciones_K_md5": md5(AQUI / "correcciones_K.csv"),
           "arconel2025_tablas_18_19_md5": md5(AQUI / "arconel2025_tablas_18_19.csv"),
           "construccion_hidro_2024_MW": {e: {t: round(float(r[e]["nueva"].loc[t, 2024]) * 1000, 3)
                                              for t in r[e]["nueva"].index if FAMILIAS["hidraulica"](t)
                                              and float(r[e]["nueva"].loc[t, 2024]) > 0}
                                          for e in ("NDCCON", "CONA6", "INCA6")}}
    (AQUI / "calibracion_resumen.json").write_text(json.dumps(res, indent=1) + "\n", encoding="utf-8")
    pd.set_option("display.width", 250)
    pd.set_option("display.max_columns", 40)
    print(a.round(2).to_string())
    print(gen_b[gen_b.anio >= 2015].pivot(index="anio", columns="fuente", values="desvio_CONA6_pct").to_string())
    print(vert[["anio", "vertido_CLG_NDCCON_GWh", "vertido_CONA6_GWh", "vertido_CONA6G_GWh", "BEN_exportacion_GWh",
                "explicacion_GWh"]].to_string(index=False))
    cols = ["tramo"] + [f"{e}_kt" for e in ESC] + [f"{c_}_menos_{o}_kt" for c_, o in PARES]
    print(d[cols].round(1).to_string())
    print(pd.DataFrame(disc)[["tecnologia", "observado_media_2023_2025_PJ", "CONA6_2026_PJ", "CONA6G_2026_PJ",
                              "CLG_NDCCON_2026_PJ", "CONA6_2026_sobre_observado", "CF_CONA6_2025", "CF_CONA6_2026",
                              "potencia_nueva_CONA6_2026_MW"]].to_string(index=False))
    print(suf[["escenario", "tecnologia", "anio", "declarada_propia_del_anio_MW", "potencia_nueva_MW",
               "de_ello_arrendada_vigente_MW", "tope_K15b_MW", "potencia_total_MW", "tope_activo",
               "inversion_acumulada_dentro_de_lo_declarado", "STOELE_del_escenario_GWh"]]
          [(suf.potencia_nueva_MW > 0) | suf.tope_activo].to_string(index=False))
    print(fac.drop(columns=[c for c in fac.columns if c.startswith("CTFE")]).round(4).to_string(index=False))
    print(json.dumps(res["construccion_hidro_2024_MW"]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
