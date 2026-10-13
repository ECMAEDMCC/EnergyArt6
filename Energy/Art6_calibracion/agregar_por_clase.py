# -*- coding: utf-8 -*-
"""Parámetros hidroeléctricos agregados por clase del modelo (archivo publicado: parametros_hidro_por_clase.csv).

El repositorio público no lleva filas por central. Los escenarios de riesgo hidrológico (ANOSECO, ANOSEC3), los de Coca
Codo (CCSOLO, CCDER) y el estado ACT anclado a 2026 necesitan tres parámetros por clase hidroeléctrica que se derivan de
datos por central:

- razon_anoseco_2024: razón de caudales de 2024 de la clase (CENACE, Informe Anual 2024, tabla 1.14, p. 73), con las
  series de las centrales de la clase ponderadas por su potencia nominal (capa CENTRALES de ARCONEL);
- participacion_coca_codo_2025: participación de Coca Codo Sinclair en la energía bruta de 2025 de la clase PPHRORAB
  (CENACE, Informe Anual 2025, Parte 1, figuras 1.4 y 1.5, p. 31-32);
- razon_2026_2025: razón observada 2026/2025 de la hidroelectricidad de la clase (CENACE, Información Operativa al
  10-10-2026 e Informe Anual 2025), con las centrales del tablero de CENACE ponderadas por su participación en la
  potencia de la clase (capa CENTRALES) y «Otras Hidro» para el resto; en PPHRORAB, la razón de la parte que no es Coca
  Codo (razon_2026_2025_resto), porque Coca Codo entra por su factor de planta de 2026.

Este script hace la agregación. Solo corre donde están los archivos por central, que se quedan fuera del repositorio:
centrales_clases.csv (extraer_centrales.py, desde CENTRALES.shp), anoseco_cenace_2024.csv, participacion_pphrorab_2025.csv
y act_2026_centrales.csv (situacion_act_2026.py). Las fórmulas son las de generar_escenarios_art6.py en su versión con
archivos por central (13-10-2026), de modo que el generador da los mismos valores con el archivo agregado.

Uso, desde Energy:
    python Art6_calibracion/agregar_por_clase.py --entrada <carpeta con los archivos por central>
    python Art6_calibracion/agregar_por_clase.py --entrada <carpeta> --comprobar    no escribe; sale con 1 si difiere
"""
import argparse
import csv
import io
import sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent
SALIDA = AQUI / "parametros_hidro_por_clase.csv"
NOTA = "derivado de CENTRALES.shp de ARCONEL, uso autorizado"
HIDRO = ["PPHD", "PPHDAMAB", "PPHDAMAM", "PPHDAMAS", "PPHDAMPM", "PPHDAMPS",
         "PPHRORAB", "PPHRORAM", "PPHRORAS", "PPHRORPM", "PPHRORPS"]
# central del modelo -> serie del CENACE (tabla 1.14). Sopladora con la razón del Paute y San Francisco con la de Agoyán;
# Pucará con la de Pisayambo, el embalse que la alimenta (campo de río de la capa)
SERIE = {"Molino": "Paute, ingreso Amaluza", "Mazar": "Mazar", "Sopladora": "Paute, ingreso Amaluza",
         "Coca Codo Sinclair": "Coca Codo Sinclair", "Agoyán": "Agoyán", "San Francisco": "Agoyán",
         "Pucará": "Pisayambo", "Delsitanisagua": "Delsitanisagua",
         "Minas San Francisco": "Minas San Francisco", "Marcel Laniado": "Marcel Laniado"}
# centrales del tablero de CENACE en cada clase (nombre en la tabla de clases: nombre en el tablero)
CLASE_CENTRALES = {"PPHDAMAB": {"Molino": "Paute"}, "PPHDAMAM": {"Mazar": "Mazar", "Agoyán": "Agoyán"},
                   "PPHRORPM": {"San Francisco": "San Francisco", "Minas San Francisco": "Minas San Francisco"},
                   "PPHRORAM": {"Delsitanisagua": "Delsitanisagua"}}
F_SECO = ("CENACE (2025), Informe Anual 2024, tabla 1.14, p. 73; ponderación por potencia nominal de la capa CENTRALES "
          "de ARCONEL")
F_CC = "CENACE, Informe Anual 2025, Parte 1, figuras 1.4 y 1.5, p. 31-32 (S26-008)"
F_ACT = ("CENACE, Información Operativa al 10-10-2026 (SCADA preliminar) e Informe Anual 2025, Parte 1, figura 1.4; "
         "ponderación por participación en la potencia de la clase de la capa CENTRALES de ARCONEL")
COLUMNAS = ["parametro", "clase", "valor", "unidad", "origen", "fuente", "nota"]


def _leer(p):
    return list(csv.DictReader(io.open(p, encoding="utf-8-sig")))


def _enum(xs):
    xs = list(xs)
    return xs[0] if len(xs) == 1 else ", ".join(xs[:-1]) + " y " + xs[-1]


def razones_secas(entrada):
    cen = {r["serie_cenace"]: float(r["razon"]) for r in _leer(entrada / "anoseco_cenace_2024.csv")}
    clases = {}
    for f in _leer(entrada / "centrales_clases.csv"):
        cl, s = f["clase_modelo"], SERIE.get(f["central"])
        if cl and s:
            clases.setdefault(cl, []).append((float(f["potencia_nominal_MW"]), cen[s], f["central"]))
    razon, origen = {}, {}
    for cl, xs in clases.items():
        razon[cl] = sum(p * r for p, r, _ in xs) / sum(p for p, _, _ in xs)
        origen[cl] = ("medida: " + _enum([c for _, _, c in xs]) + " (series del CENACE ponderadas por potencia nominal)"
                      if len(xs) > 1 else "medida: " + xs[0][2] + " (serie del CENACE)")
    razon["PPHDAMAS"], origen["PPHDAMAS"] = cen["Pisayambo"], "heredada: Pisayambo (embalse amazónico pequeño)"
    razon["PPHRORAS"], origen["PPHRORAS"] = razon["PPHDAMAS"], "heredada de PPHDAMAS"
    razon["PPHDAMPS"], origen["PPHDAMPS"] = razon["PPHDAMPM"], "heredada de PPHDAMPM (Toachi Pilatón-Sarapullo sin serie)"
    razon["PPHRORPS"], origen["PPHRORPS"] = razon["PPHRORPM"], "heredada de PPHRORPM"
    rows = _leer(entrada / "anoseco_cenace_2024.csv")
    razon["PPHD"] = sum(float(r["caudal_2024_m3s"]) for r in rows) / sum(float(r["caudal_historico_m3s"]) for r in rows)
    origen["PPHD"] = "promedio nacional de las 8 series, ponderado por caudal"
    faltan = [c for c in HIDRO if c not in razon]
    if faltan:
        sys.exit(f"sin razón de año seco para {faltan}")
    return {c: round(razon[c], 4) for c in HIDRO}, origen


def participacion_coca_codo(entrada):
    f = {r["central"]: float(r["produccion_bruta_2025_GWh"]) for r in _leer(entrada / "participacion_pphrorab_2025.csv")}
    return f["Coca Codo Sinclair"] / (f["Coca Codo Sinclair"] + f["Sopladora"])


def razones_act(entrada):
    raz = {r["central_tablero"]: float(r["razon_2026_2025"]) for r in _leer(entrada / "act_2026_centrales.csv")}
    part = {r["central"]: float(r["participacion_en_clase_2025"]) for r in _leer(entrada / "centrales_clases.csv")
            if r["clase_modelo"] and r["participacion_en_clase_2025"]}
    r_otras = raz["Otras Hidro"]
    out = {}
    for cl in HIDRO:
        if cl == "PPHRORAB":
            out[cl] = (raz["Sopladora"], "parte de la clase que no es Coca Codo (Sopladora), razón del tablero de CENACE")
            continue
        cen = CLASE_CENTRALES.get(cl, {})
        w = {c: part[c] for c in cen}
        resto = max(0.0, 1.0 - sum(w.values()))
        r_cl = sum(w[c] * raz[cen[c]] for c in cen) + resto * r_otras
        if cen:
            origen = (_enum(list(cen)) + " (razón del tablero de CENACE ponderada por su participación en la potencia de "
                      "la clase)" + (" y resto con Otras Hidro (%.4f)" % r_otras if resto > 0 else ""))
        else:
            origen = "Otras Hidro (%.4f)" % r_otras
        out[cl] = (r_cl, origen)
    return out


def filas(entrada):
    razon, origen = razones_secas(entrada)
    act = razones_act(entrada)
    out = [{"parametro": "razon_anoseco_2024", "clase": c, "valor": repr(razon[c]), "unidad": "razón",
            "origen": origen[c], "fuente": F_SECO, "nota": NOTA} for c in HIDRO]
    out.append({"parametro": "participacion_coca_codo_2025", "clase": "PPHRORAB",
                "valor": repr(participacion_coca_codo(entrada)), "unidad": "fracción de la energía bruta de la clase",
                "origen": "Coca Codo Sinclair sobre Coca Codo Sinclair y Sopladora", "fuente": F_CC, "nota": NOTA})
    for c in HIDRO:
        r, o = act[c]
        out.append({"parametro": "razon_2026_2025_resto" if c == "PPHRORAB" else "razon_2026_2025", "clase": c,
                    "valor": repr(r), "unidad": "razón", "origen": o, "fuente": F_ACT, "nota": NOTA})
    return out


def a_texto(fs):
    buf = io.StringIO()
    w = csv.DictWriter(buf, fieldnames=COLUMNAS, lineterminator="\n")
    w.writeheader()
    w.writerows(fs)
    return buf.getvalue()


def leer(ruta=SALIDA):
    """{(parametro, clase): (valor, origen)} del archivo agregado (lo usa generar_escenarios_art6.py)."""
    return {(r["parametro"], r["clase"]): (float(r["valor"]), r["origen"]) for r in _leer(ruta)}


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--entrada", required=True, help="carpeta con los archivos por central (fuera del repositorio)")
    ap.add_argument("--salida", default=str(SALIDA))
    ap.add_argument("--comprobar", action="store_true")
    a = ap.parse_args()
    texto = a_texto(filas(Path(a.entrada)))
    salida = Path(a.salida)
    if a.comprobar:
        igual = salida.exists() and salida.read_text(encoding="utf-8") == texto
        print(f"{salida.name} coincide" if igual else f"{salida.name} difiere")
        return 0 if igual else 1
    salida.write_bytes(texto.encode("utf-8"))
    print(f"{salida.name}: {texto.count(chr(10)) - 1} filas por clase")
    return 0


if __name__ == "__main__":
    sys.exit(main())
