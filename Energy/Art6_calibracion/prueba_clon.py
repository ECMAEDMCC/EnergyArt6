# -*- coding: utf-8 -*-
"""Prueba de clon: INCA6 frente a NDCINC y CONA6 frente a NDCCON, con tolerancia cero.

Uso, desde ECU_NDC/Energy, después de correr B1:
    python Art6_calibracion/prueba_clon.py

Compara, para cada par, las salidas de Executables/<esc>_0:
1. AnnualTechnologyEmission sumada por (Emission, Year);
2. ProductionByTechnology sumada por (Technology, Year);
3. el _Output.csv completo como texto, sin la columna Strategy y con las filas ordenadas;
4. el _Input.csv completo como texto, sin las columnas Strategy y Strategy.ID;
5. el datafile con sus líneas ordenadas (B1 no escribe los bloques siempre en el mismo orden).
Solo tiene sentido mientras el archivo de correcciones esté vacío: con correcciones los clones deben diferir.
Guarda el resultado en Art6_calibracion/prueba_clon_resultado.json y sale con 1 si algún par difiere.
"""
import hashlib
import json
import sys
from pathlib import Path

import pandas as pd

ENERGIA = Path(__file__).resolve().parents[1]
PARES = {"INCA6": "NDCINC", "CONA6": "NDCCON"}


def ruta(esc, sufijo):
    return ENERGIA / "Executables" / f"{esc}_0" / f"{esc}_0{sufijo}"


def md5(p):
    return hashlib.md5(p.read_bytes().replace(b"\r", b"")).hexdigest()


def agregado(df, claves, variable):
    d = df.dropna(subset=[variable])
    d = d[d[claves[0]].notna()]
    return d.groupby(claves)[variable].sum()


def comparar_series(a, b):
    a, b = a.align(b, fill_value=0.0)
    dif = (a - b).abs()
    return {"claves": int(len(a)), "diferencia_maxima": float(dif.max()) if len(dif) else 0.0,
            "claves_distintas": int((dif > 0).sum())}


def tabla_texto(p, quitar):
    df = pd.read_csv(p, dtype=str, keep_default_na=False)
    df = df.drop(columns=[c for c in quitar if c in df.columns])
    return df.sort_values(list(df.columns)).reset_index(drop=True)


def main():
    resultado, falla = {}, False
    for clon, origen in PARES.items():
        r = {}
        oc = pd.read_csv(ruta(clon, "_Output.csv"), low_memory=False)
        oo = pd.read_csv(ruta(origen, "_Output.csv"), low_memory=False)
        r["estrategia_en_salida"] = [sorted(oc.Strategy.unique().tolist()), sorted(oo.Strategy.unique().tolist())]
        r["AnnualTechnologyEmission_por_emision_anio"] = comparar_series(
            agregado(oc, ["Emission", "Year"], "AnnualTechnologyEmission"),
            agregado(oo, ["Emission", "Year"], "AnnualTechnologyEmission"))
        r["ProductionByTechnology_por_tecnologia_anio"] = comparar_series(
            agregado(oc, ["Technology", "Year"], "ProductionByTechnology"),
            agregado(oo, ["Technology", "Year"], "ProductionByTechnology"))
        tc, to = tabla_texto(ruta(clon, "_Output.csv"), ["Strategy"]), tabla_texto(ruta(origen, "_Output.csv"), ["Strategy"])
        r["output_completo_igual"] = bool(tc.equals(to))
        ic = tabla_texto(ruta(clon, "_Input.csv"), ["Strategy", "Strategy.ID"])
        io_ = tabla_texto(ruta(origen, "_Input.csv"), ["Strategy", "Strategy.ID"])
        r["input_completo_igual"] = bool(ic.equals(io_))
        lc = sorted(ruta(clon, ".txt").read_bytes().replace(b"\r", b"").split(b"\n"))
        lo = sorted(ruta(origen, ".txt").read_bytes().replace(b"\r", b"").split(b"\n"))
        r["datafile_ordenado_igual"] = lc == lo
        r["md5_output"] = {clon: md5(ruta(clon, "_Output.csv")), origen: md5(ruta(origen, "_Output.csv"))}
        igual = (r["AnnualTechnologyEmission_por_emision_anio"]["diferencia_maxima"] == 0
                 and r["ProductionByTechnology_por_tecnologia_anio"]["diferencia_maxima"] == 0
                 and r["output_completo_igual"] and r["input_completo_igual"] and r["datafile_ordenado_igual"])
        r["estado"] = "IGUAL" if igual else "DIFERENTE"
        falla |= not igual
        resultado[f"{clon}_vs_{origen}"] = r
        e, p = r["AnnualTechnologyEmission_por_emision_anio"], r["ProductionByTechnology_por_tecnologia_anio"]
        print(f"{clon} frente a {origen}: {r['estado']}")
        print(f"  AnnualTechnologyEmission por (emisión, año): {e['claves']} claves, "
              f"diferencia máxima {e['diferencia_maxima']:.12g}, claves distintas {e['claves_distintas']}")
        print(f"  ProductionByTechnology por (tecnología, año): {p['claves']} claves, "
              f"diferencia máxima {p['diferencia_maxima']:.12g}, claves distintas {p['claves_distintas']}")
        print(f"  Output completo igual: {r['output_completo_igual']}; Input completo igual: "
              f"{r['input_completo_igual']}; datafile ordenado igual: {r['datafile_ordenado_igual']}")
    Path(__file__).with_name("prueba_clon_resultado.json").write_text(
        json.dumps(resultado, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    return 1 if falla else 0


if __name__ == "__main__":
    sys.exit(main())
