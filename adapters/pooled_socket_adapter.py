import time
from core.adapter_base import LanguageAdapter
from core.connection_pool import ConnectionPool
from core.protocol import MessageProtocol
from core.data_serializer import DataSerializer

class PooledSocketAdapter(LanguageAdapter):
    """
    Ab ye complex/nested/binary data bhi handle kar sakta hai,
    aur bade data ko bhi bina truncate hue safely transfer karta hai.
    """

    def __init__(self, host="127.0.0.1", port=9000, pool_size=5, timeout=5, max_retries=3):
        self.host = host
        self.port = port
        self.timeout = timeout
        self.max_retries = max_retries
        self.pool = ConnectionPool(host, port, pool_size=pool_size, timeout=timeout)

    def call_function(self, function_name: str, args: dict) -> dict:
        """
        Ab args mein kuch bhi ho sakta hai — nested dict, array,
        binary bytes (image/file), sab automatically handle hoga.
        """
        # Complex data ko safely serialize karo (binary detect + encode)
        safe_args = DataSerializer.serialize(args)

        message = {
            "function_name": function_name,
            "args": safe_args
        }

        response = self._send_with_retry(message)

        # Response mein bhi binary ho sakta hai, decode karo
        return DataSerializer.deserialize(response)

    def _send_with_retry(self, message: dict) -> dict:
        last_error = None

        for attempt in range(1, self.max_retries + 1):
            conn = self.pool.acquire()
            try:
                MessageProtocol.send_message(conn, message)
                response = MessageProtocol.receive_message(conn)
                self.pool.release(conn)
                return response

            except (ConnectionError, OSError, TimeoutError) as e:
                last_error = e
                conn.close()
                print(f"[RETRY {attempt}/{self.max_retries}] failed: {e}")
                time.sleep(0.2 * attempt)

        raise ConnectionError(f"Unreachable after {self.max_retries} attempts: {last_error}")

    def encode(self, data): return DataSerializer.serialize(data)
    def decode(self, data): return DataSerializer.deserialize(data)

    def health_check(self) -> bool:
        try:
            conn = self.pool.acquire(wait_timeout=1)
            self.pool.release(conn)
            return True
        except Exception:
            return False