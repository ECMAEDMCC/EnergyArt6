Estructura del modelo
=====================

Convenciones
------------

.. list-table::
   :header-rows: 1
   :widths: 28 72

   * - Elemento
     - Convención
   * - Horizonte
     - 2010-2035, paso anual. La ventana de transacciones del análisis es |ventana|.
   * - Resolución intraanual
     - Un solo bloque horario, con ``YearSplit = 1``: cada año es un único periodo y el modelo no
       distingue estaciones, días ni horas. La ficha de supuestos comunes de :doc:`2_scenarios` lee
       los bloques del ``_Input.csv`` de cada escenario.
   * - Región
     - ``ECU``, nodo único nacional.
   * - Energía y actividad
     - PJ (petajulios). 1 PJ = 277,78 GWh.
   * - Capacidad
     - GW en el modelo, MW en tablas y gráficas.
   * - Relación capacidad-actividad
     - ``CapacityToActivityUnit``: PJ que produce 1 GW que opera todo el año (valor en el datafile).
   * - Emisiones
     - Mt CO2e en el modelo, kt CO2e en tablas y gráficas.

Conjuntos del modelo
--------------------

Los conjuntos salen de ``B1_Model_Structure.xlsx``. Sus nombres vienen de los clasificadores de A1 y de
la parametrización ``A-O_Parametrization.xlsx``. El tipo de planta es la familia con la que el análisis
agrupa las centrales.

.. csv-table:: Tecnologías del modelo
   :file: /_generado/tecnologias.csv
   :header-rows: 1
   :widths: 14 46 22 18

.. csv-table:: Combustibles del modelo
   :file: /_generado/combustibles.csv
   :header-rows: 1
   :widths: 20 80

.. csv-table:: Emisiones del modelo y su entrada en las emisiones del sector energía
   :file: /_generado/emisiones.csv
   :header-rows: 1
   :widths: 20 15 35 30

Variables de resultado
----------------------

Las variables de resultado salen de la solución de glpsol, en el ``_Output.csv`` de cada escenario
(``Energy/Executables/<ESC>_0``). Ese archivo es la fuente de resultados del análisis.

.. list-table::
   :header-rows: 1
   :widths: 30 52 18

   * - Variable
     - Qué mide
     - Unidad
   * - ``AnnualEmissions``
     - Emisiones anuales por componente (``CO2e_DE`` demanda final, ``CO2e_PP`` generación eléctrica,
       ``CO2e_FUG`` fugitivas, ``CO2e_REF`` refinación, y los gases por separado).
     - Mt CO2e
   * - ``AnnualTechnologyEmission``
     - Emisiones anuales por tecnología y componente, base del desglose por subsector.
     - Mt CO2e
   * - ``ProductionByTechnology``
     - Producción anual de cada tecnología por combustible de salida.
     - PJ
   * - ``TotalTechnologyAnnualActivity``
     - Actividad anual de cada tecnología. Con el piso del datafile da la térmica desplazable.
     - PJ
   * - ``TotalCapacityAnnual``
     - Capacidad total disponible en el año.
     - GW
   * - ``NewCapacity``
     - Capacidad nueva instalada en el año.
     - GW

Indicadores derivados
---------------------

``Art6_motor/analizar.py`` calcula los indicadores sobre el ``_Output.csv`` de cada escenario.

.. list-table::
   :header-rows: 1
   :widths: 30 52 18

   * - Indicador
     - Definición
     - Unidad
   * - Emisiones del sector energía
     - 1 000 × (``CO2e_DE`` + ``CO2e_PP`` + ``CO2e_FUG`` + ``CO2e_REF``), de ``AnnualTechnologyEmission``.
     - kt CO2e
   * - Generación eléctrica
     - Producción de las centrales en electricidad de red (``E1ELE``) y distribuida (``E3ELE``) ×
       277,78, agrupada en familias tecnológicas.
     - GWh
   * - Cuota ERNC
     - Generación eólica, solar, de biomasa y geotérmica sobre la generación eléctrica total. La
       hidroeléctrica no es ERNC.
     - %
   * - Factor de planta
     - Generación / (capacidad × 8,76).
     - %
   * - Reducción de una capa
     - Emisiones de la base menos las del escenario, sumadas en |ventana|.
     - kt CO2e
   * - Térmica desplazable
     - Generación térmica por encima de su piso de despacho obligatorio (:doc:`../methods`).
     - GWh
   * - Margen
     - Meta incondicional nacional del año menos la trayectoria nacional del escenario
       (:doc:`../methods`).
     - kt CO2e
   * - Sobreventa
     - Exceso de las emisiones nacionales ajustadas sobre la meta incondicional cuando ocurre una
       prueba de estrés después de autorizar ITMO.
     - kt CO2e
   * - Ingresos
     - Volumen × precio, fuera del modelo.
     - millones de US$

Estructura del repositorio
--------------------------

La carpeta ``Energy`` conserva la estructura de la cadena del Modelo CLG (repositorio
``clg-admin/ECU_NDC``) y agrega la calibración propia y la etapa de Artículo 6.

.. code-block:: text

   ejecutar_modelo.bat                     ejecución de la cadena (B1, B2 y B3)
   environment.yml, requirements.txt       entorno conda «osemosys» y dependencias
   docs/                                   esta documentación
   Energy/
   ├── A1_Inputs/, A1_Outputs/             A1: estructura del modelo (no se corre)
   ├── A1_Model_Structure_Energy.py
   ├── A2_Extra_Inputs/, A2_Output_Params/  A2: parámetros por escenario. INCA6, CONA6, INCA6G y CONA6G con carpeta propia
   ├── A2_Compiler.py, A2_Structure_Lists.xlsx
   ├── B1_Base_Scenarios_Adj_Parallel.py   B1: genera los datafiles y los resuelve con glpsol (paso 1)
   ├── B1_Scenario_Config.xlsx             todos los escenarios y, al final, las hojas Art6_*
   ├── B1_Default_Param.xlsx, B1_Model_Structure.xlsx, _GDP_Ref.xlsx
   ├── B1_Output_Params/<ESC>/             parámetros finales de cada escenario
   ├── Executables/<ESC>_0/                datafile, entradas y salidas de cada escenario
   ├── B2_Results_Creator_f0.py            B2: reúne todo en ECUInput.csv y ECUOutput.csv (paso 2)
   ├── B3_Etapa_Art6.py                    B3: verificación, manifiesto y análisis de Artículo 6 (paso 3)
   ├── B2_Output_Art6/                     resultados de B3: tablas, gráficas, tablero, cifras y verificación
   ├── B3_Visualizador_Art6.ipynb          gráficas interactivas para la decisión
   ├── Art6_motor/                         código de la etapa de Artículo 6 y scripts de la corrida
   ├── Art6_calibracion/                   calibración propia, generador de escenarios y registro (LEEME.md)
   ├── Insumos_Art6/                       agregación nacional, energía por escenario y datos del Modelo CLG, iniciativas e INGEI
   ├── tests/                              validación del libro, no regresión y base congelada
   ├── registros/                          registro de cada corrida de ejecutar_modelo.bat (no se versiona)
   ├── glpk/                               solver GLPK 4.65
   └── OSeMOSYS_Model.txt                  formulación OSeMOSYS de la NDC (GNU MathProg)

La etapa de Artículo 6 es un paso aparte, ``B3_Etapa_Art6.py``, que se corre después de B1 y no
modifica nada de lo que produce el modelo.

Relación con la cadena del Modelo CLG
-------------------------------------

Los scripts de la cadena (A1, A2, B1 y B2) y la formulación ``OSeMOSYS_Model.txt`` son los del
repositorio del Modelo CLG, sin cambios. El trabajo del Artículo 6 entra por configuración: filas
propias en ``B1_Scenario_Config.xlsx``, carpetas propias en ``A2_Output_Params`` y la etapa B3. Las 927
fórmulas del libro original se fijaron a su valor en caché, que es el que lee B1, para que el libro
pueda editarse sin perder valores.

Los códigos de escenario usan guion (``A-CCOFF``) porque B1 deduce el escenario cortando el nombre de
la carpeta en el primer guion bajo.
