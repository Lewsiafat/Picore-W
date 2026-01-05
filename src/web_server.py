import uasyncio as asyncio
import gc

class WebServer:
    """
    A lightweight asynchronous Web Server.
    Supports basic routing and method handling with POST body parsing.
    """
    def __init__(self):
        self._routes = {}
        self._running = False
        self._server = None

    def add_route(self, path, handler, method="GET"):
        """Manually register a route handler."""
        self._routes[(path, method)] = handler

    async def start(self, host='0.0.0.0', port=80):
        if not self._running:
            self._running = True
            print(f"WebServer: Starting on {host}:{port}")
            self._server = await asyncio.start_server(self._handle_client, host, port)

    def stop(self):
        if self._running and self._server:
            self._server.close()
            self._running = False
            print("WebServer: Stopped")

    async def _handle_client(self, reader, writer):
        try:
            request_line = await reader.readline()
            if not request_line:
                writer.close()
                return

            request_line = request_line.decode().strip()
            if not request_line:
                 writer.close()
                 return
                 
            method, path, _ = request_line.split(" ", 2)
            
            # Read headers
            headers = {}
            content_length = 0
            while True:
                line = await reader.readline()
                if not line or line == b'\r\n':
                    break
                
                line = line.decode().strip()
                if ':' in line:
                    key, value = line.split(":", 1)
                    headers[key.lower()] = value.strip()
                    if key.lower() == 'content-length':
                        content_length = int(value.strip())

            # Read Body if POST
            body = ""
            if method == "POST" and content_length > 0:
                body_bytes = await reader.read(content_length)
                body = body_bytes.decode()

            # Prepare request object (dictionary for simplicity)
            request = {
                "method": method,
                "path": path,
                "headers": headers,
                "body": body,
                "params": self._parse_params(body) if body else {}
            }
            
            print(f"WebServer: {method} {path}")
            
            # Find handler
            handler = self._routes.get((path, method))
            
            # Captive Portal Fallback
            if not handler:
                if method == "GET":
                     # Default to root for any unknown GET (Captive Portal behavior)
                     handler = self._routes.get(("/", "GET"))
            
            if handler:
                response = await handler(request)
                writer.write(response)
                await writer.drain()
            else:
                writer.write(b"HTTP/1.1 404 Not Found\r\n\r\nNot Found")
                await writer.drain()
                
        except Exception as e:
            print(f"WebServer: Error: {e}")
        finally:
            try:
                writer.close()
                await writer.wait_closed()
            except:
                pass

    def _parse_params(self, body):
        """Parse URL-encoded body parameters."""
        params = {}
        if not body: return params
        try:
            pairs = body.split('&')
            for pair in pairs:
                if '=' in pair:
                    key, value = pair.split('=', 1)
                    # Simple URL decoding (replace + with space, %xx with char)
                    value = value.replace('+', ' ')
                    # Basic % decoding
                    parts = value.split('%')
                    decoded_value = parts[0]
                    for part in parts[1:]:
                        if len(part) >= 2:
                            char_code = int(part[:2], 16)
                            decoded_value += chr(char_code) + part[2:]
                        else:
                            decoded_value += '%' + part
                    params[key] = decoded_value
        except Exception as e:
            print(f"WebServer: Error parsing params: {e}")
        return params