# killx.py
import socket
import threading
import json
import re
import os
import urllib.parse
from typing import Callable, Dict, Any, Optional, Union
from dataclasses import dataclass
import webbrowser
from pathlib import Path

@dataclass
class Route:
    path: str
    handler: Callable
    methods: list[str]
    params: list[str]

class Response:
    def __init__(self, content: Union[str, dict, bytes], status: int = 200, content_type: str = "text/html"):
        self.content = content
        self.status = status
        self.content_type = content_type
        self.headers = {}

    def add_header(self, key: str, value: str):
        self.headers[key] = value
        return self

    def to_http(self) -> bytes:
        status_text = {
            200: "OK",
            201: "Created",
            400: "Bad Request",
            404: "Not Found",
            405: "Method Not Allowed",
            500: "Internal Server Error"
        }.get(self.status, "OK")

        if isinstance(self.content, dict):
            content = json.dumps(self.content)
            self.content_type = "application/json"
        else:
            content = str(self.content)

        headers = [
            f"HTTP/1.1 {self.status} {status_text}",
            f"Content-Type: {self.content_type}",
            "Access-Control-Allow-Origin: *",
            "Access-Control-Allow-Methods: GET, POST, PUT, DELETE, OPTIONS",
            "Access-Control-Allow-Headers: Content-Type",
        ]

        for key, value in self.headers.items():
            headers.append(f"{key}: {value}")

        return f"{chr(10).join(headers)}\r\n\r\n{content}".encode()

class Killx:
    def __init__(self, template_dir: str = "templates", static_dir: str = "static", Debug: bool = False, RealTime: bool = False):
        self.routes: Dict[str, Route] = {}
        self.template_dir = template_dir
        self.static_dir = static_dir
        self.before_request_handlers: list[Callable] = []
        self.after_request_handlers: list[Callable] = []
        self.Debug = Debug
        self.RealTime = RealTime
        # Create necessary directories
        Path(template_dir).mkdir(exist_ok=True)
        Path(static_dir).mkdir(exist_ok=True)

    def log(self, message: str):
        if self.Debug:
            print(f"[Killx Debug] {message}")

    def render_template(self, template_name: str, **context) -> str:
        """Render a template with the given context"""
        template_path = Path(self.template_dir) / template_name
        if not template_path.exists():
            raise FileNotFoundError(f"Template {template_name} not found")
            
        with open(template_path, 'r') as f:
            content = f.read()
            
        # Simple template engine
        for key, value in context.items():
            content = content.replace('{{' + key + '}}', str(value))
            
        return content

    def serve_static(self, path: str) -> tuple[str, str]:
        """Serve static files"""
        file_path = Path(self.static_dir) / path.lstrip('/')
        if not file_path.exists():
            return 'text/plain', 'File not found'
            
        content_types = {
            '.css': 'text/css',
            '.js': 'application/javascript',
            '.jpg': 'image/jpeg',
            '.png': 'image/png',
            '.svg': 'image/svg+xml'
        }
        
        content_type = content_types.get(file_path.suffix, 'text/plain')
        with open(file_path, 'rb') as f:
            return content_type, f.read()

    def json(self, data: dict, status: int = 200) -> Response:
        """Helper method to create JSON responses"""
        return Response(data, status, "application/json")
        
    def route(self, path: str, methods: list[str] = None):
        if methods is None:
            methods = ["GET"]
            
        # Extract URL parameters
        params = re.findall(r'<([^>]+)>', path)
        # Convert path to regex pattern
        pattern = re.sub(r'<[^>]+>', r'([^/]+)', path)
            
        def decorator(handler: Callable):
            self.routes[pattern] = Route(
                path=path,
                handler=handler,
                methods=methods,
                params=params
            )
            return handler
        return decorator

    def find_route(self, path: str) -> tuple[Optional[Route], dict]:
        """Find matching route and extract URL parameters"""
        for pattern, route in self.routes.items():
            match = re.match(f"^{pattern}$", path)
            if match:
                params = dict(zip(route.params, match.groups()))
                return route, params
        return None, {}
    
    def parse_request(self, request: str) -> dict:
        try:
            request_lines = request.split('\n')
            first_line = request_lines[0]
            method, path, _ = first_line.split(' ')
            
            # Parse query parameters
            path_parts = path.split('?')
            base_path = path_parts[0]
            query_params = {}
            if len(path_parts) > 1:
                query_string = path_parts[1]
                query_params = dict(urllib.parse.parse_qs(query_string))
            
            headers = {}
            body = ""
            
            header_end = False
            for line in request_lines[1:]:
                if line.strip() == "":
                    header_end = True
                    continue
                    
                if not header_end:
                    if ': ' in line:
                        key, value = line.split(': ', 1)
                        headers[key.lower()] = value.strip()
                else:
                    body += line

            # Parse form data
            form_data = {}
            if method == "POST":
                content_type = headers.get('content-type', '')
                if 'application/x-www-form-urlencoded' in content_type:
                    form_data = dict(urllib.parse.parse_qs(body))
                elif 'application/json' in content_type:
                    try:
                        form_data = json.loads(body)
                    except json.JSONDecodeError:
                        pass

            return {
                "method": method,
                "path": base_path,
                "headers": headers,
                "query_params": query_params,
                "form_data": form_data,
                "body": body
            }
        except Exception as e:
            return {
                "method": "GET",
                "path": "/",
                "headers": {},
                "query_params": {},
                "form_data": {},
                "body": ""
            }

    def handle_client(self, client_socket: socket.socket):
        try:
            request_data = client_socket.recv(4096).decode('utf-8')
            request = self.parse_request(request_data)
            
            # Handle CORS preflight
            if request["method"] == "OPTIONS":
                response = Response("", 200).to_http()
                client_socket.send(response)
                return

            # Handle static files
            if request["path"].startswith('/static/'):
                content_type, content = self.serve_static(request["path"][7:])
                response = Response(content, 200, content_type).to_http()
                client_socket.send(response)
                return
            
            # Find matching route
            route, url_params = self.find_route(request["path"])
            if not route:
                response = Response("Page not found", 404).to_http()
                client_socket.send(response)
                return
                
            # Execute before request handlers
            for handler in self.before_request_handlers:
                handler(request)
                
            # Execute route handler
            if request["method"] not in route.methods:
                response = Response("Method not allowed", 405).to_http()
                client_socket.send(response)
                return
                
            # Add parameters to request
            request["url_params"] = url_params
            
            # Call handler with request object
            result = route.handler(request)
            
            # Convert result to Response if it isn't already
            if not isinstance(result, Response):
                result = Response(result)
            
            # Execute after request handlers
            for handler in self.after_request_handlers:
                result = handler(result)
                
            client_socket.send(result.to_http())
            
        except Exception as e:
            error_response = Response(str(e), 500).to_http()
            client_socket.send(error_response)
        finally:
            client_socket.close()
    
    def run(self, host: str = 'localhost', port: int = 8080):
        import sys
        import time
        import threading as th
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind((host, port))
        server_socket.listen(5)
        server_socket.settimeout(1.0)  # Set timeout to allow KeyboardInterrupt
        
        print(f"🔥 Killx server is running at http://{host}:{port}")
        print("Press Ctrl+C to quit")
        webbrowser.open(f"http://{host}:{port}")

        def watch_files_and_reload():
            last_mtimes = {}
            watch_paths = [sys.argv[0], self.template_dir]
            while True:
                changed = False
                for path in watch_paths:
                    if os.path.isdir(path):
                        for root, _, files in os.walk(path):
                            for f in files:
                                fp = os.path.join(root, f)
                                try:
                                    mtime = os.path.getmtime(fp)
                                    if fp not in last_mtimes:
                                        last_mtimes[fp] = mtime
                                    elif last_mtimes[fp] != mtime:
                                        changed = True
                                        last_mtimes[fp] = mtime
                                except Exception:
                                    continue
                    else:
                        try:
                            mtime = os.path.getmtime(path)
                            if path not in last_mtimes:
                                last_mtimes[path] = mtime
                            elif last_mtimes[path] != mtime:
                                changed = True
                                last_mtimes[path] = mtime
                        except Exception:
                            continue
                if changed:
                    print("[Killx RealTime] Detected change, reloading server...")
                    python = sys.executable
                    os.execv(python, [python] + sys.argv)
                time.sleep(1)

        if self.RealTime:
            th.Thread(target=watch_files_and_reload, daemon=True).start()
        
        try:
            while True:
                try:
                    client_socket, _ = server_socket.accept()
                    self.log("Accepted new connection")
                    client_thread = threading.Thread(target=self.handle_client, args=(client_socket,))
                    client_thread.start()
                except socket.timeout:
                    continue  # Allow loop to check for KeyboardInterrupt
        except KeyboardInterrupt:
            print("\n👋 Shutting down Killx server...")
        finally:
            server_socket.close()
