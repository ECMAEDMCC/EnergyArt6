# -*- coding: utf-8 -*-
"""Genera las referencias del Artículo 6 (INCA6 y CONA6) y su sensibilidad de gas (INCA6G y CONA6G) sobre el modelo de
energía de la Segunda NDC (Modelo Climate Lead Group, CLG: ECU_NDC main f19d6b1, sin cambios).

Uso, desde ECU_NDC/Energy:
    python Art6_calibracion/generar_referencias.py                     aplica Art6_calibracion/correcciones_K.csv
    python Art6_calibracion/generar_referencias.py --sin-correcciones  clones exactos de NDCINC y NDCCON
    python Art6_calibracion/generar_referencias.py --comprobar         no escribe; sale con 1 si el disco no coincide

Qué hace:
1. Copia A2_Output_Params/NDCINC en A2_Output_Params/INCA6 e INCA6G y A2_Output_Params/NDCCON en A2_Output_Params/CONA6
   y CONA6G (copia exacta, incluida la columna Scenario de los CSV, que B1 no lee) y aplica las correcciones de carpeta (A2).
2. Añade al libro B1_Scenario_Config.xlsx los escenarios INCA6, CONA6, INCA6G y CONA6G en la hoja Scenarios, con el mismo tipo que
   NDCINC y NDCCON (Activated YES, Base NO, Based_On ref) y Reference igual a su nombre: B1 lee los parámetros de
   A2_Output_Params/<Reference> (B1_Base_Scenarios_Adj_Parallel.py, l. 2129, 2135 y 2176). Copia las filas de NDCINC y
   NDCCON en Distance_Levers, Occupancy_Rate, SmartGrid, Electrical y Efficiency, en el mismo orden relativo, porque
   B1 aplica solo la primera fila de cada clave. Después aplica las correcciones de hoja.
3. Crea B1_Output_Params/<clon> para los cuatro clones: B1 escribe ahí sus parámetros de control y no crea la carpeta.

El libro se edita en su XML. Las filas de los escenarios CLG quedan byte a byte como estaban, con sus fórmulas y
sus valores en caché; solo se borran y se vuelven a escribir, al final de cada hoja, las filas de los clones. Las
celdas copiadas llevan el valor en caché de la celda de origen, sin la fórmula. Correr el script dos veces deja el
mismo libro y las mismas carpetas. Antes de escribir el libro se guarda una copia en
_stale_respaldos/B1_Scenario_Config.xlsx.bak_generar_referencias_<hhmmss> (raíz del repositorio, fuera de git).

Archivo de correcciones (CSV en UTF-8; una fila por corrección):
    codigo, escenarios, hoja_o_carpeta, parametro, tecnologia, anios, valores, unidad, fuente, nota
- escenarios: INCA6, CONA6, INCA6G o CONA6G, separados por punto y coma. Nunca un escenario CLG.
- hoja_o_carpeta:
    A2          cambia A2_Output_Params/<esc>/<parametro>.csv en las filas de esa tecnología y esos años.
                Falla si una fila del escenario en SmartGrid, Electrical o Efficiency sobrescribe ese vector.
    A2_quita_SmartGrid
                retira del clon la fila de SmartGrid (Parameter, Tech_Set) que sobrescribe el vector y escribe el
                vector completo (26 años, 2010-2035) en A2_Output_Params/<esc>/<parametro>.csv. Sirve para los
                EmissionActivityRatio que necesitan más de cuatro decimales: B1 redondea a cuatro decimales las filas de
                SmartGrid (los CH4_PP y N2O_PP de las térmicas quedan en 0). Falla si el clon no tiene esa fila.
    A2_nueva    añade al final de A2_Output_Params/<esc>/<parametro>.csv las filas de una tecnología que no tiene
                ninguna en ese parámetro (p. ej. el piso de actividad de PPBGS o el CapacityToActivityUnit de PPHD).
                Falla si la tecnología ya tiene filas o si no existe en OutputActivityRatio de la carpeta. B1 lee
                el CSV fila a fila y escribe el bloque de la tecnología en el orden de los años.
    SmartGrid   cambia los años de la fila del escenario (Parameter, Tech_Set); si no existe, la crea con método
                Exact y el resto de los años tomados de su carpeta A2. Es el único camino para EmissionActivityRatio
                de las tecnologías que ya tienen fila (tecnologia = «TEC ; EMISION»).
    Efficiency  igual que SmartGrid sobre la fila (Parameter, Set); Set es el combustible de la demanda.
    Electrical  escribe la fila (Parameter, Tech_Set) como vector completo 2010-2035 (Exact_Years hasta 2034 e hito
                2035, método Overwrite ; Interpolate ; Fix_Last). Exige los 26 años.
- tecnologia: TEC, o «TEC ; EMISION» o «TEC ; COMBUSTIBLE» cuando el parámetro tiene ese índice.
- anios: lista con punto y coma (2019;2020) o tramo (2019-2025). valores: uno por año o uno solo para todos.
  Para parámetros sin año (CapacityToActivityUnit, OperationalLife) se escribe «sin_anio» y un solo valor.
- unidad y fuente son obligatorias: ninguna corrección entra sin fuente observada.
- Las correcciones de carpeta (A2 y A2_nueva) se aplican primero y en el orden del archivo; si dos filas tocan el
  mismo vector y los mismos años, manda la última y el script lo avisa y lo anota en registro_referencias.json.
"""
import argparse
import csv
import filecmp
import hashlib
import io
import json
import re
import shutil
import subprocess
import sys
import tempfile
import zipfile
from datetime import datetime
from pathlib import Path
from xml.sax.saxutils import escape

import pandas as pd
from lxml import etree

CLONES = {"INCA6": "NDCINC", "CONA6": "NDCCON", "INCA6G": "NDCINC", "CONA6G": "NDCCON"}  # clon: escenario CLG de origen
OFICIALES = ("BAU", "BAU1NDC", "NDCINC", "NDCCON")
HOJAS_FILAS = ("Distance_Levers", "Occupancy_Rate", "SmartGrid", "Electrical", "Efficiency")
RAMA_ESPERADA = None        # sandbox PNUD: corre en cualquier rama del repositorio
ANIOS = list(range(2010, 2036))  # INI_YR y END_YR de B1
COLUMNAS_CSV = ["codigo", "escenarios", "hoja_o_carpeta", "parametro", "tecnologia", "anios", "valores",
                "unidad", "fuente", "nota"]
DESCRIPCION = {
    "INCA6": "Referencia incondicional del Artículo 6: réplica de NDCINC con carpeta A2 propia; "
             "correcciones en Art6_calibracion/correcciones_K.csv",
    "CONA6": "Referencia condicional del Artículo 6: réplica de NDCCON con carpeta A2 propia; "
             "correcciones en Art6_calibracion/correcciones_K.csv",
    "INCA6G": "Sensibilidad de gas de INCA6: INCA6 con PPNGS en su piso CLG 2026-2035 (fila G01 de "
              "Art6_calibracion/correcciones_K.csv) y respaldo de emergencia de PPFOI (filas RE01), sin el cual no "
              "tiene solución",
    "CONA6G": "Sensibilidad de gas de CONA6: CONA6 con PPNGS en su piso CLG 2026-2035 (fila G01 de "
              "Art6_calibracion/correcciones_K.csv)",
}
METODO_ELECTRICAL = "Overwrite  ;  Interpolate  ;  Fix_Last"
NS = "http://schemas.openxmlformats.org/spreadsheetml/2006/main"
NS_REL = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"


class ErrorReferencias(Exception):
    pass


def q(etiqueta):
    return f"{{{NS}}}{etiqueta}"


def md5(datos):
    return hashlib.md5(datos).hexdigest()


def md5_carpeta(carpeta):
    h = hashlib.md5()
    for f in sorted(Path(carpeta).iterdir()):
        h.update(f.name.encode())
        h.update(f.read_bytes())
    return h.hexdigest()


# ----------------------------------------------------------------------------------------------------------------
# Lectura del xlsx (XML)
# ----------------------------------------------------------------------------------------------------------------
def col_a_num(col):
    n = 0
    for ch in col:
        n = n * 26 + ord(ch) - 64
    return n


def separar_ref(ref):
    m = re.fullmatch(r"([A-Z]+)(\d+)", ref)
    return m.group(1), int(m.group(2))


def rutas_hojas(z):
    """Nombre de hoja -> ruta del XML dentro del zip."""
    wb = etree.fromstring(z.read("xl/workbook.xml"))
    rels = etree.fromstring(z.read("xl/_rels/workbook.xml.rels"))
    destino = {r.get("Id"): r.get("Target") for r in rels}
    salida = {}
    for hoja in wb.iter(q("sheet")):
        t = destino[hoja.get(f"{{{NS_REL}}}id")]
        salida[hoja.get("name")] = t.lstrip("/") if t.startswith("/") else "xl/" + t
    return salida


def leer_compartidas(z):
    if "xl/sharedStrings.xml" not in z.namelist():
        return []
    raiz = etree.fromstring(z.read("xl/sharedStrings.xml"))
    salida = []
    for si in raiz.iter(q("si")):
        salida.append("".join(t.text or "" for t in si.iter(q("t")) if t.getparent().tag != q("rPh")))
    return salida


def leer_celda(c, compartidas):
    """Devuelve (tipo, texto) con el valor en caché: tipo 's' texto, 'n' número (texto crudo), 'b' lógico, None vacía."""
    t = c.get("t", "n")
    if t == "inlineStr":
        return "s", "".join(x.text or "" for x in c.iter(q("t")))
    v = c.find(q("v"))
    if v is None or v.text is None:
        return None, None
    if t == "s":
        return "s", compartidas[int(v.text)]
    if t == "str":
        return "s", v.text
    if t == "b":
        return "b", v.text
    if t == "e":
        raise ErrorReferencias(f"celda {c.get('r')} con error de Excel ({v.text})")
    return "n", v.text


def leer_hoja(xml, compartidas):
    """Filas de la hoja: lista de (numero_de_fila, {columna: (tipo, texto, estilo)})."""
    raiz = etree.fromstring(xml)
    filas = []
    for fila in raiz.find(q("sheetData")).iter(q("row")):
        celdas = {}
        for c in fila.iter(q("c")):
            col, _ = separar_ref(c.get("r"))
            tipo, texto = leer_celda(c, compartidas)
            celdas[col] = (tipo, texto, c.get("s"))
        filas.append((int(fila.get("r")), celdas))
    return filas


def nombre_cabecera(celda):
    tipo, texto, _ = celda
    if tipo == "n":
        valor = float(texto)
        return int(valor) if valor.is_integer() else valor
    return texto


class Hoja:
    """Filas de datos de una hoja, separadas en oficiales (intocables) y clones (se regeneran)."""

    def __init__(self, nombre, xml, compartidas):
        self.nombre = nombre
        self.xml = xml.decode("utf-8")
        filas = leer_hoja(xml, compartidas)
        if not filas or filas[0][0] != 1:
            raise ErrorReferencias(f"{nombre}: falta la fila de cabecera")
        self.cabecera = {col: nombre_cabecera(c) for col, c in filas[0][1].items() if c[0] is not None}
        self.col_de = {v: k for k, v in self.cabecera.items()}
        self.datos = []      # filas de datos (con algún valor) que no son clones
        self.clones = []     # números de fila de clones ya presentes
        ultima_dato = 1
        for r, celdas in filas[1:]:
            valor_a = celdas.get("A", (None, None, None))[1]
            con_valor = any(t is not None for t, _, _ in celdas.values())
            if valor_a in CLONES:
                self.clones.append(r)
            elif con_valor:
                if self.clones:
                    raise ErrorReferencias(f"{nombre}: la fila {r} de {valor_a} está después de filas de clones; "
                                           "los clones deben ir al final")
                self.datos.append((r, celdas))
                ultima_dato = r
            else:
                raise ErrorReferencias(f"{nombre}: fila {r} sin valores (solo formato); revísela a mano")
        self.ultima_oficial = ultima_dato

    def filas_de(self, escenario):
        return [dict(c) for _, c in self.datos if c.get("A", (None, None, None))[1] == escenario]

    def estilos_tipo(self):
        """Estilo por columna de la primera fila de datos, para filas creadas por corrección."""
        return {col: c[2] for col, c in self.datos[0][1].items()} if self.datos else {}

    def valor(self, celdas, columna):
        col = self.col_de.get(columna)
        if col is None or col not in celdas:
            return None
        tipo, texto, _ = celdas[col]
        if tipo == "n":
            return nombre_cabecera(celdas[col])
        return texto

    def poner(self, celdas, columna, tipo, texto, estilos=None):
        col = self.col_de[columna]
        estilo = celdas[col][2] if col in celdas else (estilos or {}).get(col)
        celdas[col] = (tipo, texto, estilo)

    def xml_nuevo(self, filas_clon):
        """Quita las filas de clones y escribe las nuevas tras la última fila oficial."""
        texto = self.xml
        for r in self.clones:
            texto, n = re.subn(rf'<row r="{r}"(?=[\s>/])[^>]*?(?:/>|>.*?</row>)', "", texto, count=1, flags=re.S)
            if n != 1:
                raise ErrorReferencias(f"{self.nombre}: no se encontró la fila {r} para quitarla")
        partes = []
        r = self.ultima_oficial
        for celdas in filas_clon:
            r += 1
            partes.append(fila_xml(r, celdas))
        if texto.count("</sheetData>") != 1:
            raise ErrorReferencias(f"{self.nombre}: estructura de sheetData inesperada")
        texto = texto.replace("</sheetData>", "".join(partes) + "</sheetData>")
        m = re.search(r'<dimension ref="([A-Z]+)(\d+):([A-Z]+)(\d+)"/>', texto)
        if m:
            texto = texto.replace(m.group(0), f'<dimension ref="{m.group(1)}{m.group(2)}:{m.group(3)}{r}"/>')
        return texto.encode("utf-8")


def fila_xml(r, celdas):
    partes = [f'<row r="{r}">']
    for col in sorted(celdas, key=col_a_num):
        tipo, texto, estilo = celdas[col]
        s = f' s="{estilo}"' if estilo is not None else ""
        ref = f"{col}{r}"
        if tipo is None:
            partes.append(f'<c r="{ref}"{s}/>')
        elif tipo == "s":
            partes.append(f'<c r="{ref}"{s} t="inlineStr"><is><t xml:space="preserve">{escape(texto)}</t></is></c>')
        elif tipo == "b":
            partes.append(f'<c r="{ref}"{s} t="b"><v>{texto}</v></c>')
        else:
            partes.append(f'<c r="{ref}"{s}><v>{texto}</v></c>')
    partes.append("</row>")
    return "".join(partes)


# ----------------------------------------------------------------------------------------------------------------
# Correcciones
# ----------------------------------------------------------------------------------------------------------------
SIN_ANIO = "sin_anio"
DESTINOS_A2 = ("A2", "A2_nueva", "A2_quita_SmartGrid")


def leer_anios(texto):
    if str(texto).strip() == SIN_ANIO:
        return [None]
    anios = []
    for trozo in re.split(r"[;,]", str(texto)):
        trozo = trozo.strip()
        if not trozo:
            continue
        if "-" in trozo:
            a, b = (int(x) for x in trozo.split("-"))
            anios += list(range(a, b + 1))
        else:
            anios.append(int(trozo))
    return anios


def leer_correcciones(ruta):
    if ruta is None or not Path(ruta).exists() or Path(ruta).stat().st_size == 0:
        return []
    df = pd.read_csv(ruta, dtype=str, keep_default_na=False, encoding="utf-8-sig")
    if list(df.columns) != COLUMNAS_CSV:
        raise ErrorReferencias(f"{ruta}: columnas {list(df.columns)}; se esperan {COLUMNAS_CSV}")
    correcciones = []
    for i, fila in df.iterrows():
        f = {k: str(v).strip() for k, v in fila.items()}
        if not any(f.values()):
            continue
        donde = f"correcciones fila {i + 2} ({f['codigo'] or 'sin código'})"
        for k in ("codigo", "escenarios", "hoja_o_carpeta", "parametro", "tecnologia", "anios", "valores",
                  "unidad", "fuente"):
            if not f[k]:
                raise ErrorReferencias(f"{donde}: columna {k} vacía")
        escenarios = [e.strip() for e in f["escenarios"].split(";") if e.strip()]
        for e in escenarios:
            if e not in CLONES:
                raise ErrorReferencias(f"{donde}: el escenario {e} no es una referencia del Artículo 6 "
                                       f"({', '.join(CLONES)}); los escenarios CLG no se corrigen")
        if f["hoja_o_carpeta"] not in DESTINOS_A2 + ("SmartGrid", "Efficiency", "Electrical"):
            raise ErrorReferencias(f"{donde}: hoja_o_carpeta {f['hoja_o_carpeta']} no válida")
        anios = leer_anios(f["anios"])
        if anios == [None]:
            if f["hoja_o_carpeta"] not in DESTINOS_A2:
                raise ErrorReferencias(f"{donde}: «{SIN_ANIO}» solo vale para correcciones de carpeta A2")
        elif not anios or len(set(anios)) != len(anios) or any(a not in ANIOS for a in anios):
            raise ErrorReferencias(f"{donde}: años inválidos o repetidos: {f['anios']}")
        valores = [v.strip() for v in f["valores"].split(";") if v.strip()]
        for v in valores:
            try:
                float(v)
            except ValueError:
                raise ErrorReferencias(f"{donde}: valor no numérico {v!r} (use punto decimal)") from None
        if len(valores) == 1:
            valores = valores * len(anios)
        if len(valores) != len(anios):
            raise ErrorReferencias(f"{donde}: {len(anios)} años y {len(valores)} valores")
        partes = [p.strip() for p in f["tecnologia"].split(";")]
        correcciones.append({**f, "escenarios_l": escenarios, "anios_l": anios, "valores_l": valores,
                             "tec": partes[0], "indice2": partes[1] if len(partes) > 1 else None, "donde": donde})
    codigos = [c["codigo"] for c in correcciones]
    if len(set(codigos)) != len(codigos):
        raise ErrorReferencias("códigos de corrección repetidos")
    return correcciones


def filas_a2(ruta_csv, tec, indice2):
    """Líneas del CSV de A2 que corresponden a la tecnología (y al combustible o emisión, si se da)."""
    contenido = ruta_csv.read_bytes().decode("utf-8")
    lineas = contenido.splitlines(keepends=True)
    cab = next(csv.reader([lineas[0]]))
    i_t, i_y, i_v = cab.index("TECHNOLOGY"), cab.index("YEAR"), cab.index("Value")
    i_f, i_e = cab.index("FUEL"), cab.index("EMISSION")
    salida = []
    for n, linea in enumerate(lineas[1:], start=1):
        campos = next(csv.reader([linea.rstrip("\r\n")]))
        if campos[i_t] != tec:
            continue
        if indice2 is not None and indice2 not in (campos[i_f], campos[i_e]):
            continue
        salida.append((n, campos, int(campos[i_y]) if campos[i_y] else None))
    return lineas, cab, salida, i_v


def vector_a2(carpeta, parametro, tec, indice2, donde):
    ruta = carpeta / f"{parametro}.csv"
    if not ruta.exists():
        raise ErrorReferencias(f"{donde}: no existe {ruta}")
    _, cab, filas, i_v = filas_a2(ruta, tec, indice2)
    por_anio = {}
    for _, campos, anio in filas:
        if anio in por_anio:
            raise ErrorReferencias(f"{donde}: {parametro} de {tec} tiene más de una fila por año en A2 "
                                   "(indique el combustible o la emisión)")
        por_anio[anio] = campos[i_v]
    if sorted(por_anio) != ANIOS:
        raise ErrorReferencias(f"{donde}: {parametro} de {tec} no tiene los 26 años en A2")
    return por_anio


def coincide_tecnologia(tech_set, tec, indice2):
    tech_set = str(tech_set)
    if "Contains" in tech_set:
        indicadores = tech_set.replace(" ", "").split(":")[1].split(";")
        return any(ind in tec for ind in indicadores) and "IMP" not in tec
    partes = [p.strip() for p in tech_set.split(";")]
    if partes[0] != tec:
        return False
    return indice2 is None or len(partes) == 1 or partes[1] == indice2


def anios_sobrescritos(hoja, celdas, nombre_hoja):
    """Años del vector que la fila del libro sobrescribe en B1 (None si no escribe nada)."""
    if nombre_hoja == "Electrical":
        integrado = str(hoja.valor(celdas, "Built-in Parameter-Set")).replace(" ", "")
        metodo = str(hoja.valor(celdas, "Method")).replace(" ", "")
        if integrado == "NO":
            return set(ANIOS) if "Write" in metodo else None
        if "intact" in str(hoja.valor(celdas, "Exact_Years")):
            y_ini = float(hoja.valor(celdas, "y_ini"))
            return {a for a in ANIOS if a > y_ini}
        return set(ANIOS)
    if str(hoja.valor(celdas, "Built-in Parameter-Set")) != "YES":
        return None
    return set(ANIOS)


def verificar_hojas_no_pisan(c, esc, hojas, filas_clon):
    """Falla si una fila del clon en las hojas sobrescribe en B1 el vector que la corrección cambia en A2."""
    for nombre_hoja, col_tec in (("SmartGrid", "Tech_Set"), ("Electrical", "Tech_Set"), ("Efficiency", "Set")):
        hoja = hojas[nombre_hoja]
        for celdas in filas_clon[nombre_hoja][esc]:
            if hoja.valor(celdas, "Parameter") != c["parametro"]:
                continue
            if not coincide_tecnologia(hoja.valor(celdas, col_tec), c["tec"], c["indice2"]):
                continue
            pisados = anios_sobrescritos(hoja, celdas, nombre_hoja)
            if pisados and (pisados & set(c["anios_l"]) or c["anios_l"] == [None]):
                raise ErrorReferencias(
                    f"{c['donde']}: la fila de {esc} en {nombre_hoja} ({c['parametro']}, "
                    f"{hoja.valor(celdas, col_tec)}) sobrescribe ese vector; corrija en la hoja {nombre_hoja}")


def aplicar_a2_nueva(c, esc, carpeta, hojas, filas_clon):
    """Añade las filas de una tecnología que no tiene ninguna en el CSV del parámetro; devuelve cuántas añadió."""
    verificar_hojas_no_pisan(c, esc, hojas, filas_clon)
    ruta = carpeta / f"{c['parametro']}.csv"
    if not ruta.exists():
        raise ErrorReferencias(f"{c['donde']}: no existe {ruta}")
    lineas, cab, filas, i_v = filas_a2(ruta, c["tec"], c["indice2"])
    if filas:
        raise ErrorReferencias(f"{c['donde']}: {c['tecnologia']} ya tiene {len(filas)} filas en {ruta.name}; "
                               "use el destino A2")
    _, _, filas_oar, _ = filas_a2(carpeta / "OutputActivityRatio.csv", c["tec"], None)
    if not filas_oar:
        raise ErrorReferencias(f"{c['donde']}: {c['tec']} no está en OutputActivityRatio.csv; ¿nombre mal escrito?")
    if len(lineas) < 2:
        raise ErrorReferencias(f"{c['donde']}: {ruta.name} no tiene filas de ejemplo")
    ejemplo = next(csv.reader([lineas[1].rstrip("\r\n")]))
    final = lineas[1][len(lineas[1].rstrip("\r\n")):] or "\n"
    con_anio = c["anios_l"] != [None]
    if con_anio and c["anios_l"] != ANIOS:
        # B1 (function_C_mathprog) escribe los valores de cada tecnología bajo la cabecera de años por posición:
        # un bloque incompleto quedaría corrido de año.
        raise ErrorReferencias(f"{c['donde']}: una tecnología nueva en {ruta.name} necesita los 26 años 2010-2035 "
                               "en orden")
    if con_anio != bool(ejemplo[cab.index("YEAR")]):
        raise ErrorReferencias(f"{c['donde']}: {ruta.name} {'lleva' if not con_anio else 'no lleva'} año; "
                               f"revise la columna anios")
    if not lineas[-1].endswith(("\n", "\r")):
        lineas[-1] += final
    nuevas = []
    for anio, valor in zip(c["anios_l"], c["valores_l"]):
        campos = [""] * len(cab)
        for col in ("PARAMETER", "Scenario", "REGION", "TIMESLICE"):
            campos[cab.index(col)] = ejemplo[cab.index(col)]
        campos[cab.index("TECHNOLOGY")] = c["tec"]
        if c["indice2"] is not None:
            raise ErrorReferencias(f"{c['donde']}: A2_nueva no admite combustible ni emisión")
        if anio is not None:
            campos[cab.index("YEAR")] = str(anio)
        campos[i_v] = valor
        nuevas.append(",".join(campos) + final)
    ruta.write_bytes(("".join(lineas) + "".join(nuevas)).encode("utf-8"))
    return len(nuevas)


def aplicar_a2_quita(c, esc, carpeta, hojas, filas_clon):
    """Retira la fila de SmartGrid del clon que sobrescribe el vector y escribe el vector completo en A2."""
    if c["anios_l"] != ANIOS:
        raise ErrorReferencias(f"{c['donde']}: A2_quita_SmartGrid necesita los 26 años 2010-2035 en orden")
    hoja = hojas["SmartGrid"]
    filas = filas_clon["SmartGrid"][esc]
    objetivo = [f for f in filas if hoja.valor(f, "Parameter") == c["parametro"] and
                " ".join(str(hoja.valor(f, "Tech_Set")).split()) == " ".join(c["tecnologia"].split())]
    if len(objetivo) != 1:
        raise ErrorReferencias(f"{c['donde']}: el clon {esc} tiene {len(objetivo)} filas de SmartGrid "
                               f"({c['parametro']}, {c['tecnologia']}); se espera una")
    filas.remove(objetivo[0])
    return aplicar_a2(c, esc, carpeta, hojas, filas_clon)


def aplicar_a2(c, esc, carpeta, hojas, filas_clon):
    """Cambia el CSV de la carpeta A2 del clon; devuelve el número de valores cambiados."""
    for nombre_hoja, col_tec in (("SmartGrid", "Tech_Set"), ("Electrical", "Tech_Set"), ("Efficiency", "Set")):
        hoja = hojas[nombre_hoja]
        for celdas in filas_clon[nombre_hoja][esc]:
            if hoja.valor(celdas, "Parameter") != c["parametro"]:
                continue
            if not coincide_tecnologia(hoja.valor(celdas, col_tec), c["tec"], c["indice2"]):
                continue
            pisados = anios_sobrescritos(hoja, celdas, nombre_hoja)
            if pisados and pisados & set(c["anios_l"]):
                raise ErrorReferencias(
                    f"{c['donde']}: la fila de {esc} en {nombre_hoja} ({c['parametro']}, "
                    f"{hoja.valor(celdas, col_tec)}) sobrescribe los años {sorted(pisados & set(c['anios_l']))}; "
                    f"corrija en la hoja {nombre_hoja}")
    if c["tec"].startswith("Techs_"):
        print(f"AVISO  {c['donde']}: {c['tec']} es un grupo de transporte que B1 reajusta; verifique el datafile")
    ruta = carpeta / f"{c['parametro']}.csv"
    if not ruta.exists():
        raise ErrorReferencias(f"{c['donde']}: no existe {ruta}")
    lineas, _, filas, i_v = filas_a2(ruta, c["tec"], c["indice2"])
    nuevos = dict(zip(c["anios_l"], c["valores_l"]))
    vistos = {}
    for n, campos, anio in filas:
        if anio in nuevos:
            vistos[anio] = vistos.get(anio, 0) + 1
            final = lineas[n][len(lineas[n].rstrip("\r\n")):]
            campos = list(campos)
            campos[i_v] = nuevos[anio]
            lineas[n] = ",".join(campos) + final
    faltan = [a for a in c["anios_l"] if a not in vistos]
    dobles = [a for a, k in vistos.items() if k > 1]
    if faltan:
        raise ErrorReferencias(f"{c['donde']}: {c['parametro']} de {c['tecnologia']} sin fila en A2 para {faltan}")
    if dobles:
        raise ErrorReferencias(f"{c['donde']}: {c['parametro']} de {c['tecnologia']} con varias filas por año "
                               f"en A2 ({dobles}); indique el combustible o la emisión")
    ruta.write_bytes("".join(lineas).encode("utf-8"))
    return len(c["anios_l"])


def aplicar_hoja(c, esc, hojas, filas_clon, carpeta_a2):
    """Cambia o crea la fila del clon en la hoja; devuelve el número de celdas cambiadas."""
    nombre_hoja = c["hoja_o_carpeta"]
    hoja = hojas[nombre_hoja]
    col_tec = "Set" if nombre_hoja == "Efficiency" else "Tech_Set"
    filas = filas_clon[nombre_hoja][esc]
    objetivo = None
    for celdas in filas:
        if hoja.valor(celdas, "Parameter") == c["parametro"] and \
                " ".join(str(hoja.valor(celdas, col_tec)).split()) == " ".join(c["tecnologia"].split()):
            objetivo = celdas
            break
    estilos = hoja.estilos_tipo()
    if nombre_hoja == "Electrical":
        if c["anios_l"] != ANIOS:
            raise ErrorReferencias(f"{c['donde']}: en Electrical la corrección escribe el vector completo; "
                                   "dé los 26 años 2010-2035 en orden")
        vector_a2(carpeta_a2, c["parametro"], c["tec"], None, c["donde"])  # Built-in YES exige el vector en A2
        if objetivo is None:
            objetivo = {}
            filas.append(objetivo)
            hoja.poner(objetivo, "Scenario", "s", esc, estilos)
            hoja.poner(objetivo, "Parameter", "s", c["parametro"], estilos)
            hoja.poner(objetivo, "Tech_Set", "s", c["tecnologia"], estilos)
        v = c["valores_l"]
        for columna, tipo, texto in (("Description Parameter-Set", "s", f"{c['codigo']}: {c['nota']}"),
                                     ("Built-in Parameter-Set", "s", "YES"), ("Linear", "s", "YES"),
                                     ("Exact_Years", "s", " ; ".join(str(a) for a in ANIOS[:-1])),
                                     ("Exact_Values", "s", " ; ".join(v[:-1])), ("y_ini", "n", str(ANIOS[-2])),
                                     ("Milestone_Years", "n", str(ANIOS[-1])), ("Milestone_Value", "n", v[-1]),
                                     ("Unit", "s", c["unidad"]), ("Security_Multiplier", "n", "1"),
                                     ("Method", "s", METODO_ELECTRICAL)):
            hoja.poner(objetivo, columna, tipo, texto, estilos)
        return len(ANIOS)
    if objetivo is None:
        if nombre_hoja == "Efficiency":
            base = vector_demanda(carpeta_a2, c["parametro"], c["tecnologia"], c["donde"])
        else:
            base = vector_a2(carpeta_a2, c["parametro"], c["tec"], c["indice2"], c["donde"])
        objetivo = {}
        filas.append(objetivo)
        hoja.poner(objetivo, "Scenario", "s", esc, estilos)
        hoja.poner(objetivo, "Parameter", "s", c["parametro"], estilos)
        hoja.poner(objetivo, col_tec, "s", c["tecnologia"], estilos)
        if nombre_hoja == "Efficiency":
            hoja.poner(objetivo, "Set_Index", "s", "f", estilos)
            hoja.poner(objetivo, "Description_Set", "s", f"{c['codigo']}: {c['nota']}", estilos)
        else:
            hoja.poner(objetivo, "Description Parameter-Set", "s", f"{c['codigo']}: {c['nota']}", estilos)
        hoja.poner(objetivo, "Built-in Parameter-Set", "s", "YES", estilos)
        hoja.poner(objetivo, "Method", "s", "Exact", estilos)
        for anio in ANIOS:
            hoja.poner(objetivo, anio, "n", base[anio], estilos)
    else:
        metodo = str(hoja.valor(objetivo, "Method")).strip()
        if metodo != "Exact" or str(hoja.valor(objetivo, "Built-in Parameter-Set")) != "YES":
            raise ErrorReferencias(f"{c['donde']}: la fila de {esc} en {nombre_hoja} usa el método {metodo}; "
                                   "solo se corrigen filas Exact con Built-in YES")
    for anio, valor in zip(c["anios_l"], c["valores_l"]):
        if anio not in hoja.col_de:
            raise ErrorReferencias(f"{c['donde']}: la hoja {nombre_hoja} no tiene columna {anio}")
        hoja.poner(objetivo, anio, "n", valor, estilos)
    return len(c["anios_l"])


def vector_demanda(carpeta, parametro, combustible, donde):
    ruta = carpeta / f"{parametro}.csv"
    df = pd.read_csv(ruta, dtype=str, keep_default_na=False)
    df = df[df["FUEL"] == combustible]
    if sorted(int(a) for a in df["YEAR"]) != ANIOS:
        raise ErrorReferencias(f"{donde}: {parametro} de {combustible} no tiene los 26 años en A2")
    return {int(a): v for a, v in zip(df["YEAR"], df["Value"])}


# ----------------------------------------------------------------------------------------------------------------
# Generación
# ----------------------------------------------------------------------------------------------------------------
def rama_actual(raiz):
    r = subprocess.run(["git", "-C", str(raiz), "rev-parse", "--abbrev-ref", "HEAD"], capture_output=True, text=True)
    return r.stdout.strip() if r.returncode == 0 else None


def commit_actual(raiz):
    r = subprocess.run(["git", "-C", str(raiz), "rev-parse", "HEAD"], capture_output=True, text=True)
    return r.stdout.strip() if r.returncode == 0 else None


def construir(energia, correcciones, tmp):
    """Arma en tmp las carpetas A2 de los clones y el libro nuevo; devuelve (bytes del libro, registro)."""
    libro = energia / "B1_Scenario_Config.xlsx"
    original = libro.read_bytes()
    registro = {"correcciones": []}
    # 1. carpetas A2
    carpetas = {}
    for clon, origen in CLONES.items():
        fuente = energia / "A2_Output_Params" / origen
        destino = Path(tmp) / "A2" / clon
        shutil.copytree(fuente, destino)
        carpetas[clon] = destino
    # 2. libro
    with zipfile.ZipFile(io.BytesIO(original)) as z:
        rutas = rutas_hojas(z)
        compartidas = leer_compartidas(z)
        hojas = {n: Hoja(n, z.read(rutas[n]), compartidas) for n in ("Scenarios",) + HOJAS_FILAS}
    filas_clon = {}
    for nombre in HOJAS_FILAS:
        hoja = hojas[nombre]
        filas_clon[nombre] = {}
        for clon, origen in CLONES.items():
            copias = []
            for celdas in hoja.filas_de(origen):
                hoja.poner(celdas, "Scenario", "s", clon)
                if "Reference" in hoja.col_de and hoja.valor(celdas, "Reference") == origen:
                    hoja.poner(celdas, "Reference", "s", clon)
                copias.append(celdas)
            filas_clon[nombre][clon] = copias
    escenarios = hojas["Scenarios"]
    filas_esc = []
    for clon, origen in CLONES.items():
        base = escenarios.filas_de(origen)
        if len(base) != 1:
            raise ErrorReferencias(f"Scenarios: {origen} aparece {len(base)} veces")
        celdas = base[0]
        if (escenarios.valor(celdas, "Reference"), escenarios.valor(celdas, "Based_On"),
                escenarios.valor(celdas, "Base")) != (origen, "ref", "NO"):
            raise ErrorReferencias(f"Scenarios: {origen} ya no es un escenario ref con carpeta propia; revise el diseño")
        escenarios.poner(celdas, "Name", "s", clon)
        escenarios.poner(celdas, "Reference", "s", clon)
        escenarios.poner(celdas, "Description", "s", DESCRIPCION[clon])
        filas_esc.append(celdas)
    # 3. correcciones: primero las de carpeta, porque las filas nuevas de hoja toman de A2 los años no corregidos;
    #    dentro de cada grupo, en el orden del archivo (sorted es estable)
    vistos = {}  # (escenario, destino A2 u hoja, parámetro, tecnología normalizada) -> [(código, años)]
    for c in sorted(correcciones, key=lambda c: c["hoja_o_carpeta"] not in DESTINOS_A2):
        for esc in c["escenarios_l"]:
            if c["hoja_o_carpeta"] == "A2":
                n = aplicar_a2(c, esc, carpetas[esc], hojas, filas_clon)
            elif c["hoja_o_carpeta"] == "A2_nueva":
                n = aplicar_a2_nueva(c, esc, carpetas[esc], hojas, filas_clon)
            elif c["hoja_o_carpeta"] == "A2_quita_SmartGrid":
                n = aplicar_a2_quita(c, esc, carpetas[esc], hojas, filas_clon)
            else:
                n = aplicar_hoja(c, esc, hojas, filas_clon, carpetas[esc])
            destino = "A2" if c["hoja_o_carpeta"] in DESTINOS_A2 else c["hoja_o_carpeta"]
            clave = (esc, destino, c["parametro"], " ".join(c["tecnologia"].split()))
            sustituye = []
            for codigo_previo, anios_previos in vistos.get(clave, []):
                comunes = sorted(a for a in set(anios_previos) & set(c["anios_l"]) if a is not None)
                if comunes:
                    sustituye.append({"codigo": codigo_previo, "anios": comunes})
                    if esc == c["escenarios_l"][0]:
                        print(f"AVISO  {c['codigo']} sustituye en {c['parametro']} {c['tecnologia']} los años "
                              f"{comunes[0]}-{comunes[-1]} ({len(comunes)}) de {codigo_previo}")
            vistos.setdefault(clave, []).append((c["codigo"], c["anios_l"]))
            registro["correcciones"].append({"codigo": c["codigo"], "escenario": esc, "destino": c["hoja_o_carpeta"],
                                             "parametro": c["parametro"], "tecnologia": c["tecnologia"],
                                             "valores_cambiados": n, "sustituye": sustituye,
                                             "fuente": c["fuente"]})
    # 4. zip nuevo con las mismas entradas y el mismo orden
    nuevos = {rutas["Scenarios"]: escenarios.xml_nuevo(filas_esc)}
    for nombre in HOJAS_FILAS:
        filas = [f for clon in CLONES for f in filas_clon[nombre][clon]]
        nuevos[rutas[nombre]] = hojas[nombre].xml_nuevo(filas)
    salida = io.BytesIO()
    with zipfile.ZipFile(io.BytesIO(original)) as zin, zipfile.ZipFile(salida, "w") as zout:
        for info in zin.infolist():
            datos = nuevos.get(info.filename, zin.read(info.filename))
            zi = zipfile.ZipInfo(info.filename, date_time=info.date_time)
            zi.compress_type = info.compress_type
            zi.external_attr = info.external_attr
            zi.create_system = info.create_system
            zout.writestr(zi, datos)
    registro["filas_por_hoja"] = {n: {c: len(filas_clon[n][c]) for c in CLONES} for n in HOJAS_FILAS}
    return salida.getvalue(), carpetas, registro


def comparar_libros(antes, despues, correcciones):
    """Las filas oficiales no cambian; sin correcciones de hoja, cada clon es su origen con otro nombre."""
    hojas_antes = pd.read_excel(io.BytesIO(antes), sheet_name=None)
    hojas_despues = pd.read_excel(io.BytesIO(despues), sheet_name=None)
    if list(hojas_antes) != list(hojas_despues):
        raise ErrorReferencias("el libro nuevo no tiene las mismas hojas")
    con_hoja = {c["hoja_o_carpeta"] for c in correcciones if c["hoja_o_carpeta"] not in DESTINOS_A2}
    if any(c["hoja_o_carpeta"] == "A2_quita_SmartGrid" for c in correcciones):
        con_hoja.add("SmartGrid")
    for nombre, a in hojas_antes.items():
        d = hojas_despues[nombre]
        if list(a.columns) != list(d.columns):
            raise ErrorReferencias(f"{nombre}: cambiaron las columnas")
        col = a.columns[0] if len(a.columns) else None
        if col is None:
            continue
        a_of = a[~a[col].isin(list(CLONES))].reset_index(drop=True)
        d_of = d[~d[col].isin(list(CLONES))].reset_index(drop=True)
        pd.testing.assert_frame_equal(a_of, d_of, check_dtype=False, obj=f"{nombre} (filas CLG)")
        if nombre in HOJAS_FILAS and nombre not in con_hoja:
            for clon, origen in CLONES.items():
                o = d[d[col] == origen].drop(columns=[col]).reset_index(drop=True)
                if "Reference" in o.columns:
                    o["Reference"] = o["Reference"].replace({origen: clon})
                k = d[d[col] == clon].drop(columns=[col]).reset_index(drop=True)
                pd.testing.assert_frame_equal(o, k, check_dtype=False, obj=f"{nombre} ({clon} frente a {origen})")


def main():
    energia_defecto = Path(__file__).resolve().parents[1]
    p = argparse.ArgumentParser(description="Genera INCA6, CONA6, INCA6G y CONA6G (referencias del Artículo 6).")
    p.add_argument("--raiz", type=Path, default=energia_defecto, help="carpeta Energy (por omisión, la del script)")
    p.add_argument("--correcciones", type=Path, default=Path(__file__).with_name("correcciones_K.csv"))
    p.add_argument("--sin-correcciones", action="store_true", help="ignora el archivo de correcciones")
    p.add_argument("--comprobar", action="store_true", help="no escribe; sale con 1 si el disco no coincide")
    p.add_argument("--respaldo", type=Path, default=None, help="carpeta del respaldo del libro")
    args = p.parse_args()
    energia = args.raiz.resolve()
    rama = rama_actual(energia)
    if RAMA_ESPERADA and rama is not None and rama != RAMA_ESPERADA:
        raise ErrorReferencias(f"rama {rama}; este script solo corre en {RAMA_ESPERADA}")
    correcciones = [] if args.sin_correcciones else leer_correcciones(args.correcciones)
    print(f"Energía: {energia}\nRama: {rama}\nCorrecciones: "
          f"{'desactivadas' if args.sin_correcciones else f'{len(correcciones)} en {args.correcciones.name}'}")
    libro = energia / "B1_Scenario_Config.xlsx"
    antes = libro.read_bytes()
    with tempfile.TemporaryDirectory() as tmp:
        nuevo, carpetas, registro = construir(energia, correcciones, tmp)
        comparar_libros(antes, nuevo, correcciones)
        difiere = []
        if nuevo != antes:
            difiere.append(libro.name)
        for clon, carpeta in carpetas.items():
            destino = energia / "A2_Output_Params" / clon
            iguales = destino.exists() and sorted(f.name for f in destino.iterdir()) == \
                sorted(f.name for f in carpeta.iterdir()) and \
                all(filecmp.cmp(carpeta / f.name, destino / f.name, shallow=False) for f in carpeta.iterdir())
            if not iguales:
                difiere.append(f"A2_Output_Params/{clon}")
        for clon in CLONES:
            if not (energia / "B1_Output_Params" / clon).is_dir():
                difiere.append(f"B1_Output_Params/{clon}")
        if args.comprobar:
            print("Coincide con lo que generaría el script" if not difiere else f"Difiere: {', '.join(difiere)}")
            return 1 if difiere else 0
        if libro.name in difiere:
            respaldo = args.respaldo or energia.parent / "_stale_respaldos"
            respaldo.mkdir(parents=True, exist_ok=True)
            copia = respaldo / f"B1_Scenario_Config.xlsx.bak_generar_referencias_{datetime.now():%H%M%S}"
            shutil.copy2(libro, copia)
            libro.write_bytes(nuevo)
            print(f"Libro escrito; respaldo en {copia}")
        for clon, carpeta in carpetas.items():
            destino = energia / "A2_Output_Params" / clon
            if f"A2_Output_Params/{clon}" in difiere:
                if destino.exists():
                    shutil.rmtree(destino)
                shutil.copytree(carpeta, destino)
                print(f"Carpeta A2_Output_Params/{clon} escrita")
        for clon in CLONES:
            (energia / "B1_Output_Params" / clon).mkdir(parents=True, exist_ok=True)
    if not difiere:
        print("Sin cambios: el libro y las carpetas ya estaban generados")
    registro.update({
        "rama": rama, "commit": commit_actual(energia),
        "correcciones_archivo": None if args.sin_correcciones else args.correcciones.name,
        "correcciones_md5": None if args.sin_correcciones or not args.correcciones.exists()
        else md5(args.correcciones.read_bytes()),
        "libro_md5": md5(libro.read_bytes()),
        "a2_md5": {c: md5_carpeta(energia / "A2_Output_Params" / c) for c in CLONES},
        "a2_origen_md5": {o: md5_carpeta(energia / "A2_Output_Params" / o) for o in CLONES.values()},
    })
    (energia / "Art6_calibracion").mkdir(exist_ok=True)
    (energia / "Art6_calibracion" / "registro_referencias.json").write_text(
        json.dumps(registro, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    for n, por_clon in registro["filas_por_hoja"].items():
        print(f"  {n:16s} " + "  ".join(f"{c}: {k} filas" for c, k in por_clon.items()))
    print(f"  correcciones aplicadas: {len(registro['correcciones'])}")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except ErrorReferencias as e:
        print(f"ERROR  {e}")
        sys.exit(2)
