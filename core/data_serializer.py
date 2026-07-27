from core.binary_handler import BinaryDataHandler

class DataSerializer:
    """
    Kisi bhi complexity ka data (deeply nested dicts, arrays,
    mixed binary+text) ko safely serialize/deserialize karta hai.
    """

    @staticmethod
    def serialize(data):
        """
        Recursively data ke andar jhaankay — agar bytes mile
        tou unhe binary-encode kar do, baqi jaisa hai waisa rehne do
        """
        if isinstance(data, bytes):
            return BinaryDataHandler.encode_binary(data)

        elif isinstance(data, dict):
            return {key: DataSerializer.serialize(value) for key, value in data.items()}

        elif isinstance(data, list):
            return [DataSerializer.serialize(item) for item in data]

        elif isinstance(data, tuple):
            return [DataSerializer.serialize(item) for item in data]  # tuple -> list

        else:
            # int, str, float, bool, None -- already JSON-safe
            return data

    @staticmethod
    def deserialize(data):
        """Wapis convert karo — binary-encoded objects ko raw bytes mein"""
        if isinstance(data, dict):
            if data.get("__type__") == "binary":
                return BinaryDataHandler.decode_binary(data)
            return {key: DataSerializer.deserialize(value) for key, value in data.items()}

        elif isinstance(data, list):
            return [DataSerializer.deserialize(item) for item in data]

        else:
            return data