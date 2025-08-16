#!/usr/bin/env python3
"""
Phone Remote Control Server
Control your PC using your phone as a wireless mouse and keyboard
"""

import asyncio
import websockets
import json
import pyautogui
import socket
import os
import sys
from pathlib import Path
from aiohttp import web

# Configure pyautogui for remote control
pyautogui.FAILSAFE = False
pyautogui.PAUSE = 0.01

# Check for admin privileges on Windows
if sys.platform == 'win32':
    import ctypes
    try:
        is_admin = ctypes.windll.shell32.IsUserAnAdmin()
        if not is_admin:
            print("WARNING: Running without administrator privileges.")
            print("  Some applications may not respond to clicks.")
            print("  To fix: Run as administrator")
    except:
        pass

# Store connected clients
clients = set()

async def handle_websocket(websocket):
    """Handle WebSocket connections from phones"""
    clients.add(websocket)
    client_ip = websocket.remote_address[0] if websocket.remote_address else "unknown"
    print(f"[+] Phone connected from {client_ip}")
    
    try:
        async for message in websocket:
            try:
                data = json.loads(message)
                
                if data['type'] == 'mouse_move':
                    pyautogui.moveRel(data['dx'], data['dy'])
                
                elif data['type'] == 'click':
                    button = data.get('button', 'left')
                    if data.get('double'):
                        pyautogui.doubleClick(button=button)
                    else:
                        pyautogui.click(button=button)
                
                elif data['type'] == 'mousedown':
                    pyautogui.mouseDown(button=data['button'])
                
                elif data['type'] == 'mouseup':
                    pyautogui.mouseUp(button=data['button'])
                
                elif data['type'] == 'scroll':
                    pyautogui.scroll(data['dy'])
                
                elif data['type'] == 'key':
                    pyautogui.press(data['key'])
                
                elif data['type'] == 'combo':
                    pyautogui.hotkey(*data['keys'])
                
                elif data['type'] == 'type':
                    pyautogui.write(data['text'])
                
            except Exception as e:
                print(f"[ERROR] Error processing command: {e}")
                
    except websockets.exceptions.ConnectionClosed:
        pass
    finally:
        clients.remove(websocket)
        print(f"[-] Phone disconnected from {client_ip}")

async def serve_interface(request):
    """Serve the HTML interface"""
    # Determine which version to serve
    path = request.path.strip('/')
    
    if path == 'stable':
        file_name = 'stable.html'
    elif path == '' or path == 'latest':
        file_name = 'latest.html'
    else:
        return web.Response(text="Not Found", status=404)
    
    # Read and serve the HTML file
    try:
        file_path = Path(__file__).parent / file_name
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        return web.Response(text=content, content_type='text/html')
    except FileNotFoundError:
        return web.Response(text=f"Interface file '{file_name}' not found", status=404)

async def serve_home(request):
    """Serve a home page with version selection"""
    home_html = """
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Phone Remote Control</title>
        <style>
            body {
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                display: flex;
                justify-content: center;
                align-items: center;
                height: 100vh;
                margin: 0;
            }
            .container {
                text-align: center;
                padding: 20px;
            }
            h1 {
                margin-bottom: 30px;
                font-size: 2.5em;
            }
            .versions {
                display: flex;
                gap: 20px;
                justify-content: center;
                flex-wrap: wrap;
            }
            .version-card {
                background: rgba(255, 255, 255, 0.1);
                padding: 30px;
                border-radius: 15px;
                text-decoration: none;
                color: white;
                transition: all 0.3s;
                min-width: 200px;
            }
            .version-card:hover {
                background: rgba(255, 255, 255, 0.2);
                transform: scale(1.05);
            }
            .version-title {
                font-size: 1.5em;
                font-weight: bold;
                margin-bottom: 10px;
            }
            .version-desc {
                opacity: 0.9;
                font-size: 0.9em;
            }
            .recommended {
                background: rgba(76, 175, 80, 0.3);
                border: 2px solid #4caf50;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Phone Remote Control</h1>
            <div class="versions">
                <a href="/latest" class="version-card recommended">
                    <div class="version-title">Latest</div>
                    <div class="version-desc">
                        Double-tap clicking<br>
                        Enhanced gestures<br>
                        Better performance<br>
                        <strong>Recommended</strong>
                    </div>
                </a>
                <a href="/stable" class="version-card">
                    <div class="version-title">Stable</div>
                    <div class="version-desc">
                        Original version<br>
                        Simple interface<br>
                        Proven reliability
                    </div>
                </a>
            </div>
        </div>
    </body>
    </html>
    """
    return web.Response(text=home_html, content_type='text/html')

def get_local_ip():
    """Get the local IP address"""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "127.0.0.1"

async def main():
    """Main server function"""
    local_ip = get_local_ip()
    http_port = 8080
    ws_port = 8765
    
    # Create HTTP server
    app = web.Application()
    app.router.add_get('/', serve_home)
    app.router.add_get('/latest', serve_interface)
    app.router.add_get('/stable', serve_interface)
    
    # Start WebSocket server
    ws_server = await websockets.serve(handle_websocket, '0.0.0.0', ws_port)
    
    print("\n" + "="*50)
    print("PHONE REMOTE CONTROL SERVER")
    print("="*50)
    print(f"\n[OK] Server running at: http://{local_ip}:{http_port}")
    print(f"[WS] WebSocket port: {ws_port}")
    print(f"\nDirect links:")
    print(f"   Latest: http://{local_ip}:{http_port}/latest")
    print(f"   Stable: http://{local_ip}:{http_port}/stable")
    print("\n" + "="*50)
    print("Press Ctrl+C to stop")
    print("="*50 + "\n")
    
    # Start HTTP server
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', http_port)
    await site.start()
    
    # Keep server running
    await asyncio.Future()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\nServer stopped.")