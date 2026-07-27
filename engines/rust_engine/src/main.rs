use std::io::{Read, Write};
use std::net::{TcpListener, TcpStream};

fn handle_request(request: &str) -> String {
    let parts: Vec<&str> = request.trim().splitn(2, ' ').collect();
    let function_name = parts.get(0).unwrap_or(&"");
    let value = parts.get(1).unwrap_or(&"");

    if *function_name == "safe_process" {
        format!("{{\"result\": \"Rust safely processed: {}\"}}", value)
    } else {
        "{\"error\": \"unknown function\"}".to_string()
    }
}

fn handle_client(mut stream: TcpStream) {
    let mut buffer = [0; 1024];
    let bytes_read = stream.read(&mut buffer).unwrap();
    let request = String::from_utf8_lossy(&buffer[..bytes_read]);

    let response = handle_request(&request);
    stream.write_all(format!("{}\n", response).as_bytes()).unwrap();
}

fn main() {
    let listener = TcpListener::bind("127.0.0.1:9005").unwrap();
    println!("[RUST ENGINE] Listening on port 9005... (persistent)");

    for stream in listener.incoming() {
        match stream {
            Ok(stream) => handle_client(stream),
            Err(e) => println!("Error: {}", e),
        }
    }
}