# -*- coding: utf-8 -*-
"""Datos observados de 2026 para el estado ACT del Artículo 6 (decisión del 13-10-2026).

Uso, desde ECU_NDC/Energy:
    python Art6_calibracion/situacion_act_2026.py              escribe act_2026_observado.csv y act_2026_centrales.csv
    python Art6_calibracion/situacion_act_2026.py --comprobar  no escribe; sale con 1 si el disco no coincide

Cada valor se lee del documento primario guardado en la carpeta local de fuentes (ART6_FUENTES_2026) (CENACE y XM)
y no de la nota de trabajo: la nota (situacion_2026_datos.csv) solo da el identificador S26-nnn con que se cruza. Si un
documento no trae el valor esperado, el script falla.

Qué lee:
1. Consumo de energía eléctrica mensual (CENACE, Informe Ejecutivo de Gestión, sección 4): enero a agosto de 2025 del
   informe de diciembre de 2025 y enero a agosto de 2026 del informe de agosto de 2026. Su cociente es el crecimiento de
   la demanda de 2026 (S26-041).
2. Producción hidroeléctrica neta mensual (CENACE, indicadores.xlsx, hoja datos, enero a julio; Informe Ejecutivo,
   sección 2, agosto). El libro y el informe coinciden en agosto de 2025 (2.320,03 GWh) y julio de 2025 (2.335,61), así
   que el período enero a agosto se arma con las dos fuentes (S26-038 da enero a julio).
3. Producción hidroeléctrica bruta por central de 2025 (CENACE, Informe Anual 2025, Parte 1, figura 1.4, p. 31; S26-008)
   y acumulada de 2026 al 10 de octubre por central (CENACE, Información Operativa, pestaña Acumulada anual, SCADA
   preliminar; S26-040), con la producción de Coca Codo del 1 al 10 de octubre (pestaña Acumulada mensual).
4. Coca Codo Sinclair (Informe Anual 2025, Parte 1; S26-009): potencia efectiva de 1.500 MW y factor de planta de 2024
   (55.29 %) del texto de la p. 36; factor de planta de 2025 de la tabla 1.7, p. 37 (58.63 %; el texto de la p. 36 lo
   redondea a 58,60 %). Ningún valor queda escrito a mano: si el informe no los trae, el script falla.
5. Importación desde Colombia: enero a agosto de 2026 (CENACE, Informe Ejecutivo de agosto de 2026, sección 1) y diaria
   de septiembre (XM, Exportaciones kWh 2026), para lo importado antes del 07-09-2026 (S26-043 y S26-044); 2025 completo
   del Informe Anual 2025, Parte 1, p. 19 (S26-020), contrastado mes a mes con el Informe Ejecutivo de diciembre de 2025
   y con XM, Exportaciones kWh 2025.
6. Participación térmica observada (contraste) con la importación en el denominador, el mismo perímetro que el modelo
   (térmica / (hidro + térmica + ERNC + importación)): enero a agosto de 2026 con las fuentes de los puntos 2 y 5; 2025
   con indicadores.xlsx y la importación del punto 5; acumulada al 10 de octubre de 2026 del tablero de CENACE (S26-039).
   Corrección del 13-10-2026 tras la verificación independiente del paso 15: hasta entonces enero a agosto de 2026 se
   comparaba sin importación (20,68 % en lugar de 20,50 %); las claves *_sin_importacion quedan para la trazabilidad.
"""
import argparse
import os
import csv
import hashlib
import io
import re
import sys
from pathlib import Path

import pandas as pd

AQUI = Path(__file__).resolve().parent
# documentos públicos de CENACE y XM guardados localmente (no se distribuyen; ver el LEEME); carpeta en la variable de
# entorno ART6_FUENTES_2026
FUENTES = Path(os.environ.get("ART6_FUENTES_2026", "Fuentes/Situacion_2026"))
SITUACION = FUENTES / "situacion_2026_datos.csv"
INF_EJ = lambda m: FUENTES / f"CENACE_Informe_Ejecutivo_Gestion_{m}.pdf"
INDICADORES = FUENTES / "CENACE_Indicadores_energia_neta_por_fuente_mensual_2010-2026-07.xlsx"
ANUAL_2025 = FUENTES / "CENACE_Informe_Anual_2025_Parte1_2026-04.pdf"
TABLERO = FUENTES / "CENACE_Informacion_Operativa_tablero_2026-10-12.html"
XM_2026 = FUENTES / "XM_Exportaciones_kWh_2026_corte2026-10-11.xlsx"
XM_2025 = FUENTES / "XM_Exportaciones_kWh_2025_corte2026-10-06.xlsx"
SALIDA = AQUI / "act_2026_observado.csv"
SALIDA_CENTRALES = AQUI / "act_2026_centrales.csv"
MESES = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto"]
CORTE_IMPORTACION = "2026-09-07"            # desde esta fecha la exportación de Colombia cae a generación de seguridad
DIAS_HASTA_10_OCT = 283                    # 1 de enero a 10 de octubre de 2026 (corte del tablero, que tablero() comprueba)
DIAS_RESTO_2026 = 365 - DIAS_HASTA_10_OCT  # 11 de octubre a 31 de diciembre
# la potencia efectiva de Coca Codo y sus factores de planta de 2024 y 2025 se leen del Informe Anual 2025 (coca_codo())
# producción bruta hidroeléctrica por central, 2025 (Informe Anual 2025, Parte 1, figura 1.4, p. 31): el texto extraído
# del PDF desordena rótulos y valores, así que cada valor se comprueba en el texto y su suma contra el total de la figura
# 1.5 (28.031,39 GWh); los nombres del tablero de 2026 se cruzan aquí con los de la figura
HIDRO_2025 = {"Coca Codo": ("C. H. COCA CODO SINCLAIR", "7.695,99"), "Paute": ("C. H. PAUTE", "5.542,05"),
              "Sopladora": ("C. H. SOPLADORA", "2.884,03"), "Minas San Francisco": ("C. H. MINAS SAN FRANCISCO", "1.403,44"),
              "San Francisco": ("C. H. SAN FRANCISCO", "1.193,30"), "Agoyán": ("C. H. AGOYÁN", "940,49"),
              "Delsitanisagua": ("C. H. DELSITANISAGUA", "617,79"), "Mazar": ("C. H. MAZAR", "553,77")}
OTRAS_2025 = {"C. H. MARCEL LANIADO DE WIND": "1.054,26", "C. H. SAN BARTOLO": "431,93", "C. H. ABANICO": "304,22",
              "C. H. PUCARÁ": "247,01", "C. H. MANDURIACU": "181,19", "C. H. CUMBAYÁ": "149,82", "C. H. CALOPE": "91,03",
              "OTRAS C. HIDROELÉCTRICAS": "4.741,06"}
TOTAL_HIDRO_2025 = "28.031,39"


class ErrorDatos(Exception):
    pass


def md5(p):
    return hashlib.md5(Path(p).read_bytes()).hexdigest()


def num(s):
    """Número con coma decimal y punto de miles (o el formato inverso de algunos informes de 2025)."""
    s = str(s).strip()
    if re.fullmatch(r"\d{1,3}(,\d{3})+\.\d{1,2}", s):        # 2,335.61 (informe de julio de 2025)
        return float(s.replace(",", ""))
    return float(s.replace(".", "").replace(",", "."))


def texto_pdf(ruta):
    import pymupdf
    with pymupdf.open(ruta) as d:
        return [p.get_text() for p in d], [p.get_text("words") for p in d]


def filas_por_altura(palabras):
    """Agrupa las palabras de una página por línea (altura redondeada)."""
    filas = {}
    for w in palabras:
        filas.setdefault(round(w[1] / 3), []).append((w[0], w[4]))
    return {y: [t for _, t in sorted(v)] for y, v in sorted(filas.items())}


def consumo_mensual(mes_informe):
    """{(año, mes): GWh} de la sección 4 (consumo de energía eléctrica) del Informe Ejecutivo de Gestión."""
    textos, palabras = texto_pdf(INF_EJ(mes_informe))
    for t, ws in zip(textos, palabras):
        if "4. Consumo de energía eléctrica y exportaciones" not in t:
            continue
        filas = filas_por_altura(ws)
        cab = next(v for v in filas.values() if sum(1 for x in v if re.fullmatch(r"(Ene|Feb|Mar|Abr|May|Jun|Jul|Ago|Sep|"
                                                                                  r"Oct|Nov|Dic)\.", x)) == 13)
        meses = [(x, y) for x, y in zip(cab[0::2], cab[1::2])]
        val = next(v for v in filas.values() if v and v[0].upper().startswith("CONSUMO") and len(v) >= 15)
        nums = [num(x) for x in val if re.fullmatch(r"[\d.,]+", x)]
        if len(nums) != 13:
            raise ErrorDatos(f"Informe Ejecutivo {mes_informe}: la fila de consumo no trae 13 meses")
        abre = {"Ene": 1, "Feb": 2, "Mar": 3, "Abr": 4, "May": 5, "Jun": 6, "Jul": 7, "Ago": 8, "Sep": 9, "Oct": 10,
                "Nov": 11, "Dic": 12}
        return {(2000 + int(a), abre[m.rstrip(".")]): v for (m, a), v in zip(meses, nums)}, \
            textos.index(t) + 1
    raise ErrorDatos(f"Informe Ejecutivo {mes_informe}: sin sección 4")


def produccion_mes(mes_informe, rotulo):
    """GWh del mes del informe en la sección 2 (composición de la producción neta)."""
    textos, _ = texto_pdf(INF_EJ(mes_informe))
    for k, t in enumerate(textos):
        if "Composición de la producción neta" in t and rotulo in t:
            lineas = [x.strip() for x in t.splitlines()]
            i = lineas.index(rotulo)
            for x in lineas[i + 1:i + 4]:
                if re.fullmatch(r"[\d.,]+", x):
                    return num(x), k + 1
    raise ErrorDatos(f"Informe Ejecutivo {mes_informe}: sin {rotulo} en la sección 2")


def importacion_mensual(mes_informe):
    """{(año, mes): GWh} de importación desde Colombia de la sección 1 del Informe Ejecutivo."""
    textos, palabras = texto_pdf(INF_EJ(mes_informe))
    for t, ws in zip(textos, palabras):
        if "1. Producción neta de energía eléctrica" not in t:
            continue
        filas = filas_por_altura(ws)
        ys = sorted(filas)
        cab = next(v for v in filas.values() if sum(1 for x in v if x.endswith(".")) >= 13)
        meses = [(x, y) for x, y in zip(cab[cab.index(next(x for x in cab if x.endswith("."))):][0::2],
                                        cab[cab.index(next(x for x in cab if x.endswith("."))):][1::2])]
        y_cab = next(y for y in ys if filas[y] is cab)
        imp = next(filas[y] for y in ys if y > y_cab and len([x for x in filas[y] if re.fullmatch(r"[\d.,]+", x)]) == 13)
        nums = [num(x) for x in imp if re.fullmatch(r"[\d.,]+", x)]
        abre = {"Ene": 1, "Feb": 2, "Mar": 3, "Abr": 4, "May": 5, "Jun": 6, "Jul": 7, "Ago": 8, "Sep": 9, "Oct": 10,
                "Nov": 11, "Dic": 12}
        return {(2000 + int(a), abre[m.rstrip(".")]): v for (m, a), v in zip(meses, nums)}, textos.index(t) + 1
    raise ErrorDatos(f"Informe Ejecutivo {mes_informe}: sin sección 1")


def tablero():
    """Acumulados del tablero de CENACE: (encabezado anual, detalle anual por central en GWh, detalle mensual en MWh)."""
    t = TABLERO.read_text(encoding="utf-8", errors="replace")
    plano = lambda a, b: re.sub(r"\s+", " ", re.sub("<[^>]+>", " ", re.sub(r"<style.*?</style>", "", t[a:b], flags=re.S)))
    i_mes, i_anio = t.index("INFORMACIÓN OPERATIVA MENSUAL"), t.index("INFORMACIÓN OPERATIVA ANUAL")
    enc_anio = plano(i_anio, t.index("DETALLE DE PRODUCCIÓN", i_anio))
    enc_mes = plano(i_mes, t.index("DETALLE DE PRODUCCIÓN", i_mes))
    if "2026 (hasta el día 10 de octubre)" not in enc_anio or "Octubre de 2026 (hasta el día 10)" not in enc_mes:
        raise ErrorDatos("tablero de CENACE: el corte no es el 10 de octubre de 2026")

    def detalle(desde):
        """Barras del primer gráfico con Coca Codo después del encabezado de la pestaña (el primero es la dona)."""
        import json as _json
        k = t.index("DETALLE DE PRODUCCIÓN", desde)
        while True:
            k = t.index("Plotly.newPlot", k + 1)
            fin = t.index("</script>", k)
            if '"name":"Coca Codo"' in t[k:fin]:
                break
        barras = re.findall(r'"name":"([^"]+)","showlegend":true,"width":0\.4,"x":\[1\],"y":\[([\d.]+)\]', t[k:fin])
        return {_json.loads('"%s"' % n).strip(): float(v) for n, v in barras}

    def campo(enc, rot):
        m = re.search(rot + r" ([\d ]+?)(?= [A-ZÁÉÍÓÚ])", enc + " FIN")
        return float(m.group(1).replace(" ", ""))
    cab = {k: campo(enc_anio, k) for k in ("PRODUCCIÓN TOTAL", "IMPORTACIÓN", "HIDRÁULICA", "TÉRMICA",
                                           "R. NO CONVENCIONAL")}
    # la producción total del tablero incluye la importación (cierra con sus componentes salvo redondeo a 1 GWh)
    partes = cab["HIDRÁULICA"] + cab["TÉRMICA"] + cab["R. NO CONVENCIONAL"] + cab["IMPORTACIÓN"]
    if abs(cab["PRODUCCIÓN TOTAL"] - partes) > 2.0:
        raise ErrorDatos(f"tablero: la producción total ({cab['PRODUCCIÓN TOTAL']}) no es hidro + térmica + no "
                         f"convencional + importación ({partes})")
    return cab, detalle(i_anio), detalle(i_mes)


def pct(s):
    """Porcentaje del informe (58.63 % en la tabla 1.7, 58,60 % en el texto) como fracción."""
    return float(str(s).replace(",", ".")) / 100.0


def coca_codo(txt25):
    """Coca Codo Sinclair en el Informe Anual 2025, Parte 1: potencia efectiva y factor de planta de 2024 del texto de la
    p. 36 («el factor de planta fue de 58,60 % (similar al alcanzado el año anterior – 55.29%) considerando una potencia
    efectiva de 1.500 MW») y factor de planta de 2025 de la tabla 1.7 (fila COCA CODO SINCLAIR, p. 37). Devuelve
    (potencia MW, fp 2024, fp 2025 de la tabla, fp 2025 del texto, página del texto, página de la tabla)."""
    p_txt = next((k for k, t in enumerate(txt25) if "Coca Codo Sinclair que es la de mayor potencia" in t), None)
    if p_txt is None:
        raise ErrorDatos("Informe Anual 2025: no aparece el párrafo de Coca Codo Sinclair (p. 36)")
    t = re.sub(r"\s+", " ", txt25[p_txt])
    m = re.search(r"Coca Codo Sinclair que es la de mayor potencia del pa\w+, el factor de planta fue de "
                  r"(\d{2}[.,]\d{2}) ?% \(similar al alcanzado el a\w+ anterior\W+(\d{2}[.,]\d{2}) ?%\) considerando "
                  r"una potencia efectiva de ([\d.]+) MW", t)
    if not m:
        raise ErrorDatos(f"Informe Anual 2025, p. {p_txt + 1}: no se leen el factor de planta ni la potencia de Coca Codo")
    fp25_txt, fp24, mw = pct(m.group(1)), pct(m.group(2)), num(m.group(3))
    p_tab, fp25 = None, None
    for k in range(p_txt, min(p_txt + 3, len(txt25))):
        lineas = [x.strip() for x in txt25[k].splitlines() if x.strip()]
        if "% FACTOR DE PLANTA PROMEDIO ORDENADOS" in lineas and "COCA CODO SINCLAIR" in lineas:
            v = lineas[lineas.index("COCA CODO SINCLAIR") + 1]
            if not re.fullmatch(r"\d{1,3}[.,]\d{2}%", v):
                raise ErrorDatos(f"Informe Anual 2025, tabla 1.7, p. {k + 1}: la fila de Coca Codo no trae un porcentaje")
            p_tab, fp25 = k, pct(v.rstrip("%"))
            break
    if fp25 is None:
        raise ErrorDatos("Informe Anual 2025: la tabla 1.7 no trae la fila COCA CODO SINCLAIR")
    if abs(fp25 - fp25_txt) > 0.005 or not 1000.0 <= mw <= 2000.0:
        raise ErrorDatos(f"Informe Anual 2025: tabla ({fp25}) y texto ({fp25_txt}) de Coca Codo no concuerdan o la "
                         f"potencia ({mw} MW) es inverosímil")
    return mw, fp24, fp25, fp25_txt, p_txt, p_tab


def importacion_2025(txt25):
    """Importación desde Colombia de 2025 en GWh: Informe Anual 2025, Parte 1, cuadro de cifras de la p. 19
    («Importaciones de energía / GWh / 624,35»). Devuelve (GWh, página)."""
    for k, t in enumerate(txt25):
        lineas = [x.strip() for x in t.splitlines() if x.strip()]
        if "Importaciones de energía" in lineas and "Producción neta total de energía" in lineas:
            i = lineas.index("Importaciones de energía")
            if lineas[i + 1] == "GWh" and re.fullmatch(r"[\d.]+,\d{2}", lineas[i + 2]):
                return num(lineas[i + 2]), k
    raise ErrorDatos("Informe Anual 2025: el cuadro de cifras no trae la importación de 2025")


def xm_mensual(ruta):
    """{mes: GWh} de un libro de XM, Exportaciones (kWh), con todos sus enlaces."""
    x = pd.read_excel(ruta, header=2)
    x = x[pd.to_datetime(x["Fecha"], errors="coerce").notna()].copy()
    x["Fecha"] = pd.to_datetime(x["Fecha"])
    horas = [c for c in x.columns if c not in ("Fecha", "Enlace", "Versión")]
    dia = x.assign(kWh=x[horas].astype(float).sum(axis=1)).groupby("Fecha").kWh.sum() / 1e6
    return dia, dia.groupby(dia.index.month).sum()


def observado():
    filas, centrales = [], []

    def dato(clave, valor, unidad, periodo, fuente, ubicacion, archivos, sid="", nota=""):
        filas.append({"clave": clave, "valor": round(float(valor), 6), "unidad": unidad, "periodo": periodo,
                      "fuente": fuente, "ubicacion": ubicacion,
                      "archivos": " | ".join(Path(a).name for a in archivos),
                      "md5": " | ".join(md5(a) for a in archivos), "id_situacion": sid, "nota": nota})

    sit = {ln.split(";", 1)[0]: ln for ln in SITUACION.read_text(encoding="utf-8-sig").splitlines()}

    # 1. demanda: consumo de enero a agosto, 2025 y 2026
    c25, p25 = consumo_mensual("2025-12")
    c26, p26 = consumo_mensual("2026-08")
    c25b, _ = consumo_mensual("2025-08")
    ene_ago_25 = sum(c25[(2025, m)] for m in range(1, 9))
    ene_ago_26 = sum(c26[(2026, m)] for m in range(1, 9))
    if any(abs(c25[(2025, m)] - c25b[(2025, m)]) > 0.5 for m in range(1, 9)):
        raise ErrorDatos("consumo 2025: los informes de agosto y diciembre de 2025 no coinciden")
    if "24.391" not in sit["S26-041"] or "21.638" not in sit["S26-041"]:
        raise ErrorDatos("S26-041 no trae 24.391 y 21.638 GWh")
    fte = "CENACE, Informe Ejecutivo de Gestión, sección 4 (consumo de energía eléctrica)"
    dato("consumo_ene_ago_2025_GWh", ene_ago_25, "GWh", "ene-ago 2025", fte,
         f"informe de diciembre de 2025, p. {p25} (coincide con el de agosto de 2025)",
         [INF_EJ("2025-12"), INF_EJ("2025-08")], "S26-041")
    dato("consumo_ene_ago_2026_GWh", ene_ago_26, "GWh", "ene-ago 2026", fte, f"informe de agosto de 2026, p. {p26}",
         [INF_EJ("2026-08")], "S26-041")
    dato("crecimiento_demanda_2026", ene_ago_26 / ene_ago_25, "razón", "ene-ago 2026 / ene-ago 2025",
         "derivación propia sobre las dos filas anteriores", "", [INF_EJ("2025-12"), INF_EJ("2026-08")], "S26-041",
         "supuesto: el crecimiento de enero a agosto vale para el año completo")
    anio_25 = sum(c25[(2025, m)] for m in range(1, 13))
    dato("consumo_2025_GWh", anio_25, "GWh", "2025", fte, f"informe de diciembre de 2025, p. {p25}",
         [INF_EJ("2025-12")], "S26-041", "contraste")

    # 2. hidroelectricidad neta, enero a agosto
    d = pd.read_excel(INDICADORES, sheet_name="datos")
    d = d[d["Año"].isin([2025, 2026]) & d["Mes"].isin(MESES[:7])]
    h = d.groupby("Año")["Hidroeléctrica"].sum()
    te = d.groupby("Año")["Térmica"].sum()
    to = d.groupby("Año")["TOTAL"].sum()
    if len(d) != 14:
        raise ErrorDatos("indicadores.xlsx no trae enero a julio de 2025 y 2026")
    h_ago25, ph25 = produccion_mes("2025-08", "PRODUCCIÓN HIDRÁULICA")
    h_ago26, ph26 = produccion_mes("2026-08", "PRODUCCIÓN HIDRÁULICA")
    t_ago26, _ = produccion_mes("2026-08", "PRODUCCIÓN TÉRMICA")
    total_ago26, _ = produccion_mes("2026-08", "TOTAL")
    lib_ago25 = float(pd.read_excel(INDICADORES, sheet_name="datos").query("`Año` == 2025 and Mes == 'Agosto'")
                      ["Hidroeléctrica"].iloc[0])
    if abs(lib_ago25 - h_ago25) > 0.05:
        raise ErrorDatos("agosto de 2025: indicadores.xlsx y el Informe Ejecutivo difieren: perímetros distintos")
    if abs(h[2026] / h[2025] - 1.0429) > 5e-5:
        raise ErrorDatos("indicadores.xlsx: la hidro de enero a julio no da +4,29 % (S26-038)")
    fte2 = "CENACE, indicadores.xlsx (hoja datos, enero a julio) e Informe Ejecutivo de Gestión, sección 2 (agosto)"
    arch2 = [INDICADORES, INF_EJ("2025-08"), INF_EJ("2026-08")]
    dato("hidro_ene_jul_razon_2026_2025", h[2026] / h[2025], "razón", "ene-jul", "CENACE, indicadores.xlsx, hoja datos",
         "filas de enero a julio de 2025 y 2026", [INDICADORES], "S26-038", "valor citado en la revisión (+4,29 %)")
    dato("hidro_ene_ago_2025_GWh", h[2025] + h_ago25, "GWh", "ene-ago 2025", fte2,
         f"agosto: informe de agosto de 2025, p. {ph25}", arch2, "S26-038")
    dato("hidro_ene_ago_2026_GWh", h[2026] + h_ago26, "GWh", "ene-ago 2026", fte2,
         f"agosto: informe de agosto de 2026, p. {ph26}", arch2, "S26-038")
    r_hidro = (h[2026] + h_ago26) / (h[2025] + h_ago25)
    dato("hidro_ene_ago_razon_2026_2025", r_hidro, "razón", "ene-ago 2026 / ene-ago 2025",
         "derivación propia sobre las dos filas anteriores", "mismo período que la demanda", arch2, "S26-038",
         "se usa en lugar de enero a julio para que demanda e hidrología cubran los mismos meses")
    # la producción neta de la sección 2 y del libro no trae la importación: TOTAL = hidro + térmica + no convencional
    nc_ago26 = total_ago26 - h_ago26 - t_ago26
    if not 0.0 <= nc_ago26 <= 200.0:
        raise ErrorDatos(f"Informe Ejecutivo de agosto de 2026, sección 2: el total menos hidro y térmica ({nc_ago26:.2f} "
                         "GWh) no es la no convencional: el total podría traer la importación")

    # 3. centrales: 2025 (figura 1.4) y 2026 (tablero)
    txt25, _ = texto_pdf(ANUAL_2025)
    # la página de la figura (no la del índice): trae el pie y los valores
    p31 = next(k for k, t in enumerate(txt25) if re.search(r"Figura 1\.\s+4 Producción bruta hidroeléctrica anual", t)
               and "PRODUCCIÓN BRUTA POR CENTRALES" in t)
    plano25 = txt25[p31] + txt25[p31 + 1]
    # la figura lista los 16 valores y después los 16 rótulos en el mismo orden: se emparejan y se comparan con la tabla
    lineas = [x.strip() for x in txt25[p31].splitlines() if x.strip()]
    i0 = next(i for i, x in enumerate(lineas) if re.fullmatch(r"[\d.]+,\d{2}", x))
    vals = lineas[i0:i0 + 16]
    rots, buf = [], ""
    for x in lineas[i0 + 16:]:
        if x == "GWh":
            break
        buf = (buf + " " + x).strip()
        if not buf.endswith(("COCA CODO", "OTRAS C.", "MARCEL LANIADO", "MINAS SAN")):
            rots.append(buf)
            buf = ""
    leido = dict(zip(rots, vals))
    esperado = {rot: v for rot, v in HIDRO_2025.values()} | OTRAS_2025
    if leido != esperado:
        raise ErrorDatos(f"Informe Anual 2025, figura 1.4: rótulos y valores no coinciden: {leido}")
    tot25 = sum(num(v) for _, v in HIDRO_2025.values()) + sum(num(v) for v in OTRAS_2025.values())
    if abs(tot25 - num(TOTAL_HIDRO_2025)) > 0.05 or TOTAL_HIDRO_2025 not in plano25:
        raise ErrorDatos("Informe Anual 2025: las centrales no suman 28.031,39 GWh")
    cab, anual, mensual = tablero()
    tot26 = sum(anual.values())
    if abs(tot26 - cab["HIDRÁULICA"]) > 1.0 or set(anual) != set(HIDRO_2025) | {"Otras Hidro"}:
        raise ErrorDatos(f"tablero: el detalle anual por central no cierra con la hidráulica ({tot26} frente a "
                         f"{cab['HIDRÁULICA']}) o cambió de centrales: {sorted(anual)}")
    for nom in list(HIDRO_2025) + ["Otras Hidro"]:
        a25 = num(HIDRO_2025[nom][1]) if nom in HIDRO_2025 else sum(num(v) for v in OTRAS_2025.values())
        y26 = anual[nom]
        r = (y26 / tot26) / (a25 / tot25) * r_hidro
        centrales.append({"central_tablero": nom, "central_informe_2025": HIDRO_2025[nom][0] if nom in HIDRO_2025
                          else "resto de la figura 1.4 (" + ", ".join(OTRAS_2025) + ")",
                          "produccion_2025_GWh": round(a25, 2), "participacion_2025": round(a25 / tot25, 6),
                          "acumulado_2026_al_10_oct_GWh": y26, "participacion_2026_al_10_oct": round(y26 / tot26, 6),
                          "razon_2026_2025": round(r, 6),
                          "regla": "razón de la participación en la hidro (2026 al 10-10 sobre 2025) por la razón de la "
                                   "hidro total de enero a agosto (%.6f)" % r_hidro})
    if "S26-008" not in sit or "7.695,99" not in sit["S26-008"] or "6.563" not in sit["S26-040"]:
        raise ErrorDatos("S26-008 o S26-040 no traen los valores de Coca Codo")
    dato("hidro_total_2025_GWh", tot25, "GWh", "2025", "CENACE, Informe Anual 2025, Parte 1, figuras 1.4 y 1.5",
         f"p. {p31 + 1}-{p31 + 2}", [ANUAL_2025], "S26-008")
    dato("hidro_acumulada_2026_al_10_oct_GWh", tot26, "GWh", "01-01-2026 a 10-10-2026",
         "CENACE, Información Operativa, pestaña Acumulada anual (SCADA preliminar)", "detalle de producción por central",
         [TABLERO], "S26-039 y S26-040")
    # 4. Coca Codo: factor de planta de 2026 estimado y observados de 2024-2025, con la potencia efectiva del informe
    CC_MW, fp24, fp25, fp25_txt, p36, p37 = coca_codo(txt25)
    mw_txt = "{:,.0f}".format(CC_MW).replace(",", ".") + " MW"
    cc26, cc_oct = anual["Coca Codo"], mensual["Coca Codo"] / 1000.0
    fp_ytd = cc26 / (CC_MW * 24 * DIAS_HASTA_10_OCT / 1000.0)
    fp_oct = cc_oct / (CC_MW * 24 * 10 / 1000.0)
    fp26 = (cc26 + cc_oct / 10.0 * DIAS_RESTO_2026) / (CC_MW * 8.76)
    if not (0.55 <= fp26 <= 0.64):
        raise ErrorDatos(f"factor de planta de Coca Codo de 2026 ({fp26:.4f}) fuera de la banda 0,55-0,64")
    for anio, v in ((2024, fp24), (2025, fp25)):
        if ("%.2f %%" % (100.0 * v)).replace(".", ",") not in sit["S26-009"]:
            raise ErrorDatos(f"S26-009 no trae el factor de planta de Coca Codo de {anio} leído del informe ({v:.4f})")
    dato("cc_potencia_efectiva_MW", CC_MW, "MW", "2025", "CENACE, Informe Anual 2025, Parte 1, texto",
         f"p. {p36 + 1} («considerando una potencia efectiva de {mw_txt}»)", [ANUAL_2025], "S26-009",
         "denominador de los factores de planta de Coca Codo de 2026")
    dato("cc_fp_2024", fp24, "fracción", "2024", "CENACE, Informe Anual 2025, Parte 1, texto", f"p. {p36 + 1}",
         [ANUAL_2025], "S26-009")
    dato("cc_fp_2025", fp25, "fracción", "2025", "CENACE, Informe Anual 2025, Parte 1, tabla 1.7, fila COCA CODO SINCLAIR",
         f"p. {p37 + 1}; el texto de la p. {p36 + 1} lo redondea a "
         + ("%.2f %%" % (100.0 * fp25_txt)).replace(".", ","), [ANUAL_2025], "S26-009")
    dato("cc_acumulado_2026_al_10_oct_GWh", cc26, "GWh", "01-01-2026 a 10-10-2026",
         "CENACE, Información Operativa, pestaña Acumulada anual (SCADA preliminar)", "barra Coca Codo", [TABLERO], "S26-040")
    dato("cc_oct_1_10_2026_GWh", cc_oct, "GWh", "01-10-2026 a 10-10-2026",
         "CENACE, Información Operativa, pestaña Acumulada mensual (SCADA preliminar)", "barra Coca Codo", [TABLERO],
         "S26-040")
    dato("cc_fp_2026_al_10_oct", fp_ytd, "fracción", "01-01-2026 a 10-10-2026", "derivación propia", f"{mw_txt}, {DIAS_HASTA_10_OCT} días",
         [TABLERO], "S26-040", "64,4 % en la nota")
    dato("cc_fp_oct_1_10_2026", fp_oct, "fracción", "01-10-2026 a 10-10-2026", "derivación propia", f"{mw_txt}, 10 días",
         [TABLERO], "S26-040", "57,5 % en la nota")
    dato("cc_fp_2026_estimado", fp26, "fracción", "2026",
         f"derivación propia: acumulado al 10-10 más {DIAS_RESTO_2026} días al ritmo del 1 al 10 de octubre, sobre {mw_txt} x 8.760 h",
         "", [TABLERO], "S26-040", "supuesto: el resto del año sigue el ritmo de octubre (estiaje); banda de "
                                   "0,55 a 0,64")

    # 5. importación de 2026 antes del 07-09-2026
    i26, pi = importacion_mensual("2026-08")
    ene_ago_imp = sum(i26[(2026, m)] for m in range(1, 9))
    dia, xm_mes = xm_mensual(XM_2026)
    if any(abs(xm_mes[m] - i26[(2026, m)]) > 0.02 for m in range(1, 9)):
        raise ErrorDatos("importación 2026: XM y CENACE no coinciden mes a mes")
    sep_antes = float(dia["2026-09-01":"2026-09-06"].sum())
    despues = float(dia[CORTE_IMPORTACION:].sum())
    dato("importacion_ene_ago_2026_GWh", ene_ago_imp, "GWh", "ene-ago 2026",
         "CENACE, Informe Ejecutivo de Gestión de agosto de 2026, sección 1 (medida en Jamondino)", f"p. {pi}",
         [INF_EJ("2026-08")], "S26-043", "XM da los mismos valores mensuales")
    dato("importacion_sep_1_6_2026_GWh", sep_antes, "GWh", "01-09-2026 a 06-09-2026", "XM, Exportaciones (kWh) 2026",
         "suma horaria del enlace ECUADOR 230", [XM_2026], "S26-044")
    dato("importacion_2026_antes_07_09_GWh", ene_ago_imp + sep_antes, "GWh", "01-01-2026 a 06-09-2026",
         "derivación propia (CENACE enero a agosto más XM 1 a 6 de septiembre)", "", [INF_EJ("2026-08"), XM_2026],
         "S26-043 y S26-044", "desde el 07-09-2026 la importación es cero en el modelo")
    dato("importacion_desde_07_09_2026_GWh", despues, "GWh", f"{CORTE_IMPORTACION} a {dia.index.max():%d-%m-%Y}",
         "XM, Exportaciones (kWh) 2026", "suma horaria", [XM_2026], "S26-044",
         "generación de seguridad; el modelo la lleva a cero (supuesto de estrés)")

    # importación de 2025: Informe Anual 2025 (cifra definitiva), contrastada con el Informe Ejecutivo de diciembre de
    # 2025 y con XM mes a mes (XM suma los enlaces de 138 y 230 kV; agosto difiere 0,26 GWh del informe ejecutivo)
    imp25, p19 = importacion_2025(txt25)
    i25, pi25 = importacion_mensual("2025-12")
    _, xm25 = xm_mensual(XM_2025)
    ie25 = sum(v for (a, _m), v in i25.items() if a == 2025)
    if abs(imp25 - ie25) > 0.5 or abs(imp25 - float(xm25.sum())) > 0.5 \
            or any(abs(xm25[m] - i25[(2025, m)]) > 0.3 for m in range(1, 13)):
        raise ErrorDatos(f"importación 2025: Informe Anual ({imp25}), Informe Ejecutivo ({ie25:.2f}) y XM "
                         f"({float(xm25.sum()):.2f}) no concuerdan")
    if "624.350,15" not in sit["S26-020"]:
        raise ErrorDatos("S26-020 no trae 624.350,15 MWh de importación en 2025")
    dato("importacion_2025_GWh", imp25, "GWh", "2025", "CENACE, Informe Anual 2025, Parte 1, cuadro de cifras",
         "p. %d; Informe Ejecutivo de diciembre de 2025, sección 1, p. %d: %s; XM: %s"
         % (p19 + 1, pi25, ("%.2f" % ie25).replace(".", ","), ("%.2f" % float(xm25.sum())).replace(".", ",")),
         [ANUAL_2025, INF_EJ("2025-12"), XM_2025], "S26-020")

    # 6. participación térmica observada (contraste), con la importación en el denominador como el modelo: térmica /
    #    (hidro + térmica + no convencional + importación). Corrección del 13-10-2026 tras la verificación independiente
    #    del paso 15: enero a agosto de 2026 se comparaba sin importación (20,68 %) y 2025 con 14,8 %.
    d_all = pd.read_excel(INDICADORES, sheet_name="datos")
    y25 = d_all[d_all["Año"] == 2025]
    if len(y25) != 12:
        raise ErrorDatos("indicadores.xlsx no trae los doce meses de 2025")
    te25, to25 = float(y25["Térmica"].sum()), float(y25["TOTAL"].sum())
    if "4.952,42" not in sit["S26-003"] or abs(te25 - 4952.42) > 0.01:
        raise ErrorDatos("indicadores.xlsx: la térmica neta de 2025 no es 4.952,42 GWh (S26-003)")
    te_ea, to_ea = te[2026] + t_ago26, to[2026] + total_ago26
    arch6 = [INDICADORES, INF_EJ("2026-08")]
    dato("termica_participacion_ene_ago_2026", te_ea / (to_ea + ene_ago_imp), "fracción", "ene-ago 2026",
         fte2 + "; importación: Informe Ejecutivo de agosto de 2026, sección 1",
         "térmica sobre producción neta con importación: %.2f / (%.2f + %.2f) GWh" % (te_ea, to_ea, ene_ago_imp),
         arch6, "S26-038 y S26-043", "contraste; mismo denominador que el modelo (corrección del 13-10-2026)")
    dato("termica_participacion_ene_ago_2026_sin_importacion", te_ea / to_ea, "fracción", "ene-ago 2026", fte2,
         "térmica sobre producción neta sin importación", arch6, "S26-038",
         "trazabilidad: valor que el contraste usó hasta el 13-10-2026; no es comparable con el modelo")
    dato("termica_participacion_2025", te25 / (to25 + imp25), "fracción", "2025",
         "CENACE, indicadores.xlsx (hoja datos, 2025) e Informe Anual 2025, Parte 1 (importación)",
         "térmica sobre producción neta con importación: %.2f / (%.2f + %.2f) GWh" % (te25, to25, imp25),
         [INDICADORES, ANUAL_2025], "S26-003 y S26-020",
         "contraste; el Informe Anual (p. 39) publica 14,80 % con la térmica de la figura 1.9 (5.038,52 GWh, 86,11 "
         "más que la del libro) sobre 34.041,15 GWh")
    dato("termica_participacion_2025_sin_importacion", te25 / to25, "fracción", "2025",
         "CENACE, indicadores.xlsx, hoja datos", "térmica sobre producción neta sin importación", [INDICADORES],
         "S26-003", "trazabilidad: no es comparable con el modelo")
    dato("termica_participacion_2026_al_10_oct", cab["TÉRMICA"] / cab["PRODUCCIÓN TOTAL"], "fracción",
         "01-01-2026 a 10-10-2026", "CENACE, Información Operativa, pestaña Acumulada anual (SCADA preliminar)",
         "térmica sobre producción total con importación (el total cierra con hidro, térmica, no convencional e "
         "importación)", [TABLERO], "S26-039", "contraste")
    return filas, centrales


def a_csv(filas):
    buf = io.StringIO()
    w = csv.DictWriter(buf, fieldnames=list(filas[0]), lineterminator="\n")
    w.writeheader()
    w.writerows(filas)
    return buf.getvalue().encode("utf-8-sig")


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--comprobar", action="store_true")
    args = ap.parse_args()
    if not FUENTES.exists():
        raise SystemExit("situacion_act_2026.py lee los documentos de CENACE y XM guardados localmente en %s "
                         "(variable de entorno ART6_FUENTES_2026), que no se distribuyen. Su resultado, "
                         "act_2026_observado.csv, está versionado; la tabla por central que también escribe queda "
                         "fuera del repositorio y agregar_por_clase.py la resume por clase." % FUENTES)
    filas, centrales = observado()
    nuevo = {SALIDA: a_csv(filas), SALIDA_CENTRALES: a_csv(centrales)}
    difiere = [p.name for p, b in nuevo.items() if not p.exists() or p.read_bytes() != b]
    if args.comprobar:
        print("Coincide" if not difiere else "Difiere: " + ", ".join(difiere))
        return 1 if difiere else 0
    for p, b in nuevo.items():
        p.write_bytes(b)
    for f in filas:
        print("%-42s %14.6f %s" % (f["clave"], f["valor"], f["unidad"]))
    for c in centrales:
        print("%-22s 2025 %9.2f  2026 al 10-10 %8.1f  razón %.4f" % (c["central_tablero"], c["produccion_2025_GWh"],
                                                                     c["acumulado_2026_al_10_oct_GWh"], c["razon_2026_2025"]))
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except ErrorDatos as ex:
        print("ERROR", ex)
        sys.exit(2)
