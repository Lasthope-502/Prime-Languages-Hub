ENGINE_CONFIGS = {
    "cpp":      {"command": ["./engines/cpp_engine/engine_server"], "port": 9001},
    "node":     {"command": ["node", "engines/node_engine/engine_server.js"], "port": 9002},
    "java":     {"command": ["java", "-cp", "engines/java_engine", "EngineServer"], "port": 9003},
    "go":       {"command": ["./engines/go_engine/engine_server"], "port": 9004},
    "rust":     {"command": ["./engines/rust_engine/target/release/rust_engine"], "port": 9005},
    "python":   {"command": ["python3", "engines/python_engine/engine_server.py"], "port": 9006},
    "php":      {"command": ["php", "engines/php_engine/engine_server.php"], "port": 9007},
    "ruby":     {"command": ["ruby", "engines/ruby_engine/engine_server.rb"], "port": 9008},
    "csharp":   {"command": ["mono", "engines/csharp_engine/EngineServer.exe"], "port": 9009},
    "kotlin":   {"command": ["java", "-jar", "engines/kotlin_engine/engine_server.jar"], "port": 9010},
}