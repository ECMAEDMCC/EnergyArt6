# Escenarios

Los escenarios de Artículo 6 son tres escalones sobre la referencia condicional corregida CONA6. El A
está ligado a actividades del escenario condicional de la Segunda NDC. El B agrega oferta eléctrica que
la NDC no incluye. El C agrega la demanda del Plan de Acción del PLANMICC y la geotermia de Tufiño.

Sobre los escalones se aplican los estados de riesgo y las sensibilidades. Los estados de riesgo son
estos: salida de Coca Codo y Sopladora (clase completa, cota), salida de Coca Codo sola, derrateo de Coca Codo, año seco severo (cota), un año seco cada tres, año seco moderado, salida de Coca Codo y año seco severo, sin importación desde Colombia, situación actual 2026 con choque de demanda transitorio y situación actual 2026 con demanda persistente (ACT-DEM). Las sensibilidades son las siguientes: sin pisos térmicos, sin la expansión a gas declarada (sobre CONA6G) y sin sus proyectos (contrafactual). El contrafactual A-SIN retira
del A las actividades que financia.

Todos son escenarios basados en CONA6, o en CONA6G en la familia GAS. Se definen en
`Energy/B1_Scenario_Config.xlsx` y B1 los genera con su mecanismo propio.

*Tabla. Escenarios descritos en la configuración (hoja Art6_Escenarios)*

| Código | Escenario | Grupo | Palancas aplicadas | Narrativa |
|---|---|---|---|---|
| NDCINC | NDC incondicional (Modelo CLG) | Modelo CLG | (B1) | Escenario incondicional del Modelo Climate Lead Group, sin cambios. |
| NDCCON | NDC condicional (Modelo CLG) | Modelo CLG | (B1) | Escenario condicional del Modelo Climate Lead Group, sin cambios. |
| INCA6 | NDC incondicional corregida | Referencia corregida | (B1) | NDCINC del Modelo CLG con las correcciones K01-K16 (base congelada del 13-10-2026). |
| CONA6 | NDC condicional corregida | Referencia corregida | (B1) | NDCCON del Modelo CLG con las correcciones K01-K16 (base congelada del 13-10-2026). Base de A, B y C. |
| CONA6G | CONA6 sin la expansión a gas declarada | Referencia del estado | (B1) | CONA6 con PPNGS en su piso CLG 2026-2035 (G01): sin la expansión a gas declarada del Anexo A. Base y referencia de la familia GAS (sensibilidad de gas de la base congelada). |
| CONA6P | CONA6 sin pisos térmicos | Referencia del estado | FOI | CONA6 sin pisos térmicos desde 2026 (PPFOI con el piso K16; PPDSL y PPNGS con el del Modelo CLG). Referencia de la familia FOI. |
| CONA6I | CONA6 sin importación | Referencia del estado | IMP0 | CONA6 con la importación desde Colombia en cero desde 2026. Referencia de la familia IMP0. |
| A | NDC financiada | Escenario Art. 6 | A | El Ecuador financia con mercado de carbono una parte de su NDC condicional y esas actividades rinden lo que declaran: techos de generación iguales al potencial de la capacidad existente y declarada, con el factor de planta observado de la base corregida, y Chachimbiro adelantado a la fecha del Plan de Expansión. Se mide contra CONA6. |
| A-CCOFF | NDC financiada · Salida de Coca Codo y Sopladora (clase completa, cota) | Riesgo | A,CCOFF,RESP | Prueba de estrés sobre el Escenario A: la clase PPHRORAB (Coca Codo Sinclair y Sopladora) sale de operación desde 2029; cota superior. Con respaldo de emergencia (supuesto de cierre, como la térmica arrendada que el país contrata hoy): tope de PPFOI liberado desde 2026 con su potencia nueva cara (CapitalCost y FixedCost por 1.000) y STOELE cerrado en 2026-2035, de modo que solo se construye la potencia que falta. |
| A-CCSOLO | NDC financiada · Salida de Coca Codo sola | Riesgo | A,CCSOLO,RESP | Prueba de estrés sobre el Escenario A: Coca Codo Sinclair sale de operación desde 2029 y Sopladora sigue; caso central del riesgo de la central. Con respaldo de emergencia (supuesto de cierre, como la térmica arrendada que el país contrata hoy): tope de PPFOI liberado desde 2026 con su potencia nueva cara (CapitalCost y FixedCost por 1.000) y STOELE cerrado en 2026-2035, de modo que solo se construye la potencia que falta. |
| A-CCDER | NDC financiada · Derrateo de Coca Codo | Riesgo | A,CCDER,RESP | Prueba de estrés sobre el Escenario A: Coca Codo pierde el 20 % de su generación desde 2027 por sedimentos, medido por su participación en la energía de la clase. Con respaldo de emergencia (supuesto de cierre, como la térmica arrendada que el país contrata hoy): tope de PPFOI liberado desde 2026 con su potencia nueva cara (CapitalCost y FixedCost por 1.000) y STOELE cerrado en 2026-2035, de modo que solo se construye la potencia que falta. |
| A-ANOSECO | NDC financiada · Año seco severo (cota) | Riesgo | A,ANOSECO,RESP | Prueba de estrés sobre el Escenario A: los caudales de 2024 se repiten todos los años desde 2026; cota. Con respaldo de emergencia (supuesto de cierre, como la térmica arrendada que el país contrata hoy): tope de PPFOI liberado desde 2026 con su potencia nueva cara (CapitalCost y FixedCost por 1.000) y STOELE cerrado en 2026-2035, de modo que solo se construye la potencia que falta. |
| A-ANOSEC3 | NDC financiada · Un año seco cada tres | Riesgo | A,ANOSEC3,RESP | Prueba de estrés sobre el Escenario A: un año seco cada tres, con 2026 como año seco observado (2026, 2029, 2032 y 2035); caso central del riesgo hidrológico. Con respaldo de emergencia (supuesto de cierre, como la térmica arrendada que el país contrata hoy): tope de PPFOI liberado desde 2026 con su potencia nueva cara (CapitalCost y FixedCost por 1.000) y STOELE cerrado en 2026-2035, de modo que solo se construye la potencia que falta. |
| A-ANOSECM | NDC financiada · Año seco moderado | Riesgo | A,ANOSECM,RESP | Prueba de estrés sobre el Escenario A: toda la hidroelectricidad cae 9,2 % desde 2026, como en 2024. Con respaldo de emergencia (supuesto de cierre, como la térmica arrendada que el país contrata hoy): tope de PPFOI liberado desde 2026 con su potencia nueva cara (CapitalCost y FixedCost por 1.000) y STOELE cerrado en 2026-2035, de modo que solo se construye la potencia que falta. |
| A-CCOFFANOSECO | NDC financiada · Salida de Coca Codo y año seco severo | Riesgo | A,ANOSECO,CCOFF_ANOSECO,RESP | Prueba de estrés sobre el Escenario A: los dos choques a la vez: año seco severo y salida de la clase de Coca Codo. Con respaldo de emergencia (supuesto de cierre, como la térmica arrendada que el país contrata hoy): tope de PPFOI liberado desde 2026 con su potencia nueva cara (CapitalCost y FixedCost por 1.000) y STOELE cerrado en 2026-2035, de modo que solo se construye la potencia que falta. |
| A-FOI | NDC financiada · Sin pisos térmicos | Sensibilidad | A,FOI | Variante sobre el Escenario A: sin pisos térmicos desde 2026 (K16 en PPFOI; Modelo CLG en PPDSL y PPNGS); se mide contra CONA6P. |
| A-IMP0 | NDC financiada · Sin importación desde Colombia | Riesgo | A,IMP0,RESP | Prueba de estrés sobre el Escenario A: sin importación desde Colombia desde 2026; las capas se miden contra CONA6I. Con respaldo de emergencia (supuesto de cierre, como la térmica arrendada que el país contrata hoy): tope de PPFOI liberado desde 2026 con su potencia nueva cara (CapitalCost y FixedCost por 1.000) y STOELE cerrado en 2026-2035, de modo que solo se construye la potencia que falta. |
| A-ACT | NDC financiada · Situación actual 2026 con choque de demanda transitorio | Riesgo | A,ACTH,IMPACT,DEMACT,RESP | Prueba de estrés sobre el Escenario A: estrés con la situación actual anclada a 2026: en 2026, la demanda eléctrica observada (crecimiento de enero a agosto), la hidrología observada de cada clase, Coca Codo con su factor de planta de 2026 y la importación hasta el 06-09-2026; desde 2027, un año seco cada tres (razones de ANOSEC3 en 2029, 2032 y 2035) e importación cero como supuesto de estrés. La demanda vuelve a la trayectoria del Modelo CLG desde 2027 (choque transitorio, supuesto declarado). Valores de 2026: demanda eléctrica final 124,9196 PJ (CONA6 111,9876 PJ; multiplicador 1,1155), Coca Codo con factor de planta 0,6285, hidro de las clases 1,0931 veces la de CONA6 en 2025 e importación de 267,05 GWh. Con respaldo de emergencia (supuesto de cierre, como la térmica arrendada que el país contrata hoy): tope de PPFOI liberado desde 2026 con su potencia nueva cara (CapitalCost y FixedCost por 1.000) y STOELE cerrado en 2026-2035, de modo que solo se construye la potencia que falta. |
| A-ACTDEM | NDC financiada · Situación actual 2026 con demanda persistente (ACT-DEM) | Riesgo | A,ACTH,IMPACT,DEMACTDEM,RESP | Prueba de estrés sobre el Escenario A: la situación actual de ACT con la demanda de 2026 persistente: el nivel observado de 2026 se mantiene y desde ahí crece con las tasas del Modelo CLG (supuesto declarado). Valores de 2026: demanda eléctrica final 124,9196 PJ (CONA6 111,9876 PJ; multiplicador 1,1155), Coca Codo con factor de planta 0,6285, hidro de las clases 1,0931 veces la de CONA6 en 2025 e importación de 267,05 GWh. Con respaldo de emergencia (supuesto de cierre, como la térmica arrendada que el país contrata hoy): tope de PPFOI liberado desde 2026 con su potencia nueva cara (CapitalCost y FixedCost por 1.000) y STOELE cerrado en 2026-2035, de modo que solo se construye la potencia que falta. |
| A-GAS | NDC financiada · Sin la expansión a gas declarada (sobre CONA6G) | Sensibilidad | A | Variante sobre el Escenario A: las palancas del escenario sobre CONA6G, sin la expansión a gas declarada (PPNGS en su piso CLG, G01); sus capas se miden contra CONA6G. |
| A-SIN | NDC financiada · Sin sus proyectos (contrafactual) | Contrafactual | SIN | Variante sobre el Escenario A: el mismo sistema del A sin la eólica, la solar y la geotermia nuevas del condicional; la diferencia con el A es el aporte atribuible por retiro. |
| B | Ambición ampliada | Escenario Art. 6 | A,B | Sobre el A, un paquete fuera de la Segunda NDC entra como capacidad construida: la eólica del Plan de Expansión, el portafolio solar de CELEC EP con la AFD y 39,3 MW de biomasa del portafolio ESIN-CELEC EP. |
| B-CCOFF | Ambición ampliada · Salida de Coca Codo y Sopladora (clase completa, cota) | Riesgo | A,B,CCOFF,RESP | Prueba de estrés sobre el Escenario B: la clase PPHRORAB (Coca Codo Sinclair y Sopladora) sale de operación desde 2029; cota superior. Con respaldo de emergencia (supuesto de cierre, como la térmica arrendada que el país contrata hoy): tope de PPFOI liberado desde 2026 con su potencia nueva cara (CapitalCost y FixedCost por 1.000) y STOELE cerrado en 2026-2035, de modo que solo se construye la potencia que falta. |
| B-CCSOLO | Ambición ampliada · Salida de Coca Codo sola | Riesgo | A,B,CCSOLO,RESP | Prueba de estrés sobre el Escenario B: Coca Codo Sinclair sale de operación desde 2029 y Sopladora sigue; caso central del riesgo de la central. Con respaldo de emergencia (supuesto de cierre, como la térmica arrendada que el país contrata hoy): tope de PPFOI liberado desde 2026 con su potencia nueva cara (CapitalCost y FixedCost por 1.000) y STOELE cerrado en 2026-2035, de modo que solo se construye la potencia que falta. |
| B-CCDER | Ambición ampliada · Derrateo de Coca Codo | Riesgo | A,B,CCDER,RESP | Prueba de estrés sobre el Escenario B: Coca Codo pierde el 20 % de su generación desde 2027 por sedimentos, medido por su participación en la energía de la clase. Con respaldo de emergencia (supuesto de cierre, como la térmica arrendada que el país contrata hoy): tope de PPFOI liberado desde 2026 con su potencia nueva cara (CapitalCost y FixedCost por 1.000) y STOELE cerrado en 2026-2035, de modo que solo se construye la potencia que falta. |
| B-ANOSECO | Ambición ampliada · Año seco severo (cota) | Riesgo | A,B,ANOSECO,RESP | Prueba de estrés sobre el Escenario B: los caudales de 2024 se repiten todos los años desde 2026; cota. Con respaldo de emergencia (supuesto de cierre, como la térmica arrendada que el país contrata hoy): tope de PPFOI liberado desde 2026 con su potencia nueva cara (CapitalCost y FixedCost por 1.000) y STOELE cerrado en 2026-2035, de modo que solo se construye la potencia que falta. |
| B-ANOSEC3 | Ambición ampliada · Un año seco cada tres | Riesgo | A,B,ANOSEC3,RESP | Prueba de estrés sobre el Escenario B: un año seco cada tres, con 2026 como año seco observado (2026, 2029, 2032 y 2035); caso central del riesgo hidrológico. Con respaldo de emergencia (supuesto de cierre, como la térmica arrendada que el país contrata hoy): tope de PPFOI liberado desde 2026 con su potencia nueva cara (CapitalCost y FixedCost por 1.000) y STOELE cerrado en 2026-2035, de modo que solo se construye la potencia que falta. |
| B-ANOSECM | Ambición ampliada · Año seco moderado | Riesgo | A,B,ANOSECM,RESP | Prueba de estrés sobre el Escenario B: toda la hidroelectricidad cae 9,2 % desde 2026, como en 2024. Con respaldo de emergencia (supuesto de cierre, como la térmica arrendada que el país contrata hoy): tope de PPFOI liberado desde 2026 con su potencia nueva cara (CapitalCost y FixedCost por 1.000) y STOELE cerrado en 2026-2035, de modo que solo se construye la potencia que falta. |
| B-CCOFFANOSECO | Ambición ampliada · Salida de Coca Codo y año seco severo | Riesgo | A,B,ANOSECO,CCOFF_ANOSECO,RESP | Prueba de estrés sobre el Escenario B: los dos choques a la vez: año seco severo y salida de la clase de Coca Codo. Con respaldo de emergencia (supuesto de cierre, como la térmica arrendada que el país contrata hoy): tope de PPFOI liberado desde 2026 con su potencia nueva cara (CapitalCost y FixedCost por 1.000) y STOELE cerrado en 2026-2035, de modo que solo se construye la potencia que falta. |
| B-FOI | Ambición ampliada · Sin pisos térmicos | Sensibilidad | A,B,FOI | Variante sobre el Escenario B: sin pisos térmicos desde 2026 (K16 en PPFOI; Modelo CLG en PPDSL y PPNGS); se mide contra CONA6P. |
| B-IMP0 | Ambición ampliada · Sin importación desde Colombia | Riesgo | A,B,IMP0,RESP | Prueba de estrés sobre el Escenario B: sin importación desde Colombia desde 2026; las capas se miden contra CONA6I. Con respaldo de emergencia (supuesto de cierre, como la térmica arrendada que el país contrata hoy): tope de PPFOI liberado desde 2026 con su potencia nueva cara (CapitalCost y FixedCost por 1.000) y STOELE cerrado en 2026-2035, de modo que solo se construye la potencia que falta. |
| B-ACT | Ambición ampliada · Situación actual 2026 con choque de demanda transitorio | Riesgo | A,B,ACTH,IMPACT,DEMACT,RESP | Prueba de estrés sobre el Escenario B: estrés con la situación actual anclada a 2026: en 2026, la demanda eléctrica observada (crecimiento de enero a agosto), la hidrología observada de cada clase, Coca Codo con su factor de planta de 2026 y la importación hasta el 06-09-2026; desde 2027, un año seco cada tres (razones de ANOSEC3 en 2029, 2032 y 2035) e importación cero como supuesto de estrés. La demanda vuelve a la trayectoria del Modelo CLG desde 2027 (choque transitorio, supuesto declarado). Valores de 2026: demanda eléctrica final 124,9196 PJ (CONA6 111,9876 PJ; multiplicador 1,1155), Coca Codo con factor de planta 0,6285, hidro de las clases 1,0931 veces la de CONA6 en 2025 e importación de 267,05 GWh. Con respaldo de emergencia (supuesto de cierre, como la térmica arrendada que el país contrata hoy): tope de PPFOI liberado desde 2026 con su potencia nueva cara (CapitalCost y FixedCost por 1.000) y STOELE cerrado en 2026-2035, de modo que solo se construye la potencia que falta. |
| B-ACTDEM | Ambición ampliada · Situación actual 2026 con demanda persistente (ACT-DEM) | Riesgo | A,B,ACTH,IMPACT,DEMACTDEM,RESP | Prueba de estrés sobre el Escenario B: la situación actual de ACT con la demanda de 2026 persistente: el nivel observado de 2026 se mantiene y desde ahí crece con las tasas del Modelo CLG (supuesto declarado). Valores de 2026: demanda eléctrica final 124,9196 PJ (CONA6 111,9876 PJ; multiplicador 1,1155), Coca Codo con factor de planta 0,6285, hidro de las clases 1,0931 veces la de CONA6 en 2025 e importación de 267,05 GWh. Con respaldo de emergencia (supuesto de cierre, como la térmica arrendada que el país contrata hoy): tope de PPFOI liberado desde 2026 con su potencia nueva cara (CapitalCost y FixedCost por 1.000) y STOELE cerrado en 2026-2035, de modo que solo se construye la potencia que falta. |
| B-GAS | Ambición ampliada · Sin la expansión a gas declarada (sobre CONA6G) | Sensibilidad | A,B | Variante sobre el Escenario B: las palancas del escenario sobre CONA6G, sin la expansión a gas declarada (PPNGS en su piso CLG, G01); sus capas se miden contra CONA6G. |
| C | Ambición integral | Escenario Art. 6 | A,B,C | Sobre el B, la demanda del Plan de Acción del PLANMICC (electromovilidad y eficiencia industrial) y la geotermia de Tufiño-Chiles-Cerro Negro en 2035. |
| C-CCOFF | Ambición integral · Salida de Coca Codo y Sopladora (clase completa, cota) | Riesgo | A,B,C,CCOFF,RESP | Prueba de estrés sobre el Escenario C: la clase PPHRORAB (Coca Codo Sinclair y Sopladora) sale de operación desde 2029; cota superior. Con respaldo de emergencia (supuesto de cierre, como la térmica arrendada que el país contrata hoy): tope de PPFOI liberado desde 2026 con su potencia nueva cara (CapitalCost y FixedCost por 1.000) y STOELE cerrado en 2026-2035, de modo que solo se construye la potencia que falta. |
| C-CCSOLO | Ambición integral · Salida de Coca Codo sola | Riesgo | A,B,C,CCSOLO,RESP | Prueba de estrés sobre el Escenario C: Coca Codo Sinclair sale de operación desde 2029 y Sopladora sigue; caso central del riesgo de la central. Con respaldo de emergencia (supuesto de cierre, como la térmica arrendada que el país contrata hoy): tope de PPFOI liberado desde 2026 con su potencia nueva cara (CapitalCost y FixedCost por 1.000) y STOELE cerrado en 2026-2035, de modo que solo se construye la potencia que falta. |
| C-CCDER | Ambición integral · Derrateo de Coca Codo | Riesgo | A,B,C,CCDER,RESP | Prueba de estrés sobre el Escenario C: Coca Codo pierde el 20 % de su generación desde 2027 por sedimentos, medido por su participación en la energía de la clase. Con respaldo de emergencia (supuesto de cierre, como la térmica arrendada que el país contrata hoy): tope de PPFOI liberado desde 2026 con su potencia nueva cara (CapitalCost y FixedCost por 1.000) y STOELE cerrado en 2026-2035, de modo que solo se construye la potencia que falta. |
| C-ANOSECO | Ambición integral · Año seco severo (cota) | Riesgo | A,B,C,ANOSECO,RESP | Prueba de estrés sobre el Escenario C: los caudales de 2024 se repiten todos los años desde 2026; cota. Con respaldo de emergencia (supuesto de cierre, como la térmica arrendada que el país contrata hoy): tope de PPFOI liberado desde 2026 con su potencia nueva cara (CapitalCost y FixedCost por 1.000) y STOELE cerrado en 2026-2035, de modo que solo se construye la potencia que falta. |
| C-ANOSEC3 | Ambición integral · Un año seco cada tres | Riesgo | A,B,C,ANOSEC3,RESP | Prueba de estrés sobre el Escenario C: un año seco cada tres, con 2026 como año seco observado (2026, 2029, 2032 y 2035); caso central del riesgo hidrológico. Con respaldo de emergencia (supuesto de cierre, como la térmica arrendada que el país contrata hoy): tope de PPFOI liberado desde 2026 con su potencia nueva cara (CapitalCost y FixedCost por 1.000) y STOELE cerrado en 2026-2035, de modo que solo se construye la potencia que falta. |
| C-ANOSECM | Ambición integral · Año seco moderado | Riesgo | A,B,C,ANOSECM,RESP | Prueba de estrés sobre el Escenario C: toda la hidroelectricidad cae 9,2 % desde 2026, como en 2024. Con respaldo de emergencia (supuesto de cierre, como la térmica arrendada que el país contrata hoy): tope de PPFOI liberado desde 2026 con su potencia nueva cara (CapitalCost y FixedCost por 1.000) y STOELE cerrado en 2026-2035, de modo que solo se construye la potencia que falta. |
| C-CCOFFANOSECO | Ambición integral · Salida de Coca Codo y año seco severo | Riesgo | A,B,C,ANOSECO,CCOFF_ANOSECO,RESP | Prueba de estrés sobre el Escenario C: los dos choques a la vez: año seco severo y salida de la clase de Coca Codo. Con respaldo de emergencia (supuesto de cierre, como la térmica arrendada que el país contrata hoy): tope de PPFOI liberado desde 2026 con su potencia nueva cara (CapitalCost y FixedCost por 1.000) y STOELE cerrado en 2026-2035, de modo que solo se construye la potencia que falta. |
| C-IMP0 | Ambición integral · Sin importación desde Colombia | Riesgo | A,B,C,IMP0,RESP | Prueba de estrés sobre el Escenario C: sin importación desde Colombia desde 2026; las capas se miden contra CONA6I. Con respaldo de emergencia (supuesto de cierre, como la térmica arrendada que el país contrata hoy): tope de PPFOI liberado desde 2026 con su potencia nueva cara (CapitalCost y FixedCost por 1.000) y STOELE cerrado en 2026-2035, de modo que solo se construye la potencia que falta. |
| C-ACT | Ambición integral · Situación actual 2026 con choque de demanda transitorio | Riesgo | A,B,C,ACTH,IMPACT,DEMACT_C,RESP | Prueba de estrés sobre el Escenario C: estrés con la situación actual anclada a 2026: en 2026, la demanda eléctrica observada (crecimiento de enero a agosto), la hidrología observada de cada clase, Coca Codo con su factor de planta de 2026 y la importación hasta el 06-09-2026; desde 2027, un año seco cada tres (razones de ANOSEC3 en 2029, 2032 y 2035) e importación cero como supuesto de estrés. La demanda vuelve a la trayectoria del Modelo CLG desde 2027 (choque transitorio, supuesto declarado). Valores de 2026: demanda eléctrica final 124,9196 PJ (CONA6 111,9876 PJ; multiplicador 1,1155), Coca Codo con factor de planta 0,6285, hidro de las clases 1,0931 veces la de CONA6 en 2025 e importación de 267,05 GWh. Con respaldo de emergencia (supuesto de cierre, como la térmica arrendada que el país contrata hoy): tope de PPFOI liberado desde 2026 con su potencia nueva cara (CapitalCost y FixedCost por 1.000) y STOELE cerrado en 2026-2035, de modo que solo se construye la potencia que falta. |
| C-ACTDEM | Ambición integral · Situación actual 2026 con demanda persistente (ACT-DEM) | Riesgo | A,B,C,ACTH,IMPACT,DEMACTDEM_C,RESP | Prueba de estrés sobre el Escenario C: la situación actual de ACT con la demanda de 2026 persistente: el nivel observado de 2026 se mantiene y desde ahí crece con las tasas del Modelo CLG (supuesto declarado). Valores de 2026: demanda eléctrica final 124,9196 PJ (CONA6 111,9876 PJ; multiplicador 1,1155), Coca Codo con factor de planta 0,6285, hidro de las clases 1,0931 veces la de CONA6 en 2025 e importación de 267,05 GWh. Con respaldo de emergencia (supuesto de cierre, como la térmica arrendada que el país contrata hoy): tope de PPFOI liberado desde 2026 con su potencia nueva cara (CapitalCost y FixedCost por 1.000) y STOELE cerrado en 2026-2035, de modo que solo se construye la potencia que falta. |
| C-GAS | Ambición integral · Sin la expansión a gas declarada (sobre CONA6G) | Sensibilidad | A,B,C | Variante sobre el Escenario C: las palancas del escenario sobre CONA6G, sin la expansión a gas declarada (PPNGS en su piso CLG, G01); sus capas se miden contra CONA6G. |
| A-V7 | NDC financiada · Definición del 08-10-2026 (puente) | Puente | A_V7 | El Escenario A con las palancas exactas del sandbox PNUD del 08-10-2026 (biomasa de 35,6 MW y techos de esa fecha) sobre CONA6. Separa el efecto de la base del efecto de las decisiones nuevas en el caso intacto. |
| B-V7 | Ambición ampliada · Definición del 08-10-2026 (puente) | Puente | A_V7,B_V7 | El Escenario B con las palancas exactas del sandbox PNUD del 08-10-2026 (biomasa de 35,6 MW y techos de esa fecha) sobre CONA6. Separa el efecto de la base del efecto de las decisiones nuevas en el caso intacto. |
| C-V7 | Ambición integral · Definición del 08-10-2026 (puente) | Puente | A_V7,B_V7,C_V7 | El Escenario C con las palancas exactas del sandbox PNUD del 08-10-2026 (biomasa de 35,6 MW y techos de esa fecha) sobre CONA6. Separa el efecto de la base del efecto de las decisiones nuevas en el caso intacto. |

## Definición en la cadena del Modelo CLG

La hoja `Scenarios` de B1 distingue dos clases de escenario. Los escenarios de referencia
(`Based_On = ref`) se construyen desde los parámetros de su carpeta en `A2_Output_Params`. Son los
cuatro escenarios del Modelo CLG (BAU, BAU1NDC, NDCINC y NDCCON) y las cuatro referencias corregidas
(INCA6, CONA6, INCA6G y CONA6G). Los escenarios basados (`Reference = based`) parten de una copia de
otro escenario y aplican encima sus propias filas.

Las palancas están en las hojas `Electrical` y `Efficiency`. Cada fila fija un parámetro de una
tecnología o una demanda, por ejemplo el techo de actividad de la eólica
(`TotalTechnologyAnnualActivityUpperLimit` de `PPWNDON`). Su descripción empieza con el código de la
palanca entre corchetes, como `[A1]`. Cada palanca es un vector completo 2010-2035 que conserva la
historia de la base y cambia los años que declara. B1 redondea cada valor a cuatro decimales, como hace
con todas sus filas.

B1 copia la base antes de aplicar las hojas Electrical, SmartGrid y Efficiency. Por eso cada escenario
basado lleva también sus copias de las filas de la base en esas tres hojas. Sin ellas perdería, entre
otras cosas, los factores de emisión.

Las hojas `Art6_*` del mismo libro documentan la narrativa, la iniciativa, la adicionalidad y la
fuente de cada palanca. B1 no las lee. El papel de cada escenario en el análisis sale de esa definición
y de la hoja `Art6_Roles` ([Metodología](../methods.md)).

## Mapa de escenarios

El análisis compara 44 escenarios del Modelo Climate Lead Group (OSeMOSYS, Segunda NDC). Ocho forman una escalera: cada uno contiene al anterior y le suma una capa de reducción, y de la capa depende qué meta consume una tonelada vendida. Los otros 36 son pruebas sobre los escenarios de Artículo 6 (diez riesgos, dos riesgos de operación y un contrafactual), para medir cuánto del potencial resiste cuando cambian las condiciones del sistema.

#### Escalera de capas

Reducción acumulada del sector energía en 2031-2035, en kt CO2e. A cada capa se le atribuye solo lo que agrega sobre el escenario anterior.

Modelo CLG NDC incondicional (Modelo CLG) NDCINC

+ Tramo condicional del Modelo CLG (NDCINC menos NDCCON) 25 285 kt Es la meta condicional

Modelo CLG NDC condicional (Modelo CLG) NDCCON

+ INCA6 frente a NDCCON −15 468 kt Es la meta condicional

Referencia corregida NDC incondicional corregida INCA6

+ Tramo condicional de la base corregida (INCA6 menos CONA6) 22 553 kt Es la meta condicional

Referencia corregida NDC condicional corregida CONA6

+ Efecto de la referencia del estado GAS (CONA6 menos CONA6G) −2 775 kt Es la meta condicional

Referencia del estado CONA6 sin la expansión a gas declarada CONA6G

+ A frente a CONA6G 5 248 kt Descuenta de la meta condicional

Escenario de Artículo 6 NDC financiada A

+ Paquete fuera de la NDC (B sobre A) 6 129 kt No consume metas

Escenario de Artículo 6 Ambición ampliada B

+ Paquete fuera de la NDC (C sobre B) 2 350 kt No consume metas

Escenario de Artículo 6 Ambición integral C

Tramo condicional del Modelo CLG (NDCINC menos NDCCON) · 41 % INCA6 · 0 % Tramo condicional de la base corregida (INCA6 menos CONA6) · 37 % Efecto de la referencia del estado GAS (CONA6 menos CONA6G) · 0 % A · 9 % Paquete fuera de la NDC (B sobre A) · 10 % Paquete fuera de la NDC (C sobre B) · 4 %

#### Riesgos

Cada celda es un escenario del modelo. Volumen adicional: reducción frente al condicional en 2031-2035, sumada en los años en que el escenario emite menos que él. Margen 2035: meta incondicional menos la trayectoria nacional del escenario, con los otros sectores en el condicional que la NDC compromete (regla base); la regla prudente deja a los otros sectores solo en su tramo incondicional.

|  | Sistema intacto sin choques | Salida de la clase de Coca Codo (Coca Codo Sinclair y Sopladora) riesgo · desde 2029 | Salida de Coca Codo sola (caso central) riesgo · desde 2029 | Derrateo de Coca Codo riesgo · desde 2027 | Año seco severo (cota) riesgo · desde 2026 | Un año seco cada tres (caso central) riesgo · desde 2026 | Año seco moderado riesgo · desde 2026 | Salida de la clase de Coca Codo y año seco severo riesgo · desde 2026 | Sin pisos térmicos (K16 en PPFOI; Modelo CLG en PPDSL y PPNGS) riesgo de operación · desde 2026 | Importación cero desde Colombia riesgo · desde 2026 | Situación actual 2026, demanda transitoria (ACT) riesgo · desde 2026 | Situación actual 2026, demanda persistente (ACT-DEM) riesgo · desde 2026 | Sin la expansión a gas declarada (sobre CONA6G) riesgo de operación | Sin sus proyectos (contrafactual) contrafactual · desde 2026 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| NDC financiada | A Volumen adicional 2 473 ktMargen 2035 10 872 kt prudente : 7 540 kt | A-CCOFF Volumen adicional 0 ktMargen 2035 4 515 kt prudente : 1 184 kt | A-CCSOLO Volumen adicional 0 ktMargen 2035 6 494 kt prudente : 3 162 kt | A-CCDER Volumen adicional 0 ktMargen 2035 10 114 kt prudente : 6 782 kt | A-ANOSECO Volumen adicional 0 ktMargen 2035 5 230 kt prudente : 1 898 kt | A-ANOSEC3 Volumen adicional 1 678 ktMargen 2035 5 230 kt prudente : 1 898 kt | A-ANOSECM Volumen adicional 0 ktMargen 2035 9 182 kt prudente : 5 850 kt | A-CCOFFANOSECO Volumen adicional 0 ktMargen 2035 −1 040 kt prudente : −4 372 kt | A-FOI Volumen adicional 3 648 ktMargen 2035 11 200 kt prudente : 7 868 kt | A-IMP0 Volumen adicional 1 035 ktMargen 2035 10 601 kt prudente : 7 269 kt | A-ACT Volumen adicional 776 ktMargen 2035 4 852 kt prudente : 1 520 kt | A-ACTDEM Volumen adicional 0 ktMargen 2035 960 kt prudente : −2 372 kt | A-GAS Volumen adicional 260 ktMargen 2035 10 805 kt prudente : 7 473 kt | A-SIN Volumen adicional 0 ktMargen 2035 9 735 kt prudente : 6 403 kt |
| Ambición ampliada | B Volumen adicional 8 602 ktMargen 2035 11 156 kt prudente : 7 825 kt | B-CCOFF Volumen adicional 0 ktMargen 2035 7 779 kt prudente : 4 447 kt | B-CCSOLO Volumen adicional 0 ktMargen 2035 9 439 kt prudente : 6 107 kt | B-CCDER Volumen adicional 6 897 ktMargen 2035 11 156 kt prudente : 7 825 kt | B-ANOSECO Volumen adicional 0 ktMargen 2035 8 469 kt prudente : 5 137 kt | B-ANOSEC3 Volumen adicional 5 605 ktMargen 2035 8 469 kt prudente : 5 137 kt | B-ANOSECM Volumen adicional 4 625 ktMargen 2035 11 156 kt prudente : 7 825 kt | B-CCOFFANOSECO Volumen adicional 0 ktMargen 2035 2 223 kt prudente : −1 108 kt | B-FOI Volumen adicional 13 104 ktMargen 2035 12 632 kt prudente : 9 300 kt | B-IMP0 Volumen adicional 8 060 ktMargen 2035 11 156 kt prudente : 7 825 kt | B-ACT Volumen adicional 5 334 ktMargen 2035 8 109 kt prudente : 4 777 kt | B-ACTDEM Volumen adicional 0 ktMargen 2035 4 076 kt prudente : 744 kt | B-GAS Volumen adicional 8 194 ktMargen 2035 11 156 kt prudente : 7 825 kt | sin corrida |
| Ambición integral | C Volumen adicional 10 952 ktMargen 2035 11 888 kt prudente : 8 557 kt | C-CCOFF Volumen adicional 0 ktMargen 2035 8 677 kt prudente : 5 345 kt | C-CCSOLO Volumen adicional 0 ktMargen 2035 10 290 kt prudente : 6 958 kt | C-CCDER Volumen adicional 8 909 ktMargen 2035 11 888 kt prudente : 8 557 kt | C-ANOSECO Volumen adicional 0 ktMargen 2035 9 359 kt prudente : 6 027 kt | C-ANOSEC3 Volumen adicional 7 016 ktMargen 2035 9 359 kt prudente : 6 027 kt | C-ANOSECM Volumen adicional 6 183 ktMargen 2035 11 888 kt prudente : 8 557 kt | C-CCOFFANOSECO Volumen adicional 0 ktMargen 2035 3 121 kt prudente : −211 kt | sin corrida | C-IMP0 Volumen adicional 10 328 ktMargen 2035 11 888 kt prudente : 8 557 kt | C-ACT Volumen adicional 6 663 ktMargen 2035 8 999 kt prudente : 5 667 kt | C-ACTDEM Volumen adicional 0 ktMargen 2035 4 908 kt prudente : 1 576 kt | C-GAS Volumen adicional 10 344 ktMargen 2035 11 888 kt prudente : 8 557 kt | sin corrida |

el país excede su meta incondicional aun sin transferir la excede solo en la regla prudente riesgo de operación, sin proyecto detrás

Fuente: salidas de B1 de cada escenario (Energy/Executables/<ESC>_0/<ESC>_0_Output.csv e _Input.csv) del Modelo Climate Lead Group en la rama art6-escenarios de ECU_NDC; composición de cada escenario en B1_Scenario_Config.xlsx.

## Ficha de cada escenario

Cada ficha sigue el mismo orden: qué representa el escenario, qué cambia frente a su base, qué resulta en la corrida y qué implica para el Artículo 6. Un piso obliga al modelo a generar al menos esa energía con la tecnología; un techo le impide superarla.

#### NDC incondicional (Modelo CLG)

NDCINC Modelo CLG Escenario del Modelo CLG

Qué representa

Escenario incondicional del Modelo Climate Lead Group, sin cambios.

Iniciativas

16 iniciativas incondicionales de energía. Mayor reducción anual declarada: Central Hidroeléctrica Coca Codo Sinclair (3 927 kt/año), Central Hidroeléctrica Sopladora (1 150 kt/año) y Complejo Hidroeléctrico Toachi Pilatón (537 kt/año). Ver las 16 iniciativas

| Código | Iniciativa | Periodo | kt/año declarados | Adicionalidad |
|---|---|---|---|---|
| EN13 | Central Hidroeléctrica Coca Codo Sinclair | 2026-2035 | 3 927,0 | No transferible |
| EN17 | Central Hidroeléctrica Sopladora | 2026-2035 | 1 150,0 | No transferible |
| EN23 | Complejo Hidroeléctrico Toachi Pilatón | 2026-2035 | 537,0 | No transferible |
| EN16 | Central Hidroeléctrica Minas San Francisco | 2026-2035 | 529,0 | No transferible |
| EN06 | Programa de Soluciones Energéticas Upstream | 2026-2035 | 428,6 | No transferible |
| EN21 | Proyecto Hidroeléctrico Delsitanisagua | 2026-2035 | 369,0 | No transferible |
| EN15 | Central Hidroeléctrica Mazar | 2026-2035 | 255,0 | No transferible |
| EN07 | Preparación y Despacho de Gasolinas con Etanol | 2026-2035 | 199,1 | No transferible |
| EN14 | Central Hidroeléctrica Manduriacu | 2026-2035 | 168,0 | No transferible |
| EN04 | Proyecto Primera Línea del Metro de Quito | 2026-2035 | 60,0 | No transferible |
| EN24 | Proyecto Hidroeléctrico Soldados Yanuncay | 2028-2035 | 58,0 | No transferible |
| EN22 | Proyecto Eólico Villonaco | 2026-2035 | 37,0 | No transferible |
| EN27 | Proyecto Conolophus | 2029-2035 | 17,8 | No transferible |
| EN01 | Operación Comercial del Tranvía de Cuenca | 2026-2035 | 15,0 | No transferible |
| EN03 | Modernización del Sistema de Transporte Público Metropolitano de Pasajeros de Quito a través de la Dotación de Trolebuses | 2026-2035 | 5,0 | No transferible |
| EN26 | Sistema Híbrido Isabela (Fase II) | 2028-2035 | 1,3 | No transferible |

Qué cambia

Escenario del Modelo Climate Lead Group sin cambios, sin palancas de Artículo 6.

Lectura para el Artículo 6

- Sus 16 iniciativas figuran como «No transferible». Iniciativa del escenario incondicional: sostiene la meta que el país cumple con recursos propios.

#### Resultado de la corrida

Emisiones del sector energía, 2035 59 901 kt

Generación hidroeléctrica, 2035 58,5 % 25 558 GWh

Térmica desplazable, 2035 10 648 GWh generación térmica sobre su piso de despacho obligatorio

#### NDC condicional (Modelo CLG)

NDCCON Modelo CLG Escenario del Modelo CLG

Qué representa

Escenario condicional del Modelo Climate Lead Group, sin cambios.

Iniciativas

13 iniciativas condicionales de energía. Mayor reducción anual declarada: Proyecto Hidroeléctrico Santiago (7 353 kt/año), Proyecto hidroeléctrico Cardenillo (1 639 kt/año) y Proyecto Eólico Pimo (407 kt/año). Ver las 13 iniciativas

| Código | Iniciativa | Periodo | kt/año declarados | Adicionalidad |
|---|---|---|---|---|
| EN18 | Proyecto Hidroeléctrico Santiago | 2034-2035 | 7 352,8 | Sin adicionalidad |
| EN19 | Proyecto hidroeléctrico Cardenillo | 2034-2035 | 1 638,6 | Sin adicionalidad |
| EN12 | Proyecto Eólico Pimo | 2030-2035 | 406,9 | Por demostrar |
| EN10 | Proyecto Eólico Ducal Membrillo | 2029-2035 | 195,1 | Por demostrar |
| EN08 | Proyecto Geotérmico Chachimbiro | 2034-2035 | 192,4 | Firme |
| EN32 | Renovación y Descarbonización del Transporte Público y Comercial en el Ecuador | 2026-2035 | 185,0 | Por demostrar |
| EN20 | Proyecto Solar Flotante Mazar | 2029-2035 | 180,8 | Por demostrar |
| EN31 | Sistema Eléctrico de Monorriel Intracantonal para la Provincia Guayas | 2030-2035 | 42,8 | Por demostrar |
| EN05 | Proyecto Extensión de la Primera Línea del Metro de Quito desde el Labrador hasta La Ofelia | 2032-2035 | 16,0 | Por demostrar |
| EN25 | Proyecto Fotovoltaico Huascachaca | 2026-2035 | 16,0 | Por demostrar |
| EN02 | Diseño, Construcción e Implementación de la línea 2 del Tranvía de Cuenca | 2030-2035 | 8,0 | Por demostrar |
| EN28 | Sistema Solar Fotovoltaico San Cristóbal (Fase II) | 2029-2035 | 3,6 | Por demostrar |
| EN29 | Isla Floreana 100% Renovable | 2028-2035 | 0,3 | Por demostrar |

Qué cambia

Escenario del Modelo Climate Lead Group sin cambios, sin palancas de Artículo 6.

Lectura para el Artículo 6

- El tramo condicional, la reducción de la NDC condicional (Modelo CLG) frente a la NDC incondicional (Modelo CLG), suma 25 285 kt en 2031-2035. Transferirlo obliga a renunciar a la meta condicional en la misma cuantía.

- Proyecto Hidroeléctrico Santiago y Proyecto hidroeléctrico Cardenillo reúnen el 88 % de la reducción anual declarada de las iniciativas condicionales y figuran como «Sin adicionalidad». Gran hidroeléctrica, práctica común en Ecuador y financiable sin ingresos de carbono.

#### Resultado de la corrida

Emisiones del sector energía, 2035 51 454 kt

Reducción frente a la NDC incondicional (Modelo CLG), 2031-2035 25 285 kt el tramo condicional

Generación hidroeléctrica, 2035 78,3 % 34 835 GWh

Térmica desplazable, 2035 674 GWh generación térmica sobre su piso de despacho obligatorio

#### NDC incondicional corregida

INCA6 Referencia corregida Referencia corregida del Artículo 6

Qué representa

NDCINC del Modelo CLG con las correcciones K01-K16 (base congelada del 13-10-2026).

Iniciativas

16 iniciativas incondicionales de energía. Mayor reducción anual declarada: Central Hidroeléctrica Coca Codo Sinclair (3 927 kt/año), Central Hidroeléctrica Sopladora (1 150 kt/año) y Complejo Hidroeléctrico Toachi Pilatón (537 kt/año). Ver las 16 iniciativas

| Código | Iniciativa | Periodo | kt/año declarados | Adicionalidad |
|---|---|---|---|---|
| EN13 | Central Hidroeléctrica Coca Codo Sinclair | 2026-2035 | 3 927,0 | No transferible |
| EN17 | Central Hidroeléctrica Sopladora | 2026-2035 | 1 150,0 | No transferible |
| EN23 | Complejo Hidroeléctrico Toachi Pilatón | 2026-2035 | 537,0 | No transferible |
| EN16 | Central Hidroeléctrica Minas San Francisco | 2026-2035 | 529,0 | No transferible |
| EN06 | Programa de Soluciones Energéticas Upstream | 2026-2035 | 428,6 | No transferible |
| EN21 | Proyecto Hidroeléctrico Delsitanisagua | 2026-2035 | 369,0 | No transferible |
| EN15 | Central Hidroeléctrica Mazar | 2026-2035 | 255,0 | No transferible |
| EN07 | Preparación y Despacho de Gasolinas con Etanol | 2026-2035 | 199,1 | No transferible |
| EN14 | Central Hidroeléctrica Manduriacu | 2026-2035 | 168,0 | No transferible |
| EN04 | Proyecto Primera Línea del Metro de Quito | 2026-2035 | 60,0 | No transferible |
| EN24 | Proyecto Hidroeléctrico Soldados Yanuncay | 2028-2035 | 58,0 | No transferible |
| EN22 | Proyecto Eólico Villonaco | 2026-2035 | 37,0 | No transferible |
| EN27 | Proyecto Conolophus | 2029-2035 | 17,8 | No transferible |
| EN01 | Operación Comercial del Tranvía de Cuenca | 2026-2035 | 15,0 | No transferible |
| EN03 | Modernización del Sistema de Transporte Público Metropolitano de Pasajeros de Quito a través de la Dotación de Trolebuses | 2026-2035 | 5,0 | No transferible |
| EN26 | Sistema Híbrido Isabela (Fase II) | 2028-2035 | 1,3 | No transferible |

Qué cambia

NDCINC del Modelo CLG con las correcciones K01-K15 (base congelada), sin palancas de Artículo 6.

Lectura para el Artículo 6

- Sus 16 iniciativas figuran como «No transferible». Iniciativa del escenario incondicional: sostiene la meta que el país cumple con recursos propios.

- El tramo condicional, la reducción de la NDC incondicional corregida frente a la NDC incondicional (Modelo CLG), suma 9 816 kt en 2031-2035. Transferirlo obliga a renunciar a la meta condicional en la misma cuantía.

#### Resultado de la corrida

Emisiones del sector energía, 2035 57 869 kt

Reducción frente a la NDC incondicional (Modelo CLG), 2031-2035 9 816 kt el tramo condicional

Generación hidroeléctrica, 2035 58,6 % 25 588 GWh

Térmica desplazable, 2035 11 132 GWh generación térmica sobre su piso de despacho obligatorio

#### NDC condicional corregida

CONA6 Referencia corregida Referencia corregida del Artículo 6

Qué representa

NDCCON del Modelo CLG con las correcciones K01-K16 (base congelada del 13-10-2026). Base de A, B y C.

Iniciativas

13 iniciativas condicionales de energía. Mayor reducción anual declarada: Proyecto Hidroeléctrico Santiago (7 353 kt/año), Proyecto hidroeléctrico Cardenillo (1 639 kt/año) y Proyecto Eólico Pimo (407 kt/año). Ver las 13 iniciativas

| Código | Iniciativa | Periodo | kt/año declarados | Adicionalidad |
|---|---|---|---|---|
| EN18 | Proyecto Hidroeléctrico Santiago | 2034-2035 | 7 352,8 | Sin adicionalidad |
| EN19 | Proyecto hidroeléctrico Cardenillo | 2034-2035 | 1 638,6 | Sin adicionalidad |
| EN12 | Proyecto Eólico Pimo | 2030-2035 | 406,9 | Por demostrar |
| EN10 | Proyecto Eólico Ducal Membrillo | 2029-2035 | 195,1 | Por demostrar |
| EN08 | Proyecto Geotérmico Chachimbiro | 2034-2035 | 192,4 | Firme |
| EN32 | Renovación y Descarbonización del Transporte Público y Comercial en el Ecuador | 2026-2035 | 185,0 | Por demostrar |
| EN20 | Proyecto Solar Flotante Mazar | 2029-2035 | 180,8 | Por demostrar |
| EN31 | Sistema Eléctrico de Monorriel Intracantonal para la Provincia Guayas | 2030-2035 | 42,8 | Por demostrar |
| EN05 | Proyecto Extensión de la Primera Línea del Metro de Quito desde el Labrador hasta La Ofelia | 2032-2035 | 16,0 | Por demostrar |
| EN25 | Proyecto Fotovoltaico Huascachaca | 2026-2035 | 16,0 | Por demostrar |
| EN02 | Diseño, Construcción e Implementación de la línea 2 del Tranvía de Cuenca | 2030-2035 | 8,0 | Por demostrar |
| EN28 | Sistema Solar Fotovoltaico San Cristóbal (Fase II) | 2029-2035 | 3,6 | Por demostrar |
| EN29 | Isla Floreana 100% Renovable | 2028-2035 | 0,3 | Por demostrar |

Qué cambia

NDCCON del Modelo CLG con las correcciones K01-K15 (base congelada), sin palancas de Artículo 6.

Lectura para el Artículo 6

- El tramo condicional, la reducción de la NDC condicional corregida frente a la NDC incondicional (Modelo CLG), suma 32 370 kt en 2031-2035. Transferirlo obliga a renunciar a la meta condicional en la misma cuantía.

- Proyecto Hidroeléctrico Santiago y Proyecto hidroeléctrico Cardenillo reúnen el 88 % de la reducción anual declarada de las iniciativas condicionales y figuran como «Sin adicionalidad». Gran hidroeléctrica, práctica común en Ecuador y financiable sin ingresos de carbono.

#### Resultado de la corrida

Emisiones del sector energía, 2035 50 601 kt

Reducción frente a la NDC incondicional (Modelo CLG), 2031-2035 32 370 kt el tramo condicional

Generación hidroeléctrica, 2035 78,5 % 34 865 GWh

Térmica desplazable, 2035 1 052 GWh generación térmica sobre su piso de despacho obligatorio

#### CONA6 sin la expansión a gas declarada

CONA6G Referencia del estado Escenario del Modelo CLG

Qué representa

CONA6 con PPNGS en su piso CLG 2026-2035 (G01): sin la expansión a gas declarada del Anexo A. Base y referencia de la familia GAS (sensibilidad de gas de la base congelada).

Iniciativas

13 iniciativas condicionales de energía. Mayor reducción anual declarada: Proyecto Hidroeléctrico Santiago (7 353 kt/año), Proyecto hidroeléctrico Cardenillo (1 639 kt/año) y Proyecto Eólico Pimo (407 kt/año). Ver las 13 iniciativas

| Código | Iniciativa | Periodo | kt/año declarados | Adicionalidad |
|---|---|---|---|---|
| EN18 | Proyecto Hidroeléctrico Santiago | 2034-2035 | 7 352,8 | Sin adicionalidad |
| EN19 | Proyecto hidroeléctrico Cardenillo | 2034-2035 | 1 638,6 | Sin adicionalidad |
| EN12 | Proyecto Eólico Pimo | 2030-2035 | 406,9 | Por demostrar |
| EN10 | Proyecto Eólico Ducal Membrillo | 2029-2035 | 195,1 | Por demostrar |
| EN08 | Proyecto Geotérmico Chachimbiro | 2034-2035 | 192,4 | Firme |
| EN32 | Renovación y Descarbonización del Transporte Público y Comercial en el Ecuador | 2026-2035 | 185,0 | Por demostrar |
| EN20 | Proyecto Solar Flotante Mazar | 2029-2035 | 180,8 | Por demostrar |
| EN31 | Sistema Eléctrico de Monorriel Intracantonal para la Provincia Guayas | 2030-2035 | 42,8 | Por demostrar |
| EN05 | Proyecto Extensión de la Primera Línea del Metro de Quito desde el Labrador hasta La Ofelia | 2032-2035 | 16,0 | Por demostrar |
| EN25 | Proyecto Fotovoltaico Huascachaca | 2026-2035 | 16,0 | Por demostrar |
| EN02 | Diseño, Construcción e Implementación de la línea 2 del Tranvía de Cuenca | 2030-2035 | 8,0 | Por demostrar |
| EN28 | Sistema Solar Fotovoltaico San Cristóbal (Fase II) | 2029-2035 | 3,6 | Por demostrar |
| EN29 | Isla Floreana 100% Renovable | 2028-2035 | 0,3 | Por demostrar |

Qué cambia

Escenario del Modelo Climate Lead Group sin cambios, sin palancas de Artículo 6.

Lectura para el Artículo 6

- El tramo condicional, la reducción del escenario «CONA6 sin la expansión a gas declarada» frente a la NDC incondicional (Modelo CLG), suma 29 594 kt en 2031-2035. Transferirlo obliga a renunciar a la meta condicional en la misma cuantía.

- Proyecto Hidroeléctrico Santiago y Proyecto hidroeléctrico Cardenillo reúnen el 88 % de la reducción anual declarada de las iniciativas condicionales y figuran como «Sin adicionalidad». Gran hidroeléctrica, práctica común en Ecuador y financiable sin ingresos de carbono.

#### Resultado de la corrida

Emisiones del sector energía, 2035 50 738 kt

Reducción frente a la NDC incondicional (Modelo CLG), 2031-2035 29 594 kt el tramo condicional

Generación hidroeléctrica, 2035 78,6 % 34 892 GWh

Térmica desplazable, 2035 1 025 GWh generación térmica sobre su piso de despacho obligatorio

#### NDC financiada

A Escenario de Artículo 6 Descuenta de la meta condicional Base: NDC condicional corregida

Qué representa

El Ecuador financia con mercado de carbono una parte de su NDC condicional y esas actividades rinden lo que declaran: techos de generación iguales al potencial de la capacidad existente y declarada, con el factor de planta observado de la base corregida, y Chachimbiro adelantado a la fecha del Plan de Expansión. Se mide contra CONA6.

Líneas que contiene

- Núcleo Proyecto Geotérmico Chachimbiro EN08

Geotermia despachable con barrera de riesgo geológico; no se financia sin apoyo y no es práctica común en el país.

- Descartar Proyecto Eólico Ducal Membrillo EN10 , Proyecto Eólico Pimo EN12 , Proyecto Solar Flotante Mazar EN20 y Proyecto Fotovoltaico Huascachaca EN25

Renovable conectada a red: tecnología competitiva; el ICVCM no aprobó categorías de renovables bajo los CCP. La adicionalidad depende de demostrar una barrera financiera o de despacho. En la primera ronda de entrevistas, los compradores potenciales clasificaron la eólica y la solar a red como «Descartar»: sin atractivo para los compradores.

- Condicionada fuera del modelo: volumen declarado Diseño, Construcción e Implementación de la línea 2 del Tranvía de Cuenca EN02 , Proyecto Extensión de la Primera Línea del Metro de Quito desde el Labrador hasta La Ofelia EN05 , Sistema Eléctrico de Monorriel Intracantonal para la Provincia Guayas EN31 y Renovación y Descarbonización del Transporte Público y Comercial en el Ecuador EN32

Transporte: el clasificador de transporte del modelo está vacío, el volumen es el declarado.

- Condicionada fuera del modelo: volumen declarado Sistema Solar Fotovoltaico San Cristóbal (Fase II) EN28 e Isla Floreana 100% Renovable EN29

Sistema aislado de Galápagos que desplaza diésel; candidato fuerte por costo y por el valor ambiental del archipiélago.

Lectura para el Artículo 6

- La capa de la NDC financiada frente a la NDC condicional corregida suma 2 473 kt en 2031-2035.

- Transferida con ajuste correspondiente, cada tonelada de la capa deja de contar para la meta condicional.

- En 2031-2035 la capa agrega 2 684 GWh eólicos, 683 GWh geotérmicos y 594 GWh solares y deja de generar 2 546 GWh de gas natural y 1 416 GWh de fuel oil y diésel.

- La capa alcanza su máximo en 2031, con 838 kt, y en 2035 aporta 272 kt. La térmica desplazable de la NDC condicional corregida, lo único que una renovable nueva puede sustituir, pasa de 5 906 GWh en 2031 a 1 052 GWh en 2035.

- Sin las actividades que financia, el mismo sistema (escenario A-SIN) emitiría 6 048 kt más en 2031-2035: ese es el aporte atribuible por retiro, la reducción que esas actividades producen antes de la prueba de adicionalidad y de la prueba de sobreventa; la capa frente a la NDC condicional corregida mide solo lo que A añade a CONA6, que ya incluye esos proyectos.

- Veredicto de compradores potenciales para las 5 líneas que el modelo representa: 1 en «Núcleo» y 4 en «Descartar».

#### Qué cambia frente a la NDC condicional corregida

| Parámetro en 2035 | NDC condicional corregida | NDC financiada | Desde |
|---|---|---|---|
| Techo de generación eólica | 425 GWh 1,53 PJ | 914 GWh 3,29 PJ | 2026, en rampa hasta 2030 |
| Techo de generación solar | 1 019 GWh 3,67 PJ | 1 021 GWh 3,68 PJ | 2026, en rampa hasta 2034 |
| Techo de generación geotérmica | 353 GWh 1,27 PJ | 353 GWh 1,27 PJ | 2029 |
| Piso de generación geotérmica | 0 GWh 0,00 PJ | 353 GWh 1,27 PJ | 2029 |

Palancas en B1_Scenario_Config.xlsx (6)

| Palanca | Qué fija | Fuente |
|---|---|---|
| A1 | Techo de generación eólica igual al potencial de la capacidad existente de CONA6 (66.35 MW en 2025, K11) más la inversión mínima del condicional (230,4 MW en 2026-2030), con el factor de planta de CONA6 (0.3701, medio observado 2023-2025) y el factor de disponibilidad de 0,95: 1.2901 PJ en 2026 y 3.2903 PJ desde 2030. Nunca baja del techo de CONA6. | Climate Lead Group (2025), P3 Informe de modelamiento de la Segunda NDC, tabla 6, p. 19 (677 MW solares y 247,5 MW eólicos); capacidad existente y factor de planta de CONA6 (K11 y K12, Art6_calibracion/correcciones_K.csv) |
| A3 | Techo de generación solar igual al potencial de la capacidad existente de CONA6 (91.14 MW en 2025, K12, con los 67 MW del condicional de 2025) más la inversión mínima del condicional de 2026-2034, con el factor de planta de CONA6 (0.1694) y el factor de disponibilidad de 0,95; donde el techo de CONA6 es mayor, rige el de CONA6. | Climate Lead Group (2025), P3 Informe de modelamiento de la Segunda NDC, tabla 6, p. 19 (677 MW solares y 247,5 MW eólicos); capacidad existente y factor de planta de CONA6 (K11 y K12, Art6_calibracion/correcciones_K.csv) |
| A5 | Piso de generación geotérmica de 1,27 PJ desde 2029: Chachimbiro (50 MW) despacha desde su entrada adelantada. | Plan de Expansión de la Generación 2023-2032, tabla 4-4 (Chachimbiro 50 MW en 2029) y tabla 4-7 (585 MW eólicos) |
| A7 | Tope de capacidad geotérmica de 0,5 GW desde 2029 en lugar de 2032: habilita la entrada adelantada de Chachimbiro. | Plan de Expansión de la Generación 2023-2032, tabla 4-4 (Chachimbiro 50 MW en 2029) y tabla 4-7 (585 MW eólicos) |
| A8 | Inversión mínima geotérmica de 0,051 GW en 2029 en lugar de tres módulos de 0,017 GW en 2032-2034: Chachimbiro entra en la fecha del Plan de Expansión 2023-2032. | Plan de Expansión de la Generación 2023-2032, tabla 4-4 (Chachimbiro 50 MW en 2029) y tabla 4-7 (585 MW eólicos) |
| A9 | Techo de generación geotérmica de 1,27 PJ desde 2029 en lugar de la rampa 2032-2034 del condicional. | Plan de Expansión de la Generación 2023-2032, tabla 4-4 (Chachimbiro 50 MW en 2029) y tabla 4-7 (585 MW eólicos) |

#### Iniciativas modeladas

| Iniciativa | Tramo | Tecnología en el modelo | Palancas | Entrada | Capacidad 2035, MW | Generación 2035, GWh | Declarado, kt/año | Adicionalidad; veredicto |
|---|---|---|---|---|---|---|---|---|
| EN02 Diseño, Construcción e Implementación de la línea 2 del Tranvía de Cuenca | Condicional | fuera del modelo: entra con su cifra declarada |  |  |  |  | 8,0 | Por demostrar; Condicionada |
| EN05 Proyecto Extensión de la Primera Línea del Metro de Quito desde el Labrador hasta La Ofelia | Condicional | fuera del modelo: entra con su cifra declarada |  |  |  |  | 16,0 | Por demostrar; Condicionada |
| EN08 Proyecto Geotérmico Chachimbiro | Condicional | Geotermia (PPGEO) | A5, A7, A8 y A9 | 2029 | 51 | 353 | 192,4 | Firme; Núcleo |
| EN10 Proyecto Eólico Ducal Membrillo | Condicional | Eólica (PPWNDON) | A1 | 2026 | 297 | 914 | 195,1 | Por demostrar; Descartar |
| EN12 Proyecto Eólico Pimo | Condicional | Eólica (PPWNDON) | A1 | 2026 | 297 | 914 | 406,9 | Por demostrar; Descartar |
| EN20 Proyecto Solar Flotante Mazar | Condicional | Solar (PPPVT) | A3 | 2025 | 724 | 1 021 | 180,8 | Por demostrar; Descartar |
| EN25 Proyecto Fotovoltaico Huascachaca | Condicional | Solar (PPPVT) | A3 | 2025 | 724 | 1 021 | 16,0 | Por demostrar; Descartar |
| EN28 Sistema Solar Fotovoltaico San Cristóbal (Fase II) | Condicional | fuera del modelo: entra con su cifra declarada |  |  |  |  | 3,6 | Por demostrar; Condicionada |
| EN29 Isla Floreana 100% Renovable | Condicional | fuera del modelo: entra con su cifra declarada |  |  |  |  | 0,3 | Por demostrar; Condicionada |
| EN31 Sistema Eléctrico de Monorriel Intracantonal para la Provincia Guayas | Condicional | fuera del modelo: entra con su cifra declarada |  |  |  |  | 42,8 | Por demostrar; Condicionada |
| EN32 Renovación y Descarbonización del Transporte Público y Comercial en el Ecuador | Condicional | fuera del modelo: entra con su cifra declarada |  |  |  |  | 185,0 | Por demostrar; Condicionada |

Capacidad y generación en 2035 de la tecnología que modela la iniciativa (Output.csv del escenario), compartidas entre las iniciativas de esa tecnología; entrada: primer año con capacidad nueva en el escenario. Las cifras declaradas vienen de Art6_Adicionalidad.

#### Resultado de la corrida

Emisiones del sector energía, 2035 50 328 kt

Volumen adicional a la NDC, 2031-2035 2 473 kt

Margen nacional, 2035 10 872 kt regla prudente (los demás sectores cumplen solo su incondicional): 7 540 kt

Aporte atribuible por retiro, 2031-2035 6 048 kt emisiones de A-SIN (el mismo sistema sin las actividades de A) menos las de A

| Generación en 2035 | NDC condicional corregida, GWh | NDC financiada, GWh | Diferencia | Capacidad, MW |
|---|---|---|---|---|
| Gas natural | 2 199 | 1 709 | −490 | 987 → 980 |
| Eólica | 428 | 917 | 489 | 302 → 302 |
| Solar | 1 056 | 1 058 | 2 | 870 → 870 |
| Geotermia | 353 | 353 | 0 | 51 → 51 |

#### Ambición ampliada

B Escenario de Artículo 6 No consume metas Base: NDC financiada

Qué representa

Sobre el A, un paquete fuera de la Segunda NDC entra como capacidad construida: la eólica del Plan de Expansión, el portafolio solar de CELEC EP con la AFD y 39,3 MW de biomasa del portafolio ESIN-CELEC EP.

Líneas que contiene

- Condicionada Biomasa del portafolio ESIN-CELEC EP (39,3 MW, 192,8 GWh/año) B-BIO

Despachable; cuatro plantas de palma y cascarilla identificadas por ESIN-CELEC EP (2020). Debe demostrar que el residuo no tiene uso competitivo y que hay barrera de inversión.

- Descartar Portafolio solar CELEC EP y AFD (3 000 GWh/año) B-SOL y Eólica del plan de expansión no listada en la NDC (585 MW) B-EOL

Renovable conectada a red fuera de la NDC. En la primera ronda de entrevistas, los compradores potenciales clasificaron la eólica y la solar a red como «Descartar»: sin atractivo para los compradores.

Lectura para el Artículo 6

- La capa del escenario «Ambición ampliada» frente a la NDC financiada suma 6 129 kt en 2031-2035; con ella, el escenario «Ambición ampliada» acumula 8 602 kt adicionales a la NDC.

- Sus líneas están fuera de la NDC: una tonelada de la capa no consume ninguna meta si demuestra su adicionalidad.

- En 2031-2035 la capa agrega 7 457 GWh eólicos, 3 130 GWh solares y 379 GWh de biomasa y biogás y deja de generar 10 201 GWh de gas natural y 630 GWh de fuel oil y diésel.

- La capa alcanza su máximo en 2032, con 1 876 kt, y en 2035 aporta 284 kt. La térmica desplazable de la NDC financiada, lo único que una renovable nueva puede sustituir, pasa de 4 782 GWh en 2031 a 562 GWh en 2035.

- B-BIO: techo de 192,8 GWh/año desde 2031 y despacho solo en 2031-2032 (costos de relleno del Modelo CLG).

- Bajo los riesgos la misma capa reduce 12 256 kt con la salida de la clase de Coca Codo, 11 905 kt con la salida de Coca Codo sola, 8 619 kt con el derrateo de Coca Codo, 11 732 kt con el año seco severo, 9 063 kt con un año seco cada tres, 10 712 kt con el año seco moderado, 11 171 kt con la salida de la clase de Coca Codo y el año seco severo, 7 024 kt con la importación cero desde Colombia, 9 519 kt con la situación actual anclada a 2026 con choque de demanda transitorio y 12 516 kt con la situación actual anclada a 2026 con demanda persistente, frente a 6 129 kt con el sistema intacto: vuelve a haber térmica que sustituir, y en 2035 la térmica desplazable de la NDC financiada va de 1 027 a 17 106 GWh, frente a 562 GWh con el sistema intacto.

- Veredicto de compradores potenciales para las 3 líneas que el modelo representa: 1 en «Condicionada» y 2 en «Descartar».

#### Qué cambia frente a la NDC financiada

| Parámetro en 2035 | NDC financiada | Ambición ampliada | Desde |
|---|---|---|---|
| Techo de generación eólica | 914 GWh 3,29 PJ | 2 716 GWh 9,78 PJ | 2028, en rampa hasta 2032 |
| Techo de generación solar | 1 021 GWh 3,68 PJ | 3 254 GWh 11,71 PJ | 2028, en rampa hasta 2035 |
| Techo de generación con biomasa | 0 GWh 0,00 PJ | 193 GWh 0,69 PJ | 2031 |

Palancas en B1_Scenario_Config.xlsx (7)

| Palanca | Qué fija | Fuente |
|---|---|---|
| B2 | Techo de generación solar igual al potencial de la capacidad existente de CONA6, la inversión del condicional y los 1.584 MWp de CELEC EP y AFD (B8), con el factor de planta de CONA6 y el factor de disponibilidad de 0,95: 11.7140 PJ en 2035. | Regla de construcción del A aplicada a la capacidad del B |
| B4 | Techo de generación eólica igual al potencial de la capacidad existente de CONA6, la inversión del condicional y los 585 MW del Plan de Expansión (B7), con el factor de planta de CONA6 y el factor de disponibilidad de 0,95: 9.7768 PJ desde 2032. | Regla de construcción del A aplicada a la capacidad del B |
| B6 | Techo de generación de biomasa igual al potencial de los 39,3 MW nuevos (B9) con el factor de planta declarado de 0,56 (CF del modelo 0.5895 con AF 0,95): 0.6941 PJ (192.8 GWh) al año desde 2031. | ESIN-CELEC EP (2020), portafolio de biomasa de 39,3 MW en cuatro plantas de palma y cascarilla; factor de planta 0,56 (lámina 31) |
| B7 | Inversión mínima eólica: la de CONA6 más 585 MW del Plan de Expansión 2023-2032 en cinco bloques de 117 MW entre 2028 y 2032 (calendario supuesto). Conserva la historia de CONA6 (sin la eólica ficticia de 2013-2015 del Modelo CLG). | Plan de Expansión de la Generación 2023-2032, tabla 4-4 (Chachimbiro 50 MW en 2029) y tabla 4-7 (585 MW eólicos) |
| B8 | Inversión mínima solar: la de CONA6 más 1.584 MWp del portafolio de CELEC EP y AFD en ocho bloques de 198 MW entre 2028 y 2035 (calendario supuesto). | CELEC EP y AFD-TRACTEBEL (2024), 1.584 MWp |
| B9 | Inversión mínima de biomasa de 0,0393 GW en 2031: el portafolio de 39,3 MW de ESIN-CELEC EP (2020). CONA6 no tiene capacidad de PPBIM desde 2011 (K05). | ESIN-CELEC EP (2020), 39,3 MW en cuatro plantas |
| B10 | Factor de planta del modelo para la biomasa nueva desde 2031: 0.5895, el 0,56 declarado dividido por el factor de disponibilidad de 0,95 (CONA6 trae 0,4592 sin capacidad de PPBIM). | ESIN-CELEC EP (2020), lámina 31 |

#### Iniciativas modeladas

| Iniciativa | Tramo | Tecnología en el modelo | Palancas | Entrada | Capacidad 2035, MW | Generación 2035, GWh | Declarado, kt/año | Adicionalidad; veredicto |
|---|---|---|---|---|---|---|---|---|
| B-SOL Portafolio solar CELEC EP y AFD (3 000 GWh/año) | Fuera de la NDC | Solar (PPPVT) | B8 | 2025 | 2 308 | 971 |  | Por demostrar; Descartar |
| B-EOL Eólica del plan de expansión no listada en la NDC (585 MW) | Fuera de la NDC | Eólica (PPWNDON) | B7 | 2026 | 882 | 1 524 |  | Por demostrar; Descartar |
| B-BIO Biomasa del portafolio ESIN-CELEC EP (39,3 MW, 192,8 GWh/año) | Fuera de la NDC | Biomasa y biogás (PPBIM) | B10, B6 y B9 | 2031 | 39 | 0 |  | Por demostrar; Condicionada |

Capacidad y generación en 2035 de la tecnología que modela la iniciativa (Output.csv del escenario), compartidas entre las iniciativas de esa tecnología; entrada: primer año con capacidad nueva en el escenario. Las cifras declaradas vienen de Art6_Adicionalidad.

B-BIO (PPBIM): techo de generación de 192,8 GWh/año desde 2031, pero el modelo solo despacha PPBIM en 2031-2032 (192,8 y 192,8 GWh) y en 2033-2035 deja sin despacho su capacidad (39,3 MW). Con los costos de relleno del Modelo CLG, ese despacho no responde a un costo real.

#### Resultado de la corrida

Emisiones del sector energía, 2035 50 044 kt

Volumen adicional a la NDC, 2031-2035 8 602 kt 6 129 kt de esta capa

Margen nacional, 2035 11 156 kt regla prudente (los demás sectores cumplen solo su incondicional): 7 825 kt

| Generación en 2035 | NDC financiada, GWh | Ambición ampliada, GWh | Diferencia | Capacidad, MW |
|---|---|---|---|---|
| Gas natural | 1 709 | 1 307 | −401 | 980 → 666 |
| Eólica | 917 | 1 527 | 610 | 302 → 886 |
| Solar | 1 058 | 976 | −81 | 870 → 2 454 |
| Biomasa y biogás | 45 | 43 | −2 | 158 → 198 |

#### Ambición integral

C Escenario de Artículo 6 No consume metas Base: Ambición ampliada

Qué representa

Sobre el B, la demanda del Plan de Acción del PLANMICC (electromovilidad y eficiencia industrial) y la geotermia de Tufiño-Chiles-Cerro Negro en 2035.

Líneas que contiene

- Sin veredicto Electromovilidad del Plan de Acción del PLANMICC (vehículos eléctricos e híbridos privados, taxis y buses) C-EM

Desde 2030 la ley obliga a que todo vehículo nuevo del transporte público urbano, interparroquial y comercial sea eléctrico: esa parte no tiene adicionalidad regulatoria; los vehículos privados y los taxis no están obligados.

- Sin veredicto Eficiencia energética industrial del Plan de Acción del PLANMICC (ISO 50001, ESCO) C-EI

La normativa vigente obliga a los grandes consumidores industriales a sistemas de gestión de la energía: esa parte no tiene adicionalidad regulatoria (Plan de Acción, Tabla 29).

- Sin veredicto Proyecto Geotérmico Binacional Tufiño-Chiles-Cerro Negro (138 MW) C-GEO

Prefactibilidad con perforación exploratoria pendiente: barreras de riesgo geológico y financiero plausibles; el año 2035 es un supuesto del análisis.

Lectura para el Artículo 6

- La capa del escenario «Ambición integral» frente al escenario «Ambición ampliada» suma 2 350 kt en 2031-2035; con ella, el escenario «Ambición integral» acumula 10 952 kt adicionales a la NDC.

- Sus líneas están fuera de la NDC: una tonelada de la capa no consume ninguna meta si demuestra su adicionalidad.

- En 2031-2035 la capa agrega 1 283 GWh solares, 1 010 GWh de gas natural y 955 GWh geotérmicos y deja de generar 214 GWh eólicos.

- Bajo los riesgos la misma capa reduce 1 418 kt con la salida de la clase de Coca Codo, 1 395 kt con la salida de Coca Codo sola, 2 012 kt con el derrateo de Coca Codo, 1 296 kt con el año seco severo, 2 390 kt con un año seco cada tres, 1 558 kt con el año seco moderado, 1 418 kt con la salida de la clase de Coca Codo y el año seco severo, 2 268 kt con la importación cero desde Colombia, 2 309 kt con la situación actual anclada a 2026 con choque de demanda transitorio y 1 221 kt con la situación actual anclada a 2026 con demanda persistente, frente a 2 350 kt con el sistema intacto.

- Veredicto de compradores potenciales para las 3 líneas que el modelo representa: 3 sin veredicto.

#### Qué cambia frente al escenario «Ambición ampliada»

| Parámetro en 2035 | Ambición ampliada | Ambición integral | Desde |
|---|---|---|---|
| Techo de generación geotérmica | 353 GWh 1,27 PJ | 1 307 GWh 4,71 PJ | 2035 |

Palancas en B1_Scenario_Config.xlsx (17)

| Palanca | Qué fija | Fuente |
|---|---|---|
| C-GEO1 | Inversión mínima geotérmica: Chachimbiro 0,051 GW en 2029 (como A8) más 0,138 GW del Proyecto Geotérmico Binacional Tufiño-Chiles-Cerro Negro en 2035 (entrada supuesta). | Primicias (2025) y ThinkGeoEnergy (2025): 138 MW; año 2035 supuesto |
| C-GEO2 | Techo de generación geotérmica: 1,27 PJ de Chachimbiro desde 2029 (como A9) más 3.4365 PJ de Tufiño en 2035 con el mismo rendimiento por GW (24.90 PJ/GW). | Primicias (2025) y ThinkGeoEnergy (2025): 138 MW; año 2035 supuesto |
| C-EI1 | Eficiencia energética industrial del Plan de Acción del PLANMICC: E5INDBIM con 2,45 % menos en 2035, rampa lineal 2026-2035 (razón del sandbox aplicada a la demanda de CONA6). | PLANMICC, Plan de Acción Fase I (MAE, 2026), tabla 36; modelo OSeMOSYS del Plan de Acción, hoja Demandas_PJ |
| C-EI2 | Eficiencia energética industrial del Plan de Acción del PLANMICC: E5INDCOA con 2,45 % menos en 2035, rampa lineal 2026-2035 (razón del sandbox aplicada a la demanda de CONA6). | PLANMICC, Plan de Acción Fase I (MAE, 2026), tabla 36; modelo OSeMOSYS del Plan de Acción, hoja Demandas_PJ |
| C-EI3 | Eficiencia energética industrial del Plan de Acción del PLANMICC: E5INDCOK con 2,45 % menos en 2035, rampa lineal 2026-2035 (razón del sandbox aplicada a la demanda de CONA6). | PLANMICC, Plan de Acción Fase I (MAE, 2026), tabla 36; modelo OSeMOSYS del Plan de Acción, hoja Demandas_PJ |
| C-EI4 | Eficiencia energética industrial del Plan de Acción del PLANMICC: E5INDDSL con 2,45 % menos en 2035, rampa lineal 2026-2035 (razón del sandbox aplicada a la demanda de CONA6). | PLANMICC, Plan de Acción Fase I (MAE, 2026), tabla 36; modelo OSeMOSYS del Plan de Acción, hoja Demandas_PJ |
| C-EI5 | Eficiencia energética industrial del Plan de Acción del PLANMICC: E5INDELE con 2,45 % menos en 2035, rampa lineal 2026-2035 (razón del sandbox aplicada a la demanda de CONA6). | PLANMICC, Plan de Acción Fase I (MAE, 2026), tabla 36; modelo OSeMOSYS del Plan de Acción, hoja Demandas_PJ |
| C-EI6 | Eficiencia energética industrial del Plan de Acción del PLANMICC: E5INDFIR con 2,45 % menos en 2035, rampa lineal 2026-2035 (razón del sandbox aplicada a la demanda de CONA6). | PLANMICC, Plan de Acción Fase I (MAE, 2026), tabla 36; modelo OSeMOSYS del Plan de Acción, hoja Demandas_PJ |
| C-EI7 | Eficiencia energética industrial del Plan de Acción del PLANMICC: E5INDFOI con 2,45 % menos en 2035, rampa lineal 2026-2035 (razón del sandbox aplicada a la demanda de CONA6). | PLANMICC, Plan de Acción Fase I (MAE, 2026), tabla 36; modelo OSeMOSYS del Plan de Acción, hoja Demandas_PJ |
| C-EI8 | Eficiencia energética industrial del Plan de Acción del PLANMICC: E5INDGSL con 2,45 % menos en 2035, rampa lineal 2026-2035 (razón del sandbox aplicada a la demanda de CONA6). | PLANMICC, Plan de Acción Fase I (MAE, 2026), tabla 36; modelo OSeMOSYS del Plan de Acción, hoja Demandas_PJ |
| C-EI9 | Eficiencia energética industrial del Plan de Acción del PLANMICC: E5INDLPG con 2,45 % menos en 2035, rampa lineal 2026-2035 (razón del sandbox aplicada a la demanda de CONA6). | PLANMICC, Plan de Acción Fase I (MAE, 2026), tabla 36; modelo OSeMOSYS del Plan de Acción, hoja Demandas_PJ |
| C-EI10 | Eficiencia energética industrial del Plan de Acción del PLANMICC: E5INDNGS con 2,45 % menos en 2035, rampa lineal 2026-2035 (razón del sandbox aplicada a la demanda de CONA6). | PLANMICC, Plan de Acción Fase I (MAE, 2026), tabla 36; modelo OSeMOSYS del Plan de Acción, hoja Demandas_PJ |
| C-EI11 | Eficiencia energética industrial del Plan de Acción del PLANMICC: E5INDOID con 2,45 % menos en 2035, rampa lineal 2026-2035 (razón del sandbox aplicada a la demanda de CONA6). | PLANMICC, Plan de Acción Fase I (MAE, 2026), tabla 36; modelo OSeMOSYS del Plan de Acción, hoja Demandas_PJ |
| C-EI12 | Eficiencia energética industrial del Plan de Acción del PLANMICC: E5INDRDF con 2,45 % menos en 2035, rampa lineal 2026-2035 (razón del sandbox aplicada a la demanda de CONA6). | PLANMICC, Plan de Acción Fase I (MAE, 2026), tabla 36; modelo OSeMOSYS del Plan de Acción, hoja Demandas_PJ |
| C-EM1 | Electromovilidad del Plan de Acción del PLANMICC: gasolina carretera de pasajeros; en 2035 el combustible del transporte cae 2,8 % del tendencial y la electricidad añadida es el 1,4 %, descontado lo que ya hace el condicional; rampa lineal 2026-2035 (razón del sandbox aplicada a CONA6). | PLANMICC, Plan de Acción Fase I (MAE, 2026), tablas 35 y 36 |
| C-EM2 | Electromovilidad del Plan de Acción del PLANMICC: diésel carretero de pasajeros; en 2035 el combustible del transporte cae 2,8 % del tendencial y la electricidad añadida es el 1,4 %, descontado lo que ya hace el condicional; rampa lineal 2026-2035 (razón del sandbox aplicada a CONA6). | PLANMICC, Plan de Acción Fase I (MAE, 2026), tablas 35 y 36 |
| C-EM3 | Electromovilidad del Plan de Acción del PLANMICC: electricidad del transporte carretero de pasajeros; en 2035 el combustible del transporte cae 2,8 % del tendencial y la electricidad añadida es el 1,4 %, descontado lo que ya hace el condicional; rampa lineal 2026-2035 (razón del sandbox aplicada a CONA6). | PLANMICC, Plan de Acción Fase I (MAE, 2026), tablas 35 y 36 |

#### Iniciativas modeladas

| Iniciativa | Tramo | Tecnología en el modelo | Palancas | Entrada | Capacidad 2035, MW | Generación 2035, GWh | Declarado, kt/año | Adicionalidad; veredicto |
|---|---|---|---|---|---|---|---|---|
| C-EM Electromovilidad del Plan de Acción del PLANMICC (vehículos eléctricos e híbridos privados, taxis y buses) | Fuera de la NDC | Transporte (E5TROGSL) | C-EM1 |  |  |  |  | Por demostrar; sin veredicto |
| C-EM Electromovilidad del Plan de Acción del PLANMICC (vehículos eléctricos e híbridos privados, taxis y buses) | Fuera de la NDC | Transporte (E5TRODSL) | C-EM2 |  |  |  |  | Por demostrar; sin veredicto |
| C-EM Electromovilidad del Plan de Acción del PLANMICC (vehículos eléctricos e híbridos privados, taxis y buses) | Fuera de la NDC | Transporte (E5TROELE) | C-EM3 |  |  |  |  | Por demostrar; sin veredicto |
| C-EI Eficiencia energética industrial del Plan de Acción del PLANMICC (ISO 50001, ESCO) | Fuera de la NDC | Industria (E5INDBIM) | C-EI1 |  |  |  |  | Por demostrar; sin veredicto |
| C-EI Eficiencia energética industrial del Plan de Acción del PLANMICC (ISO 50001, ESCO) | Fuera de la NDC | Industria (E5INDCOA) | C-EI2 |  |  |  |  | Por demostrar; sin veredicto |
| C-EI Eficiencia energética industrial del Plan de Acción del PLANMICC (ISO 50001, ESCO) | Fuera de la NDC | Industria (E5INDCOK) | C-EI3 |  |  |  |  | Por demostrar; sin veredicto |
| C-EI Eficiencia energética industrial del Plan de Acción del PLANMICC (ISO 50001, ESCO) | Fuera de la NDC | Industria (E5INDDSL) | C-EI4 |  |  |  |  | Por demostrar; sin veredicto |
| C-EI Eficiencia energética industrial del Plan de Acción del PLANMICC (ISO 50001, ESCO) | Fuera de la NDC | Industria (E5INDELE) | C-EI5 |  |  |  |  | Por demostrar; sin veredicto |
| C-EI Eficiencia energética industrial del Plan de Acción del PLANMICC (ISO 50001, ESCO) | Fuera de la NDC | Industria (E5INDFIR) | C-EI6 |  |  |  |  | Por demostrar; sin veredicto |
| C-EI Eficiencia energética industrial del Plan de Acción del PLANMICC (ISO 50001, ESCO) | Fuera de la NDC | Industria (E5INDFOI) | C-EI7 |  |  |  |  | Por demostrar; sin veredicto |
| C-EI Eficiencia energética industrial del Plan de Acción del PLANMICC (ISO 50001, ESCO) | Fuera de la NDC | Industria (E5INDGSL) | C-EI8 |  |  |  |  | Por demostrar; sin veredicto |
| C-EI Eficiencia energética industrial del Plan de Acción del PLANMICC (ISO 50001, ESCO) | Fuera de la NDC | Industria (E5INDLPG) | C-EI9 |  |  |  |  | Por demostrar; sin veredicto |
| C-EI Eficiencia energética industrial del Plan de Acción del PLANMICC (ISO 50001, ESCO) | Fuera de la NDC | Industria (E5INDNGS) | C-EI10 |  |  |  |  | Por demostrar; sin veredicto |
| C-EI Eficiencia energética industrial del Plan de Acción del PLANMICC (ISO 50001, ESCO) | Fuera de la NDC | Industria (E5INDOID) | C-EI11 |  |  |  |  | Por demostrar; sin veredicto |
| C-EI Eficiencia energética industrial del Plan de Acción del PLANMICC (ISO 50001, ESCO) | Fuera de la NDC | Industria (E5INDRDF) | C-EI12 |  |  |  |  | Por demostrar; sin veredicto |
| C-GEO Proyecto Geotérmico Binacional Tufiño-Chiles-Cerro Negro (138 MW) | Fuera de la NDC | Geotermia (PPGEO) | C-GEO1 y C-GEO2 | 2029 | 189 | 1 307 |  | Por demostrar; sin veredicto |

Capacidad y generación en 2035 de la tecnología que modela la iniciativa (Output.csv del escenario), compartidas entre las iniciativas de esa tecnología; entrada: primer año con capacidad nueva en el escenario. Las cifras declaradas vienen de Art6_Adicionalidad.

#### Resultado de la corrida

Emisiones del sector energía, 2035 49 312 kt

Volumen adicional a la NDC, 2031-2035 10 952 kt 2 350 kt de esta capa

Margen nacional, 2035 11 888 kt regla prudente (los demás sectores cumplen solo su incondicional): 8 557 kt

| Generación en 2035 | Ambición ampliada, GWh | Ambición integral, GWh | Diferencia | Capacidad, MW |
|---|---|---|---|---|
| Geotermia | 353 | 1 307 | 955 | 51 → 189 |

#### Salida de la clase de Coca Codo (Coca Codo Sinclair y Sopladora)

A-CCOFF B-CCOFF C-CCOFF Riesgo Se aplica sobre la NDC financiada, el escenario «Ambición ampliada» y el escenario «Ambición integral»

Qué representa

Los dos choques a la vez.

Salida de la clase de Coca Codo y Sopladora. Supuesto del análisis: salida desde 2029 por el avance de la erosión regresiva del río Coca (frente a 3,6 km de la captación en mayo de 2026)

Respaldo de emergencia. Decisión del 13-10-2026: respaldo de fuel oil caro solo en los estados de riesgo, supuesto de cierre como la térmica arrendada que el país contrata hoy; regla de la variante de potencia mínima (Art6_calibracion/variante_suficiencia.py)

Lectura para el Artículo 6

- El volumen adicional a la NDC cae a cero en la NDC financiada, en el escenario «Ambición ampliada» y en el escenario «Ambición integral»; con el sistema intacto era de 2 473 kt, 8 602 kt y 10 952 kt.

- El margen nacional de 2035 queda en 4 515 kt en la NDC financiada, 7 779 kt en el escenario «Ambición ampliada» y 8 677 kt en el escenario «Ambición integral», con los otros sectores en el condicional que la NDC compromete; en la regla prudente (los otros sectores solo cumplen su tramo incondicional), en 1 184 kt, 4 447 kt y 5 345 kt.

- Si el país autoriza los 11 674 kt transferibles con el sistema intacto, quedan sin respaldo 736 kt con los otros sectores en el condicional que la NDC compromete y 6 785 kt en la regla prudente.

Origen y alcance

Alcance, límites y validación

Salida de la clase de Coca Codo y Sopladora. Cota: retira la clase completa (1.987 MW: Coca Codo 1.500 y Sopladora 487).

verificar.py: cada estado difiere de su escenario solo en sus palancas.

Respaldo de emergencia. Supuesto de cierre, no es un riesgo: solo se construye la potencia que falta; la energía de respaldo se reporta con sus emisiones, la energía no suministrada equivalente y sus horas de corte equivalentes. En INCA6G las mismas palancas son las filas RE01 de correcciones_K.csv: un supuesto de cierre introducido en la corrida K16 del 13-10-2026, fuera del acuerdo original (respaldo solo en estados de riesgo); se aprobó el 13-10-2026, después de la verificación independiente, conservarlo rotulado «con cierre de fuel oil de emergencia», con el peso del respaldo al lado.

B2_Output_Art6/tablas/respaldo_por_escenario.csv

#### Qué cambia frente al sistema intacto

| Parámetro en 2035 | Sistema intacto | Con el choque | Desde |
|---|---|---|---|
| Factor de planta de la clase PPHRORAB | 0,568 | 0,000 | 2029 |
| Factor de planta medio de las once clases hidroeléctricas | 0,539 | 0,487 | 2029 |

Palancas en B1_Scenario_Config.xlsx (7)

| Palanca | Qué fija | Fuente |
|---|---|---|
| R-CC01 a R-CC03 (3) | Salida de la clase de Coca Codo y Sopladora. Factor de planta y límites de actividad de PPHRORAB en cero desde 2029. | Supuesto del análisis: salida desde 2029 por el avance de la erosión regresiva del río Coca (frente a 3,6 km de la captación en mayo de 2026) |
| RE1 | Respaldo de emergencia (supuesto de cierre, como la térmica arrendada que el país contrata hoy): tope de capacidad de PPFOI liberado desde 2026 (99999, el valor por omisión) en lugar del tope K15b (potencia existente más expansión declarada). | Decisión del 13-10-2026: respaldo de fuel oil caro solo en los estados de riesgo, supuesto de cierre como la térmica arrendada que el país contrata hoy; regla de la variante de potencia mínima (Art6_calibracion/variante_suficiencia.py) |
| RE2 | Respaldo de emergencia (supuesto de cierre, como la térmica arrendada que el país contrata hoy): CapitalCost de PPFOI 2026-2035 por 1.000: el modelo construye solo la potencia sin la cual no cubre la demanda. | Decisión del 13-10-2026: respaldo de fuel oil caro solo en los estados de riesgo, supuesto de cierre como la térmica arrendada que el país contrata hoy; regla de la variante de potencia mínima (Art6_calibracion/variante_suficiencia.py) |
| RE3 | Respaldo de emergencia (supuesto de cierre, como la térmica arrendada que el país contrata hoy): FixedCost de PPFOI 2026-2035 por 1.000. | Decisión del 13-10-2026: respaldo de fuel oil caro solo en los estados de riesgo, supuesto de cierre como la térmica arrendada que el país contrata hoy; regla de la variante de potencia mínima (Art6_calibracion/variante_suficiencia.py) |
| RE4 | Respaldo de emergencia (supuesto de cierre, como la térmica arrendada que el país contrata hoy): STOELE cerrado en 2026-2035 (tope de capacidad cero): es un atajo sin correlato físico que el modelo usa cuando falta potencia y que subestima las emisiones. | Decisión del 13-10-2026: respaldo de fuel oil caro solo en los estados de riesgo, supuesto de cierre como la térmica arrendada que el país contrata hoy; regla de la variante de potencia mínima (Art6_calibracion/variante_suficiencia.py) |

#### Resultado de la corrida

| Sistema intacto → con el choque | NDC financiada | Ambición ampliada | Ambición integral |
|---|---|---|---|
| Emisiones del sector energía, 2035 (kt) | 50 328 → 56 685 | 50 044 → 53 422 | 49 312 → 52 524 |
| Volumen adicional a la NDC, 2031-2035 (kt) | 2 473 → 0 | 8 602 → 0 | 10 952 → 0 |
| Margen nacional 2035 (kt) | 10 872 → 4 515 | 11 156 → 7 779 | 11 888 → 8 677 |
| Margen 2035, regla prudente: los demás sectores cumplen solo su incondicional (kt) | 7 540 → 1 184 | 7 825 → 4 447 | 8 557 → 5 345 |
| Generación hidroeléctrica 2035 (GWh) | 34 865 → 25 506 | 34 860 → 25 506 | 34 860 → 25 506 |
| Térmica desplazable 2035 (GWh) | 562 → 9 920 | 60 → 5 693 | 60 → 5 479 |

#### Salida de Coca Codo sola (caso central)

A-CCSOLO B-CCSOLO C-CCSOLO Riesgo Se aplica sobre la NDC financiada, el escenario «Ambición ampliada» y el escenario «Ambición integral»

Qué representa

Los dos choques a la vez.

Salida de Coca Codo sola. CENACE, Informe Anual 2025, Parte 1, figuras 1.4 y 1.5, p. 31-32 (S26-008): Coca Codo 7.695,99 GWh y Sopladora 2.884,03 GWh brutos (Art6_calibracion/parametros_hidro_por_clase.csv)

Respaldo de emergencia. Decisión del 13-10-2026: respaldo de fuel oil caro solo en los estados de riesgo, supuesto de cierre como la térmica arrendada que el país contrata hoy; regla de la variante de potencia mínima (Art6_calibracion/variante_suficiencia.py)

Lectura para el Artículo 6

- El volumen adicional a la NDC cae a cero en la NDC financiada, en el escenario «Ambición ampliada» y en el escenario «Ambición integral»; con el sistema intacto era de 2 473 kt, 8 602 kt y 10 952 kt.

- El margen nacional de 2035 queda en 6 494 kt en la NDC financiada, 9 439 kt en el escenario «Ambición ampliada» y 10 290 kt en el escenario «Ambición integral», con los otros sectores en el condicional que la NDC compromete; en la regla prudente (los otros sectores solo cumplen su tramo incondicional), en 3 162 kt, 6 107 kt y 6 958 kt.

- Si el país autoriza los 11 674 kt transferibles con el sistema intacto, quedan sin respaldo 0 kt con los otros sectores en el condicional que la NDC compromete y 4 006 kt en la regla prudente.

Origen y alcance

Alcance, límites y validación

Salida de Coca Codo sola. Caso central del riesgo de la central.

verificar.py

Respaldo de emergencia. Supuesto de cierre, no es un riesgo: solo se construye la potencia que falta; la energía de respaldo se reporta con sus emisiones, la energía no suministrada equivalente y sus horas de corte equivalentes. En INCA6G las mismas palancas son las filas RE01 de correcciones_K.csv: un supuesto de cierre introducido en la corrida K16 del 13-10-2026, fuera del acuerdo original (respaldo solo en estados de riesgo); se aprobó el 13-10-2026, después de la verificación independiente, conservarlo rotulado «con cierre de fuel oil de emergencia», con el peso del respaldo al lado.

B2_Output_Art6/tablas/respaldo_por_escenario.csv

#### Qué cambia frente al sistema intacto

| Parámetro en 2035 | Sistema intacto | Con el choque | Desde |
|---|---|---|---|
| Factor de planta de la clase PPHRORAB | 0,568 | 0,155 | 2029 |
| Factor de planta medio de las once clases hidroeléctricas | 0,539 | 0,501 | 2029 |

Palancas en B1_Scenario_Config.xlsx (7)

| Palanca | Qué fija | Fuente |
|---|---|---|
| R-CS01 a R-CS03 (3) | Salida de Coca Codo sola. PPHRORAB por 0.2726 desde 2029 (sale la participación de Coca Codo en la energía de la clase, 0.7274). | Supuesto del análisis: salida desde 2029 por el avance de la erosión regresiva del río Coca (frente a 3,6 km de la captación en mayo de 2026); CENACE, Informe Anual 2025, Parte 1, figuras 1.4 y 1.5, p. 31-32 (S26-008): Coca Codo 7.695,99 GWh y Sopladora 2.884,03 GWh brutos (Art6_calibracion/parametros_hidro_por_clase.csv) |
| RE1 | Respaldo de emergencia (supuesto de cierre, como la térmica arrendada que el país contrata hoy): tope de capacidad de PPFOI liberado desde 2026 (99999, el valor por omisión) en lugar del tope K15b (potencia existente más expansión declarada). | Decisión del 13-10-2026: respaldo de fuel oil caro solo en los estados de riesgo, supuesto de cierre como la térmica arrendada que el país contrata hoy; regla de la variante de potencia mínima (Art6_calibracion/variante_suficiencia.py) |
| RE2 | Respaldo de emergencia (supuesto de cierre, como la térmica arrendada que el país contrata hoy): CapitalCost de PPFOI 2026-2035 por 1.000: el modelo construye solo la potencia sin la cual no cubre la demanda. | Decisión del 13-10-2026: respaldo de fuel oil caro solo en los estados de riesgo, supuesto de cierre como la térmica arrendada que el país contrata hoy; regla de la variante de potencia mínima (Art6_calibracion/variante_suficiencia.py) |
| RE3 | Respaldo de emergencia (supuesto de cierre, como la térmica arrendada que el país contrata hoy): FixedCost de PPFOI 2026-2035 por 1.000. | Decisión del 13-10-2026: respaldo de fuel oil caro solo en los estados de riesgo, supuesto de cierre como la térmica arrendada que el país contrata hoy; regla de la variante de potencia mínima (Art6_calibracion/variante_suficiencia.py) |
| RE4 | Respaldo de emergencia (supuesto de cierre, como la térmica arrendada que el país contrata hoy): STOELE cerrado en 2026-2035 (tope de capacidad cero): es un atajo sin correlato físico que el modelo usa cuando falta potencia y que subestima las emisiones. | Decisión del 13-10-2026: respaldo de fuel oil caro solo en los estados de riesgo, supuesto de cierre como la térmica arrendada que el país contrata hoy; regla de la variante de potencia mínima (Art6_calibracion/variante_suficiencia.py) |

#### Resultado de la corrida

| Sistema intacto → con el choque | NDC financiada | Ambición ampliada | Ambición integral |
|---|---|---|---|
| Emisiones del sector energía, 2035 (kt) | 50 328 → 54 707 | 50 044 → 51 761 | 49 312 → 50 910 |
| Volumen adicional a la NDC, 2031-2035 (kt) | 2 473 → 0 | 8 602 → 0 | 10 952 → 0 |
| Margen nacional 2035 (kt) | 10 872 → 6 494 | 11 156 → 9 439 | 11 888 → 10 290 |
| Margen 2035, regla prudente: los demás sectores cumplen solo su incondicional (kt) | 7 540 → 3 162 | 7 825 → 6 107 | 8 557 → 6 958 |
| Generación hidroeléctrica 2035 (GWh) | 34 865 → 28 065 | 34 860 → 28 065 | 34 860 → 28 065 |
| Térmica desplazable 2035 (GWh) | 562 → 7 362 | 60 → 3 134 | 60 → 2 920 |

#### Derrateo de Coca Codo

A-CCDER B-CCDER C-CCDER Riesgo Se aplica sobre la NDC financiada, el escenario «Ambición ampliada» y el escenario «Ambición integral»

Qué representa

Los dos choques a la vez.

Derrateo del 20 % de Coca Codo. CENACE, Informe Anual 2025, Parte 1, figuras 1.4 y 1.5, p. 31-32 (S26-008): Coca Codo 7.695,99 GWh y Sopladora 2.884,03 GWh brutos (Art6_calibracion/parametros_hidro_por_clase.csv)

Respaldo de emergencia. Decisión del 13-10-2026: respaldo de fuel oil caro solo en los estados de riesgo, supuesto de cierre como la térmica arrendada que el país contrata hoy; regla de la variante de potencia mínima (Art6_calibracion/variante_suficiencia.py)

Lectura para el Artículo 6

- El volumen adicional a la NDC pasa de 2 473 a 0 kt en la NDC financiada, de 8 602 a 6 897 kt en el escenario «Ambición ampliada» y de 10 952 a 8 909 kt en el escenario «Ambición integral».

- El margen nacional de 2035 queda en 10 114 kt en la NDC financiada, 11 156 kt en el escenario «Ambición ampliada» y 11 888 kt en el escenario «Ambición integral», con los otros sectores en el condicional que la NDC compromete; en la regla prudente (los otros sectores solo cumplen su tramo incondicional), en 6 782 kt, 7 825 kt y 8 557 kt.

- Lo que el país autorizaría con el sistema intacto, 11 674 kt, sigue cabiendo en el margen.

Origen y alcance

Alcance, límites y validación

Derrateo del 20 % de Coca Codo. Medido por participación en energía (decisión del 12-10-2026).

verificar.py

Respaldo de emergencia. Supuesto de cierre, no es un riesgo: solo se construye la potencia que falta; la energía de respaldo se reporta con sus emisiones, la energía no suministrada equivalente y sus horas de corte equivalentes. En INCA6G las mismas palancas son las filas RE01 de correcciones_K.csv: un supuesto de cierre introducido en la corrida K16 del 13-10-2026, fuera del acuerdo original (respaldo solo en estados de riesgo); se aprobó el 13-10-2026, después de la verificación independiente, conservarlo rotulado «con cierre de fuel oil de emergencia», con el peso del respaldo al lado.

B2_Output_Art6/tablas/respaldo_por_escenario.csv

#### Qué cambia frente al sistema intacto

| Parámetro en 2035 | Sistema intacto | Con el choque | Desde |
|---|---|---|---|
| Factor de planta de la clase PPHRORAB | 0,568 | 0,485 | 2027 |
| Factor de planta medio de las once clases hidroeléctricas | 0,539 | 0,531 | 2027 |

Palancas en B1_Scenario_Config.xlsx (7)

| Palanca | Qué fija | Fuente |
|---|---|---|
| R-CD01 a R-CD03 (3) | Derrateo del 20 % de Coca Codo. PPHRORAB por 1 - 0,20 x 0.7274 = 0.8545 desde 2027. | Supuesto del análisis: derrateo crónico del 20 %; CENACE, Informe Anual 2025, Parte 1, figuras 1.4 y 1.5, p. 31-32 (S26-008): Coca Codo 7.695,99 GWh y Sopladora 2.884,03 GWh brutos (Art6_calibracion/parametros_hidro_por_clase.csv) |
| RE1 | Respaldo de emergencia (supuesto de cierre, como la térmica arrendada que el país contrata hoy): tope de capacidad de PPFOI liberado desde 2026 (99999, el valor por omisión) en lugar del tope K15b (potencia existente más expansión declarada). | Decisión del 13-10-2026: respaldo de fuel oil caro solo en los estados de riesgo, supuesto de cierre como la térmica arrendada que el país contrata hoy; regla de la variante de potencia mínima (Art6_calibracion/variante_suficiencia.py) |
| RE2 | Respaldo de emergencia (supuesto de cierre, como la térmica arrendada que el país contrata hoy): CapitalCost de PPFOI 2026-2035 por 1.000: el modelo construye solo la potencia sin la cual no cubre la demanda. | Decisión del 13-10-2026: respaldo de fuel oil caro solo en los estados de riesgo, supuesto de cierre como la térmica arrendada que el país contrata hoy; regla de la variante de potencia mínima (Art6_calibracion/variante_suficiencia.py) |
| RE3 | Respaldo de emergencia (supuesto de cierre, como la térmica arrendada que el país contrata hoy): FixedCost de PPFOI 2026-2035 por 1.000. | Decisión del 13-10-2026: respaldo de fuel oil caro solo en los estados de riesgo, supuesto de cierre como la térmica arrendada que el país contrata hoy; regla de la variante de potencia mínima (Art6_calibracion/variante_suficiencia.py) |
| RE4 | Respaldo de emergencia (supuesto de cierre, como la térmica arrendada que el país contrata hoy): STOELE cerrado en 2026-2035 (tope de capacidad cero): es un atajo sin correlato físico que el modelo usa cuando falta potencia y que subestima las emisiones. | Decisión del 13-10-2026: respaldo de fuel oil caro solo en los estados de riesgo, supuesto de cierre como la térmica arrendada que el país contrata hoy; regla de la variante de potencia mínima (Art6_calibracion/variante_suficiencia.py) |

#### Resultado de la corrida

| Sistema intacto → con el choque | NDC financiada | Ambición ampliada | Ambición integral |
|---|---|---|---|
| Emisiones del sector energía, 2035 (kt) | 50 328 → 51 086 | 50 044 → 50 044 | 49 312 → 49 312 |
| Volumen adicional a la NDC, 2031-2035 (kt) | 2 473 → 0 | 8 602 → 6 897 | 10 952 → 8 909 |
| Margen nacional 2035 (kt) | 10 872 → 10 114 | 11 156 → 11 156 | 11 888 → 11 888 |
| Margen 2035, regla prudente: los demás sectores cumplen solo su incondicional (kt) | 7 540 → 6 782 | 7 825 → 7 825 | 8 557 → 8 557 |
| Generación hidroeléctrica 2035 (GWh) | 34 865 → 33 500 | 34 860 → 33 278 | 34 860 → 33 500 |
| Térmica desplazable 2035 (GWh) | 562 → 1 927 | 60 → 60 | 60 → 60 |

#### Año seco severo (cota)

A-ANOSECO B-ANOSECO C-ANOSECO Riesgo Se aplica sobre la NDC financiada, el escenario «Ambición ampliada» y el escenario «Ambición integral»

Qué representa

Los dos choques a la vez.

Año seco severo con la hidrología de 2024. CENACE (2025), Informe Anual 2024, tabla 1.14, p. 73; razón por clase ponderada por la potencia nominal de la capa CENTRALES (Art6_calibracion/parametros_hidro_por_clase.csv, derivado de CENTRALES.shp de ARCONEL, uso autorizado)

Respaldo de emergencia. Decisión del 13-10-2026: respaldo de fuel oil caro solo en los estados de riesgo, supuesto de cierre como la térmica arrendada que el país contrata hoy; regla de la variante de potencia mínima (Art6_calibracion/variante_suficiencia.py)

Lectura para el Artículo 6

- El volumen adicional a la NDC cae a cero en la NDC financiada, en el escenario «Ambición ampliada» y en el escenario «Ambición integral»; con el sistema intacto era de 2 473 kt, 8 602 kt y 10 952 kt.

- El margen nacional de 2035 queda en 5 230 kt en la NDC financiada, 8 469 kt en el escenario «Ambición ampliada» y 9 359 kt en el escenario «Ambición integral», con los otros sectores en el condicional que la NDC compromete; en la regla prudente (los otros sectores solo cumplen su tramo incondicional), en 1 898 kt, 5 137 kt y 6 027 kt.

- Si el país autoriza los 11 674 kt transferibles con el sistema intacto, quedan sin respaldo 0 kt con los otros sectores en el condicional que la NDC compromete y 3 651 kt en la regla prudente.

Origen y alcance

Alcance, límites y validación

Año seco severo con la hidrología de 2024. Cota; desde 2026 porque la historia ya es observada.

verificar.py: cociente frente a CONA6 igual a la razón de Art6_AnoSeco.

Respaldo de emergencia. Supuesto de cierre, no es un riesgo: solo se construye la potencia que falta; la energía de respaldo se reporta con sus emisiones, la energía no suministrada equivalente y sus horas de corte equivalentes. En INCA6G las mismas palancas son las filas RE01 de correcciones_K.csv: un supuesto de cierre introducido en la corrida K16 del 13-10-2026, fuera del acuerdo original (respaldo solo en estados de riesgo); se aprobó el 13-10-2026, después de la verificación independiente, conservarlo rotulado «con cierre de fuel oil de emergencia», con el peso del respaldo al lado.

B2_Output_Art6/tablas/respaldo_por_escenario.csv

#### Qué cambia frente al sistema intacto

| Parámetro en 2035 | Sistema intacto | Con el choque | Desde |
|---|---|---|---|
| Factor de planta de la clase PPHRORAB | 0,568 | 0,490 | 2026 |
| Factor de planta medio de las once clases hidroeléctricas | 0,539 | 0,409 | 2026 |

Palancas en B1_Scenario_Config.xlsx (37)

| Palanca | Qué fija | Fuente |
|---|---|---|
| R-AS01 a R-AS33 (33) | Año seco severo con la hidrología de 2024. Factor de planta, piso y techo de las 11 clases hidroeléctricas por la razón de caudales de 2024 de cada clase, en todos los años desde 2026. | CENACE (2025), Informe Anual 2024, tabla 1.14, p. 73; razón por clase ponderada por la potencia nominal de la capa CENTRALES (Art6_calibracion/parametros_hidro_por_clase.csv, derivado de CENTRALES.shp de ARCONEL, uso autorizado) |
| RE1 | Respaldo de emergencia (supuesto de cierre, como la térmica arrendada que el país contrata hoy): tope de capacidad de PPFOI liberado desde 2026 (99999, el valor por omisión) en lugar del tope K15b (potencia existente más expansión declarada). | Decisión del 13-10-2026: respaldo de fuel oil caro solo en los estados de riesgo, supuesto de cierre como la térmica arrendada que el país contrata hoy; regla de la variante de potencia mínima (Art6_calibracion/variante_suficiencia.py) |
| RE2 | Respaldo de emergencia (supuesto de cierre, como la térmica arrendada que el país contrata hoy): CapitalCost de PPFOI 2026-2035 por 1.000: el modelo construye solo la potencia sin la cual no cubre la demanda. | Decisión del 13-10-2026: respaldo de fuel oil caro solo en los estados de riesgo, supuesto de cierre como la térmica arrendada que el país contrata hoy; regla de la variante de potencia mínima (Art6_calibracion/variante_suficiencia.py) |
| RE3 | Respaldo de emergencia (supuesto de cierre, como la térmica arrendada que el país contrata hoy): FixedCost de PPFOI 2026-2035 por 1.000. | Decisión del 13-10-2026: respaldo de fuel oil caro solo en los estados de riesgo, supuesto de cierre como la térmica arrendada que el país contrata hoy; regla de la variante de potencia mínima (Art6_calibracion/variante_suficiencia.py) |
| RE4 | Respaldo de emergencia (supuesto de cierre, como la térmica arrendada que el país contrata hoy): STOELE cerrado en 2026-2035 (tope de capacidad cero): es un atajo sin correlato físico que el modelo usa cuando falta potencia y que subestima las emisiones. | Decisión del 13-10-2026: respaldo de fuel oil caro solo en los estados de riesgo, supuesto de cierre como la térmica arrendada que el país contrata hoy; regla de la variante de potencia mínima (Art6_calibracion/variante_suficiencia.py) |

#### Resultado de la corrida

| Sistema intacto → con el choque | NDC financiada | Ambición ampliada | Ambición integral |
|---|---|---|---|
| Emisiones del sector energía, 2035 (kt) | 50 328 → 55 971 | 50 044 → 52 732 | 49 312 → 51 842 |
| Volumen adicional a la NDC, 2031-2035 (kt) | 2 473 → 0 | 8 602 → 0 | 10 952 → 0 |
| Margen nacional 2035 (kt) | 10 872 → 5 230 | 11 156 → 8 469 | 11 888 → 9 359 |
| Margen 2035, regla prudente: los demás sectores cumplen solo su incondicional (kt) | 7 540 → 1 898 | 7 825 → 5 137 | 8 557 → 6 027 |
| Generación hidroeléctrica 2035 (GWh) | 34 865 → 26 449 | 34 860 → 26 449 | 34 860 → 26 449 |
| Térmica desplazable 2035 (GWh) | 562 → 8 997 | 60 → 4 769 | 60 → 4 555 |

#### Un año seco cada tres (caso central)

A-ANOSEC3 B-ANOSEC3 C-ANOSEC3 Riesgo Se aplica sobre la NDC financiada, el escenario «Ambición ampliada» y el escenario «Ambición integral»

Qué representa

Los dos choques a la vez.

Un año seco cada tres. CENACE (2025), Informe Anual 2024, tabla 1.14, p. 73; razón por clase ponderada por la potencia nominal de la capa CENTRALES (Art6_calibracion/parametros_hidro_por_clase.csv, derivado de CENTRALES.shp de ARCONEL, uso autorizado)

Respaldo de emergencia. Decisión del 13-10-2026: respaldo de fuel oil caro solo en los estados de riesgo, supuesto de cierre como la térmica arrendada que el país contrata hoy; regla de la variante de potencia mínima (Art6_calibracion/variante_suficiencia.py)

Lectura para el Artículo 6

- El volumen adicional a la NDC pasa de 2 473 a 1 678 kt en la NDC financiada, de 8 602 a 5 605 kt en el escenario «Ambición ampliada» y de 10 952 a 7 016 kt en el escenario «Ambición integral».

- El margen nacional de 2035 queda en 5 230 kt en la NDC financiada, 8 469 kt en el escenario «Ambición ampliada» y 9 359 kt en el escenario «Ambición integral», con los otros sectores en el condicional que la NDC compromete; en la regla prudente (los otros sectores solo cumplen su tramo incondicional), en 1 898 kt, 5 137 kt y 6 027 kt.

- Si el país autoriza los 11 674 kt transferibles con el sistema intacto, quedan sin respaldo 0 kt con los otros sectores en el condicional que la NDC compromete y 1 080 kt en la regla prudente.

Origen y alcance

Alcance, límites y validación

Un año seco cada tres. Caso central del riesgo hidrológico (decisión del 12-10-2026); 2026 es año seco observado.

verificar.py

Respaldo de emergencia. Supuesto de cierre, no es un riesgo: solo se construye la potencia que falta; la energía de respaldo se reporta con sus emisiones, la energía no suministrada equivalente y sus horas de corte equivalentes. En INCA6G las mismas palancas son las filas RE01 de correcciones_K.csv: un supuesto de cierre introducido en la corrida K16 del 13-10-2026, fuera del acuerdo original (respaldo solo en estados de riesgo); se aprobó el 13-10-2026, después de la verificación independiente, conservarlo rotulado «con cierre de fuel oil de emergencia», con el peso del respaldo al lado.

B2_Output_Art6/tablas/respaldo_por_escenario.csv

#### Qué cambia frente al sistema intacto

| Parámetro en 2035 | Sistema intacto | Con el choque | Desde |
|---|---|---|---|
| Factor de planta de la clase PPHRORAB | 0,568 | 0,490 | 2026; valor final desde 2035 |
| Factor de planta medio de las once clases hidroeléctricas | 0,539 | 0,409 | 2026; valor final desde 2035 |

Palancas en B1_Scenario_Config.xlsx (37)

| Palanca | Qué fija | Fuente |
|---|---|---|
| R-A301 a R-A333 (33) | Un año seco cada tres. Las mismas razones solo en 2026, 2029, 2032 y 2035. | CENACE (2025), Informe Anual 2024, tabla 1.14, p. 73; razón por clase ponderada por la potencia nominal de la capa CENTRALES (Art6_calibracion/parametros_hidro_por_clase.csv, derivado de CENTRALES.shp de ARCONEL, uso autorizado) |
| RE1 | Respaldo de emergencia (supuesto de cierre, como la térmica arrendada que el país contrata hoy): tope de capacidad de PPFOI liberado desde 2026 (99999, el valor por omisión) en lugar del tope K15b (potencia existente más expansión declarada). | Decisión del 13-10-2026: respaldo de fuel oil caro solo en los estados de riesgo, supuesto de cierre como la térmica arrendada que el país contrata hoy; regla de la variante de potencia mínima (Art6_calibracion/variante_suficiencia.py) |
| RE2 | Respaldo de emergencia (supuesto de cierre, como la térmica arrendada que el país contrata hoy): CapitalCost de PPFOI 2026-2035 por 1.000: el modelo construye solo la potencia sin la cual no cubre la demanda. | Decisión del 13-10-2026: respaldo de fuel oil caro solo en los estados de riesgo, supuesto de cierre como la térmica arrendada que el país contrata hoy; regla de la variante de potencia mínima (Art6_calibracion/variante_suficiencia.py) |
| RE3 | Respaldo de emergencia (supuesto de cierre, como la térmica arrendada que el país contrata hoy): FixedCost de PPFOI 2026-2035 por 1.000. | Decisión del 13-10-2026: respaldo de fuel oil caro solo en los estados de riesgo, supuesto de cierre como la térmica arrendada que el país contrata hoy; regla de la variante de potencia mínima (Art6_calibracion/variante_suficiencia.py) |
| RE4 | Respaldo de emergencia (supuesto de cierre, como la térmica arrendada que el país contrata hoy): STOELE cerrado en 2026-2035 (tope de capacidad cero): es un atajo sin correlato físico que el modelo usa cuando falta potencia y que subestima las emisiones. | Decisión del 13-10-2026: respaldo de fuel oil caro solo en los estados de riesgo, supuesto de cierre como la térmica arrendada que el país contrata hoy; regla de la variante de potencia mínima (Art6_calibracion/variante_suficiencia.py) |

#### Resultado de la corrida

| Sistema intacto → con el choque | NDC financiada | Ambición ampliada | Ambición integral |
|---|---|---|---|
| Emisiones del sector energía, 2035 (kt) | 50 328 → 55 971 | 50 044 → 52 732 | 49 312 → 51 842 |
| Volumen adicional a la NDC, 2031-2035 (kt) | 2 473 → 1 678 | 8 602 → 5 605 | 10 952 → 7 016 |
| Margen nacional 2035 (kt) | 10 872 → 5 230 | 11 156 → 8 469 | 11 888 → 9 359 |
| Margen 2035, regla prudente: los demás sectores cumplen solo su incondicional (kt) | 7 540 → 1 898 | 7 825 → 5 137 | 8 557 → 6 027 |
| Generación hidroeléctrica 2035 (GWh) | 34 865 → 26 449 | 34 860 → 26 449 | 34 860 → 26 449 |
| Térmica desplazable 2035 (GWh) | 562 → 8 997 | 60 → 4 769 | 60 → 4 555 |

#### Año seco moderado

A-ANOSECM B-ANOSECM C-ANOSECM Riesgo Se aplica sobre la NDC financiada, el escenario «Ambición ampliada» y el escenario «Ambición integral»

Qué representa

Los dos choques a la vez.

Año seco moderado. BEN 2025 (MAE), tabla 2.20: caída de 9,2 % de la hidro en 2024

Respaldo de emergencia. Decisión del 13-10-2026: respaldo de fuel oil caro solo en los estados de riesgo, supuesto de cierre como la térmica arrendada que el país contrata hoy; regla de la variante de potencia mínima (Art6_calibracion/variante_suficiencia.py)

Lectura para el Artículo 6

- El volumen adicional a la NDC pasa de 2 473 a 0 kt en la NDC financiada, de 8 602 a 4 625 kt en el escenario «Ambición ampliada» y de 10 952 a 6 183 kt en el escenario «Ambición integral».

- El margen nacional de 2035 queda en 9 182 kt en la NDC financiada, 11 156 kt en el escenario «Ambición ampliada» y 11 888 kt en el escenario «Ambición integral», con los otros sectores en el condicional que la NDC compromete; en la regla prudente (los otros sectores solo cumplen su tramo incondicional), en 5 850 kt, 7 825 kt y 8 557 kt.

- Lo que el país autorizaría con el sistema intacto, 11 674 kt, sigue cabiendo en el margen.

Origen y alcance

Alcance, límites y validación

Año seco moderado. Variante moderada.

verificar.py

Respaldo de emergencia. Supuesto de cierre, no es un riesgo: solo se construye la potencia que falta; la energía de respaldo se reporta con sus emisiones, la energía no suministrada equivalente y sus horas de corte equivalentes. En INCA6G las mismas palancas son las filas RE01 de correcciones_K.csv: un supuesto de cierre introducido en la corrida K16 del 13-10-2026, fuera del acuerdo original (respaldo solo en estados de riesgo); se aprobó el 13-10-2026, después de la verificación independiente, conservarlo rotulado «con cierre de fuel oil de emergencia», con el peso del respaldo al lado.

B2_Output_Art6/tablas/respaldo_por_escenario.csv

#### Qué cambia frente al sistema intacto

| Parámetro en 2035 | Sistema intacto | Con el choque | Desde |
|---|---|---|---|
| Factor de planta de la clase PPHRORAB | 0,568 | 0,515 | 2026 |
| Factor de planta medio de las once clases hidroeléctricas | 0,539 | 0,489 | 2026 |

Palancas en B1_Scenario_Config.xlsx (37)

| Palanca | Qué fija | Fuente |
|---|---|---|
| R-AM01 a R-AM33 (33) | Año seco moderado. Toda la hidroelectricidad por 0,908 desde 2026. | BEN 2025 (MAE), tabla 2.20, p. 66: generación hidroeléctrica 2024 frente a 2023 |
| RE1 | Respaldo de emergencia (supuesto de cierre, como la térmica arrendada que el país contrata hoy): tope de capacidad de PPFOI liberado desde 2026 (99999, el valor por omisión) en lugar del tope K15b (potencia existente más expansión declarada). | Decisión del 13-10-2026: respaldo de fuel oil caro solo en los estados de riesgo, supuesto de cierre como la térmica arrendada que el país contrata hoy; regla de la variante de potencia mínima (Art6_calibracion/variante_suficiencia.py) |
| RE2 | Respaldo de emergencia (supuesto de cierre, como la térmica arrendada que el país contrata hoy): CapitalCost de PPFOI 2026-2035 por 1.000: el modelo construye solo la potencia sin la cual no cubre la demanda. | Decisión del 13-10-2026: respaldo de fuel oil caro solo en los estados de riesgo, supuesto de cierre como la térmica arrendada que el país contrata hoy; regla de la variante de potencia mínima (Art6_calibracion/variante_suficiencia.py) |
| RE3 | Respaldo de emergencia (supuesto de cierre, como la térmica arrendada que el país contrata hoy): FixedCost de PPFOI 2026-2035 por 1.000. | Decisión del 13-10-2026: respaldo de fuel oil caro solo en los estados de riesgo, supuesto de cierre como la térmica arrendada que el país contrata hoy; regla de la variante de potencia mínima (Art6_calibracion/variante_suficiencia.py) |
| RE4 | Respaldo de emergencia (supuesto de cierre, como la térmica arrendada que el país contrata hoy): STOELE cerrado en 2026-2035 (tope de capacidad cero): es un atajo sin correlato físico que el modelo usa cuando falta potencia y que subestima las emisiones. | Decisión del 13-10-2026: respaldo de fuel oil caro solo en los estados de riesgo, supuesto de cierre como la térmica arrendada que el país contrata hoy; regla de la variante de potencia mínima (Art6_calibracion/variante_suficiencia.py) |

#### Resultado de la corrida

| Sistema intacto → con el choque | NDC financiada | Ambición ampliada | Ambición integral |
|---|---|---|---|
| Emisiones del sector energía, 2035 (kt) | 50 328 → 52 018 | 50 044 → 50 044 | 49 312 → 49 312 |
| Volumen adicional a la NDC, 2031-2035 (kt) | 2 473 → 0 | 8 602 → 4 625 | 10 952 → 6 183 |
| Margen nacional 2035 (kt) | 10 872 → 9 182 | 11 156 → 11 156 | 11 888 → 11 888 |
| Margen 2035, regla prudente: los demás sectores cumplen solo su incondicional (kt) | 7 540 → 5 850 | 7 825 → 7 825 | 8 557 → 8 557 |
| Generación hidroeléctrica 2035 (GWh) | 34 865 → 31 830 | 34 860 → 31 642 | 34 860 → 31 823 |
| Térmica desplazable 2035 (GWh) | 562 → 3 607 | 60 → 60 | 60 → 60 |

#### Salida de la clase de Coca Codo y año seco severo

A-CCOFFANOSECO B-CCOFFANOSECO C-CCOFFANOSECO Riesgo Se aplica sobre la NDC financiada, el escenario «Ambición ampliada» y el escenario «Ambición integral»

Qué representa

Los dos choques a la vez.

Salida de la clase de Coca Codo y Sopladora. Supuesto del análisis: salida desde 2029 por el avance de la erosión regresiva del río Coca (frente a 3,6 km de la captación en mayo de 2026)

Año seco severo con la hidrología de 2024. CENACE (2025), Informe Anual 2024, tabla 1.14, p. 73; razón por clase ponderada por la potencia nominal de la capa CENTRALES (Art6_calibracion/parametros_hidro_por_clase.csv, derivado de CENTRALES.shp de ARCONEL, uso autorizado)

Respaldo de emergencia. Decisión del 13-10-2026: respaldo de fuel oil caro solo en los estados de riesgo, supuesto de cierre como la térmica arrendada que el país contrata hoy; regla de la variante de potencia mínima (Art6_calibracion/variante_suficiencia.py)

Lectura para el Artículo 6

- El volumen adicional a la NDC cae a cero en la NDC financiada, en el escenario «Ambición ampliada» y en el escenario «Ambición integral»; con el sistema intacto era de 2 473 kt, 8 602 kt y 10 952 kt.

- El margen nacional de 2035 queda en −1 040 kt en la NDC financiada, 2 223 kt en el escenario «Ambición ampliada» y 3 121 kt en el escenario «Ambición integral», con los otros sectores en el condicional que la NDC compromete; en la regla prudente (los otros sectores solo cumplen su tramo incondicional), en −4 372 kt, −1 108 kt y −211 kt.

- Un margen negativo significa que el país excede su meta incondicional aun sin transferir.

- Si el país autoriza los 11 674 kt transferibles con el sistema intacto, quedan sin respaldo 8 548 kt con los otros sectores en el condicional que la NDC compromete y 11 674 kt en la regla prudente.

Origen y alcance

Alcance, límites y validación

Salida de la clase de Coca Codo y Sopladora. Cota: retira la clase completa (1.987 MW: Coca Codo 1.500 y Sopladora 487).

verificar.py: cada estado difiere de su escenario solo en sus palancas.

Año seco severo con la hidrología de 2024. Cota; desde 2026 porque la historia ya es observada.

verificar.py: cociente frente a CONA6 igual a la razón de Art6_AnoSeco.

Respaldo de emergencia. Supuesto de cierre, no es un riesgo: solo se construye la potencia que falta; la energía de respaldo se reporta con sus emisiones, la energía no suministrada equivalente y sus horas de corte equivalentes. En INCA6G las mismas palancas son las filas RE01 de correcciones_K.csv: un supuesto de cierre introducido en la corrida K16 del 13-10-2026, fuera del acuerdo original (respaldo solo en estados de riesgo); se aprobó el 13-10-2026, después de la verificación independiente, conservarlo rotulado «con cierre de fuel oil de emergencia», con el peso del respaldo al lado.

B2_Output_Art6/tablas/respaldo_por_escenario.csv

#### Qué cambia frente al sistema intacto

| Parámetro en 2035 | Sistema intacto | Con el choque | Desde |
|---|---|---|---|
| Factor de planta de la clase PPHRORAB | 0,568 | 0,000 | 2026; valor final desde 2029 |
| Factor de planta medio de las once clases hidroeléctricas | 0,539 | 0,364 | 2026; valor final desde 2029 |

Palancas en B1_Scenario_Config.xlsx (40)

| Palanca | Qué fija | Fuente |
|---|---|---|
| R-AS01 a R-AS33 (33) | Año seco severo con la hidrología de 2024. Factor de planta, piso y techo de las 11 clases hidroeléctricas por la razón de caudales de 2024 de cada clase, en todos los años desde 2026. | CENACE (2025), Informe Anual 2024, tabla 1.14, p. 73; razón por clase ponderada por la potencia nominal de la capa CENTRALES (Art6_calibracion/parametros_hidro_por_clase.csv, derivado de CENTRALES.shp de ARCONEL, uso autorizado) |
| R-CA01 a R-CA03 (3) | Salida de la clase de Coca Codo y Sopladora, sobre el año seco severo. Factor de planta y límites de actividad de PPHRORAB en cero desde 2029, aplicado sobre los valores del año seco severo. | Supuesto del análisis: salida desde 2029 por el avance de la erosión regresiva del río Coca (frente a 3,6 km de la captación en mayo de 2026); CENACE (2025), Informe Anual 2024, tabla 1.14, p. 73; razón por clase ponderada por la potencia nominal de la capa CENTRALES (Art6_calibracion/parametros_hidro_por_clase.csv, derivado de CENTRALES.shp de ARCONEL, uso autorizado) |
| RE1 | Respaldo de emergencia (supuesto de cierre, como la térmica arrendada que el país contrata hoy): tope de capacidad de PPFOI liberado desde 2026 (99999, el valor por omisión) en lugar del tope K15b (potencia existente más expansión declarada). | Decisión del 13-10-2026: respaldo de fuel oil caro solo en los estados de riesgo, supuesto de cierre como la térmica arrendada que el país contrata hoy; regla de la variante de potencia mínima (Art6_calibracion/variante_suficiencia.py) |
| RE2 | Respaldo de emergencia (supuesto de cierre, como la térmica arrendada que el país contrata hoy): CapitalCost de PPFOI 2026-2035 por 1.000: el modelo construye solo la potencia sin la cual no cubre la demanda. | Decisión del 13-10-2026: respaldo de fuel oil caro solo en los estados de riesgo, supuesto de cierre como la térmica arrendada que el país contrata hoy; regla de la variante de potencia mínima (Art6_calibracion/variante_suficiencia.py) |
| RE3 | Respaldo de emergencia (supuesto de cierre, como la térmica arrendada que el país contrata hoy): FixedCost de PPFOI 2026-2035 por 1.000. | Decisión del 13-10-2026: respaldo de fuel oil caro solo en los estados de riesgo, supuesto de cierre como la térmica arrendada que el país contrata hoy; regla de la variante de potencia mínima (Art6_calibracion/variante_suficiencia.py) |
| RE4 | Respaldo de emergencia (supuesto de cierre, como la térmica arrendada que el país contrata hoy): STOELE cerrado en 2026-2035 (tope de capacidad cero): es un atajo sin correlato físico que el modelo usa cuando falta potencia y que subestima las emisiones. | Decisión del 13-10-2026: respaldo de fuel oil caro solo en los estados de riesgo, supuesto de cierre como la térmica arrendada que el país contrata hoy; regla de la variante de potencia mínima (Art6_calibracion/variante_suficiencia.py) |

#### Resultado de la corrida

| Sistema intacto → con el choque | NDC financiada | Ambición ampliada | Ambición integral |
|---|---|---|---|
| Emisiones del sector energía, 2035 (kt) | 50 328 → 62 241 | 50 044 → 58 977 | 49 312 → 58 080 |
| Volumen adicional a la NDC, 2031-2035 (kt) | 2 473 → 0 | 8 602 → 0 | 10 952 → 0 |
| Margen nacional 2035 (kt) | 10 872 → −1 040 | 11 156 → 2 223 | 11 888 → 3 121 |
| Margen 2035, regla prudente: los demás sectores cumplen solo su incondicional (kt) | 7 540 → −4 372 | 7 825 → −1 108 | 8 557 → −211 |
| Generación hidroeléctrica 2035 (GWh) | 34 865 → 18 340 | 34 860 → 18 340 | 34 860 → 18 340 |
| Térmica desplazable 2035 (GWh) | 562 → 17 106 | 60 → 12 878 | 60 → 12 664 |

#### Sin pisos térmicos (K16 en PPFOI; Modelo CLG en PPDSL y PPNGS)

A-FOI B-FOI Riesgo de operación Se aplica sobre la NDC financiada y el escenario «Ambición ampliada»

Qué representa

Sin pisos térmicos. Decisiones del 12 y 13-10-2026: en el caso central el piso de PPFOI es K16 (mínimo observado 2015-2025, 5,0567 PJ) y los de PPDSL y PPNGS los del Modelo CLG (valor de 2022 congelado, sin fuente)

Lectura para el Artículo 6

- Frente a su versión intacta, el riesgo de operación reduce 1 175 kt más en la NDC financiada y 4 502 kt más en el escenario «Ambición ampliada» en 2031-2035.

- Adicionalidad: «No es actividad». Cambio de supuesto de operación sin proyecto asociado: no genera resultados de mitigación atribuibles.

- El análisis la reporta aparte y no la suma a la oferta de ITMO.

Origen y alcance

Alcance, límites y validación

Sin pisos térmicos. Sensibilidad; las capas se miden contra CONA6P.

verificar.py

#### Qué cambia frente al sistema intacto

| Parámetro en 2035 | Sistema intacto | Con el riesgo de operación | Desde |
|---|---|---|---|
| Piso de generación de térmica | 1 405 GWh 5,06 PJ | 0 GWh 0,00 PJ | 2026 |
| Piso de generación de térmica | 117 GWh 0,42 PJ | 0 GWh 0,00 PJ | 2026 |
| Piso de generación de térmica | 546 GWh 1,97 PJ | 0 GWh 0,00 PJ | 2026 |

Palancas en B1_Scenario_Config.xlsx (3)

| Palanca | Qué fija | Fuente |
|---|---|---|
| S1 | Sin el piso térmico desde 2026 (piso K16, mínimo observado 2015-2025): piso de PPFOI en cero; el despacho lo decide el modelo dentro de su tope K15b. | Decisiones del 12 y 13-10-2026: sensibilidad de los pisos (familia FOI); A2_Output_Params/NDCCON y K16 de correcciones_K.csv |
| S2 | Sin el piso térmico desde 2026 (piso del Modelo CLG, valor de 2022 congelado, sin fuente): piso de PPDSL en cero; el despacho lo decide el modelo dentro de su tope K15b. | Decisiones del 12 y 13-10-2026: sensibilidad de los pisos (familia FOI); A2_Output_Params/NDCCON y K16 de correcciones_K.csv |
| S3 | Sin el piso térmico desde 2026 (piso del Modelo CLG, valor de 2022 congelado, sin fuente): piso de PPNGS en cero; el despacho lo decide el modelo dentro de su tope K15b. | Decisiones del 12 y 13-10-2026: sensibilidad de los pisos (familia FOI); A2_Output_Params/NDCCON y K16 de correcciones_K.csv |

#### Resultado de la corrida

| Sistema intacto → con el riesgo de operación | NDC financiada | Ambición ampliada |
|---|---|---|
| Emisiones del sector energía, 2035 (kt) | 50 328 → 50 001 | 50 044 → 48 569 |
| Volumen adicional a la NDC, 2031-2035 (kt) | 2 473 → 3 648 | 8 602 → 13 104 |
| Margen nacional 2035 (kt) | 10 872 → 11 200 | 11 156 → 12 632 |
| Margen 2035, regla prudente: los demás sectores cumplen solo su incondicional (kt) | 7 540 → 7 868 | 7 825 → 9 300 |
| Generación hidroeléctrica 2035 (GWh) | 34 865 → 34 865 | 34 860 → 34 865 |
| Térmica desplazable 2035 (GWh) | 562 → 2 629 | 60 → 60 |

#### Importación cero desde Colombia

A-IMP0 B-IMP0 C-IMP0 Riesgo Se aplica sobre la NDC financiada, el escenario «Ambición ampliada» y el escenario «Ambición integral»

Qué representa

Los dos choques a la vez.

Sin importación desde Colombia. Resolución MME 40064, Circular CREG 343 y CENACE 2026 (S26-077)

Respaldo de emergencia. Decisión del 13-10-2026: respaldo de fuel oil caro solo en los estados de riesgo, supuesto de cierre como la térmica arrendada que el país contrata hoy; regla de la variante de potencia mínima (Art6_calibracion/variante_suficiencia.py)

Lectura para el Artículo 6

- El volumen adicional a la NDC pasa de 2 473 a 1 035 kt en la NDC financiada, de 8 602 a 8 060 kt en el escenario «Ambición ampliada» y de 10 952 a 10 328 kt en el escenario «Ambición integral».

- El margen nacional de 2035 queda en 10 601 kt en la NDC financiada, 11 156 kt en el escenario «Ambición ampliada» y 11 888 kt en el escenario «Ambición integral», con los otros sectores en el condicional que la NDC compromete; en la regla prudente (los otros sectores solo cumplen su tramo incondicional), en 7 269 kt, 7 825 kt y 8 557 kt.

- Lo que el país autorizaría con el sistema intacto, 11 674 kt, sigue cabiendo en el margen.

Origen y alcance

Alcance, límites y validación

Sin importación desde Colombia. Se trata como riesgo para la sobreventa; las capas se miden contra CONA6I.

verificar.py

Respaldo de emergencia. Supuesto de cierre, no es un riesgo: solo se construye la potencia que falta; la energía de respaldo se reporta con sus emisiones, la energía no suministrada equivalente y sus horas de corte equivalentes. En INCA6G las mismas palancas son las filas RE01 de correcciones_K.csv: un supuesto de cierre introducido en la corrida K16 del 13-10-2026, fuera del acuerdo original (respaldo solo en estados de riesgo); se aprobó el 13-10-2026, después de la verificación independiente, conservarlo rotulado «con cierre de fuel oil de emergencia», con el peso del respaldo al lado.

B2_Output_Art6/tablas/respaldo_por_escenario.csv

#### Qué cambia frente al sistema intacto

| Parámetro en 2035 | Sistema intacto | Con el choque | Desde |
|---|---|---|---|
| Techo de generación de importación | 489 GWh 1,76 PJ | 0 GWh 0,00 PJ | 2026 |
| Piso de generación de importación | 465 GWh 1,68 PJ | 0 GWh 0,00 PJ | 2026 |

Palancas en B1_Scenario_Config.xlsx (6)

| Palanca | Qué fija | Fuente |
|---|---|---|
| I1 | Importación de electricidad desde Colombia en cero desde 2026 (piso de IMPELE). | Resolución MME 40064 y Circular CREG 343; CENACE 2026 (S26-077): menos de 1 GWh por mes |
| I2 | Importación de electricidad desde Colombia en cero desde 2026 (techo de IMPELE). | Resolución MME 40064 y Circular CREG 343; CENACE 2026 (S26-077): menos de 1 GWh por mes |
| RE1 | Respaldo de emergencia (supuesto de cierre, como la térmica arrendada que el país contrata hoy): tope de capacidad de PPFOI liberado desde 2026 (99999, el valor por omisión) en lugar del tope K15b (potencia existente más expansión declarada). | Decisión del 13-10-2026: respaldo de fuel oil caro solo en los estados de riesgo, supuesto de cierre como la térmica arrendada que el país contrata hoy; regla de la variante de potencia mínima (Art6_calibracion/variante_suficiencia.py) |
| RE2 | Respaldo de emergencia (supuesto de cierre, como la térmica arrendada que el país contrata hoy): CapitalCost de PPFOI 2026-2035 por 1.000: el modelo construye solo la potencia sin la cual no cubre la demanda. | Decisión del 13-10-2026: respaldo de fuel oil caro solo en los estados de riesgo, supuesto de cierre como la térmica arrendada que el país contrata hoy; regla de la variante de potencia mínima (Art6_calibracion/variante_suficiencia.py) |
| RE3 | Respaldo de emergencia (supuesto de cierre, como la térmica arrendada que el país contrata hoy): FixedCost de PPFOI 2026-2035 por 1.000. | Decisión del 13-10-2026: respaldo de fuel oil caro solo en los estados de riesgo, supuesto de cierre como la térmica arrendada que el país contrata hoy; regla de la variante de potencia mínima (Art6_calibracion/variante_suficiencia.py) |
| RE4 | Respaldo de emergencia (supuesto de cierre, como la térmica arrendada que el país contrata hoy): STOELE cerrado en 2026-2035 (tope de capacidad cero): es un atajo sin correlato físico que el modelo usa cuando falta potencia y que subestima las emisiones. | Decisión del 13-10-2026: respaldo de fuel oil caro solo en los estados de riesgo, supuesto de cierre como la térmica arrendada que el país contrata hoy; regla de la variante de potencia mínima (Art6_calibracion/variante_suficiencia.py) |

#### Resultado de la corrida

| Sistema intacto → con el choque | NDC financiada | Ambición ampliada | Ambición integral |
|---|---|---|---|
| Emisiones del sector energía, 2035 (kt) | 50 328 → 50 600 | 50 044 → 50 044 | 49 312 → 49 312 |
| Volumen adicional a la NDC, 2031-2035 (kt) | 2 473 → 1 035 | 8 602 → 8 060 | 10 952 → 10 328 |
| Margen nacional 2035 (kt) | 10 872 → 10 601 | 11 156 → 11 156 | 11 888 → 11 888 |
| Margen 2035, regla prudente: los demás sectores cumplen solo su incondicional (kt) | 7 540 → 7 269 | 7 825 → 7 825 | 8 557 → 8 557 |
| Generación hidroeléctrica 2035 (GWh) | 34 865 → 34 865 | 34 860 → 34 625 | 34 860 → 34 835 |
| Térmica desplazable 2035 (GWh) | 562 → 1 027 | 60 → 60 | 60 → 60 |

#### Situación actual 2026, demanda transitoria (ACT)

A-ACT B-ACT C-ACT Riesgo Se aplica sobre la NDC financiada, el escenario «Ambición ampliada» y el escenario «Ambición integral»

Qué representa

Respaldo de emergencia. Decisión del 13-10-2026: respaldo de fuel oil caro solo en los estados de riesgo, supuesto de cierre como la térmica arrendada que el país contrata hoy; regla de la variante de potencia mínima (Art6_calibracion/variante_suficiencia.py)

Lectura para el Artículo 6

- El volumen adicional a la NDC pasa de 2 473 a 776 kt en la NDC financiada, de 8 602 a 5 334 kt en el escenario «Ambición ampliada» y de 10 952 a 6 663 kt en el escenario «Ambición integral».

- El margen nacional de 2035 queda en 4 852 kt en la NDC financiada, 8 109 kt en el escenario «Ambición ampliada» y 8 999 kt en el escenario «Ambición integral», con los otros sectores en el condicional que la NDC compromete; en la regla prudente (los otros sectores solo cumplen su tramo incondicional), en 1 520 kt, 4 777 kt y 5 667 kt.

- Si el país autoriza los 11 674 kt transferibles con el sistema intacto, quedan sin respaldo 0 kt con los otros sectores en el condicional que la NDC compromete y 1 458 kt en la regla prudente.

Origen y alcance

Alcance, límites y validación

Respaldo de emergencia. Supuesto de cierre, no es un riesgo: solo se construye la potencia que falta; la energía de respaldo se reporta con sus emisiones, la energía no suministrada equivalente y sus horas de corte equivalentes. En INCA6G las mismas palancas son las filas RE01 de correcciones_K.csv: un supuesto de cierre introducido en la corrida K16 del 13-10-2026, fuera del acuerdo original (respaldo solo en estados de riesgo); se aprobó el 13-10-2026, después de la verificación independiente, conservarlo rotulado «con cierre de fuel oil de emergencia», con el peso del respaldo al lado.

B2_Output_Art6/tablas/respaldo_por_escenario.csv

#### Qué cambia frente al sistema intacto

| Parámetro en 2035 | Sistema intacto | Con el choque | Desde |
|---|---|---|---|
| Techo de generación de importación | 489 GWh 1,76 PJ | 0 GWh 0,00 PJ | 2026; valor final desde 2027 |
| Piso de generación de importación | 465 GWh 1,68 PJ | 0 GWh 0,00 PJ | 2026; valor final desde 2027 |
| Factor de planta de la clase PPHRORAB | 0,568 | 0,490 | 2026, en rampa hasta 2035 |
| Factor de planta medio de las once clases hidroeléctricas | 0,539 | 0,409 | 2026, en rampa hasta 2035 |

Palancas en B1_Scenario_Config.xlsx (45)

| Palanca | Qué fija | Fuente |
|---|---|---|
| R-AT01 a R-AT33 (33) | ACTH. Situación actual: valor de CONA6 por 1.1123 en 2026 (hidrología observada de 2026 de la clase; Otras Hidro (0.9882)) y por la razón de caudales de 2024 (0.8410) en 2029, 2032 y 2035, un año seco cada tres; años normales en los demás. | CENACE: Informes Ejecutivos de Gestión de agosto y diciembre de 2025 y agosto de 2026 (secciones 1, 2 y 4), indicadores.xlsx (hoja datos), Informe Anual 2025 Parte 1 (figura 1.4 y p. 36) e Información Operativa al 10-10-2026 (SCADA preliminar); XM, Exportaciones kWh 2026. Leídos por Art6_calibracion/situacion_act_2026.py en act_2026_observado.csv; razones por clase en parametros_hidro_por_clase.csv; CENACE (2025), Informe Anual 2024, tabla 1.14, p. 73; razón por clase ponderada por la potencia nominal de la capa CENTRALES (Art6_calibracion/parametros_hidro_por_clase.csv, derivado de CENTRALES.shp de ARCONEL, uso autorizado) |
| I3 | Importación desde Colombia de la situación actual (piso de IMPELE): en 2026, la importada antes del 07-09-2026 (267.05 GWh = 0.9614 PJ: CENACE enero a agosto y XM 1 a 6 de septiembre); cero desde 2027, supuesto de estrés declarado. | CENACE: Informes Ejecutivos de Gestión de agosto y diciembre de 2025 y agosto de 2026 (secciones 1, 2 y 4), indicadores.xlsx (hoja datos), Informe Anual 2025 Parte 1 (figura 1.4 y p. 36) e Información Operativa al 10-10-2026 (SCADA preliminar); XM, Exportaciones kWh 2026. Leídos por Art6_calibracion/situacion_act_2026.py en act_2026_observado.csv; razones por clase en parametros_hidro_por_clase.csv; Resolución MME 40064 y Circular CREG 343 |
| I4 | Importación desde Colombia de la situación actual (techo de IMPELE): en 2026, la importada antes del 07-09-2026 (267.05 GWh = 0.9614 PJ: CENACE enero a agosto y XM 1 a 6 de septiembre); cero desde 2027, supuesto de estrés declarado. | CENACE: Informes Ejecutivos de Gestión de agosto y diciembre de 2025 y agosto de 2026 (secciones 1, 2 y 4), indicadores.xlsx (hoja datos), Informe Anual 2025 Parte 1 (figura 1.4 y p. 36) e Información Operativa al 10-10-2026 (SCADA preliminar); XM, Exportaciones kWh 2026. Leídos por Art6_calibracion/situacion_act_2026.py en act_2026_observado.csv; razones por clase en parametros_hidro_por_clase.csv; Resolución MME 40064 y Circular CREG 343 |
| D-A1 | Demanda eléctrica observada de 2026 (E5COMELE): E5COMELE por 1.115477 en 2026, para que la demanda eléctrica final de 2026 sea la de CONA6 en 2025 por el crecimiento observado de enero a agosto (1.1272); el nivel de 2026 vuelve a la trayectoria del Modelo CLG desde 2027 (choque transitorio). Supuesto declarado. | CENACE: Informes Ejecutivos de Gestión de agosto y diciembre de 2025 y agosto de 2026 (secciones 1, 2 y 4), indicadores.xlsx (hoja datos), Informe Anual 2025 Parte 1 (figura 1.4 y p. 36) e Información Operativa al 10-10-2026 (SCADA preliminar); XM, Exportaciones kWh 2026. Leídos por Art6_calibracion/situacion_act_2026.py en act_2026_observado.csv; razones por clase en parametros_hidro_por_clase.csv |
| D-A2 | Demanda eléctrica observada de 2026 (E5INDELE): E5INDELE por 1.115477 en 2026, para que la demanda eléctrica final de 2026 sea la de CONA6 en 2025 por el crecimiento observado de enero a agosto (1.1272); el nivel de 2026 vuelve a la trayectoria del Modelo CLG desde 2027 (choque transitorio). Supuesto declarado. | CENACE: Informes Ejecutivos de Gestión de agosto y diciembre de 2025 y agosto de 2026 (secciones 1, 2 y 4), indicadores.xlsx (hoja datos), Informe Anual 2025 Parte 1 (figura 1.4 y p. 36) e Información Operativa al 10-10-2026 (SCADA preliminar); XM, Exportaciones kWh 2026. Leídos por Art6_calibracion/situacion_act_2026.py en act_2026_observado.csv; razones por clase en parametros_hidro_por_clase.csv |
| D-A3 | Demanda eléctrica observada de 2026 (E5RESELE): E5RESELE por 1.115477 en 2026, para que la demanda eléctrica final de 2026 sea la de CONA6 en 2025 por el crecimiento observado de enero a agosto (1.1272); el nivel de 2026 vuelve a la trayectoria del Modelo CLG desde 2027 (choque transitorio). Supuesto declarado. | CENACE: Informes Ejecutivos de Gestión de agosto y diciembre de 2025 y agosto de 2026 (secciones 1, 2 y 4), indicadores.xlsx (hoja datos), Informe Anual 2025 Parte 1 (figura 1.4 y p. 36) e Información Operativa al 10-10-2026 (SCADA preliminar); XM, Exportaciones kWh 2026. Leídos por Art6_calibracion/situacion_act_2026.py en act_2026_observado.csv; razones por clase en parametros_hidro_por_clase.csv |
| D-A4 | Demanda eléctrica observada de 2026 (E5TROELE): E5TROELE por 1.115477 en 2026, para que la demanda eléctrica final de 2026 sea la de CONA6 en 2025 por el crecimiento observado de enero a agosto (1.1272); el nivel de 2026 vuelve a la trayectoria del Modelo CLG desde 2027 (choque transitorio). Supuesto declarado. | CENACE: Informes Ejecutivos de Gestión de agosto y diciembre de 2025 y agosto de 2026 (secciones 1, 2 y 4), indicadores.xlsx (hoja datos), Informe Anual 2025 Parte 1 (figura 1.4 y p. 36) e Información Operativa al 10-10-2026 (SCADA preliminar); XM, Exportaciones kWh 2026. Leídos por Art6_calibracion/situacion_act_2026.py en act_2026_observado.csv; razones por clase en parametros_hidro_por_clase.csv |
| D-A5 | Demanda eléctrica observada de 2026 (E5ALLTRNELE): E5ALLTRNELE por 1.115477 en 2026, para que la demanda eléctrica final de 2026 sea la de CONA6 en 2025 por el crecimiento observado de enero a agosto (1.1272); el nivel de 2026 vuelve a la trayectoria del Modelo CLG desde 2027 (choque transitorio). Supuesto declarado. | CENACE: Informes Ejecutivos de Gestión de agosto y diciembre de 2025 y agosto de 2026 (secciones 1, 2 y 4), indicadores.xlsx (hoja datos), Informe Anual 2025 Parte 1 (figura 1.4 y p. 36) e Información Operativa al 10-10-2026 (SCADA preliminar); XM, Exportaciones kWh 2026. Leídos por Art6_calibracion/situacion_act_2026.py en act_2026_observado.csv; razones por clase en parametros_hidro_por_clase.csv |
| D-A6 | Demanda eléctrica observada de 2026 (E5CONELE): E5CONELE por 1.115477 en 2026, para que la demanda eléctrica final de 2026 sea la de CONA6 en 2025 por el crecimiento observado de enero a agosto (1.1272); el nivel de 2026 vuelve a la trayectoria del Modelo CLG desde 2027 (choque transitorio). Supuesto declarado. | CENACE: Informes Ejecutivos de Gestión de agosto y diciembre de 2025 y agosto de 2026 (secciones 1, 2 y 4), indicadores.xlsx (hoja datos), Informe Anual 2025 Parte 1 (figura 1.4 y p. 36) e Información Operativa al 10-10-2026 (SCADA preliminar); XM, Exportaciones kWh 2026. Leídos por Art6_calibracion/situacion_act_2026.py en act_2026_observado.csv; razones por clase en parametros_hidro_por_clase.csv |
| RE1 | Respaldo de emergencia (supuesto de cierre, como la térmica arrendada que el país contrata hoy): tope de capacidad de PPFOI liberado desde 2026 (99999, el valor por omisión) en lugar del tope K15b (potencia existente más expansión declarada). | Decisión del 13-10-2026: respaldo de fuel oil caro solo en los estados de riesgo, supuesto de cierre como la térmica arrendada que el país contrata hoy; regla de la variante de potencia mínima (Art6_calibracion/variante_suficiencia.py) |
| RE2 | Respaldo de emergencia (supuesto de cierre, como la térmica arrendada que el país contrata hoy): CapitalCost de PPFOI 2026-2035 por 1.000: el modelo construye solo la potencia sin la cual no cubre la demanda. | Decisión del 13-10-2026: respaldo de fuel oil caro solo en los estados de riesgo, supuesto de cierre como la térmica arrendada que el país contrata hoy; regla de la variante de potencia mínima (Art6_calibracion/variante_suficiencia.py) |
| RE3 | Respaldo de emergencia (supuesto de cierre, como la térmica arrendada que el país contrata hoy): FixedCost de PPFOI 2026-2035 por 1.000. | Decisión del 13-10-2026: respaldo de fuel oil caro solo en los estados de riesgo, supuesto de cierre como la térmica arrendada que el país contrata hoy; regla de la variante de potencia mínima (Art6_calibracion/variante_suficiencia.py) |
| RE4 | Respaldo de emergencia (supuesto de cierre, como la térmica arrendada que el país contrata hoy): STOELE cerrado en 2026-2035 (tope de capacidad cero): es un atajo sin correlato físico que el modelo usa cuando falta potencia y que subestima las emisiones. | Decisión del 13-10-2026: respaldo de fuel oil caro solo en los estados de riesgo, supuesto de cierre como la térmica arrendada que el país contrata hoy; regla de la variante de potencia mínima (Art6_calibracion/variante_suficiencia.py) |

#### Resultado de la corrida

| Sistema intacto → con el choque | NDC financiada | Ambición ampliada | Ambición integral |
|---|---|---|---|
| Emisiones del sector energía, 2035 (kt) | 50 328 → 56 349 | 50 044 → 53 092 | 49 312 → 52 202 |
| Volumen adicional a la NDC, 2031-2035 (kt) | 2 473 → 776 | 8 602 → 5 334 | 10 952 → 6 663 |
| Margen nacional 2035 (kt) | 10 872 → 4 852 | 11 156 → 8 109 | 11 888 → 8 999 |
| Margen 2035, regla prudente: los demás sectores cumplen solo su incondicional (kt) | 7 540 → 1 520 | 7 825 → 4 777 | 8 557 → 5 667 |
| Generación hidroeléctrica 2035 (GWh) | 34 865 → 26 449 | 34 860 → 26 449 | 34 860 → 26 449 |
| Térmica desplazable 2035 (GWh) | 562 → 9 462 | 60 → 5 234 | 60 → 5 020 |

#### Situación actual 2026, demanda persistente (ACT-DEM)

A-ACTDEM B-ACTDEM C-ACTDEM Riesgo Se aplica sobre la NDC financiada, el escenario «Ambición ampliada» y el escenario «Ambición integral»

Qué representa

Respaldo de emergencia. Decisión del 13-10-2026: respaldo de fuel oil caro solo en los estados de riesgo, supuesto de cierre como la térmica arrendada que el país contrata hoy; regla de la variante de potencia mínima (Art6_calibracion/variante_suficiencia.py)

Lectura para el Artículo 6

- El volumen adicional a la NDC cae a cero en la NDC financiada, en el escenario «Ambición ampliada» y en el escenario «Ambición integral»; con el sistema intacto era de 2 473 kt, 8 602 kt y 10 952 kt.

- El margen nacional de 2035 queda en 960 kt en la NDC financiada, 4 076 kt en el escenario «Ambición ampliada» y 4 908 kt en el escenario «Ambición integral», con los otros sectores en el condicional que la NDC compromete; en la regla prudente (los otros sectores solo cumplen su tramo incondicional), en −2 372 kt, 744 kt y 1 576 kt.

- Un margen negativo significa que el país excede su meta incondicional aun sin transferir.

- Si el país autoriza los 11 674 kt transferibles con el sistema intacto, quedan sin respaldo 1 442 kt con los otros sectores en el condicional que la NDC compromete y 4 950 kt en la regla prudente.

Origen y alcance

Alcance, límites y validación

Respaldo de emergencia. Supuesto de cierre, no es un riesgo: solo se construye la potencia que falta; la energía de respaldo se reporta con sus emisiones, la energía no suministrada equivalente y sus horas de corte equivalentes. En INCA6G las mismas palancas son las filas RE01 de correcciones_K.csv: un supuesto de cierre introducido en la corrida K16 del 13-10-2026, fuera del acuerdo original (respaldo solo en estados de riesgo); se aprobó el 13-10-2026, después de la verificación independiente, conservarlo rotulado «con cierre de fuel oil de emergencia», con el peso del respaldo al lado.

B2_Output_Art6/tablas/respaldo_por_escenario.csv

#### Qué cambia frente al sistema intacto

| Parámetro en 2035 | Sistema intacto | Con el choque | Desde |
|---|---|---|---|
| Techo de generación de importación | 489 GWh 1,76 PJ | 0 GWh 0,00 PJ | 2026; valor final desde 2027 |
| Piso de generación de importación | 465 GWh 1,68 PJ | 0 GWh 0,00 PJ | 2026; valor final desde 2027 |
| Factor de planta de la clase PPHRORAB | 0,568 | 0,490 | 2026, en rampa hasta 2035 |
| Factor de planta medio de las once clases hidroeléctricas | 0,539 | 0,409 | 2026, en rampa hasta 2035 |

Palancas en B1_Scenario_Config.xlsx (45)

| Palanca | Qué fija | Fuente |
|---|---|---|
| R-AT01 a R-AT33 (33) | ACTH. Situación actual: valor de CONA6 por 1.1123 en 2026 (hidrología observada de 2026 de la clase; Otras Hidro (0.9882)) y por la razón de caudales de 2024 (0.8410) en 2029, 2032 y 2035, un año seco cada tres; años normales en los demás. | CENACE: Informes Ejecutivos de Gestión de agosto y diciembre de 2025 y agosto de 2026 (secciones 1, 2 y 4), indicadores.xlsx (hoja datos), Informe Anual 2025 Parte 1 (figura 1.4 y p. 36) e Información Operativa al 10-10-2026 (SCADA preliminar); XM, Exportaciones kWh 2026. Leídos por Art6_calibracion/situacion_act_2026.py en act_2026_observado.csv; razones por clase en parametros_hidro_por_clase.csv; CENACE (2025), Informe Anual 2024, tabla 1.14, p. 73; razón por clase ponderada por la potencia nominal de la capa CENTRALES (Art6_calibracion/parametros_hidro_por_clase.csv, derivado de CENTRALES.shp de ARCONEL, uso autorizado) |
| I3 | Importación desde Colombia de la situación actual (piso de IMPELE): en 2026, la importada antes del 07-09-2026 (267.05 GWh = 0.9614 PJ: CENACE enero a agosto y XM 1 a 6 de septiembre); cero desde 2027, supuesto de estrés declarado. | CENACE: Informes Ejecutivos de Gestión de agosto y diciembre de 2025 y agosto de 2026 (secciones 1, 2 y 4), indicadores.xlsx (hoja datos), Informe Anual 2025 Parte 1 (figura 1.4 y p. 36) e Información Operativa al 10-10-2026 (SCADA preliminar); XM, Exportaciones kWh 2026. Leídos por Art6_calibracion/situacion_act_2026.py en act_2026_observado.csv; razones por clase en parametros_hidro_por_clase.csv; Resolución MME 40064 y Circular CREG 343 |
| I4 | Importación desde Colombia de la situación actual (techo de IMPELE): en 2026, la importada antes del 07-09-2026 (267.05 GWh = 0.9614 PJ: CENACE enero a agosto y XM 1 a 6 de septiembre); cero desde 2027, supuesto de estrés declarado. | CENACE: Informes Ejecutivos de Gestión de agosto y diciembre de 2025 y agosto de 2026 (secciones 1, 2 y 4), indicadores.xlsx (hoja datos), Informe Anual 2025 Parte 1 (figura 1.4 y p. 36) e Información Operativa al 10-10-2026 (SCADA preliminar); XM, Exportaciones kWh 2026. Leídos por Art6_calibracion/situacion_act_2026.py en act_2026_observado.csv; razones por clase en parametros_hidro_por_clase.csv; Resolución MME 40064 y Circular CREG 343 |
| D-P1 | Demanda eléctrica observada de 2026 (E5COMELE): E5COMELE por 1.115477 en 2026-2035, para que la demanda eléctrica final de 2026 sea la de CONA6 en 2025 por el crecimiento observado de enero a agosto (1.1272); el nivel de 2026 persiste y desde ahí crece con las tasas del Modelo CLG. Supuesto declarado. | CENACE: Informes Ejecutivos de Gestión de agosto y diciembre de 2025 y agosto de 2026 (secciones 1, 2 y 4), indicadores.xlsx (hoja datos), Informe Anual 2025 Parte 1 (figura 1.4 y p. 36) e Información Operativa al 10-10-2026 (SCADA preliminar); XM, Exportaciones kWh 2026. Leídos por Art6_calibracion/situacion_act_2026.py en act_2026_observado.csv; razones por clase en parametros_hidro_por_clase.csv |
| D-P2 | Demanda eléctrica observada de 2026 (E5INDELE): E5INDELE por 1.115477 en 2026-2035, para que la demanda eléctrica final de 2026 sea la de CONA6 en 2025 por el crecimiento observado de enero a agosto (1.1272); el nivel de 2026 persiste y desde ahí crece con las tasas del Modelo CLG. Supuesto declarado. | CENACE: Informes Ejecutivos de Gestión de agosto y diciembre de 2025 y agosto de 2026 (secciones 1, 2 y 4), indicadores.xlsx (hoja datos), Informe Anual 2025 Parte 1 (figura 1.4 y p. 36) e Información Operativa al 10-10-2026 (SCADA preliminar); XM, Exportaciones kWh 2026. Leídos por Art6_calibracion/situacion_act_2026.py en act_2026_observado.csv; razones por clase en parametros_hidro_por_clase.csv |
| D-P3 | Demanda eléctrica observada de 2026 (E5RESELE): E5RESELE por 1.115477 en 2026-2035, para que la demanda eléctrica final de 2026 sea la de CONA6 en 2025 por el crecimiento observado de enero a agosto (1.1272); el nivel de 2026 persiste y desde ahí crece con las tasas del Modelo CLG. Supuesto declarado. | CENACE: Informes Ejecutivos de Gestión de agosto y diciembre de 2025 y agosto de 2026 (secciones 1, 2 y 4), indicadores.xlsx (hoja datos), Informe Anual 2025 Parte 1 (figura 1.4 y p. 36) e Información Operativa al 10-10-2026 (SCADA preliminar); XM, Exportaciones kWh 2026. Leídos por Art6_calibracion/situacion_act_2026.py en act_2026_observado.csv; razones por clase en parametros_hidro_por_clase.csv |
| D-P4 | Demanda eléctrica observada de 2026 (E5TROELE): E5TROELE por 1.115477 en 2026-2035, para que la demanda eléctrica final de 2026 sea la de CONA6 en 2025 por el crecimiento observado de enero a agosto (1.1272); el nivel de 2026 persiste y desde ahí crece con las tasas del Modelo CLG. Supuesto declarado. | CENACE: Informes Ejecutivos de Gestión de agosto y diciembre de 2025 y agosto de 2026 (secciones 1, 2 y 4), indicadores.xlsx (hoja datos), Informe Anual 2025 Parte 1 (figura 1.4 y p. 36) e Información Operativa al 10-10-2026 (SCADA preliminar); XM, Exportaciones kWh 2026. Leídos por Art6_calibracion/situacion_act_2026.py en act_2026_observado.csv; razones por clase en parametros_hidro_por_clase.csv |
| D-P5 | Demanda eléctrica observada de 2026 (E5ALLTRNELE): E5ALLTRNELE por 1.115477 en 2026-2035, para que la demanda eléctrica final de 2026 sea la de CONA6 en 2025 por el crecimiento observado de enero a agosto (1.1272); el nivel de 2026 persiste y desde ahí crece con las tasas del Modelo CLG. Supuesto declarado. | CENACE: Informes Ejecutivos de Gestión de agosto y diciembre de 2025 y agosto de 2026 (secciones 1, 2 y 4), indicadores.xlsx (hoja datos), Informe Anual 2025 Parte 1 (figura 1.4 y p. 36) e Información Operativa al 10-10-2026 (SCADA preliminar); XM, Exportaciones kWh 2026. Leídos por Art6_calibracion/situacion_act_2026.py en act_2026_observado.csv; razones por clase en parametros_hidro_por_clase.csv |
| D-P6 | Demanda eléctrica observada de 2026 (E5CONELE): E5CONELE por 1.115477 en 2026-2035, para que la demanda eléctrica final de 2026 sea la de CONA6 en 2025 por el crecimiento observado de enero a agosto (1.1272); el nivel de 2026 persiste y desde ahí crece con las tasas del Modelo CLG. Supuesto declarado. | CENACE: Informes Ejecutivos de Gestión de agosto y diciembre de 2025 y agosto de 2026 (secciones 1, 2 y 4), indicadores.xlsx (hoja datos), Informe Anual 2025 Parte 1 (figura 1.4 y p. 36) e Información Operativa al 10-10-2026 (SCADA preliminar); XM, Exportaciones kWh 2026. Leídos por Art6_calibracion/situacion_act_2026.py en act_2026_observado.csv; razones por clase en parametros_hidro_por_clase.csv |
| RE1 | Respaldo de emergencia (supuesto de cierre, como la térmica arrendada que el país contrata hoy): tope de capacidad de PPFOI liberado desde 2026 (99999, el valor por omisión) en lugar del tope K15b (potencia existente más expansión declarada). | Decisión del 13-10-2026: respaldo de fuel oil caro solo en los estados de riesgo, supuesto de cierre como la térmica arrendada que el país contrata hoy; regla de la variante de potencia mínima (Art6_calibracion/variante_suficiencia.py) |
| RE2 | Respaldo de emergencia (supuesto de cierre, como la térmica arrendada que el país contrata hoy): CapitalCost de PPFOI 2026-2035 por 1.000: el modelo construye solo la potencia sin la cual no cubre la demanda. | Decisión del 13-10-2026: respaldo de fuel oil caro solo en los estados de riesgo, supuesto de cierre como la térmica arrendada que el país contrata hoy; regla de la variante de potencia mínima (Art6_calibracion/variante_suficiencia.py) |
| RE3 | Respaldo de emergencia (supuesto de cierre, como la térmica arrendada que el país contrata hoy): FixedCost de PPFOI 2026-2035 por 1.000. | Decisión del 13-10-2026: respaldo de fuel oil caro solo en los estados de riesgo, supuesto de cierre como la térmica arrendada que el país contrata hoy; regla de la variante de potencia mínima (Art6_calibracion/variante_suficiencia.py) |
| RE4 | Respaldo de emergencia (supuesto de cierre, como la térmica arrendada que el país contrata hoy): STOELE cerrado en 2026-2035 (tope de capacidad cero): es un atajo sin correlato físico que el modelo usa cuando falta potencia y que subestima las emisiones. | Decisión del 13-10-2026: respaldo de fuel oil caro solo en los estados de riesgo, supuesto de cierre como la térmica arrendada que el país contrata hoy; regla de la variante de potencia mínima (Art6_calibracion/variante_suficiencia.py) |

#### Resultado de la corrida

| Sistema intacto → con el choque | NDC financiada | Ambición ampliada | Ambición integral |
|---|---|---|---|
| Emisiones del sector energía, 2035 (kt) | 50 328 → 60 241 | 50 044 → 57 125 | 49 312 → 56 293 |
| Volumen adicional a la NDC, 2031-2035 (kt) | 2 473 → 0 | 8 602 → 0 | 10 952 → 0 |
| Margen nacional 2035 (kt) | 10 872 → 960 | 11 156 → 4 076 | 11 888 → 4 908 |
| Margen 2035, regla prudente: los demás sectores cumplen solo su incondicional (kt) | 7 540 → −2 372 | 7 825 → 744 | 8 557 → 1 576 |
| Generación hidroeléctrica 2035 (GWh) | 34 865 → 26 640 | 34 860 → 26 449 | 34 860 → 26 449 |
| Térmica desplazable 2035 (GWh) | 562 → 14 496 | 60 → 10 459 | 60 → 10 330 |

#### Sin la expansión a gas declarada (sobre CONA6G)

A-GAS B-GAS C-GAS Riesgo de operación Se aplica sobre la NDC financiada, el escenario «Ambición ampliada» y el escenario «Ambición integral»

Qué representa

Variante sobre el Escenario A: las palancas del escenario sobre CONA6G, sin la expansión a gas declarada (PPNGS en su piso CLG, G01); sus capas se miden contra CONA6G.

Lectura para el Artículo 6

- Frente a su versión intacta, el riesgo de operación reduce −2 513 kt más en la NDC financiada, −408 kt más en el escenario «Ambición ampliada» y −609 kt más en el escenario «Ambición integral» en 2031-2035.

- El análisis la reporta aparte y no la suma a la oferta de ITMO.

#### Qué cambia frente al sistema intacto

Sin diferencias en los parámetros que mueven las palancas.

#### Resultado de la corrida

| Sistema intacto → con el riesgo de operación | NDC financiada | Ambición ampliada | Ambición integral |
|---|---|---|---|
| Emisiones del sector energía, 2035 (kt) | 50 328 → 50 396 | 50 044 → 50 044 | 49 312 → 49 312 |
| Volumen adicional a la NDC, 2031-2035 (kt) | 2 473 → 260 | 8 602 → 8 194 | 10 952 → 10 344 |
| Margen nacional 2035 (kt) | 10 872 → 10 805 | 11 156 → 11 156 | 11 888 → 11 888 |
| Margen 2035, regla prudente: los demás sectores cumplen solo su incondicional (kt) | 7 540 → 7 473 | 7 825 → 7 825 | 8 557 → 8 557 |

#### Sin sus proyectos (contrafactual)

A-SIN Contrafactual Se aplica sobre la NDC financiada

Qué representa

Variante sobre el Escenario A: el mismo sistema del A sin la eólica, la solar y la geotermia nuevas del condicional; la diferencia con el A es el aporte atribuible por retiro.

Lectura para el Artículo 6

- El volumen adicional a la NDC cae a cero en la NDC financiada; con el sistema intacto era de 2 473 kt.

- El margen nacional de 2035 queda en 9 735 kt en la NDC financiada, con los otros sectores en el condicional que la NDC compromete; en la regla prudente (los otros sectores solo cumplen su tramo incondicional), en 6 403 kt.

#### Qué cambia frente al sistema intacto

| Parámetro en 2035 | Sistema intacto | Con el choque | Desde |
|---|---|---|---|
| Techo de generación eólica | 914 GWh 3,29 PJ | 204 GWh 0,74 PJ | 2026 |
| Techo de generación solar | 1 021 GWh 3,68 PJ | 34 GWh 0,12 PJ | 2026 |
| Piso de generación solar | 971 GWh 3,50 PJ | 33 GWh 0,12 PJ | 2027 |
| Techo de generación geotérmica | 353 GWh 1,27 PJ | 0 GWh 0,00 PJ | 2029 |
| Piso de generación geotérmica | 353 GWh 1,27 PJ | 0 GWh 0,00 PJ | 2029 |

Palancas en B1_Scenario_Config.xlsx (8)

| Palanca | Qué fija | Fuente |
|---|---|---|
| SIN1 | Contrafactual: techo eólico igual al potencial de la capacidad existente de CONA6 (66.35 MW), sin la capacidad nueva del condicional. | regla de A1 sin inversión |
| SIN2 | Contrafactual: techo solar igual al potencial de la capacidad existente de CONA6 sin el condicional (24.14 MW). | regla de A3 sin inversión |
| SIN4 | Contrafactual: sin la inversión eólica del condicional (230,4 MW de 2026-2030 a cero). | retiro de la inversión del condicional |
| SIN5 | Contrafactual: sin la inversión solar del condicional (700 MW de 2025-2034 a cero). | retiro de la inversión del condicional |
| SIN6 | Contrafactual: piso solar igual a 0,98 por la generación de la capacidad existente (regla de K12c sin el incremento del condicional). | regla de K12c |
| SIN7 | Contrafactual: sin techo de generación geotérmica (cero). | retiro de la geotermia del condicional |
| SIN8 | Contrafactual: sin capacidad geotérmica (tope cero). | retiro de la geotermia del condicional |
| SIN9 | Contrafactual: sin inversión geotérmica (cero). | retiro de la geotermia del condicional |

#### Resultado de la corrida

| Sistema intacto → con el choque | NDC financiada |
|---|---|
| Emisiones del sector energía, 2035 (kt) | 50 328 → 51 466 |
| Volumen adicional a la NDC, 2031-2035 (kt) | 2 473 → 0 |
| Margen nacional 2035 (kt) | 10 872 → 9 735 |
| Margen 2035, regla prudente: los demás sectores cumplen solo su incondicional (kt) | 7 540 → 6 403 |
| Térmica desplazable 2035 (GWh) | 562 → 2 611 |

#### Supuestos comunes

- Marco de análisis: 2026-2035, vigencia de la Segunda NDC.

- Ventana de transacciones: 2031-2035.

- Emisiones del sector energía: suma de demanda final (CO2e_DE), generación eléctrica (CO2e_PP), fugitivas (CO2e_FUG) y refinación (CO2e_REF), del Output.csv de cada escenario.

- Resolución temporal: un solo bloque horario por año (Season = All).

- Margen nacional: Trayectoria nacional de un escenario: la senda de la meta condicional publicada (tendencial menos 8 800 kt del 7 % incondicional y 10 600 kt del 8 % condicional adicional, ambos sobre el tendencial, con senda lineal desde 2026) más la diferencia del sector energía frente a la referencia condicional: CONA6 en la proyección del Modelo CLG, que usan las gráficas, y NDCCON en la proyección corregida. Supone que los otros sectores cumplen el condicional que la NDC compromete. Valor alternativo: «condicional», la serie modelada de la agregación nacional del Modelo CLG, que reduce 22 977 kt en 2035 (3 577 kt más que lo comprometido).

- Regla prudente: los demás sectores cumplen solo el incondicional que la NDC compromete; se parte de la senda de la meta incondicional publicada (tendencial menos 8 800 kt en 2035) más la diferencia del sector energía frente a la referencia incondicional: INCA6 en la proyección del Modelo CLG y NDCINC en la proyección corregida. Valor alternativo: «incondicional», la serie modelada.

- Térmica desplazable: generación térmica por encima de su piso de despacho obligatorio (pisos del Modelo CLG), calculada con la actividad del Output.csv y el piso del _Input.csv de cada escenario; es lo único que una renovable nueva puede sustituir.

- Años subestimados: cuando el modelo pasa energía por STOELE con la térmica de la red en su tope (K15b), falta potencia y las emisiones de ese año quedan subestimadas; la ficha «Escenarios sin solución y años subestimados» los lista con la variante diagnóstica de potencia mínima.

- Ejercicio exploratorio: el tratamiento del ajuste correspondiente es conceptual y no constituye una metodología oficial del Artículo 6.

Fuente: salidas de B1 de cada escenario (Energy/Executables/<ESC>_0/<ESC>_0_Output.csv e _Input.csv) del Modelo Climate Lead Group en la rama art6-escenarios de ECU_NDC; B1_Scenario_Config.xlsx (hojas Art6_Escenarios, Art6_Palancas, Art6_Riesgos, Art6_Adicionalidad y Art6_Headroom).

## Parámetros de entrada por escenario

Cada escenario de Artículo 6 se construye sobre su escenario base y modifica solo los parámetros de sus palancas; cada riesgo modifica, sobre su escalón, solo los parámetros del choque. La matriz reúne esos valores para 2035 y el color indica si vienen de la base, de una palanca o de un choque.

| Escenario | Eólica techo | Solar techo | Solar piso | Geotermia techo | Geotermia piso | Biomasa y biogás techo | Térmica piso | Térmica piso | Térmica piso | Importación techo | Importación piso | Factor de planta PPBIM | Factor de planta PPHRORAB | Factor de planta PPWNDON | Factor de planta 11 clases hidro | Qué cambia |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Referencia NDC |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| NDCINC | 0,22 | 0,03 | 0,02 | sin techo | 0,00 | 0,00 | 9,38 | 0,42 | 1,97 | 1,76 | 1,68 | 0,459 | 0,568 | 0,172 | 0,539 | Escenario del Modelo Climate Lead Group sin cambios, sin palancas de Artículo 6. |
| NDCCON | 1,00 | 3,57 | 3,40 | 1,27 | 0,00 | 0,00 | 9,00 | 0,42 | 1,97 | 1,76 | 1,68 | 0,459 | 0,568 | 0,172 | 0,539 | Escenario del Modelo Climate Lead Group sin cambios, sin palancas de Artículo 6. |
| INCA6 | 0,75 | 0,12 | 0,12 | sin techo | 0,00 | 0,00 | 5,06 | 0,42 | 1,97 | 1,76 | 1,68 | 0,459 | 0,568 | 0,370 | 0,539 | NDCINC del Modelo CLG con las correcciones K01-K15 (base congelada), sin palancas de Artículo 6. |
| CONA6 | 1,53 | 3,67 | 3,50 | 1,27 | 0,00 | 0,00 | 5,06 | 0,42 | 1,97 | 1,76 | 1,68 | 0,459 | 0,568 | 0,370 | 0,539 | NDCCON del Modelo CLG con las correcciones K01-K15 (base congelada), sin palancas de Artículo 6. |
| CONA6G | 1,53 | 3,67 | 3,50 | 1,27 | 0,00 | 0,00 | 5,06 | 0,42 | 1,97 | 1,76 | 1,68 | 0,459 | 0,568 | 0,370 | 0,539 | Escenario del Modelo Climate Lead Group sin cambios, sin palancas de Artículo 6. |
| NDC financiada y sus pruebas |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| A | 3,29 | 3,68 | 3,50 | 1,27 | 1,27 | 0,00 | 5,06 | 0,42 | 1,97 | 1,76 | 1,68 | 0,459 | 0,568 | 0,370 | 0,539 | Frente a la NDC condicional corregida: techo de generación eólica a 914 GWh desde 2026; techo de generación solar a 1 021 GWh desde 2026; techo de generación geotérmica a 353 GWh desde 2029; piso de generación geotérmica a 353 GWh desde 2029. |
| A-CCOFF | 3,29 | 3,68 | 3,50 | 1,27 | 1,27 | 0,00 | 5,06 | 0,42 | 1,97 | 1,76 | 1,68 | 0,459 | 0,000 | 0,370 | 0,487 | Frente a la NDC financiada: factor de planta de la clase PPHRORAB a 0,000 desde 2029; factor de planta medio de las once clases hidroeléctricas a 0,487 desde 2029. |
| A-CCSOLO | 3,29 | 3,68 | 3,50 | 1,27 | 1,27 | 0,00 | 5,06 | 0,42 | 1,97 | 1,76 | 1,68 | 0,459 | 0,155 | 0,370 | 0,501 | Frente a la NDC financiada: factor de planta de la clase PPHRORAB a 0,155 desde 2029; factor de planta medio de las once clases hidroeléctricas a 0,501 desde 2029. |
| A-CCDER | 3,29 | 3,68 | 3,50 | 1,27 | 1,27 | 0,00 | 5,06 | 0,42 | 1,97 | 1,76 | 1,68 | 0,459 | 0,485 | 0,370 | 0,531 | Frente a la NDC financiada: factor de planta de la clase PPHRORAB a 0,485 desde 2027; factor de planta medio de las once clases hidroeléctricas a 0,531 desde 2027. |
| A-ANOSECO | 3,29 | 3,68 | 3,50 | 1,27 | 1,27 | 0,00 | 5,06 | 0,42 | 1,97 | 1,76 | 1,68 | 0,459 | 0,490 | 0,370 | 0,409 | Frente a la NDC financiada: factor de planta de la clase PPHRORAB a 0,490 desde 2026; factor de planta medio de las once clases hidroeléctricas a 0,409 desde 2026. |
| A-ANOSEC3 | 3,29 | 3,68 | 3,50 | 1,27 | 1,27 | 0,00 | 5,06 | 0,42 | 1,97 | 1,76 | 1,68 | 0,459 | 0,490 | 0,370 | 0,409 | Frente a la NDC financiada: factor de planta de la clase PPHRORAB a 0,490 desde 2026; factor de planta medio de las once clases hidroeléctricas a 0,409 desde 2026. |
| A-ANOSECM | 3,29 | 3,68 | 3,50 | 1,27 | 1,27 | 0,00 | 5,06 | 0,42 | 1,97 | 1,76 | 1,68 | 0,459 | 0,515 | 0,370 | 0,489 | Frente a la NDC financiada: factor de planta de la clase PPHRORAB a 0,515 desde 2026; factor de planta medio de las once clases hidroeléctricas a 0,489 desde 2026. |
| A-CCOFFANOSECO | 3,29 | 3,68 | 3,50 | 1,27 | 1,27 | 0,00 | 5,06 | 0,42 | 1,97 | 1,76 | 1,68 | 0,459 | 0,000 | 0,370 | 0,364 | Frente a la NDC financiada: factor de planta de la clase PPHRORAB a 0,000 desde 2026; factor de planta medio de las once clases hidroeléctricas a 0,364 desde 2026. |
| A-FOI | 3,29 | 3,68 | 3,50 | 1,27 | 1,27 | 0,00 | 0,00 | 0,00 | 0,00 | 1,76 | 1,68 | 0,459 | 0,568 | 0,370 | 0,539 | Frente a la NDC financiada: piso de generación de térmica a 0 GWh desde 2026; piso de generación de térmica a 0 GWh desde 2026; piso de generación de térmica a 0 GWh desde 2026. |
| A-IMP0 | 3,29 | 3,68 | 3,50 | 1,27 | 1,27 | 0,00 | 5,06 | 0,42 | 1,97 | 0,00 | 0,00 | 0,459 | 0,568 | 0,370 | 0,539 | Frente a la NDC financiada: techo de generación de importación a 0 GWh desde 2026; piso de generación de importación a 0 GWh desde 2026. |
| A-ACT | 3,29 | 3,68 | 3,50 | 1,27 | 1,27 | 0,00 | 5,06 | 0,42 | 1,97 | 0,00 | 0,00 | 0,459 | 0,490 | 0,370 | 0,409 | Frente a la NDC financiada: techo de generación de importación a 0 GWh desde 2026; piso de generación de importación a 0 GWh desde 2026; factor de planta de la clase PPHRORAB a 0,490 desde 2026; factor de planta medio de las once clases hidroeléctricas a 0,409 desde 2026. |
| A-ACTDEM | 3,29 | 3,68 | 3,50 | 1,27 | 1,27 | 0,00 | 5,06 | 0,42 | 1,97 | 0,00 | 0,00 | 0,459 | 0,490 | 0,370 | 0,409 | Frente a la NDC financiada: techo de generación de importación a 0 GWh desde 2026; piso de generación de importación a 0 GWh desde 2026; factor de planta de la clase PPHRORAB a 0,490 desde 2026; factor de planta medio de las once clases hidroeléctricas a 0,409 desde 2026. |
| A-GAS | 3,29 | 3,68 | 3,50 | 1,27 | 1,27 | 0,00 | 5,06 | 0,42 | 1,97 | 1,76 | 1,68 | 0,459 | 0,568 | 0,370 | 0,539 | Igual a la NDC financiada. |
| A-SIN | 0,74 | 0,12 | 0,12 | 0,00 | 0,00 | 0,00 | 5,06 | 0,42 | 1,97 | 1,76 | 1,68 | 0,459 | 0,568 | 0,370 | 0,539 | Frente a la NDC financiada: techo de generación eólica a 204 GWh desde 2026; techo de generación solar a 34 GWh desde 2026; piso de generación solar a 33 GWh desde 2027; techo de generación geotérmica a 0 GWh desde 2029; piso de generación geotérmica a 0 GWh desde 2029. |
| Ambición ampliada y sus pruebas |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| B | 9,78 | 11,71 | 3,50 | 1,27 | 1,27 | 0,69 | 5,06 | 0,42 | 1,97 | 1,76 | 1,68 | 0,590 | 0,568 | 0,370 | 0,539 | Frente a la NDC financiada: techo de generación eólica a 2 716 GWh desde 2028; techo de generación solar a 3 254 GWh desde 2028; techo de generación con biomasa a 193 GWh desde 2031. |
| B-CCOFF | 9,78 | 11,71 | 3,50 | 1,27 | 1,27 | 0,69 | 5,06 | 0,42 | 1,97 | 1,76 | 1,68 | 0,590 | 0,000 | 0,370 | 0,487 | Frente al escenario «Ambición ampliada»: factor de planta de la clase PPHRORAB a 0,000 desde 2029; factor de planta medio de las once clases hidroeléctricas a 0,487 desde 2029. |
| B-CCSOLO | 9,78 | 11,71 | 3,50 | 1,27 | 1,27 | 0,69 | 5,06 | 0,42 | 1,97 | 1,76 | 1,68 | 0,590 | 0,155 | 0,370 | 0,501 | Frente al escenario «Ambición ampliada»: factor de planta de la clase PPHRORAB a 0,155 desde 2029; factor de planta medio de las once clases hidroeléctricas a 0,501 desde 2029. |
| B-CCDER | 9,78 | 11,71 | 3,50 | 1,27 | 1,27 | 0,69 | 5,06 | 0,42 | 1,97 | 1,76 | 1,68 | 0,590 | 0,485 | 0,370 | 0,531 | Frente al escenario «Ambición ampliada»: factor de planta de la clase PPHRORAB a 0,485 desde 2027; factor de planta medio de las once clases hidroeléctricas a 0,531 desde 2027. |
| B-ANOSECO | 9,78 | 11,71 | 3,50 | 1,27 | 1,27 | 0,69 | 5,06 | 0,42 | 1,97 | 1,76 | 1,68 | 0,590 | 0,490 | 0,370 | 0,409 | Frente al escenario «Ambición ampliada»: factor de planta de la clase PPHRORAB a 0,490 desde 2026; factor de planta medio de las once clases hidroeléctricas a 0,409 desde 2026. |
| B-ANOSEC3 | 9,78 | 11,71 | 3,50 | 1,27 | 1,27 | 0,69 | 5,06 | 0,42 | 1,97 | 1,76 | 1,68 | 0,590 | 0,490 | 0,370 | 0,409 | Frente al escenario «Ambición ampliada»: factor de planta de la clase PPHRORAB a 0,490 desde 2026; factor de planta medio de las once clases hidroeléctricas a 0,409 desde 2026. |
| B-ANOSECM | 9,78 | 11,71 | 3,50 | 1,27 | 1,27 | 0,69 | 5,06 | 0,42 | 1,97 | 1,76 | 1,68 | 0,590 | 0,515 | 0,370 | 0,489 | Frente al escenario «Ambición ampliada»: factor de planta de la clase PPHRORAB a 0,515 desde 2026; factor de planta medio de las once clases hidroeléctricas a 0,489 desde 2026. |
| B-CCOFFANOSECO | 9,78 | 11,71 | 3,50 | 1,27 | 1,27 | 0,69 | 5,06 | 0,42 | 1,97 | 1,76 | 1,68 | 0,590 | 0,000 | 0,370 | 0,364 | Frente al escenario «Ambición ampliada»: factor de planta de la clase PPHRORAB a 0,000 desde 2026; factor de planta medio de las once clases hidroeléctricas a 0,364 desde 2026. |
| B-FOI | 9,78 | 11,71 | 3,50 | 1,27 | 1,27 | 0,69 | 0,00 | 0,00 | 0,00 | 1,76 | 1,68 | 0,590 | 0,568 | 0,370 | 0,539 | Frente al escenario «Ambición ampliada»: piso de generación de térmica a 0 GWh desde 2026; piso de generación de térmica a 0 GWh desde 2026; piso de generación de térmica a 0 GWh desde 2026. |
| B-IMP0 | 9,78 | 11,71 | 3,50 | 1,27 | 1,27 | 0,69 | 5,06 | 0,42 | 1,97 | 0,00 | 0,00 | 0,590 | 0,568 | 0,370 | 0,539 | Frente al escenario «Ambición ampliada»: techo de generación de importación a 0 GWh desde 2026; piso de generación de importación a 0 GWh desde 2026. |
| B-ACT | 9,78 | 11,71 | 3,50 | 1,27 | 1,27 | 0,69 | 5,06 | 0,42 | 1,97 | 0,00 | 0,00 | 0,590 | 0,490 | 0,370 | 0,409 | Frente al escenario «Ambición ampliada»: techo de generación de importación a 0 GWh desde 2026; piso de generación de importación a 0 GWh desde 2026; factor de planta de la clase PPHRORAB a 0,490 desde 2026; factor de planta medio de las once clases hidroeléctricas a 0,409 desde 2026. |
| B-ACTDEM | 9,78 | 11,71 | 3,50 | 1,27 | 1,27 | 0,69 | 5,06 | 0,42 | 1,97 | 0,00 | 0,00 | 0,590 | 0,490 | 0,370 | 0,409 | Frente al escenario «Ambición ampliada»: techo de generación de importación a 0 GWh desde 2026; piso de generación de importación a 0 GWh desde 2026; factor de planta de la clase PPHRORAB a 0,490 desde 2026; factor de planta medio de las once clases hidroeléctricas a 0,409 desde 2026. |
| B-GAS | 9,78 | 11,71 | 3,50 | 1,27 | 1,27 | 0,69 | 5,06 | 0,42 | 1,97 | 1,76 | 1,68 | 0,590 | 0,568 | 0,370 | 0,539 | Igual al escenario «Ambición ampliada». |
| Ambición integral y sus pruebas |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| C | 9,78 | 11,71 | 3,50 | 4,71 | 1,27 | 0,69 | 5,06 | 0,42 | 1,97 | 1,76 | 1,68 | 0,590 | 0,568 | 0,370 | 0,539 | Frente al escenario «Ambición ampliada»: techo de generación geotérmica a 1 307 GWh desde 2035. |
| C-CCOFF | 9,78 | 11,71 | 3,50 | 4,71 | 1,27 | 0,69 | 5,06 | 0,42 | 1,97 | 1,76 | 1,68 | 0,590 | 0,000 | 0,370 | 0,487 | Frente al escenario «Ambición integral»: factor de planta de la clase PPHRORAB a 0,000 desde 2029; factor de planta medio de las once clases hidroeléctricas a 0,487 desde 2029. |
| C-CCSOLO | 9,78 | 11,71 | 3,50 | 4,71 | 1,27 | 0,69 | 5,06 | 0,42 | 1,97 | 1,76 | 1,68 | 0,590 | 0,155 | 0,370 | 0,501 | Frente al escenario «Ambición integral»: factor de planta de la clase PPHRORAB a 0,155 desde 2029; factor de planta medio de las once clases hidroeléctricas a 0,501 desde 2029. |
| C-CCDER | 9,78 | 11,71 | 3,50 | 4,71 | 1,27 | 0,69 | 5,06 | 0,42 | 1,97 | 1,76 | 1,68 | 0,590 | 0,485 | 0,370 | 0,531 | Frente al escenario «Ambición integral»: factor de planta de la clase PPHRORAB a 0,485 desde 2027; factor de planta medio de las once clases hidroeléctricas a 0,531 desde 2027. |
| C-ANOSECO | 9,78 | 11,71 | 3,50 | 4,71 | 1,27 | 0,69 | 5,06 | 0,42 | 1,97 | 1,76 | 1,68 | 0,590 | 0,490 | 0,370 | 0,409 | Frente al escenario «Ambición integral»: factor de planta de la clase PPHRORAB a 0,490 desde 2026; factor de planta medio de las once clases hidroeléctricas a 0,409 desde 2026. |
| C-ANOSEC3 | 9,78 | 11,71 | 3,50 | 4,71 | 1,27 | 0,69 | 5,06 | 0,42 | 1,97 | 1,76 | 1,68 | 0,590 | 0,490 | 0,370 | 0,409 | Frente al escenario «Ambición integral»: factor de planta de la clase PPHRORAB a 0,490 desde 2026; factor de planta medio de las once clases hidroeléctricas a 0,409 desde 2026. |
| C-ANOSECM | 9,78 | 11,71 | 3,50 | 4,71 | 1,27 | 0,69 | 5,06 | 0,42 | 1,97 | 1,76 | 1,68 | 0,590 | 0,515 | 0,370 | 0,489 | Frente al escenario «Ambición integral»: factor de planta de la clase PPHRORAB a 0,515 desde 2026; factor de planta medio de las once clases hidroeléctricas a 0,489 desde 2026. |
| C-CCOFFANOSECO | 9,78 | 11,71 | 3,50 | 4,71 | 1,27 | 0,69 | 5,06 | 0,42 | 1,97 | 1,76 | 1,68 | 0,590 | 0,000 | 0,370 | 0,364 | Frente al escenario «Ambición integral»: factor de planta de la clase PPHRORAB a 0,000 desde 2026; factor de planta medio de las once clases hidroeléctricas a 0,364 desde 2026. |
| C-IMP0 | 9,78 | 11,71 | 3,50 | 4,71 | 1,27 | 0,69 | 5,06 | 0,42 | 1,97 | 0,00 | 0,00 | 0,590 | 0,568 | 0,370 | 0,539 | Frente al escenario «Ambición integral»: techo de generación de importación a 0 GWh desde 2026; piso de generación de importación a 0 GWh desde 2026. |
| C-ACT | 9,78 | 11,71 | 3,50 | 4,71 | 1,27 | 0,69 | 5,06 | 0,42 | 1,97 | 0,00 | 0,00 | 0,590 | 0,490 | 0,370 | 0,409 | Frente al escenario «Ambición integral»: techo de generación de importación a 0 GWh desde 2026; piso de generación de importación a 0 GWh desde 2026; factor de planta de la clase PPHRORAB a 0,490 desde 2026; factor de planta medio de las once clases hidroeléctricas a 0,409 desde 2026. |
| C-ACTDEM | 9,78 | 11,71 | 3,50 | 4,71 | 1,27 | 0,69 | 5,06 | 0,42 | 1,97 | 0,00 | 0,00 | 0,590 | 0,490 | 0,370 | 0,409 | Frente al escenario «Ambición integral»: techo de generación de importación a 0 GWh desde 2026; piso de generación de importación a 0 GWh desde 2026; factor de planta de la clase PPHRORAB a 0,490 desde 2026; factor de planta medio de las once clases hidroeléctricas a 0,409 desde 2026. |
| C-GAS | 9,78 | 11,71 | 3,50 | 4,71 | 1,27 | 0,69 | 5,06 | 0,42 | 1,97 | 1,76 | 1,68 | 0,590 | 0,568 | 0,370 | 0,539 | Igual al escenario «Ambición integral». |

palanca de la NDC financiada palanca del escenario «Ambición ampliada» palanca del escenario «Ambición integral» choque del riesgo o del riesgo de operación NDC incondicional (Modelo CLG): valor distinto del escenario «CONA6 sin la expansión a gas declarada»

Valores de 2035 en el _Input.csv de cada escenario (Executables), la entrada que usó el modelo. Techos y pisos: TotalTechnologyAnnualActivityUpperLimit y LowerLimit, en PJ/año (1 PJ = 277,78 GWh). Factor de planta: CapacityFactor, fracción de la capacidad disponible en el año; la última columna es el promedio simple de las clases hidroeléctricas. Una celda sin color repite el valor de su base. Primer año con cambio: palancas de la NDC financiada desde 2026, palancas del escenario «Ambición ampliada» desde 2028, palancas del escenario «Ambición integral» desde 2035, CCOFF desde 2029, CCSOLO desde 2029, CCDER desde 2027, ANOSECO desde 2026, ANOSEC3 desde 2026, ANOSECM desde 2026, CCOFFANOSECO desde 2026, FOI desde 2026, IMP0 desde 2026, ACT desde 2026, ACTDEM desde 2026 y SIN desde 2026.

## Adicionalidad y veredicto de compradores

La adicionalidad acota la oferta que los escenarios permiten imaginar. La hoja `Art6_Adicionalidad`
clasifica cada línea de la NDC y de los escenarios por su adicionalidad y recoge el veredicto de
compradores potenciales (primera ronda de entrevistas): núcleo, condicionada o descartar. Los volúmenes
del modelo no cambian por este veredicto. Las gráficas de potencial marcan con rayado las capas cuyas
líneas quedaron en su mayoría como «Descartar». El panel de indicadores muestra aparte la oferta con
adicionalidad firme.

*Tabla. Líneas de la NDC y de los escenarios (hoja Art6_Adicionalidad)*

| Código | Línea | Periodo | Escenario de la NDC | kt/año declarados | Escenario Art. 6 | Adicionalidad | Veredicto de compradores |
|---|---|---|---|---|---|---|---|
| EN01 | Operación Comercial del Tranvía de Cuenca | 2026-2035 | Incondicional | 15,00 | fuera | No transferible |  |
| EN02 | Diseño, Construcción e Implementación de la línea 2 del Tranvía de Cuenca | 2030-2035 | Condicional | 8,00 | A (fuera del modelo) | Por demostrar | Condicionada |
| EN03 | Modernización del Sistema de Transporte Público Metropolitano de Pasajeros de Quito a través de la Dotación de Trolebuses | 2026-2035 | Incondicional | 4,97 | fuera | No transferible |  |
| EN04 | Proyecto Primera Línea del Metro de Quito | 2026-2035 | Incondicional | 60,00 | fuera | No transferible |  |
| EN05 | Proyecto Extensión de la Primera Línea del Metro de Quito desde el Labrador hasta La Ofelia | 2032-2035 | Condicional | 16,00 | A (fuera del modelo) | Por demostrar | Condicionada |
| EN06 | Programa de Soluciones Energéticas Upstream | 2026-2035 | Incondicional | 428,55 | fuera | No transferible |  |
| EN07 | Preparación y Despacho de Gasolinas con Etanol | 2026-2035 | Incondicional | 199,06 | fuera | No transferible |  |
| EN08 | Proyecto Geotérmico Chachimbiro | 2034-2035 | Condicional | 192,39 | A | Firme | Núcleo |
| EN10 | Proyecto Eólico Ducal Membrillo | 2029-2035 | Condicional | 195,08 | A | Por demostrar | Descartar |
| EN12 | Proyecto Eólico Pimo | 2030-2035 | Condicional | 406,88 | A | Por demostrar | Descartar |
| EN13 | Central Hidroeléctrica Coca Codo Sinclair | 2026-2035 | Incondicional | 3927,00 | fuera | No transferible |  |
| EN14 | Central Hidroeléctrica Manduriacu | 2026-2035 | Incondicional | 168,00 | fuera | No transferible |  |
| EN15 | Central Hidroeléctrica Mazar | 2026-2035 | Incondicional | 255,00 | fuera | No transferible |  |
| EN16 | Central Hidroeléctrica Minas San Francisco | 2026-2035 | Incondicional | 529,00 | fuera | No transferible |  |
| EN17 | Central Hidroeléctrica Sopladora | 2026-2035 | Incondicional | 1150,00 | fuera | No transferible |  |
| EN18 | Proyecto Hidroeléctrico Santiago | 2034-2035 | Condicional | 7352,82 | fuera | Sin adicionalidad |  |
| EN19 | Proyecto hidroeléctrico Cardenillo | 2034-2035 | Condicional | 1638,63 | fuera | Sin adicionalidad |  |
| EN20 | Proyecto Solar Flotante Mazar | 2029-2035 | Condicional | 180,84 | A | Por demostrar | Descartar |
| EN21 | Proyecto Hidroeléctrico Delsitanisagua | 2026-2035 | Incondicional | 369,00 | fuera | No transferible |  |
| EN22 | Proyecto Eólico Villonaco | 2026-2035 | Incondicional | 37,00 | fuera | No transferible |  |
| EN23 | Complejo Hidroeléctrico Toachi Pilatón | 2026-2035 | Incondicional | 537,00 | fuera | No transferible |  |
| EN24 | Proyecto Hidroeléctrico Soldados Yanuncay | 2028-2035 | Incondicional | 58,00 | fuera | No transferible |  |
| EN25 | Proyecto Fotovoltaico Huascachaca | 2026-2035 | Condicional | 16,00 | A | Por demostrar | Descartar |
| EN26 | Sistema Híbrido Isabela (Fase II) | 2028-2035 | Incondicional | 1,34 | fuera | No transferible |  |
| EN27 | Proyecto Conolophus | 2029-2035 | Incondicional | 17,78 | fuera | No transferible |  |
| EN28 | Sistema Solar Fotovoltaico San Cristóbal (Fase II) | 2029-2035 | Condicional | 3,57 | A (fuera del modelo) | Por demostrar | Condicionada |
| EN29 | Isla Floreana 100% Renovable | 2028-2035 | Condicional | 0,29 | A (fuera del modelo) | Por demostrar | Condicionada |
| EN31 | Sistema Eléctrico de Monorriel Intracantonal para la Provincia Guayas | 2030-2035 | Condicional | 42,78 | A (fuera del modelo) | Por demostrar | Condicionada |
| EN32 | Renovación y Descarbonización del Transporte Público y Comercial en el Ecuador | 2026-2035 | Condicional | 185,00 | A (fuera del modelo) | Por demostrar | Condicionada |
| B-SOL | Portafolio solar CELEC EP y AFD (3 000 GWh/año) | 2028-2035 | Fuera de la NDC |  | B | Por demostrar | Descartar |
| B-EOL | Eólica del plan de expansión no listada en la NDC (585 MW) | 2028-2035 | Fuera de la NDC |  | B | Por demostrar | Descartar |
| B-BIO | Biomasa del portafolio ESIN-CELEC EP (39,3 MW, 192,8 GWh/año) | 2031-2035 | Fuera de la NDC |  | B | Por demostrar | Condicionada |
| FOI | Sin pisos térmicos del Modelo CLG | 2026-2035 | Supuesto de operación |  | sensibilidad | No es actividad |  |
| C-EM | Electromovilidad del Plan de Acción del PLANMICC (vehículos eléctricos e híbridos privados, taxis y buses) | 2026-2035 | Fuera de la NDC |  | C | Por demostrar |  |
| C-EI | Eficiencia energética industrial del Plan de Acción del PLANMICC (ISO 50001, ESCO) | 2026-2035 | Fuera de la NDC |  | C | Por demostrar |  |
| C-GEO | Proyecto Geotérmico Binacional Tufiño-Chiles-Cerro Negro (138 MW) | 2035 | Fuera de la NDC |  | C | Por demostrar |  |
