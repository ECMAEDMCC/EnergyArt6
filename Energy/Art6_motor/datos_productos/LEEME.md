# Datos de los Productos 1 a 4

Entradas del motor para las secciones de demanda, cartera, remociones y síntesis del tablero de resultados
(`tablero.py` con `productos.py`). Las escribe `extraer_productos.py` desde el tablero de los Productos 1 a 4; no se
editan a mano.

| Dato | Valor |
|---|---|
| Origen | tablero de los Productos 1 a 4, versión V8: componente React `dashboard_demanda_art6_V8 (1).jsx` |
| md5 del origen | `7e25958ad2478b737075d1f0de11ab67` |
| Fecha del archivo de origen | 13-10-2026 |
| Fecha de extracción | 13-10-2026 |

| Archivo | Contenido |
|---|---|
| `demanda.json` | 167 registros de demanda del Capítulo 1 (bloque DATA: JCM, Suiza, otros compradores y CORSIA), escalera N0-N5 y macroestructura de la demanda |
| `remociones.json` | 11 arquetipos de remoción del Capítulo 3 (bloque CDR), con los filtros y su horizonte de mercado |
| `cartera_agregada.json` | cartera del Capítulo 2 (bloque PORT, 68 iniciativas) contada por sector, veredicto, actividad, tramo de la NDC y canal de demanda |
| `sintesis.json` | 13 actividades que pasan todos los filtros (Capítulo 4) con su número de iniciativas |

Reglas de publicación (13-10-2026):

- La cartera entra solo agregada, como número de iniciativas por actividad y veredicto, sin nombres de proyecto, sin
  códigos y sin potenciales. Ni esta carpeta ni el código que la escribe contienen el detalle de la cartera por
  iniciativa: el script lo lee en memoria y comprueba, antes de escribir, que ningún nombre ni código aparezca en
  las salidas.
- Los textos extraídos se limpian de las siglas de programas de terceros que el tablero público no cita, y del
  retorno de carro que deja Excel (`_x000D_`).

Para rehacer, desde `Energy/Art6_motor`: `python extraer_productos.py <ruta del .jsx>` y después `python tablero.py`.
