# Introducción

## Pregunta del análisis

¿Cuántas reducciones del sector energía podría transferir el Ecuador como resultados de mitigación de
transferencia internacional (ITMO) en 2031-2035 sin poner en riesgo la meta incondicional de su Segunda
NDC? ¿Qué ocurre con ese potencial bajo las pruebas de estrés del sistema hidroeléctrico y con la situación
eléctrica de 2026?

## Modelo de partida y base corregida

El modelo de partida es el Modelo Climate Lead Group (Modelo CLG), el modelo de energía de la Segunda NDC
que publicó Climate Lead Group en el repositorio `clg-admin/ECU_NDC`. Sus cuatro escenarios, BAU,
BAU1NDC, NDCINC y NDCCON, se conservan sin cambios como comparación.

Las referencias del análisis son INCA6 y CONA6. Corresponden a NDCINC y NDCCON con una calibración propia,
las correcciones K01 a K16. La calibración lleva la generación eléctrica de 2010-2025 a lo observado en el
Balance Energético Nacional 2025, CENACE y ARCONEL, y fija los supuestos térmicos de 2026-2035. Ambas
referencias representan la Segunda NDC con la calibración corregida.

Los escenarios de Artículo 6 (A, B y C) se construyen sobre CONA6 y se miden frente a esa referencia. El
efecto de la calibración sobre las emisiones se informa aparte, como puente entre CONA6 y NDCCON
([Metodología](methods.md)).

## Contenido del repositorio

- La cadena del Modelo CLG (A1, A2, B1 y B2), que genera los escenarios desde un único libro de
  configuración, `Energy/B1_Scenario_Config.xlsx`. B1 resuelve todos los escenarios activos de la hoja
  `Scenarios`, 52 en la configuración publicada. El análisis usa 49 de ellos: las referencias,
  los escenarios de Artículo 6, las pruebas de estrés y las sensibilidades. Las pruebas de estrés son las
  siguientes: salida de Coca Codo y Sopladora (clase completa, cota), salida de Coca Codo sola, derrateo de Coca Codo, año seco severo (cota), un año seco cada tres, año seco moderado, salida de Coca Codo y año seco severo, sin importación desde Colombia, situación actual 2026 con choque de demanda transitorio y situación actual 2026 con demanda persistente (ACT-DEM). Las sensibilidades son estas: sin pisos térmicos, sin la expansión a gas declarada (sobre CONA6G) y sin sus proyectos (contrafactual).
- La calibración propia (`Energy/Art6_calibracion`), con sus fuentes y sus tablas de contraste.
- La etapa de Artículo 6 (B3), que se corre después de B1 y analiza volúmenes, margen frente a la meta,
  sobreventa, respaldo e ingresos.
- El cuaderno `Energy/B3_Visualizador_Art6.ipynb` y el tablero autónomo
  [tablero_art6.html](https://ecmaedmcc.github.io/EnergyArt6/_static/tablero_art6.html), que presentan cada gráfica con su guía de lectura.

## Procedencia de las cifras

Las cifras de resultados salen de la solución de glpsol de cada escenario
(`Energy/Executables/<ESC>_0/<ESC>_0_Output.csv`). Los parámetros de entrada salen de
`<ESC>_0_Input.csv` y del datafile `<ESC>_0.txt`. Cada cifra, con la tabla de la que sale y el md5 de
los `_Output.csv` que la producen, está en `Energy/B2_Output_Art6/cifras_finales_producto3.json`. Las
cifras principales de la corrida documentada están en [Cifras principales](1_art6/5_cifras.md).

## Términos del ejercicio

#### Términos del ejercicio

Los escenarios

Qué significa cada uno

Los términos que usan las fichas, las gráficas y los parámetros de entrada, en el orden en que aparecen al construir un escenario y al leer sus resultados.

| Término | Definición |
|---|---|
| Palanca | Una fila de la hoja Electrical del libro de configuración: fija un parámetro de OSeMOSYS para una tecnología y un periodo (un techo o un piso de capacidad o de generación, una inversión mínima, un factor de planta). Cada escenario es la copia del condicional más sus palancas; la hoja Art6_Palancas las documenta una por una. |
| Techo y piso | Límites que el optimizador no puede cruzar: el techo (TotalAnnualMaxCapacity, TotalTechnologyAnnualActivityUpperLimit) acota por arriba la capacidad o la generación de una tecnología; el piso (…LowerLimit) obliga a un mínimo. En los escenarios A y B los techos son el potencial de la capacidad declarada y el despacho lo decide el modelo, salvo el piso geotérmico de Chachimbiro (A5) y los pisos térmicos, que fijan una generación mínima: el de fuel oil es K16, el mínimo observado 2015-2025, y los de diésel y gas natural son los del Modelo CLG. |
| Inversión mínima | TotalAnnualMinCapacityInvestment: capacidad que el modelo debe construir en un año dado. Así entran los proyectos declarados (eólica, solar, geotermia, biomasa) con su año de operación. |
| Factor de planta | CapacityFactor: fracción del año en que una central opera a plena potencia. La eólica del A usa el valor observado (0,359) y el año seco aplica a cada clase hidroeléctrica la razón entre el caudal de 2024 y su media histórica. |
| Capa | Diferencia de emisiones del sector energía entre un escenario y su base, sumada en el marco 2026-2035 de la Segunda NDC y, para la oferta, en la ventana de transacciones 2031-2035. La capa del A se mide frente al condicional; la del B, frente al A; la del C, frente al B. |
| Contrafactual y aporte atribuible | El contrafactual es el mismo sistema sin los proyectos del escenario (A sin sus proyectos). La diferencia de emisiones con el escenario es el aporte atribuible por retiro: lo que esos proyectos reducen antes de las pruebas de adicionalidad y de sobreventa. |
| Margen | Distancia, en 2035, entre la meta incondicional y las emisiones nacionales del escenario: lo que puede transferirse con ajuste correspondiente sin incumplir la meta. Negativo: incumple. |
| Regla base y regla prudente | Cómo se proyectan los sectores que el modelo no cubre. Regla base: cumplen su tramo condicional. Regla prudente: cumplen solo su tramo incondicional, lo que deja menos margen. Toda cifra de margen se reporta con las dos. |
| Riesgo | Prueba de estrés sobre el sistema. Coca Codo: el derrateo del 20 % de Coca Codo Sinclair desde 2027 (CCDER), la salida de Coca Codo sola desde 2029 (CCSOLO, caso central) y la salida de la clase de Coca Codo, Coca Codo Sinclair y Sopladora, desde 2029 (CCOFF). Hidrología: el año seco severo con los caudales de 2024 todos los años desde 2026 (ANOSECO, cota), un año seco cada tres (ANOSEC3, caso central) y el año seco moderado (ANOSECM). Además, la salida de la clase y el año seco severo a la vez (CCOFFANOSECO) y la importación cero desde Colombia (IMP0), y la situación actual anclada a 2026 (ACT y ACT-DEM): en 2026, la demanda, la hidrología por clase, Coca Codo y la importación observadas; desde 2027, un año seco cada tres e importación cero; en ACT la demanda vuelve a la del Modelo CLG desde 2027 y en ACT-DEM el nivel de 2026 persiste. Los estados de riesgo llevan un respaldo de emergencia (tope de fuel oil liberado con potencia nueva cara y STOELE cerrado), supuesto de cierre como la térmica arrendada que el país contrata hoy. Riesgo de operación: sin pisos térmicos (FOI), un cambio de operación que no es un proyecto y no genera unidades; por eso queda fuera de los volúmenes transferibles. |
| Adicionalidad | Condición de que la reducción no ocurriría sin el ingreso del mercado. Firme: proyecto con barreras demostradas; por demostrar: pendiente de memoria de cálculo; sin adicionalidad: proyectos que se ejecutan de todos modos. El veredicto de compradores (hoja Art6_Adicionalidad) la completa. |
| Ajuste correspondiente | Regla del Artículo 6.2: la tonelada transferida se suma al balance de emisiones del Ecuador y se resta al del comprador, de modo que solo una parte la cuenta. |
