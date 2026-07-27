from adapters.pooled_socket_adapter import PooledSocketAdapter

class CSharpSocketAdapter(PooledSocketAdapter):
    language_id = "csharp"
    def __init__(self):
        super().__init__(port=9009, pool_size=5)