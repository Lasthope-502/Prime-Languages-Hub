import socket
import struct
import json
import threading

def unpack_length(header_bytes):
    return struct.unpack('>I', header_bytes)[0]

def recv_exact(sock, num_bytes):
    buffer = b''
    while len(buffer) < num_bytes:
        chunk = sock.recv(min(4096, num_bytes - len(buffer)))
        if not chunk:
            raise ConnectionError("Connection closed")
        buffer += chunk
    return buffer

def receive_message(sock):
    header = recv_exact(sock, 4)
    length = unpack_length(header)
    body = recv_exact(sock, length)
    return json.loads(body.decode('utf-8'))

def send_message(sock, data):
    json_bytes = json.dumps(data).encode('utf-8')
    length_prefix = struct.pack('>I', len(json_bytes))
    sock.sendall(length_prefix + json_bytes)

def handle_request(function_name, args):
    if function_name == "process_nested_data":
        # Example: complex nested data ko process karna
        user = args.get("user", {})
        tags = user.get("tags", [])
        return {
            "result": f"Processed user '{user.get('name')}' with {len(tags)} tags",
            "echo": args  # wapis same data bhej rahe hain, proof ke liye ke intact hai
        }

    elif function_name == "receive_file":
        # Binary file receive karke save karna
        from core.binary_handler import BinaryDataHandler
        file_info = args.get("file")
        raw_bytes = BinaryDataHandler.decode_binary(file_info)
        return {
            "result": f"Received file '{file_info.get('filename')}' — {len(raw_bytes)} bytes"
        }

    return {"error": "unknown function"}

def handle_client(client_socket):
    try:
        message = receive_message(client_socket)
        function_name = message.get("function_name")
        args = message.get("args", {})

        result = handle_request(function_name, args)
        send_message(client_socket, result)
    except Exception as e:
        print(f"[PYTHON ENGINE] Error: {e}")
    finally:
        client_socket.close()

def main():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind(('127.0.0.1', 9006))
    server.listen(50)
    print("[PYTHON ENGINE] Listening on port 9006 (complex data support)...")

    while True:
        client_socket, _ = server.accept()
        threading.Thread(target=handle_client, args=(client_socket,)).start()

if __name__ == "__main__":
    main()