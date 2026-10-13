Metodología
===========

El modelo OSeMOSYS estima las emisiones del sector energía de cada escenario. Las reglas de
contabilidad, el margen frente a la meta, la sobreventa y los ingresos se calculan fuera del modelo,
sobre sus resultados.

Base corregida
--------------

Las referencias |inc| y |con| son los escenarios NDCINC y NDCCON del Modelo CLG con carpeta de
parámetros propia (``Energy/A2_Output_Params/INCA6`` y ``CONA6``). Llevan además las correcciones K01 a
K16 de ``Energy/Art6_calibracion/correcciones_K.csv``, donde cada fila nombra el parámetro, la
tecnología, los años, los valores y su fuente. Las referencias INCA6G y CONA6G repiten la base sin la
expansión a gas declarada (G01) y dan el rango de gas.

Las correcciones llevan a lo observado la hidroelectricidad, la biomasa, el biogás, la eólica, la solar y
la térmica de 2010-2025 (Balance Energético Nacional 2025, CENACE y ARCONEL). También recalculan los
factores de emisión de las térmicas con los factores del IPCC 2006 y el potencial de calentamiento del
AR5. Por último, anclan la térmica de autoproductores a su media observada 2023-2025 y limitan la
inversión térmica nueva de la red a la expansión declarada.

Construcción de los escenarios
------------------------------

Los escenarios se generan en la cadena del Modelo CLG, desde ``B1_Scenario_Config.xlsx``
(:doc:`0_energy/2_scenarios`). Cada escenario de Artículo 6 es un escenario basado en |con|, o en CONA6G
en la familia GAS. B1 copia la base y aplica las filas propias del escenario en las hojas Electrical,
SmartGrid y Efficiency. Esas filas son vectores completos 2010-2035 que conservan la historia de la base.
Cada estado de riesgo aplica a su base la razón que declara (año seco, Coca Codo, situación de 2026).

Fuente de los resultados
------------------------

Las cifras de resultados salen del ``_Output.csv`` de cada escenario en ``Energy/Executables``. Los
parámetros de entrada salen de su ``_Input.csv`` y de su datafile. Queda fuera del análisis el escenario
sin solución óptima o cuya salida es anterior a su datafile.

Papel de cada escenario en el análisis
--------------------------------------

El papel de cada escenario sale de la hoja ``Art6_Roles`` y de la definición que usa B1 (hoja
``Scenarios``):

- Referencias corregidas: |inc| y |con|. |con| es la base de |escalera| y la referencia de sus capas.
- Escenarios del Modelo CLG: NDCINC, NDCCON y el tendencial BAU1NDC, que usa la agregación nacional.
- Escalera de Artículo 6: |escalera|. Cada escalón contiene al anterior.
- Estados: los escenarios con código ``<escalón>-<estado>``. Los estados de riesgo llevan el respaldo de
  emergencia y son estos: |pruebas|.
- Sensibilidades: estados que se miden frente a su propia referencia (CONA6P sin pisos térmicos, CONA6I
  sin importación, CONA6G sin la expansión a gas). Son las siguientes: |sensibilidades|.
- Puentes A-V7, B-V7 y C-V7: las palancas de la versión del 08-10-2026 sobre |con|, para separar el
  efecto de la base del efecto de las decisiones posteriores.

Emisiones del sector energía
----------------------------

Las emisiones del sector energía son la suma de los componentes CO2e de demanda final, generación
eléctrica, fugitivas y refinación (``CO2e_DE``, ``CO2e_PP``, ``CO2e_FUG`` y ``CO2e_REF``) de
``AnnualTechnologyEmission``, en kt CO2-eq. Las demás variables y sus unidades están en
:doc:`0_energy/0_structure`.

Capas de reducción
------------------

A cada escalón se le atribuye solo la capa que agrega: su diferencia de emisiones frente a su base,
sumada en |ventana|. La capa del A se mide frente a |con|, la del B frente al A y la del C frente al B.
Las cifras de cada capa están en :doc:`0_energy/3_results` y en :doc:`1_art6/0_potential`.

Una tonelada de una capa formada por líneas de la NDC condicional, transferida con ajuste
correspondiente, deja de contar para la meta condicional. En cambio, una tonelada de una capa formada
por líneas fuera de la NDC no consume ninguna meta si demuestra su adicionalidad.

Puente de la base
-----------------

La diferencia de emisiones entre |con| y NDCCON es el efecto de la calibración propia. Se informa como
puente, por año y en |ventana|, con su desglose por grupo de correcciones
(``Energy/Art6_calibracion/calibracion_e_desglose_puente.csv``). La sensibilidad de gas da el rango del
puente entre |con| y CONA6G.

Margen frente a la meta incondicional
-------------------------------------

El margen se ancla en las metas que publica la Segunda NDC (sec. 4.2.4). Son una reducción incondicional
de |meta_inc_kt| kt CO2-eq y una condicional de |meta_con_kt| kt adicionales, ambas en |anio_meta| y sobre
el tendencial nacional. En |anio_meta|, ese tendencial es de |tendencial_2035| kt CO2-eq. Las metas
equivalen al |pct_inc| y al |pct_con| del tendencial, y la NDC las publica redondeadas como 7 % y 8 %. Los
valores están en la hoja ``Art6_Headroom``.

- La meta incondicional de cada año sigue una senda lineal desde |anio_inicio_senda|, año en que la
  reducción es cero, hasta |anio_meta|. La meta condicional sigue la misma senda con la suma de las dos
  reducciones. La senda es un supuesto de cálculo, porque la NDC publica una sola meta, en |anio_meta|.
- Regla condicional: la trayectoria nacional de un escenario es la senda de la meta condicional más la
  diferencia del sector energía entre el escenario y la referencia condicional. Supone que los otros
  cuatro sectores cumplen el condicional que la NDC compromete.
- Regla prudente: la trayectoria parte de la senda de la meta incondicional más la diferencia del
  sector energía frente a la referencia incondicional. Supone que los otros sectores solo cumplen su
  incondicional.
- Proyecciones de esa diferencia: la del Modelo CLG y la corregida. La del Modelo CLG mide cada escenario
  frente a la referencia corregida (|con| o |inc|) y deja fuera la reducción que solo resulta de la
  calibración. La corregida lo mide frente a NDCCON o NDCINC y la incluye.
- El margen es la meta incondicional menos la trayectoria nacional. La lectura que dimensiona la
  autorización es la proyección del Modelo CLG con la regla prudente.

La agregación nacional modelada del Modelo CLG (``Energy/Insumos_Art6/Emisiones Totales.xlsx``) reduce
más de lo que la NDC compromete. Su condicional queda en |condicional_2035| kt CO2-eq en 2035,
|reduccion_modelada| kt bajo el tendencial y |exceso_modelado| kt por debajo de la meta condicional
publicada. El análisis no cuenta ese exceso, porque el país no lo compromete.

Oferta de Artículo 6
--------------------

La oferta de cada año suma bloques por nivel de adicionalidad, según la hoja ``Art6_Adicionalidad``:

- Firme: las líneas con adicionalidad «Firme», con su potencial declarado (|firmes|).
- Por demostrar dentro de la NDC: la capa del A (modelo) y las líneas «Por demostrar» con potencial
  declarado que los compradores potenciales clasificaron como «Condicionada». Esas líneas son las
  siguientes: |condicionadas_declaradas|.
- Por demostrar fuera de la NDC: las capas del B y del C (modelo).

La oferta se informa en tres casos. El caso central usa la base corregida y la expansión a gas
declarada. Una sensibilidad usa los pisos térmicos del Modelo CLG (corrida del 12-10-2026, en
``Energy/Art6_calibracion/sensibilidad_pisos_CLG_2026-10-12``). La otra retira la expansión a gas
declarada (familia GAS sobre CONA6G) y no es un nivel de oferta.

Las líneas en reserva quedan fuera de la oferta mientras no se demuestre su adicionalidad regulatoria
(EN32). Sobre la oferta se calculan cuatro subconjuntos: toda la oferta con EN32, toda sin EN32, la
lista blanca de líneas que validaron los expertos consultados y solo la línea firme.

Sobreventa
----------

Se supone que el país autoriza, con el sistema intacto, la oferta de cada año de reducción. Si después
ocurre un estado de riesgo, las emisiones nacionales ajustadas (las del escenario bajo el riesgo más los
ITMO ya transferidos) pueden superar la meta incondicional. Ese exceso es la sobreventa. Lo que el país
excede su meta aun sin transferir se informa aparte como incumplimiento propio. La sobreventa se calcula
con dos métodos de ajuste correspondiente para una meta de un solo año:

- Método anual: la meta incondicional de cada año de |ventana| se compara con las emisiones ajustadas
  de ese año. Es la prueba exigente.
- Método de promedio: el ajuste de |anio_meta| es la suma transferida en el periodo dividida entre los
  diez años de la NDC.

La reserva por año de reducción es la parte de la oferta de cada año que no conviene autorizar ex ante.
Se calcula con la sobreventa de cada estado de referencia: ACT, ACT-DEM y la salida de Coca Codo sola. El
autorizable ex post de cada año es el menor entre la reducción del estado observado, el margen y la
oferta de ese año.

Respaldo de emergencia
----------------------

Los estados de riesgo llevan el grupo de palancas RESP: tope de PPFOI liberado desde 2026, costo de
capital y costo fijo de PPFOI por 1 000 y STOELE cerrado en 2026-2035. Es un supuesto de cierre, como la
térmica arrendada que el país contrata hoy. El modelo construye solo la potencia de fuel oil que le falta
para atender la demanda.

Esa potencia se informa en MW equivalentes con el factor de planta de PPFOI (0,4254), con su energía y
sus emisiones. También se expresa en horas de corte equivalentes. La energía no suministrada equivalente
es el respaldo por las eficiencias de transmisión y distribución del datafile, y las horas son esa
energía sobre la demanda eléctrica final. El modelo tiene un solo bloque horario y no ve la punta.

Térmica desplazable
-------------------

La térmica desplazable es la generación térmica por encima de su piso de despacho obligatorio, lo único
que una renovable adicional puede sustituir. Se calcula por tecnología térmica como su producción
eléctrica multiplicada por la fracción de la actividad que supera el piso del datafile.

Ingresos
--------

Los ingresos son volumen por precio y se calculan fuera del modelo, con las referencias de la hoja
``Art6_Precios``: |precios|. Los precios de mercado cambian rápido y deben actualizarse antes de publicar.
