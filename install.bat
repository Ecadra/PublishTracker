@echo off
REM --- Asistente de Instalacion para PublishTracker (Windows) ---
REM Este script automatiza la configuracion completa del entorno de desarrollo.
ECHO --- Iniciando Instalacion de PublishTracker ---

REM 1. Verificar que Git esta instalado
ECHO Paso 1. Verificar que git está instalado
git --version >nul 2>&1
IF %ERRORLEVEL% NEQ 0 (
    ECHO.
    ECHO [ADVERTENCIA] Git no esta instalado o no esta en el PATH.
    ECHO La aplicacion funcionara, pero no podras usar la funcion de actualizacion automatica.
    ECHO Te recomendamos instalar Git para una experiencia completa.
    ECHO.
    pause
) ELSE (
    REM Verificar si es un repositorio de Git
    IF NOT EXIST .\.git (
        ECHO.
        ECHO [ADVERTENCIA] Has descargado el proyecto como un .zip.
        ECHO La aplicacion se instalara y funcionara, pero no podras recibir actualizaciones automaticas.
        ECHO Para habilitar las actualizaciones, por favor, instala usando "git clone".
        ECHO.
        pause
    )
)

REM 2. Verificar que Python esta instalado
ECHO Paso 2. Verificar que Python esta instalado
python --version >nul 2>&1
IF %ERRORLEVEL% NEQ 0 (
    ECHO Error: Python no esta instalado o no esta en el PATH.
    ECHO Por favor, instalalo para continuar.
    GOTO :EOF
)

ECHO Creando entorno virtual en la carpeta '.venv'...
python -m venv .venv

IF NOT EXIST .venv (
    ECHO Error: No se pudo crear el entorno virtual. Verifica tus permisos.
    GOTO :EOF
)

REM 3. Activar el entorno virtual
ECHO Paso 3: Activando el entorno virtual...
CALL .venv\Scripts\activate

REM 4. Actualizar pip
ECHO Paso 4: Actualizando pip...
python -m pip install --upgrade pip

REM 5. Instalar dependencias desde requirements.txt
ECHO Paso 5: Instalando dependencias del proyecto...
IF NOT EXIST requirements.txt (
    ECHO Error: No se encontro el archivo requirements.txt.
    CALL .venv\Scripts\deactivate
    GOTO :EOF
)
pip install -r requirements.txt

REM 6. Ejecutar migraciones para crear las tablas de la base de datos
ECHO Paso 6: Aplicando migraciones de la base de datos...
python manage.py makemigrations
python manage.py makemigrations authors
python manage.py makemigrations core
python manage.py makemigrations journals 
python manage.py makemigrations publications
python manage.py migrate

REM 7. Cargar los datos iniciales (fixtures)
ECHO Paso 7: Cargando datos iniciales (fixtures)...
python manage.py loaddata publishtracker/apps/authors/fixtures/initial_roles.json
python manage.py loaddata publishtracker/apps/core/fixtures/initial_estatus.json
python manage.py loaddata publishtracker/apps/core/fixtures/initial_programas.json
python manage.py loaddata publishtracker/apps/journals/fixtures/initial_tipo_archivo_revista.json
python manage.py loaddata publishtracker/apps/publications/fixtures/intial_tipos_archivo_paper.json

ECHO.
ECHO --- ¡Instalacion completada exitosamente! ---
ECHO Iniciando la aplicacion en modo de escritorio...

REM 9. Lanzar la aplicacion con el webview
python run_webview.py