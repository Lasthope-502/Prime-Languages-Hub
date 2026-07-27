import json
import glob

class RegistryLoader:
    """
    Multiple batch files (agar hum har letter alag file mein rakhain)
    ko ek single registry mein merge karta hai.
    """

    @staticmethod
    def load_single(path="data/languages.json"):
        with open(path) as f:
            return json.load(f)["languages"]

    @staticmethod
    def load_all_batches(pattern="data/languages_*.json"):
        """Agar har letter (A, B, C...) alag file mein ho, sabko merge karo"""
        all_languages = []
        for file_path in sorted(glob.glob(pattern)):
            with open(file_path) as f:
                batch = json.load(f)["languages"]
                all_languages.extend(batch)
        return all_languages

    @staticmethod
    def get_by_tier(languages, tier: int):
        return [lang for lang in languages if lang["tier"] == tier]

    @staticmethod
    def get_by_category(languages, category: str):
        return [lang for lang in languages if lang["category"] == category]

    @staticmethod
    def get_stats(languages):
        stats = {"total": len(languages), "by_tier": {}, "by_category": {}}
        for lang in languages:
            tier = lang["tier"]
            cat = lang["category"]
            stats["by_tier"][tier] = stats["by_tier"].get(tier, 0) + 1
            stats["by_category"][cat] = stats["by_category"].get(cat, 0) + 1
        return stats