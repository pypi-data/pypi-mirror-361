import asyncio
import http.server
import socketserver
import webbrowser
from pathlib import Path
import click
import rich
from rich.console import Console
from rich.panel import Panel
import watchdog.events
import watchdog.observers
import websockets

# --- Configuration ---
DEFAULT_PORT = 4005
MAX_PORTS_TO_TRY = 10
WATCH_GLOBS = ["*.html", "*.css", "*.js"]

# --- State ---
console = Console()
connected_clients = set()

# --- WebSocket Server ---
async def websocket_server(websocket):
    connected_clients.add(websocket)
    try:
        await websocket.wait_closed()
    finally:
        connected_clients.remove(websocket)

async def notify_clients_of_reload():
    if connected_clients:
        message = "reload"
        await asyncio.gather(*[client.send(message) for client in connected_clients])

# --- File System Watcher ---
class ChangeHandler(watchdog.events.PatternMatchingEventHandler):
    def __init__(self, patterns, loop):
        super().__init__(patterns=patterns)
        self.loop = loop

    def on_any_event(self, event):
        if event.event_type in ["modified", "created", "deleted", "moved"]:
            console.log(f"[yellow]File change detected:[/] {event.src_path}")
            asyncio.run_coroutine_threadsafe(notify_clients_of_reload(), self.loop)

# --- HTTP Server ---
class InjectedScriptHttpRequestHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        # In Python 3.9+, directory is a keyword argument
        if 'directory' in kwargs:
            self.directory = kwargs.pop('directory')
        else:
            self.directory = '.'  # Default to current directory
        super().__init__(*args, **kwargs)

    def end_headers(self):
        self.send_header("Cache-Control", "no-cache, no-store, must-revalidate")
        self.send_header("Pragma", "no-cache")
        self.send_header("Expires", "0")
        super().end_headers()

    def render_and_send_html(self, path):
        try:
            # Normalize and secure the path
            base_dir = Path(self.directory).resolve()
            requested_path = (base_dir / path).resolve()
            
            # Prevent directory traversal attacks
            if not requested_path.is_relative_to(base_dir):
                self.send_error(403, "Forbidden")
                return
                
            with open(requested_path, "r", encoding="utf-8") as f:
                content = f.read()
            
            # Inject the reload script
            reload_script = '''
                <script>
                    (function() {
                        const ws = new WebSocket("ws://localhost:5678");
                        ws.onmessage = function(event) {
                            if (event.data === "reload") {
                                window.location.reload();
                            }
                        };
                    })();
                </script>
            '''
            content = content.replace("</body>", f"{reload_script}</body>")
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.send_header("Content-Length", str(len(content)))
            self.end_headers()
            self.wfile.write(content.encode("utf-8"))
        except FileNotFoundError:
            self.send_error(404, "File not found")

    def do_GET(self):
        if self.path == '/':
            self.path = 'index.html'
        if self.path.endswith(".html"):
            self.render_and_send_html(self.path.lstrip("/"))
        else:
            super().do_GET()

# --- Main Application Logic ---
def find_available_port(start_port, max_ports):
    for port in range(start_port, start_port + max_ports):
        try:
            with socketserver.TCPServer(("localhost", port), None) as s:
                return port
        except OSError:
            continue
    return None

async def main_async(file, watch_dir, custom_port, no_open):
    # Determine watch directory
    if watch_dir:
        watch_path = Path(watch_dir)
    else:
        watch_path = Path(file).parent

    # Determine port
    if custom_port:
        port = custom_port
        try:
            with socketserver.TCPServer(("localhost", port), None) as s:
                pass
        except OSError:
            console.print(f"[red]Error:[/] Port {port} is already in use.")
            return
    else:
        port = find_available_port(DEFAULT_PORT, MAX_PORTS_TO_TRY)
        if not port:
            console.print(f"[red]Error:[/] Could not find an available port between {DEFAULT_PORT} and {DEFAULT_PORT + MAX_PORTS_TO_TRY - 1}.")
            return

    # --- Start Services ---
    console.print(Panel(
        f"[bold green]reloadify[/] is running!\n\n"
        f"[cyan]Serving on:[/] http://localhost:{port}\n"
        f"[cyan]Watching:[/] {watch_path}",
        expand=False,
        border_style="green"
    ))

    loop = asyncio.get_running_loop()

    # Start file watcher
    event_handler = ChangeHandler(patterns=WATCH_GLOBS, loop=loop)
    observer = watchdog.observers.Observer()
    observer.schedule(event_handler, str(watch_path), recursive=True)
    observer.start()

    # Configure and start HTTP server
    handler_class = lambda *args, **kwargs: InjectedScriptHttpRequestHandler(*args, directory=str(watch_path), **kwargs)
    httpd = socketserver.TCPServer(("localhost", port), handler_class)
    
    http_server_future = loop.run_in_executor(None, httpd.serve_forever)

    # Start WebSocket server
    async with websockets.serve(websocket_server, "localhost", 5678):
        if not no_open:
            webbrowser.open(f"http://localhost:{port}/{Path(file).name}")
        try:
            await http_server_future
        except KeyboardInterrupt:
            pass  # Allow graceful shutdown
        finally:
            observer.stop()
            observer.join()
            httpd.shutdown()
            console.print("\n[bold red]Server stopped.[/]")


@click.command()
@click.argument("file", default="index.html", type=click.Path(exists=True, dir_okay=False, resolve_path=True))
@click.option("-d", "--directory", "watch_dir", type=click.Path(exists=True, file_okay=False, resolve_path=True), help="Custom directory to watch.")
@click.option("-p", "--port", "custom_port", type=int, help="Custom port to serve on.")
@click.option("--no-open", "no_open", is_flag=True, help="Do not open the browser automatically.")
def main(file, watch_dir, custom_port, no_open):
    """A blazing-fast, ultra-lightweight Python CLI tool for live-reloading web content."""
    try:
        asyncio.run(main_async(file, watch_dir, custom_port, no_open))
    except KeyboardInterrupt:
        console.print("\n[bold red]Server stopped.[/]")

if __name__ == "__main__":
    main()
