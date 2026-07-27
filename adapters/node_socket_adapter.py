from adapters.socket_adapter_base import SocketAdapter

class NodeSocketAdapter(SocketAdapter):
    language_id = "typescript"

    def __init__(self):
        super().__init__(port=9002)

    def call_function(self, function_name, args):
        payload = self.encode({"function_name": function_name, "args": args})
        response = self._send_raw(payload)
        return self.decode(response)