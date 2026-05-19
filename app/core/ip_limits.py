import time
from collections import defaultdict
from threading import Lock

# at most 2 accounts per IP within 24 hours
_MAX_PER_DAY = 2
_WINDOW_SECONDS = 86400

# NOTE: stored in memory — resets on restart, good enough for single-instance
_store: dict[str, dict] = defaultdict(lambda: {"count": 0, "window_start": 0.0})
_lock = Lock()


def check_registration_limit(ip: str) -> tuple[bool, int]:
    """Returns (is_blocked, hours_remaining)."""
    now = time.time()
    with _lock:
        entry = _store[ip]
        # reset if the 24h window has passed
        if now - entry["window_start"] > _WINDOW_SECONDS:
            entry["count"] = 0
            entry["window_start"] = now
        if entry["count"] >= _MAX_PER_DAY:
            remaining_secs = int(_WINDOW_SECONDS - (now - entry["window_start"]))
            return True, max(1, remaining_secs // 3600)
        return False, 0


def record_registration(ip: str) -> None:
    """Tracks a new account created from this IP."""
    now = time.time()
    with _lock:
        entry = _store[ip]
        if now - entry["window_start"] > _WINDOW_SECONDS:
            entry["count"] = 0
            entry["window_start"] = now
        entry["count"] += 1
