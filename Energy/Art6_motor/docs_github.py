# -*- coding: utf-8 -*-
"""Versión en Markdown de la documentación para leerla en GitHub.

GitHub muestra los archivos .rst, pero no ejecuta las inclusiones de archivos (csv-table con :file:,
raw con :file:, include), así que las páginas fuente se ven sin sus tablas, fichas ni figuras. Este
módulo recorre las páginas de docs/ y escribe en docs/github/ una copia en Markdown con todo ese
contenido incorporado. Se rehace en cada corrida, después de exportar_docs."""
import csv
import io
import os
import re
from html.parser import HTMLParser

import comun as C

DOCS = C.DOCS
SALIDA = DOCS / "github"
PAGINAS = "https://%s.github.io/%s/" % (os.environ.get("DOCS_GITHUB_USER", "ECMAEDMCC").lower(),
                                        os.environ.get("DOCS_GITHUB_REPO", "EnergyArt6"))   # sitio publicado
NIVEL = {"=": "#", "-": "##", "~": "###", "^": "####", '"': "####"}
SUB = {}
SUBRAYADO = re.compile(r"([=\-~^\"])\1{2,}")


def _sustituciones():
    s = {}
    f = DOCS / "_generado" / "corrida.rst"
    if f.exists():
        for m in re.finditer(r"^\.\. \|([^|]+)\| replace:: (.*)$", f.read_text(encoding="utf-8"), re.M):
            s[m.group(1)] = m.group(2).strip()
    return s


def _ruta(md, archivo):
    """Ruta relativa desde la página Markdown hasta un archivo."""
    return os.path.relpath(archivo, md.parent).replace("\\", "/")


def _titulo_de_rst(rst):
    lin = rst.read_text(encoding="utf-8").splitlines()
    for i in range(len(lin) - 1):
        if lin[i].strip() and SUBRAYADO.fullmatch(lin[i + 1].strip() or "x"):
            return lin[i].strip()
    return rst.stem


def _md_de(rst):
    rel = rst.relative_to(DOCS)
    return SALIDA / (rel.parent / "README.md" if rel.name == "index.rst" else rel.with_suffix(".md"))


def _inline(t, rst, md):
    t = re.sub(r"\|([A-Za-z_]+)\|", lambda m: SUB.get(m.group(1), m.group(0)), t)
    t = re.sub(r"``([^`]+)``", r"`\1`", t)

    def doc(m):
        txt, ref = (m.group(1), m.group(2)) if m.group(2) else (None, m.group(1))
        ref = ref.strip()
        destino_rst = (DOCS / (ref.lstrip("/") + ".rst")) if ref.startswith("/") else (rst.parent / (ref + ".rst"))
        destino_rst = destino_rst.resolve()
        if not destino_rst.exists() and (destino_rst.with_suffix("") / "index.rst").exists():
            destino_rst = destino_rst.with_suffix("") / "index.rst"
        if not destino_rst.exists():
            return txt or ref
        return "[%s](%s)" % ((txt or _titulo_de_rst(destino_rst)).strip(), _ruta(md, _md_de(destino_rst)))
    t = re.sub(r":doc:`([^`<]+?)(?:\s*<([^>]+)>)?`", doc, t)
    t = re.sub(r":(?:numref|ref|term):`([^`<]+?)(?:\s*<[^>]+>)?`", r"\1", t)
    t = re.sub(r"`([^`<]+?)\s*<([^>]+)>`__?", lambda m: "[%s](%s)" % (m.group(1).strip(), _enlace(m.group(2), rst, md)), t)
    return t


def _enlace(destino, rst, md):
    """Destino de un enlace en la versión para GitHub. Las páginas HTML de _static (el tablero, las gráficas
    interactivas) se abren en el sitio publicado, porque GitHub muestra su código; el resto de _static se enlaza en el
    repositorio, relativo a la página Markdown."""
    d = destino.strip()
    if "://" in d or d.startswith("#") or "_static/" not in d:
        return d
    f = (rst.parent / d).resolve()
    try:
        rel = f.relative_to(DOCS.resolve()).as_posix()
    except ValueError:
        return d
    return PAGINAS + rel if f.suffix == ".html" else _ruta(md, f)


def _tabla_md(filas, titulo=None):
    if not filas:
        return ""
    ancho = max(len(f) for f in filas)
    filas = [f + [""] * (ancho - len(f)) for f in filas]
    esc = lambda x: str(x).replace("|", "\\|").replace("\n", " ").strip()
    out = ["*Tabla. %s*" % titulo, ""] if titulo else []
    out.append("| " + " | ".join(esc(x) for x in filas[0]) + " |")
    out.append("|" + "---|" * ancho)
    for f in filas[1:]:
        out.append("| " + " | ".join(esc(x) for x in f) + " |")
    return "\n".join(out)


class _HtmlAMd(HTMLParser):
    """Convierte los fragmentos HTML del motor (mapa, fichas, supuestos) a Markdown: títulos, párrafos,
    listas y tablas. Descarta estilos, scripts y atributos."""
    BLOQUE = {"p", "div", "section", "article", "header", "footer", "dl", "ul", "ol", "figure", "figcaption"}

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.out, self.linea, self.saltar = [], "", 0
        self.tabla, self.fila, self.celda = None, None, None
        self.titulo = None

    def _cerrar_linea(self):
        t = re.sub(r"\s+", " ", self.linea).strip()
        if t:
            self.out.append(t)
            self.out.append("")
        self.linea = ""

    def handle_starttag(self, tag, attrs):
        if tag in ("style", "script"):
            self.saltar += 1
        elif self.saltar:
            return
        elif tag == "table":
            self._cerrar_linea(); self.tabla = []
        elif tag == "tr" and self.tabla is not None:
            self.fila = []
        elif tag in ("td", "th") and self.fila is not None:
            a = dict(attrs)
            self.celda = ""
            self.span = (int(a.get("colspan") or 1), int(a.get("rowspan") or 1), tag == "th")
        elif tag in ("h1", "h2", "h3", "h4", "h5"):
            self._cerrar_linea(); self.titulo = tag
        elif tag == "li":
            self._cerrar_linea(); self.linea = "- "
        elif tag == "dt":
            self._cerrar_linea()
        elif tag == "br":
            if self.celda is not None:
                self.celda += " "
            else:
                self._cerrar_linea()
        elif tag in self.BLOQUE and self.celda is None:
            self._cerrar_linea()
        else:
            self._separar(tag)

    def _separar(self, tag=None):
        """Los elementos en línea del fragmento se separan con estilos, no con espacios."""
        if tag in ("sub", "sup"):
            return
        if self.celda is not None:
            self.celda += " "
        else:
            self.linea += " "

    def handle_endtag(self, tag):
        if tag in ("style", "script"):
            self.saltar = max(0, self.saltar - 1)
        elif self.saltar:
            return
        elif tag in ("td", "th") and self.fila is not None and self.celda is not None:
            col, fil, th = getattr(self, "span", (1, 1, False))
            txt = re.sub(r"\s+", " ", self.celda).strip()
            self.fila.append((txt, col, fil, th)); self.celda = None
        elif tag == "tr" and self.tabla is not None and self.fila is not None:
            if any(c[0] for c in self.fila):
                self.tabla.append(self.fila)
            self.fila = None
        elif tag == "table" and self.tabla is not None:
            if self.tabla:
                self.out += [_tabla_md(_aplanar(self.tabla)), ""]
            self.tabla = None
        elif tag in ("h1", "h2", "h3", "h4", "h5") and self.titulo:
            t = re.sub(r"\s+", " ", self.linea).strip()
            if t:
                self.out += ["#### " + t, ""]
            self.linea, self.titulo = "", None
        elif tag in ("li", "dd", "dt") or (tag in self.BLOQUE and self.celda is None):
            self._cerrar_linea()
        else:
            self._separar(tag)

    def handle_data(self, data):
        if self.saltar:
            return
        if self.celda is not None:
            self.celda += data
        else:
            self.linea += data

    def markdown(self):
        self._cerrar_linea()
        return "\n".join(self.out)


def _aplanar(tabla):
    """Expande colspan y rowspan y une en una sola fila los encabezados de dos niveles."""
    rejilla, pend = [], {}
    for fila in tabla:
        out, j, k = [], 0, 0
        while k < len(fila) or j in pend:
            if j in pend:
                txt, quedan, th = pend[j]
                out.append(("", th))
                if quedan > 1:
                    pend[j] = (txt, quedan - 1, th)
                else:
                    del pend[j]
                j += 1
                continue
            txt, col, fil, th = fila[k]
            for c in range(col):
                # una fila de un solo rótulo que ocupa toda la tabla es un separador de grupo
                out.append((txt if (c == 0 or len(fila) > 1) else "", th))
                if fil > 1:
                    pend[j + c] = (txt, fil - 1, th)
            j += col
            k += 1
        rejilla.append(out)
    cab = [r for r in rejilla[:2] if r and all(th for _, th in r)]
    if len(cab) == 2:
        n = max(len(cab[0]), len(cab[1]))
        a = cab[0] + [("", True)] * (n - len(cab[0]))
        b = cab[1] + [("", True)] * (n - len(cab[1]))
        unida = [" ".join(x for x in (a[i][0], b[i][0]) if x) for i in range(n)]
        return [unida] + [[t for t, _ in r] for r in rejilla[2:]]
    return [[t for t, _ in r] for r in rejilla]


def _html_limpio(ruta):
    p = _HtmlAMd()
    p.feed(ruta.read_text(encoding="utf-8"))
    return p.markdown()


def _resolver(arg, rst):
    arg = arg.strip()
    return (DOCS / arg.lstrip("/")) if arg.startswith("/") else (rst.parent / arg).resolve()


def convertir(rst, md, pagina=None, lineas=None):
    """Convierte una página rst, un fragmento incluido o el cuerpo de una directiva (lineas) a líneas Markdown."""
    pagina = pagina or rst
    lin = lineas if lineas is not None else rst.read_text(encoding="utf-8").splitlines()
    out, i = [], 0
    while i < len(lin):
        l = lin[i]
        if i + 1 < len(lin) and l.strip() and not l.startswith(" ") and SUBRAYADO.fullmatch(lin[i + 1].strip() or "x") \
                and len(lin[i + 1].strip()) >= len(l.strip()) - 2:
            out += ["%s %s" % (NIVEL.get(lin[i + 1].strip()[0], "###"), _inline(l.strip(), pagina, md)), ""]
            i += 2
            continue
        ms = re.match(r"^(\s+)\.\. [a-z\-]+::", l)
        if ms:                      # directiva dentro de una lista: se convierte sin sangría y se devuelve sangrada
            sangria = len(ms.group(1))
            j = i + 1
            while j < len(lin) and (not lin[j].strip() or len(lin[j]) - len(lin[j].lstrip()) > sangria):
                j += 1
            bloque = [x[sangria:] if x.strip() else "" for x in lin[i:j]]
            out += [(" " * sangria + x) if x.strip() else "" for x in convertir(rst, md, pagina, lineas=bloque)]
            i = j
            continue
        m = re.match(r"^\.\. ([a-z\-]+)::\s*(.*)$", l)
        if m:
            nombre, arg = m.group(1), m.group(2)
            j, opciones, cuerpo = i + 1, {}, []
            while j < len(lin) and (lin[j].startswith("   ") or not lin[j].strip()):
                mo = re.match(r"^\s+:([^:]+):\s*(.*)$", lin[j])
                if mo and not cuerpo:
                    opciones[mo.group(1)] = mo.group(2)
                else:
                    cuerpo.append(lin[j][3:] if lin[j].startswith("   ") else "")
                j += 1
            while cuerpo and not cuerpo[-1].strip():
                cuerpo.pop()
            while cuerpo and not cuerpo[0].strip():
                cuerpo.pop(0)
            tit = _inline(arg, pagina, md) if arg else None
            if nombre == "csv-table":
                if "file" in opciones:
                    f = _resolver(opciones["file"], rst)
                    filas = list(csv.reader(io.StringIO(f.read_text(encoding="utf-8-sig")))) if f.exists() else []
                else:
                    filas = list(csv.reader(io.StringIO("\n".join(cuerpo)), skipinitialspace=True))
                out += [_tabla_md(filas, tit), ""]
            elif nombre == "list-table":
                filas, act, parrafo = [], None, False
                for c in cuerpo:
                    if c.startswith("* - "):
                        act = [c[4:]]; filas.append(act); parrafo = False
                    elif c.startswith("  - ") and act is not None:
                        act.append(c[4:]); parrafo = False
                    elif not c.strip():
                        parrafo = act is not None           # el siguiente texto de la celda es otro párrafo
                    elif c.strip().startswith(".. "):
                        continue                            # clases de estilo dentro de la celda (rst-class)
                    elif act is not None:
                        act[-1] += ("<br>" if parrafo else " ") + c.strip()
                        parrafo = False
                out += [_tabla_md([[_inline(x, pagina, md) for x in f] for f in filas], tit), ""]
            elif nombre == "container":
                out += convertir(rst, md, pagina, lineas=cuerpo) + [""]
            elif nombre == "include":
                f = _resolver(arg, rst)
                if f.exists():
                    out += convertir(f, md, pagina)
            elif nombre == "raw":
                if "file" in opciones:
                    f = _resolver(opciones["file"], rst)
                    if f.exists():
                        out += [_html_limpio(f), ""]
            elif nombre in ("figure", "image"):
                f = _resolver(arg, rst)
                out += ["![%s](%s)" % (opciones.get("alt", f.stem), _ruta(md, f)), ""]
                out += [_inline(c, pagina, md) for c in cuerpo] + [""]
            elif nombre == "rubric":
                out += ["#### %s" % tit, ""]
            elif nombre in ("important", "note", "warning", "admonition", "tip"):
                for c in ([arg] if arg else []) + cuerpo:
                    out.append("> " + _inline(c, pagina, md) if c.strip() else ">")
                out.append("")
            elif nombre == "toctree":
                for c in cuerpo:
                    ref = c.strip()
                    if not ref or ref.startswith(":"):
                        continue
                    hijo = rst.parent / (ref + ".rst")
                    if not hijo.exists():
                        hijo = rst.parent / ref / "index.rst"
                    if hijo.exists():
                        out.append("- [%s](%s)" % (_titulo_de_rst(hijo), _ruta(md, _md_de(hijo))))
                out.append("")
            elif nombre == "literalinclude":
                f = _resolver(arg, rst)
                out += ["```", f.read_text(encoding="utf-8").rstrip() if f.exists() else "", "```", ""]
            elif nombre in ("code-block", "code"):
                out += ["```" + arg] + cuerpo + ["```", ""]
            i = j
            continue
        if l.strip().endswith("::") and not l.strip().startswith(".."):
            previo = l.rstrip()[:-2].rstrip()
            if previo:
                out += [_inline(previo + ":", pagina, md), ""]
            j, bloque = i + 1, []
            while j < len(lin) and (lin[j].startswith("   ") or not lin[j].strip()):
                bloque.append(lin[j][3:] if lin[j].startswith("   ") else "")
                j += 1
            while bloque and not bloque[-1].strip():
                bloque.pop()
            while bloque and not bloque[0].strip():
                bloque.pop(0)
            out += ["```"] + bloque + ["```", ""]
            i = j
            continue
        if l.startswith(".. ") or l.strip() == "..":
            i += 1
            continue
        mm = re.match(r"^(\s*)#\.\s+(.*)$", l)
        out.append("%s1. %s" % (mm.group(1), _inline(mm.group(2), pagina, md)) if mm else _inline(l, pagina, md))
        i += 1
    return out


def exportar():
    """Escribe docs/github con una página Markdown por página de la documentación y docs/README.md."""
    global SUB
    SUB = _sustituciones()
    paginas = [r for r in sorted(DOCS.rglob("*.rst"))
               if r.relative_to(DOCS).parts[0] not in ("_generado", "_build", "_static", "github")]
    for rst in paginas:
        md = _md_de(rst)
        md.parent.mkdir(parents=True, exist_ok=True)
        texto = re.sub(r"\n{3,}", "\n\n", "\n".join(convertir(rst, md))).strip() + "\n"
        md.write_text(texto, encoding="utf-8")
    (DOCS / "README.md").write_text(
        "# Documentación\n\n"
        "La documentación está publicada en <https://ecmaedmcc.github.io/EnergyArt6/>. La versión para leer en GitHub, "
        "con tablas, fichas y figuras, está en [docs/github](github/README.md).\n",
        encoding="utf-8")
    print("  documentación para GitHub en docs/github (%d páginas)" % len(paginas))
