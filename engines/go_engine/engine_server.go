package main

import (
	"bufio"
	"fmt"
	"net"
	"strings"
)

func handleRequest(request string) string {
	parts := strings.SplitN(strings.TrimSpace(request), " ", 2)
	functionName := parts[0]
	value := ""
	if len(parts) > 1 {
		value = parts[1]
	}

	if functionName == "concurrent_process" {
		return fmt.Sprintf(`{"result": "Go processed concurrently: %s"}`, value)
	}
	return `{"error": "unknown function"}`
}

func main() {
	listener, _ := net.Listen("tcp", ":9004")
	fmt.Println("[GO ENGINE] Listening on port 9004... (persistent)")

	for {
		conn, _ := listener.Accept()
		go func(c net.Conn) {
			reader := bufio.NewReader(c)
			request, _ := reader.ReadString('\n')
			response := handleRequest(request)
			c.Write([]byte(response + "\n"))
			c.Close()
		}(conn)
	}
}