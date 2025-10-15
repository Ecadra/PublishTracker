@echo off
REM --- Asistente de Instalacion para PublishTracker (Windows) ---
REM Este script automatiza la configuracion completa del entorno de desarrollo.

ECHO --- Iniciando Instalacion de PublishTracker ---

REM 1. Verificar que Python esta instalado
python --version >nul 2>&1
IF %ERRORLEVEL% NEQ 0 (
    ECHO Error: Python no esta instalado o no esta en el PATH.
    ECHO Por favor, instalalo para continuar.
    GOTO :EOF
)

ECHO Paso 1: Creando entorno virtual en la carpeta '.venv'...
python -m venv .venv

IF NOT EXIST .venv (
    ECHO Error: No se pudo crear el entorno virtual. Verifica tus permisos.
    GOTO :EOF
)

REM 2. Activar el entorno virtual
ECHO Paso 2: Activando el entorno virtual...
CALL .venv\Scripts\activate

REM 3. Actualizar pip
ECHO Paso 3: Actualizando pip...
python -m pip install --upgrade pip

REM 4. Instalar dependencias desde requirements.txt
ECHO Paso 4: Instalando dependencias del proyecto...
IF NOT EXIST requirements.txt (
    ECHO Error: No se encontro el archivo requirements.txt.
    CALL .venv\Scripts\deactivate
    GOTO :EOF
)
pip install -r requirements.txt

REM 5. Ejecutar migraciones para crear las tablas de la base de datos
ECHO Paso 5: Aplicando migraciones de la base de datos...
python manage.py makemigrations
python manage.py makemigrations authors
python manage.py makemigrations core
python manage.py makemigrations journals 
python manage.py makemigrations publications
python manage.py migrate

REM 6. Cargar los datos iniciales (fixtures) con rutas relativas
ECHO Paso 6: Cargando datos iniciales (fixtures)...
python manage.py loaddata publishtracker/apps/authors/fixtures/initial_roles.json
python manage.py loaddata publishtracker/apps/core/fixtures/initial_estatus.json
python manage.py loaddata publishtracker/apps/core/fixtures/initial_programas.json
python manage.py loaddata publishtracker/apps/journals/fixtures/initial_tipo_archivo_revista.json
python manage.py loaddata publishtracker/apps/publications/fixtures/intial_tipos_archivo_paper.json

REM 7. Crear un superusuario
ECHO Paso 7: Creando un superusuario para el panel de administracion...
ECHO Por favor, ingresa los datos para el superusuario de Django:
python manage.py createsuperuser

ECHO.
ECHO --- ¡Instalacion completada exitosamente! ---
ECHO Iniciando la aplicacion en modo de escritorio...

REM 8. Lanzar la aplicacion con el webview
python run_webview.py

