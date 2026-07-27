import socket
import queue
import threading
import time

class ConnectionPool:
    """
    Har language engine ke liye ek pool of persistent TCP connections.
    Multiple requests concurrently multiple connections use kar sakti hain.
    """

    def __init__(self, host, port, pool_size=5, timeout=3):
        self.host = host
        self.port = port
        self.pool_size = pool_size
        self.timeout = timeout
        self.pool = queue.Queue(maxsize=pool_size)
        self.lock = threading.Lock()
        self._initialize_pool()

    def _create_connection(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(self.timeout)
        sock.connect((self.host, self.port))
        return sock

    def _initialize_pool(self):
        """Pool ko shuru mein hi 'pool_size' connections sa bhar do"""
        created = 0
        for _ in range(self.pool_size):
            try:
                conn = self._create_connection()
                self.pool.put(conn)
                created += 1
            except Exception as e:
                print(f"[POOL] Warning: could not pre-create connection: {e}")
                break
        print(f"[POOL] Initialized with {created}/{self.pool_size} connections for {self.host}:{self.port}")

    def acquire(self, wait_timeout=5):
        """Pool sa ek connection nikalo (agar khali ho tou thora wait karo)"""
        try:
            conn = self.pool.get(timeout=wait_timeout)

            # Check karo connection zinda hai ya mar chuka hai
            if self._is_dead(conn):
                conn = self._create_connection()  # naya bana do

            return conn
        except queue.Empty:
            # Pool khali hai aur wait timeout ho gaya — emergency naya connection banao
            print(f"[POOL] Pool exhausted for {self.host}:{self.port}, creating overflow connection")
            return self._create_connection()

    def release(self, conn):
        """Connection wapis pool mein jama karo, taake dusri request use kar sakay"""
        try:
            self.pool.put_nowait(conn)
        except queue.Full:
            # Pool already full hai (overflow connection tha) — isay band kar do
            conn.close()

    def _is_dead(self, conn):
        """Check karo socket abhi bhi zinda hai ya nahi"""
        try:
            conn.getpeername()
            return False
        except Exception:
            return True

    def close_all(self):
        while not self.pool.empty():
            conn = self.pool.get()
            conn.close()
        print(f"[POOL] All connections closed for {self.host}:{self.port}")