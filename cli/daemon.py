"""
Ye background process hai jo asal Hub object ko hold karta hai.
'prime-hub start' isay background mein chalata hai.
Baaki CLI commands (status, call, stop) isse socket ke zariye baat karte hain.
"""

import socket
import json
import threading
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.hub import LanguageHub
from core.process_manager import ProcessManager
from engines_config import ENGINE_CONFIGS
from cli.adapter_registry import get_all_adapters

DAEMON_PORT = 8899


class PrimeHubDaemon:
    def __init__(self):
        self.pm = ProcessManager()
        self.hub = LanguageHub()
        self.hub.attach_process_manager(self.pm)

    def initialize(self):
        print("[DAEMON] Starting all engines...")
        for lang_id, config in ENGINE_CONFIGS.items():
            if lang_id == "python":
                continue
            try:
                self.pm.start_engine(lang_id, config["command"], config["port"])
            except Exception as e:
                print(f"[DAEMON] Could not start '{lang_id}': {e}")

        for adapter in get_all_adapters():
            self.hub.register(adapter)

        print(f"[DAEMON] Ready. {len(self.hub.list_connected())} languages connected.")

    def handle_command(self, command: dict) -> dict:
        action = command.get("action")

        if action == "send":
            return self.hub.send(command["source"], command["target"], command["function"], command["args"])

        elif action == "status":
            return self.hub.get_status_report()

        elif action == "shutdown":
            self.pm.stop_all()
            threading.Timer(1.0, lambda: os._exit(0)).start()
            return {"message": "shutting down"}

        return {"error": "unknown action"}

    def start_server(self):
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind(("127.0.0.1", DAEMON_PORT))
        server.listen(20)
        print(f"[DAEMON] Listening for CLI commands on port {DAEMON_PORT}")

        while True:
            client, _ = server.accept()
            threading.Thread(target=self._handle_client, args=(client,)).start()

    def _handle_client(self, client_socket):
        try:
            data = client_socket.recv(65536).decode()
            command = json.loads(data)
            response = self.handle_command(command)
            client_socket.sendall(json.dumps(response).encode())
        except Exception as e:
            client_socket.sendall(json.dumps({"error": str(e)}).encode())
        finally:
            client_socket.close()


if __name__ == "__main__":
    daemon = PrimeHubDaemon()
    daemon.initialize()
    daemon.start_server()