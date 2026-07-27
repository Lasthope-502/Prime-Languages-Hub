from adapters.socket_adapter_base import SocketAdapter

class CppSocketAdapter(SocketAdapter):
    language_id = "cpp"

    def __init__(self):
        super().__init__(port=9001)

    def call_function(self, function_name, args):
        value = args.get("x", 0)
        message = f"{function_name} {value}"
        response = self._send_raw(message)
        return self.decode(response)