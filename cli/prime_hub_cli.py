#!/usr/bin/env python3
"""
Prime Languages Hub — Command Line Interface
Usage: prime-hub <command> [options]

Ye file poora CLI tool hai jo terminal se Prime Languages Hub ko
control karta hai — languages explore karna, hub start/stop karna,
aur cross-language calls karna.
"""

import argparse
import json
import sys
import os
import subprocess
import time

# Project root ko Python path mein add karo, taake 'core', 'adapters', etc. import ho sakein
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from engines_config import ENGINE_CONFIGS
from cli.session_manager import SessionManager


# ==================== LIST COMMAND ====================

def cmd_list(args):
    """Saari 659 languages ki list dikhao (filter ke sath)"""
    from core.registry_loader import RegistryLoader

    data_pattern = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "data", "languages_*.json"
    )
    languages = RegistryLoader.load_all_batches(data_pattern)

    if args.tier:
        languages = [l for l in languages if l["tier"] == args.tier]
    if args.category:
        languages = [l for l in languages if l["category"] == args.category]
    if args.search:
        languages = [l for l in languages if args.search.lower() in l["name"].lower()]

    if not languages:
        print("No languages found matching your filters.")
        return

    print(f"\n{'ID':<25} {'Name':<35} {'Category':<22} {'Tier':<5} {'Status'}")
    print("-" * 100)
    for lang in languages:
        print(f"{lang['id']:<25} {lang['name']:<35} {lang['category']:<22} {lang['tier']:<5} {lang['status']}")
    print(f"\nTotal: {len(languages)} languages\n")


# ==================== INFO COMMAND ====================

def cmd_info(args):
    """Kisi specific language ka detail dikhao"""
    from core.registry_loader import RegistryLoader

    data_pattern = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "data", "languages_*.json"
    )
    languages = RegistryLoader.load_all_batches(data_pattern)
    lang_map = {l["id"]: l for l in languages}

    lang = lang_map.get(args.language_id)
    if not lang:
        print(f"❌ Language '{args.language_id}' not found in registry")
        print(f"   Tip: use 'prime-hub list --search {args.language_id}' to find similar names")
        return

    print(f"\n{'=' * 50}")
    print(f"Language: {lang['name']}")
    print(f"{'=' * 50}")
    print(f"ID:       {lang['id']}")
    print(f"Category: {lang['category']}")
    print(f"Tier:     {lang['tier']}")
    print(f"Status:   {lang['status']}")

    is_engine_available = lang["id"] in ENGINE_CONFIGS
    print(f"Real Engine Available: {'✅ Yes' if is_engine_available else '❌ Not yet implemented'}")
    if is_engine_available:
        print(f"Engine Port: {ENGINE_CONFIGS[lang['id']]['port']}")
    print()


# ==================== STATS COMMAND ====================

def cmd_stats(args):
    """Registry ke overall stats dikhao"""
    from core.registry_loader import RegistryLoader

    data_pattern = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "data", "languages_*.json"
    )
    languages = RegistryLoader.load_all_batches(data_pattern)
    stats = RegistryLoader.get_stats(languages)

    print(f"\n{'=' * 50}")
    print(f"PRIME LANGUAGES HUB — REGISTRY STATISTICS")
    print(f"{'=' * 50}")
    print(f"Total Languages: {stats['total']}\n")

    print("By Tier:")
    tier_names = {1: "Core", 2: "Important", 3: "Specialized", 4: "Niche/Rare"}
    for tier in sorted(stats["by_tier"].keys()):
        print(f"  Tier {tier} ({tier_names.get(tier, '?')}): {stats['by_tier'][tier]}")

    print("\nBy Category (Top 10):")
    sorted_cats = sorted(stats["by_category"].items(), key=lambda x: -x[1])[:10]
    for cat, count in sorted_cats:
        print(f"  {cat}: {count}")
    print()


# ==================== START COMMAND ====================

def cmd_start(args):
    """Daemon ko background mein start karo"""
    session = SessionManager()

    if session.is_daemon_running():
        print("⚠️  Prime Languages Hub is already running.")
        return

    print("🚀 Starting Prime Languages Hub daemon in background...")

    daemon_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "cli", "daemon.py"
    )

    log_path = "/tmp/prime_hub_daemon.log"

    subprocess.Popen(
        ["python3", daemon_path],
        stdout=open(log_path, "w"),
        stderr=subprocess.STDOUT
    )

    # Thora wait karo daemon start hone ke liye (max 10 seconds)
    for _ in range(20):
        if session.is_daemon_running():
            print("✅ Prime Languages Hub is now running!")
            print("   Run 'prime-hub status' to see connected languages")
            return
        time.sleep(0.5)

    print(f"❌ Daemon failed to start. Check {log_path} for errors.")


# ==================== STATUS COMMAND ====================

def cmd_status(args):
    """Current hub status dikhao"""
    session = SessionManager()

    if not session.is_daemon_running():
        print("❌ Hub is not running. Run 'prime-hub start' first.")
        return

    hub = session.load_hub()
    report = hub.get_status_report()

    print(f"\n{'=' * 60}")
    print(f"PRIME LANGUAGES HUB — STATUS REPORT")
    print(f"{'=' * 60}")
    print(f"Total Registry Size:     {report['total_registry_size']} languages")
    print(f"Currently Connected:     {report['currently_connected']} languages")
    print(f"\n{'Language':<15} {'Tier':<6} {'Healthy':<10} {'Circuit':<12} {'Failures'}")
    print("-" * 60)
    for lang_id, info in report["languages"].items():
        healthy_icon = "✅" if info["healthy"] else "❌"
        print(f"{lang_id:<15} {info['tier']:<6} {healthy_icon:<10} {info['circuit_state']:<12} {info['failure_count']}")
    print()


# ==================== CALL COMMAND ====================

def cmd_call(args):
    """Direct function call kisi bhi 2 languages ke beech"""
    session = SessionManager()

    if not session.is_daemon_running():
        print("❌ Hub is not running. Run 'prime-hub start' first.")
        return

    try:
        call_args = json.loads(args.args) if args.args else {}
    except json.JSONDecodeError:
        print('❌ Invalid JSON in --args. Example: --args \'{"x": 10}\'')
        return

    hub = session.load_hub()
    result = hub.send(args.source, args.target, args.function, call_args)

    print(f"\n{args.source} -> {args.target} :: {args.function}")
    print(f"Result: {json.dumps(result, indent=2)}\n")


# ==================== STOP COMMAND ====================

def cmd_stop(args):
    """Sab engines band karo"""
    session = SessionManager()

    if not session.is_daemon_running():
        print("❌ No running hub found.")
        return

    pm = session.load_process_manager()
    pm.stop_all()
    session.clear()
    print("🛑 Prime Languages Hub stopped. All engines terminated.")


# ==================== ARGUMENT PARSER SETUP ====================

def build_parser():
    parser = argparse.ArgumentParser(
        prog="prime-hub",
        description="Prime Languages Hub — Universal Language Interconnection Tool"
    )
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # list command
    p_list = subparsers.add_parser("list", help="List all supported languages")
    p_list.add_argument("--tier", type=int, help="Filter by tier (1-4)")
    p_list.add_argument("--category", type=str, help="Filter by category")
    p_list.add_argument("--search", type=str, help="Search by name")
    p_list.set_defaults(func=cmd_list)

    # info command
    p_info = subparsers.add_parser("info", help="Show details of a specific language")
    p_info.add_argument("language_id", help="Language ID (e.g. python, cpp, rust)")
    p_info.set_defaults(func=cmd_info)

    # stats command
    p_stats = subparsers.add_parser("stats", help="Show registry statistics")
    p_stats.set_defaults(func=cmd_stats)

    # start command
    p_start = subparsers.add_parser("start", help="Start the hub and all engines")
    p_start.set_defaults(func=cmd_start)

    # status command
    p_status = subparsers.add_parser("status", help="Check hub and engine health")
    p_status.set_defaults(func=cmd_status)

    # call command
    p_call = subparsers.add_parser("call", help="Make a cross-language function call")
    p_call.add_argument("source", help="Source language")
    p_call.add_argument("target", help="Target language")
    p_call.add_argument("function", help="Function name to call")
    p_call.add_argument("--args", type=str, default="{}", help='JSON arguments, e.g. \'{"x": 10}\'')
    p_call.set_defaults(func=cmd_call)

    # stop command
    p_stop = subparsers.add_parser("stop", help="Stop the hub and all engines")
    p_stop.set_defaults(func=cmd_stop)

    return parser


# ==================== MAIN ENTRY POINT ====================

def main():
    parser = build_parser()
    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    args.func(args)


if __name__ == "__main__":
    main()