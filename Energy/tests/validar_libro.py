# -*- coding: utf-8 -*-
"""Validador de B1_Scenario_Config.xlsx antes de correr B1.

Uso, desde ECU_NDC/Energy:
    python tests/validar_libro.py [ruta_del_libro]

Errores (salida 1), porque B1 los aplica mal sin avisar:
- filas con Scenario = All, que B1 aplica también a los escenarios del Modelo Climate Lead Group (CLG);
- filas que nombran un escenario que no está en la hoja Scenarios;
- claves repetidas (escenario, parámetro, tecnología o conjunto): B1 aplica solo la primera fila.
Avisos:
- filas Built-in NO cuyo método no contiene Write con mayúscula: B1 no las escribe («Overwrite» no cuenta);
- celdas vacías en las columnas clave.
Las filas de los escenarios del Modelo CLG se informan aparte, porque no se corrigen desde el Artículo 6.
"""
import sys
from pathlib import Path

import pandas as pd

LIBRO = Path(__file__).resolve().parents[1] / "B1_Scenario_Config.xlsx"
OFICIALES = {"BAU", "BAU1NDC", "NDCINC", "NDCCON"}
CLAVES = {
    "Electrical": ["Scenario", "Parameter", "Tech_Set"],
    "SmartGrid": ["Scenario", "Parameter", "Tech_Set"],
    "Efficiency": ["Scenario", "Parameter", "Set"],
    "Distance_Levers": ["Scenario", "Group_Set"],
    "Occupancy_Rate": ["Scenario", "Group_Set"],
}


def validar(ruta=LIBRO):
    escenarios = set(pd.read_excel(ruta, sheet_name="Scenarios")["Name"].dropna().astype(str))
    errores, avisos = [], []
    for hoja, claves in CLAVES.items():
        df = pd.read_excel(ruta, sheet_name=hoja)
        df["fila"] = df.index + 2
        df = df.dropna(how="all", subset=claves)
        for _, r in df[df[claves].isna().any(axis=1)].iterrows():
            avisos.append(f"{hoja} fila {r.fila}: celda vacía en {', '.join(c for c in claves if pd.isna(r[c]))}")
        for _, r in df[df["Scenario"].astype(str) == "All"].iterrows():
            errores.append(f"{hoja} fila {r.fila}: Scenario = All se aplica también a los escenarios del Modelo CLG")
        for _, r in df[~df["Scenario"].astype(str).isin(escenarios | {"All"})].iterrows():
            errores.append(f"{hoja} fila {r.fila}: el escenario {r.Scenario} no está en la hoja Scenarios")
        rep = df[df.duplicated(subset=claves, keep=False)]
        for clave, grupo in rep.groupby(claves):
            filas = ", ".join(str(f) for f in grupo.fila)
            oficial = grupo["Scenario"].astype(str).isin(OFICIALES).all()
            texto = f"{hoja} filas {filas}: clave repetida {clave}; B1 aplica solo la primera"
            (avisos if oficial else errores).append(texto + (" [CLG]" if oficial else ""))
        if "Built-in Parameter-Set" in df and "Method" in df:
            no = df["Built-in Parameter-Set"].astype(str).str.replace(" ", "").str.upper() == "NO"
            sin_write = ~df["Method"].astype(str).str.replace(" ", "").str.contains("Write", regex=False)
            for _, r in df[no & sin_write].iterrows():
                avisos.append(f"{hoja} fila {r.fila}: Built-in NO sin Write, B1 no la escribe"
                              + (" [CLG]" if r.Scenario in OFICIALES else ""))
    for e in errores:
        print("ERROR ", e)
    for a in avisos:
        print("AVISO ", a)
    print(f"{len(errores)} errores y {len(avisos)} avisos en {Path(ruta).name}")
    return 1 if errores else 0


if __name__ == "__main__":
    sys.exit(validar(sys.argv[1] if len(sys.argv) > 1 else LIBRO))
