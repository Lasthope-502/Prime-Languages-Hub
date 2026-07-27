from adapters.pooled_socket_adapter import PooledSocketAdapter

class RubySocketAdapter(PooledSocketAdapter):
    language_id = "ruby"
    def __init__(self):
        super().__init__(port=9008, pool_size=5)