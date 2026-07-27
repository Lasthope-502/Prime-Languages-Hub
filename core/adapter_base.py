"""
Base contract jo har language adapter ko follow karna zaroori hai.
Chahe wo Python ho, C++ ho, ya koi bhi naya language — sab isi
interface ko implement karenge taake Hub/Router unhe consistent
tareeqay se use kar sakein.
"""

from abc import ABC, abstractmethod


class LanguageAdapter(ABC):
    """
    Har language adapter ka base contract.
    Naya language add karna ho tou bas is class ko
    inherit karke ye 4 methods implement karne hain.
    """

    language_id: str = None  # e.g. "python", "cpp", "java"

    @abstractmethod
    def encode(self, data: dict):
        """Apni language ke native data ko common format mein convert karo"""
        pass

    @abstractmethod
    def decode(self, payload):
        """Common format sa wapis apni language ke native format mein convert karo"""
        pass

    @abstractmethod
    def call_function(self, function_name: str, args: dict):
        """Target language ke function ko call karo aur result wapis do"""
        pass

    @abstractmethod
    def health_check(self) -> bool:
        """Check karo adapter chal raha hai ya nahi"""
        pass