# -*- coding: utf-8 -*-
"""Rutas del motor de Articulo 6 del sandbox PNUD (copia de ECU_NDC, rama art6-escenarios), lectura de los datafiles que genera B1 y de
las salidas por escenario (Executables/<ESC>_0/<ESC>_0_Output.csv e _Input.csv).

Todo el motor importa de aqui. Los datafiles los escribe solo B1, desde B1_Scenario_Config.xlsx; el motor los lee
para verificarlos y para el analisis. En ECU_NDC el motor no usa ECUOutput.csv ni ECUInput.csv: son archivos del
Modelo Climate Lead Group versionados en git, y B2 los reescribiria. Lee cada escenario de su carpeta de
Executables y comprueba antes que su salida sea de la ultima corrida (estado_solucion).
"""
import csv
import hashlib
import io
import re
import shutil
from pathlib import Path

ENERGY = Path(__file__).resolve().parent.parent          # .../Energy
RAIZ = ENERGY.parent                                      # raíz del repositorio
CONFIG = ENERGY / "B1_Scenario_Config.xlsx"     # libro de B1: escenarios y filas que B1 aplica
# sandbox PNUD: un solo libro de configuración. Las hojas documentales Art6_* van en B1_Scenario_Config.xlsx, al final;
# B1 solo lee sus hojas por nombre (Scenarios, Electrical, SmartGrid, Efficiency...) y no las usa.
ART6_CONFIG = CONFIG
MODELO = ENERGY / "OSeMOSYS_Model.txt"
INSUMOS = ENERGY / "Insumos_Art6"
PROCEDENCIA = INSUMOS / "PROCEDENCIA.csv"
# copias sin cambios de PowerBI/Nacionales y PowerBI/Energy del Modelo CLG (clg-admin/ECU_NDC)
NACIONAL = INSUMOS / "Emisiones Totales.xlsx"          # agregacion nacional de los cinco sectores
ENERGIA_CLG = INSUMOS / "ECUOutput_Energy.csv"         # salida de energia del Modelo CLG por escenario
EXEC = ENERGY / "Executables"                           # <ESC>_0/<ESC>_0.txt, como la cadena del modelo
RESULTADOS = ENERGY / "B2_Output_Art6"
TABLAS = RESULTADOS / "tablas"
GRAFICAS = RESULTADOS / "graficas"
DOCS = RAIZ / "docs"                                    # documentacion del repositorio (Sphinx y version para GitHub)


def carpeta(cod):
    return EXEC / (cod + "_0")


def datafile(cod):
    return carpeta(cod) / (cod + "_0.txt")

ANIOS = list(range(2010, 2036))
IDX = {a: i for i, a in enumerate(ANIOS)}
VENTANA = list(range(2031, 2036))          # transacciones desde 2031
MARCO = list(range(2026, 2036))            # marco de referencia del análisis: vigencia de la Segunda NDC
COMP_ENERGIA = ("CO2e_DE", "CO2e_PP", "CO2e_FUG", "CO2e_REF")
PJ_A_GWH = 1.0 / 0.0036
PISO = "TotalTechnologyAnnualActivityLowerLimit"
TECHO = "TotalTechnologyAnnualActivityUpperLimit"
FP = "CapacityFactor"

# Familias de generacion. PPHD y PPIHD no tienen insumo y producen E3ELE: son generacion
# distribuida real y entran en la hidro. PPIBIM no tiene combustible de salida (solo contabiliza
# emisiones de autogeneracion en ingenios), asi que no suma generacion aunque tenga actividad.
FAMILIAS = [   # orden de apilado; los colores siguen ese orden y pasan la validacion de daltonismo
    ("Hidroeléctrica", ("PPHDAM", "PPHROR", "PPIHD", "PPHD"), "hidro"),
    ("Gas natural", ("PPNGS", "PPRNGS"), "termica"),
    ("Eólica", ("PPWND",), "ernc"),
    ("Solar", ("PPPV",), "ernc"),
    ("Crudo, GLP e importación", ("PPCRU", "PPILPG", "IMPELE"), "termica"),
    ("Biomasa y biogás", ("PPBIM", "PPBGS", "PPIBIM"), "ernc"),
    ("Geotermia", ("PPGEO",), "ernc"),
    ("Fuel oil y diésel", ("PPFOI", "PPDFOI", "PPDSL", "PPDDSL", "PPRDSL"), "termica"),
]
COLORES_FAMILIA = {
    "Hidroeléctrica": "#2a78d6", "Gas natural": "#eb6834", "Eólica": "#1baf7a", "Solar": "#eda100",
    "Crudo, GLP e importación": "#e87ba4", "Biomasa y biogás": "#008300", "Geotermia": "#4a3aa7",
    "Fuel oil y diésel": "#e34948",
}


def familia(tec):
    for nombre, prefijos, _ in FAMILIAS:
        if tec.startswith(prefijos):
            return nombre
    return None


def tipo_familia(nombre):
    return next(t for n, _, t in FAMILIAS if n == nombre)


SUBSECTORES = ["Generación eléctrica", "Transporte", "Industria", "Residencial",
               "Comercial y público", "Agro, construcción y otros", "Refinación",
               "Fugitivas de petróleo y gas"]
_TRANSPORTE = ("TRO", "TRN", "TMA", "TAE", "TCA", "Rail", "NOMOT", "TRXTRA")


def subsector(tec, comp):
    """Subsector del inventario para una tecnologia y un componente de emision CO2e."""
    if comp == "CO2e_PP":
        return "Generación eléctrica"
    if comp == "CO2e_REF":
        return "Refinación"
    if comp == "CO2e_FUG":
        return "Fugitivas de petróleo y gas"
    if tec.startswith("T4") or any(s in tec for s in _TRANSPORTE):
        return "Transporte"
    if tec.endswith("IND") or tec.startswith("T5IND"):
        return "Industria"
    if tec.endswith("RES"):
        return "Residencial"
    if tec.endswith(("COM", "PUB")):
        return "Comercial y público"
    return "Agro, construcción y otros"


# ----------------------------------------------------------------------------- utilidades

def enumerar(xs):
    """Enumeracion en espanol: «a», «a y b», «a, b y c»; «e» ante palabra que empieza por i o hi."""
    xs = [str(x) for x in xs if x]
    if len(xs) < 2:
        return "".join(xs)
    ult = re.sub(r"<[^>]+>", "", xs[-1]).strip()
    return ", ".join(xs[:-1]) + (" e " if re.match(r"(?i)h?i(?!e)", ult) else " y ") + xs[-1]


def tramos(anios):
    """«2026-2027», «2029», «2026-2027 y 2029»: anios agrupados en tramos consecutivos."""
    xs = sorted({int(a) for a in anios})
    if not xs:
        return ""
    grupos, ini, prev = [], xs[0], xs[0]
    for a in xs[1:] + [None]:
        if a is not None and a == prev + 1:
            prev = a
            continue
        grupos.append(str(ini) if ini == prev else "%d-%d" % (ini, prev))
        if a is not None:
            ini = prev = a
    return enumerar(grupos)


def huella(*rutas):
    """Fecha de modificacion de cada archivo (0 si falta). Sirve de llave de cache: un resultado
    guardado en memoria se recalcula en cuanto cambia cualquiera de sus archivos de origen."""
    return tuple(Path(p).stat().st_mtime_ns if Path(p).exists() else 0 for p in rutas)


def huella_datafile(ruta):
    """md5 del contenido de un datafile sin depender del orden de escritura. B1 recorre conjuntos de
    Python y escribe bloques y filas en un orden que cambia de una corrida a otra aunque el contenido
    sea el mismo; la huella ordena bloques y filas y descarta los cierres de bloque."""
    NL = chr(10)
    bloques, actual, param = [], [], ""

    def cerrar():
        if actual:
            bloques.append(actual[0] + NL + NL.join(sorted(actual[1:])))
    for linea in io.open(ruta, encoding="utf-8", errors="replace").read().splitlines():
        s = linea.strip()
        if not s or s == ";":
            continue
        if s.startswith("param ") or s.startswith("set "):
            param = s.split()[1]
        if s.startswith(("param ", "set ", "[")):
            cerrar()
            actual = [param + " " + s]
        else:
            actual.append(s)
    cerrar()
    return hashlib.md5(NL.join(sorted(bloques)).encode("utf-8")).hexdigest()


def huella_resultados(O, cod):
    """md5 de las filas de un escenario en la salida leida de Executables (leer_ecuoutput), ordenadas, sin depender
    del orden del archivo."""
    claves = [c for c in ("Strategy", "Future.ID", "Fuel", "Technology", "Emission", "Year") if c in O.columns]
    x = O[O["Strategy"].astype(str) == cod].sort_values(claves).reset_index(drop=True)
    return hashlib.md5(x.to_csv(index=False).encode("utf-8")).hexdigest()


def md5(ruta):
    h = hashlib.md5()
    with open(ruta, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def glpsol():
    """El glpsol incluido en Energy/glpk (GLPK 4.65), el de C:\\winglpk o, si faltan, el del PATH."""
    for p in (ENERGY / "glpk" / "glpsol.exe", Path(r"C:\winglpk\glpk\w64\glpsol.exe")):
        if p.exists():
            return str(p)
    w = shutil.which("glpsol")
    if w:
        return w
    raise SystemExit(r"No encuentro glpsol: debe estar en Energy\glpk, en C:\winglpk\glpk\w64 o en el PATH")


def procedencia():
    with io.open(PROCEDENCIA, encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


# ----------------------------------------------------------------------------- datafiles

def leer_datafile(ruta):
    return io.open(ruta, encoding="utf-8", errors="replace", newline="").read().split("\n")


def filas(lineas):
    """(indice de linea, parametro, clave, valores 2010-2035) de cada fila anual del datafile.

    La clave conserva los indices que fija el contexto (sin la region) mas la clave de la fila:
    [ECU,*,*] fila PPGEO da "PPGEO"; [ECU,PPGEO,*,*] fila All da "PPGEO,All";
    [ECU,PPFOI,CO2e_PP,*,*] fila 1 da "PPFOI,CO2e_PP,1".
    """
    par = ctx = None
    for k, ln in enumerate(lineas):
        t = ln.strip()
        m = re.match(r"^param\s+(\w+)", t)
        if m:
            par, ctx = m.group(1), None
            continue
        if t == ";":
            par = None
            continue
        if par is None:
            continue
        m = re.match(r"^\[([^\]]*)\]:?$", t)
        if m:
            ctx = m.group(1)
            continue
        c = t.split()
        if not c or c[0] == "2010" or len(c) < 1 + len(ANIOS):
            continue
        try:
            v = [float(x) for x in c[1:1 + len(ANIOS)]]
        except ValueError:
            continue
        p = ctx.split(",") if ctx else []
        fijos = [x for x in p[1:] if x != "*"]
        yield k, par, (",".join(fijos + [c[0]]) if fijos else c[0]), v


def tabla(lineas):
    return {(p, cl): (k, v) for k, p, cl, v in filas(lineas)}


def diferencias(a, b, tol=1e-9):
    """Filas que difieren entre dos datafiles: [(parametro, clave, anios distintos)]."""
    A, B = tabla(a), tabla(b)
    out = []
    for key in sorted(set(A) | set(B)):
        if key not in A or key not in B:
            out.append((key[0], key[1], "solo en uno"))
            continue
        va, vb = A[key][1], B[key][1]
        dif = [ANIOS[i] for i in range(len(ANIOS))
               if abs(va[i] - vb[i]) > tol * max(1.0, abs(va[i]), abs(vb[i]))]
        if dif:
            out.append((key[0], key[1], dif))
    return out


# ----------------------------------------------------------------------------- resultados

_COLS_OUT = ["Strategy", "Fuel", "Technology", "Emission", "Year", "ProductionByTechnology", "TotalCapacityAnnual",
             "NewCapacity", "TotalTechnologyAnnualActivity", "AnnualTechnologyEmission", "AnnualEmissions",
             "TotalDiscountedCost"]


def salida(cod):
    return carpeta(cod) / (cod + "_0_Output.csv")


def entrada(cod):
    return carpeta(cod) / (cod + "_0_Input.csv")


def estado_solucion(cod):
    """Estado de la ultima corrida de B1 para el escenario:

    optimo          hay _Output.csv posterior al datafile (B1 solo lo escribe si glpsol termino y el posproceso leyo
                    la solucion) o el registro <ESC>_0_glpsol.log dice OPTIMAL LP SOLUTION FOUND;
    sin_solucion    quedo el archivo de glpsol <ESC>_0_output.txt sin estado optimo (B1 lo borra al terminar el
                    posproceso; si queda, el posproceso fallo: es la huella de PROBLEM HAS NO PRIMAL FEASIBLE
                    SOLUTION seguido de KeyError: 'AccumulatedNewCapacity');
    error_posproceso
                    quedo el archivo de glpsol con estado optimo y sin _Output.csv nuevo (B1 fallo o sigue corriendo);
    desactualizado  hay _Output.csv anterior al datafile (salida de una corrida previa);
    sin_salida      hay datafile y ni salida de glpsol ni _Output.csv;
    sin_corrida     no hay datafile.
    """
    df = datafile(cod)
    if not df.exists():
        return "sin_corrida"
    log = carpeta(cod) / ("%s_0_glpsol.log" % cod)
    if log.exists():
        texto = log.read_text(encoding="utf-8", errors="replace")
        return "optimo" if "OPTIMAL LP SOLUTION FOUND" in texto else "sin_solucion"
    crudo = carpeta(cod) / ("%s_0_output.txt" % cod)
    out = salida(cod)
    if crudo.exists() and (not out.exists() or crudo.stat().st_mtime >= out.stat().st_mtime):
        cab = crudo.read_text(encoding="utf-8", errors="replace")[:2000]
        m = re.search(r"Status:\s*(\S+)", cab)
        return "sin_solucion" if not m or m.group(1) != "OPTIMAL" else "error_posproceso"
    if out.exists():
        return "optimo" if out.stat().st_mtime >= df.stat().st_mtime else "desactualizado"
    return "sin_salida"


def origenes_resultados(escenarios):
    """Archivos de resultados de los escenarios (llave de cache del analisis)."""
    return [salida(c) for c in escenarios] + [entrada(c) for c in escenarios]


def leer_ecuoutput(escenarios):
    """Resultados de los escenarios con solucion optima, leidos de su carpeta de Executables (misma forma que
    ECUOutput.csv: columna Strategy con el nombre del escenario)."""
    import pandas as pd
    partes = []
    for cod in escenarios:
        if estado_solucion(cod) != "optimo":
            continue
        o = pd.read_csv(salida(cod), usecols=_COLS_OUT, low_memory=False)
        o["Strategy"] = cod
        partes.append(o)
    O = pd.concat(partes, ignore_index=True)
    O["Year"] = O["Year"].astype(int)
    return O


def leer_ecuinput(columnas, escenarios):
    import pandas as pd
    partes = []
    for cod in escenarios:
        if not entrada(cod).exists():
            continue
        i = pd.read_csv(entrada(cod), usecols=["Strategy", "Technology", "Fuel", "Emission", "Year"] + list(columnas),
                        low_memory=False)
        i["Strategy"] = cod
        partes.append(i)
    I = pd.concat(partes, ignore_index=True)
    I = I[I["Year"].notna()].copy()
    I["Year"] = I["Year"].astype(int)
    return I


def _series(o, claves, col):
    """{clave: [26 valores]} de la columna col de ECUOutput, sumando por claves y año."""
    x = o[o[col].notna()]
    if x.empty:
        return {}
    t = x.groupby(claves + ["Year"])[col].sum().unstack("Year").reindex(columns=ANIOS, fill_value=0.0).fillna(0.0)
    return {k: [float(v) for v in fila] for k, fila in zip(t.index, t.values)}


def resultados_de(O, esc):
    """Resultados de un escenario desde ECUOutput.csv, con la misma forma que usa el analisis:
    emisiones {componente: [26]} en Mt; produccion {(tec, combustible): [26]} en PJ; actividad
    {tec: [26]} en PJ; capacidad y capacidad nueva {tec: [26]} en GW; emis_tec {(tec, componente
    CO2e): [26]} en Mt; costo total."""
    o = O[O["Strategy"] == esc]
    prod = {k: v for k, v in _series(o, ["Technology", "Fuel"], "ProductionByTechnology").items() if any(v)}
    et_todas = _series(o, ["Technology", "Emission"], "AnnualTechnologyEmission")
    et = {k: v for k, v in et_todas.items() if k[1] in COMP_ENERGIA and any(v)}
    return {"emisiones": _series(o, ["Emission"], "AnnualEmissions"),
            "produccion": prod,
            "actividad": _series(o, ["Technology"], "TotalTechnologyAnnualActivity"),
            "capacidad": _series(o, ["Technology"], "TotalCapacityAnnual"),
            "capacidad_nueva": _series(o, ["Technology"], "NewCapacity"),
            "emis_tec": et,
            # CO2 (sin CH4 ni N2O) de la generacion por tecnologia, en Mt: el factor del MWh desplazado se compara en
            # CO2 con el margen de operacion de la CTFE
            "co2_pp_tec": {k[0]: v for k, v in et_todas.items() if k[1] == "CO2_PP" and any(v)},
            "costo": float(o["TotalDiscountedCost"].sum())}


def emisiones_energia_kt(res):
    """Emisiones del sector energia en kt CO2e: CO2e_DE + CO2e_PP + CO2e_FUG + CO2e_REF."""
    em = res["emisiones"]
    return [1000.0 * sum(em.get(c, [0.0] * len(ANIOS))[i] for c in COMP_ENERGIA)
            for i in range(len(ANIOS))]


def generacion_por_familia_pj(res):
    out = {n: [0.0] * len(ANIOS) for n, _, _ in FAMILIAS}
    for (tec, comb), v in res["produccion"].items():
        f = familia(tec)
        if f and comb in ("E1ELE", "E3ELE"):
            out[f] = [a + b for a, b in zip(out[f], v)]
    return out


def capacidad_por_familia_gw(res):
    out = {n: [0.0] * len(ANIOS) for n, _, _ in FAMILIAS}
    for tec, v in res["capacidad"].items():
        f = familia(tec)
        if f:
            out[f] = [a + b for a, b in zip(out[f], v)]
    return out


def emisiones_por_subsector_kt(res):
    out = {s: [0.0] * len(ANIOS) for s in SUBSECTORES}
    for (tec, comp), v in res["emis_tec"].items():
        s = subsector(tec, comp)
        out[s] = [a + 1000.0 * b for a, b in zip(out[s], v)]
    return out
