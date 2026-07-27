from adapters.pooled_socket_adapter import PooledSocketAdapter

class KotlinSocketAdapter(PooledSocketAdapter):
    language_id = "kotlin"
    def __init__(self):
        super().__init__(port=9010, pool_size=5)