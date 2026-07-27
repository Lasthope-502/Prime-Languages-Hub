import socket
import json
import time
from core.adapter_base import LanguageAdapter

class SocketAdapter(LanguageAdapter):
    """
    Upgraded version — ab isme:
    - Timeout handling
    - Auto-retry (configurable attempts)
    - Proper error reporting (crash na ho)
    """

    def __init__(self, host="127.0.0.1", port=9000, timeout=3, max_retries=3):
        self.host = host
        self.port = port
        self.timeout = timeout
        self.max_retries = max_retries
        self.failure_count = 0
        self.is_healthy = True

    def _send_raw(self, message: str) -> str:
        last_error = None

        for attempt in range(1, self.max_retries + 1):
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.settimeout(self.timeout)
                    s.connect((self.host, self.port))
                    s.sendall(message.encode())
                    response = s.recv(4096).decode()

                # Success — failure count reset karo
                self.failure_count = 0
                self.is_healthy = True
                return response.strip()

            except (ConnectionRefusedError, socket.timeout, OSError) as e:
                last_error = e
                self.failure_count += 1
                print(f"[RETRY {attempt}/{self.max_retries}] '{self.language_id}' failed: {e}")
                time.sleep(0.3 * attempt)  # exponential-ish backoff

        # Sab retries fail ho gaye
        self.is_healthy = False
        raise ConnectionError(
            f"'{self.language_id}' engine unreachable after {self.max_retries} attempts. "
            f"Last error: {last_error}"
        )

    def encode(self, data): return json.dumps(data)
    def decode(self, payload): return json.loads(payload)

    def health_check(self) -> bool:
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(1)
                s.connect((self.host, self.port))
            self.is_healthy = True
            return True
        except Exception:
            self.is_healthy = False
            return False