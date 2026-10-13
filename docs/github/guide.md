# Guía de uso

## Requisitos

- Windows de 64 bits con unos 20 GB de memoria libre, porque B1 resuelve cuatro escenarios a la vez y cada
  corrida de glpsol usa unos 4,5 GB.
- Miniconda o Anaconda. `environment.yml` reproduce el entorno conda `osemosys` con las versiones
  exactas con que se corrió el modelo (Python 3.13, pandas 2.2.3 sin pyarrow, openpyxl, plotly, kaleido,
  nbclient y Sphinx).
- GLPK 4.65. El repositorio trae `glpsol.exe` y su biblioteca en `Energy/glpk`, con su licencia GNU
  GPL. También sirve una instalación de WinGLPK 4.65 en `C:\winglpk\glpk\w64` o cualquier `glpsol`
  del PATH.

## Instalación

1. Instale Miniconda para Windows de 64 bits desde https://docs.conda.io/en/latest/miniconda.html, con
   las opciones por omisión.
1. Descargue o clone el repositorio en una carpeta con una ruta corta, por ejemplo `C:\modelos`.
   Algunas rutas internas son largas y Windows limita la ruta completa a 260 caracteres.
1. Cree el entorno `osemosys` con este comando, en la consola de Anaconda y desde la raíz del
   repositorio.

   ```text
   conda env create -f environment.yml
   ```

## Resultados

Abra `Energy/B3_Visualizador_Art6.ipynb` en VS Code o el tablero
`Energy/B2_Output_Art6/tablero_art6.html` en el navegador. El tablero funciona sin internet y cada
gráfica lleva su guía de lectura.

`Energy/B2_Output_Art6/cifras_finales_producto3.json` trae cada cifra con la tabla de la que sale y el
md5 de los `_Output.csv` que la producen. Un subconjunto de esas cifras está en el README y en
[Cifras principales](1_art6/5_cifras.md).
