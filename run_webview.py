import webview
import subprocess
import time
import sys
import threading

# --- Lanzador de Aplicación PublishTracker con Webview ---
# Este script inicia el servidor de desarrollo de Django en un hilo separado
# y luego abre una ventana de pywebview que muestra la aplicación.

# Variable global para mantener el proceso del servidor
server_process = None

def run_django_server():
    """
    Ejecuta el comando 'runserver' de Django en un subproceso.
    """
    global server_process
    # Se usa --noreload para evitar que el servidor se reinicie, lo cual puede crear procesos huérfanos.
    command = [sys.executable, "manage.py", "runserver", "--noreload"]
    server_process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    
    # Imprimir la salida del servidor en la consola para depuración
    # Esto se ejecutará en un hilo separado para no bloquear.
    def print_output(pipe):
        for line in iter(pipe.readline, ''):
            print(f"[Django Server] {line.strip()}")
        pipe.close()

    stdout_thread = threading.Thread(target=print_output, args=(server_process.stdout,))
    stderr_thread = threading.Thread(target=print_output, args=(server_process.stderr,))
    stdout_thread.start()
    stderr_thread.start()

def on_closed():
    """
    Se ejecuta cuando la ventana de webview se cierra.
    Detiene el proceso del servidor de Django.
    """
    global server_process
    if server_process:
        print("Cerrando el servidor de Django...")
        server_process.kill()
        print("Servidor de Django cerrado.")

if __name__ == '__main__':
    # Iniciar el servidor de Django en un hilo separado para no bloquear la GUI
    server_thread = threading.Thread(target=run_django_server)
    server_thread.daemon = True  # Permite que el programa principal termine aunque el hilo siga corriendo
    server_thread.start()

    # Esperar un momento para que el servidor de Django inicie
    print("Esperando a que el servidor de Django inicie...")
    time.sleep(4)
    print("Servidor listo. Abriendo webview...")

    # Crear y mostrar la ventana de webview
    window = webview.create_window(
        'PublishTracker',
        'http://127.0.0.1:8000/',
        width=1280,
        height=800,
        resizable=True,
        min_size=(800, 600)
    )
    
    # Registrar el evento para cuando la ventana se cierre
    window.events.closed += on_closed
    
    webview.start()
