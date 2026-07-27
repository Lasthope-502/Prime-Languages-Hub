"""
Category-wise default connection strategy.
Har naya language jab tak khud ka override na de,
uski category ka default method use hoga.
"""

CATEGORY_DEFAULT_STRATEGY = {
    "general_purpose": "ffi_or_grpc",       # Python, Java, C++, Go, Rust etc.
    "scripting": "subprocess_pipe",          # Shell, Perl, Ruby scripts
    "jvm_based": "jvm_native_bridge",        # Kotlin, Scala, Groovy, Clojure
    "web_frontend": "js_bridge",             # JS, TS, Dart(web), Elm
    "config_data_format": "parser_only",     # JSON, YAML, TOML, XML
    "database_query": "driver_native",       # SQL, Cypher, GraphQL
    "blockchain": "abi_rpc_binding",         # Solidity, Vyper, Move
    "hardware_description": "no_runtime_bridge",  # VHDL, Verilog
    "quantum": "sdk_binding",                # Qiskit, Q#, Cirq
    "esoteric": "subprocess_sandbox",        # Brainfuck, Malbolge etc.
    "shader": "compiler_pipeline_only",      # GLSL, HLSL, WGSL
    "assembly": "native_binary_link",        # x86, ARM, RISC-V
    "theorem_prover": "cli_invocation",      # Coq, Isabelle, Lean
    "ci_cd_config": "parser_only",           # GitHub Actions, GitLab CI
    "markup_doc": "parser_only",             # Markdown, LaTeX, AsciiDoc
}

# Special override — agar kisi language pair ka default rule
# uski category sa hut kar hai, tou yahan likho
LANGUAGE_OVERRIDES = {
    "cpp-python": "ffi",
    "cpp-rust": "native_ffi",
    "java-python": "grpc",
    "java-typescript": "graalvm",
    "python-shell": "pipe",
}