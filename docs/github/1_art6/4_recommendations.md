# Recomendaciones

## Incorporación de un módulo de recursos al modelo de la NDC

Los riesgos que más reducen el potencial de Artículo 6 son hidrológicos, y el modelo de energía de la
Segunda NDC no representa el agua. La disponibilidad de cada central entra como un factor de planta
fijo. Una sequía solo puede imponerse desde fuera, como hace la prueba de régimen seco con los caudales
que el CENACE observó en 2024. Con un solo bloque horario por año, el modelo ve el caudal medio y nunca
el mes en que el sistema falla.

Según el Informe Anual 2024 del CENACE (fig. 1.31 y tabla 1.14), el caudal medio de Mazar en 2024 fue
de 45,09 m³/s, frente a una media histórica de 86,05. En noviembre bajó a 13,44 m³/s, y los
racionamientos de ese año dejaron 1 922,69 GWh sin suministrar. Un riesgo que decide cuánto puede
transferir el país debería salir del propio modelo.

Con fines exploratorios, y según el enfoque CLEWs (clima, tierra, agua y energía), se acopló el modelo
de energía con los sectores de tierra y agua. El diagnóstico de ese acoplamiento identifica lo que falta
para que el canal agua-energía transmita la señal de una sequía: restricciones de escasez de agua y de
suelo, hoy ausentes. Se recomienda incorporar al modelo de la NDC un módulo de recursos con:

- disponibilidad de agua por cuenca hidrográfica, vinculada a las centrales que dependen de ella (por
  ejemplo, las cuencas del Coca, del Paute y del Jubones)
- bloques estacionales, al menos estación seca y lluviosa, día y noche, para representar el periodo
  crítico
- restricciones de uso del suelo con la cobertura oficial del Ministerio de Ambiente y Energía, que
  acoten la biomasa y las nuevas centrales
- escenarios hidrológicos generados por el propio modelo, que permitan dimensionar la reserva de ITMO
  sin autorizar.

## Actualización del condicional del Modelo CLG

El condicional del Modelo CLG (NDCCON) instala capacidad renovable que sus techos de actividad no dejan
generar. La guía de la figura de capacidad instalada muestra el factor de planta resultante. El primer
escalón de la escalera existe en buena medida para corregir esa inconsistencia. Se recomienda que el
datafile del condicional permita generar lo que la NDC declara. Así, la diferencia entre el condicional
y un escenario de Artículo 6 reflejaría actividades de mitigación y no ajustes de modelación.

## Calibración del modelo de la NDC

La base corregida reproduce la generación eléctrica observada de 2010-2025 y el INGEI del subsector
1A1 con un error de un solo signo en 2016-2022 (`Energy/Art6_calibracion/calibracion_a_tabla5.csv`).
Se recomienda someter las correcciones K01 a K16, con sus fuentes, a la Dirección de Mitigación del
Cambio Climático. Así podrían evaluarse en el modelo con el que se reporta la NDC antes del segundo
informe bienal de transparencia. También se recomienda que cada actualización del modelo conserve una
prueba de no regresión como la de `tests`.

## Costos reales

Cargar costos de inversión, de operación y de combustible, con la tasa de descuento social del país,
permitiría estimar el costo de cada reducción y el precio mínimo al que conviene transferirla.

## Representación del transporte

Las iniciativas de transporte de la NDC entran al potencial con su valor declarado. Con el clasificador
de transporte del modelo activado, esas reducciones se medirían con el mismo método que las del sector
eléctrico.

## Priorización de las líneas con adicionalidad firme

Se recomienda que la oferta inicial de Artículo 6 se construya sobre las líneas con adicionalidad firme
(Proyecto Geotérmico Chachimbiro) y sobre las líneas condicionadas que logren demostrar su adicionalidad. El volumen de las
líneas que los compradores potenciales descartaron debería tratarse como contribución a la NDC.

## Autorización prudente

Mientras el riesgo hidrológico se imponga desde fuera del modelo, una eventual autorización debería
seguir estas pautas:

- dimensionarse con la proyección del Modelo CLG y la regla prudente
- informar la sobreventa con los dos métodos de ajuste correspondiente
- conservar sin autorizar la reserva de cada año de reducción frente a la situación eléctrica observada
- limitarse a resultados verificados ex post de líneas con adicionalidad firme o validada.
