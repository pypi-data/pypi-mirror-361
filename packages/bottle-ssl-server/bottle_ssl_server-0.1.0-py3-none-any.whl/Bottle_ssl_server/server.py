import os
import socket
import logging
import argparse
from bottle import ServerAdapter, Bottle, request, response

# Initialize Bottle app
app = Bottle()

# Configure logging with timestamp
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

UPLOAD_DIR = 'uploads'
# Ensure uploads directory exists
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)

@app.post('/upload')
def upload_file():
    """Handle file uploads and save them to the uploads directory."""
    upload = request.files.get('file')
    if not upload:
        response.status = 400
        return "No file uploaded"
    
    file_path = os.path.join(UPLOAD_DIR, upload.filename)
    try:
        upload.save(file_path, overwrite=True)
        logging.info(f"File uploaded: {upload.filename} saved to {file_path}")
        return f"File {upload.filename} uploaded successfully"
    except Exception as e:
        logging.error(f"Failed to upload file {upload.filename}: {str(e)}")
        response.status = 500
        return f"Failed to upload file: {str(e)}"

class LoggingMiddleware:
    """Middleware to log incoming HTTP requests with server and client details."""
    def __init__(self, app, server_name):
        self.app = app
        self.server_name = server_name

    def __call__(self, environ, start_response):
        method = environ['REQUEST_METHOD']
        path = environ['PATH_INFO']
        ip = environ['REMOTE_ADDR']
        # server_name = environ['SERVER_NAME']
        server_name = self.server_name or 'unknown'
        try:
            server_ip = socket.gethostbyname(server_name)
        except socket.gaierror:
            server_ip = "unknown"
        # Log the request with server hostname and IP
        logging.info(f"{server_name}/{server_ip} - Received {method} request for {path} from {ip}")
        return self.app(environ, start_response)

class SSLCherootAdapter(ServerAdapter):
    """SSL-enabled Cheroot server adapter for Bottle.
    
    A custom server adapter for Bottle that enables SSL using Cheroot.
    Credits: Inspired by https://github.com/nickbabcock/bottle-ssl
    
    Args:
        host (str): Server host address (default: '127.0.0.1')
        port (int): Server port (default: 8080)
        certfile (str): Path to SSL certificate file
        keyfile (str): Path to SSL key file
        debug (bool): Enable debug logging (default: False)
    """
    
    def __init__(self, host='127.0.0.1', port=8080, **options):
        super(SSLCherootAdapter, self).__init__(host, port, **options)
        
        self.certfile = options.get('certfile')
        self.keyfile = options.get('keyfile')
        self.server_name = host
        
        if not self.certfile or not self.keyfile:
            raise ValueError("Both certfile and keyfile are required for SSL configuration")
    
    def run(self, handler):
        import ssl
        from cheroot import wsgi
        from cheroot.ssl.builtin import BuiltinSSLAdapter
        
        if self.options.get('debug', False):
            logging.getLogger().setLevel(logging.DEBUG)
            
        if self.options.get('reloader', False):
            logging.warning("Reloader is not supported with SSLCherootAdapter")

        handler = LoggingMiddleware(handler, self.server_name)

        server = wsgi.Server((self.host, self.port), handler)
        server.ssl_adapter = BuiltinSSLAdapter(self.certfile, self.keyfile)

        try:
            server.start()
        finally:
            server.stop()

def run_server(host='127.0.0.1', port=8080, certfile=None, keyfile=None, debug=False):
    """Run the Bottle server programmatically with SSL support.
    
    Args:
        host (str): Server host address (default: '127.0.0.1')
        port (int): Server port (default: 8080)
        certfile (str): Path to SSL certificate file
        keyfile (str): Path to SSL key file
        debug (bool): Enable debug logging (default: False)
    """
    
    app.run(
        host=host,
        port=port,
        server=SSLCherootAdapter,
        certfile=certfile,
        keyfile=keyfile,
        debug=debug
    )
    
def main():
    """Parse CLI arguments and run the SSL-enabled Bottle server."""
    parser = argparse.ArgumentParser(description="Run a Bottle server with SSL and file upload support.")
    parser.add_argument('--host', default='127.0.0.1', help='Server host (default: 127.0.0.1)')
    parser.add_argument('--port', type=int, default=8080, help='Server port (default: 8080)')
    parser.add_argument('--certfile', required=True, help='Path to SSL certificate file')
    parser.add_argument('--keyfile', required=True, help='Path to SSL key file')
    parser.add_argument('--debug', action='store_true', help='Enable debug logging')

    args = parser.parse_args()

    # Run the Bottle app with the provided configuration
    app.run(
        host=args.host,
        port=args.port,
        server=SSLCherootAdapter,
        certfile=args.certfile,
        keyfile=args.keyfile,
        debug=args.debug
    )

if __name__ == "__main__":
    main()