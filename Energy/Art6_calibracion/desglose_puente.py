# -*- coding: utf-8 -*-
"""Desglose del puente CO2e_PP CONA6 - NDCCON por grupo de correcciones, con corridas contrafactuales de glpsol.

Uso, desde ECU_NDC/Energy, después de correr B1 (glpsol en el PATH; unos 2 minutos y 4,5 GB de RAM por corrida):
    python Art6_calibracion/desglose_puente.py --trabajo <carpeta fuera del repositorio>

Para cada grupo G (K08; K13a, rendimientos, con K13g; historia_K15, que reúne el anclaje 2015-2025 de la hidro, la
térmica y las importaciones, K01, K02, K09 y K13b-K13f, con K15: K15a, CF 2026-2035 de PPFOI y PPDSL; K15b, tope de
potencia de las térmicas de la red; K15c, potencia de las térmicas 2023-2035 con los arriendos vigentes; K15d y K15e,
techo y CF de PPNGS con la oferta observada y la energía declarada a gas; K11; K12; biomasa; biogás; otras: K03 y K07;
K14, actividad 2026-2035 de los autoproductores y PPILPG anclada a lo observado; K16, piso de PPFOI 2026-2035 igual al
mínimo observado 2015-2025, desde el 13-10-2026) arma el datafile «CONA6 sin G»: el
de CONA6 con los vectores que tocan las filas de G en correcciones_K.csv devueltos a su valor en el datafile de NDCCON,
escenario del Modelo Climate Lead Group (CLG), o retirados si NDCCON no los tiene. K15 va con la historia porque el tope
K15b supone el parque observado de 2025: con la historia CLG el contrafactual no tiene solución. K15 solo (con la
historia observada) se resuelve aparte y se informa como «de ello», fuera de la suma. G01 (sensibilidad de gas) no es
de CONA6 y no entra. Lo resuelve con glpsol y OSeMOSYS_Model.txt, sin pasar por B1, y lee el CO2e_PP de
SelectedResults.csv. El aporte de G es CO2e_PP(CONA6) - CO2e_PP(CONA6 sin G); la interacción es el puente menos la suma
de los aportes. Antes comprueba que «CONA6 sin todas las correcciones» es línea a línea el datafile de NDCCON.
K08 cambia solo EmissionActivityRatio, que no entra en el objetivo (no hay penalidad de emisiones), así que su aporte se
reparte de forma contable con la actividad de CONA6: factor IPCC (f x IAR CLG - EAR CLG) y rendimiento observado
(f x (IAR de CONA6 - IAR CLG)); K13a (rendimiento) actúa por el costo del combustible en el despacho. La hidro y la
térmica 2015-2025 van juntas en «historia» porque anclan el mismo balance: con la hidro CLG y la térmica observada
el contrafactual no tiene solución factible (la térmica CLG era 28 % a 42 % mayor que la del BEN y la hidro, menor).
La interacción incluye el término cruzado actividad x factor de las térmicas (columna termino_cruzado_actividad_x_factor):
K08 se mide con la actividad de CONA6 y los grupos que mueven el despacho con los factores de CONA6, de modo que la suma de
aportes cuenta ese producto dos veces y la interacción lo devuelve.

Lectura principal (versión K15, 12-10-2026), secuencial y sin partida de cierre:
    puente = K08 con la actividad CLG [sum act_NDCCON x (EAR_CONA6 - EAR_NDCCON)]
           + aporte de cada grupo de actividad con los factores corregidos [CO2e(CONA6) - CO2e(CONA6 sin G)]
           + resto no lineal [efecto conjunto de la actividad, sum (act_CONA6 - act_NDCCON) x EAR_CONA6, menos la suma
             de los aportes: interacción de los grupos dentro del LP]
La identidad es exacta: la suma de las tres partes es el puente. Aparte, el término cruzado actividad x factor
[sum (act_CONA6 - act_NDCCON) x (EAR_CONA6 - EAR_NDCCON)] y K08 con la actividad de CONA6 (lectura simétrica), que ya no
se suman a la lectura principal. Con --reusar no vuelve a resolver un grupo cuyo
datafile no cambió. Escribe Art6_calibracion/calibracion_e_desglose_puente.csv y desglose_puente.json (md5 de insumos y estado de cada
corrida). Los escenarios CLG y el libro no se tocan.
"""
import argparse
import csv
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

import pandas as pd

ENERGIA = Path(__file__).resolve().parents[1]
AQUI = Path(__file__).resolve().parent
EX = ENERGIA / "Executables"
GRUPOS = {
    "K08": lambda c: c.startswith("K08"),
    "K13a": lambda c: c.startswith(("K13a", "K13g")),
    # historia (anclaje 2015-2025) con K15 (CF continuo, tope y potencia del parque observado): el tope K15b supone el
    # parque observado de 2025 y es incompatible con la historia CLG, que construye 2,93 GW de PPFOI hasta 2025 con su CF
    # de relleno (el contrafactual «sin historia» con K15 no tiene solución factible:
    # tests/logs/paso8_desglose_intento1_historia_sin_K15_infactible_2026-10-12.log); K15 solo va aparte, informativo
    "historia_K15": lambda c: c.startswith(("K01", "K02", "K09", "K13b", "K13c", "K13d", "K13e", "K13f", "K15")),
    "K11": lambda c: c.startswith("K11"),
    "K12": lambda c: c.startswith("K12"),
    "biomasa": lambda c: c.startswith(("K04", "K05")),
    "biogas": lambda c: c.startswith("K06"),
    "otras": lambda c: c.startswith(("K03", "K07")),
    "K14": lambda c: c.startswith("K14"),
    # K16 (13-10-2026): piso de despacho de PPFOI 2026-2035 = mínimo observado 2015-2025. En CONA6 va como vector
    # completo en Electrical (K16-PPFOI-CON) cuyos años 2010-2025 repiten A2 y K13b: el grupo solo revierte 2026-2035
    # (ANIOS_DEL_GRUPO), que es lo que K16 corrige
    "K16": lambda c: c.startswith("K16"),
}
# años que revierte cada grupo cuando la fila trae el vector completo pero corrige solo una parte
ANIOS_DEL_GRUPO = {"K16": set(range(2026, 2036))}
GRUPOS_ACTIVIDAD = [g for g in GRUPOS if g != "K08"]
# grupos informativos: se resuelven, pero no entran en la suma (se solapan con un grupo de la suma). K15_gas son el techo
# y el CF de PPNGS con la oferta observada y la energía declarada (K15d-e, arreglo de la verificación del 12-10-2026):
# sin ellos y con los arriendos vencidos el contrafactual puede no tener solución, y eso se informa como hallazgo de
# suficiencia, no como error
INFORMATIVOS = {"K15": lambda c: c.startswith("K15"), "K15_gas": lambda c: c.startswith(("K15d", "K15e"))}
Y = list(range(2026, 2036))


def md5(ruta):
    return hashlib.md5(Path(ruta).read_bytes()).hexdigest()


class Datafile:
    """Datafile de B1 como líneas, con la ubicación de cada vector (parámetro, tecnología, índice2)."""

    def __init__(self, ruta):
        self.lineas = Path(ruta).read_text(encoding="utf-8").split("\n")
        self.indexar()

    def indexar(self):
        self.tabla, self.bloque, self.dos, self.anios = {}, {}, {}, {}
        par, forma, cab, anios_tabla = None, None, None, None
        i, n = 0, len(self.lineas)
        while i < n:
            ln = self.lineas[i]
            m = re.match(r"^param\s+(\w+)\s+default\s+\S+\s*(:=|:)\s*$", ln)
            if m:
                par, forma = m.group(1), m.group(2)
                if forma == ":":
                    cols = self.lineas[i + 1].replace(":=", "").split()
                    self.dos[par] = (i + 1, i + 2, cols)
                    i += 3
                    continue
                i += 1
                continue
            if par is None or ln.strip() == ";":
                par = None if ln.strip() == ";" else par
                i += 1
                continue
            s = ln.strip()
            if s.startswith("["):
                fijos = s.rstrip(":").strip("[]").split(",")[1:]
                if fijos.count("*") == len(fijos):       # tabla: filas «TEC valores»
                    cab = "tabla"
                    anios_tabla = self.lineas[i + 1].replace(":=", "").split()
                    i += 2
                    continue
                idx = [f for f in fijos if f != "*"]       # bloque de una tecnología: cabecera, años y valores
                cab = "bloque"
                clave = (par, idx[0], idx[1] if len(idx) > 1 else None)
                self.bloque[clave] = (i, i + 2)
                self.anios[clave] = self.lineas[i + 1].replace(":=", "").split()
                i += 3
                continue
            if cab == "tabla" and s:
                self.tabla[(par, s.split()[0], None)] = i
                self.anios[(par, s.split()[0], None)] = anios_tabla
            i += 1

    def vector(self, clave):
        """Texto que representa el vector (para copiarlo de otro datafile) o None."""
        par, tec, idx2 = clave
        if clave in self.tabla:
            return ("tabla", self.lineas[self.tabla[clave]])
        if clave in self.bloque:
            a, b = self.bloque[clave]
            return ("bloque", self.lineas[a:b + 1])
        if par in self.dos:
            h, v, cols = self.dos[par]
            if tec in cols:
                return ("dos", self.lineas[v].split()[1 + cols.index(tec)])
        return None


def cola(texto):
    return texto[len(texto.rstrip()):]


def mezclar(linea_base, linea_ref, anios_base, anios_ref, anios):
    """Fila «etiqueta v1 v2 ...» de base con los valores de ref en los años pedidos (todos si anios es None)."""
    if anios_base != anios_ref:
        raise SystemExit("cabeceras de años distintas entre CONA6 y NDCCON")
    vb, vr = linea_base.split(), linea_ref.split()
    if vb[0] != vr[0] or len(vb) != len(vr):
        raise SystemExit(f"filas no comparables: {vb[0]} / {vr[0]}")
    for k, a in enumerate(anios_base):
        if anios is None or int(a) in anios:
            vb[1 + k] = vr[1 + k]
    return " ".join(vb) + cola(linea_base)


def revertir(base, ref, claves):
    """Copia de base con los años de cada vector de claves tomados de ref (o el vector retirado si ref no lo tiene).

    claves: {(parámetro, tecnología, índice2): años o None}; None es el vector completo. Se revierten solo los años de
    las filas del grupo, así dos grupos que corrigen años distintos del mismo vector (K13b-d en 2015-2025 y K14 en
    2026-2035) no se pisan."""
    lineas = list(base.lineas)
    borrar = set()
    for clave, anios in claves.items():
        par, tec, idx2 = clave
        de_ref = ref.vector(clave)
        completo = anios is None or (clave in base.anios and {int(a) for a in base.anios[clave]} <= set(anios))
        if clave in base.tabla:
            i = base.tabla[clave]
            if de_ref is None:
                if not completo:
                    raise SystemExit(f"{clave}: NDCCON no tiene el vector y el grupo corrige solo algunos años")
                borrar.add(i)
            else:
                lineas[i] = mezclar(lineas[i], de_ref[1], base.anios[clave], ref.anios[clave], anios)
        elif clave in base.bloque:
            a, b = base.bloque[clave]
            if de_ref is None:
                if not completo:
                    raise SystemExit(f"{clave}: NDCCON no tiene el vector y el grupo corrige solo algunos años")
                borrar.update(range(a, b + 1))
            elif b - a != 2 or len(de_ref[1]) != 3:
                raise SystemExit(f"{clave}: bloque con más de una fila de valores")
            else:
                lineas[b] = mezclar(lineas[b], de_ref[1][2], base.anios[clave], ref.anios[clave], anios)
        elif par in base.dos and tec in base.dos[par][2]:
            h, v, cols = base.dos[par]
            j = cols.index(tec)
            valores = lineas[v].split()
            if de_ref is None:
                cabecera = lineas[h].split()
                cabecera.remove(tec)
                del valores[1 + j]
                lineas[h] = " ".join(cabecera) + cola(lineas[h])
            else:
                valores[1 + j] = de_ref[1]
            lineas[v] = " ".join(valores) + cola(lineas[v])
        else:
            raise SystemExit(f"{clave}: no está en el datafile de CONA6")
    return "\n".join(l for k, l in enumerate(lineas) if k not in borrar)


def claves_de(filas, grupo):
    """{(parámetro, tecnología, índice2): años que corrigen las filas del grupo en CONA6, o None si es sin año}."""
    from verificar_correcciones import anios_de  # noqa: E402
    out = {}
    for f in filas:
        if "CONA6" not in [e.strip() for e in f["escenarios"].split(";")] or                 not {**GRUPOS, **INFORMATIVOS}[grupo](f["codigo"]):
            continue
        partes = [p.strip() for p in f["tecnologia"].split(";")]
        clave = (f["parametro"], partes[0], partes[1] if len(partes) > 1 else None)
        anios = anios_de(f["anios"])
        if grupo in ANIOS_DEL_GRUPO and anios != [None]:
            anios = sorted(set(anios) & ANIOS_DEL_GRUPO[grupo])
        if anios == [None] or (clave in out and out[clave] is None):
            out[clave] = None
        else:
            out[clave] = out.get(clave, set()) | set(anios)
    return out


def unir(*dicts):
    out = {}
    for d in dicts:
        for k, v in d.items():
            out[k] = None if v is None or (k in out and out[k] is None) else out.get(k, set()) | v
    return out


def co2e_selected(ruta):
    """CO2e_PP por año (kt) de la sección Annual Emissions by Technology de SelectedResults.csv."""
    lineas = Path(ruta).read_text(encoding="utf-8", errors="replace").split("\n")
    i = next(k for k, l in enumerate(lineas) if l.startswith("Annual Emissions by Technology"))
    anios = None
    tot = {}
    for l in lineas[i + 1:]:
        p = l.strip().split(",")
        if p[0] == "Technology":
            anios = [int(x) for x in p[2:] if x]
            continue
        if anios and len(p) >= 2 + len(anios) and p[1] == "CO2e_PP":
            for a, v in zip(anios, p[2:]):
                tot[a] = tot.get(a, 0.0) + float(v) * 1000
    return tot


def co2e_output(esc):
    o = pd.read_csv(EX / f"{esc}_0" / f"{esc}_0_Output.csv", usecols=["Emission", "Year", "AnnualTechnologyEmission"],
                    low_memory=False)
    return (o[o.Emission == "CO2e_PP"].groupby("Year").AnnualTechnologyEmission.sum() * 1000).to_dict()


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--trabajo", type=Path, required=True, help="carpeta de trabajo fuera del repositorio")
    p.add_argument("--solo-comprobar", action="store_true", help="arma los datafiles y no resuelve")
    p.add_argument("--reusar", action="store_true",
                   help="no vuelve a resolver un grupo si su datafile es idéntico al que ya está en la carpeta de trabajo "
                        "y existe su SelectedResults_sin_<grupo>.csv")
    a = p.parse_args()
    trabajo = a.trabajo.resolve()
    if ENERGIA.parent in trabajo.parents or trabajo == ENERGIA.parent:
        raise SystemExit("la carpeta de trabajo debe estar fuera del repositorio")
    trabajo.mkdir(parents=True, exist_ok=True)
    filas = list(csv.DictReader((AQUI / "correcciones_K.csv").open(encoding="utf-8-sig")))
    r_c, r_o = EX / "CONA6_0" / "CONA6_0.txt", EX / "NDCCON_0" / "NDCCON_0.txt"
    base, ref = Datafile(r_c), Datafile(r_o)
    sys.path.insert(0, str(AQUI))
    todas = unir(*(claves_de(filas, g) for g in GRUPOS))
    for g1 in GRUPOS:  # dos grupos no pueden corregir el mismo año del mismo vector
        for g2 in GRUPOS:
            if g1 < g2:
                c1, c2 = claves_de(filas, g1), claves_de(filas, g2)
                for k in set(c1) & set(c2):
                    if c1[k] is None or c2[k] is None or c1[k] & c2[k]:
                        raise SystemExit(f"{k}: los grupos {g1} y {g2} corrigen los mismos años")
    sin_nada = revertir(base, ref, todas)
    ok = sorted(sin_nada.replace("\r", "").split("\n")) == sorted(r_o.read_text(encoding="utf-8").split("\n"))
    print("CONA6 sin todas las correcciones = NDCCON línea a línea (ordenadas):", ok)
    if not ok:
        raise SystemExit("las correcciones no explican todas las diferencias entre CONA6 y NDCCON")
    shutil.copy2(ENERGIA / "OSeMOSYS_Model.txt", trabajo / "OSeMOSYS_Model.txt")
    estado = {"insumos": {"CONA6_0.txt": md5(r_c), "NDCCON_0.txt": md5(r_o),
                          "correcciones_K.csv": md5(AQUI / "correcciones_K.csv"),
                          "OSeMOSYS_Model.txt": md5(ENERGIA / "OSeMOSYS_Model.txt"),
                          "CONA6_Output": md5(EX / "CONA6_0" / "CONA6_0_Output.csv"),
                          "NDCCON_Output": md5(EX / "NDCCON_0" / "NDCCON_0_Output.csv")},
              "corridas": {}}
    res = {"CONA6": co2e_output("CONA6"), "NDCCON": co2e_output("NDCCON")}
    for g in list(GRUPOS) + list(INFORMATIVOS):
        datos = trabajo / f"CONA6_sin_{g}.txt"
        texto_df = revertir(base, ref, claves_de(filas, g))
        previo = trabajo / f"SelectedResults_sin_{g}.csv"
        igual = datos.exists() and datos.read_text(encoding="utf-8") == texto_df and previo.exists()
        datos.write_text(texto_df, encoding="utf-8")
        estado["corridas"][g] = {"datafile_md5": md5(datos), "vectores_revertidos": len(claves_de(filas, g))}
        if a.solo_comprobar:
            continue
        if a.reusar and igual and previo.exists():
            res[f"sin_{g}"] = co2e_selected(previo)
            estado["corridas"][g].update({"reusada": True})
            print(f"{g}: datafile idéntico al de la corrida anterior; se reusa {previo.name}")
            continue
        sel = trabajo / "SelectedResults.csv"
        if sel.exists():
            sel.unlink()
        log = trabajo / f"glpsol_sin_{g}.log"
        with log.open("w", encoding="utf-8") as h:
            rc = subprocess.run(["glpsol", "-m", "OSeMOSYS_Model.txt", "-d", datos.name], cwd=trabajo, stdout=h,
                                stderr=subprocess.STDOUT, env=os.environ).returncode
        texto = log.read_text(encoding="utf-8", errors="replace")
        optimo = "OPTIMAL LP SOLUTION FOUND" in texto
        estado["corridas"][g].update({"rc": rc, "optimo": optimo})
        print(f"{g}: rc {rc}, óptimo {optimo}")
        if not optimo and g in INFORMATIVOS:
            estado["corridas"][g]["estado"] = ("sin solución factible: " +
                                               ("PROBLEM HAS NO PRIMAL FEASIBLE SOLUTION" if "NO PRIMAL FEASIBLE" in texto
                                                else "ver el registro"))
            res[f"sin_{g}"] = None
            continue
        if not optimo:
            raise SystemExit(f"{g}: la corrida no es óptima; ver {log}")
        res[f"sin_{g}"] = co2e_selected(sel)
        shutil.copy2(sel, trabajo / f"SelectedResults_sin_{g}.csv")
    if a.solo_comprobar:
        print(json.dumps(estado, indent=1))
        return 0
    sys.path.insert(0, str(AQUI))
    from verificar_correcciones import leer_datafile, FACTOR, COMB  # noqa: E402
    d_c, d_o = leer_datafile(r_c), leer_datafile(r_o)

    def actividad(esc):
        o = pd.read_csv(EX / f"{esc}_0" / f"{esc}_0_Output.csv",
                        usecols=["Technology", "Year", "TotalTechnologyAnnualActivity"], low_memory=False)
        return o.groupby(["Technology", "Year"]).TotalTechnologyAnnualActivity.max().fillna(0).to_dict()
    act, act_n = actividad("CONA6"), actividad("NDCCON")
    ears = {}
    for k, (v, _) in d_c.items():
        if k[0] == "EmissionActivityRatio" and k[2] == "CO2e_PP" and k[3] == "1":
            ears[(k[1], int(k[4]))] = [v, 0.0]
    for k, (v, _) in d_o.items():
        if k[0] == "EmissionActivityRatio" and k[2] == "CO2e_PP" and k[3] == "1":
            ears.setdefault((k[1], int(k[4])), [0.0, 0.0])[1] = v
    filas_e = []
    for y in Y:
        puente = res["CONA6"][y] - res["NDCCON"][y]
        k08_clg = k08_c = cruz = efecto_act = 0.0
        for (t, yy), (e_c, e_o) in ears.items():
            if yy != y:
                continue
            a_c, a_o = act.get((t, y), 0.0), act_n.get((t, y), 0.0)
            k08_clg += a_o * (e_c - e_o) * 1000
            k08_c += a_c * (e_c - e_o) * 1000
            cruz += (a_c - a_o) * (e_c - e_o) * 1000
            efecto_act += (a_c - a_o) * e_c * 1000
        fila = {"anio": y, "tramo": "2026-2028" if y <= 2028 else "2029-2035",
                "NDCCON_kt": round(res["NDCCON"][y], 2), "CONA6_kt": round(res["CONA6"][y], 2),
                "puente_kt": round(puente, 2), "K08_con_actividad_CLG_kt": round(k08_clg, 2)}
        fac = ren = 0.0
        for t, c in COMB.items():
            a_o = act_n.get((t, y), 0.0)
            i_c = d_c[("InputActivityRatio", t, c, "1", str(y))][0]
            i_o = d_o[("InputActivityRatio", t, c, "1", str(y))][0]
            e_o = d_o[("EmissionActivityRatio", t, "CO2e_PP", "1", str(y))][0]
            fac += a_o * (FACTOR[c] * i_o / 1000 - e_o) * 1000
            ren += a_o * FACTOR[c] * (i_c - i_o)
        fila["K08_de_ello_factor_IPCC_kt"] = round(fac, 2)
        fila["K08_de_ello_rendimiento_observado_kt"] = round(ren, 2)
        suma = 0.0
        for g in GRUPOS_ACTIVIDAD:
            ap = res["CONA6"][y] - res[f"sin_{g}"][y]
            fila[f"aporte_{g}_kt"] = round(ap, 2)
            suma += ap
        for g in INFORMATIVOS:
            fila[f"de_ello_{g}_solo_kt"] = (round(res["CONA6"][y] - res[f"sin_{g}"][y], 2)
                                            if res.get(f"sin_{g}") is not None else None)
        fila["efecto_conjunto_actividad_kt"] = round(efecto_act, 2)
        fila["resto_no_lineal_kt"] = round(efecto_act - suma, 2)
        fila["control_suma_menos_puente_kt"] = round(k08_clg + efecto_act - puente, 4)
        # aparte: lectura simétrica y término cruzado (no se suman a la lectura principal)
        fila["aparte_K08_con_actividad_CONA6_kt"] = round(k08_c, 2)
        fila["aparte_K08_glpsol_kt"] = round(res["CONA6"][y] - res["sin_K08"][y], 2)
        fila["aparte_termino_cruzado_actividad_x_factor_kt"] = round(cruz, 2)
        filas_e.append(fila)
        if abs(fila["control_suma_menos_puente_kt"]) > 0.5:
            raise SystemExit(f"{y}: la lectura secuencial no reproduce el puente ({fila['control_suma_menos_puente_kt']})")
    df = pd.DataFrame(filas_e)
    sumas = []
    for nombre, ys in (("2026-2028", [2026, 2027, 2028]), ("2031-2035", list(range(2031, 2036))), ("2026-2035", Y)):
        tot = df[df.anio.isin(ys)].drop(columns=["anio", "tramo"]).sum().round(2)
        tot["anio"], tot["tramo"] = nombre, "suma"
        sumas.append(tot.to_frame().T)
    df = pd.concat([df] + sumas, ignore_index=True)
    df.to_csv(AQUI / "calibracion_e_desglose_puente.csv", index=False)
    estado["resultado"] = {r["anio"]: r for r in df.to_dict("records")}
    (AQUI / "desglose_puente.json").write_text(json.dumps(estado, indent=1, ensure_ascii=False, default=str) + "\n",
                                               encoding="utf-8")
    pd.set_option("display.width", 250)
    print(df.to_string(index=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
