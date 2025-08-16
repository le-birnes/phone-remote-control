#!/usr/bin/env python3
"""
Remote Control Server - Control your PC from Android phone
Run this on your computer to receive commands from phone
"""

import asyncio
import websockets
import json
import pyautogui
import socket
import qrcode
import io
import base64
from aiohttp import web
import os
import sys
import subprocess

# Install required packages
def install_requirements():
    packages = ['pyautogui', 'websockets', 'aiohttp', 'qrcode', 'pillow']
    for package in packages:
        try:
            __import__(package.replace('-', '_'))
        except ImportError:
            print(f"Installing {package}...")
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', package])

install_requirements()

import pyautogui
import websockets
from aiohttp import web
import qrcode
from PIL import Image

# Configure pyautogui
pyautogui.FAILSAFE = False  # Disable fail-safe for remote control
pyautogui.PAUSE = 0.01

# Try to run with elevated privileges on Windows
if sys.platform == 'win32':
    import ctypes
    try:
        # Check if running as admin
        is_admin = ctypes.windll.shell32.IsUserAnAdmin()
        if not is_admin:
            print("Note: Running without administrator privileges.")
            print("Some applications may not respond to clicks.")
            print("To fix: Run this script as administrator.")
    except:
        pass

# Store connected clients
clients = set()

# HTML interface
HTML_CONTENT = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>PC Remote Control</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
            -webkit-touch-callout: none;
            -webkit-user-select: none;
            user-select: none;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            height: 100vh;
            overflow: hidden;
            position: fixed;
            width: 100%;
        }
        
        .container {
            height: 100vh;
            display: flex;
            flex-direction: column;
            padding: 10px;
        }
        
        .header {
            text-align: center;
            padding: 10px;
            background: rgba(255, 255, 255, 0.1);
            border-radius: 10px;
            margin-bottom: 10px;
        }
        
        .status {
            display: inline-block;
            padding: 5px 10px;
            border-radius: 20px;
            font-size: 12px;
            margin-top: 5px;
        }
        
        .status.connected {
            background: #4caf50;
        }
        
        .status.disconnected {
            background: #f44336;
        }
        
        .controls {
            flex: 1;
            display: flex;
            flex-direction: column;
            gap: 10px;
        }
        
        .touchpad {
            flex: 1;
            background: rgba(255, 255, 255, 0.1);
            border-radius: 15px;
            position: relative;
            touch-action: none;
            min-height: 200px;
            border: 2px solid rgba(255, 255, 255, 0.3);
        }
        
        .touchpad-info {
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            opacity: 0.3;
            font-size: 18px;
            pointer-events: none;
        }
        
        .mouse-buttons {
            display: flex;
            gap: 10px;
            height: 60px;
        }
        
        .mouse-btn {
            flex: 1;
            background: rgba(255, 255, 255, 0.2);
            border: 2px solid rgba(255, 255, 255, 0.3);
            border-radius: 10px;
            color: white;
            font-size: 16px;
            font-weight: bold;
            display: flex;
            align-items: center;
            justify-content: center;
            cursor: pointer;
            transition: all 0.2s;
        }
        
        .mouse-btn:active {
            background: rgba(255, 255, 255, 0.4);
            transform: scale(0.95);
        }
        
        .actions {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 10px;
            margin-top: 10px;
        }
        
        .action-btn {
            background: rgba(255, 255, 255, 0.2);
            border: 2px solid rgba(255, 255, 255, 0.3);
            border-radius: 10px;
            color: white;
            padding: 15px;
            font-size: 14px;
            font-weight: bold;
            cursor: pointer;
            transition: all 0.2s;
            display: flex;
            align-items: center;
            justify-content: center;
            flex-direction: column;
        }
        
        .action-btn:active {
            background: rgba(255, 255, 255, 0.4);
            transform: scale(0.95);
        }
        
        .action-btn svg {
            width: 24px;
            height: 24px;
            margin-bottom: 5px;
        }
        
        .keyboard-toggle {
            position: fixed;
            bottom: 20px;
            right: 20px;
            width: 60px;
            height: 60px;
            background: #4caf50;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            cursor: pointer;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
            z-index: 1000;
        }
        
        .keyboard-toggle:active {
            transform: scale(0.9);
        }
        
        .keyboard-input {
            position: fixed;
            bottom: -100px;
            left: 0;
            width: 100%;
            opacity: 0;
            pointer-events: none;
        }
        
        .scroll-area {
            height: 80px;
            background: rgba(255, 255, 255, 0.1);
            border-radius: 10px;
            display: flex;
            align-items: center;
            justify-content: center;
            touch-action: none;
            border: 2px solid rgba(255, 255, 255, 0.3);
            margin-top: 10px;
        }
        
        @media (max-height: 600px) {
            .touchpad {
                min-height: 150px;
            }
            .actions {
                grid-template-columns: repeat(4, 1fr);
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h2>PC Remote Control</h2>
            <span id="status" class="status disconnected">Connecting...</span>
        </div>
        
        <div class="controls">
            <div class="touchpad" id="touchpad">
                <div class="touchpad-info">TOUCHPAD</div>
            </div>
            
            <div class="mouse-buttons">
                <div class="mouse-btn" id="leftClick">LEFT</div>
                <div class="mouse-btn" id="rightClick">RIGHT</div>
                <div class="mouse-btn" id="middleClick">MIDDLE</div>
            </div>
            
            <div class="scroll-area" id="scrollArea">
                <div>SCROLL (Swipe up/down)</div>
            </div>
            
            <div class="actions">
                <div class="action-btn" onclick="sendKey('escape')">
                    <svg fill="white" viewBox="0 0 24 24"><path d="M19 6.41L17.59 5 12 10.59 6.41 5 5 6.41 10.59 12 5 17.59 6.41 19 12 13.41 17.59 19 19 17.59 13.41 12z"/></svg>
                    ESC
                </div>
                <div class="action-btn" onclick="sendKey('enter')">
                    <svg fill="white" viewBox="0 0 24 24"><path d="M19 7v4H5.83l3.58-3.59L8 6l-6 6 6 6 1.41-1.41L5.83 13H21V7z"/></svg>
                    ENTER
                </div>
                <div class="action-btn" onclick="sendKey('space')">
                    <svg fill="white" viewBox="0 0 24 24"><path d="M18 9v4H6V9H4v6h16V9z"/></svg>
                    SPACE
                </div>
                <div class="action-btn" onclick="sendKey('backspace')">
                    <svg fill="white" viewBox="0 0 24 24"><path d="M22 3H7c-.69 0-1.23.35-1.59.88L0 12l5.41 8.11c.36.53.9.89 1.59.89h15c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zm-3 12.59L17.59 17 14 13.41 10.41 17 9 15.59 12.59 12 9 8.41 10.41 7 14 10.59 17.59 7 19 8.41 15.41 12 19 15.59z"/></svg>
                    BACK
                </div>
                <div class="action-btn" onclick="sendKey('tab')">
                    <svg fill="white" viewBox="0 0 24 24"><path d="M11.59 7.41L15.17 11H1v2h14.17l-3.59 3.59L13 18l6-6-6-6-1.41 1.41zM20 6v12h2V6h-2z"/></svg>
                    TAB
                </div>
                <div class="action-btn" onclick="sendCombo(['alt', 'tab'])">
                    <svg fill="white" viewBox="0 0 24 24"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z"/></svg>
                    ALT+TAB
                </div>
            </div>
        </div>
    </div>
    
    <div class="keyboard-toggle" onclick="toggleKeyboard()">
        <svg fill="white" viewBox="0 0 24 24" width="30" height="30">
            <path d="M20 5H4c-1.1 0-1.99.9-1.99 2L2 17c0 1.1.9 2 2 2h16c1.1 0 2-.9 2-2V7c0-1.1-.9-2-2-2zm-9 3h2v2h-2V8zm0 3h2v2h-2v-2zM8 8h2v2H8V8zm0 3h2v2H8v-2zm-1 2H5v-2h2v2zm0-3H5V8h2v2zm9 7H8v-2h8v2zm0-4h-2v-2h2v2zm0-3h-2V8h2v2zm3 3h-2v-2h2v2zm0-3h-2V8h2v2z"/>
        </svg>
    </div>
    
    <input type="text" id="keyboardInput" class="keyboard-input" />
    
    <script>
        let ws = null;
        let touchpadActive = false;
        let lastX = 0;
        let lastY = 0;
        let lastTouchTime = 0;
        
        // Connect to WebSocket
        function connect() {
            const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
            const wsUrl = `${protocol}//${window.location.hostname}:8765`;
            
            ws = new WebSocket(wsUrl);
            
            ws.onopen = () => {
                document.getElementById('status').textContent = 'Connected';
                document.getElementById('status').className = 'status connected';
            };
            
            ws.onclose = () => {
                document.getElementById('status').textContent = 'Disconnected';
                document.getElementById('status').className = 'status disconnected';
                setTimeout(connect, 2000);
            };
            
            ws.onerror = (error) => {
                console.error('WebSocket error:', error);
            };
        }
        
        // Send command to server
        function sendCommand(cmd) {
            if (ws && ws.readyState === WebSocket.OPEN) {
                ws.send(JSON.stringify(cmd));
            }
        }
        
        // Touchpad handling
        const touchpad = document.getElementById('touchpad');
        
        touchpad.addEventListener('touchstart', (e) => {
            e.preventDefault();
            touchpadActive = true;
            const touch = e.touches[0];
            lastX = touch.clientX;
            lastY = touch.clientY;
            lastTouchTime = Date.now();
        });
        
        touchpad.addEventListener('touchmove', (e) => {
            e.preventDefault();
            if (!touchpadActive) return;
            
            const touch = e.touches[0];
            const deltaX = touch.clientX - lastX;
            const deltaY = touch.clientY - lastY;
            
            // Send mouse move command
            sendCommand({
                type: 'mouse_move',
                dx: deltaX * 2,  // Multiply for sensitivity
                dy: deltaY * 2
            });
            
            lastX = touch.clientX;
            lastY = touch.clientY;
        });
        
        touchpad.addEventListener('touchend', (e) => {
            e.preventDefault();
            const touchDuration = Date.now() - lastTouchTime;
            
            // Tap to click
            if (touchDuration < 200) {
                sendCommand({ type: 'click', button: 'left' });
            }
            
            touchpadActive = false;
        });
        
        // Mouse buttons
        document.getElementById('leftClick').addEventListener('click', () => {
            sendCommand({ type: 'click', button: 'left' });
        });
        
        document.getElementById('rightClick').addEventListener('click', () => {
            sendCommand({ type: 'click', button: 'right' });
        });
        
        document.getElementById('middleClick').addEventListener('click', () => {
            sendCommand({ type: 'click', button: 'middle' });
        });
        
        // Scroll area
        const scrollArea = document.getElementById('scrollArea');
        let scrollStartY = 0;
        
        scrollArea.addEventListener('touchstart', (e) => {
            e.preventDefault();
            scrollStartY = e.touches[0].clientY;
        });
        
        scrollArea.addEventListener('touchmove', (e) => {
            e.preventDefault();
            const deltaY = e.touches[0].clientY - scrollStartY;
            sendCommand({
                type: 'scroll',
                dy: -Math.sign(deltaY) * 3
            });
            scrollStartY = e.touches[0].clientY;
        });
        
        // Keyboard functions
        function toggleKeyboard() {
            const input = document.getElementById('keyboardInput');
            input.focus();
            input.click();
        }
        
        document.getElementById('keyboardInput').addEventListener('input', (e) => {
            const value = e.target.value;
            if (value) {
                sendCommand({
                    type: 'type',
                    text: value
                });
                e.target.value = '';
            }
        });
        
        function sendKey(key) {
            sendCommand({
                type: 'key',
                key: key
            });
        }
        
        function sendCombo(keys) {
            sendCommand({
                type: 'combo',
                keys: keys
            });
        }
        
        // Prevent default touch behaviors
        document.addEventListener('touchmove', (e) => {
            if (e.target.closest('.touchpad') || e.target.closest('.scroll-area')) {
                e.preventDefault();
            }
        }, { passive: false });
        
        // Connect on load
        connect();
    </script>
</body>
</html>
"""

async def handle_websocket(websocket):
    """Handle WebSocket connections"""
    clients.add(websocket)
    try:
        print(f"Client connected from phone/browser")
    except Exception as e:
        print(f"Client connected")
    
    try:
        async for message in websocket:
            try:
                data = json.loads(message)
                
                if data['type'] == 'mouse_move':
                    pyautogui.moveRel(data['dx'], data['dy'])
                
                elif data['type'] == 'click':
                    button = data['button']
                    # Handle double-click
                    if data.get('double'):
                        pyautogui.doubleClick(button=button)
                    else:
                        pyautogui.click(button=button)
                
                elif data['type'] == 'mousedown':
                    # Mouse button down (for drag operations)
                    pyautogui.mouseDown(button=data['button'])
                
                elif data['type'] == 'mouseup':
                    # Mouse button up (end drag)
                    pyautogui.mouseUp(button=data['button'])
                
                elif data['type'] == 'scroll':
                    pyautogui.scroll(data['dy'])
                
                elif data['type'] == 'key':
                    pyautogui.press(data['key'])
                
                elif data['type'] == 'combo':
                    pyautogui.hotkey(*data['keys'])
                
                elif data['type'] == 'type':
                    pyautogui.write(data['text'])
                
                print(f"Executed: {data['type']}")
                
            except Exception as e:
                print(f"Error processing command: {e}")
                
    except websockets.exceptions.ConnectionClosed:
        pass
    except Exception as e:
        print(f"Connection error: {e}")
    finally:
        clients.remove(websocket)
        print(f"Client disconnected")

async def handle_http(request):
    """Serve HTML interface"""
    return web.Response(text=HTML_CONTENT, content_type='text/html')

async def handle_root(request):
    """Root handler"""
    return web.Response(text=HTML_CONTENT, content_type='text/html')

def get_local_ip():
    """Get local IP address"""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "127.0.0.1"

def generate_qr_code(url):
    """Generate QR code for easy mobile access"""
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(url)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    
    # Convert to ASCII art for terminal
    width = img.width // 2
    ascii_qr = []
    for y in range(0, img.height, 2):
        line = ""
        for x in range(0, img.width):
            if y < img.height - 1:
                top = img.getpixel((x, y))
                bottom = img.getpixel((x, y + 1))
                if top and bottom:
                    line += "█"
                elif top and not bottom:
                    line += "▀"
                elif not top and bottom:
                    line += "▄"
                else:
                    line += " "
            else:
                if img.getpixel((x, y)):
                    line += "▀"
                else:
                    line += " "
        ascii_qr.append(line)
    
    return "\n".join(ascii_qr)

async def main():
    """Main server function"""
    local_ip = get_local_ip()
    http_port = 8080
    ws_port = 8765
    
    # Create HTTP server
    app = web.Application()
    app.router.add_get('/', handle_root)
    
    # Start WebSocket server
    ws_server = await websockets.serve(handle_websocket, '0.0.0.0', ws_port)
    
    # Generate URL and QR code
    url = f"http://{local_ip}:{http_port}"
    qr_ascii = generate_qr_code(url)
    
    print("\n" + "="*50)
    print("PC REMOTE CONTROL SERVER")
    print("="*50)
    print(f"\n✓ Server running on: {url}")
    print(f"✓ WebSocket port: {ws_port}")
    print("\nScan QR code with your phone or enter URL in browser:\n")
    print(qr_ascii)
    print("\n" + "="*50)
    print("\nPress Ctrl+C to stop the server")
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