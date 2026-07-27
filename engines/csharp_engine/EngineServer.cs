using System;
using System.Net;
using System.Net.Sockets;
using System.Text;
using System.Threading;
using System.Text.Json;
using System.Collections.Generic;

class EngineServer
{
    static void Main()
    {
        int port = 9009;
        TcpListener listener = new TcpListener(IPAddress.Parse("127.0.0.1"), port);
        listener.Start();
        Console.WriteLine($"[C# ENGINE] Listening on port {port}... (persistent)");

        while (true)
        {
            TcpClient client = listener.AcceptTcpClient();
            Thread thread = new Thread(() => HandleClient(client));
            thread.Start();
        }
    }

    static void HandleClient(TcpClient client)
    {
        try
        {
            NetworkStream stream = client.GetStream();

            byte[] header = ReadExact(stream, 4);
            if (BitConverter.IsLittleEndian) Array.Reverse(header);
            int length = BitConverter.ToInt32(header, 0);

            byte[] bodyBytes = ReadExact(stream, length);
            string body = Encoding.UTF8.GetString(bodyBytes);

            var message = JsonSerializer.Deserialize<Dictionary<string, JsonElement>>(body);
            string functionName = message["function_name"].GetString();
            var args = message.ContainsKey("args") ? message["args"] : default;

            string response = HandleRequest(functionName, args);
            byte[] responseBytes = Encoding.UTF8.GetBytes(response);
            byte[] responseHeader = BitConverter.GetBytes(responseBytes.Length);
            if (BitConverter.IsLittleEndian) Array.Reverse(responseHeader);

            stream.Write(responseHeader, 0, 4);
            stream.Write(responseBytes, 0, responseBytes.Length);
        }
        catch (Exception e)
        {
            Console.WriteLine($"[C# ENGINE] Error: {e.Message}");
        }
        finally
        {
            client.Close();
        }
    }

    static byte[] ReadExact(NetworkStream stream, int numBytes)
    {
        byte[] buffer = new byte[numBytes];
        int totalRead = 0;
        while (totalRead < numBytes)
        {
            int read = stream.Read(buffer, totalRead, numBytes - totalRead);
            if (read == 0) break;
            totalRead += read;
        }
        return buffer;
    }

    static string HandleRequest(string functionName, JsonElement args)
    {
        if (functionName == "ecosystem_integration")
        {
            string value = args.TryGetProperty("x", out var v) ? v.ToString() : "";
            return $"{{\"result\": \"C# ecosystem integration processed: {value}\"}}";
        }
        return "{\"error\": \"unknown function\"}";
    }
}