Resultados del modelo
=====================

Las gráficas salen del modelo OSeMOSYS de la Segunda NDC con la base corregida. Usan los escenarios de
``Energy/B1_Scenario_Config.xlsx`` y las salidas de cada escenario en ``Energy/Executables``. También
están en el tablero `tablero_art6.html <../_static/tablero_art6.html>`_, un solo archivo que funciona
sin internet.

Emisiones del sector energía
----------------------------

.. include:: /_generado/fig_g20_escalera.rst

.. include:: /_generado/fig_g03_energia_escenarios.rst

.. include:: /_generado/fig_g04_reduccion_anual.rst

.. include:: /_generado/fig_g05_emisiones_generacion.rst

.. include:: /_generado/fig_g06_subsectores.rst

.. csv-table:: Emisiones del sector energía por escenario (kt CO2e)
   :file: /_generado/emisiones_energia_kt.csv
   :header-rows: 1

.. csv-table:: Descomposición de las reducciones, |ventana| (kt CO2e)
   :file: /_generado/descomposicion_reducciones.csv
   :header-rows: 1

.. csv-table:: Marco 2026-2035: corrección de la base y capas de cada escalón (kt CO2-eq)
   :file: /_generado/marco_2026_2035.csv
   :header-rows: 1

.. csv-table:: Capas de cada escalón bajo cada estado (kt CO2-eq)
   :file: /_generado/capas_por_estado.csv
   :header-rows: 1

.. csv-table:: Puentes V7: capas de la versión del 08-10-2026, de las mismas palancas sobre CONA6 y de los escenarios vigentes (kt CO2-eq)
   :file: /_generado/puente_v7.csv
   :header-rows: 1

Matriz eléctrica
----------------

.. include:: /_generado/fig_g07_generacion.rst

.. include:: /_generado/fig_g08_capacidad.rst

.. include:: /_generado/fig_g09_ernc.rst

.. csv-table:: Cuota de la ERNC en la generación (%)
   :file: /_generado/cuota_ernc_pct.csv
   :header-rows: 1

.. csv-table:: Térmica desplazable por escenario (GWh)
   :file: /_generado/termica_desplazable_GWh.csv
   :header-rows: 1

.. csv-table:: Factor de emisión del MWh desplazado frente al margen de operación de 2025 (t CO2/MWh)
   :file: /_generado/factor_desplazado_frente_al_margen.csv
   :header-rows: 1

.. csv-table:: Solución de glpsol y huellas de cada escenario
   :file: /_generado/solucion_por_escenario.csv
   :header-rows: 1
