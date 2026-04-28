import threading
from datetime import datetime, timedelta
import pytz


class ManualLock:
    def __init__(self):
        self._lock = threading.Lock()
        self._expires_at = None

    def lock(self, minutes):
        with self._lock:
            self._expires_at = datetime.now(pytz.timezone('America/New_York')) + timedelta(minutes=minutes)

    def unlock(self):
        with self._lock:
            self._expires_at = None

    def is_active(self):
        with self._lock:
            if self._expires_at is None:
                return False
            if datetime.now(pytz.timezone('America/New_York')) >= self._expires_at:
                self._expires_at = None
                return False
            return True

    def expires_at(self):
        with self._lock:
            return self._expires_at


manual_lock = ManualLock()
