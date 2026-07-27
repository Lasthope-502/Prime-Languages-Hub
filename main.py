from core.hub import LanguageHub
from core.process_manager import ProcessManager
from engines_config import ENGINE_CONFIGS

from adapters.python_native_adapter import PythonNativeAdapter
from adapters.cpp_socket_adapter import CppSocketAdapter
from adapters.node_socket_adapter import NodeSocketAdapter
from adapters.java_socket_adapter import JavaSocketAdapter
from adapters.go_socket_adapter import GoSocketAdapter
from adapters.rust_socket_adapter import RustSocketAdapter
from adapters.php_socket_adapter import PhpSocketAdapter
from adapters.ruby_socket_adapter import RubySocketAdapter
from adapters.csharp_socket_adapter import CSharpSocketAdapter
from adapters.kotlin_socket_adapter import KotlinSocketAdapter

pm = ProcessManager()

# Sab engines ek loop mein start karo
for lang_id, config in ENGINE_CONFIGS.items():
    if lang_id in ["python"]:  # Python native hai, socket engine ki zaroorat nahi
        continue
    pm.start_engine(lang_id, config["command"], config["port"])

hub = LanguageHub()
hub.attach_process_manager(pm)

hub.register(PythonNativeAdapter())
hub.register(CppSocketAdapter())
hub.register(NodeSocketAdapter())
hub.register(JavaSocketAdapter())
hub.register(GoSocketAdapter())
hub.register(RustSocketAdapter())
hub.register(PhpSocketAdapter())
hub.register(RubySocketAdapter())
hub.register(CSharpSocketAdapter())
hub.register(KotlinSocketAdapter())

print(f"\n🎉 Total connected: {len(hub.list_connected())} REAL languages")
print(f"Languages: {hub.list_connected()}\n")

# Test har language ko
tests = [
    ("php", "process_web_logic", {"x": "form_submission"}),
    ("ruby", "clean_syntax_process", {"x": "elegant_code"}),
    ("csharp", "ecosystem_integration", {"x": "windows_app"}),
    ("kotlin", "null_safety_process", {"x": "android_widget"}),
]

for lang, func, args in tests:
    result = hub.send("python", lang, func, args)
    print(f"{lang}: {result}")

pm.stop_all()