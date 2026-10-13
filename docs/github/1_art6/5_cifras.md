# Cifras principales

*Tabla. Cifras principales de la corrida (kt CO2-eq)*

| Cifra | Valor | Periodo |
|---|---|---|
| Oferta transferible, sin la electromovilidad de flotas en reserva<br>`tablas/oferta_tres_niveles.csv`, clave `oferta_central_sin_reserva` | 11 674,4 | 2031-2035 |
| Lista blanca validada por los expertos, autorizable con el sistema intacto<br>`tablas/reserva_por_aniada.csv`, clave `reserva\|lista_blanca\|intacto` | 3 072,3 | 2031-2035 |
| De esa oferta, línea firme (geotermia de Chachimbiro)<br>`tablas/oferta_por_caso.csv`, clave `oferta_central_firme` | 384,8 | 2031-2035 |
| Margen de 2035 del Escenario C frente a la meta incondicional (1)<br>`tablas/headroom_proyecciones.csv`, clave `margen_2035_C_CLG_prudente` | 8 556,8 | 2035 |
| Lista blanca autorizable si persiste la demanda de 2026 (1)<br>`tablas/reserva_por_aniada.csv`, clave `reserva\|lista_blanca\|ACTDEM` | 2 793,8 | 2031-2035 |
| Sobreventa, situación actual 2026 con demanda persistente (1)<br>`tablas/sobreventa_por_metodo_y_subconjunto.csv`, clave `sobreventa\|sin_EN32\|anual\|CLG_prudente\|ACTDEM` | 4 950,3 | 2031-2035 |
| Sobreventa, salida de Coca Codo sola (1)<br>`tablas/sobreventa_por_metodo_y_subconjunto.csv`, clave `sobreventa\|sin_EN32\|anual\|CLG_prudente\|CCSOLO` | 4 006,2 | 2031-2035 |
| Sobreventa, situación actual 2026 con demanda transitoria (1)<br>`tablas/sobreventa_por_metodo_y_subconjunto.csv`, clave `sobreventa\|sin_EN32\|anual\|CLG_prudente\|ACT` | 1 457,8 | 2031-2035 |
| Sobreventa, un año seco cada tres (1)<br>`tablas/sobreventa_por_metodo_y_subconjunto.csv`, clave `sobreventa\|sin_EN32\|anual\|CLG_prudente\|ANOSEC3` | 1 080,0 | 2031-2035 |
| Capa del Escenario A sobre CONA6<br>`tablas/descomposicion_reducciones.csv`, clave `capa_A_2031_2035` | 2 473,1 | 2031-2035 |
| Capa del Escenario B sobre A<br>`tablas/descomposicion_reducciones.csv`, clave `capa_B_2031_2035` | 6 129,0 | 2031-2035 |
| Capa del Escenario C sobre B<br>`tablas/descomposicion_reducciones.csv`, clave `capa_C_2031_2035` | 2 350,3 | 2031-2035 |
| Oferta con la electromovilidad de flotas en reserva<br>`tablas/oferta_tres_niveles.csv`, clave `oferta_central_con_reserva` | 12 599,4 | 2031-2035 |
| Oferta con los pisos térmicos del Modelo CLG (sensibilidad)<br>`tablas/oferta_tres_niveles.csv`, clave `oferta_con_pisos_CLG_12_10_sin_reserva` | 9 446,9 | 2031-2035 |
| Puente CONA6 menos NDCCON (efecto de la calibración propia)<br>`tablas/descomposicion_reducciones.csv`, clave `puente_CONA6_menos_NDCCON_2031_2035` | −7 085,0 | 2031-2035 |
| Puente CONA6G menos NDCCON (sin la expansión a gas declarada)<br>`tablas/descomposicion_reducciones.csv`, clave `puente_CONA6G_menos_NDCCON_2031_2035` | −4 310,0 | 2031-2035 |
| Margen de 2035 de CONA6 frente a la meta incondicional (1)<br>`tablas/headroom_proyecciones.csv`, clave `margen_2035_CONA6_CLG_prudente` | 7 268,2 | 2035 |
| Margen de 2035 de CONA6 con la regla condicional<br>`tablas/headroom_proyecciones.csv`, clave `margen_2035_CONA6_CLG_condicional` | 10 600,0 | 2035 |

Fuente: `Energy/B2_Output_Art6/cifras_finales_producto3.json` de la corrida del 13-10-2026, 22:15 (md5 `4e118305ce76a2d7b5fc967568cb1997`). Bajo cada cifra figuran la tabla de `Energy/B2_Output_Art6` de la que sale y su clave en el JSON. (1) Proyección del Modelo CLG y regla prudente. La sobreventa usa el método anual y la oferta sin la electromovilidad de flotas en reserva.
