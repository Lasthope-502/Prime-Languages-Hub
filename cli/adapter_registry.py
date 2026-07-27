"""
Sab available adapters ko ek jagah collect karta hai,
taake CLI aur baaki system easily access kar sakay.
"""

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


def get_all_adapters():
    """Har available language ka adapter instance return karta hai"""
    return [
        PythonNativeAdapter(),
        CppSocketAdapter(),
        NodeSocketAdapter(),
        JavaSocketAdapter(),
        GoSocketAdapter(),
        RustSocketAdapter(),
        PhpSocketAdapter(),
        RubySocketAdapter(),
        CSharpSocketAdapter(),
        KotlinSocketAdapter(),
    ]