# Escenarios de Artículo 6 del sector energía del Ecuador

EnergyArt6 estima cuántas reducciones del sector energía podría transferir el Ecuador bajo el Artículo 6 del
Acuerdo de París sin poner en riesgo la meta incondicional de su Segunda NDC. Esas reducciones se
transferirían como resultados de mitigación de transferencia internacional (ITMO). Mide también cuánto de ese
volumen resiste los riesgos del sistema eléctrico: la salida o el derrateo de Coca Codo Sinclair, los años
secos, la importación cero desde Colombia y la situación de 2026.

El análisis cubre el periodo de la Segunda NDC, 2026-2035, y mide la oferta, la sobreventa y los ingresos en
2031-2035. Es un ejercicio exploratorio con fines analíticos, preparado por el Consultor para el PNUD (Proyecto
00110180 del PNUD Ecuador, Climate Promise). El tratamiento del ajuste correspondiente es conceptual y no
constituye una metodología oficial.

La documentación completa está en <https://ecmaedmcc.github.io/EnergyArt6/>.

## Para decidir

- [Cifras principales](https://ecmaedmcc.github.io/EnergyArt6/1_art6/5_cifras.html), con el origen de cada una
- [Potencial de ITMO](https://ecmaedmcc.github.io/EnergyArt6/1_art6/0_potential.html)
- [Pruebas de estrés y sobreventa](https://ecmaedmcc.github.io/EnergyArt6/1_art6/1_risks.html)
- [Recomendaciones](https://ecmaedmcc.github.io/EnergyArt6/1_art6/4_recommendations.html)
- [Tablero de resultados](https://ecmaedmcc.github.io/EnergyArt6/_static/tablero_art6.html), con las gráficas
  interactivas

### Resultados de la corrida

<!-- cifras:inicio -->
| Cifra | Valor (kt CO2-eq) | Periodo |
|---|---:|---|
| Oferta transferible, sin la electromovilidad de flotas en reserva | 11 674,4 | 2031-2035 |
| Lista blanca validada por los expertos, autorizable con el sistema intacto | 3 072,3 | 2031-2035 |
| De esa oferta, línea firme (geotermia de Chachimbiro) | 384,8 | 2031-2035 |
| Margen de 2035 del Escenario C frente a la meta incondicional (1) | 8 556,8 | 2035 |
| Lista blanca autorizable si persiste la demanda de 2026 (1) | 2 793,8 | 2031-2035 |
| Sobreventa, situación actual 2026 con demanda persistente (1) | 4 950,3 | 2031-2035 |
| Sobreventa, salida de Coca Codo sola (1) | 4 006,2 | 2031-2035 |
| Sobreventa, situación actual 2026 con demanda transitoria (1) | 1 457,8 | 2031-2035 |
| Sobreventa, un año seco cada tres (1) | 1 080,0 | 2031-2035 |
| Capa del Escenario A sobre CONA6 | 2 473,1 | 2031-2035 |
| Capa del Escenario B sobre A | 6 129,0 | 2031-2035 |
| Capa del Escenario C sobre B | 2 350,3 | 2031-2035 |
| Oferta con la electromovilidad de flotas en reserva | 12 599,4 | 2031-2035 |
| Oferta con los pisos térmicos del Modelo CLG (sensibilidad) | 9 446,9 | 2031-2035 |
| Puente CONA6 menos NDCCON (efecto de la calibración propia) | −7 085,0 | 2031-2035 |
| Puente CONA6G menos NDCCON (sin la expansión a gas declarada) | −4 310,0 | 2031-2035 |
| Margen de 2035 de CONA6 frente a la meta incondicional (1) | 7 268,2 | 2035 |
| Margen de 2035 de CONA6 con la regla condicional | 10 600,0 | 2035 |

Fuente: `Energy/B2_Output_Art6/cifras_finales_producto3.json` de la corrida del 13-10-2026, 22:15 (md5 `4e118305ce76a2d7b5fc967568cb1997`). (1) Proyección del Modelo CLG y regla prudente. La sobreventa usa el método anual y la oferta sin la electromovilidad de flotas en reserva.
<!-- cifras:fin -->

Las cifras son óptimos de mínimo costo y consecuencia de los supuestos documentados, sin valor de pronóstico.

### Margen frente a la Segunda NDC

El margen se mide frente a las metas publicadas de la Segunda NDC al 2035 sobre el tendencial nacional, con los
cinco sectores y USCUSS: 7 % incondicional (unos 8 800 kt CO2-eq) y 8 % condicional adicional (unos 10 600 kt).
El modelo representa solo el sector energía. Los otros sectores entran con la agregación nacional del Modelo CLG
y con dos reglas, condicional y prudente.

### Modelo de partida y referencias

El modelo de partida es el de energía de la Segunda NDC que publicó Climate Lead Group
([clg-admin/ECU_NDC](https://github.com/clg-admin/ECU_NDC), en este repositorio «Modelo CLG»). Sus cuatro
escenarios, BAU, BAU1NDC, NDCINC y NDCCON, se conservan sin cambios como comparación.

Las referencias del análisis son INCA6 y CONA6, los escenarios incondicional (NDCINC) y condicional (NDCCON) de
la Segunda NDC con una calibración corregida. Las correcciones K01 a K16 llevan la generación eléctrica de
2010-2025 a lo observado en el Balance Energético Nacional 2025, CENACE y ARCONEL. También recalculan los
factores de emisión de las térmicas con el IPCC 2006 y fijan los supuestos térmicos de 2026-2035.

Los escenarios A, B y C y sus estados de riesgo se construyen sobre CONA6 y se miden frente a ella. La
diferencia entre CONA6 y NDCCON, que es el efecto de la calibración, se informa aparte como puente.

## Para reproducir

### Instalación

1. Instale [Miniconda](https://docs.conda.io/en/latest/miniconda.html) para Windows de 64 bits, con las
   opciones por omisión.
2. Descargue o clone este repositorio en una carpeta con ruta corta, por ejemplo `C:\modelos`. Windows limita
   la ruta completa a 260 caracteres y algunas rutas internas son largas.
3. GLPK 4.65 viene incluido en `Energy/glpk` (licencia GNU GPL v3). Si prefiere una instalación propia,
   descargue WinGLPK 4.65 (https://sourceforge.net/projects/winglpk/), descomprímalo en `C:\winglpk` y agregue
   `C:\winglpk\glpk\w64` al PATH.
4. Cree el entorno conda `osemosys` con `conda env create -f environment.yml`, desde la raíz del repositorio en
   la consola de Anaconda.

Se necesitan unos 20 GB de memoria libre, porque B1 resuelve cuatro escenarios a la vez y cada corrida de
glpsol usa unos 4,5 GB.

### Escenarios

Todos se definen en `Energy/B1_Scenario_Config.xlsx` y los genera B1 con su mecanismo propio. Las filas de los
escenarios del Artículo 6 las escribe `Energy/Art6_calibracion/generar_escenarios_art6.py`. Las hojas `Art6_*`
del mismo libro documentan narrativa, palancas, riesgos, metas, precios, adicionalidad y fuentes.

| Código | Escenario |
|---|---|
| `BAU`, `BAU1NDC`, `NDCINC`, `NDCCON` | Modelo CLG sin cambios, como comparación |
| `INCA6`, `CONA6` | Referencias corregidas: NDCINC y NDCCON con las correcciones K01 a K16 |
| `INCA6G`, `CONA6G` | Sensibilidad de gas: las referencias sin la expansión a gas declarada. INCA6G lleva el cierre de fuel oil de emergencia |
| `A` «NDC financiada» | Actividades eléctricas del escenario condicional financiadas con mercado de carbono, sobre CONA6 |
| `B` «Ambición ampliada» | A más 585 MW eólicos, 1 584 MWp solares y 39,3 MW de biomasa fuera de la Segunda NDC |
| `C` «Ambición integral» | B más la electromovilidad y la eficiencia industrial del Plan de Acción del PLANMICC y la geotermia de Tufiño-Chiles-Cerro Negro |
| `-CCSOLO`, `-CCOFF`, `-CCDER` | Coca Codo Sinclair: salida sola desde 2029 (caso central), salida de la clase con Sopladora (cota) y derrateo del 20 % desde 2027 |
| `-ANOSEC3`, `-ANOSECO`, `-ANOSECM` | Año seco con la hidrología de 2024: uno cada tres (caso central), en todos los años (cota) y moderado |
| `-CCOFFANOSECO` | Salida de la clase de Coca Codo y año seco severo |
| `-IMP0` | Importación cero desde Colombia desde 2026 |
| `-ACT`, `-ACTDEM` | 2026 observado (demanda, hidrología, Coca Codo e importación) con demanda transitoria o persistente |
| `A-FOI`, `B-FOI` | Sensibilidad sin pisos térmicos, frente a la referencia CONA6P |
| `-GAS` | Sensibilidad sin la expansión a gas declarada, sobre CONA6G |
| `A-SIN` | Contrafactual: el A sin las actividades que financia |
| `-V7` | Puentes: las palancas de la versión del 08-10-2026 sobre CONA6 |
| `CONA6P`, `CONA6I` | Referencias de estado: CONA6 sin pisos térmicos y sin importación |

Los estados de riesgo llevan un respaldo de emergencia de fuel oil caro que solo se construye si falta
potencia. Ese respaldo se informa en MW equivalentes y en horas de corte equivalentes.

### Estructura del repositorio

| Carpeta o archivo | Contenido |
|---|---|
| `Energy/` | Cadena del modelo (A1, A2, B1 y B2), calibración propia (`Art6_calibracion`), etapa de Artículo 6 y scripts de la corrida (`B3_Etapa_Art6.py`, `Art6_motor`), pruebas (`tests`), insumos y resultados |
| `Energy/Executables/<ESC>_0/` | Datafile, entradas y salidas de cada escenario, versionados para comprobar las cifras sin correr el modelo |
| `Energy/Insumos_Art6/` | Insumos del análisis. `Emisiones Totales.xlsx`, `ECUOutput_Energy.csv` y `Energy.xlsx` son copias sin cambios de `PowerBI/` y `Data/` del Modelo CLG (agregación nacional, energía por escenario y datos de la calibración) |
| `Energy/registros/` | Registro de cada corrida de `ejecutar_modelo.bat`, fuera del control de versiones |
| `docs/` | Documentación Sphinx publicada en GitHub Pages |
| `ejecutar_modelo.bat`, `environment.yml`, `requirements.txt` | Ejecución de la cadena, entorno y dependencias |
| `LICENSE`, `NOTICE` | Licencia Apache 2.0 y reconocimiento del modelo base con la lista de cambios |

## Licencia y autoría

Derechos de autor 2026, Consultor para el PNUD (escenarios de Artículo 6, Proyecto 00110180 del PNUD Ecuador,
Climate Promise). Derechos de autor 2025, Climate Lead Group (modelo base).

El repositorio es una obra derivada del modelo de Climate Lead Group y se distribuye bajo la licencia Apache 2.0
(`LICENSE`). El archivo `NOTICE` reconoce el modelo base y lista los cambios. GLPK 4.65 se distribuye bajo la
GNU GPL v3 (`Energy/glpk/COPYING`). La capa CENTRALES de ARCONEL se usó con autorización, y el repositorio
publica solo parámetros agregados por clase.

- Escenarios de Artículo 6, calibración propia y documentación: Consultor para el PNUD, Dr. Ing. Mario
  Alejandro Heredia Salgado.
- Modelo OSeMOSYS de energía de la Segunda NDC: Climate Lead Group (2025).
