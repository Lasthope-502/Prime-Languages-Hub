<?php
$host = '127.0.0.1';
$port = 9007;

$server = stream_socket_server("tcp://$host:$port", $errno, $errstr);
if (!$server) {
    die("[PHP ENGINE] Failed to start: $errstr ($errno)\n");
}

echo "[PHP ENGINE] Listening on port $port... (persistent)\n";

function handle_request($function_name, $args) {
    if ($function_name === "process_web_logic") {
        $value = $args['x'] ?? '';
        return ["result" => "PHP processed web logic: $value"];
    }
    return ["error" => "unknown function"];
}

function read_exact($socket, $num_bytes) {
    $buffer = '';
    while (strlen($buffer) < $num_bytes) {
        $chunk = fread($socket, $num_bytes - strlen($buffer));
        if ($chunk === false || $chunk === '') break;
        $buffer .= $chunk;
    }
    return $buffer;
}

while ($client = stream_socket_accept($server)) {
    // Length-prefixed protocol: 4 bytes header + JSON body
    $header = read_exact($client, 4);
    $length = unpack('N', $header)[1];  // big-endian unsigned int
    $body = read_exact($client, $length);

    $message = json_decode($body, true);
    $function_name = $message['function_name'] ?? '';
    $args = $message['args'] ?? [];

    $response = handle_request($function_name, $args);
    $json_response = json_encode($response);
    $response_header = pack('N', strlen($json_response));

    fwrite($client, $response_header . $json_response);
    fclose($client);
}