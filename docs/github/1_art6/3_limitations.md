# Limitaciones

Los resultados son consecuencias de los supuestos del modelo de la Segunda NDC, de la base corregida y de
los escenarios de Artículo 6. Las limitaciones que pueden superarse con trabajo de modelación adicional
tienen su recomendación en [Recomendaciones](4_recommendations.md).

- Un solo bloque horario por año. El modelo no distingue estaciones, días ni horas
  (`YearSplit = 1`). No representa la punta nocturna ni el almacenamiento, y el aporte de la solar a
  la potencia firme queda sobrestimado.
- Costos de relleno. El modelo de la NDC lleva costos variables, de capital y fijos iguales a 1 en buena
  parte de sus tecnologías. Con esos costos, el despacho dentro de sus pisos y techos es degenerado y el
  reparto anual entre térmica e hidroelectricidad depende del desempate de glpsol. Por eso el análisis
  mide cada capa como diferencia de emisiones entre un escenario y su base, y no usa los costos.
- Agua y suelo fuera del modelo. La disponibilidad hidroeléctrica entra como factores de planta
  fijos. El año seco se impone desde fuera, con los caudales observados en 2024. El caso central repite
  un año seco cada tres, y el año seco severo en todos los años es la cota. El modelo no puede
  representar el mes crítico de una sequía.
- Riesgo de Coca Codo Sinclair. El caso central retira la participación de Coca Codo en la energía de
  2025 de su clase. La salida de la clase completa retira también Sopladora y es una cota superior.
- Situación de 2026. Los datos de 2026 son preliminares (SCADA del CENACE al 10 de octubre) y el
  crecimiento de la demanda de enero a agosto se extiende al año. Después de 2026, ACT supone que la
  demanda vuelve a la trayectoria del Modelo CLG y ACT-DEM, que el nivel de 2026 persiste. Son dos
  supuestos declarados.
- Respaldo de emergencia. Los estados de riesgo pueden construir potencia de fuel oil cara cuando les
  falta potencia, como la térmica arrendada que el país contrata hoy. Esa potencia se informa en MW
  equivalentes con el factor de planta de PPFOI y en horas de corte equivalentes. Con un solo bloque
  horario, el modelo no ve la punta.
- Expansión térmica declarada. El tope de la inversión térmica de la red se aplica a la potencia
  acumulada, sin límite propio para la inversión de cada año. La vigencia de los arriendos sin fecha de
  fin publicada y el combustible de los proyectos que no lo declaran son supuestos.
- Expansión a gas declarada. El bloque de ciclo combinado del ajuste del Plan Maestro es un proyecto por
  definir. La familia GAS y la referencia CONA6G dan el resultado sin esa expansión.
- Rendimiento decreciente de las capas. Una renovable adicional solo reduce emisiones mientras haya
  térmica desplazable. La figura de reducción anual y la ficha de cada escenario muestran en qué años
  se concentra cada capa y cuánta térmica desplazable queda.
- Líneas fuera del modelo. Las iniciativas que el modelo no representa entran en el potencial con su
  valor declarado.
- Tendencial nacional retroactivo. Las metas se expresan sobre un tendencial (BAU1NDC) que excluye
  obras de la Primera NDC ya en operación. En 2035, 8 329 kt de la diferencia entre el
  tendencial y la referencia incondicional del sector energía provienen de esa construcción.
- Otros sectores. La regla condicional supone que los otros cuatro sectores cumplen el condicional que
  la NDC compromete. La regla prudente supone que solo cumplen su incondicional. La agregación nacional
  modelada reduce 3 576,6 kt más que la meta condicional publicada en 2035, y el análisis no
  cuenta esa diferencia.
- Datos por central. La capa CENTRALES de ARCONEL se usó con autorización para fechas de entrada,
  composición de clases y ponderaciones. El repositorio publica solo los parámetros agregados por clase.
  Por eso los scripts que derivan esos parámetros necesitan la capa local para volver a correr.
- Ajuste correspondiente conceptual. El ejercicio no aplica operativamente las reglas del Artículo 6
  ni constituye una metodología oficial.
