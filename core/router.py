import json
import hashlib
from core.registry_loader import RegistryLoader
from core.strategy_config import CATEGORY_DEFAULT_STRATEGY, LANGUAGE_OVERRIDES

class ConnectionRouter:
    def __init__(self, registry_pattern="data/languages_*.json"):
        # Ab sab 26 files automatically merge ho jayengi
        self.registry = RegistryLoader.load_all_batches(registry_pattern)
        self.lang_map = {lang["id"]: lang for lang in self.registry}
        self.cache = {}

        print(f"[ROUTER] Registry loaded: {len(self.registry)} languages total")

    def get_language_info(self, lang_id: str):
        """Kisi bhi language ka pura metadata nikalo"""
        return self.lang_map.get(lang_id)

    def get_strategy(self, source_lang: str, target_lang: str) -> str:
        override_key = f"{source_lang}-{target_lang}"

        # 1. Specific override check
        if override_key in LANGUAGE_OVERRIDES:
            return LANGUAGE_OVERRIDES[override_key]

        # 2. Category-based default
        target_meta = self.lang_map.get(target_lang)
        if target_meta:
            category = target_meta["category"]
            strategy = CATEGORY_DEFAULT_STRATEGY.get(category)
            if strategy:
                return strategy

        # 3. Fallback
        return "grpc"

    def is_language_known(self, lang_id: str) -> bool:
        """Check karo ye language hamari 659 ki registry mein exist karti hai ya nahi"""
        return lang_id in self.lang_map

    def get_tier(self, lang_id: str):
        info = self.lang_map.get(lang_id)
        return info["tier"] if info else None

    def _data_fingerprint(self, data) -> str:
        raw = json.dumps(data, sort_keys=True, default=str).encode()
        return hashlib.md5(raw).hexdigest()

    def route(self, source_lang: str, target_lang: str, data: dict):
        # Registry validation — pehlay check karo ye languages hamari list mein hain
        if not self.is_language_known(target_lang):
            return {"error": f"'{target_lang}' is not in the Prime Languages Hub registry (659 supported languages)"}

        fingerprint = self._data_fingerprint(data)
        cache_key = f"{source_lang}->{target_lang}->{fingerprint}"

        if cache_key in self.cache:
            print(f"[CACHE HIT] {source_lang} -> {target_lang}")
            return self.cache[cache_key]

        strategy = self.get_strategy(source_lang, target_lang)
        target_info = self.get_language_info(target_lang)

        result = {
            "strategy_used": strategy,
            "source": source_lang,
            "target": target_lang,
            "target_category": target_info["category"],
            "target_tier": target_info["tier"],
            "payload": data
        }

        self.cache[cache_key] = result
        return result