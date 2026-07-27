const net = require('net');

const PORT = 9002;  // Node engine ka fixed port

function handleRequest(input) {
    const { function_name, args } = JSON.parse(input);

    if (function_name === "render_ui") {
        return JSON.stringify({ result: `Node rendered UI with: ${args.x}` });
    }
    return JSON.stringify({ error: "unknown function" });
}

const server = net.createServer((socket) => {
    socket.on('data', (data) => {
        const response = handleRequest(data.toString());
        socket.write(response + "\n");
        socket.end();  // client se connection close, server chalta rehta hai
    });
});

server.listen(PORT, () => {
    console.log(`[NODE ENGINE] Listening on port ${PORT}... (persistent)`);
});