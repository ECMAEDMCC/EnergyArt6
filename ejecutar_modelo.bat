@echo off
rem ============================================================================================================
rem  Corrida con un clic del modelo de energia y de los escenarios de Articulo 6 (sandbox PNUD).
rem
rem    ejecutar_modelo.bat           cadena completa: B1 (52 escenarios, unos 30 minutos), B2 y B3
rem    ejecutar_modelo.bat rapido    B1 solo con las 8 referencias y los escenarios A, B y C (unos 8 minutos),
rem                                  despues B2 y B3 con todos los escenarios
rem
rem  Comprueba conda y glpsol, crea el entorno "osemosys" desde environment.yml si no existe y deja el registro
rem  de la corrida en Energy\registros\corrida_<modo>_<fecha>.log. Resultados: Energy\B2_Output_Art6 (tablas, graficas,
rem  tablero_art6.html, cifras_finales_producto3.json y verificacion.txt).
rem ============================================================================================================
setlocal EnableExtensions EnableDelayedExpansion
chcp 65001 >nul

set "RAIZ=%~dp0"
if "%RAIZ:~-1%"=="\" set "RAIZ=%RAIZ:~0,-1%"
set "ENERGY=%RAIZ%\Energy"
set "ENTORNO=osemosys"
set "MODO=completo"
if /I "%~1"=="rapido" set "MODO=rapido"
if not "%~1"=="" if /I not "%~1"=="rapido" if /I not "%~1"=="completo" (
    echo Uso: ejecutar_modelo.bat [rapido^|completo]
    exit /b 2
)

if not exist "%ENERGY%\registros" mkdir "%ENERGY%\registros"
for /f "usebackq delims=" %%i in (`powershell -NoProfile -Command "Get-Date -Format yyyy-MM-dd_HHmmss"`) do set "SELLO=%%i"
set "LOG=%ENERGY%\registros\corrida_%MODO%_%SELLO%.log"
echo Corrida %MODO% iniciada %DATE% %TIME% > "%LOG%"
echo.
echo Modelo de energia y escenarios de Articulo 6 - corrida %MODO%
echo Registro: %LOG%
echo.

rem ------------------------------------------------------------------------------------------------ 1. conda
set "CONDA_BAT="
if defined CONDA_EXE (
    for %%d in ("%CONDA_EXE%\..\..") do if exist "%%~fd\condabin\conda.bat" set "CONDA_BAT=%%~fd\condabin\conda.bat"
)
if not defined CONDA_BAT for %%c in (
    "%USERPROFILE%\miniconda3\condabin\conda.bat"
    "%USERPROFILE%\anaconda3\condabin\conda.bat"
    "%LOCALAPPDATA%\miniconda3\condabin\conda.bat"
    "%LOCALAPPDATA%\anaconda3\condabin\conda.bat"
    "%PROGRAMDATA%\miniconda3\condabin\conda.bat"
    "%PROGRAMDATA%\anaconda3\condabin\conda.bat"
) do if not defined CONDA_BAT if exist %%c set "CONDA_BAT=%%~c"
if not defined CONDA_BAT (
    for /f "delims=" %%w in ('where conda.bat 2^>nul') do if not defined CONDA_BAT set "CONDA_BAT=%%w"
)
if not defined CONDA_BAT (
    echo [ERROR] No encuentro conda. Instale Miniconda (ver README.md, seccion Instalacion^) y vuelva a correr.
    echo [ERROR] No encuentro conda >> "%LOG%"
    exit /b 1
)
echo [1/6] conda: %CONDA_BAT%
echo conda: %CONDA_BAT% >> "%LOG%"

rem ------------------------------------------------------------------------------------- 2. entorno osemosys
call "%CONDA_BAT%" env list | findstr /R /C:"^%ENTORNO% " >nul
if errorlevel 1 (
    echo [2/6] El entorno %ENTORNO% no existe: se crea desde environment.yml ^(unos minutos, requiere internet^)
    echo Creando el entorno %ENTORNO% desde environment.yml >> "%LOG%"
    call "%CONDA_BAT%" env create -f "%RAIZ%\environment.yml" >> "%LOG%" 2>&1
    if errorlevel 1 (
        echo [ERROR] No se pudo crear el entorno; ver %LOG%
        exit /b 1
    )
) else (
    echo [2/6] Entorno %ENTORNO% encontrado
)
call "%CONDA_BAT%" activate %ENTORNO%
if errorlevel 1 (
    echo [ERROR] No se pudo activar el entorno %ENTORNO%
    exit /b 1
)
for /f "delims=" %%v in ('python -c "import sys, pandas; print(sys.version.split()[0], pandas.__version__)"') do set "VERSIONES=%%v"
echo        Python y pandas: %VERSIONES%
echo Python y pandas: %VERSIONES% >> "%LOG%"

rem ------------------------------------------------------------------------------------------------ 3. glpsol
where glpsol >nul 2>nul
if errorlevel 1 (
    if exist "%ENERGY%\glpk\glpsol.exe" (
        set "PATH=%ENERGY%\glpk;%PATH%"
    ) else if exist "C:\winglpk\glpk\w64\glpsol.exe" (
        set "PATH=C:\winglpk\glpk\w64;%PATH%"
    ) else (
        echo [ERROR] No encuentro glpsol: instale GLPK 4.65 ^(ver README.md^) o deje glpsol.exe en Energy\glpk
        echo [ERROR] No encuentro glpsol >> "%LOG%"
        exit /b 1
    )
)
for /f "delims=" %%g in ('glpsol --version ^| findstr /C:"GLPK"') do set "GLPK=%%g"
for /f "delims=" %%w in ('where glpsol') do if not defined GLPSOL set "GLPSOL=%%w"
echo [3/6] glpsol: %GLPSOL% (%GLPK%)
echo glpsol: %GLPSOL% (%GLPK%) >> "%LOG%"

set "PYTHONIOENCODING=utf-8"
set "CORRER=python "%ENERGY%\Art6_motor\correr_con_registro.py" --registro "%LOG%""
pushd "%ENERGY%"

rem ------------------------------------------------------------------- 4. validacion del libro y B1
%CORRER% --titulo "Validacion del libro de configuracion" -- python tests\validar_libro.py
if errorlevel 1 (
    echo [ERROR] El libro de configuracion tiene errores; B1 no se corre. Ver %LOG%
    popd
    exit /b 1
)
if /I "%MODO%"=="rapido" (
    python "%ENERGY%\Art6_motor\seleccionar_escenarios.py" --rapido >> "%LOG%" 2>&1
    if errorlevel 1 (
        echo [ERROR] No se pudo preparar la corrida rapida; ver %LOG%
        popd
        exit /b 1
    )
    echo [4/6] B1 con las 8 referencias y A, B y C ^(unos 8 minutos^)
) else (
    echo [4/6] B1 con los 52 escenarios ^(unos 30 minutos; cuatro escenarios a la vez, unos 4,5 GB de RAM cada uno^)
)
%CORRER% --titulo "B1" -- python B1_Base_Scenarios_Adj_Parallel.py
set "ERR_B1=%ERRORLEVEL%"
if /I "%MODO%"=="rapido" python "%ENERGY%\Art6_motor\seleccionar_escenarios.py" --completo >> "%LOG%" 2>&1
if not "%ERR_B1%"=="0" (
    echo [ERROR] B1 termino con codigo %ERR_B1%; ver %LOG%
    popd
    exit /b 1
)
%CORRER% --titulo "Prueba de no regresion de los escenarios del Modelo CLG" -- python tests\no_regresion.py
if errorlevel 1 echo [AVISO] Los escenarios del Modelo CLG difieren de la linea base; ver %LOG%
%CORRER% --titulo "Prueba de la base congelada" -- python tests\base_congelada.py
if errorlevel 1 echo [AVISO] La base corregida difiere de la congelada; ver %LOG%

rem ------------------------------------------------------------------------------------------------ 5. B2
echo [5/6] B2: consolida ECUInput.csv y ECUOutput.csv
%CORRER% --titulo "B2" -- python B2_Results_Creator_f0.py
if errorlevel 1 echo [AVISO] B2 termino con error; B3 lee cada escenario de Executables y sigue

rem ------------------------------------------------------------------------------------------------ 6. B3
echo [6/6] B3: verificacion, analisis, tablas, graficas, tablero y documentacion ^(unos 3 minutos^)
%CORRER% --titulo "B3" -- python B3_Etapa_Art6.py
set "ERR_B3=%ERRORLEVEL%"
popd
if "%ERR_B3%"=="0" (
    pushd "%RAIZ%"
    %CORRER% --titulo "Cifras principales para README y docs" -- python Energy\Art6_motor\cifras_principales.py
    popd
)

echo.
if not "%ERR_B3%"=="0" (
    echo [ERROR] B3 termino con codigo %ERR_B3%; ver %LOG%
    exit /b 1
)
echo Listo. Resultados en Energy\B2_Output_Art6:
echo    tablas\                          tablas de la corrida
echo    cifras_finales_producto3.json    cifras con el md5 de cada _Output.csv
echo    tablero_art6.html                tablero ^(se abre en el navegador, sin internet^)
echo    verificacion.txt                 comprobaciones del motor y de la contabilidad
echo Registro: %LOG%
echo Corrida terminada %DATE% %TIME% >> "%LOG%"
endlocal
exit /b 0
