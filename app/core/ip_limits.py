import time
from collections import defaultdict
from threading import Lock

_MAX_PER_DAY = 2
_WINDOW_SECONDS = 86400  # 24 horas

_store: dict[str, dict] = defaultdict(lambda: {"count": 0, "window_start": 0.0})
_lock = Lock()


def check_registration_limit(ip: str) -> tuple[bool, int]:
    """Retorna (está_bloqueado, horas_restantes)."""
    now = time.time()
    with _lock:
        entry = _store[ip]
        if now - entry["window_start"] > _WINDOW_SECONDS:
            entry["count"] = 0
            entry["window_start"] = now
        if entry["count"] >= _MAX_PER_DAY:
            remaining_secs = int(_WINDOW_SECONDS - (now - entry["window_start"]))
            return True, max(1, remaining_secs // 3600)
        return False, 0


def record_registration(ip: str) -> None:
    """Registra uma nova conta criada para esse IP."""
    now = time.time()
    with _lock:
        entry = _store[ip]
        if now - entry["window_start"] > _WINDOW_SECONDS:
            entry["count"] = 0
            entry["window_start"] = now
        entry["count"] += 1
