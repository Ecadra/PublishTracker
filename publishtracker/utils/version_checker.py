import logging
from datetime import timedelta, datetime

import requests
from packaging import version
from django.conf import settings
from django.core.cache import cache

logger = logging.getLogger(__name__)

# Constantes de cache
_CACHE_KEY_BASE = "update_check"
_CACHE_TTL_OK = 60 * 60 * 6          # 6 horas para resultados válidos
_CACHE_TTL_ERROR = 60 * 10           # 10 minutos para errores/transitorios
_NO_UPDATE_SENTINEL = {"_no_update": True}


def _cache_key(repo: str, current_version: str) -> str:
    """Construye una clave de cache estable por repo y versión actual."""
    return f"{_CACHE_KEY_BASE}:{repo}:{current_version}"


def _github_headers() -> dict:
    """Headers para GitHub API.
    Pasos:
    1) Identificar agente de usuario (mejora para GH)
    2) Forzar JSON y compresión si aplica
    3) Incluir token (opcional) si existe en settings.GITHUB_TOKEN para elevar rate limits
    """
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": getattr(settings, "UPDATE_CHECK_UA", "PublishTracker-UpdateCheck/1.0"),
    }
    token = getattr(settings, "GITHUB_TOKEN", None)
    if token:
        headers["Authorization"] = f"Bearer {token}"
    return headers


def check_for_updates():
    """
    Verifica si hay una nueva versión disponible en GitHub.

    Retorna:
        dict | None:
            - dict con información de la actualización si hay nueva versión.
            - None si no hay actualizaciones o si ocurre un error.

    Pasos:
    1) Validar configuración mínima (GITHUB_REPO, CURRENT_VERSION)
    2) Leer de cache (positivo o negativo mediante centinela)
    3) Consumir GitHub /releases/latest con headers adecuados
    4) Parsear y normalizar versiones (strip de 'v', comparar con packaging.version)
    5) Cachear resultado:
        - Si hay update: cache por 6h con payload de actualización
        - Si no hay update: cache centinela por 6h
        - Si error: cache centinela de error por 10min para backoff
    """
    # 1) Validar configuración mínima
    repo = getattr(settings, "GITHUB_REPO", None)
    current_version = getattr(settings, "CURRENT_VERSION", None)
    if not repo or not current_version:
        logger.error("Faltan settings requeridos: GITHUB_REPO y/o CURRENT_VERSION")
        return None

    # 2) Leer de cache (positivo o negativo)
    ckey = _cache_key(repo, current_version)
    cached = cache.get(ckey)
    if cached:
        # Centinela de “no update”
        if cached is _NO_UPDATE_SENTINEL or cached.get("_no_update"):
            return None
        # Respuesta previa positiva
        return cached

    try:
        # 3) Consumir GitHub /releases/latest
        api_url = f"https://api.github.com/repos/{repo}/releases/latest"
        response = requests.get(api_url, headers=_github_headers(), timeout=5)

        # Manejo básico de rate limit u otros códigos
        if response.status_code == 403:
            logger.warning("GitHub API rate-limited (403). Aplicando backoff corto.")
            cache.set(ckey, _NO_UPDATE_SENTINEL, _CACHE_TTL_ERROR)
            return None
        if response.status_code != 200:
            logger.warning(f"GitHub API respondió con código {response.status_code}")
            cache.set(ckey, _NO_UPDATE_SENTINEL, _CACHE_TTL_ERROR)
            return None

        data = response.json()

        # 4) Parsear y normalizar versiones
        latest_tag = (data.get("tag_name") or "").strip()
        latest_version = latest_tag.lstrip("v")
        curr_version = str(current_version).lstrip("v")

        # Si no hay tag_name válido, fallback a no update (evita romper)
        if not latest_version:
            logger.warning("Respuesta de GitHub sin 'tag_name' válido.")
            cache.set(ckey, _NO_UPDATE_SENTINEL, _CACHE_TTL_ERROR)
            return None

        # Comparar semver (packaging.version maneja bien distintos formatos)
        if version.parse(latest_version) > version.parse(curr_version):
            update_info = {
                "version": latest_tag,                     # conservar formato original (posible 'vX.Y.Z')
                "url": data.get("html_url"),
                "name": data.get("name"),
                "published_at": data.get("published_at"),
                "body": (data.get("body") or "")[:200],    # primeros 200 chars
                "checked_at": datetime.utcnow().isoformat() + "Z",
            }
            # 5) Cachear resultado positivo
            cache.set(ckey, update_info, _CACHE_TTL_OK)
            return update_info

        # 5) Cachear “no update” vía centinela
        cache.set(ckey, _NO_UPDATE_SENTINEL, _CACHE_TTL_OK)
        return None

    except requests.RequestException as e:
        logger.error(f"Error de red al verificar actualizaciones: {e}")
        cache.set(ckey, _NO_UPDATE_SENTINEL, _CACHE_TTL_ERROR)
        return None
    except Exception as e:
        logger.error(f"Error inesperado en check_for_updates: {e}")
        cache.set(ckey, _NO_UPDATE_SENTINEL, _CACHE_TTL_ERROR)
        return None
