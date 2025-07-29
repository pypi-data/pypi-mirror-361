import socket
import threading
import json
import os
from .topography.topography_system import TopographySystem
from .model_context_protocol import ModelContextProtocol

CONFIG_PATH = os.path.join(os.path.dirname(__file__), 'mcp_config.json')

# Load configuration
with open(CONFIG_PATH, 'r') as f:
    config = json.load(f)

HOST = config.get('server', {}).get('host', '127.0.0.1')
PORT = config.get('server', {}).get('port', 65432)
USER_INPUT_MODE = config.get('user_input_mode', 'manual')
MODEL_PARAMETERS = config.get('model_parameters', {})

"""
Model Context Protocol (MCP) Server
----------------------------------
Protocol:
- Client sends a JSON message: {"context": <context_data>, "query": <query_string>}
- Server processes the context and query, and returns a JSON response: {"result": <result_data>}
- All messages are UTF-8 encoded and newline-terminated (\n)

This is a stub implementation. Replace the handler logic to integrate with your model/context system.
"""

model = TopographySystem()


def handle_client(conn, addr):
    print(f"[MCP] Connected by {addr}")
    with conn:
        buffer = b''
        while True:
            data = conn.recv(1024)
            if not data:
                break
            buffer += data
            while b'\n' in buffer:
                line, buffer = buffer.split(b'\n', 1)
                try:
                    message = json.loads(line.decode())
                    context = message.get('context')
                    query = message.get('query')
                    # Set context if provided
                    if context is not None:
                        model.set_context(context)
                    # Determine query to use based on user_input_mode
                    if USER_INPUT_MODE == 'manual':
                        if query is None:
                            response = json.dumps({"error": "No query provided in manual mode"}) + '\n'
                        else:
                            result = model.run(query, **MODEL_PARAMETERS)
                            response = json.dumps({"result": result}) + '\n'
                    else:  # auto mode
                        # Use query from client, or a default if not provided
                        if query is None:
                            # Use a default query string or empty string
                            query = MODEL_PARAMETERS.get('default_query', '')
                        result = model.run(query, **MODEL_PARAMETERS)
                        response = json.dumps({"result": result}) + '\n'
                except Exception as e:
                    response = json.dumps({"error": str(e)}) + '\n'
                conn.sendall(response.encode())
    print(f"[MCP] Disconnected {addr}")

def start_mcp_server(host=HOST, port=PORT):
    """Start the Model Context Protocol (MCP) server."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((host, port))
        s.listen()
        print(f"[MCP] Model Context Protocol Server listening on {host}:{port}")
        while True:
            conn, addr = s.accept()
            thread = threading.Thread(target=handle_client, args=(conn, addr), daemon=True)
            thread.start()

if __name__ == "__main__":
    start_mcp_server() 