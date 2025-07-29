import asyncio
import threading
import time
from typing import Any, Dict
import json
from cadbuildr.foundation.utils import reset_ids

try:
    import websockets

    is_websockets_available = True
except ImportError:
    is_websockets_available = False


# Global variables to manage the server and clients
server_instance = None
connected_clients = set()
message_buffer: list[str] = []  # Buffer to store messages when no clients are connected
server_event_loop = None  # Event loop for the server

# Store last screenshot result and an event for synchronization
screenshot_result: str | None = None
waiting_screenshot_id: str | None = None
screenshot_event = threading.Event()

PORT = 3001


def set_port(port: int):
    global PORT
    PORT = port


async def handle_connection(websocket, path):
    """Handle incoming WebSocket connections."""
    connected_clients.add(websocket)
    print(f"Client connected: {websocket.remote_address}")

    # Send buffered messages to the newly connected client
    for message in message_buffer:
        try:
            await websocket.send(message)
        except Exception as e:
            print(f"Error sending buffered message to {websocket.remote_address}: {e}")

    # Clear the buffer after sending
    message_buffer.clear()

    try:
        # Listen for messages coming from the client (browser)
        async for message in websocket:
            try:
                data = json.loads(message)
            except Exception:
                data = None

            if isinstance(data, dict) and data.get("action") == "screenshot":
                global screenshot_result, waiting_screenshot_id
                if waiting_screenshot_id and data.get("id") == waiting_screenshot_id:
                    screenshot_result = data.get("payload")
                    screenshot_event.set()
    except Exception as e:
        print(f"Error in websocket communication: {e}")
    finally:
        connected_clients.remove(websocket)
        print(f"Client disconnected: {websocket.remote_address}")


async def start_server():
    """Start the WebSocket server if not already running."""
    global server_instance, PORT
    if server_instance is None:
        max_attempts = 10
        original_port = PORT
        
        for attempt in range(max_attempts):
            try:
                server_instance = await websockets.serve(handle_connection, "127.0.0.1", PORT)
                print(f"WebSocket server started on ws://127.0.0.1:{PORT}")
                break
            except OSError as e:
                if e.errno == 48 or "Address already in use" in str(e):  # Port already in use
                    PORT += 1
                    if attempt == max_attempts - 1:
                        print(f"Failed to start WebSocket server after {max_attempts} attempts. Tried ports {original_port}-{PORT}")
                        raise
                    continue
                else:
                    raise  # Re-raise if it's a different error


def start_server_in_background():
    global server_event_loop
    server_event_loop = asyncio.new_event_loop()
    asyncio.set_event_loop(server_event_loop)
    server_event_loop.run_until_complete(start_server())
    server_event_loop.run_forever()


# Send dict message to clients (wrap in json)
def send_to_clients(data: Dict):
    """Send data to all connected WebSocket clients. If no clients, buffer the data."""
    message = json.dumps(data)
    if connected_clients and server_event_loop is not None:
        asyncio.run_coroutine_threadsafe(_send_all_clients(message), server_event_loop)
    else:
        print("No clients connected to send data. Buffering message.")
        message_buffer.append(message)  # Store serialized message


async def _send_all_clients(message: str):
    """Helper coroutine to send messages to all clients."""
    if connected_clients:
        await asyncio.gather(
            *(client.send(message) for client in connected_clients),
            return_exceptions=True,
        )


# PUBLIC API

# Helper to ensure the server is running
def _ensure_server():
    if not is_websockets_available:
        print("Websockets are not available")
        return False
    try:
        global server_instance
        if server_instance is None:
            # Start the server in a background thread
            threading.Thread(target=start_server_in_background, daemon=True).start()
            # Give the server time to start
            time.sleep(0.1)
        return True
    except Exception as e:
        print(f"WebSocket error: {e}")
        return False


def show_ext(dag: Any) -> None:
    """Function to generate DAG data and send it via WebSocket."""
    if not _ensure_server():
        return
    # Record the buffer size before sending the data. If the size increases
    # after the call, it means the message has been buffered (no clients
    # were connected yet).
    prev_buffer_size = len(message_buffer)

    # Wrap the DAG in the new message format
    message = {"action": "display", "payload": dag}

    # Send the data (either directly to clients or into the buffer)
    send_to_clients(message)

    # If the message ended up in the buffer, give clients a chance to
    # connect and consume it before the Python process exits. This is
    # particularly helpful for short-lived one-off scripts where the main
    # thread would otherwise terminate immediately.
    if len(message_buffer) > prev_buffer_size:
        wait_seconds = 5
        start_time = time.time()
        while message_buffer and (time.time() - start_time < wait_seconds):
            time.sleep(0.1)
    reset_ids()


def get_screenshot(timeout: int = 10):
    """Request a screenshot of the current viewer state and wait for the result.

    Returns base64 PNG data on success.
    Raises NoViewerConnected or ScreenshotTimeout on failure.
    """
    if not _ensure_server():
        raise RuntimeError("WebSocket server unavailable")

    # Wait briefly for a viewer connection
    if not connected_clients:
        waited = 0
        while waited < 2 and not connected_clients:
            time.sleep(0.1)
            waited += 0.1
        if not connected_clients:
            raise ConnectionError("No viewer connected to WebSocket")

    import uuid

    global screenshot_result, waiting_screenshot_id
    waiting_screenshot_id = uuid.uuid4().hex
    screenshot_result = None
    screenshot_event.clear()

    # Request screenshot with correlation id
    send_to_clients({"action": "get_screenshot", "id": waiting_screenshot_id})

    if not screenshot_event.wait(timeout=timeout):
        waiting_screenshot_id = None
        raise TimeoutError("Viewer did not return screenshot in time")

    waiting_screenshot_id = None
    return screenshot_result
