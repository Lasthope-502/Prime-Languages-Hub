from adapters.socket_adapter_base import SocketAdapter

class GoSocketAdapter(SocketAdapter):
    language_id = "go"

    def __init__(self):
        super().__init__(port=9004)

    def call_function(self, function_name, args):
        value = args.get("x", "")
        message = f"{function_name} {value}\n"
        response = self._send_raw(message)
        return self.decode(response)