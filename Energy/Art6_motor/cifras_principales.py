# -*- coding: utf-8 -*-
"""Cifras principales de la corrida para el README y la documentación, leídas de cifras_finales_producto3.json.

B3 escribe Energy/B2_Output_Art6/cifras_finales_producto3.json con cada cifra, su archivo de origen y el md5 de los
_Output.csv que la producen. Este script toma de ahí un subconjunto, sin recalcular nada, y escribe:
- docs/_generado/cifras_principales.csv (todas las columnas, para quien quiera la tabla como datos);
- docs/_generado/cifras_principales.rst (tabla de la página de cifras principales, con el origen bajo cada cifra);
- la tabla del README.md entre las marcas <!-- cifras:inicio --> y <!-- cifras:fin -->.
Cada salida lleva el md5 del JSON del que salió.

Uso, desde la raíz del repositorio:  python Energy/Art6_motor/cifras_principales.py
"""
import csv
import hashlib
import io
import json
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
JSON = RAIZ / "Energy" / "B2_Output_Art6" / "cifras_finales_producto3.json"
README = RAIZ / "README.md"
GEN = RAIZ / "docs" / "_generado"
SEL = [
    # Primero lo que pregunta quien decide: cuánto se puede transferir, cuánto es vendible, qué es firme y qué
    # margen y sobreventa deja el riesgo. Después, la descomposición y las sensibilidades.
    ("oferta_central_sin_reserva", "Oferta transferible, sin la electromovilidad de flotas en reserva"),
    ("reserva|lista_blanca|intacto", "Lista blanca validada por los expertos, autorizable con el sistema intacto"),
    ("oferta_central_firme", "De esa oferta, línea firme (geotermia de Chachimbiro)"),
    ("margen_2035_C_CLG_prudente", "Margen de 2035 del Escenario C frente a la meta incondicional (1)"),
    ("reserva|lista_blanca|ACTDEM", "Lista blanca autorizable si persiste la demanda de 2026 (1)"),
    ("sobreventa|sin_EN32|anual|CLG_prudente|ACTDEM", "Sobreventa, situación actual 2026 con demanda persistente (1)"),
    ("sobreventa|sin_EN32|anual|CLG_prudente|CCSOLO", "Sobreventa, salida de Coca Codo sola (1)"),
    ("sobreventa|sin_EN32|anual|CLG_prudente|ACT", "Sobreventa, situación actual 2026 con demanda transitoria (1)"),
    ("sobreventa|sin_EN32|anual|CLG_prudente|ANOSEC3", "Sobreventa, un año seco cada tres (1)"),
    ("capa_A_2031_2035", "Capa del Escenario A sobre CONA6"),
    ("capa_B_2031_2035", "Capa del Escenario B sobre A"),
    ("capa_C_2031_2035", "Capa del Escenario C sobre B"),
    ("oferta_central_con_reserva", "Oferta con la electromovilidad de flotas en reserva"),
    ("oferta_con_pisos_CLG_12_10_sin_reserva", "Oferta con los pisos térmicos del Modelo CLG (sensibilidad)"),
    ("puente_CONA6_menos_NDCCON_2031_2035", "Puente CONA6 menos NDCCON (efecto de la calibración propia)"),
    ("puente_CONA6G_menos_NDCCON_2031_2035", "Puente CONA6G menos NDCCON (sin la expansión a gas declarada)"),
    ("margen_2035_CONA6_CLG_prudente", "Margen de 2035 de CONA6 frente a la meta incondicional (1)"),
    ("margen_2035_CONA6_CLG_condicional", "Margen de 2035 de CONA6 con la regla condicional"),
]
NOTA = ("(1) Proyección del Modelo CLG y regla prudente. La sobreventa usa el método anual y la oferta sin la "
        "electromovilidad de flotas en reserva.")


def md5(p):
    return hashlib.md5(Path(p).read_bytes()).hexdigest()


def fmt(v):
    s = "{:,.1f}".format(float(v)).replace(",", " ").replace(".", ",")   # espacio que no se parte
    return s.replace("-", "−")


def fecha(g):
    """'2026-10-13T13:45' -> '13-10-2026, 13:45'; cualquier otro formato se deja como viene."""
    try:
        dia, hora = g.split("T")
        a, m, d = dia.split("-")
        return "%s-%s-%s, %s" % (d, m, a, hora)
    except ValueError:
        return g


def tabla_rst(filas, unidad):
    """list-table con el origen (tabla y clave del JSON) en una línea gris bajo cada cifra."""
    cab = ["Cifra", "Valor", "Periodo"] if unidad else ["Cifra", "Valor", "Unidad", "Periodo"]
    r = [".. list-table:: Cifras principales de la corrida" + (" (%s)" % unidad if unidad else ""),
         "   :header-rows: 1",
         "   :widths: %s" % ("70 14 16" if unidad else "60 13 13 14"),
         "   :class: ea-cifras", "",
         "   * - " + cab[0]] + ["     - " + c for c in cab[1:]]
    for f in filas:
        r += ["   * - " + f["Cifra"], "",
              "       .. rst-class:: ea-origen", "",
              "       ``%s``, clave ``%s``" % (f["Archivo"], f["Clave"]),
              "     - " + f["Valor"]]
        if not unidad:
            r.append("     - " + f["Unidad"])
        r.append("     - " + f["Periodo"])
    return "\n".join(r) + "\n"


def main():
    if not JSON.exists():
        sys.exit("No está %s: corra antes B3 (python Energy/B3_Etapa_Art6.py)" % JSON.relative_to(RAIZ))
    d = json.loads(JSON.read_text(encoding="utf-8"))
    h = md5(JSON)
    por_id = {c["id"]: c for c in d["cifras"]}
    faltan = [i for i, _ in SEL if i not in por_id]
    if faltan:
        sys.exit("cifras_finales_producto3.json no trae: %s" % faltan)
    filas = []
    for i, rotulo in SEL:
        c = por_id[i]
        filas.append({"Cifra": rotulo, "Valor": fmt(c["valor"]), "Unidad": c.get("unidad", ""),
                      "Periodo": c.get("periodo", ""), "Archivo": c.get("archivo", ""), "Clave": i})
    unidades = {f["Unidad"] for f in filas}
    unidad = next(iter(unidades)) if len(unidades) == 1 else ""   # una sola unidad va al título, no a cada fila
    GEN.mkdir(parents=True, exist_ok=True)
    buf = io.StringIO()
    w = csv.DictWriter(buf, fieldnames=list(filas[0]), lineterminator="\n")
    w.writeheader()
    w.writerows([dict(f, Valor=f["Valor"].replace(" ", " ")) for f in filas])
    (GEN / "cifras_principales.csv").write_text(buf.getvalue(), encoding="utf-8")
    origen = "de la corrida del %s (md5 %%s)" % fecha(d.get("generado", ""))
    (GEN / "cifras_principales.rst").write_text(
        tabla_rst(filas, unidad) + "\n.. rst-class:: ea-fuente\n\n"
        "Fuente: ``Energy/B2_Output_Art6/cifras_finales_producto3.json`` " + origen % ("``%s``" % h) + ". Bajo cada "
        "cifra figuran la tabla de ``Energy/B2_Output_Art6`` de la que sale y su clave en el JSON. " + NOTA + "\n",
        encoding="utf-8")
    if README.exists():
        t = README.read_text(encoding="utf-8")
        ini, fin = "<!-- cifras:inicio -->", "<!-- cifras:fin -->"
        if ini in t and fin in t:
            if unidad:
                tabla = ["| Cifra | Valor (%s) | Periodo |" % unidad, "|---|---:|---|"]
                tabla += ["| %s | %s | %s |" % (f["Cifra"], f["Valor"], f["Periodo"]) for f in filas]
            else:
                tabla = ["| Cifra | Valor | Unidad | Periodo |", "|---|---:|---|---|"]
                tabla += ["| %s | %s | %s | %s |" % (f["Cifra"], f["Valor"], f["Unidad"], f["Periodo"]) for f in filas]
            bloque = (ini + "\n" + "\n".join(tabla) + "\n\nFuente: `Energy/B2_Output_Art6/cifras_finales_producto3.json` "
                      + origen % ("`%s`" % h) + ". " + NOTA + "\n" + fin)
            t = t[:t.index(ini)] + bloque + t[t.index(fin) + len(fin):]
            README.write_bytes(t.encode("utf-8"))
    print("cifras principales: %d cifras de cifras_finales_producto3.json (md5 %s)" % (len(filas), h))
    return 0


if __name__ == "__main__":
    sys.exit(main())
