"""
CLI commands alag alag processes hain, isliye Hub object
memory mein persist nahi rehta. Ye session manager ek
background daemon process manage karta hai jo Hub ko
zinda rakhta hai, aur CLI commands us daemon se baat karte hain.
"""

import json
import os
import subprocess
import socket
import time

SESSION_FILE = os.path.expanduser("~/.prime_hub_session.json")
DAEMON_PORT = 8899  # CLI <-> Daemon communication ke liye


class SessionManager:

    def save(self, pm, hub):
        """Session info disk pe save karo (daemon start hone ke baad)"""
        session_data = {
            "daemon_running": True,
            "connected_languages": hub.list_connected(),
            "engine_pids": {lang: proc.pid for lang, proc in pm.running_processes.items()}
        }
        with open(SESSION_FILE, "w") as f:
            json.dump(session_data, f)

    def is_daemon_running(self):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(1)
                return s.connect_ex(("127.0.0.1", DAEMON_PORT)) == 0
        except Exception:
            return False

    def send_daemon_command(self, command_dict):
        """Daemon ko command bhejo, response wapas lo"""
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(10)
            s.connect(("127.0.0.1", DAEMON_PORT))
            s.sendall(json.dumps(command_dict).encode())
            response = s.recv(65536).decode()
            return json.loads(response)

    def load_hub(self):
        """Daemon se 'proxy' object return karo jo hub jaisa behave kare"""
        if not self.is_daemon_running():
            return None
        return DaemonHubProxy(self)

    def load_process_manager(self):
        if not self.is_daemon_running():
            return None
        return DaemonProcessManagerProxy(self)

    def clear(self):
        if os.path.exists(SESSION_FILE):
            os.remove(SESSION_FILE)


class DaemonHubProxy:
    """CLI se calls ko daemon tak forward karta hai, jaisa asal Hub ho"""

    def __init__(self, session_manager):
        self.session = session_manager

    def send(self, source, target, function_name, args):
        return self.session.send_daemon_command({
            "action": "send",
            "source": source,
            "target": target,
            "function": function_name,
            "args": args
        })

    def get_status_report(self):
        return self.session.send_daemon_command({"action": "status"})


class DaemonProcessManagerProxy:
    def __init__(self, session_manager):
        self.session = session_manager

    def stop_all(self):
        return self.session.send_daemon_command({"action": "shutdown"})