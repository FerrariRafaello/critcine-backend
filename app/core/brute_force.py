import time
from collections import defaultdict
from threading import Lock

# max failed attempts before locking the IP
_MAX_ATTEMPTS = 5
# sliding window to count failures (10 min)
_WINDOW_SECONDS = 600
# how long the IP stays blocked (15 min)
_LOCKOUT_SECONDS = 900

_store: dict[str, dict] = defaultdict(
    lambda: {"attempts": 0, "first_attempt": 0.0, "locked_until": 0.0}
)
_lock = Lock()


def check_brute_force(ip: str) -> tuple[bool, int]:
    """Returns (is_blocked, seconds_remaining)."""
    now = time.time()
    with _lock:
        entry = _store[ip]
        # still in lockout period
        if now < entry["locked_until"]:
            return True, int(entry["locked_until"] - now)
        # window expired, reset counter
        if now - entry["first_attempt"] > _WINDOW_SECONDS:
            entry["attempts"] = 0
            entry["first_attempt"] = now
        return False, 0


def record_failure(ip: str) -> bool:
    """Records a failed attempt. Returns True if the IP just got locked."""
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
    """Clears tracking after a successful login."""
    with _lock:
        _store[ip] = {"attempts": 0, "first_attempt": 0.0, "locked_until": 0.0}
