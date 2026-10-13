# -*- coding: utf-8 -*-
"""Prueba permanente de la base congelada del Artículo 6 (INCA6, CONA6, INCA6G y CONA6G).

Decisión del 13-10-2026: la base corregida queda congelada con K01-K16 y G01 en la corrida de B1 del
13-10-2026, 08:26:55-08:31:05. La corrida incluye RE01 (respaldo de emergencia en INCA6G), que es un supuesto de cierre introducido en esa corrida, fuera del acuerdo original (respaldo de fuel oil solo en
los estados de riesgo); se aprobó el 13-10-2026, después de la verificación independiente, conservarlo rotulado
«con cierre de fuel oil de emergencia», con el peso del respaldo al lado (tests/logs/paso13_base_k16_2026-10-13.log;
CONA6_0_Output.csv md5 0410ba4f...). Frente a la base anterior solo cambian el piso de PPFOI 2026-2035 (K16) en las
cuatro referencias y las cuatro filas RE01 de INCA6G (tests/diferencias_clones.py --frente-a). La base anterior (K01-K15
y G01, corrida del 12-10-2026, 16:46:51-16:50:54, CONA6 331e5665) queda en tests/base_congelada_2026-10-12.json y sus
copias en _stale_ECU_NDC_2026-10-11/base_congelada_2026-10-12_1646. Ninguna corrección K ni ninguna fila de esas
referencias cambia después del corte: lo nuevo va a escenarios aparte.

Uso, desde ECU_NDC/Energy:
    python tests/base_congelada.py            compara la corrida actual con la congelada; sale con 1 si difiere
    python tests/base_congelada.py --fijar    (solo una vez, en el corte) guarda las huellas y copia las salidas

Qué compara, por referencia:
- el _Output.csv sin la columna Strategy, con las filas ordenadas (md5 del contenido normalizado). Si difiere y existe
  la copia congelada, informa las columnas y el primer año con diferencia;
- el datafile con sus líneas ordenadas (B1 no escribe los bloques siempre en el mismo orden);
- la carpeta A2_Output_Params/<ref> (md5 de nombres y contenidos);
- las filas de la referencia en las hojas Scenarios, Electrical, SmartGrid, Efficiency, Distance_Levers y
  Occupancy_Rate de B1_Scenario_Config.xlsx (valores en caché, sin estilos);
- el estado de la solución: si una referencia no tuviera solución en la corrida congelada (INCA6G en la base del
  12-10-2026), la prueba exige que siga así (sin _Output.csv nuevo). En la base del 13-10-2026 las cuatro tienen solución.
"""
import hashlib
import io
import json
import shutil
import sys
from pathlib import Path

import pandas as pd

ENERGY = Path(__file__).resolve().parents[1]
FIJO = Path(__file__).with_name("base_congelada.json")
COPIAS = ENERGY.parents[1] / "_stale_ECU_NDC_2026-10-11" / "base_congelada_2026-10-13_0826"
REFERENCIAS = ["INCA6", "CONA6", "INCA6G", "CONA6G"]
HOJAS = ["Scenarios", "Electrical", "SmartGrid", "Efficiency", "Distance_Levers", "Occupancy_Rate"]
CORRIDA = {"log": "tests/logs/paso13_base_k16_2026-10-13.log", "inicio": "2026-10-13 08:26:55",
           "fin": "2026-10-13 08:31:05", "CONA6_0_Output_md5": "0410ba4f6df37851dcac6ce1e72dbbb1",
           "base_anterior": {"huellas": "tests/base_congelada_2026-10-12.json",
                             "copias": "_stale_ECU_NDC_2026-10-11/base_congelada_2026-10-12_1646",
                             "CONA6_0_Output_md5": "331e5665a80029b8549059092e9bc161"},
           "cambios_frente_a_la_anterior": "K16 (piso de PPFOI 2026-2035 = 5,0567 PJ) en las cuatro referencias; RE01 "
                                           "(respaldo de emergencia) en INCA6G"}


def _md5(b):
    return hashlib.md5(b).hexdigest()


def huella_output(ruta):
    """md5 del _Output.csv sin Strategy y con filas ordenadas; None si no existe."""
    if not ruta.exists():
        return None
    df = pd.read_csv(ruta, low_memory=False, dtype=str, keep_default_na=False)
    df = df.drop(columns=[c for c in ("Strategy",) if c in df.columns])
    df = df.sort_values(list(df.columns)).reset_index(drop=True)
    return _md5(df.to_csv(index=False).encode("utf-8"))


def huella_datafile(ruta):
    if not ruta.exists():
        return None
    lineas = ruta.read_bytes().replace(b"\r", b"").split(b"\n")
    return _md5(b"\n".join(sorted(lineas)))


def huella_carpeta(carpeta):
    h = hashlib.md5()
    for f in sorted(Path(carpeta).iterdir()):
        h.update(f.name.encode())
        h.update(f.read_bytes().replace(b"\r", b""))
    return h.hexdigest()


def huella_filas(ref):
    """md5 de las filas de la referencia en cada hoja del libro (valores en caché)."""
    salida = {}
    libro = ENERGY / "B1_Scenario_Config.xlsx"
    for hoja in HOJAS:
        df = pd.read_excel(libro, sheet_name=hoja, dtype=str)
        col = "Name" if hoja == "Scenarios" else "Scenario"
        x = df[df[col].astype(str) == ref].fillna("")
        salida[hoja] = _md5(x.to_csv(index=False).encode("utf-8"))
    return salida


def huellas():
    out = {}
    for ref in REFERENCIAS:
        base = ENERGY / "Executables" / f"{ref}_0" / f"{ref}_0"
        out[ref] = {"output": huella_output(Path(str(base) + "_Output.csv")),
                    "datafile": huella_datafile(Path(str(base) + ".txt")),
                    "A2": huella_carpeta(ENERGY / "A2_Output_Params" / ref),
                    "filas_libro": huella_filas(ref)}
    return out


def _diagnostico(ref):
    """Columnas y años que difieren frente a la copia congelada."""
    copia = COPIAS / f"{ref}_0_Output.csv"
    actual = ENERGY / "Executables" / f"{ref}_0" / f"{ref}_0_Output.csv"
    if not copia.exists() or not actual.exists():
        return "sin copia congelada o sin salida actual para diagnosticar"
    claves = ["Fuel", "Technology", "Emission", "Year"]
    a = pd.read_csv(copia, low_memory=False).drop(columns=["Strategy"]).fillna("")
    b = pd.read_csv(actual, low_memory=False).drop(columns=["Strategy"]).fillna("")
    a = a.sort_values(claves).reset_index(drop=True)
    b = b.sort_values(claves).reset_index(drop=True)
    if len(a) != len(b):
        return f"filas: congelada {len(a)}, actual {len(b)}"
    cols = []
    for c in a.columns:
        if c in claves:
            continue
        x = pd.to_numeric(a[c], errors="coerce").fillna(0)
        y = pd.to_numeric(b[c], errors="coerce").fillna(0)
        d = (x - y).abs()
        if (d > 1e-9).any():
            cols.append(f"{c} (máx. {d.max():.6g}, primer año {int(a.loc[d.idxmax(), 'Year'])})")
    return "columnas distintas: " + ("; ".join(cols) if cols else "ninguna numérica (cambio de formato)")


def fijar():
    if FIJO.exists():
        raise SystemExit("base_congelada.json ya existe: la base está congelada y no se vuelve a fijar")
    datos = {"corrida": CORRIDA, "referencias": huellas()}
    if datos["referencias"]["CONA6"]["output"] is None:
        raise SystemExit("falta CONA6_0_Output.csv")
    md5_cona6 = _md5((ENERGY / "Executables" / "CONA6_0" / "CONA6_0_Output.csv").read_bytes())
    if md5_cona6 != CORRIDA["CONA6_0_Output_md5"]:
        raise SystemExit(f"CONA6_0_Output.csv tiene md5 {md5_cona6}, no el de la corrida congelada")
    COPIAS.mkdir(parents=True, exist_ok=True)
    for ref in REFERENCIAS:
        for suf in ("_Output.csv", ".txt"):
            origen = ENERGY / "Executables" / f"{ref}_0" / f"{ref}_0{suf}"
            if origen.exists():
                shutil.copy2(origen, COPIAS / origen.name)
    datos["copias"] = str(COPIAS)
    FIJO.write_text(json.dumps(datos, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"base congelada fijada en {FIJO.name}; copias en {COPIAS}")


def comparar():
    if not FIJO.exists():
        raise SystemExit("falta tests/base_congelada.json")
    fijo = json.loads(FIJO.read_text(encoding="utf-8"))["referencias"]
    actual = huellas()
    fallas = 0
    for ref in REFERENCIAS:
        f, a = fijo[ref], actual[ref]
        partes = []
        if f["output"] is None:
            ok_out = a["output"] is None
            partes.append("sin solución, como en la corrida congelada" if ok_out
                          else "ahora tiene _Output.csv y la corrida congelada no tenía solución")
        else:
            ok_out = f["output"] == a["output"]
            partes.append("Output igual" if ok_out else "Output DISTINTO: " + _diagnostico(ref))
        ok_dat = f["datafile"] == a["datafile"]
        ok_a2 = f["A2"] == a["A2"]
        ok_libro = f["filas_libro"] == a["filas_libro"]
        partes.append("datafile igual" if ok_dat else "datafile DISTINTO")
        partes.append("A2 igual" if ok_a2 else "A2 DISTINTA")
        partes.append("filas del libro iguales" if ok_libro else "filas del libro DISTINTAS: " + ", ".join(
            h for h in HOJAS if f["filas_libro"].get(h) != a["filas_libro"].get(h)))
        ok = ok_out and ok_dat and ok_a2 and ok_libro
        fallas += 0 if ok else 1
        print(("IGUAL    " if ok else "DIFIERE  ") + ref + ": " + "; ".join(partes))
    print("base congelada: " + ("IGUAL" if not fallas else f"{fallas} referencias difieren"))
    return 1 if fallas else 0


if __name__ == "__main__":
    if "--fijar" in sys.argv[1:]:
        fijar()
    else:
        sys.exit(comparar())
