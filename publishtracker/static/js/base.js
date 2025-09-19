// static/js/base.js

document.addEventListener('DOMContentLoaded', function() {
    // Configuración global
    window.PublishTracker = {
        csrfToken: getCookie('csrftoken'),
        baseUrl: window.location.origin
    };

    // Auto-submit en filtros
    const filterSelects = document.querySelectorAll('select[name="status"], select[name="year"]');
    filterSelects.forEach(select => {
        select.addEventListener('change', function() {
            this.closest('form').submit();
        });
    });

    // Inicializar tooltips de Bootstrap
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
});

// Función helper para obtener CSRF token
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// Funciones globales de utilidad
function showAlert(message, type = 'info') {
    // Implementar sistema de alertas
    console.log(`${type.toUpperCase()}: ${message}`);
}

function showLoading(element) {
    element.classList.add('loading');
}

function hideLoading(element) {
    element.classList.remove('loading');
}

// Funciones para manejo de modales - VERSIÓN ACTUALIZADA
function openDynamicModal(title, content, size = '', footer = '') {
    const modalElement = document.getElementById('dynamicModal');
    
    if (!modalElement) {
        console.error('No se encontró el elemento del modal');
        return;
    }

    const modalDialog = document.getElementById('modalDialog');
    const modalTitle = document.getElementById('modalTitle');
    const modalBody = document.getElementById('modalBody');
    const modalFooter = document.getElementById('modalFooter');

    // Limpiar clases de tamaño anteriores
    if (modalDialog) {
        modalDialog.className = 'modal-dialog';
        if (size) {
            modalDialog.classList.add(`modal-${size}`);
        }
    }

    // Actualizar contenido
    if (modalTitle) {
        modalTitle.textContent = title;
    }
    
    if (modalBody) {
        modalBody.innerHTML = content;
    }

    // Opcional: actualizar footer
    if (modalFooter) {
        if (footer) {
            modalFooter.innerHTML = footer;
            modalFooter.style.display = 'block';
        } else {
            modalFooter.style.display = 'none';
        }
    }

    // Crear y mostrar el modal con opciones explícitas
    try {
        const modal = new bootstrap.Modal(modalElement, {
            backdrop: 'static',
            keyboard: true
        });
        modal.show();
    } catch (error) {
        console.error('Error al crear o mostrar el modal:', error);
        // Fallback: intentar mostrar con el método data-api de Bootstrap
        modalElement.classList.add('show');
        modalElement.style.display = 'block';
        document.body.classList.add('modal-open');
    }
}

console.log('base.js cargado correctamente');

/**
 * Carga contenido HTML en el modal dinámico y lo muestra.
 * @param {string} url - La URL para obtener el contenido HTML.
 * @param {string} title - El título del modal.
 * @param {string} [size=''] - El tamaño del modal (e.g., 'sm', 'lg', 'xl').
 */
function loadModalContent(url, title, size = '') {
    const modalElement = document.getElementById('dynamicModal');
    const modalTitle = document.getElementById('dynamicModalLabel');
    const modalBody = document.getElementById('modalBodyContent');
    const modalFooter = document.getElementById('modalFooterContent');
    const modalDialog = document.getElementById('modalDialog');

    if (!modalElement || !modalTitle || !modalBody) {
        console.error('Elementos del modal no encontrados en el DOM.');
        alert('Error: No se pudo preparar el modal.');
        return;
    }

    // Mostrar un indicador de carga
    modalBody.innerHTML = '<div class="text-center"><div class="spinner-border" role="status"><span class="visually-hidden">Cargando...</span></div></div>';
    modalFooter.style.display = 'none'; // Ocultar footer por defecto

    // Limpiar clases de tamaño anteriores y aplicar la nueva
    modalDialog.className = 'modal-dialog';
    if (size) {
        modalDialog.classList.add(`modal-${size}`);
    } else {
        modalDialog.classList.add('modal-xl'); // Tamaño por defecto
    }

    // Establecer el título
    modalTitle.textContent = title;

    // Cargar el contenido vía fetch
    fetch(url, {
        method: 'GET',
        headers: {
            'X-Requested-With': 'XMLHttpRequest',
        }
    })
    .then(response => {
        if (!response.ok) {
            if (response.status === 404) {
                throw new Error('Página no encontrada (404)');
            } else if (response.status === 500) {
                throw new Error('Error interno del servidor (500)');
            } else {
                throw new Error(`Error HTTP: ${response.status}`);
            }
        }
        return response.text();
    })
    .then(html => {
        modalBody.innerHTML = html;
    })
    .catch(error => {
        console.error('Error al cargar el contenido del modal:', error);
        modalBody.innerHTML = `<div class="alert alert-danger">No se pudo cargar el contenido. Error: ${error.message}</div>`;
    });
}

/**
 * Muestra el modal dinámico usando la API de Bootstrap.
 */
function showDynamicModal() {
    const modalElement = document.getElementById('dynamicModal');
    if (!modalElement) {
        console.error('❌ No se encontró el elemento del modal para mostrarlo.');
        alert('Error: No se pudo mostrar el modal.');
        return Promise.reject(new Error('Modal element not found'));
    }

    return new Promise((resolve) => {
        try {
            // Intentar obtener la instancia existente o crear una nueva
            let modalInstance = bootstrap.Modal.getInstance(modalElement);
            if (!modalInstance) {
                console.log("Creando nueva instancia de modal...");
                modalInstance = new bootstrap.Modal(modalElement, {
                    backdrop: true,
                    keyboard: true
                });
            } else {
                console.log("Usando instancia existente del modal.");
            }
            modalInstance.show();
            resolve();
        } catch (error) {
            console.error('⚠️ Error al instanciar/mostrar el modal con Bootstrap:', error);
            // Fallback: disparar el evento manualmente si Bootstrap falla
            console.log("Intentando fallback para mostrar el modal...");
            modalElement.classList.add('show');
            modalElement.style.display = 'block';
            document.body.classList.add('modal-open');
            // Crear un backdrop manual si es necesario
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
 * Función específica para abrir el modal de nuevo paper.
 */
async function openNewPaperModal() {
    try {
        // 1. Cargar el contenido en el modal
        await loadModalContent('/modal/new-paper/', 'Registrar Nuevo Paper', 'xl');
        
        // 2. Mostrar el modal
        await showDynamicModal();
        
        // 3. Inicializar componentes del modal después de que se muestre
        setTimeout(() => {
            // Inicializar palabras clave
            inicializarPalabrasClave();
            
            // Inicializar roles si es necesario
            if (typeof cargarRoles === 'function') {
                cargarRoles().then(() => {
                    console.log("Roles cargados correctamente");
                });
            }
        }, 300); // Pequeño retraso para asegurar que el DOM esté listo
        
    } catch (error) {
        console.error('❌ Error en openNewPaperModal:', error);
        showDynamicModal().catch(err => console.error('❌ Error al mostrar modal de error:', err));
    }
}

// Array para almacenar autores seleccionados temporalmente
let autoresSeleccionadosTemporal = [];
let rolesDisponibles = []; // Array para almacenar roles cargados

// Función para cargar roles desde la API
async function cargarRoles() {
    try {
        const response = await fetch('/authors/api/roles/');
        const data = await response.json();
        if (data.success) {
            rolesDisponibles = data.roles;
            console.log("Roles cargados:", rolesDisponibles);
        }
    } catch (error) {
        console.error('Error al cargar roles:', error);
    }
}

// Función para buscar autores localmente (en la lista ya cargada)
function buscarAutorLocal() {
    const query = document.getElementById('buscarAutor').value.trim().toLowerCase();
    if (!query) {
        alert("Por favor, ingrese un nombre o ORCID.");
        return;
    }

    const filasDisponibles = document.querySelectorAll('#autoresDisponibles tr');
    let encontrados = 0;

    filasDisponibles.forEach(fila => {
        const nombre = fila.querySelector('td:first-child').textContent.toLowerCase();
        const orcid = fila.querySelector('td:nth-child(2)').textContent.toLowerCase();
        
        if (nombre.includes(query) || orcid.includes(query)) {
            fila.style.display = '';
            encontrados++;
        } else {
            fila.style.display = 'none';
        }
    });

    if (encontrados === 0) {
        alert("No se encontraron autores con ese criterio.");
    }
}

// Función para agregar un autor a la lista de seleccionados (local)
function agregarAutorSeleccionadoLocal(autorId, nombre, orcid) {
    console.log("Agregando autor:", autorId, nombre, orcid);
    
    // Verificar si ya está seleccionado
    const yaSeleccionado = autoresSeleccionadosTemporal.some(autor => autor.autor_id === autorId);
    if (yaSeleccionado) {
        alert("Este autor ya está seleccionado.");
        return;
    }

    // Agregar al array temporal
    const nuevoAutor = {
        autor_id: autorId,
        nombre: nombre,
        orcid: orcid,
        orden: autoresSeleccionadosTemporal.length + 1,
        rol_id: null // ID del rol seleccionado
    };
    autoresSeleccionadosTemporal.push(nuevoAutor);

    // Actualizar tabla visual
    actualizarTablaAutoresSeleccionados();

    // Ocultar de la lista disponible
    const filaDisponible = document.querySelector(`#autoresDisponibles tr[data-autor-id="${autorId}"]`);
    if (filaDisponible) {
        filaDisponible.style.display = 'none';
    }

    // Actualizar campo oculto
    document.getElementById('autoresSeleccionadosData').value = JSON.stringify(autoresSeleccionadosTemporal);
    console.log("Autores seleccionados:", autoresSeleccionadosTemporal);
}

// Función para eliminar un autor de la lista de seleccionados
function eliminarAutorSeleccionadoLocal(autorId) {
    console.log("Eliminando autor:", autorId);
    
    // Eliminar del array temporal
    autoresSeleccionadosTemporal = autoresSeleccionadosTemporal.filter(autor => autor.autor_id !== autorId);

    // Reordenar
    autoresSeleccionadosTemporal.forEach((autor, index) => {
        autor.orden = index + 1;
    });

    // Actualizar tabla visual
    actualizarTablaAutoresSeleccionados();

    // Mostrar nuevamente en la lista disponible
    const filaDisponible = document.querySelector(`#autoresDisponibles tr[data-autor-id="${autorId}"]`);
    if (filaDisponible) {
        filaDisponible.style.display = '';
    }

    // Actualizar campo oculto
    document.getElementById('autoresSeleccionadosData').value = JSON.stringify(autoresSeleccionadosTemporal);
    console.log("Autores seleccionados después de eliminar:", autoresSeleccionadosTemporal);
}

// Función para actualizar la tabla visual de autores seleccionados
function actualizarTablaAutoresSeleccionados() {
    const tbody = document.getElementById('autoresSeleccionados');
    tbody.innerHTML = '';

    // Crear opciones de roles
    let rolOptions = '<option value="">Seleccionar rol</option>';
    rolesDisponibles.forEach(rol => {
        rolOptions += `<option value="${rol.id}">${rol.nombre_rol}</option>`;
    });

    autoresSeleccionadosTemporal.forEach(autor => {
        const fila = document.createElement('tr');
        fila.setAttribute('data-autor-id', autor.autor_id);
        
        fila.innerHTML = `
            <td>${autor.nombre}</td>
            <td>${autor.orcid}</td>
            <td><input type="number" class="form-control form-control-sm" value="${autor.orden}" min="1" onchange="actualizarOrdenAutor(${autor.autor_id}, this.value)"></td>
            <td>
                <select class="form-select form-select-sm" onchange="actualizarRolAutor(${autor.autor_id}, this.value)">
                    ${rolOptions}
                    ${autor.rol_id ? `<option value="${autor.rol_id}" selected>Seleccionado</option>` : ''}
                </select>
            </td>
            <td>
                <button type="button" class="btn btn-sm btn-danger" onclick="eliminarAutorSeleccionadoLocal(${autor.autor_id})">
                    <i class="fas fa-trash"></i>
                </button>
            </td>
        `;
        tbody.appendChild(fila);
    });
}

// Función para actualizar el rol de un autor
function actualizarRolAutor(autorId, nuevoRolId) {
    const autor = autoresSeleccionadosTemporal.find(a => a.autor_id === autorId);
    if (autor) {
        autor.rol_id = nuevoRolId || null;
        document.getElementById('autoresSeleccionadosData').value = JSON.stringify(autoresSeleccionadosTemporal);
    }
}

// Función para actualizar el orden de un autor
function actualizarOrdenAutor(autorId, nuevoOrden) {
    const autor = autoresSeleccionadosTemporal.find(a => a.autor_id === autorId);
    if (autor) {
        autor.orden = parseInt(nuevoOrden);
        // Reordenar el array
        autoresSeleccionadosTemporal.sort((a, b) => a.orden - b.orden);
        actualizarTablaAutoresSeleccionados();
        document.getElementById('autoresSeleccionadosData').value = JSON.stringify(autoresSeleccionadosTemporal);
    }
}

// Función para obtener los autores seleccionados (para usar en guardarPaper)
function getAutoresSeleccionados() {
    return autoresSeleccionadosTemporal;
}

// Funciones para manejar la lógica del acordeón
function openAutoresModal() {
    openDynamicModal('Seleccionar Autores', '<p>Contenido para seleccionar autores.</p>', 'lg');
}

function guardarPaper() {
    alert('Funcionalidad de guardar paper aún no implementada.');
}

// Variables globales para palabras clave
window.palabrasClaveSeleccionadas = [];
window.palabrasClaveDisponibles = [];

/**
 * Cargar palabras clave vía AJAX
 */
async function cargarPalabrasClaveViaAjax() {
    try {
        const response = await fetch('/api/palabras-clave/');
        const data = await response.json();
        if (data.success) {
            window.palabrasClaveDisponibles = data.palabras_clave;
            console.log("Palabras clave cargadas vía AJAX:", window.palabrasClaveDisponibles);
        }
    } catch (error) {
        console.error('Error al cargar palabras clave vía AJAX:', error);
    }
}

/**
 * Mostrar palabras clave disponibles en la interfaz
 */
function mostrarPalabrasClaveDisponibles() {
    const container = document.getElementById('palabrasClaveDisponibles');
    if (!container) {
        console.log("Contenedor de palabras clave no encontrado en el DOM");
        return;
    }
    
    container.innerHTML = '';
    
    window.palabrasClaveDisponibles.forEach(palabra => {
        // Verificar si ya está seleccionada
        const yaSeleccionada = window.palabrasClaveSeleccionadas.some(p => 
            (p.id && p.id === palabra.id) || (p.nombre && p.nombre === palabra.nombre)
        );
        
        if (!yaSeleccionada) {
            const span = document.createElement('span');
            span.className = 'badge bg-secondary';
            span.style.cursor = 'pointer';
            span.style.margin = '2px';
            span.innerHTML = `${palabra.nombre}`;
            span.onclick = () => seleccionarPalabraClave(palabra);
            container.appendChild(span);
        }
    });
}

/**
 * Seleccionar una palabra clave existente
 */
function seleccionarPalabraClave(palabra) {
    // Verificar si ya está seleccionada
    const yaSeleccionada = window.palabrasClaveSeleccionadas.some(p => 
        (p.id && p.id === palabra.id) || (p.nombre && p.nombre === palabra.nombre)
    );
    
    if (yaSeleccionada) {
        alert("Esta palabra clave ya está seleccionada.");
        return;
    }
    
    // Agregar al array de seleccionadas
    window.palabrasClaveSeleccionadas.push({
        id: palabra.id,
        nombre: palabra.nombre
    });
    
    // Actualizar visualización
    actualizarPalabrasClaveSeleccionadas();
    mostrarPalabrasClaveDisponibles();
    
    // Actualizar campo oculto
    const hiddenInput = document.getElementById('palabrasClaveData');
    if (hiddenInput) {
        hiddenInput.value = JSON.stringify(window.palabrasClaveSeleccionadas);
    }
}

/**
 * Agregar una nueva palabra clave
 */
function agregarNuevaPalabraClave() {
    const input = document.getElementById('palabrasClaveInput');
    if (!input) return;
    
    const valor = input.value.trim();
    
    if (!valor) {
        alert("Por favor, ingrese una palabra clave.");
        return;
    }
    
    // Verificar si ya existe
    const existe = window.palabrasClaveDisponibles.some(p => p.nombre.toLowerCase() === valor.toLowerCase());
    if (existe) {
        alert("Esta palabra clave ya existe en la lista disponible. Selecciónela de la lista.");
        return;
    }
    
    // Verificar si ya está seleccionada
    const yaSeleccionada = window.palabrasClaveSeleccionadas.some(p => p.nombre.toLowerCase() === valor.toLowerCase());
    if (yaSeleccionada) {
        alert("Esta palabra clave ya está seleccionada.");
        return;
    }
    
    // Agregar como nueva palabra clave
    window.palabrasClaveSeleccionadas.push({
        id: null, // null indica que es nueva
        nombre: valor
    });
    
    // Actualizar visualización
    actualizarPalabrasClaveSeleccionadas();
    input.value = '';
    
    // Actualizar campo oculto
    const hiddenInput = document.getElementById('palabrasClaveData');
    if (hiddenInput) {
        hiddenInput.value = JSON.stringify(window.palabrasClaveSeleccionadas);
    }
}

/**
 * Actualizar la visualización de palabras clave seleccionadas
 */
function actualizarPalabrasClaveSeleccionadas() {
    const container = document.getElementById('palabrasClaveSeleccionadas');
    if (!container) return;
    
    container.innerHTML = '';
    
    window.palabrasClaveSeleccionadas.forEach((palabra, index) => {
        const span = document.createElement('span');
        span.className = 'badge bg-primary';
        span.style.margin = '2px';
        span.innerHTML = `
            ${palabra.nombre} 
            <button type="button" class="btn-close btn-close-white" aria-label="Eliminar" 
                    onclick="eliminarPalabraClaveSeleccionada(${index})" style="font-size: 0.5em;"></button>
        `;
        container.appendChild(span);
    });
}

/**
 * Eliminar una palabra clave seleccionada
 */
function eliminarPalabraClaveSeleccionada(index) {
    window.palabrasClaveSeleccionadas.splice(index, 1);
    actualizarPalabrasClaveSeleccionadas();
    mostrarPalabrasClaveDisponibles();
    
    // Actualizar campo oculto
    const hiddenInput = document.getElementById('palabrasClaveData');
    if (hiddenInput) {
        hiddenInput.value = JSON.stringify(window.palabrasClaveSeleccionadas);
    }
}

/**
 * Obtener palabras clave seleccionadas
 */
function getPalabrasClaveSeleccionadas() {
    return window.palabrasClaveSeleccionadas;
}

/**
 * Inicializar el sistema de palabras clave
 */
function inicializarPalabrasClave() {
    cargarPalabrasClaveViaAjax().then(() => {
        setTimeout(() => {
            mostrarPalabrasClaveDisponibles();
        }, 100);
    });
}