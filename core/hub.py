import json
from core.router import ConnectionRouter
from core.circuit_breaker import CircuitBreaker

class LanguageHub:
    def __init__(self, registry_pattern="data/languages_*.json"):
        self.router = ConnectionRouter(registry_pattern)
        self.connected_adapters = {}
        self.circuit_breakers = {}
        self.message_log = []
        self.process_manager = None

    def attach_process_manager(self, pm):
        self.process_manager = pm

    def register(self, adapter):
        lang_id = adapter.language_id

        # Naya check: warn karo agar language registry mein nahi hai
        if not self.router.is_language_known(lang_id):
            print(f"[HUB WARNING] '{lang_id}' is not in the official 659-language registry. Registering anyway as custom.")
        else:
            tier = self.router.get_tier(lang_id)
            print(f"[HUB] '{lang_id}' found in registry (Tier {tier})")

        self.connected_adapters[lang_id] = adapter
        self.circuit_breakers[lang_id] = CircuitBreaker()
        print(f"[HUB] '{lang_id}' connected. Total active: {len(self.connected_adapters)}")

    def unregister(self, lang_id):
        self.connected_adapters.pop(lang_id, None)
        self.circuit_breakers.pop(lang_id, None)

    def list_connected(self):
        return list(self.connected_adapters.keys())

    def list_supported_but_not_connected(self):
        """Registry mein hain lekin abhi active nahi — future planning ke liye useful"""
        all_ids = set(self.router.lang_map.keys())
        connected_ids = set(self.connected_adapters.keys())
        return list(all_ids - connected_ids)

    def send(self, source_lang: str, target_lang: str, function_name: str, args: dict):
        if target_lang not in self.connected_adapters:
            # Check karo kum se kum registry mein hai ya nahi (better error message)
            if self.router.is_language_known(target_lang):
                return {"error": f"'{target_lang}' is a supported language (Tier {self.router.get_tier(target_lang)}) but not currently connected. Register its adapter first."}
            return {"error": f"'{target_lang}' is not recognized in Prime Languages Hub"}

        breaker = self.circuit_breakers[target_lang]
        if not breaker.can_attempt():
            return {"error": f"'{target_lang}' circuit is OPEN — temporarily unavailable"}

        target_adapter = self.connected_adapters[target_lang]
        strategy = self.router.get_strategy(source_lang, target_lang)

        try:
            result = target_adapter.call_function(function_name, args)
            breaker.record_success()
            self.message_log.append({"from": source_lang, "to": target_lang, "function": function_name, "strategy": strategy, "status": "success"})
            return result

        except ConnectionError as e:
            breaker.record_failure()
            if self.process_manager:
                self.process_manager.restart_engine(target_lang)
            return {"error": f"'{target_lang}' engine failed: {str(e)}"}

        except Exception as e:
            breaker.record_failure()
            return {"error": f"Unexpected error: {str(e)}"}

    def broadcast(self, source_lang: str, function_name: str, args: dict, exclude=None):
        exclude = exclude or []
        results = {}
        for lang_id in self.connected_adapters:
            if lang_id == source_lang or lang_id in exclude:
                continue
            results[lang_id] = self.send(source_lang, lang_id, function_name, args)
        return results

    def get_status_report(self):
        report = {
            "total_registry_size": len(self.router.registry),
            "currently_connected": len(self.connected_adapters),
            "languages": {}
        }
        for lang_id, adapter in self.connected_adapters.items():
            breaker = self.circuit_breakers[lang_id]
            report["languages"][lang_id] = {
                "healthy": adapter.health_check() if hasattr(adapter, 'health_check') else "unknown",
                "circuit_state": breaker.state,
                "failure_count": breaker.failure_count,
                "tier": self.router.get_tier(lang_id)
            }
        return report