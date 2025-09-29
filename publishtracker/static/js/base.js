/**
 * =========================
 * 1. UTILIDADES GENERALES
 * =========================
 */

/**
 * Obtiene el valor de una cookie por nombre.
 * @param {string} name - Nombre de la cookie.
 * @returns {string|null} Valor de la cookie o null si no existe.
 */
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.startsWith(name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

/**
 * Muestra una alerta tipo toast (Bootstrap) con mensaje personalizado.
 * @param {string} message - Mensaje a mostrar.
 * @param {string} [type='info'] - Clase de color Bootstrap (success, danger, etc.).
 * @param {number} [duration=3000] - Tiempo en ms antes de desaparecer.
 */
function showCustomAlert(message, type = 'info', duration = 3000) {
    let alertContainer = document.getElementById('custom-alert-container');
    if (!alertContainer) {
        alertContainer = document.createElement('div');
        alertContainer.id = 'custom-alert-container';
        alertContainer.className = 'position-fixed top-0 end-0 p-3';
        alertContainer.style.zIndex = '2000';
        document.body.appendChild(alertContainer);
    }

    const alertId = `alert-${Date.now()}`;
    const alertContent = `
        <div id="${alertId}" class="toast align-items-center border-0" role="alert" aria-live="assertive" aria-atomic="true">
            <div class="d-flex">
                <div class="toast-body bg-${type} text-white rounded-start">${message}</div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>
            </div>
        </div>
    `;
    alertContainer.insertAdjacentHTML('beforeend', alertContent);

    const toastElement = document.getElementById(alertId);
    const toast = new bootstrap.Toast(toastElement, { autohide: true, delay: duration });

    toastElement.addEventListener('hidden.bs.toast', () => toastElement.remove());
    toast.show();
}

/**
 * Agrega/elimina clase 'loading' para indicar carga en un elemento.
 */
function showLoading(element) { element.classList.add('loading'); }
function hideLoading(element) { element.classList.remove('loading'); }

/**
 * =========================
 * 2. INICIALIZACIÓN DEL DOM
 * =========================
 */

document.addEventListener('DOMContentLoaded', () => {
    // Configuración global accesible desde toda la app
    window.PublishTracker = {
        csrfToken: getCookie('csrftoken'),
        baseUrl: window.location.origin,
        modalStack: []
    };

    // Auto-submit en formularios de filtros
    document.querySelectorAll('select[name="status"], select[name="year"]').forEach(select => {
        select.addEventListener('change', () => select.closest('form').submit());
    });

    // Inicializar tooltips de Bootstrap
    [...document.querySelectorAll('[data-bs-toggle="tooltip"]')].forEach(el =>
        new bootstrap.Tooltip(el)
    );
});

/**
 * =========================
 * 3. MANEJO DE MODALES
 * =========================
 */

/**
 * Carga contenido remoto y lo muestra como una nueva vista en el modal dinámico (usando pila).
 * @param {string} url - URL del contenido a cargar.
 * @param {string} title - Título de la nueva vista.
 * @param {string} [size=''] - Tamaño del modal ('sm', 'lg', 'xl', etc.).
 */
async function loadModalContent(url, title, size = '') {
    const modal = document.getElementById('dynamicModal');
    if (!modal) {
        showCustomAlert('Error: Modal no encontrado.', 'danger');
        return;
    }

    // Mostrar indicador de carga DIRECTAMENTE en el cuerpo del modal (sin usar la pila)
    const loadingContent = `
        <div class="text-center py-4">
            <div class="spinner-border text-primary" role="status">
                <span class="visually-hidden">Cargando...</span>
            </div>
            <p class="mt-2">Cargando contenido...</p>
        </div>
    `;
    document.getElementById('modalBody').innerHTML = loadingContent;

    // Mostrar el modal si no está visible
    let modalInstance = bootstrap.Modal.getInstance(modal);
    if (!modalInstance) {
        modalInstance = new bootstrap.Modal(modal, { backdrop: true, keyboard: true });
    }
    modalInstance.show();

    try {
        const response = await fetch(url, {
            method: 'GET',
            headers: { 'X-Requested-With': 'XMLHttpRequest' }
        });

        if (!response.ok) {
            throw new Error(`Error HTTP: ${response.status}`);
        }

        const html = await response.text();

        // Empujar la vista real a la pila
        pushModalView(title, html, size, '');

    } catch (error) {
        console.error('Error al cargar contenido del modal:', error);

        // Mostrar vista de error
        const errorContent = `
            <div class="alert alert-danger">
                <h5><i class="fas fa-exclamation-triangle"></i> Error al cargar</h5>
                <p>No se pudo cargar el contenido. ${error.message}</p>
                <button class="btn btn-outline-secondary btn-sm" onclick="popModalView()">
                    ← Volver
                </button>
            </div>
        `;
        pushModalView(title, errorContent, size, '');
    }
}
/**
 * Muestra el modal dinámico (con fallback si falla Bootstrap).
 */
function showDynamicModal() {
    const modal = document.getElementById('dynamicModal');
    if (!modal) {
        showCustomAlert('Error: Modal no encontrado.', 'danger');
        return Promise.reject(new Error('Modal element not found'));
    }

    return new Promise(resolve => {
        try {
            let instance = bootstrap.Modal.getInstance(modal);
            if (!instance) instance = new bootstrap.Modal(modal, { backdrop: true, keyboard: true });
            instance.show();
            resolve();
        } catch (error) {
            console.error('⚠️ Error con Bootstrap Modal:', error);
            // Fallback manual
            modal.classList.add('show');
            modal.style.display = 'block';
            document.body.classList.add('modal-open');
            if (!document.querySelector('.modal-backdrop')) {
                const backdrop = document.createElement('div');
                backdrop.className = 'modal-backdrop fade show';
                document.body.appendChild(backdrop);
            }
            resolve();
        }
    });
}

/**
 * Abre el modal para registrar un nuevo paper.
 */
async function openNewPaperModal() {
    try {
        await loadModalContent('/modal/new-paper/', 'Registrar Nuevo Paper', 'xl');
        setTimeout(() => {
            inicializarPalabrasClave();
            if (typeof cargarRoles === 'function') {
                cargarRoles().then(() => console.log('✅ Roles cargados.'));
            }
        }, 300);
    } catch (error) {
        console.error('❌ Error en openNewPaperModal:', error);
        showCustomAlert('No se pudo abrir el formulario.', 'danger');
    }
}

async function openNewAutorModal() {
    // Guarda el estado actual del formulario en la pila
    saveCurrentFormDataToStack();

    try {
        const response = await fetch('modal/new-author', {
            method: 'GET',
            headers: { 'X-Requested-With': 'XMLHttpRequest' }
        });
        if (!response.ok) {
            throw new Error(`Error HTTP: ${response.status}`);
        }
        const html = await response.text();
        pushModalView('Registrar nuevo author', html, 'md', '');
    } catch (error) {
        console.error('ERROR en openNewAutorModal:', error);
        showCustomAlert('No se pudo abrir el formulario.', 'danger');
    }
}


/**
 * Gestión de modales con vistas internas:
 * Esta sección permite que, desde un modal ya abierto se pueda abrir una sub-vista sin perder el estado del formulario principal y poder volver a él.
 * 
 * Primero se creará una variable global para almacenar el estado de los modales.
 * Constará del título de la vista, el html del cuerpo, el footer (opcional) y el tamaño del modal.
 * 
 */

/**
 * Agrega una nueva vista al modal dinámico y la muestra, guardando el estado actual en una pila para permitir navegación hacia atrás.
 *
 * @param {string} title - Título que se mostrará en el modal.
 * @param {string} content - Contenido HTML que se mostrará en el cuerpo del modal.
 * @param {string} [size=''] - Clase de tamaño para el modal (por ejemplo, 'modal-lg', 'modal-sm'). Opcional.
 * @param {string} [footer=''] - Contenido HTML para el pie del modal. Opcional.
 */
function pushModalView(title, content, size = '', footer = '') {
    console.log("Introduciendo la vista a la pila");
    const modal = document.getElementById('dynamicModal');
    if (!modal) {
        console.error('Modal no encontrado');
        return;
    }

    // Empujar la nueva vista a la pila
    window.PublishTracker.modalStack.push({
        title: title,
        content: content,
        footer: footer,
        size: size,
        formData: null // la nueva vista no tiene datos guardados aún
    });
    // Aplicar la nueva vista
    renderCurrentModalView();

    // Mostrar el modal si no está visible (por si acaso)
    let modalInstance = bootstrap.Modal.getInstance(modal);
    if (!modalInstance) {
        modalInstance = new bootstrap.Modal(modal, { backdrop: true, keyboard: true });
    }
    if (!modal.classList.contains('show')) {
        modalInstance.show();
    }
}

/**
 * Guarda el estado actual de los campos de entrada (ya sea dentro de un <form> o no) en la última vista de la pila.
 */
function saveCurrentFormDataToStack() {
    const currentBody = document.getElementById('modalBody');
    if (!currentBody || window.PublishTracker.modalStack.length === 0) {
        console.warn("No hay vista actual en la pila o no hay cuerpo.");
        return;
    }

    // Intenta encontrar un <form> como antes
    let form = currentBody.querySelector('form');

    // Si no hay un <form>, busca directamente los inputs dentro del cuerpo del modal
    let inputs;
    if (form) {
        inputs = form.querySelectorAll('input, select, textarea');
    } else {
        // Si no hay form, busca campos en el cuerpo del modal
        console.warn("No se encontró un <form> en la vista actual, buscando campos directamente en el cuerpo.");
        inputs = currentBody.querySelectorAll('input, select, textarea');
    }

    if (!inputs || inputs.length === 0) {
        console.warn("No se encontraron campos de entrada (<input>, <select>, <textarea>) en la vista actual.");
        // Aún así guardamos un objeto vacío para mantener la estructura de la pila
        const stack = window.PublishTracker.modalStack;
        const currentView = stack[stack.length - 1];
        currentView.formData = {};
        return;
    }

    const formData = {};
    inputs.forEach(input => {
        // Asegurarse de que el campo tenga un nombre para poder guardarlo
        if (input.name) {
            if (input.type === 'checkbox' || input.type === 'radio') {
                formData[input.name] = input.checked;
            } else {
                formData[input.name] = input.value;
            }
        } else {
            // Opcional: puedes elegir ignorar campos sin nombre o usar otro identificador
            console.warn(`Campo sin 'name' encontrado:`, input);
        }
    });

    // Guardar en la última entrada de la pila
    const stack = window.PublishTracker.modalStack;
    const currentView = stack[stack.length - 1];
    currentView.formData = formData;
    console.log("✅ Estado de campos guardado en la pila:", currentView.title, formData);
}
/**
 * Navega a una nueva vista, guardando el estado actual del formulario antes de salirf
 * @param {string} title - Título de la nueva vista.
 * @param {string} content - Contenido HTML de la nueva vista.
 * @param {string} [size=''] - Tamaño del modal.
 * @param {string} [footer=''] - Contenido del pie.
 */
async function goToModalView(url, title, size = '', footer = '') {
    const modal = document.getElementById('dynamicModal');
    if (!modal) {
        console.error('Modal no encontrado');
        return;
    }

    // Guarda el estado actual del formulario en la pila
    saveCurrentFormDataToStack();

    try {
        const response = await fetch(url, {
            method: 'GET',
            headers: { 'X-Requested-With': 'XMLHttpRequest' }
        });
        if (!response.ok) {
            throw new Error(`Error HTTP: ${response.status}`);
        }
        const content = await response.text();
        // Empuja la nueva vista usando pushModalView (sin formData porque es nueva)
        pushModalView(title, content, size, footer);
    } catch (error) {
        console.error('Error al cargar contenido del modal:', error);

        // Mostrar vista de error usando pushModalView
        const errorContent = `
            <div class="alert alert-danger">
                <h5><i class="fas fa-exclamation-triangle"></i> Error al cargar</h5>
                <p>No se pudo cargar el contenido. ${error.message}</p>
                <button class="btn btn-outline-secondary btn-sm" onclick="popModalView()">
                    ← Volver
                </button>
            </div>
        `;
        pushModalView(title, errorContent, size, '');
    }
}
/**
 * Elimina la vista actual del modal de la pila y muestra la vista anterior.
 * Si solo queda una vista en la pila, muestra una advertencia y no hace nada.
 *
 * @function
 * @returns {void}
 */
function popModalView() {
    console.log("Sacando la vista de la pila")
    if (window.PublishTracker.modalStack.length <= 1) {
        // Si solo queda una vista, cerrar el modal o no hacer nada
        console.warn('No hay vistas anteriores.');
        return;
    }

    window.PublishTracker.modalStack.pop(); // eliminar la vista actual
    renderCurrentModalView();
}

/**
 * Renderiza la vista actual del modal basada en el elemento superior de la pila de modales.
 * Actualiza el título, cuerpo, pie y tamaño del modal según la configuración actual del modal.
 * También reinicializa los componentes de Bootstrap (por ejemplo, tooltips) dentro del cuerpo del modal.
 *
 * Supone la siguiente estructura global:
 *   window.PublishTracker.modalStack: Array de objetos de configuración del modal, cada uno con:
 *      @param title: {string} Texto del título del modal.
 *      @param content: {string} Contenido HTML para el cuerpo del modal.
 *      @param footer: {string|undefined} Contenido HTML opcional para el pie del modal.
 *      @param size: {string} Clase de tamaño de modal de Bootstrap (por ejemplo, 'modal-lg').
 *
 * Elementos DOM esperados:
 *   - #modalTitle: Elemento para el título del modal.
 *   - #modalBody: Elemento para el contenido del cuerpo del modal.
 *   - #modalFooter: Elemento para el pie del modal.
 *   - #modalDialog: Elemento para el contenedor del diálogo del modal.
 */
/**
 * Renderiza la vista actual del modal basada en el elemento superior de la pila de modales.
 * Actualiza el título, cuerpo, pie y tamaño del modal según la configuración actual del modal.
 * También reinicializa los componentes de Bootstrap (por ejemplo, tooltips) dentro del cuerpo del modal.
 * Y restaura el estado de los campos de entrada si existe.
 *
 * Supone la siguiente estructura global:
 *   window.PublishTracker.modalStack: Array de objetos de configuración del modal, cada uno con:
 *      @param title: {string} Texto del título del modal.
 *      @param content: {string} Contenido HTML para el cuerpo del modal.
 *      @param footer: {string|undefined} Contenido HTML opcional para el pie del modal.
 *      @param size: {string} Clase de tamaño de modal de Bootstrap (por ejemplo, 'modal-lg').
 *      @param formData: {Object|undefined} Datos del formulario guardados anteriormente.
 *
 * Elementos DOM esperados:
 *   - #modalTitle: Elemento para el título del modal.
 *   - #modalBody: Elemento para el contenido del cuerpo del modal.
 *   - #modalFooter: Elemento para el pie del modal.
 *   - #modalDialog: Elemento para el contenedor del diálogo del modal.
 */
function renderCurrentModalView() {
    console.log("Renderizando la vista");
    const stack = window.PublishTracker.modalStack;
    if (stack.length === 0) return;
    const current = stack[stack.length - 1];
    const titleEl = document.getElementById('modalTitle');
    const bodyEl = document.getElementById('modalBody');
    const footerEl = document.getElementById('modalFooter');
    const dialogEl = document.getElementById('modalDialog');

    if (titleEl) titleEl.textContent = current.title;
    if (bodyEl) bodyEl.innerHTML = current.content; // Esto reemplaza el HTML, perdiendo el estado anterior
    if (footerEl) {
        footerEl.innerHTML = current.footer || '';
        footerEl.style.display = current.footer ? 'block' : 'none';
    }
    if (dialogEl) {
        dialogEl.className = 'modal-dialog';
        if (current.size) dialogEl.classList.add(`modal-${current.size}`);
    }

    // 🔑 RESTAURAR EL ESTADO DE LOS CAMPOS DE ENTRADA SI EXISTE formData
    console.log("Restaurando estado de campos (si corresponde)");
    if (current.formData && bodyEl) {
        // Buscar campos como lo hace saveCurrentFormDataToStack
        let form = bodyEl.querySelector('form');
        let inputs;
        if (form) {
            inputs = form.querySelectorAll('input, select, textarea');
        } else {
            inputs = bodyEl.querySelectorAll('input, select, textarea');
        }

        if (inputs && inputs.length > 0) {
            inputs.forEach(input => {
                if (input.name) { // Solo restaurar si el campo tiene un 'name'
                    const savedValue = current.formData[input.name];
                    if (savedValue !== undefined) {
                        if (input.type === 'checkbox' || input.type === 'radio') {
                            input.checked = savedValue;
                        } else {
                            input.value = savedValue;
                        }
                        console.log(`  - Campo '${input.name}' restaurado a:`, savedValue);
                    }
                }
            });
        } else {
            console.warn("No se encontraron campos para restaurar en la vista actual después de renderizar.");
        }
    }
}
/**
 * =========================
 * 4. GESTIÓN DE AUTORES
 * =========================
 */

let autoresSeleccionadosTemporal = [];
let rolesDisponibles = [];

async function cargarRoles() {
    try {
        const res = await fetch('/authors/api/roles/');
        const data = await res.json();
        if (data.success) rolesDisponibles = data.roles;
        console.log(rolesDisponibles)
    } catch (err) {
        console.error('Error al cargar roles:', err);
    }
}

function buscarAutorLocal() {
    const query = document.getElementById('buscarAutor')?.value.trim().toLowerCase();
    if (!query) {
        showCustomAlert('Ingrese un nombre o ORCID.');
        return;
    }

    const filas = document.querySelectorAll('#autoresDisponibles tr');
    let encontrados = 0;
    filas.forEach(fila => {
        const nombre = fila.querySelector('td:first-child')?.textContent.toLowerCase() || '';
        const orcid = fila.querySelector('td:nth-child(2)')?.textContent.toLowerCase() || '';
        if (nombre.includes(query) || orcid.includes(query)) {
            fila.style.display = '';
            encontrados++;
        } else {
            fila.style.display = 'none';
        }
    });

    if (encontrados === 0) showCustomAlert('No se encontraron autores.');
}

function agregarAutorSeleccionadoLocal(autorId, nombre, orcid) {
    if (autoresSeleccionadosTemporal.some(a => a.autor_id === autorId)) {
        showCustomAlert('Autor ya seleccionado.');
        return;
    }

    autoresSeleccionadosTemporal.push({
        autor_id: autorId,
        nombre,
        orcid,
        orden: autoresSeleccionadosTemporal.length + 1,
        rol_id: null
    });

    actualizarTablaAutoresSeleccionados();
    document.querySelector(`#autoresDisponibles tr[data-autor-id="${autorId}"]`)?.style.setProperty('display', 'none');
    document.getElementById('autoresSeleccionadosData')?.setAttribute('value', JSON.stringify(autoresSeleccionadosTemporal));
}

function eliminarAutorSeleccionadoLocal(autorId) {
    autoresSeleccionadosTemporal = autoresSeleccionadosTemporal.filter(a => a.autor_id !== autorId);
    autoresSeleccionadosTemporal.forEach((a, i) => a.orden = i + 1);
    actualizarTablaAutoresSeleccionados();
    document.querySelector(`#autoresDisponibles tr[data-autor-id="${autorId}"]`)?.style.removeProperty('display');
    document.getElementById('autoresSeleccionadosData')?.setAttribute('value', JSON.stringify(autoresSeleccionadosTemporal));
}

function actualizarTablaAutoresSeleccionados() {
    const tbody = document.getElementById('autoresSeleccionados');
    if (!tbody) return;

    const rolOptions = rolesDisponibles.map(r => `<option value="${r.id}">${r.nombre_rol}</option>`).join('');
    tbody.innerHTML = autoresSeleccionadosTemporal.map(autor => `
        <tr data-autor-id="${autor.autor_id}">
            <td>${autor.nombre}</td>
            <td>${autor.orcid}</td>
            <td><input type="number" class="form-control form-control-sm" value="${autor.orden}" min="1" onchange="actualizarOrdenAutor(${autor.autor_id}, this.value)"></td>
            <td>
                <select class="form-select form-select-sm" onchange="actualizarRolAutor(${autor.autor_id}, this.value)">
                    <option value="">Seleccionar rol</option>
                    ${rolOptions}
                    ${autor.rol_id ? `<option value="${autor.rol_id}" selected>Seleccionado</option>` : ''}
                </select>
            </td>
            <td><button type="button" class="btn btn-sm btn-danger" onclick="eliminarAutorSeleccionadoLocal(${autor.autor_id})"><i class="fas fa-trash"></i></button></td>
        </tr>
    `).join('');
}

function actualizarRolAutor(autorId, rolId) {
    const autor = autoresSeleccionadosTemporal.find(a => a.autor_id === autorId);
    if (autor) {
        autor.rol_id = rolId || null;
        document.getElementById('autoresSeleccionadosData')?.setAttribute('value', JSON.stringify(autoresSeleccionadosTemporal));
    }
}

function actualizarOrdenAutor(autorId, nuevoOrden) {
    const autor = autoresSeleccionadosTemporal.find(a => a.autor_id === autorId);
    if (autor) {
        autor.orden = parseInt(nuevoOrden, 10);
        autoresSeleccionadosTemporal.sort((a, b) => a.orden - b.orden);
        actualizarTablaAutoresSeleccionados();
        document.getElementById('autoresSeleccionadosData')?.setAttribute('value', JSON.stringify(autoresSeleccionadosTemporal));
    }
}

/**
 * =========================
 * 5. GESTIÓN DE PALABRAS CLAVE
 * =========================
 */

window.palabrasClaveSeleccionadas = [];
window.palabrasClaveDisponibles = [];

async function cargarPalabrasClaveViaAjax() {
    try {
        const res = await fetch('/api/palabras-clave/');
        const data = await res.json();
        if (data.success) window.palabrasClaveDisponibles = data.palabras_clave;
        console.log(palabrasClaveDisponibles)
    } catch (err) {
        console.error('Error al cargar palabras clave:', err);
    }
}

function mostrarPalabrasClaveDisponibles() {
    const container = document.getElementById('palabrasClaveDisponibles');
    if (!container) return;

    container.innerHTML = '';
    window.palabrasClaveDisponibles.forEach(palabra => {
        const yaSel = window.palabrasClaveSeleccionadas.some(p =>
            (p.id && p.id === palabra.id) || (p.nombre === palabra.nombre)
        );
        if (!yaSel) {
            const span = document.createElement('span');
            span.className = 'badge bg-secondary me-1 mb-1';
            span.style.cursor = 'pointer';
            span.textContent = palabra.nombre;
            span.onclick = () => seleccionarPalabraClave(palabra);
            container.appendChild(span);
        }
    });
}

function seleccionarPalabraClave(palabra) {
    const yaSel = window.palabrasClaveSeleccionadas.some(p =>
        (p.id && p.id === palabra.id) || (p.nombre === palabra.nombre)
    );
    if (yaSel) {
        showCustomAlert('Palabra clave ya seleccionada.');
        return;
    }
    window.palabrasClaveSeleccionadas.push({ id: palabra.id, nombre: palabra.nombre });
    actualizarPalabrasClaveSeleccionadas();
    mostrarPalabrasClaveDisponibles();
    document.getElementById('palabrasClaveData')?.setAttribute('value', JSON.stringify(window.palabrasClaveSeleccionadas));
}

function agregarNuevaPalabraClave() {
    const input = document.getElementById('palabrasClaveInput');
    if (!input) return;
    const valor = input.value.trim();
    if (!valor) {
        showCustomAlert('Ingrese una palabra clave.');
        return;
    }

    const existe = window.palabrasClaveDisponibles.some(p => p.nombre.toLowerCase() === valor.toLowerCase());
    const yaSel = window.palabrasClaveSeleccionadas.some(p => p.nombre.toLowerCase() === valor.toLowerCase());

    if (existe) {
        showCustomAlert('Ya existe. Selecciónela de la lista.');
        return;
    }
    if (yaSel) {
        showCustomAlert('Ya está seleccionada.');
        return;
    }

    window.palabrasClaveSeleccionadas.push({ id: null, nombre: valor });
    actualizarPalabrasClaveSeleccionadas();
    input.value = '';
    document.getElementById('palabrasClaveData')?.setAttribute('value', JSON.stringify(window.palabrasClaveSeleccionadas));
}

function actualizarPalabrasClaveSeleccionadas() {
    const container = document.getElementById('palabrasClaveSeleccionadas');
    if (!container) return;

    container.innerHTML = window.palabrasClaveSeleccionadas.map((p, i) => `
        <span class="badge bg-primary me-1 mb-1">
            ${p.nombre}
            <button type="button" class="btn-close btn-close-white" aria-label="Eliminar" 
                    onclick="eliminarPalabraClaveSeleccionada(${i})" style="font-size:0.5em;"></button>
        </span>
    `).join('');
}

function eliminarPalabraClaveSeleccionada(index) {
    window.palabrasClaveSeleccionadas.splice(index, 1);
    actualizarPalabrasClaveSeleccionadas();
    mostrarPalabrasClaveDisponibles();
    document.getElementById('palabrasClaveData')?.setAttribute('value', JSON.stringify(window.palabrasClaveSeleccionadas));
}

function inicializarPalabrasClave() {
    cargarPalabrasClaveViaAjax().then(() => {
        setTimeout(mostrarPalabrasClaveDisponibles, 100);
    });
}

/**
 * =========================
 * 6. FUNCIONES DE NEGOCIO
 * =========================
 */

/**
 * Guarda un nuevo paper con validaciones y envío al servidor.
 */
async function guardarPaper() {
    // --- Recolección y validación de datos ---
    const fields = {
        titulo: document.getElementById('tituloPaper')?.value.trim(),
        anio: document.getElementById('anioPublicacion')?.value,
        estatus: document.getElementById('estatusPublicacion')?.value,
        revista: document.getElementById('revistaSelect')?.value,
        volumen: document.getElementById('volumenRevista')?.value.trim(),
        numero: document.getElementById('numeroRevista')?.value.trim(),
        indiceRevista: document.getElementById('indiceRevista')?.value.trim(),
        doi: document.getElementById('doiPaper')?.value.trim(),
        urlCita: document.getElementById('urlCita')?.value.trim(),
        totalCitas: document.getElementById('totalCitas')?.value,
        paginaInicio: document.getElementById('paginaInicio')?.value,
        paginaFin: document.getElementById('paginaFin')?.value,
        objetivo: document.getElementById('objetivoPaper')?.value.trim(),
        descripcion: document.getElementById('descripcionPaper')?.value.trim(),
        abstract: document.getElementById('abstractPaper')?.value.trim(),
        apoyoSECITI: document.getElementById('apoyoSECITI')?.checked,
        programaSECITI: document.getElementById('programaSECITI')?.value,
        ejeSECITHI: document.getElementById('ejeSECITHI')?.value
    };

    // Validaciones básicas
    const required = ['titulo', 'anio', 'estatus', 'revista', 'volumen', 'numero', 'indiceRevista', 'doi', 'urlCita', 'objetivo', 'descripcion', 'abstract'];
    for (const key of required) {
        if (!fields[key]) {
            showCustomAlert(`El campo "${key.replace(/([A-Z])/g, ' $1').toLowerCase()}" es requerido.`, 'danger');
            return;
        }
    }

    // Validaciones numéricas
    if (isNaN(fields.totalCitas) || fields.totalCitas < 0) {
        showCustomAlert('Total de citas debe ser un número válido.', 'danger'); return;
    }
    if (isNaN(fields.paginaInicio) || fields.paginaInicio <= 0) {
        showCustomAlert('Página de inicio debe ser un número positivo.', 'danger'); return;
    }
    if (isNaN(fields.paginaFin) || fields.paginaFin <= 0) {
        showCustomAlert('Página final debe ser un número positivo.', 'danger'); return;
    }
    if (parseInt(fields.paginaInicio) > parseInt(fields.paginaFin)) {
        showCustomAlert('Página de inicio no puede ser mayor que la final.', 'danger'); return;
    }

    // Validaciones de relaciones
    if (autoresSeleccionadosTemporal.length === 0) {
        showCustomAlert('Debe seleccionar al menos un autor.', 'danger'); return;
    }
    if (autoresSeleccionadosTemporal.some(a => !a.rol_id)) {
        showCustomAlert('Todos los autores deben tener un rol asignado.', 'danger'); return;
    }
    if (window.palabrasClaveSeleccionadas.length === 0) {
        showCustomAlert('Debe agregar al menos una palabra clave.', 'danger'); return;
    }

    if (fields.apoyoSECITI && (!fields.programaSECITI || !fields.ejeSECITHI)) {
        showCustomAlert('Si hay apoyo SECITI, debe seleccionar programa y eje.', 'danger'); return;
    }

    // Archivos
    const archivoPaper = document.getElementById('archivoPaper')?.files[0];
    const primeraPagina = document.getElementById('primeraPagina')?.files[0];
    if (!archivoPaper) { showCustomAlert('Debe adjuntar el archivo del paper.', 'danger'); return; }
    if (!primeraPagina) { showCustomAlert('Debe adjuntar la primera página.', 'danger'); return; }

    // Generar referencia APA
    const nombreRevista = document.querySelector('#revistaSelect option:checked')?.textContent || '';
    const referenciaAPA = generarReferenciaAPA({
        titulo: fields.titulo,
        anio: fields.anio,
        nombreRevista,
        volumen: fields.volumen,
        numero: fields.numero,
        paginaInicio: fields.paginaInicio,
        paginaFin: fields.paginaFin,
        doi: fields.doi
    });

    // --- Preparar FormData ---
    const formData = new FormData();
    Object.entries(fields).forEach(([key, value]) => {
        if (key === 'apoyoSECITI') {
            formData.append('recibio_apoyo_seciti', value ? 'true' : 'false');
        } else {
            formData.append(key.replace(/([A-Z])/g, '_$1').toLowerCase(), value);
        }
    });
    formData.append('referencia_apa', referenciaAPA);
    formData.append('autores', JSON.stringify(autoresSeleccionadosTemporal));
    formData.append('palabras_clave', JSON.stringify(window.palabrasClaveSeleccionadas));
    if (archivoPaper) formData.append('archivo_paper', archivoPaper);
    if (primeraPagina) formData.append('primera_pagina', primeraPagina);

    // --- Crear palabras clave nuevas si es necesario ---
    const palabrasNuevas = window.palabrasClaveSeleccionadas.filter(p => !p.id && !window.palabrasClaveDisponibles.some(d => d.nombre.toLowerCase() === p.nombre.toLowerCase()));
    for (const palabra of palabrasNuevas) {
        try {
            const res = await fetch('/api/palabras-clave/create/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': window.PublishTracker.csrfToken,
                    'X-Requested-With': 'XMLHttpRequest'
                },
                body: JSON.stringify({ nombre: palabra.nombre.toLowerCase() })
            });
            const data = await res.json();
            if (data.success && data.palabra_clave) {
                palabra.id = data.palabra_clave.id;
                palabra.nombre = data.palabra_clave.nombre;
                window.palabrasClaveDisponibles.push(data.palabra_clave);
            }
        } catch (err) {
            console.warn('No se pudo crear palabra clave:', palabra.nombre);
        }
    }

    // --- Enviar al servidor ---
    try {
        const response = await fetch('/publications/create/', {
            method: 'POST',
            headers: {
                'X-CSRFToken': window.PublishTracker.csrfToken,
                'X-Requested-With': 'XMLHttpRequest'
            },
            body: formData
        });
        const data = await response.json();

        if (!response.ok) throw new Error(data.message || 'Error al guardar.');
        if (data.success) {
            showCustomAlert('✅ Paper guardado correctamente.', 'success');
            setTimeout(() => {
                bootstrap.Modal.getInstance(document.getElementById('dynamicModal'))?.hide();
                window.location.reload();
            }, 1500);
        } else {
            throw new Error(data.message || 'Error desconocido.');
        }
    } catch (error) {
        console.error('Error al guardar el paper:', error);
        showCustomAlert(`❌ ${error.message}`, 'danger');
    }
}

/**
 * Genera una referencia en formato APA.
 */
function generarReferenciaAPA(data) {
    const autores = autoresSeleccionadosTemporal
        .sort((a, b) => a.orden - b.orden)
        .map(a => a.nombre);

    let citaAutores = '';
    if (autores.length === 1) citaAutores = autores[0];
    else if (autores.length === 2) citaAutores = `${autores[0]} & ${autores[1]}`;
    else if (autores.length > 2) citaAutores = `${autores[0]} et al.`;

    const volumenNumero = data.volumen && data.numero ? `${data.volumen}(${data.numero})` : (data.volumen || '');
    const paginas = data.paginaInicio ? `, ${data.paginaInicio}${data.paginaFin ? `-${data.paginaFin}` : ''}` : '';

    return `${citaAutores}. (${data.anio}). ${data.titulo}. ${data.nombreRevista}${volumenNumero ? `, ${volumenNumero}` : ''}${paginas}.${data.doi ? ` https://doi.org/${data.doi}` : ''}`;
}

/**
 * =========================
 * 7. FUNCIONALIDADES PENDIENTES
 * =========================
 */

function viewPaper() { showCustomAlert('Funcionalidad no implementada.', 'warning'); }
function editPaper() { showCustomAlert('Funcionalidad no implementada.', 'warning'); }
function generateReport() { showCustomAlert('Funcionalidad no implementada.', 'warning'); }