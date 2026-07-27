require 'socket'
require 'json'

PORT = 9008
server = TCPServer.new('127.0.0.1', PORT)
puts "[RUBY ENGINE] Listening on port #{PORT}... (persistent)"

def handle_request(function_name, args)
  case function_name
  when "clean_syntax_process"
    value = args["x"] || ""
    { result: "Ruby processed with clean syntax: #{value}" }
  else
    { error: "unknown function" }
  end
end

def read_exact(socket, num_bytes)
  buffer = ""
  while buffer.length < num_bytes
    chunk = socket.recv(num_bytes - buffer.length)
    break if chunk.nil? || chunk.empty?
    buffer += chunk
  end
  buffer
end

loop do
  client = server.accept

  Thread.new(client) do |conn|
    begin
      header = read_exact(conn, 4)
      length = header.unpack('N')[0]
      body = read_exact(conn, length)

      message = JSON.parse(body)
      function_name = message["function_name"]
      args = message["args"] || {}

      response = handle_request(function_name, args)
      json_response = response.to_json
      response_header = [json_response.bytesize].pack('N')

      conn.write(response_header + json_response)
    rescue => e
      puts "[RUBY ENGINE] Error: #{e.message}"
    ensure
      conn.close
    end
  end
end