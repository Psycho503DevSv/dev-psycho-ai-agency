"""
key_rotator.py — Rotador inteligente de API keys

Soporta múltiples claves por proveedor separadas por coma:
  GEMINI_API_KEY=key1,key2,key3,key4
  GROQ_API_KEY=keyA,keyB

Estrategia de rotación:
  1. Rotación DIARIA: cada 24h cambia a la siguiente key del pool.
  2. Rotación INMEDIATA: si la key activa devuelve 429, timeout o error de cuota,
     se marca como "agotada para esta sesión" y pasa a la siguiente.
  3. Estado persistido en memory/key_rotation_state.json para sobrevivir reinicios.
"""

import os
import json
import logging
from datetime import datetime, date
from typing import List, Optional

logger = logging.getLogger(__name__)

# Ruta al archivo de estado de rotación
_STATE_FILE = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "memory", "key_rotation_state.json"
)


def _load_state() -> dict:
    """Carga el estado actual del rotador desde disco."""
    if not os.path.exists(_STATE_FILE):
        return {}
    try:
        with open(_STATE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def _save_state(state: dict) -> None:
    """Persiste el estado del rotador en disco."""
    os.makedirs(os.path.dirname(_STATE_FILE), exist_ok=True)
    try:
        with open(_STATE_FILE, "w", encoding="utf-8") as f:
            json.dump(state, f, indent=2, ensure_ascii=False)
    except Exception as e:
        logger.warning(f"[KeyRotator] No se pudo guardar estado: {e}")


def parse_keys(raw: str) -> List[str]:
    """Divide la cadena de claves separadas por coma y filtra vacías."""
    if not raw:
        return []
    return [k.strip() for k in raw.split(",") if k.strip()]


def get_active_key(provider: str, all_keys: List[str]) -> Optional[str]:
    """
    Retorna la key activa para el proveedor dado.

    Lógica:
    - Carga el estado guardado.
    - Si el día cambió, avanza al siguiente índice base (rotación diaria).
    - Excluye keys permanentemente inválidas (403) — nunca se resetean.
    - Excluye keys agotadas por cuota (429/503) en la sesión actual.
    - Retorna la primera key válida del pool (circular).
    - Si todas las no-permanentes están agotadas, resetea solo las de cuota.
    """
    if not all_keys:
        return None

    state = _load_state()
    today = str(date.today())
    provider_state = state.get(provider, {})

    # ── Rotación diaria: si el día cambió, avanza el índice base ──
    last_date = provider_state.get("last_rotation_date", "")
    base_index = provider_state.get("base_index", 0)

    if last_date != today:
        base_index = (base_index + 1) % len(all_keys)
        provider_state["last_rotation_date"] = today
        provider_state["base_index"] = base_index
        provider_state["exhausted_today"] = []  # resetear solo cuota-agotadas; las permanentes persisten
        logger.info(f"[KeyRotator] {provider}: Rotación diaria → key #{base_index}")

    # ── Excluir keys agotadas (cuota) y permanentemente inválidas (403) ──
    exhausted: List[int] = provider_state.get("exhausted_today", [])
    permanently_invalid: List[int] = provider_state.get("permanently_invalid", [])
    blocked = set(exhausted) | set(permanently_invalid)

    # Si todas las keys no-permanentes están agotadas, resetear solo las de cuota
    non_permanent = [i for i in range(len(all_keys)) if i not in permanently_invalid]
    if non_permanent and all(i in blocked for i in non_permanent):
        logger.warning(f"[KeyRotator] {provider}: Keys de cuota agotadas. Reseteando pool (keys inválidas permanentes excluidas).")
        exhausted = []
        provider_state["exhausted_today"] = []
        blocked = set(permanently_invalid)
    elif not non_permanent:
        # Todas las keys son permanentemente inválidas
        logger.error(f"[KeyRotator] {provider}: TODAS las keys son permanentemente inválidas (403). Proveedor no disponible.")
        return None

    # Buscar la primera key válida empezando desde base_index (circular)
    selected_index = None
    for offset in range(len(all_keys)):
        candidate = (base_index + offset) % len(all_keys)
        if candidate not in blocked:
            selected_index = candidate
            break

    if selected_index is None:
        # Fallback: usar la primera no-permanente
        selected_index = non_permanent[0] if non_permanent else 0

    provider_state["current_index"] = selected_index
    state[provider] = provider_state
    _save_state(state)

    selected_key = all_keys[selected_index]
    logger.debug(f"[KeyRotator] {provider}: Usando key #{selected_index} (pool de {len(all_keys)}, {len(permanently_invalid)} inválidas permanentes)")
    return selected_key


def mark_key_exhausted(provider: str, all_keys: List[str], failed_key: str, permanent: bool = False) -> None:
    """
    Marca una key como agotada para la sesión actual (429/timeout) o permanentemente inválida (403).

    Args:
        permanent: Si True, la key se añade a `permanently_invalid` y NUNCA se resetea
                   aunque el pool diario se reinicie. Usar para errores 403.
    """
    if not all_keys or failed_key not in all_keys:
        return

    failed_index = all_keys.index(failed_key)
    state = _load_state()
    provider_state = state.get(provider, {})

    if permanent:
        # Key permanentemente inválida (403 Forbidden) — no vuelve al pool nunca
        permanently_invalid: List[int] = provider_state.get("permanently_invalid", [])
        if failed_index not in permanently_invalid:
            permanently_invalid.append(failed_index)
            provider_state["permanently_invalid"] = permanently_invalid
            state[provider] = provider_state
            _save_state(state)
            logger.error(
                f"[KeyRotator] {provider}: Key #{failed_index} marcada como PERMANENTEMENTE INVÁLIDA (403) "
                f"— excluida del pool para siempre en esta instalación."
            )
    else:
        # Key agotada por cuota (429/503/timeout) — se resetea al día siguiente
        exhausted: List[int] = provider_state.get("exhausted_today", [])
        if failed_index not in exhausted:
            exhausted.append(failed_index)
            provider_state["exhausted_today"] = exhausted
            state[provider] = provider_state
            _save_state(state)
            logger.warning(
                f"[KeyRotator] {provider}: Key #{failed_index} marcada como agotada (cuota) "
                f"({len(exhausted)}/{len(all_keys)} agotadas hoy)"
            )


def is_quota_error(status_code: int, error_text: str) -> bool:
    """Detecta si el error es de cuota/rate-limit (429/503) — justifica rotar key temporalmente."""
    quota_codes = {429, 503}
    quota_keywords = ["quota", "rate limit", "rate_limit", "too many requests",
                      "exceeded", "resource_exhausted", "ResourceExhausted"]

    if status_code in quota_codes:
        return True
    error_lower = error_text.lower()
    return any(kw.lower() in error_lower for kw in quota_keywords)


def is_permanent_error(status_code: int, error_text: str) -> bool:
    """Detecta si el error indica key permanentemente inválida (403) — se excluye para siempre."""
    if status_code == 403:
        return True
    permanent_keywords = ["api key not valid", "invalid api key", "permission denied",
                          "api_key_invalid", "forbidden", "unauthorized"]
    error_lower = error_text.lower()
    return any(kw in error_lower for kw in permanent_keywords)


def get_rotation_status() -> dict:
    """Retorna el estado actual del rotador para el dashboard."""
    state = _load_state()
    summary = {}
    for provider, pstate in state.items():
        exhausted_count = len(pstate.get("exhausted_today", []))
        summary[provider] = {
            "current_index": pstate.get("current_index", 0),
            "base_index": pstate.get("base_index", 0),
            "exhausted_today": exhausted_count,
            "last_rotation_date": pstate.get("last_rotation_date", ""),
        }
    return summary


def get_valid_keys(provider: str, all_keys: List[str]) -> List[str]:
    """Retorna la lista de keys filtrando las marcadas en permanently_invalid."""
    state = _load_state()
    provider_state = state.get(provider, {})
    permanently_invalid_indices = provider_state.get("permanently_invalid", [])
    return [key for idx, key in enumerate(all_keys) if idx not in permanently_invalid_indices]

