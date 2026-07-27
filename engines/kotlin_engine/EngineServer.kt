import java.net.ServerSocket
import java.net.Socket
import java.io.DataInputStream
import java.io.DataOutputStream
import kotlin.concurrent.thread

fun readExact(input: DataInputStream, numBytes: Int): ByteArray {
    val buffer = ByteArray(numBytes)
    input.readFully(buffer)
    return buffer
}

fun handleRequest(functionName: String, value: String): String {
    return when (functionName) {
        "null_safety_process" -> "{\"result\": \"Kotlin processed with null safety: $value\"}"
        else -> "{\"error\": \"unknown function\"}"
    }
}

fun main() {
    val port = 9010
    val serverSocket = ServerSocket(port)
    println("[KOTLIN ENGINE] Listening on port $port... (persistent)")

    while (true) {
        val client = serverSocket.accept()
        thread {
            handleClient(client)
        }
    }
}

fun handleClient(client: Socket) {
    try {
        val input = DataInputStream(client.getInputStream())
        val output = DataOutputStream(client.getOutputStream())

        val header = readExact(input, 4)
        val length = ((header[0].toInt() and 0xFF) shl 24) or
                     ((header[1].toInt() and 0xFF) shl 16) or
                     ((header[2].toInt() and 0xFF) shl 8) or
                     (header[3].toInt() and 0xFF)

        val bodyBytes = readExact(input, length)
        val body = String(bodyBytes)

        // Simple parsing (production mein kotlinx.serialization use karo)
        val functionName = Regex("\"function_name\"\\s*:\\s*\"([^\"]+)\"").find(body)?.groupValues?.get(1) ?: ""
        val value = Regex("\"x\"\\s*:\\s*\"?([^\",}]+)\"?").find(body)?.groupValues?.get(1) ?: ""

        val response = handleRequest(functionName, value)
        val responseBytes = response.toByteArray()
        val responseLength = responseBytes.size

        output.write(byteArrayOf(
            (responseLength shr 24).toByte(),
            (responseLength shr 16).toByte(),
            (responseLength shr 8).toByte(),
            responseLength.toByte()
        ))
        output.write(responseBytes)
        output.flush()

    } catch (e: Exception) {
        println("[KOTLIN ENGINE] Error: ${e.message}")
    } finally {
        client.close()
    }
}