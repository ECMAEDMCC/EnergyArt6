# -*- coding: utf-8 -*-
"""Extrae del tablero de los Productos 1 a 4 los datos que publica el tablero de resultados.

El tablero de los Productos 1 a 4 es un componente React con recharts que embebe tres bloques de datos (DATA, PORT y
CDR) y lleva en su codigo la escalera N0-N5, la macroestructura de la demanda, los puentes entre la cartera y la
demanda y la sintesis del Capitulo 4. Este script los lee del archivo, sin copiarlos a mano, y escribe en
datos_productos/ las entradas que usa productos.py:

- demanda.json: registros de demanda del Capitulo 1 (bloque DATA), escalera N0-N5 y macroestructura de la demanda.
- remociones.json: arquetipos de remocion del Capitulo 3 (bloque CDR), nombres de los filtros y horizonte de mercado.
- cartera_agregada.json: cartera del Capitulo 2 (bloque PORT) contada por sector, veredicto y actividad, por tramo de
  la NDC y por canal de demanda.
- sintesis.json: actividades que pasan todos los filtros (Capitulo 4) con su numero de iniciativas.
- LEEME.md: origen, fechas, md5 del archivo de origen y reglas de publicacion.

Reglas de publicacion (13-10-2026): la cartera entra solo agregada, como numero de
iniciativas, sin nombres de proyecto, sin codigos y sin potenciales. El bloque PORT se lee en memoria y ningun archivo
recibe su detalle por iniciativa: antes de escribir, el script comprueba que ningun nombre ni codigo de PORT aparezca
en lo que va a guardar. Los textos extraidos se limpian de las siglas de programas de terceros que el tablero publico
no cita (_neutro).

Uso, desde Energy/Art6_motor: python extraer_productos.py <ruta del .jsx>
Despues: python tablero.py, que rehace el tablero sin correr el modelo.
"""
import datetime
import hashlib
import io
import json
import re
import sys
import unicodedata
from collections import Counter, OrderedDict
from difflib import SequenceMatcher
from pathlib import Path

AQUI = Path(__file__).resolve().parent
DESTINO = AQUI / "datos_productos"
VERSION = "V8"

# Siglas de programas de terceros que el tablero publico no cita (decision del 13-10-2026). Se guardan como huella
# (primeros 16 caracteres del SHA-256 de la sigla o del par de palabras en minusculas) para que el codigo tampoco las
# nombre. _neutro las retira de todo texto extraido y _comprobar falla si alguna queda.
RETIRADAS = {"f25a7706781f3210", "6f9dbbcd6c7ff866", "d5a7893781d3a0fd", "3141c439fd03395b", "74e42492d8591f46",
             "45597ab5e373473b"}
_PALABRA = re.compile(r"[A-Za-zÀ-ÿ][\wÀ-ÿ-]*")


class ErrorExtraccion(Exception):
    pass


# ----------------------------------------------------------------------------- lectura del componente
def _literal(txt, inicio):
    """Texto del literal JS (arreglo u objeto) que abre en txt[inicio], hasta su cierre."""
    nivel, i, cadena = 0, inicio, None
    while i < len(txt):
        c = txt[i]
        if cadena:
            if c == "\\":
                i += 2
                continue
            if c == cadena:
                cadena = None
        elif c in "\"'`":
            cadena = c
        elif c in "[{":
            nivel += 1
        elif c in "]}":
            nivel -= 1
            if nivel == 0:
                return txt[inicio:i + 1]
        i += 1
    raise ErrorExtraccion("literal sin cierre desde la posicion %d" % inicio)


def _a_json(literal):
    """Literal JS sencillo (claves sin comillas, cadenas con comillas dobles, numeros, true y false) a objeto Python."""
    out, i, cadena = [], 0, False
    while i < len(literal):
        c = literal[i]
        if cadena:
            out.append(c)
            if c == "\\":
                out.append(literal[i + 1])
                i += 2
                continue
            cadena = c != '"'
            i += 1
            continue
        if c == '"':
            cadena = True
            out.append(c)
            i += 1
            continue
        m = re.match(r"[A-Za-z_]\w*(?=\s*:)", literal[i:])
        previo = "".join(out).rstrip()[-1:]
        if m and previo in ("{", ","):
            out.append('"%s"' % m.group(0))
            i += m.end()
            continue
        out.append(c)
        i += 1
    return json.loads(re.sub(r",\s*([}\]])", r"\1", "".join(out)))


def _buscar(txt, patron, que, desde=0, banderas=re.S):
    m = re.compile(patron, banderas).search(txt, desde)
    if not m:
        raise ErrorExtraccion("no se encontro %s en el componente" % que)
    return m


def _bloque_datos(txt, nombre):
    """Bloques DATA, PORT y CDR: arreglos JSON en una linea «const X = [...];»."""
    m = _buscar(txt, r"^const %s = (\[.*\]);\s*$" % nombre, "el bloque %s" % nombre, banderas=re.M)
    return json.loads(m.group(1))


def _literal_tras(txt, patron, que, desde=0):
    m = _buscar(txt, patron, que, desde)
    return _a_json(_literal(txt, m.end() - 1)), m.end()


def _sin_etiquetas(s):
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>|\{[^{}]*\}", " ", s)).strip()


# ----------------------------------------------------------------------------- limpieza de textos
def _huella(s):
    return hashlib.sha256(s.lower().encode("utf-8")).hexdigest()[:16]


def _retirada(texto):
    ps = _PALABRA.findall(texto)
    return (any(_huella(p) in RETIRADAS for p in ps)
            or any(_huella(a + " " + b) in RETIRADAS for a, b in zip(ps, ps[1:])))


def _neutro(texto):
    """Retira las siglas de RETIRADAS: el parentesis que contiene una nombra al intermediario y se suprime entero;
    fuera de parentesis se suprime la sigla con su separador. La acreditacion de politicas se nombra solo en general."""
    if isinstance(texto, str):
        texto = re.sub(r"(?i)policy\s+crediting\s*/\s*reforma\s+(?:de\s+)?subsidios?\s+(?:a\s+los\s+)?f[oó]siles?",
                       "Acreditación de políticas", texto)
    if not isinstance(texto, str) or not _retirada(texto):
        return texto
    t = re.sub(r"\s*\([^()]*\)", lambda m: "" if _retirada(m.group(0)) else m.group(0), texto)
    for p in sorted(set(_PALABRA.findall(t)), key=len, reverse=True):
        if _huella(p) in RETIRADAS:
            t = re.sub(r"(?<![\w-])%s(?![\w-])\s*/?\s*" % re.escape(p), "", t)
    t = re.sub(r"\s+([,;.)])", r"\1", re.sub(r"\s{2,}", " ", t)).strip(" /")
    if _retirada(t):
        raise ErrorExtraccion("quedo una sigla retirada en un texto extraido")
    return t[:1].upper() + t[1:] if texto[:1].isupper() else t


def _limpio(v):
    """Texto de una celda: sin el retorno de carro que deja Excel (_x000D_) y sin siglas retiradas."""
    if isinstance(v, str):
        return _neutro(re.sub(r"\s*_x000D_\s*", " ", v).strip())
    return v


def _norm(s):
    s = unicodedata.normalize("NFKD", str(s)).encode("ascii", "ignore").decode().lower()
    return re.findall(r"[a-z0-9]+", s)


def _parecido(a, b):
    """Parecido entre dos rotulos de actividad: palabras compartidas sobre las del rotulo corto, sobre todas, y
    parecido de las cadenas."""
    ta, tb = set(_norm(a)), set(_norm(b))
    comun = len(ta & tb)
    return (comun / float(min(len(ta), len(tb)) or 1) + comun / float(len(ta | tb) or 1)
            + 0.5 * SequenceMatcher(None, " ".join(_norm(a)), " ".join(_norm(b))).ratio())


def _emparejar(rotulos, candidatos, que):
    """{rotulo: candidato}: cada rotulo del componente con la actividad mas parecida de su grupo, sin repetir."""
    par = {}
    for r in rotulos:
        mejor = max(candidatos, key=lambda c: _parecido(r, c))
        if _parecido(r, mejor) < 1.0:
            raise ErrorExtraccion("%s: «%s» no se parece a ninguna actividad de su grupo" % (que, r))
        par[r] = mejor
    if len(set(par.values())) != len(par):
        raise ErrorExtraccion("%s: dos rotulos apuntan a la misma actividad" % que)
    return par


# ----------------------------------------------------------------------------- reglas de la cartera
def _tramo(piso):
    """Tramo de la NDC de una iniciativa a partir de la bandera de piso del componente."""
    p = str(piso or "").lower()
    if "incondicional" in p:
        return "Incondicional"
    if p.startswith("condicional"):
        return "Condicional (duplica una iniciativa de la NDC)" if "dedup" in p else "Condicional"
    if "por determinar" in p:
        return "Por determinar"
    if p.startswith("n/a"):
        return "No aplica (habilitante)"
    if p.startswith("fuera de ndc"):
        return "Fuera de la NDC"
    raise ErrorExtraccion("bandera de piso desconocida en la cartera: agregue su tramo en _tramo()")


PORTAFOLIOS = OrderedDict([("NDC2", "Segunda NDC"), ("PLANMICC-PdI", "Plan de Inversión del PLANMICC"),
                           ("Cap. II", "Actividades de cartera del Capítulo 2")])


def _codigos_re(port):
    """Patron de los codigos de PORT en cualquier escritura: letras y numero, juntos, con guion o con espacios."""
    partes = set()
    for p in port:
        m = re.match(r"\s*([A-Za-z]+)\s*-?\s*(\d+)\s*$", str(p.get("Codigo") or ""))
        if m:
            partes.add((m.group(1), m.group(2)))
    alternativas = ["%s\\s*-?\\s*%s" % (re.escape(a), re.escape(n)) for a, n in sorted(partes)]
    return re.compile(r"(?<![A-Za-z0-9])(?:%s)(?![0-9])" % "|".join(alternativas)) if alternativas else None


def _sin_cartera(texto, port, codigos):
    """Quita de un texto de la sintesis los codigos y nombres de proyecto de PORT: el parentesis que contiene uno se
    suprime entero."""
    if not isinstance(texto, str):
        return texto
    nombres = [str(p["Proyecto"]).lower() for p in port if p.get("Tipo") != "cartera" and p.get("Proyecto")]
    con_cartera = lambda s: bool(codigos and codigos.search(s)) or any(n in s.lower() for n in nombres)
    t = re.sub(r"\s*\([^()]*\)", lambda m: "" if con_cartera(m.group(0)) else m.group(0), texto)
    if codigos:
        t = codigos.sub("", t)
    return re.sub(r"\s{2,}", " ", t).strip(" ,;·")


# ----------------------------------------------------------------------------- extraccion
def extraer(ruta):
    ruta = Path(ruta)
    crudo = ruta.read_bytes()
    txt = crudo.decode("utf-8")
    md5 = hashlib.md5(crudo).hexdigest()
    origen = OrderedDict([("archivo", ruta.name), ("version", VERSION), ("md5", md5),
                          ("fecha_archivo", datetime.date.fromtimestamp(ruta.stat().st_mtime).isoformat()),
                          ("fecha_extraccion", datetime.date.today().isoformat())])
    data, port, cdr = _bloque_datos(txt, "DATA"), _bloque_datos(txt, "PORT"), _bloque_datos(txt, "CDR")
    codigos = _codigos_re(port)

    # --- Capitulo 1: demanda
    escalera, _ = _literal_tras(txt, r"const LADDER\s*=\s*\[", "la escalera N0-N5")
    macro_ini = _buscar(txt, r"MACRO-ESTRUCTURA", "la macroestructura de la demanda").start()
    cifras, fin_macro = _literal_tras(txt, r"\[(?=\s*\{k:)", "las cifras de la macroestructura", macro_ini)
    titulo_macro = _buscar(txt, r"Hallazgo principal · ([^<{]+)<", "el titulo de la macroestructura", macro_ini)
    nota_macro = _sin_etiquetas(_buscar(txt, r"fontStyle:\"italic\"[^>]*>(.*?)</div>", "la nota de la macroestructura",
                                        fin_macro).group(1))
    fuente_macro = _buscar(nota_macro, r"Fuente: ([^.]+)\.", "la fuente de la macroestructura").group(1).strip()
    fecha_macro = re.search(r"\(([a-z]{3}-\d{4})\)", titulo_macro.group(1))
    demanda = OrderedDict([
        ("origen", OrderedDict(list(origen.items()) + [("bloque", "DATA"), ("capitulo", "Capítulo 1 · Demanda")])),
        ("registros", [OrderedDict((k, _limpio(v)) for k, v in r.items()) for r in data]),
        ("escalera", [OrderedDict([("peldano", e["n"]), ("descripcion", _limpio(e["t"])),
                                   ("lado", "revelada" if e["cat"] == "R" else "anunciada")]) for e in escalera]),
        ("macroestructura", OrderedDict([
            ("titulo", _limpio(re.sub(r"\s*\([a-z]{3}-\d{4}\)\s*$", "", titulo_macro.group(1).strip()))),
            ("fecha", fecha_macro.group(1) if fecha_macro else ""),
            ("cifras", [OrderedDict([("cifra", _limpio(c["k"])), ("descripcion", _limpio(c["d"]))]) for c in cifras]),
            ("fuente", _limpio(fuente_macro))])),
    ])

    # --- Capitulo 2 y 3: puentes del componente (veredicto o clasificacion, actividad, canal)
    sk_ini = _buscar(txt, r"function SankeyModule2\s*\(", "los puentes de la cartera y la demanda").start()
    cap2, _ = _literal_tras(txt, r"const CAP2\s*=\s*\{", "los puentes de la cartera", sk_ini)
    sk_cdr, _ = _literal_tras(txt, r"const CDR\s*=\s*\{", "los puentes de las remociones", sk_ini)

    # --- Capitulo 3: remociones
    filtros_txt = _sin_etiquetas(_buscar(txt, r"<b>5 filtros:</b>(.*?)</div>", "los filtros de las remociones").group(1))
    filtros = OrderedDict((f, re.sub(r"\s+y$", "", n).strip()) for f, n in
                          re.findall(r"(F\d)·(.+?)(?=\s+y\s+F\d·|\s*\(|\s+·\s+F\d·|\.\s|$)", filtros_txt))
    hor = {d["id"]: d for d in sk_cdr["dems"]}
    clas = {c["id"]: c["label"] for c in sk_cdr["cats"]}
    por_clas = {}
    for a in sk_cdr["acts"]:
        por_clas.setdefault(clas[a["ver"]], []).append(a)
    horizonte = {}
    for cl, acts in por_clas.items():
        cands = [r["Actividad"] for r in cdr if r["Categoria"] == cl]
        par = _emparejar([a["label"] for a in acts], cands, "remociones %s" % cl)
        for a in acts:
            d = hor[a["dem"][0]]
            horizonte[par[a["label"]]] = OrderedDict([("horizonte", d["label"]), ("detalle", d.get("sub", ""))])
    if len(horizonte) != len(cdr):
        raise ErrorExtraccion("los puentes de las remociones no cubren los %d arquetipos" % len(cdr))
    remociones = OrderedDict([
        ("origen", OrderedDict(list(origen.items()) + [("bloque", "CDR"), ("capitulo", "Capítulo 3 · Remociones")])),
        ("registros", [OrderedDict(list((k, _limpio(v)) for k, v in r.items())
                                   + list(horizonte[r["Actividad"]].items())) for r in cdr]),
        ("filtros", filtros),
    ])

    # --- Capitulo 2: cartera agregada (PORT solo en memoria)
    tipo = lambda p: "actividad de cartera" if p.get("Tipo") == "cartera" else "proyecto"
    veredictos = [c["label"] for c in cap2["cats"]]
    ver_id = {c["id"]: c["label"] for c in cap2["cats"]}
    canales = OrderedDict((d["id"], OrderedDict([("canal", d["label"]), ("detalle", d.get("sub", "")),
                                                 ("revelada", bool(d.get("rev")))])) for d in cap2["dems"])
    if set(p["Ver"] for p in port) - set(veredictos):
        raise ErrorExtraccion("la cartera tiene veredictos que los puentes no declaran")
    canal_de = {}
    for vid, v in ver_id.items():
        acts = [a for a in cap2["acts"] if a["ver"] == vid]
        cands = sorted(set(p["Actividad"] for p in port if p["Ver"] == v))
        par = _emparejar([a["label"] for a in acts], cands, "cartera %s" % v)
        for a in acts:
            act = par[a["label"]]
            n_port = sum(1 for p in port if p["Ver"] == v and p["Actividad"] == act)
            if n_port != a["n"]:
                raise ErrorExtraccion("cartera %s: el puente cuenta %d iniciativas y la cartera %d" % (v, a["n"], n_port))
            canal_de[(v, act)] = [canales[d]["canal"] for d in a["dem"]]
    grupos = Counter((p["Sector"], p["Ver"], p["Actividad"], tipo(p)) for p in port)
    orden_v = {v: i for i, v in enumerate(veredictos)}
    por_actividad = [OrderedDict([("sector", s), ("veredicto", v), ("actividad", a), ("tipo", t), ("iniciativas", n),
                                  ("canales", canal_de.get((v, a), []))])
                     for (s, v, a, t), n in sorted(grupos.items(), key=lambda kv: (orden_v[kv[0][1]], -kv[1], kv[0][2]))]
    sin_canal = [x for x in por_actividad if not x["canales"]]
    if sin_canal:
        raise ErrorExtraccion("%d actividades de la cartera no tienen canal en los puentes" % len(sin_canal))
    tramos = Counter((PORTAFOLIOS.get(p["Portafolio"], p["Portafolio"]), p["Ver"], _tramo(p.get("Piso"))) for p in port)
    por_tramo = [OrderedDict([("portafolio", o), ("veredicto", v), ("tramo", t), ("iniciativas", n)])
                 for (o, v, t), n in sorted(tramos.items(), key=lambda kv: (list(PORTAFOLIOS.values()).index(kv[0][0])
                                                                          if kv[0][0] in PORTAFOLIOS.values() else 9,
                                                                          orden_v[kv[0][1]], kv[0][2]))]
    canal_n = Counter()
    for x in por_actividad:
        for c in x["canales"]:
            canal_n[(x["veredicto"], c)] += x["iniciativas"]
    por_canal = [OrderedDict([("veredicto", v), ("canal", c), ("iniciativas", canal_n[(v, c)])])
                 for v in veredictos for c in [d["canal"] for d in canales.values()] if canal_n.get((v, c))]
    nota = _sin_etiquetas(_buscar(txt, r"Reconciliaci[oó]n explorador(.*?)</div>", "la conciliacion de la cartera").group(1))
    conc = re.search(r"(\d+) NDC2 \+ (\d+) PLANMICC-PdI = (\d+) instancias", nota)
    ficha = re.search(r"(\d+) entradas con ficha", nota)
    cartera = OrderedDict([
        ("origen", OrderedDict(list(origen.items()) + [("bloque", "PORT"), ("capitulo", "Capítulo 2 · Portafolio")])),
        ("regla", "Solo número de iniciativas por sector, veredicto, actividad, tramo y canal: sin nombres de proyecto, "
                  "sin códigos y sin potenciales (decisión del 13-10-2026)."),
        ("totales", OrderedDict([("iniciativas", len(port)),
                                 ("proyectos", sum(1 for p in port if tipo(p) == "proyecto")),
                                 ("actividades_de_cartera", sum(1 for p in port if tipo(p) != "proyecto"))])),
        ("conciliacion_documento", OrderedDict([
            ("instancias_del_documento", int(conc.group(3)) if conc else None),
            ("segunda_ndc", int(conc.group(1)) if conc else None),
            ("planmicc_en_el_documento", int(conc.group(2)) if conc else None),
            ("proyectos_con_ficha", int(ficha.group(1)) if ficha else None)])),
        ("veredictos", veredictos),
        ("canales", list(canales.values())),
        ("por_actividad", por_actividad),
        ("por_tramo", por_tramo),
        ("por_canal", por_canal),
    ])

    # --- Capitulo 4: sintesis
    syn, _ = _literal_tras(txt, r"const SYN\s*=\s*\[", "la sintesis")
    match, _ = _literal_tras(txt, r"const SYN_MATCH\s*=\s*\{", "la correspondencia de la sintesis")
    niveles = list(OrderedDict.fromkeys(s["tier"] for s in syn))
    actividades = []
    for s in syn:
        m = match.get(s["act"], {})
        ps = [p for a in m.get("port", []) for p in port if p["Actividad"] == a]
        cs = [c for a in m.get("cdr", []) for c in cdr if c["Actividad"] == a]
        etiqueta = _sin_cartera(s["act"], port, codigos)
        if any(str(p["Proyecto"]).lower() == etiqueta.lower() for p in port if p.get("Tipo") != "cartera"):
            etiqueta = ", ".join(m.get("port", [])) or etiqueta     # el rotulo era un nombre de proyecto
        actividades.append(OrderedDict([
            ("nivel", s["tier"]), ("actividad", _limpio(etiqueta)),
            ("ejes", _limpio(_sin_cartera(s["axes"], port, codigos))),
            ("canal", _limpio(_sin_cartera(s["canal"], port, codigos))),
            ("norma", _limpio(_sin_cartera(s["norma"], port, codigos))),
            ("actividades_de_la_cartera", m.get("port", [])), ("arquetipos_de_remocion", m.get("cdr", [])),
            ("proyectos", sum(1 for p in ps if tipo(p) == "proyecto")),
            ("actividades_de_cartera", sum(1 for p in ps if tipo(p) != "proyecto")),
            ("arquetipos", len(cs))]))
    sintesis = OrderedDict([
        ("origen", OrderedDict(list(origen.items()) + [("bloque", "SYN"), ("capitulo", "Capítulo 4 · Síntesis")])),
        ("niveles", niveles),
        ("actividades", actividades),
    ])

    salidas = OrderedDict([("demanda.json", demanda), ("remociones.json", remociones),
                           ("cartera_agregada.json", cartera), ("sintesis.json", sintesis)])
    _comprobar(salidas, port, codigos)
    return origen, salidas


def _comprobar(salidas, port, codigos):
    """Ninguna salida lleva nombre ni codigo de proyecto de PORT, ni una sigla retirada."""
    nombres = [re.sub(r"\s+", " ", str(p["Proyecto"])).strip().lower() for p in port
               if p.get("Tipo") != "cartera" and p.get("Proyecto")]
    for archivo, obj in salidas.items():
        texto = re.sub(r"\s+", " ", json.dumps(obj, ensure_ascii=False))
        bajo = texto.lower()
        fugas = sum(1 for n in nombres if n and n in bajo) + (len(codigos.findall(texto)) if codigos else 0)
        if fugas:
            raise ErrorExtraccion("%s llevaria %d nombres o codigos de la cartera: no se escribe" % (archivo, fugas))
        if any(_retirada(s) for s in re.findall(r'"((?:[^"\\]|\\.)*)"', texto)):
            raise ErrorExtraccion("%s llevaria una sigla retirada: no se escribe" % archivo)


LEEME = """# Datos de los Productos 1 a 4

Entradas del motor para las secciones de demanda, cartera, remociones y síntesis del tablero de resultados
(`tablero.py` con `productos.py`). Las escribe `extraer_productos.py` desde el tablero de los Productos 1 a 4; no se
editan a mano.

| Dato | Valor |
|---|---|
| Origen | tablero de los Productos 1 a 4, versión {version}: componente React `{archivo}` |
| md5 del origen | `{md5}` |
| Fecha del archivo de origen | {fecha_archivo} |
| Fecha de extracción | {fecha_extraccion} |

| Archivo | Contenido |
|---|---|
| `demanda.json` | {n_dem} registros de demanda del Capítulo 1 (bloque DATA: JCM, Suiza, otros compradores y CORSIA), escalera N0-N5 y macroestructura de la demanda |
| `remociones.json` | {n_cdr} arquetipos de remoción del Capítulo 3 (bloque CDR), con los filtros y su horizonte de mercado |
| `cartera_agregada.json` | cartera del Capítulo 2 (bloque PORT, {n_port} iniciativas) contada por sector, veredicto, actividad, tramo de la NDC y canal de demanda |
| `sintesis.json` | {n_syn} actividades que pasan todos los filtros (Capítulo 4) con su número de iniciativas |

Reglas de publicación (13-10-2026):

- La cartera entra solo agregada, como número de iniciativas por actividad y veredicto, sin nombres de proyecto, sin
  códigos y sin potenciales. Ni esta carpeta ni el código que la escribe contienen el detalle de la cartera por
  iniciativa: el script lo lee en memoria y comprueba, antes de escribir, que ningún nombre ni código aparezca en
  las salidas.
- Los textos extraídos se limpian de las siglas de programas de terceros que el tablero público no cita, y del
  retorno de carro que deja Excel (`_x000D_`).

Para rehacer, desde `Energy/Art6_motor`: `python extraer_productos.py <ruta del .jsx>` y después `python tablero.py`.
"""


def escribir(origen, salidas):
    DESTINO.mkdir(parents=True, exist_ok=True)
    for archivo, obj in salidas.items():
        io.open(DESTINO / archivo, "w", encoding="utf-8", newline="\n").write(
            json.dumps(obj, ensure_ascii=False, indent=1) + "\n")
    fecha = lambda iso: "-".join(reversed(iso.split("-")))          # 2026-10-13 -> 13-10-2026
    texto = LEEME.format(n_dem=len(salidas["demanda.json"]["registros"]),
                         n_cdr=len(salidas["remociones.json"]["registros"]),
                         n_port=salidas["cartera_agregada.json"]["totales"]["iniciativas"],
                         n_syn=len(salidas["sintesis.json"]["actividades"]),
                         **dict(origen, fecha_archivo=fecha(origen["fecha_archivo"]),
                                fecha_extraccion=fecha(origen["fecha_extraccion"])))
    io.open(DESTINO / "LEEME.md", "w", encoding="utf-8", newline="\n").write(texto)
    for archivo in list(salidas) + ["LEEME.md"]:
        print("  %s" % (DESTINO / archivo))


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("Uso: python extraer_productos.py <ruta del .jsx del tablero de los Productos 1 a 4>")
    escribir(*extraer(sys.argv[1]))
