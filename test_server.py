import http.server
import socketserver
import socket

def get_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    ip = s.getsockname()[0]
    s.close()
    return ip

PORT = 8080
Handler = http.server.SimpleHTTPRequestHandler

print(f"Starting simple test server...")
print(f"Local IP: {get_ip()}")
print(f"Try accessing: http://{get_ip()}:{PORT}")
print(f"Or try: http://localhost:{PORT}")

with socketserver.TCPServer(("", PORT), Handler) as httpd:
    print(f"Server running on port {PORT}")
    httpd.serve_forever()