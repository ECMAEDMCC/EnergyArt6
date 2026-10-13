# -*- coding: utf-8 -*-
"""B3: etapa de Artículo 6, posterior a la cadena oficial del modelo.

Orden: B1_Base_Scenarios_Adj_Parallel.py (crea y resuelve los escenarios de B1_Scenario_Config.xlsx),
B2_Results_Creator_f0.py (consolida ECUInput.csv y ECUOutput.csv) y este archivo. B3 no modifica
datafiles ni resultados: los lee, verifica que cada escenario difiera de su base solo en sus palancas,
escribe B2_Output_Art6/MANIFIESTO.csv con el md5 de cada datafile y produce tablas, gráficas, tablero,
cuaderno y documentación.
"""
import os
import sys

os.chdir(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, "Art6_motor")
import etapa_art6  # noqa: E402

if __name__ == "__main__":
    etapa_art6.posterior()
