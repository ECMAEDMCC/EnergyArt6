# -*- coding: utf-8 -*-
"""Prueba de no regresión de los cuatro escenarios del Modelo Climate Lead Group (CLG) del sector energía.

Uso, desde ECU_NDC/Energy:
    python tests/no_regresion.py --fijar [ref]   guarda la línea base desde una versión de git (main por omisión)
    python tests/no_regresion.py                 compara las salidas actuales de Executables con la línea base

Por escenario compara tres huellas y una tabla:
- md5 del _Output.csv y del _Input.csv sin retornos de carro (git normaliza los finales de línea);
- md5 del datafile con sus líneas ordenadas, porque B1 no escribe los bloques siempre en el mismo orden;
- AnnualTechnologyEmission sumada por emisión y año, con tolerancia cero.
Sale con código 1 si algún escenario del Modelo CLG difiere.
"""
import hashlib
import io
import json
import subprocess
import sys
from datetime import date
from pathlib import Path

import pandas as pd

ENERGY = Path(__file__).resolve().parents[1]
REPO = ENERGY.parent
BASE = Path(__file__).with_name("linea_base_main.json")
OFICIALES = ["BAU", "BAU1NDC", "NDCINC", "NDCCON"]


def _rutas(esc):
    raiz = f"Energy/Executables/{esc}_0/{esc}_0"
    return {"output": raiz + "_Output.csv", "input": raiz + "_Input.csv", "datafile": raiz + ".txt"}


def _leer_git(ref):
    def leer(ruta):
        return subprocess.run(["git", "-C", str(REPO), "show", f"{ref}:{ruta}"],
                              capture_output=True, check=True).stdout
    return leer


def _leer_disco(ruta):
    return (REPO / ruta).read_bytes()


def _md5(contenido):
    return hashlib.md5(contenido).hexdigest()


def _emisiones(output):
    df = pd.read_csv(io.BytesIO(output), usecols=["Emission", "Year", "AnnualTechnologyEmission"], low_memory=False)
    serie = df.dropna(subset=["Emission"]).groupby(["Emission", "Year"]).AnnualTechnologyEmission.sum()
    return {f"{e}|{int(y)}": round(float(v), 9) for (e, y), v in serie.items()}


def huellas(leer):
    resultado = {}
    for esc in OFICIALES:
        r = _rutas(esc)
        output = leer(r["output"]).replace(b"\r", b"")
        entrada = leer(r["input"]).replace(b"\r", b"")
        datafile = leer(r["datafile"]).replace(b"\r", b"")
        resultado[esc] = {
            "output_md5": _md5(output),
            "input_md5": _md5(entrada),
            "datafile_ordenado_md5": _md5(b"\n".join(sorted(datafile.split(b"\n")))),
            "emisiones": _emisiones(output),
        }
    return resultado


def fijar(ref="main"):
    commit = subprocess.run(["git", "-C", str(REPO), "rev-parse", ref], capture_output=True, text=True,
                            check=True).stdout.strip()
    base = {"ref": ref, "commit": commit, "fecha": date.today().isoformat(), "escenarios": huellas(_leer_git(ref))}
    BASE.write_text(json.dumps(base, indent=1, ensure_ascii=False), encoding="utf-8")
    for esc, h in base["escenarios"].items():
        print(f"{esc:8s} output {h['output_md5'][:8]}  input {h['input_md5'][:8]}  datafile {h['datafile_ordenado_md5'][:8]}")
    print(f"Línea base fijada desde {ref} ({commit[:7]}) en {BASE.name}")


def verificar():
    base = json.loads(BASE.read_text(encoding="utf-8"))
    actual = huellas(_leer_disco)
    falla = False
    for esc in OFICIALES:
        b, a = base["escenarios"][esc], actual[esc]
        difs = [k for k in ("output_md5", "input_md5", "datafile_ordenado_md5") if a[k] != b[k]]
        claves = set(a["emisiones"]) | set(b["emisiones"])
        dmax = max(abs(a["emisiones"].get(k, 0.0) - b["emisiones"].get(k, 0.0)) for k in claves)
        estado = "IGUAL" if not difs and dmax == 0 else "DIFERENTE"
        falla |= estado != "IGUAL"
        print(f"{esc:8s} {estado:9s} huellas distintas: {', '.join(difs) or 'ninguna'}; "
              f"diferencia máxima de emisiones: {dmax:.9f} Mt")
    print(f"Línea base: {base['ref']} ({base['commit'][:7]}, fijada el {base['fecha']})")
    return 1 if falla else 0


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--fijar":
        fijar(sys.argv[2] if len(sys.argv) > 2 else "main")
    else:
        sys.exit(verificar())
