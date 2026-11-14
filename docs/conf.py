# Configuración de Sphinx de la documentación de los escenarios de Artículo 6 (sector energía,
# modelo OSeMOSYS de la Segunda NDC del Ecuador). Sigue la estructura de la documentación del
# modelo OSeMOSYS del Ecuador (ECU_OSeMOSYS): un solo índice numerado, figuras y tablas numeradas.
import os

project = 'Escenarios de Artículo 6 · sector energía del Ecuador'
copyright = '2026, Consultor para el PNUD (escenarios de Artículo 6). Derechos de autor 2025, Climate Lead Group (modelo base)'
author = 'Mario Alejandro Heredia Salgado'
release = 'V2 (13-10-2026)'
version = 'V2'
language = 'es'

extensions = []
templates_path = ['_templates']
# _generado lo escribe la cadena del modelo en cada corrida; sus archivos entran por include, raw y
# csv-table, nunca como páginas sueltas
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store', '_generado']

numfig = True
numfig_format = {'figure': 'Figura %s', 'table': 'Tabla %s', 'code-block': 'Listado %s', 'section': 'Sección %s'}
numfig_secnum_depth = 1

# sustituciones con el alcance y las cifras de contexto de la corrida documentada
_corrida = os.path.join(os.path.dirname(os.path.abspath(__file__)), '_generado', 'corrida.rst')
rst_prolog = open(_corrida, encoding='utf-8').read() if os.path.exists(_corrida) else ''

html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']
html_css_files = ['energyart6.css']   # paleta del proyecto, Fira Sans y medida de lectura
html_js_files = ['interactivas.js']
html_title = 'Escenarios de Artículo 6 · Ecuador'
html_theme_options = {
    'style_nav_header_background': '#1F2A44',
    'prev_next_buttons_location': 'bottom',
    'collapse_navigation': False,
    'navigation_depth': 3,
}
# enlace «Editar en GitHub»: se activa con las variables de entorno DOCS_GITHUB_USER y DOCS_GITHUB_REPO (cuenta y
# repositorio donde se publique); sin ellas no se muestra
if os.environ.get('DOCS_GITHUB_USER') and os.environ.get('DOCS_GITHUB_REPO'):
    html_context = {
        'display_github': True,
        'github_user': os.environ['DOCS_GITHUB_USER'],
        'github_repo': os.environ['DOCS_GITHUB_REPO'],
        'github_version': 'main',
        'conf_py_path': '/docs/',
    }
