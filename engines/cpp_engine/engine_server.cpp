#include <iostream>
#include <string>
#include <sstream>
#include <thread>
#include <cstring>
#include <sys/socket.h>
#include <netinet/in.h>
#include <unistd.h>

std::string fast_compute(int x) {
    int result = x * 2;
    std::ostringstream out;
    out << "{\"result\": \"C++ computed at high speed: " << result << "\"}";
    return out.str();
}

std::string handle_request(const std::string& request) {
    std::istringstream iss(request);
    std::string function_name;
    int value;
    iss >> function_name >> value;

    if (function_name == "fast_compute") {
        return fast_compute(value);
    }
    return "{\"error\": \"unknown function\"}";
}

void handle_client(int client_socket) {
    char buffer[1024] = {0};
    read(client_socket, buffer, 1024);

    std::string response = handle_request(std::string(buffer)) + "\n";
    send(client_socket, response.c_str(), response.length(), 0);
    close(client_socket);
}

int main() {
    int server_fd = socket(AF_INET, SOCK_STREAM, 0);
    int opt = 1;
    setsockopt(server_fd, SOL_SOCKET, SO_REUSEADDR, &opt, sizeof(opt));

    sockaddr_in address;
    address.sin_family = AF_INET;
    address.sin_addr.s_addr = INADDR_ANY;
    address.sin_port = htons(9001);

    bind(server_fd, (struct sockaddr*)&address, sizeof(address));
    listen(server_fd, 50);  // backlog barha diya — zyada connections queue ho sakti hain

    std::cout << "[C++ ENGINE] Listening on port 9001 (multi-threaded, persistent)..." << std::endl;

    while (true) {
        int client_socket = accept(server_fd, nullptr, nullptr);
        // Har client ko alag thread mein handle karo — concurrent connections possible
        std::thread(handle_client, client_socket).detach();
    }

    return 0;
}