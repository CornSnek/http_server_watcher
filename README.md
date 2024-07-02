# HTTP Server and Watcher Script
This is a simple python script in order to try to make a simple website. The script creates an `http.server.SimpleHTTPRequestHandler` object and uses the module [watchdog](https://pypi.org/project/watchdog/) to see if any `.js`, `.css`, or `.html` files have been edited. More extensions can be added by editing the array `EXTENSIONS_TO_WATCH` in the script. Every edit will open the last `.html` website last edited (Or open `http://localhost:{PORT}/index.html`).

# Known Bugs
When pressing `Ctrl+C` to kill the program, the program will open the browser again to open a website in a new tab. It is because `TCPServer.handle_request()` is blocking the server thread until it gets a request so that the thread can shut down successfully. If the server is still blocking, visit the `http://localhost:{PORT}/` again to try to shut down the server thread.

# TODO
Find a way to only open a website just once and not open multiple of them in a new tab.