# -*- coding: utf-8 -*-
"""Extracto de la capa CENTRALES de ARCONEL para las correcciones del Artículo 6 (K04, K06, K11, K12) y la tabla de clases
hidroeléctricas que usará el paso 4 (año seco).

Uso, desde ECU_NDC/Energy:
    python Art6_calibracion/extraer_centrales.py [--capa <ruta local de CENTRALES.dbf>]

Sandbox PNUD: la capa (uso autorizado) y los archivos por central que este script escribe no se distribuyen; el
repositorio lleva solo los parámetros agregados por clase (agregar_por_clase.py). La ruta por omisión se toma de la
variable de entorno ART6_CAPA_CENTRALES.

Fuente: ARCONEL, capa CENTRALES (CENTRALES.shp con su .dbf, 355 registros); uso autorizado;
referencia del oficio [verificar]. Solo se lee la tabla de atributos (.dbf) con un lector propio en Python, sin geometría
ni coordenadas: el Control de aplicaciones de Windows bloquea gdal y la tabla basta. La fecha de la última actualización
del .dbf está en su cabecera.

Escribe en Art6_calibracion:
- centrales_extracto.csv: los registros usados (biomasa, biogás, eólica, solar y las centrales hidroeléctricas de la
  tabla de clases) con las columnas leídas, el uso que se les da y el md5 del .shp y del .dbf.
- centrales_clases.csv: asignación de las centrales hidroeléctricas mayores a las clases del modelo, con potencia
  nominal y efectiva, fecha de inicio, vertiente y la evidencia de la asignación (A2_Output_Params/NDCCON y
  ECU_NDC/Data/Energy.xlsx, hoja Proyectos_Plantas).
- centrales_series.csv: potencia por año 2010-2035 que la capa permite reconstruir con la fecha de inicio (biomasa,
  biogás, eólica del SNI y distribuida, solar del SNI y distribuida).
La capa es una fotografía del parque a la fecha del .dbf: da la fecha de inicio de cada central y su potencia actual,
no la historia de ampliaciones; confirma el parque, no la serie. Una central cuenta en un año si su fecha de inicio es
anterior o igual al 31 de diciembre de ese año y sigue activa (EstaActiva = S, sin fecha de extinción anterior).
FechaInici se lee como inicio de la operación comercial [inferencia: la capa no define el campo; coincide con la
operación comercial formal de Coca Codo Sinclair y Sopladora, mientras CENACE registra energía desde mayo-junio de 2016].
La potencia nominal (PotenciaNo) se compara con potencia instalada o nominal y la efectiva (PotenciaEf) con efectiva.

Versión K15 (12-10-2026): el extracto incluye las centrales térmicas del S.N.I. (K15c, conciliación de la potencia
térmica de 2025 por central) y las centrales de crudo operadas por CELEC (K14, sistema al que pertenecen); la serie
termica_SNI suma su potencia por fecha de inicio; centrales_clases.csv trae los años de entrada en el Modelo CLG
(inversiones mínimas de A2_Output_Params/NDCCON) frente al año de inicio de la capa.
"""
import argparse
import os
import hashlib
import struct
import sys
from datetime import date
from pathlib import Path

import openpyxl
import pandas as pd

ENERGIA = Path(__file__).resolve().parents[1]
AQUI = Path(__file__).resolve().parent
CAPA = Path(os.environ.get("ART6_CAPA_CENTRALES", "CENTRALES.dbf"))   # capa local (uso autorizado, no distribuida)
ENERGY_XLSX = ENERGIA / "Insumos_Art6" / "Energy.xlsx"   # copia sin cambios de Data/Energy.xlsx del Modelo CLG
A2 = ENERGIA / "A2_Output_Params" / "NDCCON"
CITA = "ARCONEL, capa CENTRALES; uso autorizado; referencia del oficio [verificar]"
COLUMNAS = ["IdCentral", "NombreCent", "NombreEmpr", "TipoEmpres", "TipoCentra", "Sistema", "Provincia", "Canton",
            "FechaInici", "PotenciaNo", "PotenciaEf", "TipoInvers", "EstaActiva", "fecha_crea", "fecha_exti"]
ANIOS = list(range(2010, 2036))
# Centrales hidroeléctricas de la tabla de clases (nombre del encargo -> nombres en la capa)
HIDRO = {"Mazar": ["Mazar"], "Molino": ["Molino"], "Sopladora": ["Sopladora"], "Coca Codo Sinclair": ["Coca Codo Sinclair"],
         "Agoyán": ["Agoyán"], "San Francisco": ["San Francisco"], "Pucará": ["Pucará"],
         "Delsitanisagua": ["Delsitanisagua"], "Minas San Francisco": ["Minas San Francisco"],
         "Marcel Laniado": ["Marcel Laniado"], "Toachi Pilatón": ["Sarapullo", "Alluriquín", "Mini Central Toachi"],
         "Manduriacu": ["Manduriacu"]}
# Clase del modelo, río y evidencia. La vertiente de la clase sale de su código (A1_Outputs/A-O_AR_Model_Base_Year.xlsx,
# hoja Primary: «Hydro Dam/ROR Amazon/Pacific Big (+450 MW)/Medium (<450 MW)/Small (<50 MW)»).
CLASES = {
    "Molino": ("PPHDAMAB", "Paute", None,
               "ResidualCapacity de PPHDAMAB = 1,075 GW en 2010-2035 (A2 NDCCON), igual a la potencia nominal de Molino"),
    "Mazar": ("PPHDAMAM", "Paute", "Central Hidroeléctrica Mazar",
              "Energy.xlsx Proyectos_Plantas (embalse, Amazonas, mediana, ingreso 2010); ResidualCapacity de PPHDAMAM "
              "0,33 GW desde 2015 = Mazar 170 + Agoyán 160 MW"),
    "Agoyán": ("PPHDAMAM", "Pastaza", None,
               "ResidualCapacity de PPHDAMAM 0,33 GW - Mazar 0,17 GW = 0,16 GW (A2 NDCCON); la capa da 156 MW nominales"),
    "Marcel Laniado": ("PPHDAMPM", "Daule", None,
                       "ResidualCapacity de PPHDAMPM 0,286 GW = Marcel Laniado 213 + Pucará 73 MW (A2 NDCCON)"),
    "Pucará": ("PPHDAMPM", "Pastaza (embalse Pisayambo)", None,
               "ResidualCapacity de PPHDAMPM 0,286 GW - Marcel Laniado 0,213 GW = 0,073 GW = potencia nominal de Pucará"),
    "San Francisco": ("PPHRORPM", "Pastaza", None,
                      "ResidualCapacity de PPHRORPM = 0,230 GW en 2010-2035 (A2 NDCCON), igual a la potencia nominal de "
                      "San Francisco"),
    "Coca Codo Sinclair": ("PPHRORAB", "Coca", "Central Hidroeléctrica Coca Codo Sinclair",
                           "Energy.xlsx Proyectos_Plantas (pasada, Amazonas, grande); K02-K03"),
    "Sopladora": ("PPHRORAB", "Paute", "Proyecto Hidroeléctrico Sopladora",
                  "Energy.xlsx Proyectos_Plantas (pasada, Amazonas, grande); K02-K03"),
    "Manduriacu": ("PPHRORPM", "Guayllabamba", "Central Hidroeléctrica Manduriacu",
                   "Energy.xlsx Proyectos_Plantas (pasada, Pacífico, mediana, 65 MW, 2015); TotalAnnualMinCapacityInvestment "
                   "de PPHRORPM 0,0217 GW en 2015-2017 (A2 NDCCON)"),
    "Minas San Francisco": ("PPHRORPM", "Jubones", "Proyecto Hidroeléctrico Minas San Francisco",
                            "Energy.xlsx Proyectos_Plantas (pasada, Pacífico, mediana, 270 MW, 2017); "
                            "TotalAnnualMinCapacityInvestment de PPHRORPM 0,09 GW en 2017-2019 (A2 NDCCON)"),
    "Delsitanisagua": ("PPHRORAM", "Zamora", "Proyecto Hidroeléctrico Delsitanisagua",
                       "Energy.xlsx Proyectos_Plantas (pasada, Amazonas, mediana, 180 MW, 2019); "
                       "TotalAnnualMinCapacityInvestment de PPHRORAM 0,06 GW en 2018-2020 (A2 NDCCON)"),
    "Sarapullo": ("PPHDAMPS", "Toachi-Pilatón", "Complejo Hidroeléctrico Toachi Pilatón (Sarapullo)",
                  "Energy.xlsx Proyectos_Plantas (embalse, Pacífico, pequeña, 49 MW, 2022); TotalAnnualMinCapacityInvestment "
                  "de PPHDAMPS 0,0163 GW en 2022-2024 (A2 NDCCON)"),
    "Alluriquín": ("PPHDAMPM", "Toachi-Pilatón", "Complejo Hidroeléctrico Toachi Pilatón (Alluriquín)",
                   "Energy.xlsx Proyectos_Plantas (embalse, Pacífico, mediana, 205,4 MW, 2025); "
                   "TotalAnnualMinCapacityInvestment de PPHDAMPM 0,0685 GW en 2025-2027 (A2 NDCCON)"),
    "Mini Central Toachi": (None, "Toachi-Pilatón", None,
                            "Sin clase: 1,4 MW, no está en Energy.xlsx ni en las inversiones mínimas de A2"),
}
# Vertiente de las centrales que Energy.xlsx no lista: inferida del río (la capa da provincia, no cuenca)
VERTIENTE_RIO = {"Paute": "Amazonas", "Pastaza": "Amazonas", "Pastaza (embalse Pisayambo)": "Amazonas",
                 "Daule": "Pacífico", "Toachi-Pilatón": "Pacífico"}


def md5(ruta):
    return hashlib.md5(Path(ruta).read_bytes()).hexdigest()


def leer_dbf(ruta):
    """Tabla de atributos de un .dbf (dBASE III) como DataFrame de texto; devuelve también la fecha de la cabecera."""
    b = Path(ruta).read_bytes()
    _, aa, mm, dd, n, largo_cab, largo_reg = struct.unpack("<BBBBIHH", b[:12])
    campos, i = [], 32
    while b[i] != 0x0D:
        campos.append((b[i:i + 11].split(b"\0")[0].decode("latin-1"), chr(b[i + 11]), b[i + 16]))
        i += 32
    filas = []
    for k in range(n):
        r = b[largo_cab + k * largo_reg: largo_cab + (k + 1) * largo_reg]
        if r[:1] == b"*":
            continue
        pos, d = 1, {}
        for nombre, _, largo in campos:
            d[nombre] = r[pos:pos + largo].decode("utf-8", errors="strict").strip()
            pos += largo
        filas.append(d)
    return pd.DataFrame(filas), date(1900 + aa, mm, dd), n


def activa_en(f, anio):
    """La central cuenta en el año si inició operación a más tardar el 31 de diciembre y no se extinguió antes."""
    if not f.FechaInici:
        return False
    if int(f.FechaInici[:4]) > anio:
        return False
    if f.EstaActiva != "S" and f.fecha_exti not in ("", "0") and int(f.fecha_exti) <= anio:
        return False
    return True


def proyectos_energy_xlsx():
    wb = openpyxl.load_workbook(ENERGY_XLSX, data_only=True, read_only=True)
    ws = wb["Proyectos_Plantas"]
    salida = {}
    for fila in ws.iter_rows(values_only=True):
        if fila[2] and fila[3] and str(fila[3]).startswith("Hidroeléctrica"):
            salida[fila[2]] = {"tipo": fila[3], "vertiente": fila[4], "MW": fila[5], "ingreso": fila[7],
                               "clasificacion": fila[11]}
    wb.close()
    return salida


def evidencia_a2():
    """Vectores de A2_Output_Params/NDCCON que sostienen la asignación (se comprueban, no se copian a mano)."""
    rc = pd.read_csv(A2 / "ResidualCapacity.csv")
    mi = pd.read_csv(A2 / "TotalAnnualMinCapacityInvestment.csv")

    def v(d, t, y):
        x = d[(d.TECHNOLOGY == t) & (d.YEAR == y)].Value
        return float(x.iloc[0]) if len(x) else 0.0
    return {"PPHDAMAB_rc": v(rc, "PPHDAMAB", 2015), "PPHDAMAM_rc": v(rc, "PPHDAMAM", 2015),
            "PPHDAMPM_rc": v(rc, "PPHDAMPM", 2015), "PPHRORPM_rc": v(rc, "PPHRORPM", 2015),
            "PPHRORPM_mi": {y: v(mi, "PPHRORPM", y) for y in range(2015, 2020)},
            "PPHRORAM_mi": {y: v(mi, "PPHRORAM", y) for y in range(2018, 2021)},
            "PPHDAMPS_mi": {y: v(mi, "PPHDAMPS", y) for y in range(2022, 2025)},
            "PPHDAMPM_mi": {y: v(mi, "PPHDAMPM", y) for y in range(2025, 2028)}}


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--capa", type=Path, default=CAPA)
    a = p.parse_args()
    dbf = a.capa
    if not dbf.exists():
        raise SystemExit("extraer_centrales.py lee la capa CENTRALES de ARCONEL (uso autorizado), que no se distribuye: "
                         "indique su .dbf con --capa o con la variable de entorno ART6_CAPA_CENTRALES. Los archivos "
                         "por central que escribe quedan fuera del repositorio; agregar_por_clase.py los resume.")
    shp = dbf.with_suffix(".shp")
    df, fecha_dbf, n = leer_dbf(dbf)
    if n != 355 or len(df) != 355:
        raise SystemExit(f"la capa trae {n} registros ({len(df)} vigentes); se esperaban 355")
    for c in ("PotenciaNo", "PotenciaEf"):
        df[c] = pd.to_numeric(df[c])
    huellas = {"md5_shp": md5(shp), "md5_dbf": md5(dbf), "fecha_dbf": fecha_dbf.isoformat()}
    # ---- extracto
    usos = []
    nombres_hidro = {n_ for v in HIDRO.values() for n_ in v}
    for _, f in df.iterrows():
        uso = None
        if f.TipoCentra == "Biomasa":
            uso = "K04 (contraste de potencia de PPIBIM)"
        elif f.TipoCentra == "Biogas":
            uso = "K06 (contraste de potencia y fecha de PPBGS)"
        elif f.TipoCentra == "Eólica":
            uso = "K11 (fecha de entrada y potencia eólica)"
        elif f.TipoCentra == "Solar":
            uso = "K12 (fecha de entrada y potencia solar)"
        elif f.TipoCentra == "Hidráulica" and f.NombreCent in nombres_hidro:
            uso = "centrales_clases.csv (clases hidro para el año seco, paso 4)"
        elif f.TipoCentra == "Térmica" and f.Sistema == "S.N.I.":
            uso = "K15c (potencia térmica del S.N.I. por central, conciliación de 2023-2025)"
        elif f.TipoCentra == "Térmica" and "crudo" in f.NombreCent.lower():
            uso = "K14 (central de crudo operada por CELEC: sistema eléctrico al que pertenece)"
        if uso:
            d = {c: f[c] for c in COLUMNAS}
            d.update({"uso": uso, "fuente": CITA, **huellas})
            usos.append(d)
    ext = pd.DataFrame(usos)
    faltan = nombres_hidro - set(ext.NombreCent)
    if faltan:
        raise SystemExit(f"la capa no trae {faltan}")
    ext.to_csv(AQUI / "centrales_extracto.csv", index=False)
    # ---- series por año
    filas = []
    grupos = {"biomasa_autogeneradora": lambda f: f.TipoCentra == "Biomasa",
              "biogas": lambda f: f.TipoCentra == "Biogas",
              "eolica_SNI": lambda f: f.TipoCentra == "Eólica" and f.Sistema == "S.N.I.",
              "eolica_no_incorporada": lambda f: f.TipoCentra == "Eólica" and f.Sistema != "S.N.I.",
              "solar_SNI": lambda f: f.TipoCentra == "Solar" and f.Sistema == "S.N.I.",
              "solar_no_incorporada": lambda f: f.TipoCentra == "Solar" and f.Sistema != "S.N.I.",
              "termica_SNI": lambda f: f.TipoCentra == "Térmica" and f.Sistema == "S.N.I.",
              "termica_SNI_generadora": lambda f: f.TipoCentra == "Térmica" and f.Sistema == "S.N.I." and
              f.TipoEmpres == "Generadora",
              "termica_SNI_distribuidora": lambda f: f.TipoCentra == "Térmica" and f.Sistema == "S.N.I." and
              f.TipoEmpres == "Distribuidora"}
    for g, fn in grupos.items():
        sub = df[df.apply(fn, axis=1)]
        for y in ANIOS:
            act = sub[sub.apply(lambda f: activa_en(f, y), axis=1)]
            filas.append({"grupo": g, "anio": y, "centrales": len(act), "potencia_nominal_MW": round(act.PotenciaNo.sum(), 3),
                          "potencia_efectiva_MW": round(act.PotenciaEf.sum(), 3),
                          "centrales_que_inician": "; ".join(f"{r.NombreCent} ({r.FechaInici[:4]}-{r.FechaInici[4:6]}-"
                                                             f"{r.FechaInici[6:]})" for r in sub.itertuples()
                                                             if r.FechaInici[:4] == str(y))})
    series = pd.DataFrame(filas)
    series["fuente"] = CITA
    series["md5_dbf"] = huellas["md5_dbf"]
    series.to_csv(AQUI / "centrales_series.csv", index=False)
    # ---- clases hidro
    proy = proyectos_energy_xlsx()
    ev = evidencia_a2()
    # controles de la evidencia: los vectores de A2 que se citan deben seguir valiendo lo que dice la evidencia
    controles = {"PPHDAMAB_rc = Molino": abs(ev["PPHDAMAB_rc"] - 1.075) < 1e-9,
                 "PPHDAMAM_rc = 0,33": abs(ev["PPHDAMAM_rc"] - 0.33) < 1e-9,
                 "PPHDAMPM_rc = 0,286": abs(ev["PPHDAMPM_rc"] - 0.286) < 1e-9,
                 "PPHRORPM_rc = 0,23": abs(ev["PPHRORPM_rc"] - 0.23) < 1e-9,
                 "PPHRORPM_mi = 0,335": abs(sum(ev["PPHRORPM_mi"].values()) - 0.3351) < 1e-3,
                 "PPHRORAM_mi = 0,18": abs(sum(ev["PPHRORAM_mi"].values()) - 0.18) < 1e-9,
                 "PPHDAMPS_mi = 0,049": abs(sum(ev["PPHDAMPS_mi"].values()) - 0.0489) < 1e-9,
                 "PPHDAMPM_mi = 0,2055": abs(sum(ev["PPHDAMPM_mi"].values()) - 0.2055) < 1e-9}
    if not all(controles.values()):
        raise SystemExit(f"la evidencia de A2 cambió: {controles}")
    filas = []
    for central, nombres in HIDRO.items():
        for nom in nombres:
            r = df[(df.NombreCent == nom) & (df.TipoCentra == "Hidráulica")]
            if len(r) != 1:
                raise SystemExit(f"{nom}: {len(r)} registros hidro en la capa")
            r = r.iloc[0]
            clase, rio, clave_x, evid = CLASES[nom]
            if clave_x:
                x = proy[clave_x]
                vert, f_vert = x["vertiente"], f"Energy.xlsx Proyectos_Plantas ({clave_x})"
                tipo = x["tipo"].replace("Hidroeléctrica ", "").lower()
            else:
                vert = VERTIENTE_RIO.get(rio, "[verificar]")
                f_vert = (f"inferida del río {rio} (provincia {r.Provincia} en la capa) [inferencia, verificar con la "
                          "capa de cuencas de la etapa 3G]")
                tipo = "[verificar]"
            if clase:
                v_clase = "Amazonas" if clase[6] == "A" else "Pacífico"
                t_clase = "embalse" if clase.startswith("PPHDAM") else "pasada"
                tam = {"B": "grande (450 MW o más)", "M": "mediana (menos de 450 MW)", "S": "pequeña (menos de 50 MW)"}[clase[7]]
                coincide = "sí" if v_clase == vert else ("no" if vert in ("Amazonas", "Pacífico") else "[verificar]")
            else:
                v_clase = t_clase = tam = coincide = ""
            filas.append({"central": central, "nombre_capa": nom, "IdCentral": r.IdCentral, "empresa": r.NombreEmpr,
                          "tipo_empresa": r.TipoEmpres, "sistema": r.Sistema, "provincia": r.Provincia,
                          "fecha_inicio_capa": f"{r.FechaInici[:4]}-{r.FechaInici[4:6]}-{r.FechaInici[6:]}",
                          "potencia_nominal_MW": r.PotenciaNo, "potencia_efectiva_MW": r.PotenciaEf, "rio": rio,
                          "tipo": tipo, "vertiente": vert, "fuente_vertiente": f_vert, "clase_modelo": clase or "",
                          "vertiente_de_la_clase": v_clase, "tipo_de_la_clase": t_clase, "tamano_de_la_clase": tam,
                          "vertiente_coincide": coincide, "evidencia_clase": evid,
                          "fuente_potencia_y_fecha": CITA, "md5_dbf": huellas["md5_dbf"]})
    cl = pd.DataFrame(filas)
    cl = cl.rename(columns={"fecha_inicio_capa": "fecha_inicio_capa_inferida_operacion_comercial"})
    # años de entrada en el Modelo CLG (inversión mínima de la clase en A2 NDCCON, repartida en tramos iguales) frente al
    # año de inicio de la capa; las centrales sin inversión mínima están en la capacidad residual desde 2010
    mi = pd.read_csv(A2 / "TotalAnnualMinCapacityInvestment.csv")

    def tramo(t, desde, hasta, gw):
        d = mi[(mi.TECHNOLOGY == t) & (mi.YEAR.between(desde, hasta))]
        vals = dict(zip(d.YEAR, d.Value))
        if any(v + 1e-9 < gw for v in vals.values()) or len(vals) != hasta - desde + 1:
            raise SystemExit(f"la inversión mínima de {t} {desde}-{hasta} ya no es {gw} GW por año: {vals}")
        mw, tot = f"{gw * 1000:g}".replace(".", ","), f"{gw * 1000 * (hasta - desde + 1):g}".replace(".", ",")
        return f"{desde}-{hasta} ({t}, {mw} MW por año, {tot} MW)"
    entrada = {"Manduriacu": tramo("PPHRORPM", 2015, 2017, 0.0217),
               "Minas San Francisco": tramo("PPHRORPM", 2017, 2019, 0.09),
               "Delsitanisagua": tramo("PPHRORAM", 2018, 2020, 0.06),
               "Sarapullo": tramo("PPHDAMPS", 2022, 2024, 0.0163),
               "Alluriquín": tramo("PPHDAMPM", 2025, 2027, 0.0685),
               "Coca Codo Sinclair": tramo("PPHRORAB", 2015, 2017, 0.5) + "; K03 la fija en 2016 con Sopladora",
               "Sopladora": tramo("PPHRORAB", 2015, 2017, 0.5) + " y 2026-2028 (PPHRORAB, 162,3 MW por año); K03 la "
                                                                "fija en 2016"}
    cl["anios_entrada_CLG"] = cl.nombre_capa.map(lambda n: entrada.get(n, "capacidad residual desde 2010" if n not in
                                                                       ("Mini Central Toachi",) else "sin clase"))
    cl["anio_inicio_capa"] = cl.fecha_inicio_capa_inferida_operacion_comercial.str[:4].astype(int)

    def contraste(r):
        e = entrada.get(r.nombre_capa)
        if not e:
            return ""
        a0, a1, c = int(e[:4]), int(e[5:9]), r.anio_inicio_capa
        if c < a0:
            return f"el CLG la incorpora después de la capa ({a0}-{a1} frente a {c})"
        if c > a1:
            return f"el CLG la adelanta entera ({a0}-{a1} frente a {c})"
        if c > a0:
            return (f"el CLG adelanta parte de la potencia: la reparte en {a0}-{a1} y la capa da inicio en {c} "
                    f"({c - a0} de {a1 - a0 + 1} tramos antes del inicio)")
        if a1 > a0:
            return f"el CLG completa la potencia en {a1}, {a1 - a0} años después del inicio de la capa ({c})"
        return f"coincide ({c})"
    cl["contraste_entrada"] = cl.apply(contraste, axis=1)
    # potencia de cada clase en el Modelo CLG (NDCCON, TotalCapacityAnnual 2025 y 2035) y parte que explican las centrales
    # de la capa asignadas a ella: lo que falta es potencia sin central identificada (residual o construida por el LP)
    o = pd.read_csv(ENERGIA / "Executables" / "NDCCON_0" / "NDCCON_0_Output.csv",
                    usecols=["Technology", "Year", "TotalCapacityAnnual"], low_memory=False)
    cap = o.groupby(["Technology", "Year"]).TotalCapacityAnnual.max().fillna(0)
    asig = cl[cl.clase_modelo != ""].groupby("clase_modelo").potencia_nominal_MW.sum()
    cl["potencia_clase_CLG_2025_MW"] = cl.clase_modelo.map(lambda c: round(cap.get((c, 2025), 0.0) * 1000, 1) if c else None)
    cl["potencia_clase_CLG_2035_MW"] = cl.clase_modelo.map(lambda c: round(cap.get((c, 2035), 0.0) * 1000, 1) if c else None)
    cl["capa_asignada_a_la_clase_MW"] = cl.clase_modelo.map(lambda c: round(float(asig.get(c, 0.0)), 2) if c else None)
    cl["participacion_en_clase_2025"] = (cl.potencia_nominal_MW / cl.potencia_clase_CLG_2025_MW).round(4)
    cl.to_csv(AQUI / "centrales_clases.csv", index=False)
    pd.set_option("display.width", 250)
    pd.set_option("display.max_columns", 30)
    print(f"Capa {dbf.name}: {n} registros; .dbf actualizado el {fecha_dbf}; md5 .shp {huellas['md5_shp']}, "
          f".dbf {huellas['md5_dbf']}")
    print(f"centrales_extracto.csv: {len(ext)} registros ({ext.TipoCentra.value_counts().to_dict()})")
    print(series[series.anio.isin([2014, 2015, 2016, 2017, 2022, 2023, 2025])].pivot(
        index="anio", columns="grupo", values="potencia_nominal_MW").to_string())
    print(cl[["central", "nombre_capa", "potencia_nominal_MW", "potencia_efectiva_MW", "anio_inicio_capa",
              "anios_entrada_CLG", "contraste_entrada", "clase_modelo", "vertiente_coincide",
              "potencia_clase_CLG_2025_MW", "capa_asignada_a_la_clase_MW"]].to_string(index=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
