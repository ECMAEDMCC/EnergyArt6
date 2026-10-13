Emisiones nacionales y metas de la Segunda NDC
==============================================

El modelo de energía representa uno de los cinco sectores de mitigación de la Segunda NDC. El margen
frente a la meta se mide en el balance nacional. Por eso el análisis usa el tendencial nacional, las metas
publicadas y el inventario observado.

Meta, línea base y métrica de la Segunda NDC
--------------------------------------------

- Una sola meta, en |anio_meta|, para los cinco sectores de mitigación: Energía, Procesos Industriales,
  Agricultura, USCUSS y Residuos. El periodo de implementación va del 1 de enero de 2026 al 31 de
  diciembre de 2035 (sec. 4.3.2).
- Reducción incondicional de |meta_inc_kt| kt CO2e y condicional de |meta_con_kt| kt adicionales frente
  al escenario tendencial al final del periodo (sec. 4.2.4 y 4.4.1). La NDC las publica redondeadas como
  7 % y 8 %. Frente al tendencial de |tendencial_2035| kt equivalen al |pct_inc| y al |pct_con|. El
  análisis usa las cifras en kt, porque el indicador de referencia de la NDC se expresa en kt CO2e frente
  a la línea base al final del periodo.
- Año base 2010. Línea base: el tendencial de la Primera NDC proyectado a 2035 y, para USCUSS, las
  proyecciones del INGEI desde 2010. Métrica: GWP-100 del AR5.

Tendencial, metas e inventario
------------------------------

.. include:: /_generado/fig_g18_referencias.rst

.. include:: /_generado/fig_g11_peso_energia.rst

.. csv-table:: Peso del sector energía en las trayectorias nacionales (kt CO2e)
   :file: /_generado/peso_sector_energia.csv
   :header-rows: 1

Conciliación con las metas publicadas
-------------------------------------

La agregación nacional del Modelo CLG reduce |reduccion_modelada| kt CO2e en 2035, |exceso_modelado| kt
más que la meta condicional publicada. El tendencial es retroactivo, porque excluye obras de la Primera
NDC que ya operan. En el sector energía, esa construcción explica |retro_energia| kt de la diferencia
entre el tendencial y la referencia incondicional en 2035. El análisis mide el margen con las metas
publicadas (hoja ``Art6_Headroom``) y no cuenta la reducción que la NDC no compromete (:doc:`methods`).
