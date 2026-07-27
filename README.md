# 🔗 Prime Languages Hub (PLH)

**Universal Programming Language Interconnection System**

Prime Languages Hub ek aisa tool hai jo kisi bhi programming language ko kisi 
bhi doosri programming language ke sath stable, fast, aur scalable tareeqay 
se connect karta hai — chahe wo Python ho, C++, Java, Rust, ya koi bhi 
specialized/niche language.

> Jaisay pipe-connector alag-alag pipes ko jorta hai, waisay hi Prime 
> Languages Hub alag-alag programming languages ko ek **Central Hub** ke 
> zariye jorta hai — unlimited languages, ek sath, real-time.

---

## 📋 Table of Contents

- [Why Prime Languages Hub](#why-prime-languages-hub)
- [Architecture Overview](#architecture-overview)
- [Supported Languages](#supported-languages)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [CLI Reference](#cli-reference)
- [Core Concepts](#core-concepts)
- [Adding a New Language](#adding-a-new-language)
- [Project Structure](#project-structure)
- [Roadmap](#roadmap)
- [Contributing](#contributing)

---

## Why Prime Languages Hub

Modern software projects rarely use one language. A single system might need:

- **C++** for raw computational speed
- **Python** for AI/ML and rapid scripting
- **Java** for enterprise stability
- **Rust** for memory-safe performance
- **JavaScript/TypeScript** for the frontend
- **Go** for concurrent networking

Traditionally, connecting these languages means juggling different tools 
(SWIG, gRPC, FFI, WebAssembly, message queues) — each with its own setup, 
learning curve, and failure modes.

**Prime Languages Hub solves this by providing ONE unified interface** that:

1. Automatically decides the best connection strategy for any language pair
2. Keeps connections persistent (no restart overhead)
3. Handles errors, crashes, and recovery automatically
4. Supports simple values AND complex data (nested JSON, binary, files)
5. Scales to unlimited simultaneous languages, not just two at a time

---

## Architecture Overview
```bash

                ┌──────────────────────────────┐
                │      CENTRAL HUB / BROKER      │
                │  (Registry + Router + Bus)     │
                └──────────────────────────────┘
                 /      |       |       |      \
                /       |       |       |       \
          [Python]  [C++]   [Java]   [Rust]   [...unlimited]
                \       |       |       |       /
                 \      |       |       |      /
                  Persistent Socket Connections
                   (with pooling + auto-recovery)
```

---


### Core Components

| Component | Responsibility |
|---|---|
| **Hub** (`core/hub.py`) | Central registry of connected languages, routes calls, manages broadcasts |
| **Router** (`core/router.py`) | Decides the best connection strategy per language pair based on category rules |
| **Registry** (`data/languages_*.json`) | Metadata for all 659 supported languages (category, tier, status) |
| **Adapters** (`adapters/`) | Language-specific bridge implementing a common interface |
| **Process Manager** (`core/process_manager.py`) | Auto-starts, monitors, and restarts language engines |
| **Circuit Breaker** (`core/circuit_breaker.py`) | Prevents repeated calls to a failing language, allows graceful degradation |
| **Connection Pool** (`core/connection_pool.py`) | Reuses persistent socket connections for high concurrency |
| **Protocol** (`core/protocol.py`) | Length-prefixed message framing — supports arbitrarily large payloads |
| **Data Serializer** (`core/data_serializer.py`) | Recursively handles nested JSON + binary data (files, images) |
| **CLI** (`cli/`) | Terminal interface (`prime-hub`) to control everything |

---

### How a Call Flows

Python code calls: hub.send("python", "cpp", "fast_compute", {"x": 21})

- Hub checks if "cpp" is registered and its circuit breaker is CLOSED
- Router determines strategy (e.g., persistent socket via connection pool)
- Adapter serializes the data (handles nested/binary automatically)
- Message sent via length-prefixed protocol over a pooled TCP connection
- C++ engine (already running persistently) processes and responds
- Response deserialized and returned to Python
- On failure: retry -> circuit breaker -> auto-restart via Process Manager

---

## Supported Languages

Prime Languages Hub maintains a registry of **659 languages/DSLs**, organized 
into **4 tiers**:

| Tier | Description | Count | Examples |
|---|---|---|---|
| **1** | Core, production-critical, real engines built | ~35 | Python, Java, C++, C#, Go, Rust, PHP, Ruby, Kotlin, JavaScript |
| **2** | Important, widely used, engines planned | ~92 | Swift, Scala, Elixir, Haskell, COBOL, SQL variants |
| **3** | Specialized, domain-specific | ~178 | Solidity, GLSL, Terraform HCL, GraphQL |
| **4** | Niche, historical, esoteric, or dead | ~354 | Brainfuck, ALGOL 60, Malbolge, COMTRAN |

Every language is categorized (`general_purpose`, `blockchain`, `shader`, 
`quantum`, `esoteric`, `theorem_prover`, etc.) which determines its **default 
connection strategy** automatically — no manual configuration needed for 
each of the 659 entries.

Check the full list anytime:
```bash
prime-hub list
prime-hub list --tier 1
prime-hub list --category blockchain
prime-hub list --search "script"
```

---

## Installation

**Prerequisites**
- Python 3.8+
- (Optional, per language you want to connect) compilers/runtimes:
`g++`, `node`, `java/javac`, `go`, `cargo/rustc`, `php`, `ruby`, `mono/dotnet`,`kotlinc`

**Install**
```bash
git clone https://github.com/Lasthope-502/prime-languages-hub.git
cd prime-languages-hub
pip install -e .
```
This registers the prime-hub command globally.

---

## Quick Start
```bash
# See registry statistics
prime-hub stats

# Explore available languages
prime-hub list --tier 1

# Get details on a specific language
prime-hub info rust

# Start the hub (auto-launches all available engines in background)
prime-hub start

# Check what's connected and healthy
prime-hub status

# Make a live cross-language call
prime-hub call python cpp fast_compute --args '{"x": 21}'

# Stop everything cleanly
prime-hub stop
```
---

## CLI Reference

| Command	Description |
|---|---|---|
| prime-hub stats |	| Show registry statistics (tiers, categories) |
| prime-hub list [--tier N] [--category X] [--search Y] |	| List/filter the 659 languages |
| prime-hub info <language_id> |	| Show details about one language |
| prime-hub start |	| Start the hub daemon + all configured engines |
| prime-hub status |	| Show health of all connected languages |
| prime-hub call <source> <target> <function> --args '<json>' |	| Execute a cross-language call |
| prime-hub stop |

---

## Core Concepts

**1. Persistent Engines, Not One-Off Processes**
Each language runs as a long-lived socket server (started once, stays
alive). Calls reuse existing TCP connections via a connection pool,
avoiding expensive process-startup overhead on every call.

**2. Category-Based Strategy Selection**
Rather than configuring a connection method for each of the 659 languages
individually, every language belongs to a category
(general_purpose, blockchain, database_query, esoteric, etc.), and
each category has a sensible default strategy:
```bash
CATEGORY_DEFAULT_STRATEGY = {
    "general_purpose": "ffi_or_grpc",
    "blockchain": "abi_rpc_binding",
    "database_query": "driver_native",
    "esoteric": "subprocess_sandbox",
    ...
}
```
Specific language pairs can still override this default when needed
(LANGUAGE_OVERRIDES in core/strategy_config.py).

**3. Fault Tolerance**
- Retries with exponential backoff on transient failures
- Circuit Breaker temporarily skips a repeatedly-failing language
instead of hammering it
- Auto-Restart: a background health monitor detects crashed engines
and restarts them without manual intervention

**4. Complex Data Support**

Any data structure — deeply nested dictionaries, arrays, or raw binary
(files, images) — is automatically serialized/deserialized. Binary data is
Base64-encoded transparently so it can travel safely inside JSON messages.

**5. Unlimited Simultaneous Connections**

The Hub is not a point-to-point pipe; it's a broker. Any number of
languages can register at once, and any registered language can call, be
called by, or broadcast to any other.
```bash
hub.send("java", "python", "process_data", {...})      # one-to-one
hub.broadcast("java", "safe_process", {...})            # one-to-many
hub.collect("python", "aggregate", {...})                # many-to-one
```

---

## Adding a New Language
Thanks to the reusable adapter pattern, adding a new language typically
takes under 30 minutes:

1. Write a persistent socket server in the target language that:

- Listens on a TCP port
- Reads a 4-byte length-prefixed JSON message
- Processes the requested function
- Writes back a length-prefixed JSON response

2. Create a Python adapter (usually ~10 lines):

```bash
from adapters.pooled_socket_adapter import PooledSocketAdapter

class MyNewLanguageAdapter(PooledSocketAdapter):
    language_id = "my_new_language"
    def __init__(self):
        super().__init__(port=9999, pool_size=5)
```

3. Register it in engines_config.py and cli/adapter_registry.py

4. Verify it's in the registry (data/languages_*.json) — if it's one
of the 659 already listed, you're done; if new, add an entry with its
category and tier.

That's it — the Hub, Router, Circuit Breaker, and Connection Pool all work
with it automatically because they operate on the common LanguageAdapter
interface, not on language-specific code.

---

## Protocol Spec (must-follow for new engines)

Request/Response format:
[4 bytes: big-endian uint32 length][N bytes: UTF-8 JSON body]

Request JSON shape:
`{ "function_name": "...", "args": { ... } }`

Response JSON shape:
`{ "result": ... } OR { "error": "..." }`

---

## Code Style

- Keep engine servers minimal — one file, no external dependencies where possible
- Python-side code follows PEP8
- Comment non-obvious protocol-handling code in English or Urdu/Hinglish — both accepted

---

## Project Structure

```bash
prime-languages-hub/
├── core/
│   ├── hub.py                  # Central broker
│   ├── router.py                # Strategy selection engine
│   ├── registry_loader.py       # Merges all languages_*.json files
│   ├── adapter_base.py          # Common interface all adapters follow
│   ├── strategy_config.py       # Category -> default strategy rules
│   ├── process_manager.py       # Engine lifecycle + auto-restart
│   ├── circuit_breaker.py       # Fault-tolerance state machine
│   ├── connection_pool.py       # Persistent connection reuse
│   ├── protocol.py              # Length-prefixed message framing
│   ├── binary_handler.py        # Base64 binary/file encode-decode
│   └── data_serializer.py       # Recursive nested-data (de)serialization
├── adapters/
│   ├── socket_adapter_base.py
│   ├── pooled_socket_adapter.py
│   ├── python_native_adapter.py
│   ├── cpp_socket_adapter.py
│   ├── java_socket_adapter.py
│   ├── go_socket_adapter.py
│   ├── rust_socket_adapter.py
│   ├── node_socket_adapter.py
│   ├── php_socket_adapter.py
│   ├── ruby_socket_adapter.py
│   ├── csharp_socket_adapter.py
│   └── kotlin_socket_adapter.py
├── engines/
│   ├── cpp_engine/engine_server.cpp
│   ├── java_engine/EngineServer.java
│   ├── go_engine/engine_server.go
│   ├── rust_engine/src/main.rs
│   ├── node_engine/engine_server.js
│   ├── python_engine/engine_server.py
│   ├── php_engine/engine_server.php
│   ├── ruby_engine/engine_server.rb
│   ├── csharp_engine/EngineServer.cs
│   └── kotlin_engine/EngineServer.kt
├── cli/
│   ├── prime_hub_cli.py         # argparse-based CLI
│   ├── daemon.py                # Background process holding the live Hub
│   ├── session_manager.py       # CLI <-> daemon communication
│   └── adapter_registry.py      # Central list of all adapters
├── data/
│   └── languages_a.json ... languages_z.json   # 659-language registry, A-Z
├── engines_config.py             # port/command config per engine
├── setup.py
└── README.md
```

---

## License

MIT License — free to use, modify, and distribute.