/**
 * PublishTracker - Sistema de Gestión de Publicaciones Académicas
 * Versión refactorizada con JSDoc completo y mejores prácticas
 * @author Edwin Campos Dragusin
 * @version 2.0.0
 */

// =============================================================================
// MÓDULO DE UTILIDADES
// =============================================================================

/**
 * Módulo de utilidades generales para operaciones comunes
 * @namespace Utils
 */
const Utils = {
  /**
   * Obtiene el valor de una cookie por su nombre
   * @param {string} name - Nombre de la cookie a buscar
   * @returns {string|null} Valor decodificado de la cookie o null si no existe
   * @example
   * const token = Utils.getCookie('csrftoken');
   */
  getCookie(name) {
    if (!document.cookie) return null;

    const cookies = document.cookie.split(';');
    for (let cookie of cookies) {
      cookie = cookie.trim();
      if (cookie.startsWith(`${name}=`)) {
        return decodeURIComponent(cookie.substring(name.length + 1));
      }
    }
    return null;
  },

  /**
   * Muestra un mensaje toast de Bootstrap
   * @param {string} message - Mensaje a mostrar
   * @param {('info'|'success'|'warning'|'danger')} [type='info'] - Tipo de alerta
   * @param {number} [duration=3000] - Duración en milisegundos
   * @example
   * Utils.showToast('Guardado exitoso', 'success', 2000);
   */
  showToast(message, type = 'info', duration = 3000) {
    let container = document.getElementById('custom-alert-container');

    if (!container) {
      container = document.createElement('div');
      container.id = 'custom-alert-container';
      container.className = 'position-fixed top-0 end-0 p-3';
      container.style.zIndex = '2000';
      document.body.appendChild(container);
    }

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

    const toastElement = document.getElementById(alertId);
    const toast = new bootstrap.Toast(toastElement, { autohide: true, delay: duration });

    toastElement.addEventListener('hidden.bs.toast', () => toastElement.remove());
    toast.show();
  },

  /**
   * Valida que un valor sea un número válido y opcionalmente mayor que un mínimo
   * @param {*} value - Valor a validar
   * @param {number} [min=0] - Valor mínimo permitido
   * @returns {boolean} true si el valor es un número válido >= min
   * @example
   * Utils.isValidNumber('42', 0); // true
   * Utils.isValidNumber('-5', 0); // false
   */
  isValidNumber(value, min = 0) {
    const num = Number(value);
    return !isNaN(num) && num >= min;
  },

  /**
   * Valida que un rango de valores sea consistente (inicio <= fin)
   * @param {*} start - Valor de inicio
   * @param {*} end - Valor de fin
   * @returns {boolean} true si ambos son números válidos y start <= end
   * @example
   * Utils.isValidRange(10, 20); // true
   * Utils.isValidRange(20, 10); // false
   */
  isValidRange(start, end) {
    return this.isValidNumber(start, 1) &&
      this.isValidNumber(end, 1) &&
      Number(start) <= Number(end);
  }
};

// =============================================================================
// MÓDULO DE GESTIÓN DE MODALES
// =============================================================================

/**
 * Gestiona el sistema de modales dinámicos con pila de navegación
 * Permite cargar contenido AJAX, navegar entre vistas y mantener estado
 * @namespace ModalManager
 */
const ModalManager = {
  /**
   * Pila de vistas del modal (historial de navegación)
   * @type {Array<{title: string, content: string, footer: string, size: string, formData: Object}>}
   */
  stack: [],

  /**
   * Carga contenido dinámico en el modal mediante AJAX
   * @async
   * @param {string} url - URL del endpoint que devuelve el contenido
   * @param {string} title - Título del modal
   * @param {string} [size=''] - Tamaño del modal ('sm', 'lg', 'xl')
   * @param {string} [footer=''] - HTML del footer del modal
   * @param {boolean} [saveState=true] - Si debe guardar el estado del formulario actual
   * @returns {Promise<void>}
   * @example
   * await ModalManager.loadContent('/modal/form/', 'Nuevo Registro', 'lg');
   */
  async loadContent(url, title, size = '', footer = '', saveState = true,onRendered=null) {
    const modal = document.getElementById('dynamicModal');
    if (!modal) {
      Utils.showToast('Error: Modal no encontrado.', 'danger');
      return;
    }

    if (saveState && this.stack.length > 0) {
      this._backupFormData();
    }

    this._showLoadingState();
    this._showModal(modal);

    try {
      const response = await fetch(url, {
        method: 'GET',
        headers: { 'X-Requested-With': 'XMLHttpRequest' }
      });

      if (!response.ok) throw new Error(`Error HTTP: ${response.status}`);

      const content = await response.text();
      this.push(title, content, size, footer,onRendered);

    } catch (error) {
      console.error('Error al cargar contenido del modal:', error);
      const errorContent = `
        <div class="alert alert-danger">
          <h5><i class="fas fa-exclamation-triangle"></i> Error al cargar</h5>
          <p>No se pudo cargar el contenido. ${error.message}</p>
          <button class="btn btn-outline-secondary btn-sm" 
                  onclick="ModalManager.pop()">← Volver</button>
        </div>
      `;
      this.push(title, errorContent, size, footer);
    }
  },

  /**
   * Añade una nueva vista a la pila del modal y la muestra
   * @param {string} title - Título de la vista
   * @param {string} content - Contenido HTML de la vista
   * @param {string} [size=''] - Tamaño del modal
   * @param {string} [footer=''] - HTML del footer
   * @example
   * ModalManager.push('Mi Título', '<p>Contenido</p>', 'lg');
   */
  push(title, content, size = '', footer = '',onRendered=null) {
    this.stack.push({
      title,
      content,
      footer,
      size,
      formData: null
    });

    this._renderCurrentView().then(() => {
      // Ejecutar callback después de renderizar
      if (typeof onRendered === 'function') {
        onRendered();
      }
    });
    this._ensureModalVisible();
  },

  /**
   * Regresa a la vista anterior en la pila del modal
   * Si no hay vistas anteriores, muestra una advertencia
   * @example
   * ModalManager.pop(); // Vuelve atrás
   */
  pop() {
    if (this.stack.length <= 1) {
      console.warn('No hay vistas anteriores.');
      return;
    }

    this.stack.pop();
    this._renderCurrentView();
  },

  /**
   * Muestra un spinner de carga en el cuerpo del modal
   * @private
   */
  _showLoadingState() {
    const loadingContent = `
      <div class="text-center py-4">
        <div class="spinner-border text-primary" role="status">
          <span class="visually-hidden">Cargando...</span>
        </div>
        <p class="mt-2">Cargando contenido...</p>
      </div>
    `;
    document.getElementById('modalBody').innerHTML = loadingContent;
  },

  /**
   * Muestra el modal de Bootstrap si no está visible
   * @private
   * @param {HTMLElement} modal - Elemento DOM del modal
   */
  _showModal(modal) {
    let modalInstance = bootstrap.Modal.getInstance(modal);
    if (!modalInstance) {
      modalInstance = new bootstrap.Modal(modal, { backdrop: true, keyboard: true });
    }
    if (!modal.classList.contains('show')) {
      modalInstance.show();
    }
  },

  /**
   * Asegura que el modal esté visible (versión sin parámetro)
   * @private
   */
  _ensureModalVisible() {
    const modal = document.getElementById('dynamicModal');
    if (!modal) return;

    let modalInstance = bootstrap.Modal.getInstance(modal);
    if (!modalInstance) {
      modalInstance = new bootstrap.Modal(modal, { backdrop: true, keyboard: true });
    }
    if (!modal.classList.contains('show')) {
      modalInstance.show();
    }
  },

  /**
   * Guarda el estado actual de todos los campos del formulario en la pila
   * @private
   */
  _backupFormData() {
    const currentBody = document.getElementById('modalBody');
    if (!currentBody || this.stack.length === 0) return;

    const form = currentBody.querySelector('form');
    const inputs = form
      ? form.querySelectorAll('input, select, textarea')
      : currentBody.querySelectorAll('input, select, textarea');

    if (!inputs.length) {
      this.stack[this.stack.length - 1].formData = {};
      return;
    }

    const formData = {};
    inputs.forEach(input => {
      if (input.name) {
        formData[input.name] = ['checkbox', 'radio'].includes(input.type)
          ? input.checked
          : input.value;
      }
    });

    this.stack[this.stack.length - 1].formData = formData;
  },

  /**
   * Renderiza la vista actual de la pila con animaciones
   * @private
   * @async
   * @returns {Promise<void>}
   */
  async _renderCurrentView() {
    if (this.stack.length === 0) return;

    const current = this.stack[this.stack.length - 1];
    const elements = {
      title: document.getElementById('modalTitle'),
      body: document.getElementById('modalBody'),
      footer: document.getElementById('footer')
    };

    await this._animateOut(elements);
    this._updateContent(elements, current);
    this._restoreFormData(elements.body, current.formData);
  },

  /**
   * Anima la salida del contenido actual con fadeOut
   * @private
   * @async
   * @param {Object} elements - Objetos DOM de título, body y footer
   * @returns {Promise<void>}
   */
  async _animateOut(elements) {
    const promises = [];

    ['body', 'title'].forEach(key => {
      const content = elements[key]?.firstElementChild;
      if (content && content.nodeType === 1) {
        content.classList.add('animate__animated', 'animate__fadeOut');
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
   * Actualiza el contenido del modal con la vista actual
   * @private
   * @param {Object} elements - Elementos DOM del modal
   * @param {Object} current - Vista actual de la pila
   */
  _updateContent(elements, current) {
    // Título
    if (elements.title) {
      elements.title.innerHTML = '';
      const titleSpan = document.createElement('span');
      titleSpan.textContent = current.title;
      titleSpan.classList.add('animate__animated', 'animate__fadeIn');
      elements.title.appendChild(titleSpan);
    }

    // Cuerpo
    if (elements.body) {
      elements.body.innerHTML = '';
      const bodyDiv = document.createElement('div');
      bodyDiv.innerHTML = current.content;
      bodyDiv.classList.add('animate__animated', 'animate__fadeIn');
      elements.body.appendChild(bodyDiv);
    }

    // Footer
    if (elements.footer) {
      elements.footer.innerHTML = current.footer || '';
      elements.footer.style.display = current.footer ? 'block' : 'none';
    }
  },

  /**
   * Restaura los valores guardados en los campos del formulario
   * @private
   * @param {HTMLElement} bodyElement - Elemento body del modal
   * @param {Object} formData - Datos del formulario guardados
   */
  _restoreFormData(bodyElement, formData) {
    if (!formData || !bodyElement) return;

    const container = bodyElement.firstElementChild;
    if (!container) return;

    const inputs = container.querySelectorAll('input, select, textarea');
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
 * Gestiona la selección y configuración de autores para un paper
 * Permite buscar, agregar, eliminar y asignar roles a autores
 * @namespace AuthorManager
 */
const AuthorManager = {
  /**
   * Lista de autores seleccionados para el paper actual
   * @type {Array<{autor_id: number, nombre: string, orcid: string, orden: number, rol_id: number|null}>}
   */
  selected: [],

  /**
   * Lista de roles disponibles cargados desde el servidor
   * @type {Array<{id: number, nombre_rol: string}>}
   */
  roles: [],

  /**
   * Carga la lista de roles disponibles desde el servidor
   * @async
   * @returns {Promise<void>}
   * @example
   * await AuthorManager.loadRoles();
   */
  async loadRoles() {
    try {
      const res = await fetch('/authors/api/roles/');
      const data = await res.json();
      if (data.success) this.roles = data.roles;
    } catch (err) {
      console.error('Error al cargar roles:', err);
    }
  },

  /**
   * Busca autores localmente en la tabla de disponibles
   * Filtra por nombre u ORCID según el término ingresado
   * @example
   * AuthorManager.searchLocal();
   */
  searchLocal() {
    const query = document.getElementById('buscarAutor')?.value.trim().toLowerCase();
    if (!query) {
      Utils.showToast('Ingrese un nombre o ORCID.');
      return;
    }

    const rows = document.querySelectorAll('#autoresDisponibles tr');
    let found = 0;

    rows.forEach(row => {
      const name = row.querySelector('td:first-child')?.textContent.toLowerCase() || '';
      const orcid = row.querySelector('td:nth-child(2)')?.textContent.toLowerCase() || '';
      const matches = name.includes(query) || orcid.includes(query);

      row.style.display = matches ? '' : 'none';
      if (matches) found++;
    });

    if (found === 0) {
      Utils.showToast('No se encontraron autores.');
    }
  },

  /**
   * Agrega un autor a la lista de seleccionados
   * @param {number} authorId - ID del autor
   * @param {string} name - Nombre completo del autor
   * @param {string} orcid - Identificador ORCID del autor
   * @example
   * AuthorManager.add(123, 'Juan Pérez', '0000-0001-2345-6789');
   */
  add(authorId, name, orcid) {
    if (this.selected.some(a => a.autor_id === authorId)) {
      Utils.showToast('Autor ya seleccionado.');
      return;
    }

    this.selected.push({
      autor_id: authorId,
      nombre: name,
      orcid,
      orden: this.selected.length + 1,
      rol_id: null
    });

    this._updateUI(authorId);
  },

  /**
   * Elimina un autor de la lista de seleccionados
   * Reordena automáticamente los autores restantes
   * @param {number} authorId - ID del autor a eliminar
   * @example
   * AuthorManager.remove(123);
   */
  remove(authorId) {
    this.selected = this.selected.filter(a => a.autor_id !== authorId);
    this.selected.forEach((a, i) => a.orden = i + 1);
    this._updateUI(authorId, true);
  },

  /**
   * Actualiza el rol asignado a un autor
   * @param {number} authorId - ID del autor
   * @param {number|string} roleId - ID del rol a asignar
   * @example
   * AuthorManager.updateRole(123, 1);
   */
  updateRole(authorId, roleId) {
    const author = this.selected.find(a => a.autor_id === authorId);
    if (author) {
      author.rol_id = roleId || null;
      this._updateHiddenField();
    }
  },

  /**
   * Actualiza el orden de aparición de un autor
   * Reordena automáticamente toda la lista
   * @param {number} authorId - ID del autor
   * @param {number|string} newOrder - Nuevo orden (posición)
   * @example
   * AuthorManager.updateOrder(123, 2);
   */
  updateOrder(authorId, newOrder) {
    const author = this.selected.find(a => a.autor_id === authorId);
    if (author) {
      author.orden = parseInt(newOrder, 10);
      this.selected.sort((a, b) => a.orden - b.orden);
      this._updateUI();
    }
  },

  /**
   * Actualiza toda la interfaz de autores (tabla, lista disponible, campo hidden)
   * @private
   * @param {number} [authorId=null] - ID del autor afectado
   * @param {boolean} [removed=false] - Si el autor fue eliminado
   */
  _updateUI(authorId = null, removed = false) {
    this._updateTable();
    if (authorId) this._updateAvailableList(authorId, removed);
    this._updateHiddenField();
  },

  /**
   * Actualiza la tabla de autores seleccionados
   * @private
   */
  _updateTable() {
    const tbody = document.getElementById('autoresSeleccionados');
    if (!tbody) return;

    const roleOptions = this.roles
      .map(r => `<option value="${r.id}">${r.nombre_rol}</option>`)
      .join('');

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
   * Actualiza la visibilidad de un autor en la lista de disponibles
   * @private
   * @param {number} authorId - ID del autor
   * @param {boolean} show - Si debe mostrarse
   */
  _updateAvailableList(authorId, show) {
    const row = document.querySelector(`#autoresDisponibles tr[data-autor-id="${authorId}"]`);
    if (row) {
      row.style.display = show ? '' : 'none';
    }
  },

  /**
   * Actualiza el campo hidden con los datos JSON de autores seleccionados
   * @private
   */
  _updateHiddenField() {
    const field = document.getElementById('autoresSeleccionadosData');
    if (field) {
      field.value = JSON.stringify(this.selected);
    }
  },

  /**
   * Valida que haya al menos un autor seleccionado y todos tengan rol
   * @returns {boolean} true si la validación es exitosa
   * @example
   * if (AuthorManager.validate()) { // proceder }
   */
  validate() {
    if (this.selected.length === 0) {
      Utils.showToast('Debe seleccionar al menos un autor.', 'danger');
      return false;
    }

    if (this.selected.some(a => !a.rol_id)) {
      Utils.showToast('Todos los autores deben tener un rol asignado.', 'danger');
      return false;
    }

    return true;
  }
};

// =============================================================================
// MÓDULO DE GESTIÓN DE PALABRAS CLAVE
// =============================================================================

/**
 * Gestiona las palabras clave asociadas a un paper
 * Permite cargar, seleccionar, crear y eliminar palabras clave
 * @namespace KeywordManager
 */
const KeywordManager = {
  /**
   * Palabras clave seleccionadas para el paper actual
   * @type {Array<{id: number|null, nombre: string}>}
   */
  selected: [],

  /**
   * Palabras clave disponibles en el sistema
   * @type {Array<{id: number, nombre: string}>}
   */
  available: [],

  /**
   * Carga las palabras clave disponibles desde el servidor
   * @async
   * @returns {Promise<void>}
   * @example
   * await KeywordManager.load();
   */
  async load() {
    try {
      const res = await fetch('/api/palabras-clave/');
      const data = await res.json();
      if (data.success) {
        this.available = data.palabras_clave;
        // Renderizar solo si el contenedor existe
        const container = document.getElementById('palabrasClaveDisponibles');
        if (container) {
          this._renderAvailable();
        }
      }
    } catch (err) {
      console.error('Error al cargar palabras clave:', err);
    }
  },

  /**
   * Selecciona una palabra clave existente
   * @param {{id: number, nombre: string}} keyword - Palabra clave a seleccionar
   * @example
   * KeywordManager.select({ id: 1, nombre: 'Machine Learning' });
   */
  select(keyword) {
    const exists = this.selected.some(k =>
      (k.id && k.id === keyword.id) || (k.nombre === keyword.nombre)
    );

    if (exists) {
      Utils.showToast('Palabra clave ya seleccionada.');
      return;
    }

    this.selected.push({ id: keyword.id, nombre: keyword.nombre });
    this._updateUI();
  },

  /**
   * Agrega una nueva palabra clave personalizada
   * Lee el valor del input y la agrega si es válida
   * @example
   * KeywordManager.addNew();
   */
  addNew() {
    const input = document.getElementById('palabrasClaveInput');
    const value = input?.value.trim();

    if (!value) {
      Utils.showToast('Ingrese una palabra clave.');
      return;
    }

    const existsInAvailable = this.available.some(
      k => k.nombre.toLowerCase() === value.toLowerCase()
    );
    const existsInSelected = this.selected.some(
      k => k.nombre.toLowerCase() === value.toLowerCase()
    );

    if (existsInAvailable) {
      Utils.showToast('Ya existe. Selecciónela de la lista.');
      return;
    }

    if (existsInSelected) {
      Utils.showToast('Ya está seleccionada.');
      return;
    }

    this.selected.push({ id: null, nombre: value });
    this._updateUI();
    input.value = '';
  },

  /**
   * Elimina una palabra clave seleccionada por índice
   * @param {number} index - Índice de la palabra clave en el array selected
   * @example
   * KeywordManager.remove(2);
   */
  remove(index) {
    this.selected.splice(index, 1);
    this._updateUI();
  },

  /**
   * Crea en el servidor las palabras clave nuevas que no existen
   * Actualiza los IDs de las palabras clave creadas exitosamente
   * @async
   * @returns {Promise<void>}
   * @example
   * await KeywordManager.createNewKeywords();
   */
  async createNewKeywords() {
    const newKeywords = this.selected.filter(k =>
      !k.id && !this.available.some(
        a => a.nombre.toLowerCase() === k.nombre.toLowerCase()
      )
    );

    for (const keyword of newKeywords) {
      try {
        const res = await fetch('/api/palabras-clave/create/', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': window.PublishTracker.csrfToken,
            'X-Requested-With': 'XMLHttpRequest'
          },
          body: JSON.stringify({ nombre: keyword.nombre.toLowerCase() })
        });

        const data = await res.json();
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
   * Actualiza toda la interfaz de palabras clave
   * @private
   */
  _updateUI() {
    this._renderSelected();
    this._renderAvailable();
    this._updateHiddenField();
  },

  /**
   * Renderiza las palabras clave seleccionadas como badges
   * @private
   */
  _renderSelected() {
    const container = document.getElementById('palabrasClaveSeleccionadas');
    if (!container) return;

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
   * Renderiza las palabras clave disponibles para selección
   * @private
   */
  _renderAvailable() {
    const container = document.getElementById('palabrasClaveDisponibles');
    if (!container) {
      console.warn('Contenedor de palabras clave disponibles no encontrado');
      return;
    }

    container.innerHTML = '';
    this.available.forEach(keyword => {
      const isSelected = this.selected.some(k =>
        (k.id && k.id === keyword.id) || (k.nombre === keyword.nombre)
      );

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
   * Actualiza el campo hidden con los datos JSON de palabras clave
   * @private
   */
  _updateHiddenField() {
    const field = document.getElementById('palabrasClaveData');
    if (field) {
      field.value = JSON.stringify(this.selected);
    }
  },

  /**
   * Valida que haya al menos una palabra clave seleccionada
   * @returns {boolean} true si hay al menos una palabra clave
   * @example
   * if (KeywordManager.validate()) { // proceder }
   */
  validate() {
    if (this.selected.length === 0) {
      Utils.showToast('Debe agregar al menos una palabra clave.', 'danger');
      return false;
    }
    return true;
  }
};

// =============================================================================
// MÓDULO DE GESTIÓN DE PAPERS
// =============================================================================

/**
 * Gestiona el proceso completo de creación y guardado de papers
 * Coordina la recolección de datos, validaciones y envío al servidor
 * @namespace PaperManager
 */
const PaperManager = {
  /**
   * Guarda un nuevo paper con todos sus datos asociados
   * Orquesta todo el proceso: validación, generación de referencia y envío
   * @async
   * @returns {Promise<void>}
   * @example
   * await PaperManager.save();
   */
  async save() {
    const fields = this._collectFields();

    if (!this._validateAll(fields)) return;

    const journalName = document.querySelector('#revistaSelect option:checked')?.textContent || '';
    const apaReference = this._generateAPAReference({ ...fields, nombreRevista: journalName });

    try {
      await this._submitData(fields, apaReference);
    } catch (error) {
      console.error('Error al guardar el paper:', error);
      Utils.showToast(`❌ ${error.message}`, 'danger');
    }
  },

  /**
   * Recolecta todos los campos del formulario de nuevo paper
   * @private
   * @returns {Object} Objeto con todos los campos del paper
   */
  _collectFields() {
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
   * Ejecuta todas las validaciones necesarias
   * @private
   * @param {Object} fields - Campos del formulario
   * @returns {boolean} true si todas las validaciones pasan
   */
  _validateAll(fields) {
    return this._validateRequired(fields) &&
      this._validateNumeric(fields) &&
      this._validateFiles() &&
      AuthorManager.validate() &&
      KeywordManager.validate();
  },

  /**
   * Valida que todos los campos requeridos estén completos
   * @private
   * @param {Object} fields - Campos del formulario
   * @returns {boolean} true si todos los campos requeridos están completos
   */
  _validateRequired(fields) {
    const required = [
      'titulo', 'anio_publicacion', 'estatus_publicacion', 'revista',
      'volumen', 'numero', 'indiceRevista', 'doi', 'urlCita',
      'objetivo', 'descripcion', 'abstract'
    ];

    for (const key of required) {
      if (!fields[key]) {
        const fieldName = key.replace(/([A-Z])/g, ' $1').toLowerCase();
        Utils.showToast(`El campo "${fieldName}" es requerido.`, 'danger');
        return false;
      }
    }
    return true;
  },

  /**
   * Valida que los campos numéricos tengan valores válidos
   * @private
   * @param {Object} fields - Campos del formulario
   * @returns {boolean} true si todos los números son válidos
   */
  _validateNumeric(fields) {
    if (!Utils.isValidNumber(fields.totalCitas)) {
      Utils.showToast('Total de citas debe ser un número válido.', 'danger');
      return false;
    }

    if (!Utils.isValidRange(fields.paginaInicio, fields.paginaFin)) {
      Utils.showToast('Las páginas deben ser números válidos y consistentes.', 'danger');
      return false;
    }

    return true;
  },

  /**
   * Valida que los archivos requeridos estén adjuntos
   * @private
   * @returns {boolean} true si ambos archivos están presentes
   */
  _validateFiles() {
    const paperFile = document.getElementById('archivoPaper')?.files[0];
    const firstPage = document.getElementById('primeraPagina')?.files[0];

    if (!paperFile) {
      Utils.showToast('Debe adjuntar el archivo del paper.', 'danger');
      return false;
    }

    if (!firstPage) {
      Utils.showToast('Debe adjuntar la primera página.', 'danger');
      return false;
    }

    return true;
  },

  /**
   * Envía los datos del paper al servidor
   * @private
   * @async
   * @param {Object} fields - Campos del paper
   * @param {string} apaReference - Referencia APA generada
   * @throws {Error} Si la respuesta del servidor indica error
   * @returns {Promise<void>}
   */
  async _submitData(fields, apaReference) {
    const formData = new FormData();

   // Campos básicos
    Object.entries(fields).forEach(([key, value]) => {
      // Aplicar la transformación de nombre solo a campos que no sean booleanos especiales como apoyoSECITI
      // O manejar apoyoSECITI de forma específica
      let fieldName;
       if (key === 'apoyoSECITI') {
          fieldName = 'recibio_apoyo_seciti'; // Nombre exacto esperado por Django
      } else if (key === 'programaSECITI') {
          fieldName = 'programa_seciti'; // Nombre exacto esperado por Django
      } else if (key === 'ejeSECITHI') {
          fieldName = 'eje_secithi'; // Nombre exacto esperado por Django
      } else {
          fieldName = key.replace(/([A-Z])/g, '_$1').toLowerCase(); // Transformación estándar para otros campos
      }
      console.warn(fieldName);
      formData.append(fieldName, key === 'apoyoSECITI' ? (value ? 'true' : 'false') : value);
    });

    // Datos adicionales
    formData.append('referencia_apa', apaReference);
    formData.append('autores', JSON.stringify(AuthorManager.selected));
    formData.append('palabras_clave', JSON.stringify(KeywordManager.selected));

    // Archivos
    const paperFile = document.getElementById('archivoPaper')?.files[0];
    const firstPage = document.getElementById('primeraPagina')?.files[0];
    if (paperFile) formData.append('archivo_paper', paperFile);
    if (firstPage) formData.append('primera_pagina', firstPage);

    // Crear palabras clave nuevas
    await KeywordManager.createNewKeywords();

    // Enviar
    const response = await fetch('/publications/create/', {
      method: 'POST',
      headers: {
        'X-CSRFToken': window.PublishTracker.csrfToken,
        'X-Requested-With': 'XMLHttpRequest'
      },
      body: formData
    });

    const data = await response.json();
    if (!response.ok || !data.success) {
      throw new Error(data.message || 'Error al guardar.');
    }

    Utils.showToast('✅ Paper guardado correctamente.', 'success');
    setTimeout(() => {
      bootstrap.Modal.getInstance(document.getElementById('dynamicModal'))?.hide();
      window.location.reload();
    }, 1500);
  },

  /**
   * Genera una referencia en formato APA para el paper
   * @private
   * @param {Object} data - Datos del paper incluyendo nombreRevista
   * @returns {string} Referencia formateada en estilo APA
   * @example
   * // Retorna: "Pérez et al. (2023). Title. Journal, 10(2), 15-20. https://doi.org/..."
   */
  _generateAPAReference(data) {
    const authors = AuthorManager.selected
      .sort((a, b) => a.orden - b.orden)
      .map(a => a.nombre);

    let authorCitation = '';
    if (authors.length === 1) {
      authorCitation = authors[0];
    } else if (authors.length === 2) {
      authorCitation = `${authors[0]} & ${authors[1]}`;
    } else if (authors.length > 2) {
      authorCitation = `${authors[0]} et al.`;
    }

    const volumeIssue = data.volumen && data.numero
      ? `${data.volumen}(${data.numero})`
      : (data.volumen || '');

    const pages = data.paginaInicio
      ? `, ${data.paginaInicio}${data.paginaFin ? `-${data.paginaFin}` : ''}`
      : '';

    return `${authorCitation}. (${data.anio_publicacion}). ${data.titulo}. ${data.nombreRevista}${volumeIssue ? `, ${volumeIssue}` : ''}${pages}.${data.doi ? ` https://doi.org/${data.doi}` : ''}`;
  }
};

// =============================================================================
// MÓDULO DE GESTIÓN DE ENTIDADES
// =============================================================================

/**
 * Gestiona la creación de entidades relacionadas (revistas, editoriales, países, etc.)
 * Proporciona funcionalidad genérica para guardar y manejar errores
 * @namespace EntityManager
 */
const EntityManager = {
  /**
   * Guarda una entidad genérica en el servidor
   * @async
   * @param {string} entityType - Tipo de entidad ('revista', 'pais', 'editorial', etc.)
   * @param {string} formId - ID del formulario HTML
   * @param {string} createUrl - URL del endpoint de creación
   * @param {string} [titleField='nombre'] - Nombre del campo usado como título
   * @returns {Promise<void>}
   * @example
   * await EntityManager.save('revista', 'formNuevaRevista', '/journals/create/');
   */
  async save(entityType, formId, createUrl, titleField = 'nombre') {
    const form = document.getElementById(formId);
    if (!form) {
      Utils.showToast('Error: Formulario no encontrado.', 'danger');
      return;
    }

    const formData = new FormData(form);

    try {
      const response = await fetch(createUrl, {
        method: 'POST',
        body: formData,
        headers: { 'X-CSRFToken': window.PublishTracker.csrfToken }
      });

      const data = await response.json();

      if (data.success) {
        this._clearErrors(formId);
        Utils.showToast(data.message, 'success');

        setTimeout(() => {
          ModalManager.pop();
          setTimeout(() => {
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
   * Limpia todos los mensajes de error del formulario
   * @private
   * @param {string} formId - ID del formulario
   */
  _clearErrors(formId) {
    const errorContainers = document.querySelectorAll(`#${formId} .text-danger`);
    errorContainers.forEach(container => {
      if (container.id.startsWith('error-')) {
        container.textContent = '';
      }
    });

    const invalidFields = document.querySelectorAll(`#${formId} .is-invalid`);
    invalidFields.forEach(field => field.classList.remove('is-invalid'));
  },

  /**
   * Maneja y muestra los errores de validación del servidor
   * @private
   * @param {string} formId - ID del formulario
   * @param {Object} data - Respuesta del servidor con errores
   */
  _handleErrors(formId, data) {
    this._clearErrors(formId);
    Utils.showToast(data.message, 'danger');

    if (data.errors) {
      console.group(`Errores de Validación:`);
      for (const [fieldName, errorMessages] of Object.entries(data.errors)) {
        console.error(`Campo '${fieldName}':`, errorMessages);

        const errorContainer = document.getElementById(`error-${fieldName}`);
        if (errorContainer) {
          errorContainer.textContent = errorMessages.join(' ');

          const fieldElement = document.querySelector(`#${formId} [name="${fieldName}"]`);
          if (fieldElement) {
            fieldElement.classList.add('is-invalid');
          }
        }
      }
      console.groupEnd();
    }
  },

  /**
   * Recarga el formulario padre con la nueva entidad seleccionada
   * @private
   * @param {string} entityType - Tipo de entidad creada
   * @param {number} entityId - ID de la entidad creada
   */
  _reloadParentForm(entityType, entityId) {
    // 1. Determinar la vista padre a recargar y el parámetro basado en la entidad creada
    // Asumiendo que entidades como 'revista', 'pais', etc., se crean desde el formulario de Paper
    // y entidades como 'autor', 'programa', 'eje' también lo hacen.
    const entitiesForPaperForm = ['autor', 'programaSeciti', 'ejeSecithi', 'revista'];

    let reloadUrl, title, size;

    if (entitiesForPaperForm.includes(entityType)) {
      reloadUrl = `/modal/new-paper/?${this._getReloadParamName(entityType)}=${entityId}`;
      title = 'Registrar Nuevo Paper';
      size = 'xl';
      onRenderCallback = initializePaperFormListeners;
    } else {
      reloadUrl = `/journals/modal/new-journal/?${this._getReloadParamName(entityType)}=${entityId}`;
      title = 'Añadir Nueva Revista'; // Ajusta si es necesario para otros formularios de Journal
      size = 'lg';
      onRenderCallback = initializePaperFormListeners;
    }

    // 2. Guardar estado temporal del formulario actual ANTES de pop/loadContent
    let estadoTemporal = null;
    if (ModalManager.stack.length > 0) {
        estadoTemporal = { ...ModalManager.stack[ModalManager.stack.length - 1] };
        console.debug("EntityManager._reloadParentForm: Estado temporal guardado:", estadoTemporal);
        ModalManager.stack.pop(); // Sacar la vista actual antes de recargarla
        console.debug(`EntityManager._reloadParentForm: Popping current view to reload it (was ${ModalManager.stack.length + 1} items).`);
    }

    // 3. Cargar la vista padre actualizada
    ModalManager.loadContent(reloadUrl, title, size, '', false,onRenderCallback); // No guardar estado

    // 4. Restaurar el estado del formulario DESPUÉS de que se haya cargado la vista
    //    Y ASEGURAR QUE EL NUEVO OBJETO ESTÉ SELECCIONADO
    if (estadoTemporal) {
        setTimeout(() => {
            if (ModalManager.stack.length > 0) {
                // Crear una copia del formData guardado para modificarlo
                const formDataAModificar = { ...estadoTemporal.formData };

                // Mapear el entityType al nombre del campo en el formulario HTML correspondiente
                // Ajusta estos nombres según tus modelos y Django Forms reales
                const fieldMap = {
                    'revista': 'revista', // Asumiendo el campo se llama 'revista' en el form de Paper
                    'pais': 'pais_publicacion', // Asumiendo el campo se llama 'pais_publicacion' en el form de Revista
                    'categoria': 'categoria', // Asumiendo el campo se llama 'categoria' en el form de Revista
                    'ambito': 'ambito', // Asumiendo el campo se llama 'ambito' en el form de Revista
                    'editorial': 'editorial', // Asumiendo el campo se llama 'editorial' en el form de Revista
                    // 'autor': 'autores_seleccionados', // Los autores se manejan de otra forma
                    'programaSeciti': 'programa_seciti', // Asumiendo el campo se llama 'programa_seciti' en el form de Paper
                    'ejeSecithi': 'eje_secithi', // Asumiendo el campo se llama 'eje_secithi' en el form de Paper
                };

                const fieldName = fieldMap[entityType];

                // Si el campo existe en el mapeo y está en el formData, actualizar su valor
                if (fieldName && formDataAModificar.hasOwnProperty(fieldName)) {
                    // Asignar el ID del nuevo objeto al campo correspondiente
                    formDataAModificar[fieldName] = entityId.toString(); // Asegurar que sea string como lo espera un <select>
                    console.debug(`EntityManager._reloadParentForm: Campo '${fieldName}' actualizado a nuevo ID: ${entityId}`);
                } else {
                    console.debug(`EntityManager._reloadParentForm: Campo para '${entityType}' no encontrado o no se sobrescribe (puede ser un campo complejo como autores).`);
                }

                // Aplicar el formData MODIFICADO a la nueva entrada de la pila
                ModalManager.stack[ModalManager.stack.length - 1].formData = formDataAModificar;

                console.debug("EntityManager._reloadParentForm: Estado (modificado) restaurado en la nueva vista:", ModalManager.stack[ModalManager.stack.length - 1]);
                // Actualizar el DOM del modal con el estado restaurado (y el nuevo ID seleccionado)
                ModalManager._renderCurrentView();
            }
        }, 100); // Pequeño delay para asegurar carga
    }
  },

  // Función auxiliar para mapear entidad al nombre del parámetro de recarga
  _getReloadParamName(entityType) {
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
    return paramMap[entityType];
  }
};

// =============================================================================
// FUNCIONES GLOBALES DE GUARDADO
// =============================================================================

/**
 * Guarda una nueva revista desde el modal dinámico
 * @async
 * @returns {Promise<void>}
 */
async function guardarRevista() {
  await EntityManager.save('revista', 'formNuevaRevista', '/journals/create/', 'nombre');
}

/**
 * Guarda un nuevo país desde el modal dinámico
 * @async
 * @returns {Promise<void>}
 */
async function guardarPais() {
  await EntityManager.save('pais', 'formGenerico', '/journals/create-country/', 'nombre');
}

/**
 * Guarda una nueva categoría desde el modal dinámico
 * @async
 * @returns {Promise<void>}
 */
async function guardarCategoria() {
  await EntityManager.save('categoria', 'formGenerico', '/journals/create-category/', 'nombre');
}

/**
 * Guarda un nuevo ámbito desde el modal dinámico
 * @async
 * @returns {Promise<void>}
 */
async function guardarAmbito() {
  await EntityManager.save('ambito', 'formGenerico', '/journals/create-scope/', 'nombre');
}

/**
 * Guarda una nueva editorial desde el modal dinámico
 * @async
 * @returns {Promise<void>}
 */
async function guardarEditorial() {
  await EntityManager.save('editorial', 'formGenerico', '/journals/create-publisher/', 'nombre');
}
/**
 * Guarda un nuevo programa Secithi
 * @async
 * @returns {Promise<void>}
 */
async function guardarPrograma() {
  await EntityManager.save('programaSeciti', 'formGenerico', '/core/create-program/', 'nombre')
}
/**
 * Guarda un nuevo eje Secithi
 * @async
 * @returns {Promise<void>}
 */
async function guardarEje() {
  await EntityManager.save('ejeSecithi', 'formGenerico', '/core/create-axis/', 'nombre')
}
/**
 * Guarda un nuevo autor desde el modal dinámico
 * @async
 * @returns {Promise<void>}
 */
async function guardarAutorDesdeModal() {
  await EntityManager.save('autor', 'formGenerico', '/authors/create/', 'nombre');
}

/**
 * Guarda un nuevo paper con todos sus datos asociados
 * @async
 * @returns {Promise<void>}
 */
async function guardarPaper() {
  await PaperManager.save();
}

// =============================================================================
// FUNCIONES GLOBALES DE GESTIÓN (Compatibilidad con HTML)
// =============================================================================

/**
 * Carga contenido dinámico en el modal (función wrapper)
 * @param {string} url - URL del contenido
 * @param {string} title - Título del modal
 * @param {string} [size=''] - Tamaño del modal
 * @param {string} [footer=''] - Footer HTML
 * @param {boolean} [saveState=true] - Guardar estado del formulario
 * @returns {Promise<void>}
 */
function cargarContenidoModal(url, title, size, footer, saveState) {
  return ModalManager.loadContent(url, title, size, footer, saveState);
}

/**
 * Regresa a la vista anterior del modal
 */
function regresarAVistaAnterior() {
  ModalManager.pop();
}

/**
 * Carga los roles disponibles para autores
 * @returns {Promise<void>}
 */
function cargarRoles() {
  return AuthorManager.loadRoles();
}

/**
 * Busca autores localmente en la tabla
 */
function buscarAutorLocal() {
  AuthorManager.searchLocal();
}

/**
 * Agrega un autor a la lista de seleccionados
 * @param {number} authorId - ID del autor
 * @param {string} name - Nombre del autor
 * @param {string} orcid - ORCID del autor
 */
function agregarAutorSeleccionadoLocal(authorId, name, orcid) {
  AuthorManager.add(authorId, name, orcid);
}

/**
 * Elimina un autor de la lista de seleccionados
 * @param {number} authorId - ID del autor
 */
function eliminarAutorSeleccionadoLocal(authorId) {
  AuthorManager.remove(authorId);
}

/**
 * Actualiza el rol de un autor
 * @param {number} authorId - ID del autor
 * @param {number} roleId - ID del rol
 */
function actualizarRolAutor(authorId, roleId) {
  AuthorManager.updateRole(authorId, roleId);
}

/**
 * Actualiza el orden de un autor
 * @param {number} authorId - ID del autor
 * @param {number} newOrder - Nuevo orden
 */
function actualizarOrdenAutor(authorId, newOrder) {
  AuthorManager.updateOrder(authorId, newOrder);
}

/**
 * Inicializa el sistema de palabras clave
 * @returns {Promise<void>}
 */
function inicializarPalabrasClave() {
  return KeywordManager.load();
}

/**
 * Selecciona una palabra clave
 * @param {{id: number, nombre: string}} keyword - Palabra clave a seleccionar
 */
function seleccionarPalabraClave(keyword) {
  KeywordManager.select(keyword);
}

/**
 * Agrega una nueva palabra clave personalizada
 */
function agregarNuevaPalabraClave() {
  KeywordManager.addNew();
}

/**
 * Elimina una palabra clave seleccionada
 * @param {number} index - Índice de la palabra clave
 */
function eliminarPalabraClaveSeleccionada(index) {
  KeywordManager.remove(index);
}

/**
 * Muestra un mensaje toast (wrapper de utilidad)
 * @param {string} message - Mensaje a mostrar
 * @param {string} [type='info'] - Tipo de alerta
 * @param {number} [duration=3000] - Duración en ms
 */
function mostrarAlertaPersonalizada(message, type, duration) {
  Utils.showToast(message, type, duration);
}

// =============================================================================
// MODAL DE NUEVO PAPER
// =============================================================================
/**
 * Adjunta todos los listeners necesarios al formulario de nuevo paper.
 * Debe llamarse cada vez que el contenido del modal del paper se renderiza.
 */
function initializePaperFormListeners() {
    console.log("Inicializando listeners del formulario del paper...");
    
    // Inicializadores de datos
    inicializarPalabrasClave();
    if(typeof cargarRoles === 'function') cargarRoles();

    // Listeners para el Asistente de Edición
    const revistaSelect = document.getElementById('revistaSelect');
    const anioInput = document.getElementById('anioPublicacion');
    const volumenInput = document.getElementById('volumenRevista');
    const numeroInput = document.getElementById('numeroRevista');

    if (revistaSelect && anioInput && volumenInput && numeroInput) {
        // Eliminar listeners antiguos para evitar duplicados (buena práctica)
        const check = () => EditionManager.check();
        revistaSelect.removeEventListener('change', check);
        anioInput.removeEventListener('blur', check);
        volumenInput.removeEventListener('blur', check);
        numeroInput.removeEventListener('blur', check);

        // Añadir listeners nuevos
        revistaSelect.addEventListener('change', check);
        anioInput.addEventListener('blur', check);
        volumenInput.addEventListener('blur', check);
        numeroInput.addEventListener('blur', check);
        
        console.log("Listeners de EditionManager adjuntados.");
    } else {
        console.warn("No se encontraron todos los elementos para el Asistente de Edición.");
    }
}
/**
 * Abre el modal para registrar un nuevo paper
 * Inicializa palabras clave y roles automáticamente
 * @async
 * @returns {Promise<void>}
 */
async function abrirModalNuevoPaper() {
  try {
    await ModalManager.loadContent(
      '/modal/new-paper/',
      'Registrar Nuevo Paper',
      'xl',
      '',
      false,
      initializePaperFormListeners
      );
  } catch (error) {
    console.error('Error en abrirModalNuevoPaper:', error);
    Utils.showToast('No se pudo abrir el formulario.', 'danger');
  }
}

// =============================================================================
// ACTUALIZADORES DE SELECT
// =============================================================================

/**
 * Gestiona la actualización de elementos <select> después de crear entidades
 * @namespace SelectUpdater
 */
const SelectUpdater = {
  /**
   * Actualiza el select de revistas con una nueva revista
   * @param {{id: number, nombre: string}} newJournal - Nueva revista creada
   */
  updateJournal(newJournal) {
    if (!newJournal) return;

    const select = document.getElementById('revistaSelect');
    if (!select) return;

    const option = document.createElement('option');
    option.value = newJournal.id;
    option.textContent = newJournal.nombre;
    option.selected = true;

    select.appendChild(option);
    window.nuevaRevistaCreada = null;
  },

  /**
   * Actualiza el select de editoriales con una nueva editorial
   * @param {{id: number, nombre: string}} newPublisher - Nueva editorial creada
   */
  updatePublisher(newPublisher) {
    this._updateSelect('id_editorial', newPublisher, 'Editorial');
    window.nuevaEditorialCreada = null;
  },

  /**
   * Actualiza el select de países con un nuevo país
   * @param {{id: number, nombre: string, nombre_completo: string}} newCountry - Nuevo país creado
   */
  updateCountry(newCountry) {
    if (!newCountry) return;

    const select = document.getElementById('id_pais_publicacion');
    if (!select) {
      console.warn('Select de país no encontrado.');
      return;
    }

    const exists = Array.from(select.options).some(opt => opt.value == newCountry.id);
    if (!exists) {
      const option = document.createElement('option');
      option.value = newCountry.id;
      option.textContent = newCountry.nombre_completo || newCountry.nombre;
      option.selected = true;

      select.appendChild(option);
      Utils.showToast(`País "${option.textContent}" añadido.`, 'info', 2000);
    }

    window.nuevoPaisCreado = null;
  },

  /**
   * Actualiza el select de categorías con una nueva categoría
   * @param {{id: number, nombre: string}} newCategory - Nueva categoría creada
   */
  updateCategory(newCategory) {
    this._updateSelect('id_categoria', newCategory, 'Categoría');
    window.nuevaCategoriaCreada = null;
  },

  /**
   * Actualiza el select de ámbitos con un nuevo ámbito
   * @param {{id: number, nombre: string}} newScope - Nuevo ámbito creado
   */
  updateScope(newScope) {
    this._updateSelect('id_ambito', newScope, 'Ámbito');
    window.nuevoAmbitoCreado = null;
  },

  updateProgram(newProgram) {
    this._updateSelect('programaSeciti', newProgram, 'ProgramaSeciti');
    window.nuevoProgramaCreado = null;
  },

  updateAxis(newAxis) {
    this._updateSelect('ejeSecithi', newAxis, 'EjeSecithi');
    window.nuevoEjeCreado = null;
  },
  /**
   * Actualiza un select genérico con una nueva entidad
   * @private
   * @param {string} selectId - ID del elemento select
   * @param {{id: number, nombre: string}} newEntity - Nueva entidad
   * @param {string} entityName - Nombre de la entidad para mensajes
   */
  _updateSelect(selectId, newEntity, entityName) {
    if (!newEntity) return;

    const select = document.getElementById(selectId);
    if (!select) {
      console.warn(`Select ${selectId} no encontrado.`);
      return;
    }

    const exists = Array.from(select.options).some(opt => opt.value == newEntity.id);
    if (!exists) {
      const option = document.createElement('option');
      option.value = newEntity.id;
      option.textContent = newEntity.nombre;
      option.selected = true;

      select.appendChild(option);
      Utils.showToast(`${entityName} "${newEntity.nombre}" añadida.`, 'info', 2000);
    } else {
      console.warn(`${entityName} con ID ${newEntity.id} ya existe.`);
    }
  }
};

/**
 * Actualiza el select de revistas (wrapper)
 * @param {{id: number, nombre: string}} newJournal - Nueva revista
 */
function actualizarSelectRevistas(newJournal) {
  SelectUpdater.updateJournal(newJournal);
}

/**
 * Actualiza el select de editoriales (wrapper)
 * @param {{id: number, nombre: string}} newPublisher - Nueva editorial
 */
function actualizarSelectEditorial(newPublisher) {
  SelectUpdater.updatePublisher(newPublisher);
}

/**
 * Actualiza el select de países (wrapper)
 * @param {{id: number, nombre: string}} newCountry - Nuevo país
 */
function actualizarSelectPais(newCountry) {
  SelectUpdater.updateCountry(newCountry);
}

/**
 * Actualiza el select de categorías (wrapper)
 * @param {{id: number, nombre: string}} newCategory - Nueva categoría
 */
function actualizarSelectCategoria(newCategory) {
  SelectUpdater.updateCategory(newCategory);
}

/**
 * Actualiza el select de ámbitos (wrapper)
 * @param {{id: number, nombre: string}} newScope - Nuevo ámbito
 */
function actualizarSelectAmbito(newScope) {
  SelectUpdater.updateScope(newScope);
}

function actualizarSelectPrograma(newProgram) {
  SelectUpdater.updateProgram(newProgram);
}

function actualizarSelectEje(newAxis) {
  SelectUpdater.updateAxis(newAxis);
}

// =============================================================================
// FUNCIONALIDADES PENDIENTES
// =============================================================================

/**
 * Visualiza los detalles de un paper (no implementado)
 * @todo Implementar funcionalidad
 */
function viewPaper() {
  Utils.showToast('Funcionalidad no implementada.', 'warning');
}

/**
 * Edita un paper existente (no implementado)
 * @todo Implementar funcionalidad
 */
function editPaper() {
  Utils.showToast('Funcionalidad no implementada.', 'warning');
}

/**
 * Genera un reporte de publicaciones (no implementado)
 * @todo Implementar funcionalidad
 */
function generateReport() {
  Utils.showToast('Funcionalidad no implementada.', 'warning');
}

// =============================================================================
// INICIALIZACIÓN
// =============================================================================

/**
 * Inicializa la aplicación cuando el DOM está listo
 * Configura el objeto global, sincroniza pilas y activa listeners
 */
document.addEventListener('DOMContentLoaded', () => {
  // Inicializar objeto global PublishTracker
  window.PublishTracker = {
    csrfToken: Utils.getCookie('csrftoken'),
    baseUrl: window.location.origin,
    modalStack: ModalManager.stack
  };

  // Sincronizar pila de modales
  ModalManager.stack = window.PublishTracker.modalStack;

  // Auto-submit en formularios de filtros
  document.querySelectorAll('select[name="status"], select[name="year"]').forEach(select => {
    select.addEventListener('change', () => {
      const form = select.closest('form');
      if (form) form.submit();
    });
  });

  // Inicializar tooltips de Bootstrap
  document.querySelectorAll('[data-bs-toggle="tooltip"]').forEach(el => {
    new bootstrap.Tooltip(el);
  });

  // Exponer módulos al scope global para debugging
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

const EditionManager = {
  async check() {
    // IDs tomados directamente de paper_accordion.html
    const revistaId = document.getElementById('revistaSelect')?.value;
    const anio = document.getElementById('anioPublicacion')?.value;
    const volumen = document.getElementById('volumenRevista')?.value;
    const numero = document.getElementById('numeroRevista')?.value;

    const container = document.getElementById('edicionArchivosContainer');

    // Solo proceder si los campos clave que definen una edición están llenos
    if (!revistaId || !anio || !volumen || !numero) {
      container.style.display = 'none';
      return;
    }

    container.style.display = 'block';
    container.innerHTML = `<p class="text-center text-muted"><div class="spinner-border spinner-border-sm" role="status"></div> Verificando edición...</p>`;

    try {
      const url = `/journals/api/verificar-edicion/?revista_id=${revistaId}&anio=${anio}&volumen=${volumen}&numero=${numero}`;
      const response = await fetch(url);

      if (!response.ok) throw new Error(`Error del servidor: ${response.statusText}`);

      const data = await response.json();

      if (data.success) {
        this.renderUI(data);
      } else {
        container.innerHTML = `<p class="text-danger">Error al verificar la edición: ${data.error || 'Desconocido'}</p>`;
      }
    } catch (error) {
      console.error("Error en EditionManager.check:", error);
      container.innerHTML = `<p class="text-danger">No se pudo conectar con el servidor.</p>`;
    }
  },

  renderUI(data) {
    const container = document.getElementById('edicionArchivosContainer');
    let html = '';
    const tiposRequeridos = ['Portada', 'Hoja Legal', 'Índice de Paper'];

    if (data.edicion_existe) {
      html += `<h6><i class="fas fa-check-circle text-success"></i> Edición Encontrada</h6>`;
      html += `<p class="small text-muted mb-2">La documentación de esta edición se compartirá entre artículos.</p>`;

      tiposRequeridos.forEach(tipo => {
        const archivo = data.archivos[tipo]; // Ahora es un objeto {nombre, url}
        const inputName = `archivo_edicion_${tipo.toLowerCase().replace(/\s+/g, '_')}`;

        if (archivo) {
          // --- ESTE BLOQUE ES LA LÓGICA NUEVA ---
          html += `
                        <div class="mb-2">
                            <label class="form-label small">${tipo}:</label>
                            
                            <div id="info_${inputName}" class="alert alert-light p-2 small border d-flex justify-content-between align-items-center">
                                <span>
                                    <i class="fas fa-file-archive text-success me-2"></i>
                                    <strong>${archivo.nombre}</strong>
                                </span>
                                <span>
                                    <a href="${archivo.url}" target="_blank" class="btn btn-sm btn-outline-secondary py-0 px-1" title="Ver archivo actual">Ver</a>
                                    <button type="button" class="btn btn-sm btn-outline-warning py-0 px-1" title="Reemplazar archivo" onclick="EditionManager.toggleReplaceUI('${inputName}', true)">Reemplazar</button>
                                </span>
                            </div>

                            <div id="upload_${inputName}" style="display: none;">
                                <input class="form-control form-control-sm" type="file" id="${inputName}" name="${inputName}">
                                <button type="button" class="btn btn-sm btn-link text-muted py-0" onclick="EditionManager.toggleReplaceUI('${inputName}', false)">Cancelar</button>
                            </div>
                        </div>`;
          // --- FIN DEL BLOQUE NUEVO ---
        } else {
          // El código para archivos faltantes sigue igual
          html += `
                        <div class="mb-2">
                            <label for="${inputName}" class="form-label small">${tipo}: <span class="text-danger">*</span></label>
                            <input class="form-control form-control-sm" type="file" id="${inputName}" name="${inputName}">
                        </div>`;
        }
      });
    } else {
      // El código para ediciones nuevas sigue igual
      html += `<h6><i class="fas fa-star text-info"></i> Nueva Edición Detectada</h6>`;
      html += `<p class="small text-muted mb-2">Por favor, adjunta los documentos. Se guardarán para futuros artículos.</p>`;

      tiposRequeridos.forEach(tipo => {
        const inputName = `archivo_edicion_${tipo.toLowerCase().replace(/\s+/g, '_')}`;
        html += `
                    <div class="mb-2">
                        <label for="${inputName}" class="form-label small">${tipo}: <span class="text-danger">*</span></label>
                        <input class="form-control form-control-sm" type="file" id="${inputName}" name="${inputName}">
                    </div>`;
      });
    }

    container.innerHTML = html;
  },
  toggleReplaceUI(baseName, showUpload) {
    const infoDiv = document.getElementById(`info_${baseName}`);
    const uploadDiv = document.getElementById(`upload_${baseName}`);

    if (showUpload) {
      infoDiv.style.display = 'none';
      uploadDiv.style.display = 'block';
    } else {
      infoDiv.style.display = 'flex';
      uploadDiv.style.display = 'none';
      // Opcional: limpiar el input si cancelan
      const fileInput = document.getElementById(baseName);
      if (fileInput) fileInput.value = '';
    }
  }
};