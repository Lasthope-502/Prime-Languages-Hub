import subprocess
import time
import socket
import threading

class ProcessManager:
    def __init__(self):
        self.running_processes = {}
        self.engine_configs = {}   # restart ke liye command yaad rakhna
        self.monitor_active = False

    def start_engine(self, lang_id: str, command: list, port: int):
        self.engine_configs[lang_id] = {"command": command, "port": port}

        if self._is_port_open(port):
            print(f"[PROCESS MANAGER] '{lang_id}' already running on port {port}")
            return

        process = subprocess.Popen(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        self.running_processes[lang_id] = process
        print(f"[PROCESS MANAGER] Started '{lang_id}' (PID: {process.pid}) on port {port}")
        self._wait_until_ready(port)

    def restart_engine(self, lang_id: str):
        """Crash hone par isay call karo — engine ko dobara start karega"""
        config = self.engine_configs.get(lang_id)
        if not config:
            print(f"[PROCESS MANAGER] No config found for '{lang_id}', cannot restart")
            return False

        print(f"[PROCESS MANAGER] Restarting '{lang_id}'...")

        # Purana process (agar zinda hai) kill karo
        old_process = self.running_processes.get(lang_id)
        if old_process and old_process.poll() is None:
            old_process.terminate()
            time.sleep(0.5)

        # Naya process start karo
        try:
            process = subprocess.Popen(config["command"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            self.running_processes[lang_id] = process
            self._wait_until_ready(config["port"], timeout=5)
            print(f"[PROCESS MANAGER] '{lang_id}' restarted successfully (PID: {process.pid})")
            return True
        except Exception as e:
            print(f"[PROCESS MANAGER] Failed to restart '{lang_id}': {e}")
            return False

    def start_health_monitor(self, hub, interval=5):
        """
        Background thread jo har 'interval' seconds mein sab engines
        ko check karta rahega — agar koi crash hua tou auto-restart
        """
        self.monitor_active = True

        def monitor_loop():
            while self.monitor_active:
                for lang_id, config in self.engine_configs.items():
                    if not self._is_port_open(config["port"]):
                        print(f"[HEALTH MONITOR] '{lang_id}' is DOWN — attempting restart")
                        self.restart_engine(lang_id)
                time.sleep(interval)

        thread = threading.Thread(target=monitor_loop, daemon=True)
        thread.start()
        print(f"[PROCESS MANAGER] Health monitor started (checking every {interval}s)")

    def stop_monitor(self):
        self.monitor_active = False

    def _is_port_open(self, port, host="127.0.0.1"):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(0.5)
            return s.connect_ex((host, port)) == 0

    def _wait_until_ready(self, port, timeout=5):
        start = time.time()
        while time.time() - start < timeout:
            if self._is_port_open(port):
                return True
            time.sleep(0.1)
        raise TimeoutError(f"Engine on port {port} did not start in time")

    def stop_all(self):
        self.monitor_active = False
        for lang_id, process in self.running_processes.items():
            process.terminate()
            print(f"[PROCESS MANAGER] Stopped '{lang_id}'")