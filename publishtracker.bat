@echo off
REM --- Lanzador Silencioso para PublishTracker ---
REM Este script inicia la aplicacion sin mostrar una ventana de consola.
REM El usuario puede hacer doble clic en este archivo para iniciar el programa.

REM Cambia al directorio donde se encuentra el script para asegurar rutas relativas correctas.
cd /d "%~dp0"

REM Define la ruta al ejecutable de pythonw.exe dentro del entorno virtual.
SET PYTHONW_EXEC=".\.venv\Scripts\pythonw.exe"

REM Define la ruta al script que lanza la aplicacion.
SET LAUNCHER_SCRIPT=".\run_webview.py"

REM Verifica si el entorno virtual y el lanzador existen.
IF NOT EXIST %PYTHONW_EXEC% (
    ECHO Error: El entorno virtual no parece estar instalado.
    ECHO Por favor, ejecuta 'install.bat' primero.
    pause
    exit /b
)

IF NOT EXIST %LAUNCHER_SCRIPT% (
    ECHO Error: No se encuentra el script de inicio 'run_webview.py'.
    pause
    exit /b
)

ECHO Iniciando PublishTracker...

REM Lanza la aplicacion en segundo plano usando pythonw.exe.
START "PublishTracker" %PYTHONW_EXEC% %LAUNCHER_SCRIPT%

exit
