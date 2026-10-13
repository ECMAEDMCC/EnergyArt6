# -*- coding: utf-8 -*-
"""Variantes de la expansión térmica declarada (K15b) y de la vigencia de los arriendos (K15c), resueltas con glpsol sobre
los datafiles que B1 escribe, sin pasar por B1 ni tocar el libro, las carpetas A2 o los escenarios.

1. Vigencia de los arriendos. El caso central (B1) da por vencidos el 31-12-2028 los arriendos sin fecha de fin
   publicada (S26-116; Santa Elena, 10-11-2028, S26-081). La variante los mantiene hasta el 31-03-2032, fin del bloque 1 de
   generación firme (MEM, PME 2023-2032, cap. 4, tabla 4-9, p. 134): el datafile de cada referencia con la ResidualCapacity
   y el TotalAnnualMaxCapacity de PPFOI, PPDSL y PPNGS de esa variante (correcciones_K_insumos.json, derivaciones K15b,
   variante_arriendos_2032).
2. Suficiencia. Para cada referencia y vigencia en la que el tope de PPFOI queda activo en algún año, el modelo pasa
   energía por STOELE (paso sin pérdidas que el LP usa cuando le falta potencia) o la corrida no tiene solución, resuelve el
   mismo datafile con el tope de PPFOI liberado en 2026-2035 (99999, el valor por omisión), el CapitalCost y el FixedCost de
   PPFOI en 2026-2035 multiplicados por 1.000 y el TotalAnnualMaxCapacity de STOELE en 0 en 2026-2035 (el Modelo CLG no lo
   usa en esos años), y mide la potencia de PPFOI por encima del tope: la capacidad faltante por año. Con la potencia de
   PPFOI cara y sin STOELE el LP construye solo la potencia sin la cual no cubre la demanda: es la variante de mínima
   inversión extra. Con el tope solo liberado (intento 1, tests/logs/paso9_suficiencia_intento1_tope_liberado_preferencia_
   LP.csv) el LP construye fuel oil aunque no le falte potencia, porque con los costos de relleno del modelo prefiere
   quemarlo a turbinar la hidro de PPHDAMAB (CONA6G 2029-2031: 229 a 283 MW más y 3,0 a 3,7 PJ menos de hidro): eso es
   una preferencia de costo, no una falta de potencia. Solo se libera PPFOI: PPNGS tiene su techo de actividad (K15d) y su
   CF (K15e) fijados para que la potencia declarada produzca justo ese techo, y en PPDSL el tope es la potencia existente
   (no hay diésel declarado): liberarlo mide la elección de combustible, no la suficiencia
   (tests/logs/paso8_variante_intento1_con_PPDSL_liberado.csv).

3. Factor del MWh desplazado por perturbación (--desplazado). Resuelve CONA6, CONA6G e INCA6 con la demanda final de
   electricidad (SpecifiedAnnualDemand de E5COMELE, E5INDELE, E5RESELE, E5TROELE, E5ALLTRNELE y E5CONELE) reducida 1 % en
   2026-2035 y mide, por año, la caída de CO2e_PP y CO2_PP sobre la caída de la generación de las centrales (PP e
   IMPELE, sin buses): el factor del MWh que el propio modelo deja de generar, y qué tecnologías bajan. Escribe
   calibracion_f_desplazado_perturbacion.csv.

Uso, desde ECU_NDC/Energy, después de correr B1 y construir_correcciones.py (glpsol en el PATH; unos 2 minutos y 4,5 GB de
RAM por corrida):
    python Art6_calibracion/variante_suficiencia.py --trabajo <carpeta fuera del repositorio> [--reusar] [--desplazado]

Escribe Art6_calibracion/calibracion_g_variante_arriendos_2032.csv (CO2e_PP, puente frente al escenario CLG y potencia de
cada referencia con la vigencia central y la de 2032), calibracion_g_suficiencia_variante.csv (capacidad faltante por año)
y variante_suficiencia.json (md5 de insumos y estado de cada corrida). Son diagnósticos, no referencias nuevas.
"""
import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

import pandas as pd

ENERGIA = Path(__file__).resolve().parents[1]
AQUI = Path(__file__).resolve().parent
EX = ENERGIA / "Executables"
PJ = 277.78
Y = list(range(2026, 2036))
CLONES = ("CONA6", "INCA6", "CONA6G", "INCA6G")
REF = {"CONA6": "NDCCON", "CONA6G": "NDCCON", "INCA6": "NDCINC", "INCA6G": "NDCINC"}
RED = ("PPFOI", "PPDSL", "PPNGS")


def md5(ruta):
    return hashlib.md5(Path(ruta).read_bytes()).hexdigest()


def poner(texto, parametro, filas):
    """Datafile con las filas {tecnología: {año: valor}} escritas en la tabla [ECU,*,*] del parámetro."""
    ini = texto.index(f"param {parametro} default")
    fin = texto.index("\n;", ini)
    bloque = texto[ini:fin].split("\n")
    cab = None
    hechos = 0
    for k, ln in enumerate(bloque):
        if ln.strip().startswith("["):
            cab = bloque[k + 1].replace(":=", "").split()
            continue
        p = ln.split()
        if cab and p and p[0] in filas and len(p) == len(cab) + 1:
            for j, a in enumerate(cab):
                if int(a) in filas[p[0]]:
                    v = filas[p[0]][int(a)]
                    p[1 + j] = "99999" if v == 99999 else f"{v:.6f}".rstrip("0").rstrip(".")
                    hechos += 1
            bloque[k] = " ".join(p) + ln[len(ln.rstrip()):]
    esperados = sum(len(v) for v in filas.values())
    if hechos != esperados:
        raise SystemExit(f"{parametro}: se esperaban {esperados} cambios y hubo {hechos}")
    return texto[:ini] + "\n".join(bloque) + texto[fin:]


CARO = 1000.0  # multiplica el costo de capital y fijo de PPFOI en la variante de potencia mínima


def datos_costo(texto):
    """{(parámetro, año): valor} de CapitalCost y FixedCost de PPFOI en el datafile."""
    out = {}
    for par in ("CapitalCost", "FixedCost"):
        ini = texto.index(f"param {par} default")
        fin = texto.index("\n;", ini)
        bloque = texto[ini:fin].split("\n")
        cab = None
        for k, ln in enumerate(bloque):
            if ln.strip().startswith("["):
                cab = bloque[k + 1].replace(":=", "").split()
                continue
            p = ln.split()
            if cab and p and p[0] == "PPFOI" and len(p) == len(cab) + 1:
                out.update({(par, int(a)): float(v) for a, v in zip(cab, p[1:])})
    if len(out) != 2 * 26:
        raise SystemExit("CapitalCost o FixedCost de PPFOI incompletos en el datafile")
    return out


def seccion(lineas, titulo, columnas_id=1):
    """{(id..., año): valor} de una sección «Technology,años» de SelectedResults.csv."""
    i = next(k for k, l in enumerate(lineas) if l.startswith(titulo))
    out, anios = {}, None
    for l in lineas[i + 1:]:
        p = l.strip().split(",")
        if not l.strip():
            if anios:
                break
            continue
        if p[0] == "Technology":
            anios = [int(x) for x in p[columnas_id:] if x]
            continue
        if anios and len(p) >= columnas_id + len(anios):
            for a, v in zip(anios, p[columnas_id:]):
                try:
                    out[tuple(p[:columnas_id]) + (a,)] = float(v)
                except ValueError:
                    pass
        elif anios:
            break
    return out


def resultados_selected(ruta):
    lineas = Path(ruta).read_text(encoding="utf-8", errors="replace").split("\n")
    cap = seccion(lineas, "TotalAnnualCapacity")
    nue = seccion(lineas, "NewCapacity")
    emis = seccion(lineas, "Annual Emissions by Technology", columnas_id=2)
    prod = seccion(lineas, "ProductionByTechnology", columnas_id=3)
    return {"co2": {y: sum(v for (t, e, yy), v in emis.items() if e == "CO2e_PP" and yy == y) * 1000 for y in Y},
            "cap": {(t, y): cap.get((t, y), 0.0) for t in RED for y in Y},
            "nueva": {(t, y): nue.get((t, y), 0.0) for t in RED for y in Y},
            "stoele": {y: sum(v for (t, f, l, yy), v in prod.items() if t == "STOELE" and yy == y) for y in Y}}


def resultados_output(esc):
    ruta = EX / f"{esc}_0" / f"{esc}_0_Output.csv"
    if not ruta.exists():
        return None
    o = pd.read_csv(ruta, usecols=["Technology", "Year", "Emission", "AnnualTechnologyEmission", "TotalCapacityAnnual",
                                   "NewCapacity", "TotalTechnologyAnnualActivity"], low_memory=False)
    co2 = (o[o.Emission == "CO2e_PP"].groupby("Year").AnnualTechnologyEmission.sum() * 1000).to_dict()
    cap = o.groupby(["Technology", "Year"]).TotalCapacityAnnual.max().fillna(0).to_dict()
    nue = o.groupby(["Technology", "Year"]).NewCapacity.max().fillna(0).to_dict()
    sto = o[o.Technology == "STOELE"].groupby("Year").TotalTechnologyAnnualActivity.max().fillna(0).to_dict()
    return {"co2": {y: co2.get(y, 0.0) for y in Y}, "cap": {(t, y): cap.get((t, y), 0.0) for t in RED for y in Y},
            "nueva": {(t, y): nue.get((t, y), 0.0) for t in RED for y in Y}, "stoele": {y: sto.get(y, 0.0) for y in Y},
            "md5": md5(ruta)}


DEMANDA_ELE = ("E5COMELE", "E5INDELE", "E5RESELE", "E5TROELE", "E5ALLTRNELE", "E5CONELE")
NETA_BRUTA = 4952.41 / 5136.35  # CENACE, Informe Anual 2025, Parte 1, figuras 1.10 y 1.7 (térmica neta / bruta)


def leer_fila(texto, parametro, nombre):
    """{año: valor} de la fila de la tabla [ECU,*,*] del parámetro."""
    ini = texto.index(f"param {parametro} default")
    fin = texto.index("\n;", ini)
    bloque = texto[ini:fin].split("\n")
    cab = None
    for k, ln in enumerate(bloque):
        if ln.strip().startswith("["):
            cab = bloque[k + 1].replace(":=", "").split()
            continue
        p = ln.split()
        if cab and p and p[0] == nombre and len(p) == len(cab) + 1:
            return {int(a): float(v) for a, v in zip(cab, p[1:])}
    raise SystemExit(f"{parametro}: falta la fila {nombre}")


def generacion_y_emision(prod_o_output, emis=None):
    """Generación de las centrales (PJ, PP e IMPELE en E1ELE y E3ELE) y emisiones por tecnología, por año."""
    gen, act = {}, {}
    for (t, f, y), v in prod_o_output.items():
        if (t.startswith("PP") or t == "IMPELE") and f in ("E1ELE", "E3ELE"):
            gen[y] = gen.get(y, 0.0) + v
            act[(t, y)] = act.get((t, y), 0.0) + v
    return gen, act


def desplazado(trabajo, reusar, estado):
    filas = []
    for e in ("CONA6", "CONA6G", "INCA6"):
        base_df = (EX / f"{e}_0" / f"{e}_0.txt").read_text(encoding="utf-8")
        filas_dem = {f: {y: v * 0.99 for y, v in leer_fila(base_df, "SpecifiedAnnualDemand", f).items() if y in Y}
                     for f in DEMANDA_ELE}
        texto = poner(base_df, "SpecifiedAnnualDemand", filas_dem)
        nombre = f"{e}_demanda_electrica_menos_1pct"
        r = resolver(trabajo, nombre, texto, reusar, estado)
        if r is None:
            raise SystemExit(f"{nombre}: sin solución")
        lin = (trabajo / f"SelectedResults_{nombre}.csv").read_text(encoding="utf-8", errors="replace").split("\n")
        prod = seccion(lin, "ProductionByTechnology", columnas_id=3)
        emis = seccion(lin, "Annual Emissions by Technology", columnas_id=2)
        gen_v, act_v = generacion_y_emision({(t, f, y): v for (t, f, l, y), v in prod.items()})
        o = pd.read_csv(EX / f"{e}_0" / f"{e}_0_Output.csv", usecols=["Technology", "Fuel", "Year", "Emission",
                                                                     "ProductionByTechnology", "AnnualTechnologyEmission"],
                        low_memory=False)
        po = o.dropna(subset=["ProductionByTechnology"]).groupby(["Technology", "Fuel", "Year"]).ProductionByTechnology \
            .sum().to_dict()
        gen_b, act_b = generacion_y_emision(po)
        eb = o[o.Emission.isin(["CO2e_PP", "CO2_PP"])].groupby(["Emission", "Year"]).AnnualTechnologyEmission.sum()
        for y in Y:
            dg = (gen_b[y] - gen_v[y]) * PJ  # GWh
            de = {g: (float(eb.get((g, y), 0.0)) - sum(v for (t, gg, yy), v in emis.items() if gg == g and yy == y))
                  * 1e6 for g in ("CO2e_PP", "CO2_PP")}  # t
            bajan = {t: (act_b.get((t, y), 0.0) - act_v.get((t, y), 0.0)) * PJ for t in
                     {k[0] for k in act_b} | {k[0] for k in act_v}}
            bajan = {t: v for t, v in bajan.items() if abs(v) > 0.5}
            filas.append({"escenario": e, "anio": y, "generacion_desplazada_GWh": round(dg, 1),
                          "CO2e_PP_evitado_t": round(de["CO2e_PP"], 0), "CO2_PP_evitado_t": round(de["CO2_PP"], 0),
                          "factor_CO2e_t_MWh_bruto": round(de["CO2e_PP"] / (dg * 1000), 4) if dg > 1 else None,
                          "factor_CO2_t_MWh_neto": round(de["CO2_PP"] / (dg * 1000) / NETA_BRUTA, 4) if dg > 1 else None,
                          "factor_CO2e_t_MWh_neto": round(de["CO2e_PP"] / (dg * 1000) / NETA_BRUTA, 4) if dg > 1 else None,
                          "cambio_por_tecnologia_GWh": "; ".join(f"{t} {-v:+.0f}" for t, v in
                                                                 sorted(bajan.items(), key=lambda x: -abs(x[1])))})
    out = pd.DataFrame(filas)
    out.to_csv(AQUI / "calibracion_f_desplazado_perturbacion.csv", index=False)
    print(out.to_string(index=False))
    return out


def resolver(trabajo, nombre, texto, reusar, estado):
    """Resuelve el datafile con glpsol en la carpeta de trabajo; devuelve los resultados o None si no hay solución."""
    datos = trabajo / f"{nombre}.txt"
    previo = trabajo / f"SelectedResults_{nombre}.csv"
    igual = datos.exists() and datos.read_text(encoding="utf-8") == texto and previo.exists()
    datos.write_text(texto, encoding="utf-8")
    estado[nombre] = {"datafile_md5": md5(datos)}
    if reusar and igual:
        estado[nombre].update({"reusada": True, "optimo": True})
        print(f"{nombre}: datafile idéntico; se reusa {previo.name}")
        return resultados_selected(previo)
    sel = trabajo / "SelectedResults.csv"
    if sel.exists():
        sel.unlink()
    log = trabajo / f"glpsol_{nombre}.log"
    with log.open("w", encoding="utf-8") as h:
        rc = subprocess.run(["glpsol", "-m", "OSeMOSYS_Model.txt", "-d", datos.name], cwd=trabajo, stdout=h,
                            stderr=subprocess.STDOUT, env=os.environ).returncode
    texto_log = log.read_text(encoding="utf-8", errors="replace")
    optimo = "OPTIMAL LP SOLUTION FOUND" in texto_log
    estado[nombre].update({"rc": rc, "optimo": optimo,
                           "infactible": "NO PRIMAL FEASIBLE" in texto_log})
    print(f"{nombre}: rc {rc}, óptimo {optimo}")
    if not optimo:
        return None
    shutil.copy2(sel, previo)
    return resultados_selected(previo)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--trabajo", type=Path, required=True)
    ap.add_argument("--reusar", action="store_true", help="no vuelve a resolver un datafile idéntico al ya resuelto")
    ap.add_argument("--desplazado", action="store_true", help="solo el factor del MWh desplazado por perturbación")
    a = ap.parse_args()
    trabajo = a.trabajo.resolve()
    if ENERGIA.parent in trabajo.parents:
        raise SystemExit("la carpeta de trabajo debe estar fuera del repositorio")
    trabajo.mkdir(parents=True, exist_ok=True)
    shutil.copy2(ENERGIA / "OSeMOSYS_Model.txt", trabajo / "OSeMOSYS_Model.txt")
    if a.desplazado:
        est = {}
        desplazado(trabajo, a.reusar, est)
        (AQUI / "desplazado_perturbacion.json").write_text(
            json.dumps({"insumos": {f"{e}_0.txt": md5(EX / f"{e}_0" / f"{e}_0.txt") for e in ("CONA6", "CONA6G", "INCA6")},
                        "corridas": est}, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
        return 0
    der = json.loads((AQUI / "correcciones_K_insumos.json").read_text(encoding="utf-8"))["derivaciones"]
    k15b = der["K15b"]
    var32 = k15b["variante_arriendos_2032"]
    tope = {"2028": {(t, int(y)): v for t, d in k15b["tope_GW"].items() for y, v in d.items()},
            "2032": {(t, int(y)): v for t, d in var32.items() for y, v in d["TotalAnnualMaxCapacity"].items()}}
    estado = {"insumos": {"correcciones_K_insumos.json": md5(AQUI / "correcciones_K_insumos.json"),
                          "OSeMOSYS_Model.txt": md5(ENERGIA / "OSeMOSYS_Model.txt"),
                          **{f"{e}_0.txt": md5(EX / f"{e}_0" / f"{e}_0.txt") for e in CLONES}},
              "vigencia_arriendos": der["K15c"]["vigencia_arriendos"], "corridas": {}}
    res = {}
    clg = {e: resultados_output(e) for e in ("NDCCON", "NDCINC")}
    for e in CLONES:
        base = (EX / f"{e}_0" / f"{e}_0.txt").read_text(encoding="utf-8")
        res[(e, "2028")] = resultados_output(e)            # B1: None si la corrida no tuvo solución
        estado["corridas"][f"{e}_vigencia_2028"] = {"fuente": "B1", "optimo": res[(e, "2028")] is not None}
        texto32 = poner(base, "ResidualCapacity", {t: {int(y): v for y, v in d["ResidualCapacity"].items()}
                                                   for t, d in var32.items()})
        texto32 = poner(texto32, "TotalAnnualMaxCapacity", {t: {int(y): v for y, v in d["TotalAnnualMaxCapacity"].items()}
                                                            for t, d in var32.items()})
        res[(e, "2032")] = resolver(trabajo, f"{e}_arriendos_2032", texto32, a.reusar, estado["corridas"])
        for vig, texto in (("2028", base), ("2032", texto32)):
            r = res[(e, vig)]
            activo = r is not None and any(tope[vig][("PPFOI", y)] - r["cap"][("PPFOI", y)] < 5e-5 for y in Y)
            stoele = r is not None and any(r["stoele"][y] > 1e-6 for y in Y)
            if r is None or activo or stoele:
                d_ = datos_costo(texto)
                lib = poner(texto, "TotalAnnualMaxCapacity", {"PPFOI": {y: 99999 for y in Y}, "STOELE": {y: 0 for y in Y}})
                lib = poner(lib, "CapitalCost", {"PPFOI": {y: d_[("CapitalCost", y)] * CARO for y in Y}})
                lib = poner(lib, "FixedCost", {"PPFOI": {y: d_[("FixedCost", y)] * CARO for y in Y}})
                nombre = f"{e}_arriendos_{vig}_potencia_minima"
                res[(e, vig, "suf")] = resolver(trabajo, nombre, lib, a.reusar, estado["corridas"])
                estado["corridas"][nombre]["motivo"] = (
                    "sin solución con el tope" if r is None else
                    "tope activo y STOELE" if activo and stoele else "tope activo" if activo else "STOELE")
    filas_v, filas_s = [], []
    for e in CLONES:
        c = clg[REF[e]]
        for y in Y:
            f = {"escenario": e, "anio": y, f"CLG_{REF[e]}_kt": round(c["co2"][y], 2)}
            for vig in ("2028", "2032"):
                r = res[(e, vig)]
                f[f"CO2e_PP_arriendos_{vig}_kt"] = round(r["co2"][y], 2) if r else None
                f[f"puente_arriendos_{vig}_kt"] = round(r["co2"][y] - c["co2"][y], 2) if r else None
                f[f"PPFOI_MW_arriendos_{vig}"] = round(r["cap"][("PPFOI", y)] * 1000, 2) if r else None
                f[f"tope_PPFOI_MW_arriendos_{vig}"] = round(tope[vig][("PPFOI", y)] * 1000, 2)
                f[f"STOELE_GWh_arriendos_{vig}"] = round(r["stoele"][y] * PJ, 1) if r else None
                rs = res.get((e, vig, "suf"))
                if (e, vig, "suf") in res:
                    filas_s.append({
                        "escenario": e, "vigencia_arriendos": vig, "anio": y,
                        "estado_con_tope": "sin solución" if r is None else "óptimo",
                        "tope_PPFOI_MW": round(tope[vig][("PPFOI", y)] * 1000, 2),
                        "PPFOI_con_tope_MW": round(r["cap"][("PPFOI", y)] * 1000, 2) if r else None,
                        "tope_activo": bool(r and tope[vig][("PPFOI", y)] - r["cap"][("PPFOI", y)] < 5e-5),
                        "STOELE_con_tope_GWh": round(r["stoele"][y] * PJ, 1) if r else None,
                        "estado_variante": "óptimo" if rs else "sin solución",
                        "PPFOI_variante_MW": round(rs["cap"][("PPFOI", y)] * 1000, 2) if rs else None,
                        "PPFOI_nueva_variante_MW": round(rs["nueva"][("PPFOI", y)] * 1000, 2) if rs else None,
                        "capacidad_faltante_PPFOI_MW": round(max(0.0, rs["cap"][("PPFOI", y)] - tope[vig][("PPFOI", y)])
                                                             * 1000, 2) if rs else None,
                        "STOELE_variante_GWh": round(rs["stoele"][y] * PJ, 1) if rs else None,
                        "CO2e_PP_con_tope_kt": round(r["co2"][y], 2) if r else None,
                        "CO2e_PP_variante_kt": round(rs["co2"][y], 2) if rs else None,
                        "diferencia_CO2e_kt": round(rs["co2"][y] - r["co2"][y], 2) if (r and rs) else None,
                        "puente_variante_kt": round(rs["co2"][y] - c["co2"][y], 2) if rs else None})
            filas_v.append(f)
    v = pd.DataFrame(filas_v)
    sumas = []
    for nombre, ys in (("2026-2028", [2026, 2027, 2028]), ("2031-2035", list(range(2031, 2036)))):
        for e in CLONES:
            x = v[(v.escenario == e) & v.anio.isin(ys)]
            fila = {"escenario": e, "anio": nombre}
            for col in [c for c in v.columns if c.startswith(("puente_", "CO2e_PP_", "CLG_"))]:
                fila[col] = round(x[col].sum(), 2) if x[col].notna().all() else None
            sumas.append(fila)
    v = pd.concat([v, pd.DataFrame(sumas)], ignore_index=True)
    v.to_csv(AQUI / "calibracion_g_variante_arriendos_2032.csv", index=False)
    s = pd.DataFrame(filas_s)
    s.to_csv(AQUI / "calibracion_g_suficiencia_variante.csv", index=False)
    estado["resultado_suficiencia"] = filas_s
    (AQUI / "variante_suficiencia.json").write_text(json.dumps(estado, indent=1, ensure_ascii=False, default=str) + "\n",
                                                    encoding="utf-8")
    pd.set_option("display.width", 250)
    pd.set_option("display.max_columns", 40)
    print(v.to_string(index=False))
    print(s.to_string(index=False) if len(s) else "ningún tope activo, sin STOELE y todas las corridas con solución")
    return 0


if __name__ == "__main__":
    sys.exit(main())
