import os
import http.server
import socketserver
import threading
import time
import logging
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import time
import webbrowser

PORT = 80
DIRECTORY_TO_WATCH = "./"
EXTENSIONS_TO_WATCH = [".css",".js",".html"]

logging.basicConfig(level=logging.INFO,
                    format='[%(asctime)s] %(message)s',
                    datefmt='%H:%M:%S')
class MyHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY_TO_WATCH, **kwargs)
class ChangeHandler(FileSystemEventHandler):
    def __init__(self):
        self.debounced_events=None #Because FileSystemEventHandler is called twice when saving to an affected file, debounce the cloned event
        self.current_file=None
    def on_modified(self, event):
        if event==self.debounced_events:
            self.debounced_events=None
            return
        for ext in EXTENSIONS_TO_WATCH:
          if event.src_path.endswith(ext):
              if ext==".html": self.current_file=event.src_path[2:] #Exclude './' string
              website=f'http://localhost:{PORT}/{self.current_file or ""}'
              logging.info(f"File changed: {self.current_file}. Opening last html file '{website}'")
              self.debounced_events=event
              webbrowser.open(website,0,False)
              time.sleep(0.25) #Sleep to prevent accidental twice events
              return

class ThreadLoop:
    def __init__(self):
        self.shutdown_flag = threading.Event()
    def shutdown(self):
        self.shutdown_flag.set()
    def is_shutdown(self):
        return self.shutdown_flag.is_set()
    
def run_server(thread_loop:ThreadLoop):
    handler = MyHandler
    with socketserver.TCPServer(("", PORT), handler) as httpd:
        logging.info(f"Serving at link 'http://localhost:{PORT}/'")
        try:
            while not thread_loop.is_shutdown():
                httpd.handle_request()
            logging.info("Shutting down server.")
        finally: pass

def run_watcher(thread_loop:ThreadLoop):
    logging.info(f"Watching files at directory '{DIRECTORY_TO_WATCH}' with extensions {EXTENSIONS_TO_WATCH}")
    event_handler = ChangeHandler()
    observer = Observer()
    observer.schedule(event_handler, DIRECTORY_TO_WATCH, recursive=True)
    observer.start()
    try:
        while not thread_loop.is_shutdown():
            time.sleep(1)
        logging.info("Shutting down watcher.")
    finally:
        observer.stop()
        observer.join()

if __name__ == "__main__":
    logging.info("Initializing server and watcher threads. Press Ctrl+C to shutdown...")
    os.chdir(DIRECTORY_TO_WATCH)
    thread_loop=ThreadLoop()
    server_thread = threading.Thread(target=run_server,args=(thread_loop,))
    server_thread.start()
    watcher_thread = threading.Thread(target=run_watcher,args=(thread_loop,))
    watcher_thread.start()
    try:
        while True: time.sleep(1)
    finally: #Ctrl+C is used
        thread_loop.shutdown()
        time.sleep(1)
        webbrowser.open(f'http://localhost:{PORT}/',0,False) #To unblock the server to shutdown
        watcher_thread.join()
        server_thread.join()
        logging.info("Shutting down server and watcher.")
        exit(1)