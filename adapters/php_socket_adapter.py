from adapters.pooled_socket_adapter import PooledSocketAdapter

class PhpSocketAdapter(PooledSocketAdapter):
    language_id = "php"
    def __init__(self):
        super().__init__(port=9007, pool_size=5)