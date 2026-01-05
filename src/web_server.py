import uasyncio as asyncio
import gc

class WebServer:
    """
    A lightweight asynchronous Web Server.
    Supports basic routing and method handling.
    """
    def __init__(self):
        self._routes = {}
        self._running = False
        self._server = None

    def route(self, path, method="GET"):
        """Decorator to register a route handler."""
        def decorator(handler):
            self._routes[(path, method)] = handler
            return handler
        return decorator

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
            method, path, _ = request_line.split(" ", 2)
            
            print(f"WebServer: {method} {path}")
            
            # Read headers (consume until empty line)
            headers = {}
            while True:
                line = await reader.readline()
                if not line or line == b'\r\n':
                    break
                # Optional: Parse headers if needed
                # parts = line.decode().split(":", 1)
                # if len(parts) == 2: headers[parts[0].strip()] = parts[1].strip()

            # Handle POST body (simplified)
            body = None
            # (In a full implementation, we'd read Content-Length and read the body)
            
            # Find handler
            handler = self._routes.get((path, method))
            
            # Captive Portal: Fallback for unknown paths -> Redirect to root or serve portal
            if not handler:
                # If checking for connectivity (e.g., Apple/Android checks), return Success or Redirect
                if method == "GET":
                     # Default fallback: 302 Redirect to root
                     handler = self._handle_redirect_root
            
            if handler:
                response = await handler(request=None) # Pass request object in future
                writer.write(response)
                await writer.drain()
            else:
                writer.write(b"HTTP/1.1 404 Not Found\r\n\r\nNot Found")
                await writer.drain()
                
        except Exception as e:
            print(f"WebServer: Error: {e}")
        finally:
            writer.close()
            await writer.wait_closed()

    async def _handle_redirect_root(self, request):
        return b"HTTP/1.1 302 Found\r\nLocation: /\r\n\r\n"
