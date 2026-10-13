Escenarios
==========

Los escenarios de Artículo 6 son tres escalones sobre la referencia condicional corregida |con|. El A
está ligado a actividades del escenario condicional de la Segunda NDC. El B agrega oferta eléctrica que
la NDC no incluye. El C agrega la demanda del Plan de Acción del PLANMICC y la geotermia de Tufiño.

Sobre los escalones se aplican los estados de riesgo y las sensibilidades. Los estados de riesgo son
estos: |pruebas|. Las sensibilidades son las siguientes: |sensibilidades|. El contrafactual A-SIN retira
del A las actividades que financia.

Todos son escenarios basados en |con|, o en CONA6G en la familia GAS. Se definen en
``Energy/B1_Scenario_Config.xlsx`` y B1 los genera con su mecanismo propio.

.. csv-table:: Escenarios descritos en la configuración (hoja Art6_Escenarios)
   :file: /_generado/escenarios.csv
   :header-rows: 1
   :widths: 12 22 14 18 34

Definición en la cadena del Modelo CLG
--------------------------------------

La hoja ``Scenarios`` de B1 distingue dos clases de escenario. Los escenarios de referencia
(``Based_On = ref``) se construyen desde los parámetros de su carpeta en ``A2_Output_Params``. Son los
cuatro escenarios del Modelo CLG (BAU, BAU1NDC, NDCINC y NDCCON) y las cuatro referencias corregidas
(INCA6, CONA6, INCA6G y CONA6G). Los escenarios basados (``Reference = based``) parten de una copia de
otro escenario y aplican encima sus propias filas.

Las palancas están en las hojas ``Electrical`` y ``Efficiency``. Cada fila fija un parámetro de una
tecnología o una demanda, por ejemplo el techo de actividad de la eólica
(``TotalTechnologyAnnualActivityUpperLimit`` de ``PPWNDON``). Su descripción empieza con el código de la
palanca entre corchetes, como ``[A1]``. Cada palanca es un vector completo 2010-2035 que conserva la
historia de la base y cambia los años que declara. B1 redondea cada valor a cuatro decimales, como hace
con todas sus filas.

B1 copia la base antes de aplicar las hojas Electrical, SmartGrid y Efficiency. Por eso cada escenario
basado lleva también sus copias de las filas de la base en esas tres hojas. Sin ellas perdería, entre
otras cosas, los factores de emisión.

Las hojas ``Art6_*`` del mismo libro documentan la narrativa, la iniciativa, la adicionalidad y la
fuente de cada palanca. B1 no las lee. El papel de cada escenario en el análisis sale de esa definición
y de la hoja ``Art6_Roles`` (:doc:`../methods`).

Mapa de escenarios
------------------

.. raw:: html
   :file: ../_generado/escenarios_mapa.html

Ficha de cada escenario
-----------------------

.. raw:: html
   :file: ../_generado/escenarios_fichas.html

Parámetros de entrada por escenario
-----------------------------------

.. raw:: html
   :file: ../_generado/escenarios_supuestos.html

Adicionalidad y veredicto de compradores
----------------------------------------

La adicionalidad acota la oferta que los escenarios permiten imaginar. La hoja ``Art6_Adicionalidad``
clasifica cada línea de la NDC y de los escenarios por su adicionalidad y recoge el veredicto de
compradores potenciales (primera ronda de entrevistas): núcleo, condicionada o descartar. Los volúmenes
del modelo no cambian por este veredicto. Las gráficas de potencial marcan con rayado las capas cuyas
líneas quedaron en su mayoría como «Descartar». El panel de indicadores muestra aparte la oferta con
adicionalidad firme.

.. csv-table:: Líneas de la NDC y de los escenarios (hoja Art6_Adicionalidad)
   :file: /_generado/adicionalidad.csv
   :header-rows: 1
   :widths: 7 30 9 11 9 11 11 12
