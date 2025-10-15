# PublishTracker

Asistente de publicaciones con interfaz web integrada y configuración automatizada.

## Requisitos

- Python 3.6 o superior
- pip y venv (generalmente incluidos con Python)

## Instalación

### 1. Descarga o Clona el Repositorio

Puedes descargar el .zip desde GitHub y descomprimirlo, o clonar el repositorio con git:

```bash
git clone https://github.com/Ecadra/PublishTracker.git
cd PublishTracker
```

### 2. Ejecuta el Asistente de Instalación

Simplemente haz doble clic en el archivo `install.bat` o ejecútalo desde la terminal:

```cmd
install.bat
```

### 3. Sigue las Instrucciones en Pantalla

El script te guiará a través de todo el proceso de configuración y, al finalizar, lanzará automáticamente la aplicación por primera vez. Durante la instalación, se te pedirá que crees una cuenta de superusuario.

## Cómo Iniciar la Aplicación

Una vez instalado, puedes iniciar la aplicación en cualquier momento:

### Windows (Recomendado)

Simplemente haz doble clic en el archivo `PublishTracker.bat`. La aplicación se iniciará directamente sin abrir ninguna consola.

## Ejecución para Desarrolladores (con Consola)

Si necesitas ver la salida de la consola para depuración:

```cmd
.\.venv\Scripts\activate && python run_webview.py
```

## Notas

- El entorno virtual se crea automáticamente en la carpeta `.venv`
- Todas las dependencias se instalan automáticamente durante el proceso de instalación
- La aplicación utiliza una interfaz web integrada para una mejor experiencia de usuario

## Contribuciones

Las contribuciones son bienvenidas. Por favor, abre un issue o pull request para sugerencias y mejoras.

## Licencia

Este proyecto es de uso libre.