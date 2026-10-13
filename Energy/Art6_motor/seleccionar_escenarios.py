# -*- coding: utf-8 -*-
"""Activa un subconjunto de escenarios de B1 para la corrida rápida y lo deja como estaba después.

B1 resuelve los escenarios con Activated = YES en la hoja Scenarios de Energy/B1_Scenario_Config.xlsx. La corrida
rápida resuelve solo las ocho referencias (BAU, BAU1NDC, NDCINC y NDCCON del Modelo CLG; INCA6, CONA6, INCA6G y CONA6G de
la base corregida) y los escenarios A, B y C; los demás escenarios conservan las salidas versionadas en Executables.

Uso, desde la raíz del repositorio:
    python Energy/Art6_motor/seleccionar_escenarios.py --rapido      guarda una copia del libro y deja activos solo esos 11
    python Energy/Art6_motor/seleccionar_escenarios.py --completo    devuelve el libro exacto (byte a byte) de la copia
    python Energy/Art6_motor/seleccionar_escenarios.py --estado      muestra cuántos escenarios están activos

El cambio se hace en el XML de la hoja Scenarios (columna Activated): las demás hojas no se tocan y el libro no pasa por
openpyxl, que reescribiría todo el archivo.
"""
import argparse
import io
import re
import shutil
import sys
import zipfile
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
LIBRO = RAIZ / "Energy" / "B1_Scenario_Config.xlsx"
COPIA = RAIZ / "Energy" / "_stale_respaldos" / "B1_Scenario_Config.antes_de_corrida_rapida.xlsx"
RAPIDO = ["BAU", "BAU1NDC", "NDCINC", "NDCCON", "INCA6", "CONA6", "INCA6G", "CONA6G", "A", "B", "C"]
NS = "http://schemas.openxmlformats.org/spreadsheetml/2006/main"


def _ruta_hoja(z, nombre):
    wb = z.read("xl/workbook.xml").decode("utf-8")
    rels = z.read("xl/_rels/workbook.xml.rels").decode("utf-8")
    m = re.search(r'<sheet\b[^>]*\bname="%s"[^>]*/>' % re.escape(nombre), wb)
    rid = re.search(r'\br:id="([^"]+)"', m.group(0)).group(1)
    rel = next(r for r in re.findall(r"<Relationship\b[^>]*/>", rels) if 'Id="%s"' % rid in r)
    t = re.search(r'\bTarget="([^"]+)"', rel).group(1)
    return t.lstrip("/") if t.startswith("/") else "xl/" + t


def _compartidas(z):
    if "xl/sharedStrings.xml" not in z.namelist():
        return []
    s = z.read("xl/sharedStrings.xml").decode("utf-8")
    return ["".join(re.findall(r"<t[^>]*>([^<]*)</t>", si)) for si in re.findall(r"<si>(.*?)</si>", s, re.S)]


def _texto(celda, comp):
    t = re.search(r'\bt="([^"]+)"', celda.split(">")[0])
    t = t.group(1) if t else "n"
    if t == "inlineStr":
        return "".join(re.findall(r"<t[^>]*>([^<]*)</t>", celda))
    v = re.search(r"<v>([^<]*)</v>", celda)
    if not v:
        return None
    return comp[int(v.group(1))] if t == "s" else v.group(1)


def leer_activacion(libro=LIBRO):
    """[(fila, nombre, activado)] de la hoja Scenarios."""
    with zipfile.ZipFile(libro) as z:
        comp = _compartidas(z)
        xml = z.read(_ruta_hoja(z, "Scenarios")).decode("utf-8")
    out = []
    for fila in re.findall(r"<row\b[^>]*>.*?</row>", xml, re.S):
        r = int(re.search(r'\br="(\d+)"', fila).group(1))
        celdas = {re.search(r'\br="([A-Z]+)\d+"', c).group(1): c
                  for c in re.findall(r"<c\b[^>]*/>|<c\b[^>]*>.*?</c>", fila, re.S)}
        if r == 1:
            cab = {_texto(c, comp): col for col, c in celdas.items()}
            col_n, col_a = cab["Name"], cab["Activated"]
            continue
        if col_n in celdas:
            out.append((r, _texto(celdas[col_n], comp), _texto(celdas.get(col_a, ""), comp) if col_a in celdas else None))
    return out, col_a


def activar(nombres):
    filas, col_a = leer_activacion()
    con = {n for _, n, _ in filas}
    faltan = [n for n in nombres if n not in con]
    if faltan:
        sys.exit("No están en la hoja Scenarios: %s" % faltan)
    datos = LIBRO.read_bytes()
    zin = zipfile.ZipFile(io.BytesIO(datos))
    ruta = _ruta_hoja(zin, "Scenarios")
    xml = zin.read(ruta).decode("utf-8")
    for r, n, _ in filas:
        valor = "YES" if n in nombres else "NO"
        ref = "%s%d" % (col_a, r)
        patron = re.compile(r'<c\b[^>]*\br="%s"[^>]*?(?:/>|>.*?</c>)' % ref, re.S)
        m = patron.search(xml)
        estilo = re.search(r'\bs="(\d+)"', m.group(0).split(">")[0]) if m else None
        nueva = '<c r="%s"%s t="inlineStr"><is><t>%s</t></is></c>' % (ref, ' s="%s"' % estilo.group(1) if estilo else "",
                                                                     valor)
        if m:
            xml = xml[:m.start()] + nueva + xml[m.end():]
        else:
            sys.exit("La fila %d de Scenarios no tiene celda en la columna Activated" % r)
    salida = io.BytesIO()
    with zipfile.ZipFile(salida, "w") as zout:
        for info in zin.infolist():
            d = xml.encode("utf-8") if info.filename == ruta else zin.read(info.filename)
            zi = zipfile.ZipInfo(info.filename, date_time=info.date_time)
            zi.compress_type = info.compress_type
            zi.external_attr = info.external_attr
            zi.create_system = info.create_system
            zout.writestr(zi, d)
    LIBRO.write_bytes(salida.getvalue())


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--rapido", action="store_true")
    g.add_argument("--completo", action="store_true")
    g.add_argument("--estado", action="store_true")
    a = ap.parse_args()
    if a.estado:
        filas, _ = leer_activacion()
        act = [n for _, n, v in filas if v == "YES"]
        print("%d de %d escenarios activos: %s" % (len(act), len(filas), ", ".join(act)))
        return 0
    if a.rapido:
        if COPIA.exists():
            sys.exit("Ya hay una copia de una corrida rápida anterior (%s): corra antes --completo" % COPIA)
        COPIA.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(LIBRO, COPIA)
        activar(RAPIDO)
        filas, _ = leer_activacion()
        print("Corrida rápida: %d de %d escenarios activos (%s); copia del libro en %s"
              % (sum(v == "YES" for _, _, v in filas), len(filas), ", ".join(RAPIDO), COPIA.relative_to(RAIZ)))
        return 0
    if not COPIA.exists():
        filas, _ = leer_activacion()
        if all(v == "YES" for _, _, v in filas):
            print("El libro ya tiene los %d escenarios activos" % len(filas))
            return 0
        sys.exit("No hay copia de la corrida rápida y el libro no tiene todos los escenarios activos: revise "
                 "Energy/B1_Scenario_Config.xlsx (hoja Scenarios, columna Activated)")
    shutil.copy2(COPIA, LIBRO)
    COPIA.unlink()
    filas, _ = leer_activacion()
    print("Libro restituido: %d de %d escenarios activos" % (sum(v == "YES" for _, _, v in filas), len(filas)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
