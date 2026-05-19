import time
from collections import defaultdict
from threading import Lock

_MAX_ATTEMPTS = 5
_WINDOW_SECONDS = 600   # 10 minutos
_LOCKOUT_SECONDS = 900  # 15 minutos de bloqueio

_store: dict[str, dict] = defaultdict(
    lambda: {"attempts": 0, "first_attempt": 0.0, "locked_until": 0.0}
)
_lock = Lock()


def check_brute_force(ip: str) -> tuple[bool, int]:
    """Retorna (está_bloqueado, segundos_restantes)."""
    now = time.time()
    with _lock:
        entry = _store[ip]
        if now < entry["locked_until"]:
            return True, int(entry["locked_until"] - now)
        if now - entry["first_attempt"] > _WINDOW_SECONDS:
            entry["attempts"] = 0
            entry["first_attempt"] = now
        return False, 0


def record_failure(ip: str) -> bool:
    """Registra tentativa falha. Retorna True se o IP foi bloqueado agora."""
    now = time.time()
    with _lock:
        entry = _store[ip]
        if entry["attempts"] == 0:
            entry["first_attempt"] = now
        entry["attempts"] += 1
        if entry["attempts"] >= _MAX_ATTEMPTS:
            entry["locked_until"] = now + _LOCKOUT_SECONDS
            entry["attempts"] = 0
            return True
        return False


def record_success(ip: str) -> None:
    """Reseta o rastreamento após login bem-sucedido."""
    with _lock:
        _store[ip] = {"attempts": 0, "first_attempt": 0.0, "locked_until": 0.0}
