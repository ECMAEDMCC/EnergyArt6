Insumos y parámetros
====================

Definición de los parámetros de entrada
---------------------------------------

Los parámetros se definen en ``B1_Scenario_Config.xlsx`` y en ``A2_Output_Params`` y quedan, escenario
por escenario, en ``Executables/<ESC>_0/<ESC>_0.txt`` (datafile), ``<ESC>_0_Input.csv`` y
``B1_Output_Params/<ESC>/``.

.. list-table::
   :header-rows: 1
   :widths: 34 50 16

   * - Parámetro
     - Qué fija
     - Unidad
   * - ``TotalTechnologyAnnualActivityUpperLimit``
     - Techo de actividad: producción máxima de la tecnología en el año.
     - PJ/año
   * - ``TotalTechnologyAnnualActivityLowerLimit``
     - Piso de actividad: producción mínima de la tecnología en el año.
     - PJ/año
   * - ``CapacityFactor``
     - Fracción de la capacidad instalada disponible en el año. Con un solo bloque horario equivale
       al factor de planta anual máximo.
     - fracción (0-1)
   * - ``TotalAnnualMinCapacityInvestment``
     - Capacidad nueva mínima que debe instalarse en el año.
     - GW
   * - ``ResidualCapacity``
     - Capacidad existente que no requiere inversión del modelo.
     - GW

Palancas de los escenarios
--------------------------

Cada palanca es una fila de la hoja ``Electrical`` cuya descripción empieza con su código entre
corchetes. Las hojas ``Art6_Palancas`` y ``Art6_Adicionalidad`` documentan qué fija, qué iniciativa
representa, su adicionalidad y su fuente. Los valores de 2030 y 2035 se leen del datafile de un
escenario que la usa.

.. include:: /_generado/palancas.rst

Parámetros de entrada por escenario
-----------------------------------

La tabla recoge los techos y pisos de actividad en PJ/año y los factores de planta como fracción de la
capacidad. Son los valores de 2035 tal como el modelo los recibió (``_Input.csv`` de cada escenario). La
columna hidroeléctrica media es el promedio simple de las clases hidroeléctricas. La matriz interactiva,
con el año desde el que rige cada cambio, está en :doc:`2_scenarios`.

.. csv-table:: Parámetros de entrada de 2035 por escenario
   :file: /_generado/supuestos_escenarios.csv
   :header-rows: 1

Pruebas de estrés
-----------------

Cada prueba cambia solo las filas de sus palancas: hidroeléctricas, de importación o de demanda, y las
del respaldo de emergencia. Sus mecanismos, su procedencia y su validación están en la hoja
``Art6_Riesgos``.

.. csv-table:: Pruebas de estrés (hoja Art6_Riesgos)
   :file: /_generado/riesgos.csv
   :header-rows: 1
   :widths: 8 16 6 22 16 14 18

El régimen seco multiplica el factor de planta, el piso y el techo de actividad de cada clase
hidroeléctrica por una razón de caudales. La razón divide los caudales medios de 2024 entre los caudales
históricos de las series del CENACE de sus centrales (Informe Anual 2024, tabla 1.14). Las series se
ponderan por la potencia nominal de cada central en la capa CENTRALES de ARCONEL. Las clases sin central
medida heredan la razón de una clase vecina o el promedio nacional ponderado por caudal.

El repositorio no lleva filas por central. La razón de cada clase está en
``Energy/Art6_calibracion/parametros_hidro_por_clase.csv`` (derivado de CENTRALES.shp de ARCONEL, uso
autorizado). El estado ACT toma de ese mismo archivo la razón 2026/2025 de cada clase.

.. csv-table:: Razón aplicada por clase hidroeléctrica (hoja Art6_AnoSeco)
   :file: /_generado/anoseco_clases.csv
   :header-rows: 1

Situación eléctrica de 2026
---------------------------

Los estados ACT y ACT-DEM anclan 2026 a lo observado: demanda eléctrica, hidrología por clase, factor de
planta de Coca Codo Sinclair e importación desde Colombia. Los datos salen de documentos de CENACE y XM,
recogidos en ``act_2026_observado.csv``. La tabla contrasta 2025 y 2026 del modelo con lo observado.

.. csv-table:: 2025 y 2026 del modelo frente a lo observado (estados ACT y ACT-DEM)
   :file: /_generado/act_2026_contraste.csv
   :header-rows: 1

Calibración propia
------------------

Las correcciones K01 a K16 de las referencias corregidas están en
``Energy/Art6_calibracion/correcciones_K.csv``, una fila por corrección con su fuente. Sus contrastes
con el Balance Energético Nacional 2025 y con el INGEI están en ``calibracion_a_tabla5.csv`` a
``calibracion_g_suficiencia_termica.csv``.

Archivos de insumo
------------------

.. list-table::
   :header-rows: 1
   :widths: 35 65

   * - Archivo
     - Uso
   * - ``Energy/Insumos_Art6/Emisiones Totales.xlsx``
     - Agregación nacional del Modelo CLG de los cinco sectores (tendencial, incondicional y
       condicional), copia sin cambios de ``PowerBI/Nacionales`` del repositorio original. Fuente del
       margen nacional.
   * - ``Energy/Insumos_Art6/ECUOutput_Energy.csv``
     - Salida de energía del Modelo CLG por escenario, que usa la agregación nacional (BAU1NDC, NDCINC y
       NDCCON), copia sin cambios de ``PowerBI/Energy`` del repositorio original.
   * - ``Energy/Insumos_Art6/Energy.xlsx``
     - Proyectos, capacidad, factores de planta y generación del Modelo CLG que usa la calibración propia,
       copia sin cambios de ``Data/`` del repositorio original.
   * - ``Energy/Insumos_Art6/Energia_oficial_por_escenario_kt.csv``
     - Emisiones del sector energía del Modelo CLG por escenario, incluido BAU1NDC, el tendencial
       retroactivo que usa la agregación nacional.
   * - ``Energy/Insumos_Art6/INICIATIVAS_ENERGIA.xlsx``
     - Iniciativas de energía de la Segunda NDC con su potencial declarado.

.. csv-table:: Fuentes (hoja Art6_Fuentes)
   :file: /_generado/fuentes.csv
   :header-rows: 1
   :widths: 40 35 25

.. csv-table:: Procedencia de los insumos (Insumos_Art6/PROCEDENCIA.csv)
   :file: /_generado/procedencia.csv
   :header-rows: 1
