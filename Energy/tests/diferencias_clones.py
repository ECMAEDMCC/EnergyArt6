# -*- coding: utf-8 -*-
"""Prueba permanente: toda diferencia entre el datafile de un clon y el de su escenario del Modelo Climate Lead Group (CLG)
está en correcciones_K.csv.

Uso, desde ECU_NDC/Energy, después de correr B1:
    python tests/diferencias_clones.py

Compara Executables/CONA6_0/CONA6_0.txt y CONA6G con Executables/NDCCON_0/NDCCON_0.txt, e INCA6 e INCA6G con NDCINC, valor por valor
(parámetro, índices y año), además de los conjuntos (set) y los valores por omisión (default). Falla (salida 1) si:
- algún conjunto o valor por omisión difiere;
- un valor difiere y ninguna fila de Art6_calibracion/correcciones_K.csv lo explica (misma tecnología, mismo índice de
  emisión o combustible, mismo año, escenario incluido);
- un valor explicado no coincide con el de la fila que manda (tolerancia 6e-5 para las filas que pasan por una hoja del
  libro, que B1 redondea a cuatro decimales; 1e-9 relativo para las que van a A2, que B1 copia tal cual).
Escribe tests/logs/diferencias_clones.csv con cada diferencia y su explicación.

Con --frente-a <carpeta> --codigos K16,RE01 compara cada clon con su datafile de una base congelada anterior (copias
<clon>_0.txt de la carpeta) y falla si algún valor distinto no lo explica una fila de esos códigos (13-10-2026: la base
con K16 frente a la del 12-10-2026).
"""
import csv
import re
import sys
from pathlib import Path

ENERGIA = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ENERGIA / "Art6_calibracion"))
from verificar_correcciones import leer_datafile, anios_de  # noqa: E402

PARES = {"CONA6": "NDCCON", "INCA6": "NDCINC", "CONA6G": "NDCCON", "INCA6G": "NDCINC"}
DESTINOS_A2 = ("A2", "A2_nueva", "A2_quita_SmartGrid")
TOL_HOJA = 6e-5


def cabeceras(ruta):
    """Líneas set y param ... default de un datafile."""
    salida = []
    for linea in ruta.read_text(encoding="utf-8").split("\n"):
        if linea.startswith("set "):
            salida.append(" ".join(linea.split()))
        m = re.match(r"^param\s+(\w+)\s+default\s+(\S+)", linea)
        if m:
            salida.append(f"param {m.group(1)} default {m.group(2)}")
    return sorted(salida)


def clave_csv(k):
    """Clave del datafile -> (parámetro, tecnología, índice2, año) como en correcciones_K.csv."""
    par = k[0]
    if len(k) == 2:
        return (par, k[1], None, None)
    if par == "CapacityFactor":
        return (par, k[1], None, int(k[3]))
    if par in ("EmissionActivityRatio", "InputActivityRatio", "OutputActivityRatio"):
        return (par, k[1], k[2], int(k[4]))
    if len(k) == 3 and k[2].isdigit():
        return (par, k[1], None, int(k[2]))
    return (par,) + tuple(k[1:])


def explicaciones(clon, prefijos=None):
    filas = list(csv.DictReader((ENERGIA / "Art6_calibracion" / "correcciones_K.csv").open(encoding="utf-8-sig")))
    filas = [f for f in filas if clon in [e.strip() for e in f["escenarios"].split(";")]]
    if prefijos:
        filas = [f for f in filas if f["codigo"].startswith(tuple(prefijos))]
    orden = sorted(range(len(filas)), key=lambda j: filas[j]["hoja_o_carpeta"] not in DESTINOS_A2)
    manda = {}
    for j in orden:
        f = filas[j]
        partes = [p.strip() for p in f["tecnologia"].split(";")]
        tec, idx2 = partes[0], (partes[1] if len(partes) > 1 else None)
        anios = anios_de(f["anios"])
        v = [float(x) for x in f["valores"].split(";")]
        v = v * len(anios) if len(v) == 1 else v
        for a, x in zip(anios, v):
            manda[(f["parametro"], tec, idx2, a)] = (f["codigo"], x, f["hoja_o_carpeta"])
    return manda


def comparar(clon, ref):
    r_c = ENERGIA / "Executables" / f"{clon}_0" / f"{clon}_0.txt"
    r_o = ENERGIA / "Executables" / f"{ref}_0" / f"{ref}_0.txt"
    problemas, filas = [], []
    cab_c, cab_o = cabeceras(r_c), cabeceras(r_o)
    if cab_c != cab_o:
        problemas.append(f"{clon}: conjuntos o valores por omisión distintos de {ref}: "
                         f"{sorted(set(cab_c) ^ set(cab_o))[:5]}")
    d_c = {k: v for k, (v, _) in leer_datafile(r_c).items()}
    d_o = {k: v for k, (v, _) in leer_datafile(r_o).items()}
    manda = explicaciones(clon)
    n_dif = n_ok = 0
    for k in sorted(set(d_c) | set(d_o), key=str):
        vc, vo = d_c.get(k), d_o.get(k)
        if vc is not None and vo is not None and abs(vc - vo) <= 1e-12 * max(1.0, abs(vo)):
            continue
        n_dif += 1
        kc = clave_csv(k)
        exp = manda.get(kc)
        estado = "EXPLICADA"
        if exp is None:
            estado = "SIN_EXPLICAR"
        elif vc is None:
            estado = "AUSENTE_EN_CLON"
        else:
            tol = TOL_HOJA if exp[2] not in DESTINOS_A2 else 1e-9 * max(1.0, abs(exp[1])) + 1e-15
            if abs(vc - exp[1]) > tol:
                estado = "VALOR_DISTINTO_AL_CSV"
        if estado != "EXPLICADA":
            problemas.append(f"{clon} {k}: {estado} (clon {vc}, CLG {vo}, CSV {exp[1] if exp else None})")
        else:
            n_ok += 1
        filas.append({"clon": clon, "escenario_CLG": ref, "clave": "|".join(str(x) for x in k), "valor_clon": vc,
                      "valor_CLG": vo, "estado": estado, "codigo": exp[0] if exp else "",
                      "valor_csv": exp[1] if exp else ""})
    print(f"{clon} frente a {ref}: {n_dif} valores distintos, {n_ok} explicados por correcciones_K.csv, "
          f"{n_dif - n_ok} sin explicar o con valor distinto")
    return problemas, filas


def frente_a_base(carpeta, prefijos):
    """Compara el datafile actual de cada clon con su copia en carpeta (una base congelada anterior): cada valor
    distinto debe estar en una fila de correcciones_K.csv cuyo código empieza por uno de los prefijos, con su valor.
    Escribe tests/logs/diferencias_frente_a_base.csv y un resumen por parámetro, tecnología y años."""
    problemas, todas = [], []
    for clon in PARES:
        r_a = ENERGIA / "Executables" / f"{clon}_0" / f"{clon}_0.txt"
        r_p = Path(carpeta) / f"{clon}_0.txt"
        if cabeceras(r_a) != cabeceras(r_p):
            problemas.append(f"{clon}: conjuntos o valores por omisión distintos de la base anterior")
        d_a = {k: v for k, (v, _) in leer_datafile(r_a).items()}
        d_p = {k: v for k, (v, _) in leer_datafile(r_p).items()}
        manda = explicaciones(clon, prefijos)
        grupos = {}
        for k in sorted(set(d_a) | set(d_p), key=str):
            va, vp = d_a.get(k), d_p.get(k)
            if va is not None and vp is not None and abs(va - vp) <= 1e-12 * max(1.0, abs(vp)):
                continue
            kc = clave_csv(k)
            exp = manda.get(kc)
            estado = "EXPLICADA"
            if exp is None:
                estado = "SIN_EXPLICAR"
            elif va is None:
                estado = "AUSENTE"
            else:
                tol = TOL_HOJA if exp[2] not in DESTINOS_A2 else 1e-9 * max(1.0, abs(exp[1])) + 1e-15
                if abs(va - exp[1]) > tol:
                    estado = "VALOR_DISTINTO_AL_CSV"
            if estado != "EXPLICADA":
                problemas.append(f"{clon} {k}: {estado} (actual {va}, base anterior {vp})")
            g = (kc[0], kc[1], kc[2], exp[0] if exp else "")
            grupos.setdefault(g, []).append(kc[3])
            todas.append({"clon": clon, "clave": "|".join(str(x) for x in k), "valor_actual": va,
                          "valor_base_anterior": vp, "estado": estado, "codigo": exp[0] if exp else ""})
        print(f"{clon}: {sum(len(v) for v in grupos.values())} valores distintos de la base anterior")
        for (par, tec, idx2, cod), anios in sorted(grupos.items(), key=str):
            a = sorted(x for x in anios if x is not None)
            print(f"    {par} {tec}{' ' + idx2 if idx2 else ''}: {a[0] if a else ''}-{a[-1] if a else ''} "
                  f"({len(anios)} valores) {cod or 'SIN CÓDIGO'}")
    salida = ENERGIA / "tests" / "logs" / "diferencias_frente_a_base.csv"
    salida.parent.mkdir(parents=True, exist_ok=True)
    with salida.open("w", encoding="utf-8", newline="") as h:
        w = csv.DictWriter(h, fieldnames=list(todas[0]) if todas else ["clon"], lineterminator="\n")
        w.writeheader()
        w.writerows(todas)
    for p in problemas[:40]:
        print("FALLA ", p)
    print("Resultado frente a la base anterior:",
          "SOLO CAMBIAN LAS FILAS " + ", ".join(prefijos) if not problemas else f"{len(problemas)} problemas")
    return 1 if problemas else 0


def main():
    if "--frente-a" in sys.argv:
        i = sys.argv.index("--frente-a")
        prefijos = sys.argv[sys.argv.index("--codigos") + 1].split(",") if "--codigos" in sys.argv else None
        return frente_a_base(sys.argv[i + 1], prefijos)
    problemas, todas = [], []
    for clon, ref in PARES.items():
        p, f = comparar(clon, ref)
        problemas += p
        todas += f
    salida = ENERGIA / "tests" / "logs" / "diferencias_clones.csv"
    salida.parent.mkdir(parents=True, exist_ok=True)
    with salida.open("w", encoding="utf-8", newline="") as h:
        w = csv.DictWriter(h, fieldnames=list(todas[0]) if todas else ["clon"], lineterminator="\n")
        w.writeheader()
        w.writerows(todas)
    for p in problemas[:40]:
        print("FALLA ", p)
    print("Resultado:", "IGUAL SALVO LO EXPLICADO" if not problemas else f"{len(problemas)} problemas")
    return 1 if problemas else 0


if __name__ == "__main__":
    sys.exit(main())
