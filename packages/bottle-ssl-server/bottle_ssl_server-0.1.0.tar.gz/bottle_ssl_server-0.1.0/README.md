# Bottle SSL Server

A lightweight, SSL-enabled web server built with Bottle and Cheroot, featuring file upload capabilities and request logging. This package provides a custom server adapter for secure HTTP communication and a CLI interface for easy configuration.

Inspired by [nickbabcock/bottle-ssl](https://github.com/nickbabcock/bottle-ssl).

## Features

- **SSL Support**: Runs a secure server with customizable SSL certificates.
- **File Uploads**: Handles file uploads via a `/upload` POST endpoint, saving files to an `uploads/` directory.
- **Request Logging**: Logs all incoming requests with server hostname, IP, method, path, and client IP.
- **CLI and Programmatic Usage**: Run the server via command-line arguments or programmatically with a Python function.
- **PyPI Ready**: Packaged for easy distribution and installation.

## Installation

Install the package via pip:

```bash
pip install bottle-ssl-server
```

## Requirements

- Python 3.6+
- `bottle>=0.12.18`
- `cheroot>=8.5.2`

## Usage

### Command-Line Interface

Run the server from the command line:

```bash
python -m bottle_ssl_server --host localhost --port 8080 --certfile path/to/cert.pem --keyfile path/to/key.pem --debug
```

**Options**:

- `--host`: Server host (default: `127.0.0.1`)
- `--port`: Server port (default: `8080`)
- `--certfile`: Path to SSL certificate file (required)
- `--keyfile`: Path to SSL key file (required)
- `--debug`: Enable debug logging

### Programmatic Usage

Run the server programmatically:

```python
from bottle_ssl_server import run_server

run_server(
    host='localhost',
    port=8080,
    certfile='path/to/cert.pem',
    keyfile='path/to/key.pem',
    debug=True
)
```

### File Upload

Upload files to the `/upload` endpoint using `curl`:

```bash
curl -k -X POST -F "file=@/path/to/test.txt" https://localhost:8080/upload
```

Or use an HTML form:

```html
<form action="https://localhost:8080/upload" method="post" enctype="multipart/form-data">
    <input type="file" name="file">
    <input type="submit" value="Upload">
</form>
```

Files are saved to the `uploads/` directory.

### Example Log Output

```
2025-07-09 18:37:10,123 localhost/127.0.0.1 - Received POST request for /upload from 127.0.0.1
2025-07-09 18:37:10,125 - File test.txt uploaded: saved to uploads/test.txt
```

## Development

To set up the project locally:

1. Clone the repository:

   ```bash
   git clone https://github.com/yourusername/bottle-ssl-server.git
   cd bottle-ssl-server
   ```

2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Generate SSL certificates (e.g., using OpenSSL):

   ```bash
   openssl req -x509 -newkey rsa:2048 -keyout localhost-key.pem -out localhost.pem -days 365 -nodes
   ```

4. Run the server:

   ```bash
   python -m bottle_ssl_server --certfile localhost.pem --keyfile localhost-key.pem
   ```

## License

MIT License. See [LICENSE](LICENSE) for details.

## Credits

This project is inspired by [nickbabcock/bottle-ssl](https://github.com/nickbabcock/bottle-ssl).
