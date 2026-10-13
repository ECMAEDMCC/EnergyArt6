# -*- coding: utf-8 -*-
"""Suficiencia de los escenarios del Artículo 6: capacidad térmica faltante por año cuando B1 no encuentra solución o
cuando el modelo pasa energía por STOELE (la señal de falta de potencia con el tope K15b activo).

Para cada escenario elegido resuelve con glpsol, fuera de B1 y fuera del repositorio, la variante de potencia mínima de
variante_suficiencia.py sobre el datafile que escribió B1: tope de PPFOI liberado en 2026-2035 (99999), CapitalCost y
FixedCost de PPFOI en 2026-2035 por 1.000 y TotalAnnualMaxCapacity de STOELE en cero en 2026-2035. Con la potencia de
PPFOI cara y sin STOELE, el LP construye solo la potencia sin la cual no cubre la demanda: la diferencia con el tope
K15b es la capacidad faltante del año. Es un diagnóstico; no cambia ningún escenario ni la base congelada.

Uso, desde ECU_NDC/Energy, después de B1 (glpsol en el PATH; unos 2 minutos y 4,5 GB de RAM por corrida):
    python Art6_calibracion/suficiencia_escenarios_art6.py --trabajo <carpeta fuera del repositorio> [--reusar]
                                                           [--escenarios A-CCOFF B-CCOFF ...]

Sin --escenarios toma los escenarios de B1_Scenario_Config.xlsx (hoja Art6_Escenarios) sin solución en la
corrida de B1 o con STOELE en 2026-2035. Escribe Art6_calibracion/calibracion_h_suficiencia_escenarios_art6.csv y
suficiencia_escenarios_art6.json (md5 de los insumos y estado de cada corrida).
"""
import argparse
import json
import shutil
import sys
from pathlib import Path

import pandas as pd

AQUI = Path(__file__).resolve().parent
ENERGIA = AQUI.parent
sys.path.insert(0, str(AQUI))
sys.path.insert(0, str(ENERGIA / "Art6_motor"))
import variante_suficiencia as VS  # noqa: E402
import comun as C  # noqa: E402
import configuracion as K  # noqa: E402

Y = VS.Y
COMP = ("CO2e_DE", "CO2e_PP", "CO2e_FUG", "CO2e_REF")


def emisiones_selected(ruta):
    """{(componente, año): kt} de la sección de emisiones por tecnología de SelectedResults.csv."""
    lineas = Path(ruta).read_text(encoding="utf-8", errors="replace").split("\n")
    emis = VS.seccion(lineas, "Annual Emissions by Technology", columnas_id=2)
    out = {}
    for (t, e, y), v in emis.items():
        if e in COMP:
            out[(e, y)] = out.get((e, y), 0.0) + 1000.0 * v
    return out


def stoele_en_salida(cod):
    if C.estado_solucion(cod) != "optimo":
        return None
    o = pd.read_csv(C.salida(cod), usecols=["Technology", "Year", "TotalTechnologyAnnualActivity"], low_memory=False)
    x = o[(o.Technology == "STOELE") & (o.Year.between(2026, 2035))]["TotalTechnologyAnnualActivity"].fillna(0)
    return float(x.sum()) * VS.PJ


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--trabajo", type=Path, required=True)
    ap.add_argument("--reusar", action="store_true")
    ap.add_argument("--escenarios", nargs="*")
    ap.add_argument("--paralelo", type=int, default=1, help="corridas de glpsol a la vez (4,5 GB de RAM cada una)")
    a = ap.parse_args()
    trabajo = a.trabajo.resolve()
    if ENERGIA.parent in trabajo.parents:
        raise SystemExit("la carpeta de trabajo debe estar fuera del repositorio")
    trabajo.mkdir(parents=True, exist_ok=True)
    shutil.copy2(ENERGIA / "OSeMOSYS_Model.txt", trabajo / "OSeMOSYS_Model.txt")
    if a.escenarios:
        elegidos = a.escenarios
    else:
        elegidos = []
        for e in K.escenarios():
            c = e["codigo"]
            st = C.estado_solucion(c)
            if st != "optimo" or (stoele_en_salida(c) or 0.0) > 0.5:
                elegidos.append(c)
    print("escenarios:", elegidos)
    filas, estado = [], {"insumos": {"OSeMOSYS_Model.txt": VS.md5(ENERGIA / "OSeMOSYS_Model.txt")}, "corridas": {}}

    def una(c):
        """Variante de potencia mínima de un escenario, en su propia subcarpeta (SelectedResults.csv no choca)."""
        sub = trabajo / c
        sub.mkdir(parents=True, exist_ok=True)
        shutil.copy2(ENERGIA / "OSeMOSYS_Model.txt", sub / "OSeMOSYS_Model.txt")
        df = C.datafile(c)
        texto = df.read_text(encoding="utf-8")
        tope = VS.leer_fila(texto, "TotalAnnualMaxCapacity", "PPFOI")
        costo = VS.datos_costo(texto)
        lib = VS.poner(texto, "TotalAnnualMaxCapacity", {"PPFOI": {y: 99999 for y in Y}, "STOELE": {y: 0 for y in Y}})
        lib = VS.poner(lib, "CapitalCost", {"PPFOI": {y: costo[("CapitalCost", y)] * VS.CARO for y in Y}})
        lib = VS.poner(lib, "FixedCost", {"PPFOI": {y: costo[("FixedCost", y)] * VS.CARO for y in Y}})
        nombre = f"{c}_potencia_minima"
        est = {}
        r = VS.resolver(sub, nombre, lib, a.reusar, est)
        em = emisiones_selected(sub / f"SelectedResults_{nombre}.csv") if r else {}
        return c, VS.md5(df), tope, r, em, est

    from concurrent.futures import ThreadPoolExecutor
    with ThreadPoolExecutor(max_workers=max(1, a.paralelo)) as ex:
        hechos = list(ex.map(una, elegidos))
    for c, md5_df, tope, r, em, est in hechos:
        estado["insumos"][f"{c}_0.txt"] = md5_df
        estado["corridas"].update(est)
        for y in Y:
            cap = r["cap"][("PPFOI", y)] * 1000 if r else None
            filas.append({"escenario": c, "estado_B1": C.estado_solucion(c), "anio": y,
                          "tope_PPFOI_MW": round(tope[y] * 1000, 2),
                          "PPFOI_variante_MW": None if cap is None else round(cap, 2),
                          "faltante_MW": None if cap is None else round(max(0.0, cap - tope[y] * 1000), 2),
                          "STOELE_variante_GWh": round(r["stoele"][y] * VS.PJ, 1) if r else None,
                          "CO2e_PP_variante_kt": round(r["co2"][y], 1) if r else None,
                          "energia_variante_kt": round(sum(em.get((k, y), 0.0) for k in COMP), 1) if r else None,
                          "variante_con_solucion": r is not None})
    # con el respaldo de emergencia en los estados de riesgo (13-10-2026) puede no quedar ningún escenario sin solución ni
    # con STOELE: la tabla se escribe igual, con su cabecera y sin filas
    t = pd.DataFrame(filas, columns=["escenario", "estado_B1", "anio", "tope_PPFOI_MW", "PPFOI_variante_MW", "faltante_MW",
                                     "STOELE_variante_GWh", "CO2e_PP_variante_kt", "energia_variante_kt",
                                     "variante_con_solucion"])
    t.to_csv(AQUI / "calibracion_h_suficiencia_escenarios_art6.csv", index=False, encoding="utf-8-sig")
    (AQUI / "suficiencia_escenarios_art6.json").write_text(json.dumps(estado, indent=1, ensure_ascii=False) + "\n",
                                                          encoding="utf-8")
    if len(t):
        print(t.pivot_table(index="anio", columns="escenario", values="faltante_MW").to_string())
    return 0


if __name__ == "__main__":
    sys.exit(main())
