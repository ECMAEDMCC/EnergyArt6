# Estructura del modelo

## Convenciones

| Elemento | Convención |
|---|---|
| Horizonte | 2010-2035, paso anual. La ventana de transacciones del análisis es 2031-2035. |
| Resolución intraanual | Un solo bloque horario, con `YearSplit = 1`: cada año es un único periodo y el modelo no distingue estaciones, días ni horas. La ficha de supuestos comunes de [Escenarios](2_scenarios.md) lee los bloques del `_Input.csv` de cada escenario. |
| Región | `ECU`, nodo único nacional. |
| Energía y actividad | PJ (petajulios). 1 PJ = 277,78 GWh. |
| Capacidad | GW en el modelo, MW en tablas y gráficas. |
| Relación capacidad-actividad | `CapacityToActivityUnit`: PJ que produce 1 GW que opera todo el año (valor en el datafile). |
| Emisiones | Mt CO2e en el modelo, kt CO2e en tablas y gráficas. |

## Conjuntos del modelo

Los conjuntos salen de `B1_Model_Structure.xlsx`. Sus nombres vienen de los clasificadores de A1 y de
la parametrización `A-O_Parametrization.xlsx`. El tipo de planta es la familia con la que el análisis
agrupa las centrales.

*Tabla. Tecnologías del modelo*

| Código | Nombre | Grupo de la parametrización | Tipo de planta |
|---|---|---|---|
| DIST_DSL | Primaria - Importación/Distribución - Diesel | Primaria |  |
| DIST_GSL | Primaria -  Importación/Distribución - Gasolina | Primaria |  |
| DIST_NGS | Primaria - Importación/Distribución - Gas Natural | Primaria |  |
| DIST_LPG | Primaria -  Importación/Distribución - GLP | Primaria |  |
| DIST_COK | Primaria -  Importación/Distribución - Coque | Primaria |  |
| DIST_KER | Primaria -  Importación/Distribución - Keroseno | Primaria |  |
| DIST_JET | Primaria -  Importación/Distribución - Jet | Primaria |  |
| DIST_FIR | Primaria - ETD - Leña | Primaria |  |
| DIST_CHA | Primaria - ETD - Carbon Vegetal | Primaria |  |
| DIST_BIM | Primaria - ETD - Biomasa | Primaria |  |
| DIST_BGS | Primaria - ETD - Biogas | Primaria |  |
| DIST_OPE | Primaria -  Importación/Distribución - OPE | Primaria |  |
| EXTT_CRU | Primaria Extracción/Transformation - Crudo | Primaria |  |
| DIST_COA | Primaria -  Importación/Distribución - Carbón | Primaria |  |
| DIST_FOI | Primaria -  Importación/Distribución - Búnker | Primaria |  |
| PPGEO | Primaria - Transformación - Geotérmica | Primaria | Geotermia |
| PPWNDON | Primaria - Transformación - Eólica | Primaria | Eólica |
| PPWNDONS | Primaria - Transformación - Eólica con Almacenamiento | Primaria | Eólica |
| PPWNDOFF | Primaria - Transformación - Eólica Offshore | Primaria | Eólica |
| PPPVT | Primaria - Transformación - Solar | Primaria | Solar |
| PPPVTS | Primaria - Transformación - Solar con almacenamiento de batería | Primaria | Solar |
| PPPVD | Primaria - Transformación - Solar Distribuida | Primaria | Solar |
| PPPVDS | Primaria - Transformación - Solar Distribuida con almacenamiento de batería | Primaria | Solar |
| ELE_TRANS | Secundaria - Transmisión de Potencia | Secundaria |  |
| ELE_DIST | Secundaria - Distribución de Potencia | Secundaria |  |
| HYD_G_PROD | Secundaria - Producción de Hidrógeno Verde | Secundaria |  |
| HYD_DIST | Secundaria - Distribución de Hidrógeno | Secundaria |  |
| STOELE | Secundaria - Transmisión de Potencia | Secundaria |  |
| PPBIM | Primaria - Transformación - Biomass | Secundaria | Biomasa y biogás |
| PPBGS | Primaria - Transformación - Biogas | Secundaria | Biomasa y biogás |
| PPNGS | Primaria - Transformación - Natural Gas | Secundaria | Gas natural |
| PPDSL | Primaria - Transformación - Diesel | Secundaria | Fuel oil y diésel |
| PPFOI | Primaria - Transformación - Búnker | Secundaria | Fuel oil y diésel |
| REF_DSL | Secundaria Refinación Diesel | Secundaria |  |
| REF_GSL | Secundaria Refinación Gasolina | Secundaria |  |
| REF_LPG | Secundaria Refinación LPG | Secundaria |  |
| REF_FOI | Secundaria Refinación Fuel Oil | Secundaria |  |
| REF_JET | Primaria -  Importación/Distribución - Jet | Secundaria |  |
| REF_OPE | Primaria -  Importación/Distribución - OPE | Secundaria |  |
| T5DSLCOM | Demand Diesel for Commercial | Demanda |  |
| T5GSLCOM | Demand Gasoline for Commercial |  |  |
| T5LPGCOM | Demand LPG for Commercial | Demanda |  |
| T5ELECOM | Demand Electric for Commercial | Demanda |  |
| T5FIRCOM | Demand Firewood for Commercial |  |  |
| T5CHACOM | Demand Charcoal for Commercial |  |  |
| T5OPECOM | Demand Other non-energy petroleum products for Commercial |  |  |
| T5DSLRES | Demand Diesel for Residential |  |  |
| T5GSLRES | Demand Gasoline for Residential | Demanda |  |
| T5LPGRES | Demand LPG for Residential | Demanda |  |
| T5ELERES | Demand Electric for Residential | Demanda |  |
| T5KERRES | Demand Kerosen for Residential | Demanda |  |
| T5FIRRES | Demand Firewood for Residential | Demanda |  |
| T5CHARES | Demand Charcoal for Residential | Demanda |  |
| T5OPERES | Demand Other non-energy petroleum products for Residential | Demanda |  |
| T5ELEPUB | Demand Electric for Public | Demanda |  |
| T5DSLIND | Demand Diesel for Industrial | Demanda |  |
| T5GSLIND | Demand Gasoline for Industrial | Demanda |  |
| T5NGSIND | Demand Natural Gas for Industrial | Demanda |  |
| T5ELEIND | Demand Electric for Industrial | Demanda |  |
| T5HYDIND | Demand Hydrogen for Industrial | Demanda |  |
| T5COKIND | Demand Coke for Industrial |  |  |
| T5BIMIND | Demand Biomass for Industrial | Demanda |  |
| T5COAIND | Demand Carbón de coque  for Industrial | Demanda |  |
| T5FOIIND | Demand Fuel Oil for Industrial | Demanda |  |
| T5DSLCON | Demand Diesel for Construction | Demanda |  |
| T5ELECON | Demand Electric for Construction | Demanda |  |
| T5FOICON | Demand Fuel Oil for Construction | Demanda |  |
| T5DSLEXP | Demand Diesel for Exports | Demanda |  |
| T5JETEXP | Demand Jet Fuel and others for Exports | Demanda |  |
| T5FOIEXP | Demand Fuel Oil for Exports | Demanda |  |
| T5JETTAE | Demand Jet Fuel and others for Transport - Aero | Demanda |  |
| T5DSLTMA | Demand Diesel for Transport - Maritime | Demanda |  |
| T5NGSTMA | Demand Natural Gas for Transport - Maritime | Demanda |  |
| T5LPGTMA | Demand LPG for Transport - Maritime | Demanda |  |
| T5ELETMA | Demand Electric for Transport - Maritime | Demanda |  |
| T5FOITMA | Demand Fuel Oil for Transport - Maritime | Demanda |  |
| T5DSLTRO | Demand Diesel for Transport - Road | Demanda |  |
| T5GSLTRO | Demand Gasoline for Transport - Road | Demanda |  |
| T5NGSTRO | Demand Natural Gas for Transport - Road | Demanda |  |
| T5LPGTRO | Demand LPG for Transport - Road | Demanda |  |
| T5ELETRO | Demand Electric for Transport - Road | Demanda |  |
| T5BGSTRO | Demand Biofuel/Biogas for Transport - Road | Demanda |  |
| T5FOITRO | Demand Fuel Oil for Transport - Road | Demanda |  |
| T4ELE_HEA | Distribute Electric for Heavy Freight | Distribución para transporte |  |
| TRXTRAIELE | Floating technology Electric | Vehículos |  |
| Techs_Rail | Floating technology | Grupos de vehículos |  |
| TRANE6NOMOT | Tecnología habilitadora de reducción de no-motorizado | Otras |  |
| PROCRU | Production - Crude | Secundaria |  |
| PPCRU | Power Plant Crude | Secundaria | Crudo, GLP e importación |
| PPRNGS | Isolated Power Plant Refinery Natural Gas | Secundaria | Gas natural |
| PPRDSL | Isolated Power Plant Refinery Diesel | Secundaria | Fuel oil y diésel |
| IMPELE | Import/Distribution - Electricity | Primaria | Crudo, GLP e importación |
| T5FOICOM | Demand Fuel Oil for Commercial | Demanda |  |
| T5NGSRES | Demand Gas Natural for Residential | Demanda |  |
| T5LPGIND | Demand LPG for Industrial | Demanda |  |
| T5FIRIND | Demand Firewood for Industrial | Demanda |  |
| T5GSLCON | Demand Gasoline for Construcción y otros | Demanda |  |
| T5LPGCON | Demand Firewood for Construcción y otros | Demanda |  |
| T5OPECON | Demand Other non-energy petroleum products for Construcción y otros | Demanda |  |
| PPWNDD | Primary - Transformation - Distributed Wind | Primaria | Eólica |
| PPHD | Primary - Transformation - Hidroeléctrica distribuida | Primaria | Hidroeléctrica |
| PRONGS | Production - Natural_Gas | Secundaria |  |
| EXTT_NGS | Reserves - Natural Gas | Primaria |  |
| ADD_GRE | Primary - Import/Distribution - Gas Refineria | Primaria |  |
| T5CRUEXP | Demand Crude for Exports | Demanda |  |
| T5INDCOK | Demand Fuel Oil for Transport - Road | Demanda |  |
| T5VEGWAS | Demand Fuel Oil for Transport - Road | Demanda |  |
| T5TRNFOI | Demand Fuel Oil for Transport - Road | Demanda |  |
| T5COMGSL | Demand Commercial - Gasoline | Demanda |  |
| T5TAEGSL | Demand Aero Transport - Gasoline | Demanda |  |
| T5TMAGSL | Demand Maritime Transport - Gasoline | Demanda |  |
| T5TCADSL | Demand Heavy Duty Transport - Diesel | Demanda |  |
| T5TCAGSL | Demand Heavy Duty Transport - Gasoline | Demanda |  |
| T5ALLTRNDSL |  | Demanda |  |
| T5ALLTRNELE |  | Demanda |  |
| T5ALLTRNFOI |  | Demanda |  |
| T5ALLTRNLPG |  | Demanda |  |
| T5ALLTRNGSL |  | Demanda |  |
| T5ALLTRNJET |  | Demanda |  |
| T5CONKER | Demand Kerosene for Construction | Demanda |  |
| T5AGRDSL | Demand Diesel for Agriculture | Demanda |  |
| T5AGRLPG | Demand LPG for Agriculture | Demanda |  |
| T5AGRGSL | Demand Gasoline for Agriculture | Demanda |  |
| T5AGROTP | Demand Other non-energy petroleum products for Agriculture | Demanda |  |
| PPDFOI | Distributed Power Plant Fuel Oil | Secundaria | Fuel oil y diésel |
| PPDDSL | Distributed Power Plant  Diesel | Secundaria | Fuel oil y diésel |
| PPILPG | Isolated Power Plant LPG | Secundaria | Crudo, GLP e importación |
| PPIBIM | Isolated Power Plant Biomass/Residue | Secundaria | Biomasa y biogás |
| PPIHD | Primary - Transformation - Isolated Hidroeléctrica | Primaria | Hidroeléctrica |
| PPHDAMAB | Primary - Transformation - Hydro Dam Amazon Big (+ 450 MW) | Primaria | Hidroeléctrica |
| PPHDAMAM | Primary - Transformation - Hydro Dam Amazon Medium (< 450 MW) | Primaria | Hidroeléctrica |
| PPHDAMAS | Primary - Transformation - Hydro Dam Amazon Small (<50 MW) | Primaria | Hidroeléctrica |
| PPHDAMPM | Primary - Transformation - Hydro Dam Pacific Medium (< 450 MW) | Primaria | Hidroeléctrica |
| PPHDAMPS | Primary - Transformation - Hydro Dam Pacific Small (<50 MW) | Primaria | Hidroeléctrica |
| PPHRORAB | Primary - Transformation - Hydro ROR Amazon Big (+ 450 MW) | Primaria | Hidroeléctrica |
| PPHRORAM | Primary - Transformation - Hydro ROR Amazon Medium (< 450 MW) | Primaria | Hidroeléctrica |
| PPHRORAS | Primary - Transformation - Hydro ROR Amazon Small (<50 MW) | Primaria | Hidroeléctrica |
| PPHRORPM | Primary - Transformation - Hydro ROR Pacific Medium (< 450 MW) | Primaria | Hidroeléctrica |
| PPHRORPS | Primary - Transformation - Hydro ROR Pacific Small (<50 MW) | Primaria | Hidroeléctrica |
| DIST_CRU | Primary Import - Crude | Primaria |  |
| DIST_RDF | Primary - Import/Distribution - Desechos municipales no biomasa | Primaria |  |
| DIST_OID | Primary - Import/Distribution - Óleos de desecho | Primaria |  |
| T5RDFIND | Demand Desechos municipales no biomasa for Industrial | Demanda |  |
| T5OIDIND | Demand Óleos de desecho for Industrial | Demanda |  |

*Tabla. Combustibles del modelo*

| Código | Nombre |
|---|---|
| E1DSL | Primaria - Diesel |
| E1GSL | Primaria - Gasolina |
| E1NGS | Primaria -  Gas Natural |
| E1LPG | Primaria - GLP |
| E1COK | Primaria -  Coque |
| E1KER | Primaria -  Keroseno |
| E1JET | Primaria -  Jet |
| E1FIR | Primaria - Leña |
| E1CHA | Primaria - Carbon Vegetal |
| E1BIM | Primaria - Biomasa |
| E1BGS | Primaria - Biogas |
| E0CRU |  |
| E1COA | Primaria -  Carbón |
| E1FO1 | Primaria - Búnker |
| E1ELE | Secundaria - Electricidad de la Generación |
| E3ELE | Secondary - Electricidad de la Distribución |
| E2ELE | Secundaria - Electricidad de la Transmisión |
| E2HYDG | Secundaria - Hidrógeno Verde Producido |
| E1CRU |  |
| E3HYD | Secundaria - Hidrógeno Transportado |
| E1FOI | Primaria - Búnker |
| E5COMDSL | Final - Commercial - Diesel |
| E5COMGSL | Final - Commercial - Gasoline |
| E5COMLPG | Final - Commercial - LPG |
| E5COMELE | Final - Commercial - Electric |
| E5COMFIR | Final - Commercial - Firewood |
| E5COMCHA | Final - Commercial - Charcoal |
| E5COMOPE | Final - Commercial - Other non-energy petroleum products |
| E5RESDSL | Final - Residential - Diesel |
| E5RESGSL | Final - Residential - Gasoline |
| E5RESLPG | Final - Residential - LPG |
| E5RESELE | Final - Residential - Electric |
| E5RESKER | Final - Residential - Kerosen |
| E5RESFIR | Final - Residential - Firewood |
| E5RESCHA | Final - Residential - Charcoal |
| E5RESOPE | Final - Residential - Other non-energy petroleum products |
| E5PUBELE | Final - Public - Electric |
| E5INDDSL | Final - Industrial - Diesel |
| E5INDGSL | Final - Industrial - Gasoline |
| E5INDNGS | Final - Industrial - Natural Gas |
| E5INDELE | Final - Industrial - Electric |
| E5INDHYD | Final - Industrial - Hydrogen |
| E5INDCOK | Final - Industrial - Coke |
| E5INDBIM | Final - Industrial - Biomass |
| E5INDCOA | Final - Industrial - Coal |
| E5INDFOI | Final - Industrial - Fuel Oil |
| E5CONDSL | Final - Construction - Diesel |
| E5CONELE | Final - Construction - Electric |
| E5CONFOI | Final - Construction - Fuel Oil |
| E5EXPDSL | Final - Exports - Diesel |
| E5EXPJET | Final - Exports - Jet Fuel and others |
| E5EXPFOI | Final - Exports - Fuel Oil |
| E5TAEJET | Final - Transport - Aero - Jet Fuel and others |
| E5TMADSL | Final - Transport - Maritime - Diesel |
| E5TMANGS | Final - Transport - Maritime - Natural Gas |
| E5TMALPG | Final - Transport - Maritime - LPG |
| E5TMAELE | Final - Transport - Maritime - Electric |
| E5TMAFOI | Final - Transport - Maritime - Fuel Oil |
| E5TRODSL | Final - Transport - Road - Diesel |
| E5TROGSL | Final - Transport - Road - Gasoline |
| E5TRONGS | Final - Transport - Road - Natural Gas |
| E5TROLPG | Final - Transport - Road - LPG |
| E5TROELE | Final - Transport - Road - Electric |
| E5TROBGS | Final - Transport - Road - Biofuel/Biogas |
| E5TROFOI | Final - Transport - Road - Fuel Oil |
| E4ELE_HEA |  |
| E5TRXTRAI |  |
| E6TDFREHEA |  |
| E6TRNOMOT |  |
| E5COMFOI | Final - Commercial - Fuel Oil |
| E5RESNGS | Final - Residential - Natural Gas |
| E5INDLPG | Final - Industrial - LPG |
| E5INDFIR | Final - Industrial - Firewood |
| E5CONGSL | Final - Construction - Gasoline |
| E5CONLPG | Final - Construction - LPG |
| E5CONOPE | Final - Construction - Other non-energy petroleum products |
| E0NGS |  |
| E0GRE |  |
| E0GSL |  |
| E0JET |  |
| E0DSL |  |
| E0FOI |  |
| E0LPG |  |
| E5EXPCRU | Final - Exports - Crude |
| E5VEGWAS |  |
| E5TRNFOI |  |
| E5TAEGSL | Final - Transport - Aero - Gasoline |
| E5TMAGSL | Final - Transport - Maritime - Gasoline |
| E5TCADSL |  |
| E5TCAGSL |  |
| E5ALLTRNDSL |  |
| E5ALLTRNELE |  |
| E5ALLTRNFOI |  |
| E5ALLTRNLPG |  |
| E5ALLTRNGSL |  |
| E5ALLTRNJET |  |
| E5CONKER | Final - Construction - Kerosen |
| E5AGRDSL |  |
| E5AGRLPG |  |
| E5AGRGSL |  |
| E5AGROTP |  |
| E1RDF |  |
| E1OID |  |
| E5INDRDF |  |
| E5INDOID |  |
| E1OPE |  |

*Tabla. Emisiones del modelo y su entrada en las emisiones del sector energía*

| Código | Gas | Componente | En las emisiones del sector energía |
|---|---|---|---|
| CO2e_REF | CO2e | refinación | sí |
| CO2e_PP | CO2e | generación eléctrica | sí |
| CO2e_FUG | CO2e | fugitivas | sí |
| CO2e_DE | CO2e | demanda final | sí |
| CO2e_sources | CO2e | todas las fuentes |  |
| CO2_PP | CO2 | generación eléctrica |  |
| CH4_PP | CH4 | generación eléctrica |  |
| N2O_PP | N2O | generación eléctrica |  |
| CO2_DE | CO2 | demanda final |  |
| CH4_DE | CH4 | demanda final |  |
| N2O_DE | N2O | demanda final |  |
| CO2_FUG | CO2 | fugitivas |  |
| CH4_FUG | CH4 | fugitivas |  |
| N2O_FUG | N2O | fugitivas |  |
| CO2_REF | CO2 | refinación |  |
| CH4_REF | CH4 | refinación |  |
| N2O_REF | N2O | refinación |  |

## Variables de resultado

Las variables de resultado salen de la solución de glpsol, en el `_Output.csv` de cada escenario
(`Energy/Executables/<ESC>_0`). Ese archivo es la fuente de resultados del análisis.

| Variable | Qué mide | Unidad |
|---|---|---|
| `AnnualEmissions` | Emisiones anuales por componente (`CO2e_DE` demanda final, `CO2e_PP` generación eléctrica, `CO2e_FUG` fugitivas, `CO2e_REF` refinación, y los gases por separado). | Mt CO2e |
| `AnnualTechnologyEmission` | Emisiones anuales por tecnología y componente, base del desglose por subsector. | Mt CO2e |
| `ProductionByTechnology` | Producción anual de cada tecnología por combustible de salida. | PJ |
| `TotalTechnologyAnnualActivity` | Actividad anual de cada tecnología. Con el piso del datafile da la térmica desplazable. | PJ |
| `TotalCapacityAnnual` | Capacidad total disponible en el año. | GW |
| `NewCapacity` | Capacidad nueva instalada en el año. | GW |

## Indicadores derivados

`Art6_motor/analizar.py` calcula los indicadores sobre el `_Output.csv` de cada escenario.

| Indicador | Definición | Unidad |
|---|---|---|
| Emisiones del sector energía | 1 000 × (`CO2e_DE` + `CO2e_PP` + `CO2e_FUG` + `CO2e_REF`), de `AnnualTechnologyEmission`. | kt CO2e |
| Generación eléctrica | Producción de las centrales en electricidad de red (`E1ELE`) y distribuida (`E3ELE`) × 277,78, agrupada en familias tecnológicas. | GWh |
| Cuota ERNC | Generación eólica, solar, de biomasa y geotérmica sobre la generación eléctrica total. La hidroeléctrica no es ERNC. | % |
| Factor de planta | Generación / (capacidad × 8,76). | % |
| Reducción de una capa | Emisiones de la base menos las del escenario, sumadas en 2031-2035. | kt CO2e |
| Térmica desplazable | Generación térmica por encima de su piso de despacho obligatorio ([Metodología](../methods.md)). | GWh |
| Margen | Meta incondicional nacional del año menos la trayectoria nacional del escenario ([Metodología](../methods.md)). | kt CO2e |
| Sobreventa | Exceso de las emisiones nacionales ajustadas sobre la meta incondicional cuando ocurre una prueba de estrés después de autorizar ITMO. | kt CO2e |
| Ingresos | Volumen × precio, fuera del modelo. | millones de US$ |

## Estructura del repositorio

La carpeta `Energy` conserva la estructura de la cadena del Modelo CLG (repositorio
`clg-admin/ECU_NDC`) y agrega la calibración propia y la etapa de Artículo 6.

```text
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
```

La etapa de Artículo 6 es un paso aparte, `B3_Etapa_Art6.py`, que se corre después de B1 y no
modifica nada de lo que produce el modelo.

## Relación con la cadena del Modelo CLG

Los scripts de la cadena (A1, A2, B1 y B2) y la formulación `OSeMOSYS_Model.txt` son los del
repositorio del Modelo CLG, sin cambios. El trabajo del Artículo 6 entra por configuración: filas
propias en `B1_Scenario_Config.xlsx`, carpetas propias en `A2_Output_Params` y la etapa B3. Las 927
fórmulas del libro original se fijaron a su valor en caché, que es el que lee B1, para que el libro
pueda editarse sin perder valores.

Los códigos de escenario usan guion (`A-CCOFF`) porque B1 deduce el escenario cortando el nombre de
la carpeta en el primer guion bajo.
