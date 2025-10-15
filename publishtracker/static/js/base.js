/**
 * PublishTracker - Sistema de Gestión de Publicaciones Académicas
 * Versión refactorizada con docstrings estilo "Pasos" y comentarios numerados
 * @author Edwin Campos Dragusin
 * @version 2.0.2
 */

// =============================================================================
// MÓDULO DE UTILIDADES
// =============================================================================

/**
 * Módulo de utilidades generales para operaciones comunes
 * Pasos:
 * 1. Exponer helpers de cookies, toasts y validaciones
 * 2. Mantener API estable para otros módulos
 */
const Utils = {
  /**
   * Obtener el valor de una cookie por nombre.
   * Pasos:
   * 1. Verificar que existan cookies
   * 2. Dividir el string en cookies individuales
   * 3. Buscar coincidencia nombre=valor
   * 4. Decodificar y retornar, o null si no existe
   */
  getCookie(name) {
    // 1. Verificar que existan cookies
    if (!document.cookie) return null;

    // 2. Dividir el string en cookies individuales
    const cookies = document.cookie.split(';');

    // 3. Buscar coincidencia nombre=valor
    for (let cookie of cookies) {
      cookie = cookie.trim();
      if (cookie.startsWith(`${name}=`)) {
        // 4. Decodificar y retornar, o null si no existe
        return decodeURIComponent(cookie.substring(name.length + 1));
      }
    }
    return null;
  },

  /**
   * Mostrar un mensaje toast con Bootstrap.
   * Pasos:
   * 1. Asegurar contenedor de toasts
   * 2. Inyectar markup del toast
   * 3. Inicializar y mostrar con autohide
   * 4. Remover del DOM al ocultarse
   */
  showToast(message, type = 'info', duration = 3000) {
    // 1. Asegurar contenedor de toasts
    let container = document.getElementById('custom-alert-container');
    if (!container) {
      container = document.createElement('div');
      container.id = 'custom-alert-container';
      container.className = 'position-fixed top-0 end-0 p-3';
      container.style.zIndex = '2000';
      document.body.appendChild(container);
    }

    // 2. Inyectar markup del toast
    const alertId = `alert-${Date.now()}`;
    container.insertAdjacentHTML('beforeend', `
      <div id="${alertId}" class="toast align-items-center border-0" role="alert">
        <div class="d-flex">
          <div class="toast-body bg-${type} text-white rounded-start">${message}</div>
          <button type="button" class="btn-close btn-close-white me-2 m-auto" 
                  data-bs-dismiss="toast" aria-label="Close"></button>
        </div>
      </div>
    `);

    // 3. Inicializar y mostrar con autohide
    const toastElement = document.getElementById(alertId);
    const toast = new bootstrap.Toast(toastElement, { autohide: true, delay: duration });

    // 4. Remover del DOM al ocultarse
    toastElement.addEventListener('hidden.bs.toast', () => toastElement.remove());
    toast.show();
  },

  /**
   * Validar que un valor sea numérico y >= min.
   * Pasos:
   * 1. Intentar convertir a Number
   * 2. Verificar NaN y mínimo
   * 3. Retornar booleano de validez
   */
  isValidNumber(value, min = 0) {
    // 1. Intentar convertir a Number
    const num = Number(value);
    // 2. Verificar NaN y mínimo
    // 3. Retornar booleano de validez
    return !isNaN(num) && num >= min;
  },

  /**
   * Validar que start y end formen un rango válido.
   * Pasos:
   * 1. Validar que ambos sean números válidos (>=1)
   * 2. Comparar start <= end
   * 3. Retornar resultado de la validación
   */
  isValidRange(start, end) {
    // 1. Validar que ambos sean números válidos (>=1)
    // 2. Comparar start <= end
    // 3. Retornar resultado de la validación
    return this.isValidNumber(start, 1) &&
      this.isValidNumber(end, 1) &&
      Number(start) <= Number(end);
  }
};

// =============================================================================
// MÓDULO DE GESTIÓN DE MODALES
// =============================================================================

/**
 * Gestionar modales dinámicos con pila de navegación.
 * Pasos:
 * 1. Mantener historial de vistas
 * 2. Cargar, apilar, renderizar y volver atrás
 * 3. Respaldar/restaurar estado de formularios
 */
const ModalManager = {
  /**
   * Pila de vistas del modal.
   * Pasos:
   * 1. Guardar título, contenido, footer, tamaño y estado del form
   * 2. Trabajar como historial navegable
   */
  stack: [],

  /**
   * Cargar contenido dinámico en el modal.
   * Pasos:
   * 1. Validar modal y respaldar estado
   * 2. Mostrar loading y abrir modal
   * 3. Fetch del contenido remoto
   * 4. Apilar y renderizar (o mostrar error)
   */
  async loadContent(url, title, size = '', footer = '', saveState = true, onRendered = null) {
    // 1. Validar modal y respaldar estado
    const modal = document.getElementById('dynamicModal');
    if (!modal) {
      Utils.showToast('Error: Modal no encontrado.', 'danger');
      return;
    }
    if (saveState && this.stack.length > 0) this._backupFormData();

    // 2. Mostrar loading y abrir modal
    this._showLoadingState();
    this._showModal(modal);

    try {
      // 3. Fetch del contenido remoto
      const response = await fetch(url, { method: 'GET', headers: { 'X-Requested-With': 'XMLHttpRequest' } });
      if (!response.ok) throw new Error(`Error HTTP: ${response.status}`);
      const content = await response.text();

      // 4. Apilar y renderizar (o mostrar error)
      this.push(title, content, size, footer, onRendered);
    } catch (error) {
      console.error('Error al cargar contenido del modal:', error);
      const errorContent = `
        <div class="alert alert-danger">
          <h5><i class="fas fa-exclamation-triangle"></i> Error al cargar</h5>
          <p>No se pudo cargar el contenido. ${error.message}</p>
          <button class="btn btn-outline-secondary btn-sm" onclick="ModalManager.pop()">← Volver</button>
        </div>`;
      this.push(title, errorContent, size, footer);
    }
  },

  /**
   * Apilar y renderizar una nueva vista.
   * Pasos:
   * 1. Agregar la vista a la pila
   * 2. Renderizar la vista actual
   * 3. Ejecutar callback post-render si existe
   * 4. Asegurar visibilidad del modal
   */
  push(title, content, size = '', footer = '', onRendered = null) {
    // 1. Agregar la vista a la pila
    this.stack.push({ title, content, footer, size, formData: null });

    // 2. Renderizar la vista actual
    this._renderCurrentView().then(() => {
      // 3. Ejecutar callback post-render si existe
      if (typeof onRendered === 'function') onRendered();
    });

    // 4. Asegurar visibilidad del modal
    this._ensureModalVisible();
  },

  /**
   * Volver a la vista anterior.
   * Pasos:
   * 1. Verificar que haya historial previo
   * 2. Quitar la vista actual
   * 3. Renderizar la vista anterior
   */
  pop() {
    // 1. Verificar que haya historial previo
    if (this.stack.length <= 1) {
      console.warn('No hay vistas anteriores.');
      return;
    }
    // 2. Quitar la vista actual
    this.stack.pop();
    // 3. Renderizar la vista anterior
    this._renderCurrentView();
  },

  /**
   * Mostrar estado de carga en el modal.
   * Pasos:
   * 1. Construir markup con spinner
   * 2. Inyectar en el cuerpo del modal
   */
  _showLoadingState() {
    // 1. Construir markup con spinner
    const loadingContent = `
      <div class="text-center py-4">
        <div class="spinner-border text-primary" role="status">
          <span class="visually-hidden">Cargando...</span>
        </div>
        <p class="mt-2">Cargando contenido...</p>
      </div>
    `;
    // 2. Inyectar en el cuerpo del modal
    document.getElementById('modalBody').innerHTML = loadingContent;
  },

  /**
   * Abrir el modal de Bootstrap si está oculto.
   * Pasos:
   * 1. Obtener/crear instancia de Bootstrap.Modal
   * 2. Mostrar el modal si no está visible
   */
  _showModal(modal) {
    // 1. Obtener/crear instancia de Bootstrap.Modal
    let modalInstance = bootstrap.Modal.getInstance(modal);
    if (!modalInstance) {
      modalInstance = new bootstrap.Modal(modal, { backdrop: true, keyboard: true });
    }
    // 2. Mostrar el modal si no está visible
    if (!modal.classList.contains('show')) {
      modalInstance.show();
    }
  },

  /**
   * Asegurar que el modal esté visible.
   * Pasos:
   * 1. Obtener/crear instancia del modal
   * 2. Abrir si está oculto
   */
  _ensureModalVisible() {
    // 1. Obtener/crear instancia del modal
    const modal = document.getElementById('dynamicModal');
    if (!modal) return;
    let modalInstance = bootstrap.Modal.getInstance(modal);
    if (!modalInstance) {
      modalInstance = new bootstrap.Modal(modal, { backdrop: true, keyboard: true });
    }
    // 2. Abrir si está oculto
    if (!modal.classList.contains('show')) modalInstance.show();
  },

  /**
   * Respaldar estado de inputs visibles.
   * Pasos:
   * 1. Localizar contenedor y formulario (si existe)
   * 2. Recolectar inputs relevantes
   * 3. Guardar snapshot en la vista actual
   */
  _backupFormData() {
    // 1. Localizar contenedor y formulario (si existe)
    const currentBody = document.getElementById('modalBody');
    if (!currentBody || this.stack.length === 0) return;
    const form = currentBody.querySelector('form');
    const inputs = form
      ? form.querySelectorAll('input, select, textarea')
      : currentBody.querySelectorAll('input, select, textarea');

    // 2. Recolectar inputs relevantes
    const formData = {};
    inputs.forEach(input => {
      if (input.name) {
        formData[input.name] = ['checkbox', 'radio'].includes(input.type) ? input.checked : input.value;
      }
    });

    // 3. Guardar snapshot en la vista actual
    this.stack[this.stack.length - 1].formData = formData;
  },

  /**
   * Renderizar la vista activa.
   * Pasos:
   * 1. Obtener vista actual y elementos del modal
   * 2. Ejecutar animación de salida
   * 3. Actualizar título, cuerpo y footer
   * 4. Restaurar estado del formulario
   */
  async _renderCurrentView() {
    // 1. Obtener vista actual y elementos del modal
    if (this.stack.length === 0) return;
    const current = this.stack[this.stack.length - 1];
    const elements = {
      title: document.getElementById('modalTitle'),
      body: document.getElementById('modalBody'),
      footer: document.getElementById('modalFooter')
    };

    // 2. Ejecutar animación de salida
    await this._animateOut(elements);

    // 3. Actualizar título, cuerpo y footer
    this._updateContent(elements, current);

    // 4. Restaurar estado del formulario
    this._restoreFormData(elements.body, current.formData);
  },

  /**
   * Animar salida de contenido actual.
   * Pasos:
   * 1. Detectar nodos animables
   * 2. Aplicar clases de fadeOut
   * 3. Esperar finalización de animaciones
   */
  async _animateOut(elements) {
    // 1. Detectar nodos animables
    const promises = [];
    ['body', 'title'].forEach(key => {
      const content = elements[key]?.firstElementChild;
      if (content && content.nodeType === 1) {
        // 2. Aplicar clases de fadeOut
        content.classList.add('animate__animated', 'animate__fadeOut');
        // 3. Esperar finalización de animaciones
        promises.push(
          new Promise(resolve => {
            content.addEventListener('animationend', () => {
              content.classList.remove('animate__animated', 'animate__fadeOut');
              content.style.display = 'none';
              resolve();
            }, { once: true });
          })
        );
      }
    });

    try {
      await Promise.all(promises);
    } catch (error) {
      console.error('Error en animación de salida:', error);
    }
  },

  /**
   * Actualizar contenido del modal.
   * Pasos:
   * 1. Renderizar título con animación
   * 2. Renderizar cuerpo con animación
   * 3. Renderizar/ocultar footer
   */
  _updateContent(elements, current) {
    // 1. Renderizar título con animación
    if (elements.title) {
      elements.title.innerHTML = '';
      const titleSpan = document.createElement('span');
      titleSpan.textContent = current.title;
      titleSpan.classList.add('animate__animated', 'animate__fadeIn');
      elements.title.appendChild(titleSpan);
    }

    // 2. Renderizar cuerpo con animación
    if (elements.body) {
      elements.body.innerHTML = '';
      const bodyDiv = document.createElement('div');
      bodyDiv.innerHTML = current.content;
      bodyDiv.classList.add('animate__animated', 'animate__fadeIn');
      elements.body.appendChild(bodyDiv);
    }
    
    // 3. Renderizar/ocultar footer
    // Busca si el nuevo contenido tiene un div con la clase .modal-footer
    const newFooter = elements.body.querySelector('.modal-footer');
    if (newFooter) {
        elements.footer.innerHTML = newFooter.innerHTML;
        elements.footer.style.display = 'block';
        newFooter.remove(); // Eliminar el footer del body para no duplicarlo
    } else {
        elements.footer.innerHTML = '';
        elements.footer.style.display = 'none';
    }
  },

  /**
   * Restaurar valores previos en inputs.
   * Pasos:
   * 1. Verificar snapshot y contenedor
   * 2. Seleccionar inputs del nuevo DOM
   * 3. Reaplicar valores y checks
   */
  _restoreFormData(bodyElement, formData) {
    // 1. Verificar snapshot y contenedor
    if (!formData || !bodyElement) return;
    const container = bodyElement.firstElementChild;
    if (!container) return;

    // 2. Seleccionar inputs del nuevo DOM
    const inputs = container.querySelectorAll('input, select, textarea');

    // 3. Reaplicar valores y checks
    inputs.forEach(input => {
      if (input.name && formData[input.name] !== undefined) {
        if (['checkbox', 'radio'].includes(input.type)) {
          input.checked = formData[input.name];
        } else {
          input.value = formData[input.name];
        }
      }
    });
  }
};

// =============================================================================
// MÓDULO DE GESTIÓN DE AUTORES
// =============================================================================

/**
 * Gestionar selección y configuración de autores.
 * Pasos:
 * 1. Mantener lista seleccionada y roles disponibles
 * 2. Buscar, agregar, eliminar, ordenar y asignar roles
 * 3. Sincronizar campo hidden y UI
 */
const AuthorManager = {
  /**
   * Lista de autores seleccionados.
   * Pasos:
   * 1. Guardar autor_id, nombre, orcid, orden, rol_id
   * 2. Mantener orden estable y único
   */
  selected: [],

  /**
   * Lista de roles disponibles.
   * Pasos:
   * 1. Cargar roles desde API
   * 2. Usar para opciones de select en la tabla
   */
  roles: [],

  /**
   * Cargar roles desde el servidor.
   * Pasos:
   * 1. Consumir endpoint de roles
   * 2. Validar respuesta y asignar this.roles
   * 3. Manejar errores de red
   */
  async loadRoles() {
    // 1. Consumir endpoint de roles
    try {
      const res = await fetch('/authors/api/roles/');
      const data = await res.json();
      // 2. Validar respuesta y asignar this.roles
      if (data.success) this.roles = data.roles;
    } catch (err) {
      // 3. Manejar errores de red
      console.error('Error al cargar roles:', err);
    }
  },

  /**
   * Buscar autores en la tabla local.
   * Pasos:
   * 1. Leer término del input
   * 2. Filtrar filas por nombre u ORCID
   * 3. Mostrar alerta si no hay coincidencias
   */
  searchLocal() {
    // 1. Leer término del input
    const query = document.getElementById('buscarAutor')?.value.trim().toLowerCase();
    if (!query) {
      Utils.showToast('Ingrese un nombre o ORCID.');
      return;
    }

    // 2. Filtrar filas por nombre u ORCID
    const rows = document.querySelectorAll('#autoresDisponibles tr');
    let found = 0;
    rows.forEach(row => {
      const name = row.querySelector('td:first-child')?.textContent.toLowerCase() || '';
      const orcid = row.querySelector('td:nth-child(2)')?.textContent.toLowerCase() || '';
      const matches = name.includes(query) || orcid.includes(query);
      row.style.display = matches ? '' : 'none';
      if (matches) found++;
    });

    // 3. Mostrar alerta si no hay coincidencias
    if (found === 0) Utils.showToast('No se encontraron autores.');
  },

  /**
   * Agregar autor a la lista seleccionada.
   * Pasos:
   * 1. Evitar duplicados por autor_id
   * 2. Insertar con orden incremental
   * 3. Actualizar interfaz y campo hidden
   */
  add(authorId, name, orcid) {
    // 1. Evitar duplicados por autor_id
    if (this.selected.some(a => a.autor_id === authorId)) {
      Utils.showToast('Autor ya seleccionado.');
      return;
    }

    // 2. Insertar con orden incremental
    this.selected.push({
      autor_id: authorId,
      nombre: name,
      orcid,
      orden: this.selected.length + 1,
      rol_id: null
    });

    // 3. Actualizar interfaz y campo hidden
    this._updateUI(authorId);
  },

  /**
   * Eliminar autor de la lista seleccionada.
   * Pasos:
   * 1. Filtrar autor por ID
   * 2. Reenumerar órdenes
   * 3. Refrescar UI y lista disponible
   */
  remove(authorId) {
    // 1. Filtrar autor por ID
    this.selected = this.selected.filter(a => a.autor_id !== authorId);
    // 2. Reenumerar órdenes
    this.selected.forEach((a, i) => a.orden = i + 1);
    // 3. Refrescar UI y lista disponible
    this._updateUI(authorId, true);
  },

  /**
   * Actualizar rol de un autor.
   * Pasos:
   * 1. Localizar autor en selección
   * 2. Asignar rol_id o null
   * 3. Sincronizar campo hidden
   */
  updateRole(authorId, roleId) {
    // 1. Localizar autor en selección
    const author = this.selected.find(a => a.autor_id === authorId);
    if (author) {
      // 2. Asignar rol_id o null
      author.rol_id = roleId || null;
      // 3. Sincronizar campo hidden
      this._updateHiddenField();
    }
  },

  /**
   * Actualizar orden de un autor.
   * Pasos:
   * 1. Localizar autor y convertir nuevo orden
   * 2. Reordenar colección por orden
   * 3. Refrescar UI
   */
  updateOrder(authorId, newOrder) {
    // 1. Localizar autor y convertir nuevo orden
    const author = this.selected.find(a => a.autor_id === authorId);
    if (author) {
      author.orden = parseInt(newOrder, 10);
      // 2. Reordenar colección por orden
      this.selected.sort((a, b) => a.orden - b.orden);
      // 3. Refrescar UI
      this._updateUI();
    }
  },

  /**
   * Refrescar UI completa de autores.
   * Pasos:
   * 1. Actualizar tabla de seleccionados
   * 2. Actualizar visibilidad en disponibles
   * 3. Actualizar campo hidden JSON
   */
  _updateUI(authorId = null, removed = false) {
    // 1. Actualizar tabla de seleccionados
    this._updateTable();
    // 2. Actualizar visibilidad en disponibles
    if (authorId) this._updateAvailableList(authorId, removed);
    // 3. Actualizar campo hidden JSON
    this._updateHiddenField();
  },

  /**
   * Construir tabla de autores seleccionados.
   * Pasos:
   * 1. Obtener contenedor tbody
   * 2. Construir opciones de roles
   * 3. Renderizar filas con inputs y acciones
   */
  _updateTable() {
    // 1. Obtener contenedor tbody
    const tbody = document.getElementById('autoresSeleccionados');
    if (!tbody) return;

    // 2. Construir opciones de roles
    const roleOptions = this.roles.map(r => `<option value="${r.id}">${r.nombre_rol}</option>`).join('');

    // 3. Renderizar filas con inputs y acciones
    tbody.innerHTML = this.selected.map(author => `
      <tr data-autor-id="${author.autor_id}">
        <td>${author.nombre}</td>
        <td>${author.orcid}</td>
        <td>
          <input type="number" class="form-control form-control-sm" 
                 value="${author.orden}" min="1" 
                 onchange="AuthorManager.updateOrder(${author.autor_id}, this.value)">
        </td>
        <td>
          <select class="form-select form-select-sm" 
                  onchange="AuthorManager.updateRole(${author.autor_id}, this.value)">
            <option value="">Seleccionar rol</option>
            ${roleOptions}
          </select>
        </td>
        <td>
          <button type="button" class="btn btn-sm btn-danger" 
                  onclick="AuthorManager.remove(${author.autor_id})">
            <i class="fas fa-trash"></i>
          </button>
        </td>
      </tr>
    `).join('');
  },

  /**
   * Mostrar/ocultar autor en lista de disponibles.
   * Pasos:
   * 1. Buscar fila del autor por data-atributo
   * 2. Alternar display según acción (remove/add)
   */
  _updateAvailableList(authorId, show) {
    // 1. Buscar fila del autor por data-atributo
    const row = document.querySelector(`#autoresDisponibles tr[data-autor-id="${authorId}"]`);
    // 2. Alternar display según acción (remove/add)
    if (row) row.style.display = show ? '' : 'none';
  },

  /**
   * Sincronizar campo hidden con JSON de autores.
   * Pasos:
   * 1. Localizar input hidden
   * 2. Serializar this.selected y asignar
   */
  _updateHiddenField() {
    // 1. Localizar input hidden
    const field = document.getElementById('autoresSeleccionadosData');
    // 2. Serializar this.selected y asignar
    if (field) field.value = JSON.stringify(this.selected);
  },

  /**
   * Validar lista de autores.
   * Pasos:
   * 1. Verificar que exista al menos un autor
   * 2. Verificar que todos tengan rol asignado
   * 3. Retornar resultado de validación
   */
  validate() {
    // 1. Verificar que exista al menos un autor
    if (this.selected.length === 0) {
      Utils.showToast('Debe seleccionar al menos un autor.', 'danger');
      return false;
    }
    // 2. Verificar que todos tengan rol asignado
    if (this.selected.some(a => !a.rol_id)) {
      Utils.showToast('Todos los autores deben tener un rol asignado.', 'danger');
      return false;
    }
    // 3. Retornar resultado de validación
    return true;
  }
};

// =============================================================================
// MÓDULO DE GESTIÓN DE PALABRAS CLAVE
// =============================================================================

/**
 * Gestionar palabras clave asociadas a un paper.
 * Pasos:
 * 1. Cargar catálogo, seleccionar existentes y crear nuevas
 * 2. Mantener arrays selected/available sincronizados
 * 3. Renderizar badges y actualizar campo hidden
 */
const KeywordManager = {
  /**
   * Palabras clave seleccionadas.
   * Pasos:
   * 1. Guardar id (o null) y nombre
   * 2. Mantener sin duplicados
   */
  selected: [],

  /**
   * Palabras clave disponibles.
   * Pasos:
   * 1. Cargar desde API
   * 2. Renderizar para selección
   */
  available: [],

  /**
   * Cargar palabras clave disponibles.
   * Pasos:
   * 1. Consumir endpoint /api/palabras-clave/
   * 2. Guardar lista en available
   * 3. Renderizar si hay contenedor
   */
  async load() {
    try {
      // 1. Consumir endpoint /api/palabras-clave/
      const res = await fetch('/api/palabras-clave/');
      const data = await res.json();
      // 2. Guardar lista en available
      if (data.success) {
        this.available = data.palabras_clave;
        // 3. Renderizar si hay contenedor
        const container = document.getElementById('palabrasClaveDisponibles');
        if (container) this._renderAvailable();
      }
    } catch (err) {
      console.error('Error al cargar palabras clave:', err);
    }
  },

  /**
   * Seleccionar una palabra clave existente.
   * Pasos:
   * 1. Verificar que no esté ya seleccionada
   * 2. Insertar en selected con su id y nombre
   * 3. Refrescar UI y campo hidden
   */
  select(keyword) {
    // 1. Verificar que no esté ya seleccionada
    const exists = this.selected.some(k =>
      (k.id && k.id === keyword.id) || (k.nombre === keyword.nombre)
    );
    if (exists) {
      Utils.showToast('Palabra clave ya seleccionada.');
      return;
    }
    // 2. Insertar en selected con su id y nombre
    this.selected.push({ id: keyword.id, nombre: keyword.nombre });
    // 3. Refrescar UI y campo hidden
    this._updateUI();
  },

  /**
   * Agregar palabra clave personalizada.
   * Pasos:
   * 1. Leer valor del input
   * 2. Validar no vacío y no duplicado
   * 3. Insertar (id=null) y refrescar UI
   */
  addNew() {
    // 1. Leer valor del input
    const input = document.getElementById('palabrasClaveInput');
    const value = input?.value.trim();

    // 2. Validar no vacío y no duplicado
    if (!value) {
      Utils.showToast('Ingrese una palabra clave.');
      return;
    }
    const existsInAvailable = this.available.some(k => k.nombre.toLowerCase() === value.toLowerCase());
    const existsInSelected = this.selected.some(k => k.nombre.toLowerCase() === value.toLowerCase());
    if (existsInAvailable) {
      Utils.showToast('Ya existe. Selecciónela de la lista.');
      return;
    }
    if (existsInSelected) {
      Utils.showToast('Ya está seleccionada.');
      return;
    }

    // 3. Insertar (id=null) y refrescar UI
    this.selected.push({ id: null, nombre: value });
    this._updateUI();
    input.value = '';
  },

  /**
   * Eliminar palabra clave seleccionada por índice.
   * Pasos:
   * 1. Quitar elemento en posición index
   * 2. Refrescar UI y campo hidden
   */
  remove(index) {
    // 1. Quitar elemento en posición index
    this.selected.splice(index, 1);
    // 2. Refrescar UI y campo hidden
    this._updateUI();
  },

  /**
   * Crear en backend las palabras nuevas.
   * Pasos:
   * 1. Filtrar seleccionadas sin id y no presentes en available
   * 2. Enviar POST por cada nueva al endpoint create
   * 3. Actualizar id y sincronizar catálogo local
   */
  async createNewKeywords() {
    // 1. Filtrar seleccionadas sin id y no presentes en available
    const newKeywords = this.selected.filter(k =>
      !k.id && !this.available.some(a => a.nombre.toLowerCase() === k.nombre.toLowerCase())
    );

    // 2. Enviar POST por cada nueva al endpoint create
    for (const keyword of newKeywords) {
      try {
        const res = await fetch('/api/palabras-clave/create/', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': Utils.getCookie('csrftoken'),
            'X-Requested-With': 'XMLHttpRequest'
          },
          body: JSON.stringify({ nombre: keyword.nombre.toLowerCase() })
        });
        const data = await res.json();

        // 3. Actualizar id y sincronizar catálogo local
        if (data.success && data.palabra_clave) {
          keyword.id = data.palabra_clave.id;
          keyword.nombre = data.palabra_clave.nombre;
          this.available.push(data.palabra_clave);
        }
      } catch (err) {
        console.warn('No se pudo crear palabra clave:', keyword.nombre);
      }
    }
  },

  /**
   * Refrescar interfaz de palabras clave.
   * Pasos:
   * 1. Renderizar seleccionadas (badges)
   * 2. Renderizar disponibles (chips)
   * 3. Actualizar campo hidden JSON
   */
  _updateUI() {
    // 1. Renderizar seleccionadas (badges)
    this._renderSelected();
    // 2. Renderizar disponibles (chips)
    this._renderAvailable();
    // 3. Actualizar campo hidden JSON
    this._updateHiddenField();
  },

  /**
   * Renderizar badges de seleccionadas.
   * Pasos:
   * 1. Localizar contenedor
   * 2. Construir badges con botón de eliminar
   * 3. Inyectar HTML resultante
   */
  _renderSelected() {
    // 1. Localizar contenedor
    const container = document.getElementById('palabrasClaveSeleccionadas');
    if (!container) return;

    // 2. Construir badges con botón de eliminar
    container.innerHTML = this.selected.map((k, i) => `
      <span class="badge bg-primary me-1 mb-1">
        ${k.nombre}
        <button type="button" class="btn-close btn-close-white" 
                aria-label="Eliminar" 
                onclick="KeywordManager.remove(${i})" 
                style="font-size:0.5em;"></button>
      </span>
    `).join('');
  },

  /**
   * Renderizar catálogo disponible.
   * Pasos:
   * 1. Localizar contenedor
   * 2. Iterar catálogo excluyendo ya seleccionadas
   * 3. Construir chips clicables para seleccionar
   */
  _renderAvailable() {
    // 1. Localizar contenedor
    const container = document.getElementById('palabrasClaveDisponibles');
    if (!container) {
      console.warn('Contenedor de palabras clave disponibles no encontrado');
      return;
    }

    // 2. Iterar catálogo excluyendo ya seleccionadas
    container.innerHTML = '';
    this.available.forEach(keyword => {
      const isSelected = this.selected.some(k =>
        (k.id && k.id === keyword.id) || (k.nombre === keyword.nombre)
      );

      // 3. Construir chips clicables para seleccionar
      if (!isSelected) {
        const span = document.createElement('span');
        span.className = 'badge bg-secondary me-1 mb-1';
        span.style.cursor = 'pointer';
        span.textContent = keyword.nombre;
        span.onclick = () => this.select(keyword);
        container.appendChild(span);
      }
    });
  },

  /**
   * Sincronizar campo hidden con selected.
   * Pasos:
   * 1. Localizar input hidden
   * 2. Guardar JSON.stringify(selected)
   */
  _updateHiddenField() {
    // 1. Localizar input hidden
    const field = document.getElementById('palabrasClaveData');
    // 2. Guardar JSON.stringify(selected)
    if (field) field.value = JSON.stringify(this.selected);
  },

  /**
   * Validar que exista al menos una palabra clave.
   * Pasos:
   * 1. Verificar longitud de selected
   * 2. Notificar error si está vacío
   * 3. Retornar resultado
   */
  validate() {
    // 1. Verificar longitud de selected
    if (this.selected.length === 0) {
      // 2. Notificar error si está vacío
      Utils.showToast('Debe agregar al menos una palabra clave.', 'danger');
      return false;
    }
    // 3. Retornar resultado
    return true;
  }
};

// =============================================================================
// MÓDULO DE GESTIÓN DE PAPERS
// =============================================================================

/**
 * Gestionar creación y guardado de papers.
 * Pasos:
 * 1. Recolectar campos del formulario
 * 2. Validar datos, autores y palabras clave
 * 3. Generar referencia APA
 * 4. Enviar datos y archivos al backend
 * 5. Mostrar feedback y actualizar UI
 */
const PaperManager = {
  /**
   * Guardar un nuevo paper con datos asociados.
   * Pasos:
   * 1. Recolectar campos del formulario
   * 2. Validar requeridos, numéricos, archivos, autores y keywords
   * 3. Generar referencia APA
   * 4. Enviar payload al backend
   * 5. Notificar éxito y refrescar
   */
  async save() {
    // 1. Recolectar campos del formulario
    const fields = this._collectFields();

    // 2. Validar requeridos, numéricos, archivos, autores y keywords
    if (!this._validateAll(fields)) return;

    // 3. Generar referencia APA
    const journalName = document.querySelector('#revistaSelect option:checked')?.textContent || '';
    const apaReference = this._generateAPAReference({ ...fields, nombreRevista: journalName });

    try {
      // 4. Enviar payload al backend
      await this._submitData(fields, apaReference);

      // 5. Notificar éxito y refrescar
      Utils.showToast('✅ Paper guardado correctamente.', 'success');
      setTimeout(() => {
        bootstrap.Modal.getInstance(document.getElementById('dynamicModal'))?.hide();
        window.location.reload();
      }, 1500);
    } catch (error) {
      console.error('Error al guardar el paper:', error);
      Utils.showToast(`❌ ${error.message}`, 'danger');
    }
  },

  /**
   * Recolectar campos del formulario.
   * Pasos:
   * 1. Leer valores de inputs por id
   * 2. Normalizar strings con trim
   * 3. Retornar objeto de campos
   */
  _collectFields() {
    // 1. Leer valores de inputs por id
    // 2. Normalizar strings con trim
    // 3. Retornar objeto de campos
    return {
      titulo: document.getElementById('tituloPaper')?.value.trim(),
      anio_publicacion: document.getElementById('anioPublicacion')?.value,
      estatus_publicacion: document.getElementById('estatusPublicacion')?.value,
      revista: document.getElementById('revistaSelect')?.value,
      volumen: document.getElementById('volumenRevista')?.value.trim(),
      numero: document.getElementById('numeroRevista')?.value.trim(),
      indiceRevista: document.getElementById('indiceRevista')?.value.trim(),
      doi: document.getElementById('doiPaper')?.value.trim(),
      urlCita: document.getElementById('urlCita')?.value.trim(),
      totalCitas: document.getElementById('totalCitas')?.value,
      paginaInicio: document.getElementById('paginaInicio')?.value,
      paginaFin: document.getElementById('paginaFin')?.value,
      proposito: document.getElementById('propositoPaper')?.value,
      objetivo: document.getElementById('objetivoPaper')?.value.trim(),
      descripcion: document.getElementById('descripcionPaper')?.value.trim(),
      abstract: document.getElementById('abstractPaper')?.value.trim(),
      apoyoSECITI: document.getElementById('apoyoSECITI')?.checked,
      programaSECITI: document.getElementById('programaSECITI')?.value,
      ejeSECITHI: document.getElementById('ejeSECITHI')?.value
    };
  },

  /**
   * Validar todos los aspectos requeridos.
   * Pasos:
   * 1. Validar campos obligatorios
   * 2. Validar numéricos y rangos
   * 3. Validar archivos obligatorios
   * 4. Validar autores y palabras clave
   */
  _validateAll(fields) {
    // 1. Validar campos obligatorios
    return this._validateRequired(fields) &&
      // 2. Validar numéricos y rangos
      this._validateNumeric(fields) &&
      // 3. Validar archivos obligatorios
      this._validateFiles() &&
      // 4. Validar autores y palabras clave
      AuthorManager.validate() &&
      KeywordManager.validate();
  },

  /**
   * Validar campos requeridos.
   * Pasos:
   * 1. Definir lista de campos obligatorios
   * 2. Verificar que todos tengan valor
   * 3. Notificar y abortar si falta alguno
   */
  _validateRequired(fields) {
    // 1. Definir lista de campos obligatorios
    const required = [
      'titulo', 'anio_publicacion', 'estatus_publicacion', 'revista',
      'volumen', 'numero', 'indiceRevista', 'doi', 'urlCita',
      'objetivo', 'descripcion', 'abstract'
    ];

    // 2. Verificar que todos tengan valor
    for (const key of required) {
      if (!fields[key]) {
        // 3. Notificar y abortar si falta alguno
        const fieldName = key.replace(/([A-Z])/g, ' $1').toLowerCase();
        Utils.showToast(`El campo "${fieldName}" es requerido.`, 'danger');
        return false;
      }
    }
    return true;
  },

  /**
   * Validar numéricos y rangos.
   * Pasos:
   * 1. Validar total de citas como número válido
   * 2. Validar rango de páginas consistente
   * 3. Retornar resultado
   */
  _validateNumeric(fields) {
    // 1. Validar total de citas como número válido
    if (!Utils.isValidNumber(fields.totalCitas)) {
      Utils.showToast('Total de citas debe ser un número válido.', 'danger');
      return false;
    }
    // 2. Validar rango de páginas consistente
    if (!Utils.isValidRange(fields.paginaInicio, fields.paginaFin)) {
      Utils.showToast('Las páginas deben ser números válidos y consistentes.', 'danger');
      return false;
    }
    // 3. Retornar resultado
    return true;
  },

  /**
   * Validar presencia de archivos requeridos.
   * Pasos:
   * 1. Verificar archivo principal del paper
   * 2. Verificar archivo de primera página
   * 3. Retornar resultado
   */
  _validateFiles() {
    // 1. Verificar archivo principal del paper
    const paperFile = document.getElementById('archivoPaper')?.files[0];
    if (!paperFile) {
      Utils.showToast('Debe adjuntar el archivo del paper.', 'danger');
      return false;
    }
    // 2. Verificar archivo de primera página
    const firstPage = document.getElementById('primeraPagina')?.files[0];
    if (!firstPage) {
      Utils.showToast('Debe adjuntar la primera página.', 'danger');
      return false;
    }
    // 3. Retornar resultado
    return true;
  },

  /**
   * Enviar datos al backend.
   * Pasos:
   * 1. Construir FormData con nombres esperados
   * 2. Adjuntar referencia, autores y palabras clave
   * 3. Adjuntar archivos del paper y de la edición
   * 4. Crear palabras clave nuevas y sincronizar
   * 5. POST a /publications/create/ y validar respuesta
   */
  async _submitData(fields, apaReference) {
    // 1. Construir FormData con nombres esperados
    const formData = new FormData();
    Object.entries(fields).forEach(([key, value]) => {
      let fieldName;
      if (key === 'apoyoSECITI') fieldName = 'recibio_apoyo_seciti';
      else if (key === 'programaSECITI') fieldName = 'programa_seciti';
      else if (key === 'ejeSECITHI') fieldName = 'eje_secithi';
      else fieldName = key.replace(/([A-Z])/g, '_$1').toLowerCase();
      console.warn(fieldName);
      formData.append(fieldName, key === 'apoyoSECITI' ? (value ? 'true' : 'false') : value);
    });

    // 2. Adjuntar referencia, autores y palabras clave
    formData.append('referencia_apa', apaReference);
    formData.append('autores', JSON.stringify(AuthorManager.selected));
    formData.append('palabras_clave', JSON.stringify(KeywordManager.selected));

    // 3. Adjuntar archivos del paper y de la edición
    const paperFile = document.getElementById('archivoPaper')?.files[0];
    const firstPage = document.getElementById('primeraPagina')?.files[0];
    if (paperFile) formData.append('archivo_paper', paperFile);
    if (firstPage) formData.append('primera_pagina', firstPage);
    const editionFilesContainer = document.getElementById('edicionArchivosContainer');
    if (editionFilesContainer) {
      const editionFileInputs = editionFilesContainer.querySelectorAll('input[type="file"]');
      editionFileInputs.forEach(input => {
        if (input.files.length > 0) formData.append(input.name, input.files[0]);
      });
    }

    // 4. Crear palabras clave nuevas y sincronizar
    await KeywordManager.createNewKeywords();

    // 5. POST a /publications/create/ y validar respuesta
    const response = await fetch('/publications/create/', {
      method: 'POST',
      headers: {
        'X-CSRFToken': Utils.getCookie('csrftoken'),
        'X-Requested-With': 'XMLHttpRequest'
      },
      body: formData
    });
    const data = await response.json();
    if (!response.ok || !data.success) {
      throw new Error(data.message || 'Error al guardar.');
    }
  },

  /**
   * Generar referencia APA simple.
   * Pasos:
   * 1. Ordenar autores y construir cita corta
   * 2. Componer volumen/número y páginas
   * 3. Armar string en formato APA básico
   */
  _generateAPAReference(data) {
    // 1. Ordenar autores y construir cita corta
    const authors = AuthorManager.selected
      .sort((a, b) => a.orden - b.orden)
      .map(a => a.nombre);

    let authorCitation = '';
    if (authors.length === 1) authorCitation = authors[0];
    else if (authors.length === 2) authorCitation = `${authors[0]} & ${authors[1]}`;
    else if (authors.length > 2) authorCitation = `${authors[0]} et al.`;

    // 2. Componer volumen/número y páginas
    const volumeIssue = data.volumen && data.numero
      ? `${data.volumen}(${data.numero})`
      : (data.volumen || '');
    const pages = data.paginaInicio
      ? `, ${data.paginaInicio}${data.paginaFin ? `-${data.paginaFin}` : ''}`
      : '';

    // 3. Armar string en formato APA básico
    return `${authorCitation}. (${data.anio_publicacion}). ${data.titulo}. ${data.nombreRevista}${volumeIssue ? `, ${volumeIssue}` : ''}${pages}.${data.doi ? ` https://doi.org/${data.doi}` : ''}`;
  }
};

// =============================================================================
// MÓDULO DE GESTIÓN DE ENTIDADES
// =============================================================================

/**
 * Gestionar creación de entidades relacionadas (catálogos).
 * Pasos:
 * 1. Enviar formulario al endpoint correspondiente
 * 2. Manejar éxito/errores y remarcar campos
 * 3. Recargar formulario padre con nueva entidad seleccionada
 */
const EntityManager = {
  /**
   * Guardar entidad vía POST.
   * Pasos:
   * 1. Localizar formulario y construir FormData
   * 2. Hacer fetch POST con CSRF
   * 3. Procesar respuesta (éxito/errores)
   * 4. Recargar vista padre y seleccionar nueva entidad
   */
  async save(entityType, formId, createUrl, titleField = 'nombre') {
    // 1. Localizar formulario y construir FormData
    const form = document.getElementById(formId);
    if (!form) {
      Utils.showToast('Error: Formulario no encontrado.', 'danger');
      return;
    }
    const formData = new FormData(form);

    try {
      // 2. Hacer fetch POST con CSRF
      const response = await fetch(createUrl, {
        method: 'POST',
        body: formData,
        headers: { 'X-CSRFToken': Utils.getCookie('csrftoken') }
      });
      const data = await response.json();

      // 3. Procesar respuesta (éxito/errores)
      if (data.success) {
        this._clearErrors(formId);
        Utils.showToast(data.message, 'success');

        setTimeout(() => {
          ModalManager.pop();
          setTimeout(() => {
            // 4. Recargar vista padre y seleccionar nueva entidad
            this._reloadParentForm(entityType, data.objeto.id);
          }, 300);
        }, 800);
      } else {
        this._handleErrors(formId, data);
      }
    } catch (error) {
      console.error(`Error al guardar ${entityType}:`, error);
      Utils.showToast('Error al comunicarse con el servidor.', 'danger');
    }
  },

  /**
   * Limpiar mensajes de error del formulario.
   * Pasos:
   * 1. Vaciar contenedores .text-danger relevantes
   * 2. Remover clases is-invalid
   */
  _clearErrors(formId) {
    // 1. Vaciar contenedores .text-danger relevantes
    const errorContainers = document.querySelectorAll(`#${formId} .text-danger`);
    errorContainers.forEach(container => {
      if (container.id.startsWith('error-')) container.textContent = '';
    });
    // 2. Remover clases is-invalid
    const invalidFields = document.querySelectorAll(`#${formId} .is-invalid`);
    invalidFields.forEach(field => field.classList.remove('is-invalid'));
  },

  /**
   * Mostrar errores de validación de backend.
   * Pasos:
   * 1. Limpiar errores previos y toast general
   * 2. Iterar campos y pintar mensajes/clases
   * 3. Loggear en consola para debugging
   */
  _handleErrors(formId, data) {
    // 1. Limpiar errores previos y toast general
    this._clearErrors(formId);
    Utils.showToast(data.message, 'danger');

    // 2. Iterar campos y pintar mensajes/clases
    if (data.errors) {
      console.group(`Errores de Validación:`);
      for (const [fieldName, errorMessages] of Object.entries(data.errors)) {
        console.error(`Campo '${fieldName}':`, errorMessages);
        const errorContainer = document.getElementById(`error-${fieldName}`);
        if (errorContainer) {
          errorContainer.textContent = errorMessages.join(' ');
          const fieldElement = document.querySelector(`#${formId} [name="${fieldName}"]`);
          if (fieldElement) fieldElement.classList.add('is-invalid');
        }
      }
      // 3. Loggear en consola para debugging
      console.groupEnd();
    }
  },

  /**
   * Recargar formulario padre tras crear entidad.
   * Pasos:
   * 1. Determinar URL y metadatos de recarga
   * 2. Guardar estado temporal y hacer pop
   * 3. Cargar vista padre sin guardar estado
   * 4. Restaurar estado y seleccionar nueva entidad
   */
  _reloadParentForm(entityType, entityId) {
    // 1. Determinar URL y metadatos de recarga
    const entitiesForPaperForm = ['autor', 'programaSeciti', 'ejeSecithi', 'revista'];
    let reloadUrl, title, size;
    let onRenderCallback = null;

    if (entitiesForPaperForm.includes(entityType)) {
      reloadUrl = `/modal/new-paper/?${this._getReloadParamName(entityType)}=${entityId}`;
      title = 'Registrar Nuevo Paper';
      size = 'xl';
      onRenderCallback = initializePaperFormListeners;
    } else {
      reloadUrl = `/journals/modal/new-journal/?${this._getReloadParamName(entityType)}=${entityId}`;
      title = 'Añadir Nueva Revista';
      size = 'lg';
      onRenderCallback = initializePaperFormListeners;
    }

    // 2. Guardar estado temporal y hacer pop
    let estadoTemporal = null;
    if (ModalManager.stack.length > 0) {
      estadoTemporal = { ...ModalManager.stack[ModalManager.stack.length - 1] };
      ModalManager.stack.pop();
    }

    // 3. Cargar vista padre sin guardar estado
    ModalManager.loadContent(reloadUrl, title, size, '', false, onRenderCallback);

    // 4. Restaurar estado y seleccionar nueva entidad
    if (estadoTemporal) {
      setTimeout(() => {
        if (ModalManager.stack.length > 0) {
          const formDataAModificar = { ...estadoTemporal.formData };
          const fieldMap = {
            'revista': 'revista',
            'pais': 'pais_publicacion',
            'categoria': 'categoria',
            'ambito': 'ambito',
            'editorial': 'editorial',
            'programaSeciti': 'programa_seciti',
            'ejeSecithi': 'eje_secithi',
          };
          const fieldName = fieldMap[entityType];
          if (fieldName && Object.prototype.hasOwnProperty.call(formDataAModificar, fieldName)) {
            formDataAModificar[fieldName] = String(entityId);
          }
          ModalManager.stack[ModalManager.stack.length - 1].formData = formDataAModificar;
          ModalManager._renderCurrentView().then(() => {
            if (typeof initializePaperFormListeners === 'function') initializePaperFormListeners();
          });
        }
      }, 100);
    }
  },

  /**
   * Mapear entidad → nombre de parámetro para recarga.
   * Pasos:
   * 1. Definir diccionario de parámetros
   * 2. Retornar clave según entityType
   */
  _getReloadParamName(entityType) {
    // 1. Definir diccionario de parámetros
    const paramMap = {
      revista: 'nueva_revista_id',
      pais: 'nuevo_pais_id',
      categoria: 'nueva_categoria_id',
      ambito: 'nuevo_ambito_id',
      editorial: 'nueva_editorial_id',
      autor: 'nuevo_autor_id',
      programaSeciti: 'nuevo_programa_id',
      ejeSecithi: 'nuevo_eje_id'
    };
    // 2. Retornar clave según entityType
    return paramMap[entityType];
  }
};

// =============================================================================
// FUNCIONES GLOBALES DE GUARDADO (Wrappers)
// =============================================================================

/**
 * Guarda una nueva revista desde el modal.
 * Pasos:
 * 1. Delegar a EntityManager.save con ruta journals/create
 * 2. Manejar feedback por dentro de EntityManager
 */
async function guardarRevista() {
  await EntityManager.save('revista', 'formNuevaRevista', '/journals/create/', 'nombre');
}

/**
 * Guarda un nuevo país desde el modal.
 * Pasos:
 * 1. Delegar a EntityManager.save con ruta create-country
 * 2. Manejar feedback por dentro de EntityManager
 */
async function guardarPais() {
  await EntityManager.save('pais', 'formGenerico', '/journals/create-country/', 'nombre');
}

/**
 * Guarda una nueva categoría desde el modal.
 * Pasos:
 * 1. Delegar a EntityManager.save con ruta create-category
 * 2. Manejar feedback por dentro de EntityManager
 */
async function guardarCategoria() {
  await EntityManager.save('categoria', 'formGenerico', '/journals/create-category/', 'nombre');
}

/**
 * Guarda un nuevo ámbito desde el modal.
 * Pasos:
 * 1. Delegar a EntityManager.save con ruta create-scope
 * 2. Manejar feedback por dentro de EntityManager
 */
async function guardarAmbito() {
  await EntityManager.save('ambito', 'formGenerico', '/journals/create-scope/', 'nombre');
}

/**
 * Guarda una nueva editorial desde el modal.
 * Pasos:
 * 1. Delegar a EntityManager.save con ruta create-publisher
 * 2. Manejar feedback por dentro de EntityManager
 */
async function guardarEditorial() {
  await EntityManager.save('editorial', 'formGenerico', '/journals/create-publisher/', 'nombre');
}

/**
 * Guarda un nuevo programa SECITI.
 * Pasos:
 * 1. Delegar a EntityManager.save con ruta create-program
 * 2. Manejar feedback por dentro de EntityManager
 */
async function guardarPrograma() {
  await EntityManager.save('programaSeciti', 'formGenerico', '/core/create-program/', 'nombre');
}

/**
 * Guarda un nuevo eje SECITHI.
 * Pasos:
 * 1. Delegar a EntityManager.save con ruta create-axis
 * 2. Manejar feedback por dentro de EntityManager
 */
async function guardarEje() {
  await EntityManager.save('ejeSecithi', 'formGenerico', '/core/create-axis/', 'nombre');
}

/**
 * Guarda un nuevo autor desde el modal.
 * Pasos:
 * 1. Delegar a EntityManager.save con ruta authors/create
 * 2. Manejar feedback por dentro de EntityManager
 */
async function guardarAutorDesdeModal() {
  await EntityManager.save('autor', 'formGenerico', '/authors/create/', 'nombre');
}

/**
 * Guarda un nuevo paper completo.
 * Pasos:
 * 1. Delegar a PaperManager.save
 * 2. Manejar feedback dentro de PaperManager
 */
async function guardarPaper() {
  await PaperManager.save();
}

// =============================================================================
// FUNCIONES GLOBALES DE GESTIÓN (Compatibilidad con HTML)
// =============================================================================

/**
 * Carga contenido dinámico en modal.
 * Pasos:
 * 1. Delegar a ModalManager.loadContent
 * 2. Propagar parámetros recibidos
 */
function cargarContenidoModal(url, title, size, footer, saveState) {
  return ModalManager.loadContent(url, title, size, footer, saveState);
}

/**
 * Vuelve a la vista anterior del modal.
 * Pasos:
 * 1. Delegar a ModalManager.pop
 * 2. Respetar historial de la pila
 */
function regresarAVistaAnterior() {
  ModalManager.pop();
}

/**
 * Carga roles de autores.
 * Pasos:
 * 1. Delegar a AuthorManager.loadRoles
 * 2. Retornar promesa para chaining
 */
function cargarRoles() {
  return AuthorManager.loadRoles();
}

/**
 * Busca autores en tabla local.
 * Pasos:
 * 1. Delegar a AuthorManager.searchLocal
 * 2. Mostrar toasts según resultados
 */
function buscarAutorLocal() {
  AuthorManager.searchLocal();
}

/**
 * Agrega un autor seleccionado.
 * Pasos:
 * 1. Delegar a AuthorManager.add
 * 2. Actualizar UI y campo hidden
 */
function agregarAutorSeleccionadoLocal(authorId, name, orcid) {
  AuthorManager.add(authorId, name, orcid);
}

/**
 * Elimina un autor seleccionado.
 * Pasos:
 * 1. Delegar a AuthorManager.remove
 * 2. Reordenar y refrescar UI
 */
function eliminarAutorSeleccionadoLocal(authorId) {
  AuthorManager.remove(authorId);
}

/**
 * Actualiza el rol de un autor.
 * Pasos:
 * 1. Delegar a AuthorManager.updateRole
 * 2. Sincronizar campo hidden
 */
function actualizarRolAutor(authorId, roleId) {
  AuthorManager.updateRole(authorId, roleId);
}

/**
 * Actualiza el orden de un autor.
 * Pasos:
 * 1. Delegar a AuthorManager.updateOrder
 * 2. Refrescar tabla y hidden
 */
function actualizarOrdenAutor(authorId, newOrder) {
  AuthorManager.updateOrder(authorId, newOrder);
}

/**
 * Inicializa el sistema de palabras clave.
 * Pasos:
 * 1. Delegar a KeywordManager.load
 * 2. Renderizar catálogo si aplica
 */
function inicializarPalabrasClave() {
  return KeywordManager.load();
}

/**
 * Selecciona una palabra clave existente.
 * Pasos:
 * 1. Delegar a KeywordManager.select
 * 2. Refrescar UI
 */
function seleccionarPalabraClave(keyword) {
  KeywordManager.select(keyword);
}

/**
 * Agrega una nueva palabra clave.
 * Pasos:
 * 1. Delegar a KeywordManager.addNew
 * 2. Validar, insertar y refrescar
 */
function agregarNuevaPalabraClave() {
  KeywordManager.addNew();
}

/**
 * Elimina una palabra clave seleccionada.
 * Pasos:
 * 1. Delegar a KeywordManager.remove
 * 2. Refrescar UI y hidden
 */
function eliminarPalabraClaveSeleccionada(index) {
  KeywordManager.remove(index);
}

/**
 * Muestra un toast de utilidad.
 * Pasos:
 * 1. Delegar a Utils.showToast
 * 2. Pasar parámetros directos
 */
function mostrarAlertaPersonalizada(message, type, duration) {
  Utils.showToast(message, type, duration);
}

// =============================================================================
// MODAL DE NUEVO PAPER
// =============================================================================

/**
 * Inicializa los listeners del formulario del paper.
 * Pasos:
 * 1. Inicializar palabras clave y roles
 * 2. Adjuntar listeners de verificación de edición
 * 3. Limpiar listeners duplicados previamente
 */
function initializePaperFormListeners() {
  // 1. Inicializar palabras clave y roles
  inicializarPalabrasClave();
  if (typeof cargarRoles === 'function') cargarRoles();

  // 2. Adjuntar listeners de verificación de edición
  const revistaSelect = document.getElementById('revistaSelect');
  const anioInput = document.getElementById('anioPublicacion');
  const volumenInput = document.getElementById('volumenRevista');
  const numeroInput = document.getElementById('numeroRevista');

  if (revistaSelect && anioInput && volumenInput && numeroInput) {
    const check = () => EditionManager.check();

    // 3. Limpiar listeners duplicados previamente
    revistaSelect.removeEventListener('change', check);
    anioInput.removeEventListener('blur', check);
    volumenInput.removeEventListener('blur', check);
    numeroInput.removeEventListener('blur', check);

    revistaSelect.addEventListener('change', check);
    anioInput.addEventListener('blur', check);
    volumenInput.addEventListener('blur', check);
    numeroInput.addEventListener('blur', check);
  }
}

/**
 * Abre el modal de registro de paper.
 * Pasos:
 * 1. Cargar contenido del modal con callback de init
 * 2. Manejar errores con toast
 */
async function abrirModalNuevoPaper() {
  try {
    // 1. Cargar contenido del modal con callback de init
    await ModalManager.loadContent(
      '/modal/new-paper/',
      'Registrar Nuevo Paper',
      'xl',
      '',
      false,
      initializePaperFormListeners
    );
  } catch (error) {
    // 2. Manejar errores con toast
    console.error('Error en abrirModalNuevoPaper:', error);
    Utils.showToast('No se pudo abrir el formulario.', 'danger');
  }
}

// =============================================================================
// ACTUALIZADORES DE SELECT
// =============================================================================

/**
 * Actualizar selects tras crear entidades relacionadas.
 * Pasos:
 * 1. Inyectar <option> si no existe
 * 2. Seleccionarlo por defecto y notificar con toast
 */
const SelectUpdater = {
  /**
   * Actualizar select de revistas.
   * Pasos:
   * 1. Localizar <select> de revista
   * 2. Insertar opción seleccionada si no existe
   */
  updateJournal(newJournal) {
    // 1. Localizar <select> de revista
    if (!newJournal) return;
    const select = document.getElementById('revistaSelect');
    if (!select) return;

    // 2. Insertar opción seleccionada si no existe
    const option = document.createElement('option');
    option.value = newJournal.id;
    option.textContent = newJournal.nombre;
    option.selected = true;
    select.appendChild(option);
    window.nuevaRevistaCreada = null;
  },

  /**
   * Actualizar select de editoriales.
   * Pasos:
   * 1. Delegar a helper genérico _updateSelect
   * 2. Limpiar bandera global
   */
  updatePublisher(newPublisher) {
    // 1. Delegar a helper genérico _updateSelect
    this._updateSelect('id_editorial', newPublisher, 'Editorial');
    // 2. Limpiar bandera global
    window.nuevaEditorialCreada = null;
  },

  /**
   * Actualizar select de países.
   * Pasos:
   * 1. Localizar <select> de país
   * 2. Insertar option si no existe y seleccionar
   * 3. Notificar con toast informativo
   */
  updateCountry(newCountry) {
    // 1. Localizar <select> de país
    if (!newCountry) return;
    const select = document.getElementById('id_pais_publicacion');
    if (!select) {
      console.warn('Select de país no encontrado.');
      return;
    }

    // 2. Insertar option si no existe y seleccionar
    const exists = Array.from(select.options).some(opt => opt.value == newCountry.id);
    if (!exists) {
      const option = document.createElement('option');
      option.value = newCountry.id;
      option.textContent = newCountry.nombre_completo || newCountry.nombre;
      option.selected = true;
      select.appendChild(option);

      // 3. Notificar con toast informativo
      Utils.showToast(`País "${option.textContent}" añadido.`, 'info', 2000);
    }
    window.nuevoPaisCreado = null;
  },

  /**
   * Actualizar select de categorías.
   * Pasos:
   * 1. Delegar a _updateSelect con id del campo
   * 2. Limpiar bandera global
   */
  updateCategory(newCategory) {
    this._updateSelect('id_categoria', newCategory, 'Categoría');
    window.nuevaCategoriaCreada = null;
  },

  /**
   * Actualizar select de ámbitos.
   * Pasos:
   * 1. Delegar a _updateSelect con id del campo
   * 2. Limpiar bandera global
   */
  updateScope(newScope) {
    this._updateSelect('id_ambito', newScope, 'Ámbito');
    window.nuevoAmbitoCreado = null;
  },

  /**
   * Actualizar select de programas.
   * Pasos:
   * 1. Delegar a _updateSelect con id del campo
   * 2. Limpiar bandera global
   */
  updateProgram(newProgram) {
    this._updateSelect('programaSeciti', newProgram, 'ProgramaSeciti');
    window.nuevoProgramaCreado = null;
  },

  /**
   * Actualizar select de ejes.
   * Pasos:
   * 1. Delegar a _updateSelect con id del campo
   * 2. Limpiar bandera global
   */
  updateAxis(newAxis) {
    this._updateSelect('ejeSecithi', newAxis, 'EjeSecithi');
    window.nuevoEjeCreado = null;
  },

  /**
   * Helper genérico para actualizar selects.
   * Pasos:
   * 1. Localizar select por id
   * 2. Insertar opción si no existe
   * 3. Seleccionar y notificar
   */
  _updateSelect(selectId, newEntity, entityName) {
    // 1. Localizar select por id
    if (!newEntity) return;
    const select = document.getElementById(selectId);
    if (!select) {
      console.warn(`Select ${selectId} no encontrado.`);
      return;
    }

    // 2. Insertar opción si no existe
    const exists = Array.from(select.options).some(opt => opt.value == newEntity.id);
    if (!exists) {
      const option = document.createElement('option');
      option.value = newEntity.id;
      option.textContent = newEntity.nombre;
      option.selected = true;
      select.appendChild(option);

      // 3. Seleccionar y notificar
      Utils.showToast(`${entityName} "${newEntity.nombre}" añadida.`, 'info', 2000);
    } else {
      console.warn(`${entityName} con ID ${newEntity.id} ya existe.`);
    }
  }
};

/**
 * Actualizar select de revistas (wrapper).
 * Pasos:
 * 1. Delegar a SelectUpdater.updateJournal
 * 2. Pasar objeto recibido tal cual
 */
function actualizarSelectRevistas(newJournal) {
  SelectUpdater.updateJournal(newJournal);
}

/**
 * Actualizar select de editoriales (wrapper).
 * Pasos:
 * 1. Delegar a SelectUpdater.updatePublisher
 * 2. Pasar objeto recibido tal cual
 */
function actualizarSelectEditorial(newPublisher) {
  SelectUpdater.updatePublisher(newPublisher);
}

/**
 * Actualizar select de países (wrapper).
 * Pasos:
 * 1. Delegar a SelectUpdater.updateCountry
 * 2. Pasar objeto recibido tal cual
 */
function actualizarSelectPais(newCountry) {
  SelectUpdater.updateCountry(newCountry);
}

/**
 * Actualizar select de categorías (wrapper).
 * Pasos:
 * 1. Delegar a SelectUpdater.updateCategory
 * 2. Pasar objeto recibido tal cual
 */
function actualizarSelectCategoria(newCategory) {
  SelectUpdater.updateCategory(newCategory);
}

/**
 * Actualizar select de ámbitos (wrapper).
 * Pasos:
 * 1. Delegar a SelectUpdater.updateScope
 * 2. Pasar objeto recibido tal cual
 */
function actualizarSelectAmbito(newScope) {
  SelectUpdater.updateScope(newScope);
}

/**
 * Actualizar select de programas (wrapper).
 * Pasos:
 * 1. Delegar a SelectUpdater.updateProgram
 * 2. Pasar objeto recibido tal cual
 */
function actualizarSelectPrograma(newProgram) {
  SelectUpdater.updateProgram(newProgram);
}

/**
 * Actualizar select de ejes (wrapper).
 * Pasos:
 * 1. Delegar a SelectUpdater.updateAxis
 * 2. Pasar objeto recibido tal cual
 */
function actualizarSelectEje(newAxis) {
  SelectUpdater.updateAxis(newAxis);
}


/**
 * Visualiza los detalles de un paper en un modal dinámico.
 * @param {number} paperId - ID del paper a visualizar.
 */
function viewPaper(paperId) {
    if (!paperId) {
        Utils.showToast('ID de paper no válido.', 'danger');
        return;
    }
    const url = `/publications/paper/${paperId}/detail/`;
    ModalManager.loadContent(url, 'Detalles del Paper', 'xl');
}
// =============================================================================
//  TODO: FUNCIONALIDADES PENDIENTES
// =============================================================================

/**
 * Edita un paper existente (pendiente).
 * Pasos:
 * 1. Mostrar toast de funcionalidad no implementada
 * 2. Mantener compatibilidad con UI
 */
function editPaper() {
  Utils.showToast('Funcionalidad no implementada.', 'warning');
}

/**
 * Genera reporte de publicaciones (pendiente).
 * Pasos:
 * 1. Mostrar toast de funcionalidad no implementada
 * 2. Mantener compatibilidad con UI
 */
function generateReport() {
  Utils.showToast('Funcionalidad no implementada.', 'warning');
}
// =============================================================================
// MÓDULO DE GESTIÓN DE ACTUALIZACIONES
// =============================================================================

/**
 * Gestiona el proceso de actualización de la aplicación.
 * @namespace UpdateManager
 */
const UpdateManager = {
  /**
   * Inicia el proceso de actualización.
   * Pasos:
   * 1. Notificar inicio de actualización
   * 2. Abrir changelog en nueva pestaña
   * 3. Enviar solicitud POST al backend
   * 4. Parsear respuesta JSON
   * 5. Notificar éxito si la actualización fue aplicada
   * 6. Notificar error si el backend responde con fallo
   * 7. Notificar error de red en caso de excepción
   * @param {string} changelogUrl - La URL de la página de lanzamientos de GitHub.
   */
  async applyUpdate(changelogUrl) {
    // 1. Notificar inicio de actualización
    Utils.showToast('Iniciando actualización... No cierres la aplicación.', 'info', 8000);

    // 2. Abrir changelog en nueva pestaña
    window.open(changelogUrl, '_blank');

    try {
      // 3. Enviar solicitud POST al backend
      const response = await fetch('/core/apply-update/', {
        method: 'POST',
        headers: {
          'X-CSRFToken': Utils.getCookie('csrftoken'),
          'X-Requested-With': 'XMLHttpRequest'
        }
      });

      // 4. Parsear respuesta JSON
      const data = await response.json();

      if (response.ok && data.success) {
        // 5. Notificar éxito
        Utils.showToast(`✅ ${data.message}`, 'success', 15000);
      } else {
        // 6. Notificar error del backend
        Utils.showToast(`❌ Error: ${data.message}`, 'danger', 15000);
        console.error('Detalles del error desde el servidor:', data.output || data.message);
      }
    } catch (error) {
      // 7. Notificar error de red
      console.error('Error de red al intentar actualizar:', error);
      Utils.showToast('❌ Error de conexión al intentar actualizar. Revisa la consola del servidor.', 'danger', 10000);
    }
  }
};

// =============================================================================
// INICIALIZACIÓN
// =============================================================================

/**
 * Inicializar aplicación al cargar el DOM.
 * Pasos:
 * 1. Exponer objeto global PublishTracker y sincronizar pila
 * 2. Activar autosubmit en selects de filtros
 * 3. Inicializar tooltips de Bootstrap
 * 4. Exponer módulos al scope global para debugging
 */
document.addEventListener('DOMContentLoaded', () => {
  // 1. Exponer objeto global PublishTracker y sincronizar pila
  window.PublishTracker = {
    baseUrl: window.location.origin,
    modalStack: ModalManager.stack
  };
  ModalManager.stack = window.PublishTracker.modalStack;

  // 2. Activar autosubmit en selects de filtros
  document.querySelectorAll('select[name="status"], select[name="year"]').forEach(select => {
    select.addEventListener('change', () => {
      const form = select.closest('form');
      if (form) form.submit();
    });
  });

  // 3. Inicializar tooltips de Bootstrap
  document.querySelectorAll('[data-bs-toggle="tooltip"]').forEach(el => {
    new bootstrap.Tooltip(el);
  });

  // 4. Exponer módulos al scope global para debugging
  if (typeof window !== 'undefined') {
    window.PublishTracker.Utils = Utils;
    window.PublishTracker.ModalManager = ModalManager;
    window.PublishTracker.AuthorManager = AuthorManager;
    window.PublishTracker.KeywordManager = KeywordManager;
    window.PublishTracker.PaperManager = PaperManager;
    window.PublishTracker.EntityManager = EntityManager;
    window.PublishTracker.SelectUpdater = SelectUpdater;
  }

  console.log('✅ PublishTracker inicializado correctamente');
});

// =============================================================================
// MÓDULO DE GESTIÓN DE EDICIÓN DE REVISTA (VERSIÓN ACTUALIZADA)
// =============================================================================

/**
 * Asistente de edición de revista compartida.
 * Pasos:
 * 1. Verificar si existe la edición con parámetros clave
 * 2. Renderizar UI para archivos requeridos
 * 3. Permitir reemplazo/cancelación de archivos existentes
 */
const EditionManager = {
  /**
   * Verificar existencia de edición y preparar UI.
   * Pasos:
   * 1. Leer revista, año, volumen y número
   * 2. Ocultar/mostrar contenedor según completitud
   * 3. Consultar API /journals/api/verificar-edicion/
   * 4. Renderizar respuesta o mostrar error
   */
  async check() {
    // 1. Leer revista, año, volumen y número
    const revistaId = document.getElementById('revistaSelect')?.value;
    const anio = document.getElementById('anioPublicacion')?.value;
    const volumen = document.getElementById('volumenRevista')?.value;
    const numero = document.getElementById('numeroRevista')?.value;

    // 2. Ocultar/mostrar contenedor según completitud
    const container = document.getElementById('edicionArchivosContainer');
    if (!revistaId || !anio || !volumen || !numero) {
      container.style.display = 'none';
      return;
    }
    container.style.display = 'block';
    container.innerHTML = `<p class="text-center text-muted"><div class="spinner-border spinner-border-sm" role="status"></div> Verificando edición...</p>`;

    try {
      // 3. Consultar API /journals/api/verificar-edicion/
      const url = `/journals/api/verificar-edicion/?revista_id=${revistaId}&anio=${anio}&volumen=${volumen}&numero=${numero}`;
      const response = await fetch(url);
      if (!response.ok) throw new Error(`Error del servidor: ${response.statusText}`);
      const data = await response.json();

      // 4. Renderizar respuesta o mostrar error
      if (data.success) {
        this.renderUI(data);
      } else {
        container.innerHTML = `<p class="text-danger">Error: ${data.error || 'Desconocido'}</p>`;
      }
    } catch (error) {
      console.error("Error en EditionManager.check:", error);
      container.innerHTML = `<p class="text-danger">No se pudo conectar con el servidor.</p>`;
    }
  },

  /**
   * Renderizar inputs e información de archivos de edición.
   * Pasos:
   * 1. Preparar banner según exista o no la edición
   * 2. Iterar tipos requeridos y pintar estado/input
   * 3. Inyectar el HTML en el contenedor
   */
  renderUI(data) {
    // 1. Preparar banner según exista o no la edición
    const container = document.getElementById('edicionArchivosContainer');
    let html = '';
    const tiposRequeridos = ['Portada', 'Hoja Legal', 'Indice de Paper'];

    if (data.edicion_existe) {
      html += `<h6><i class="fas fa-check-circle text-success"></i> Edición Encontrada</h6>`;
      html += `<p class="small text-muted mb-2">La documentación de esta edición se compartirá entre artículos.</p>`;
    } else {
      html += `<h6><i class="fas fa-star text-info"></i> Nueva Edición Detectada</h6>`;
      html += `<p class="small text-muted mb-2">Por favor, adjunta los documentos requeridos.</p>`;
    }

    // 2. Iterar tipos requeridos y pintar estado/input
    tiposRequeridos.forEach(tipo => {
      const archivo = data.archivos[tipo];
      const inputName = `archivo_edicion_${tipo.toLowerCase().replace(/\s+/g, '_')}`;

      if (archivo) {
        html += `
          <div class="mb-3">
            <label class="form-label small fw-bold">${tipo}:</label>
            <div id="info_${inputName}" class="alert alert-success p-2 small d-flex justify-content-between align-items-center">
              <span>
                <i class="fas fa-check-circle me-2"></i>
                <strong>${archivo.nombre}</strong>
                <span class="badge bg-success ms-2">Ya cargado</span>
              </span>
              <span>
                <a href="${archivo.url}" target="_blank" class="btn btn-sm btn-outline-secondary py-0 px-2 me-1" title="Ver archivo">
                  <i class="fas fa-eye"></i> Ver
                </a>
                <button type="button" class="btn btn-sm btn-outline-warning py-0 px-2" title="Reemplazar" 
                        onclick="EditionManager.toggleReplaceUI('${inputName}', true)">
                  <i class="fas fa-sync-alt"></i> Reemplazar
                </button>
              </span>
            </div>
            <div id="upload_${inputName}" style="display: none;">
              <input class="form-control form-control-sm" type="file" id="${inputName}" name="${inputName}">
              <button type="button" class="btn btn-sm btn-link text-muted py-0 px-0 mt-1" 
                      onclick="EditionManager.toggleReplaceUI('${inputName}', false)">
                <i class="fas fa-times"></i> Cancelar reemplazo
              </button>
            </div>
          </div>`;
      } else {
        html += `
          <div class="mb-3">
            <label for="${inputName}" class="form-label small fw-bold">
              ${tipo}: <span class="text-danger">* Requerido</span>
            </label>
            <input class="form-control form-control-sm" type="file" id="${inputName}" name="${inputName}" required>
            <small class="text-muted">Este documento es necesario para crear la edición.</small>
          </div>`;
      }
    });

    // 3. Inyectar el HTML en el contenedor
    container.innerHTML = html;
  },

  /**
   * Alternar UI de reemplazo de archivo.
   * Pasos:
   * 1. Localizar bloques informativos y de carga
   * 2. Alternar visibilidad según acción
   * 3. Limpiar input si se cancela reemplazo
   */
  toggleReplaceUI(baseName, showUpload) {
    // 1. Localizar bloques informativos y de carga
    const infoDiv = document.getElementById(`info_${baseName}`);
    const uploadDiv = document.getElementById(`upload_${baseName}`);

    // 2. Alternar visibilidad según acción
    if (showUpload) {
      infoDiv.style.display = 'none';
      uploadDiv.style.display = 'block';
    } else {
      infoDiv.style.display = 'flex';
      uploadDiv.style.display = 'none';
      // 3. Limpiar input si se cancela reemplazo
      const fileInput = document.getElementById(baseName);
      if (fileInput) fileInput.value = '';
    }
  }
};
