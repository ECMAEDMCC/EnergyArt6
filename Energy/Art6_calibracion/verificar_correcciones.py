# -*- coding: utf-8 -*-
"""Comprueba que cada corrección de correcciones_K.csv quedó escrita en Executables/<esc>_0/<esc>_0.txt.

Uso, desde ECU_NDC/Energy, después de correr B1:
    python Art6_calibracion/verificar_correcciones.py

Por fila del CSV y escenario (solo los escenarios de la columna escenarios) informa ESCRITA (todos los años con el valor de la fila), SUSTITUIDA (años que una fila
posterior del mismo vector reemplaza; se comprueba el valor de la fila que manda) o DIFERENTE, con la diferencia
máxima y el número de línea del datafile donde está el vector. Tolerancia 6e-5: B1 redondea a cuatro decimales las
filas de SmartGrid y las de Electrical (CONA6 tiene una fila «intact» sobre el techo de PPHDAMAB).
Escribe Art6_calibracion/verificacion_datafiles.csv y sale con 1 si alguna fila es DIFERENTE.
Además comprueba, en los cuatro clones: la identidad CO2e_PP = CO2_PP + 28 CH4_PP + 265 N2O_PP (K08g); que el CO2e_PP de
las ocho térmicas sea el factor IPCC por el IAR del propio datafile (K08 con K13); y que el combustible por tipo del
_Output.csv quede a ±2,1 % del BEN 2025, tabla 2.28, en 2015-2025 (K13).
"""
import csv
import re
import sys
from pathlib import Path

ENERGIA = Path(__file__).resolve().parents[1]
AQUI = Path(__file__).resolve().parent
ESCENARIOS = ("INCA6", "CONA6", "INCA6G", "CONA6G")
TOL = 6e-5


def leer_datafile(ruta):
    """{(parámetro, índices sin región...): (valor, línea)} para los bloques param del datafile de B1."""
    datos = {}
    lineas = ruta.read_text(encoding="utf-8").split("\n")
    i, n = 0, len(lineas)
    while i < n:
        m = re.match(r"^param\s+(\w+)\s+default\s+\S+\s*(:=|:)\s*$", lineas[i])
        if not m:
            i += 1
            continue
        par, forma = m.group(1), m.group(2)
        i += 1
        if forma == ":":  # parámetro de dos índices: cabecera de columnas y una fila por región
            cols = lineas[i].replace(":=", "").split()
            i += 1
            while i < n and lineas[i].strip() != ";":
                partes = lineas[i].split()
                for c, v in zip(cols, partes[1:]):
                    datos[(par, c)] = (float(v), i + 1)
                i += 1
            continue
        fijos, cols = None, None
        while i < n and lineas[i].strip() != ";":
            s = lineas[i].strip()
            if s.startswith("["):
                fijos = s.rstrip(":").strip("[]").split(",")[1:]  # sin la región
                i += 1
                cols = lineas[i].replace(":=", "").split()
                i += 1
                continue
            partes = s.split()
            if partes and fijos is not None:
                clave_fila = partes[0]
                for c, v in zip(cols, partes[1:]):
                    idx, k = [], 0
                    for f in fijos:
                        if f == "*":
                            idx.append(clave_fila if k == 0 else c)
                            k += 1
                        else:
                            idx.append(f)
                    datos[(par,) + tuple(idx)] = (float(v), i + 1)
            i += 1
        i += 1
    return datos


def clave(param, tec, idx2, anio):
    if anio is None:
        return (param, tec)
    if param == "CapacityFactor":
        return (param, tec, "All", str(anio))
    if param in ("EmissionActivityRatio", "InputActivityRatio", "OutputActivityRatio"):
        return (param, tec, idx2, "1", str(anio))
    return (param, tec, str(anio))


def anios_de(texto):
    if texto == "sin_anio":
        return [None]
    salida = []
    for t in texto.split(";"):
        if "-" in t:
            a, b = (int(x) for x in t.split("-"))
            salida += list(range(a, b + 1))
        else:
            salida.append(int(t))
    return salida


def main():
    filas = list(csv.DictReader((AQUI / "correcciones_K.csv").open(encoding="utf-8-sig")))
    for f in filas:
        partes = [p.strip() for p in f["tecnologia"].split(";")]
        f["tec"], f["idx2"] = partes[0], (partes[1] if len(partes) > 1 else None)
        f["anios_l"] = anios_de(f["anios"])
        v = [float(x) for x in f["valores"].split(";")]
        f["valores_l"] = v * len(f["anios_l"]) if len(v) == 1 else v
    salida, falla = [], False
    for esc in ESCENARIOS:
        # filas que se aplican al escenario y valor que manda por (parámetro, tecnología, índice2, año): la última fila
        # (orden de aplicación del generador: carpeta A2 primero, después hojas; dentro de cada grupo, orden del archivo)
        filas_e = [f for f in filas if esc in [x.strip() for x in f["escenarios"].split(";")]]
        orden = sorted(range(len(filas_e)),
                       key=lambda j: filas_e[j]["hoja_o_carpeta"] not in ("A2", "A2_nueva", "A2_quita_SmartGrid"))
        manda = {}
        for j in orden:
            f = filas_e[j]
            for a, v in zip(f["anios_l"], f["valores_l"]):
                manda[(f["parametro"], f["tec"], f["idx2"], a)] = (f["codigo"], v)
        ruta = ENERGIA / "Executables" / f"{esc}_0" / f"{esc}_0.txt"
        datos = leer_datafile(ruta)
        for f in filas_e:
            dif, lineas, sustituidos, faltan = 0.0, set(), {}, []
            for a, v in zip(f["anios_l"], f["valores_l"]):
                codigo_manda, v_manda = manda[(f["parametro"], f["tec"], f["idx2"], a)]
                if codigo_manda != f["codigo"]:
                    sustituidos.setdefault(codigo_manda, []).append(a)
                k = clave(f["parametro"], f["tec"], f["idx2"], a)
                if k not in datos:
                    faltan.append(a)
                    continue
                val, linea = datos[k]
                dif = max(dif, abs(val - v_manda))
                lineas.add(linea)
            if faltan:
                estado = "AUSENTE"
            elif dif > TOL:
                estado = "DIFERENTE"
            else:
                estado = "ESCRITA" if not sustituidos else "ESCRITA_CON_AÑOS_SUSTITUIDOS"
            falla |= estado in ("AUSENTE", "DIFERENTE")
            a0, a1 = f["anios_l"][0], f["anios_l"][-1]
            muestra = []
            for a in (a0, a1) if a0 != a1 else (a0,):
                k = clave(f["parametro"], f["tec"], f["idx2"], a)
                if k in datos:
                    muestra.append(f"{a if a is not None else 'sin año'}={datos[k][0]:g}")
            salida.append({"escenario": esc, "codigo": f["codigo"], "parametro": f["parametro"],
                           "tecnologia": f["tecnologia"], "anios": f["anios"], "estado": estado,
                           "dif_max": f"{dif:.2e}", "lineas_datafile": ";".join(str(x) for x in sorted(lineas)),
                           "muestra_datafile": " ".join(muestra),
                           "sustituida_por": "; ".join(f"{c} ({min(y)}-{max(y)})" for c, y in sustituidos.items()),
                           "faltan": ";".join(str(x) for x in faltan)})
    with (AQUI / "verificacion_datafiles.csv").open("w", encoding="utf-8", newline="") as h:
        w = csv.DictWriter(h, fieldnames=list(salida[0]), lineterminator="\n")
        w.writeheader()
        w.writerows(salida)
    for s in salida:
        if s["estado"] != "ESCRITA":
            print(f"{s['escenario']:6s} {s['codigo']:16s} {s['estado']:30s} dif {s['dif_max']} "
                  f"{s['sustituida_por']} {s['faltan']}")
    n_ok = sum(s["estado"].startswith("ESCRITA") for s in salida)
    print(f"{n_ok} de {len(salida)} filas escritas en los datafiles de {', '.join(ESCENARIOS)}")
    falla |= identidad_gases()
    falla |= factor_por_iar()
    falla |= combustible_ben()
    return 1 if falla else 0


TERMICAS = ("PPFOI", "PPDFOI", "PPDSL", "PPRDSL", "PPDDSL", "PPNGS", "PPRNGS", "PPCRU")
OTRAS = ("PPILPG", "PPIBIM", "PPBIM", "PPBGS")
COMB = {"PPFOI": "E1FO1", "PPDFOI": "E1FO1", "PPDSL": "E1DSL", "PPRDSL": "E1DSL", "PPDDSL": "E1DSL",
        "PPNGS": "E1NGS", "PPRNGS": "E1NGS", "PPCRU": "E1CRU"}
# IPCC 2006, vol. 2, cap. 2, cuadro 2.2, con PCG AR5 (CH4 28, N2O 265), t CO2-eq/TJ
FACTOR = {"E1FO1": 77.4 + 28 * 3e-3 + 265 * 0.6e-3, "E1DSL": 74.1 + 28 * 3e-3 + 265 * 0.6e-3,
          "E1NGS": 56.1 + 28 * 1e-3 + 265 * 0.1e-3, "E1CRU": 73.3 + 28 * 3e-3 + 265 * 0.6e-3}


def factor_por_iar():
    """K08 y K13: en las ocho térmicas fósiles, 2011-2035, el EAR de CO2e_PP del datafile es factor IPCC x IAR del mismo
    datafile / 1000 (el factor sigue al rendimiento que el modelo usa)."""
    falla = False
    for esc in ESCENARIOS:
        datos = leer_datafile(ENERGIA / "Executables" / f"{esc}_0" / f"{esc}_0.txt")
        dmax = 0.0
        for t in TERMICAS:
            for y in range(2011, 2036):
                ear = datos[("EmissionActivityRatio", t, "CO2e_PP", "1", str(y))][0]
                iar = datos[("InputActivityRatio", t, COMB[t], "1", str(y))][0]
                dmax = max(dmax, abs(ear - FACTOR[COMB[t]] * iar / 1000) / ear)
        falla |= dmax > 1e-9
        print(f"{esc}: CO2e_PP = factor IPCC x IAR del datafile en las térmicas fósiles 2011-2035, diferencia relativa "
              f"máxima {dmax:.1e} ({'cumple' if dmax <= 1e-9 else 'NO cumple'})")
    return falla


def combustible_ben(tol=0.021):
    """K13: combustible por tipo del modelo (UseByTechnology de las térmicas; actividad de PPILPG para el GLP) frente al
    BEN 2025, tabla 2.28, en 2015-2025. La banda de actividad 0,98-1,02 lo deja dentro de ±2 %."""
    import pandas as pd
    b = pd.read_csv(AQUI / "ben2025_tabla_2_28.csv", index_col="anio")
    pj = 3.6 / 0.6196 / 1000
    ben = {"E1CRU": b.petroleo * pj, "E1NGS": b.gas_natural * pj, "E1DSL": b.diesel_oil * pj,
           "E1FO1": (b.fuel_oil + b.crudo_reducido) * pj, "GLP": b.gas_licuado * pj}
    falla = False
    for esc in ESCENARIOS:
        if not (ENERGIA / "Executables" / f"{esc}_0" / f"{esc}_0_Output.csv").exists():
            # B1 no escribe la salida de una corrida sin solución factible (K15b: hallazgo de suficiencia; la resuelve
            # variante_suficiencia.py); el datafile sí se verifica arriba
            print(f"{esc}: sin _Output.csv (la corrida de B1 no tuvo solución factible); combustible frente al BEN 2.28 no "
                  "comprobado en este escenario")
            continue
        o = pd.read_csv(ENERGIA / "Executables" / f"{esc}_0" / f"{esc}_0_Output.csv",
                        usecols=["Technology", "Fuel", "Year", "UseByTechnology", "TotalTechnologyAnnualActivity"],
                        low_memory=False)
        u = o[o.Technology.isin(TERMICAS)].dropna(subset=["UseByTechnology"]).groupby(["Fuel", "Year"]) \
            .UseByTechnology.sum()
        glp = o[o.Technology == "PPILPG"].groupby("Year").TotalTechnologyAnnualActivity.max()
        peor = (0.0, None)
        for f, serie in ben.items():
            for y in range(2015, 2026):
                m = float(glp.get(y, 0.0)) if f == "GLP" else float(u.get((f, y), 0.0))
                d = (m - float(serie[y])) / float(serie[y])
                if abs(d) > abs(peor[0]):
                    peor = (d, f"{f} {y}")
        falla |= abs(peor[0]) > tol
        print(f"{esc}: combustible por tipo frente al BEN 2.28 en 2015-2025, desvío máximo {peor[0] * 100:+.2f} % "
              f"({peor[1]}) ({'cumple' if abs(peor[0]) <= tol else 'NO cumple'} ±{tol * 100:.1f} %)")
    return falla


def identidad_gases():
    """K08g: en las ocho térmicas fósiles, 2011-2035, CO2e_PP = CO2_PP + 28 CH4_PP + 265 N2O_PP (PCG AR5).
    Informa la brecha que el CLG ya tiene en PPILPG, PPIBIM, PPBIM y PPBGS (no se corrige)."""
    falla = False
    for esc in ESCENARIOS:
        datos = leer_datafile(ENERGIA / "Executables" / f"{esc}_0" / f"{esc}_0.txt")

        def g(t, e, y):
            return datos.get(("EmissionActivityRatio", t, e, "1", str(y)), (0.0, 0))[0]
        dmax = max(abs(g(t, "CO2e_PP", y) - g(t, "CO2_PP", y) - 28 * g(t, "CH4_PP", y) - 265 * g(t, "N2O_PP", y))
                   for t in TERMICAS for y in range(2011, 2036))
        falla |= dmax > 1e-9
        print(f"{esc}: CO2e_PP - (CO2_PP + 28 CH4_PP + 265 N2O_PP) en las térmicas fósiles 2011-2035, máximo "
              f"{dmax:.1e} Mt/PJ ({'cumple' if dmax <= 1e-9 else 'NO cumple'})")
        for t in OTRAS:
            e, c, m, n = (g(t, x, 2035) for x in ("CO2e_PP", "CO2_PP", "CH4_PP", "N2O_PP"))
            print(f"  {t} (brecha del CLG, se conserva): CO2e {e:.6g}; CO2 {c:.6g}; 28 CH4 + 265 N2O "
                  f"{28 * m + 265 * n:.6g} Mt/PJ")
    return falla


if __name__ == "__main__":
    sys.exit(main())
