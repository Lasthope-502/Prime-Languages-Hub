"""
Binary Data Handler
Binary data (files, images, raw bytes) ko JSON-safe
string mein convert karta hai aur wapis — cross-platform (Windows/Linux/Mac).
"""

import base64
import os


class BinaryDataHandler:

    @staticmethod
    def encode_binary(raw_bytes: bytes) -> dict:
        """Raw bytes ko JSON-transportable format mein convert karo"""
        return {
            "__type__": "binary",
            "encoding": "base64",
            "data": base64.b64encode(raw_bytes).decode('ascii'),
            "size_bytes": len(raw_bytes)
        }

    @staticmethod
    def decode_binary(encoded: dict) -> bytes:
        """Wapis raw bytes mein convert karo"""
        if encoded.get("__type__") != "binary":
            raise ValueError("Not a valid binary-encoded object")
        return base64.b64decode(encoded["data"])

    @staticmethod
    def encode_file(file_path: str) -> dict:
        """Poori file ko transportable format mein convert karo"""
        with open(file_path, 'rb') as f:
            raw_bytes = f.read()
        result = BinaryDataHandler.encode_binary(raw_bytes)

        # os.path.basename() cross-platform hai — Windows (\) aur
        # Linux/Mac (/) dono path separators ko sahi handle karta hai
        result["filename"] = os.path.basename(file_path)
        return result

    @staticmethod
    def decode_to_file(encoded: dict, output_path: str):
        """Wapis file mein save karo"""
        raw_bytes = BinaryDataHandler.decode_binary(encoded)
        with open(output_path, 'wb') as f:
            f.write(raw_bytes)