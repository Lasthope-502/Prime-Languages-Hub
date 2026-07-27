import java.io.*;
import java.net.*;

public class EngineServer {
    static final int PORT = 9003;

    public static void main(String[] args) throws IOException {
        ServerSocket serverSocket = new ServerSocket(PORT, 50);  // backlog 50
        System.out.println("[JAVA ENGINE] Listening on port " + PORT + " (multi-threaded)...");

        while (true) {
            Socket clientSocket = serverSocket.accept();
            new Thread(() -> handleClient(clientSocket)).start();  // har client alag thread
        }
    }

    static void handleClient(Socket clientSocket) {
        try {
            BufferedReader in = new BufferedReader(new InputStreamReader(clientSocket.getInputStream()));
            PrintWriter out = new PrintWriter(clientSocket.getOutputStream(), true);

            String request = in.readLine();
            String response = handleRequest(request);

            out.println(response);
            clientSocket.close();
        } catch (IOException e) {
            e.printStackTrace();
        }
    }

    static String handleRequest(String request) {
        String[] parts = request.split(" ", 2);
        String functionName = parts[0];
        String value = parts.length > 1 ? parts[1] : "";

        if (functionName.equals("transfer_data")) {
            return "{\"result\": \"Java transferred: " + value + "\"}";
        }
        return "{\"error\": \"unknown function\"}";
    }
}