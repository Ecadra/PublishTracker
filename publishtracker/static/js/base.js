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
