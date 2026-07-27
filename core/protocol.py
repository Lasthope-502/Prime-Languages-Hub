"""
Message Framing Protocol.
Format: [4 bytes: message length][message length bytes: actual data]

Isse hum kitna bhi bara data (chahe 1KB ho ya 1GB) safely
bina truncate/corrupt hue transfer kar sakte hain.
"""

import struct
import json

class MessageProtocol:

    @staticmethod
    def pack(data: dict) -> bytes:
        """Data ko JSON + length-prefix mein convert karo"""
        json_bytes = json.dumps(data).encode('utf-8')
        length_prefix = struct.pack('>I', len(json_bytes))  # 4-byte big-endian length
        return length_prefix + json_bytes

    @staticmethod
    def unpack_length(header_bytes: bytes) -> int:
        """4-byte header sa length nikalo"""
        return struct.unpack('>I', header_bytes)[0]

    @staticmethod
    def recv_exact(sock, num_bytes: int) -> bytes:
        """Socket sa exact 'num_bytes' parho (chahay kitni baar recv() call karni paray)"""
        buffer = b''
        while len(buffer) < num_bytes:
            chunk = sock.recv(min(4096, num_bytes - len(buffer)))
            if not chunk:
                raise ConnectionError("Connection closed while receiving data")
            buffer += chunk
        return buffer

    @classmethod
    def send_message(cls, sock, data: dict):
        """Poora message socket pe safely bhejo"""
        packed = cls.pack(data)
        sock.sendall(packed)

    @classmethod
    def receive_message(cls, sock) -> dict:
        """Poora message socket sa safely parho (chahay kitna bara ho)"""
        header = cls.recv_exact(sock, 4)
        length = cls.unpack_length(header)
        body = cls.recv_exact(sock, length)
        return json.loads(body.decode('utf-8'))