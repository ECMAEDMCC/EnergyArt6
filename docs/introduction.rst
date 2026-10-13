Introducción
============

Pregunta del análisis
---------------------

¿Cuántas reducciones del sector energía podría transferir el Ecuador como resultados de mitigación de
transferencia internacional (ITMO) en |ventana| sin poner en riesgo la meta incondicional de su Segunda
NDC? ¿Qué ocurre con ese potencial bajo las pruebas de estrés del sistema hidroeléctrico y con la situación
eléctrica de 2026?

Modelo de partida y base corregida
----------------------------------

El modelo de partida es el Modelo Climate Lead Group (Modelo CLG), el modelo de energía de la Segunda NDC
que publicó Climate Lead Group en el repositorio ``clg-admin/ECU_NDC``. Sus cuatro escenarios, BAU,
BAU1NDC, NDCINC y NDCCON, se conservan sin cambios como comparación.

Las referencias del análisis son |inc| y |con|. Corresponden a NDCINC y NDCCON con una calibración propia,
las correcciones K01 a K16. La calibración lleva la generación eléctrica de 2010-2025 a lo observado en el
Balance Energético Nacional 2025, CENACE y ARCONEL, y fija los supuestos térmicos de 2026-2035. Ambas
referencias representan la Segunda NDC con la calibración corregida.

Los escenarios de Artículo 6 (|escalera|) se construyen sobre |con| y se miden frente a esa referencia. El
efecto de la calibración sobre las emisiones se informa aparte, como puente entre |con| y NDCCON
(:doc:`methods`).

Contenido del repositorio
-------------------------

- La cadena del Modelo CLG (A1, A2, B1 y B2), que genera los escenarios desde un único libro de
  configuración, ``Energy/B1_Scenario_Config.xlsx``. B1 resuelve todos los escenarios activos de la hoja
  ``Scenarios``, 52 en la configuración publicada. El análisis usa |escenarios| de ellos: las referencias,
  los escenarios de Artículo 6, las pruebas de estrés y las sensibilidades. Las pruebas de estrés son las
  siguientes: |pruebas|. Las sensibilidades son estas: |sensibilidades|.
- La calibración propia (``Energy/Art6_calibracion``), con sus fuentes y sus tablas de contraste.
- La etapa de Artículo 6 (B3), que se corre después de B1 y analiza volúmenes, margen frente a la meta,
  sobreventa, respaldo e ingresos.
- El cuaderno ``Energy/B3_Visualizador_Art6.ipynb`` y el tablero autónomo
  `tablero_art6.html <_static/tablero_art6.html>`_, que presentan cada gráfica con su guía de lectura.

Procedencia de las cifras
-------------------------

Las cifras de resultados salen de la solución de glpsol de cada escenario
(``Energy/Executables/<ESC>_0/<ESC>_0_Output.csv``). Los parámetros de entrada salen de
``<ESC>_0_Input.csv`` y del datafile ``<ESC>_0.txt``. Cada cifra, con la tabla de la que sale y el md5 de
los ``_Output.csv`` que la producen, está en ``Energy/B2_Output_Art6/cifras_finales_producto3.json``. Las
cifras principales de la corrida documentada están en :doc:`1_art6/5_cifras`.

Términos del ejercicio
----------------------

.. raw:: html
   :file: _generado/glosario.html
