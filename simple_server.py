#!/usr/bin/env python3
"""
Simple Phone Remote Control Server with Embedded HTML
Works just like the original version
"""

import asyncio
import websockets
import json
import pyautogui
import socket
from aiohttp import web

# Configure pyautogui
pyautogui.FAILSAFE = False
pyautogui.PAUSE = 0.01

# The HTML interface (embedded directly)
HTML_INTERFACE = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>Phone Remote Control</title>
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
        }
        
        .action-btn:active {
            background: rgba(255, 255, 255, 0.4);
            transform: scale(0.95);
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
                <div class="touchpad-info">TOUCHPAD<br>Double-tap to click</div>
            </div>
            
            <div class="mouse-buttons">
                <div class="mouse-btn" id="leftClick">LEFT</div>
                <div class="mouse-btn" id="rightClick">RIGHT</div>
                <div class="mouse-btn" id="middleClick">MIDDLE</div>
            </div>
            
            <div class="actions">
                <div class="action-btn" onclick="sendKey('escape')">ESC</div>
                <div class="action-btn" onclick="sendKey('enter')">ENTER</div>
                <div class="action-btn" onclick="sendKey('space')">SPACE</div>
                <div class="action-btn" onclick="sendKey('backspace')">BACK</div>
                <div class="action-btn" onclick="sendKey('tab')">TAB</div>
                <div class="action-btn" onclick="sendCombo(['alt', 'tab'])">ALT+TAB</div>
            </div>
        </div>
    </div>
    
    <script>
        let ws = null;
        let touchpadActive = false;
        let lastX = 0;
        let lastY = 0;
        let lastTouchTime = 0;
        let tapCount = 0;
        let tapTimer = null;
        
        // Connect to WebSocket server
        function connect() {
            const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
            const wsUrl = protocol + '//' + window.location.hostname + ':8765';
            
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
        
        // Touchpad handling with double-tap for click
        const touchpad = document.getElementById('touchpad');
        let touchStartTime = 0;
        let touchStartX = 0;
        let touchStartY = 0;
        let touchMoved = false;
        
        touchpad.addEventListener('touchstart', (e) => {
            e.preventDefault();
            touchpadActive = true;
            const touch = e.touches[0];
            lastX = touch.clientX;
            lastY = touch.clientY;
            touchStartX = touch.clientX;
            touchStartY = touch.clientY;
            touchStartTime = Date.now();
            touchMoved = false;
            
            // Handle double tap
            const currentTime = Date.now();
            const tapInterval = currentTime - lastTouchTime;
            
            if (tapInterval < 300) {
                tapCount++;
            } else {
                tapCount = 1;
            }
            
            lastTouchTime = currentTime;
            
            // Clear existing timer
            if (tapTimer) clearTimeout(tapTimer);
        });
        
        touchpad.addEventListener('touchmove', (e) => {
            e.preventDefault();
            if (!touchpadActive) return;
            
            const touch = e.touches[0];
            const deltaX = touch.clientX - lastX;
            const deltaY = touch.clientY - lastY;
            
            // Check if actually moved
            const totalMoveX = Math.abs(touch.clientX - touchStartX);
            const totalMoveY = Math.abs(touch.clientY - touchStartY);
            if (totalMoveX > 5 || totalMoveY > 5) {
                touchMoved = true;
            }
            
            // Send mouse move command
            sendCommand({
                type: 'mouse_move',
                dx: deltaX * 2,
                dy: deltaY * 2
            });
            
            lastX = touch.clientX;
            lastY = touch.clientY;
        });
        
        touchpad.addEventListener('touchend', (e) => {
            e.preventDefault();
            const touchDuration = Date.now() - touchStartTime;
            
            // Quick tap without movement
            if (!touchMoved && touchDuration < 300) {
                if (tapCount >= 2) {
                    // Double tap = click
                    clearTimeout(tapTimer);
                    sendCommand({ type: 'click', button: 'left' });
                    tapCount = 0;
                } else {
                    // Wait to see if it's a double tap
                    clearTimeout(tapTimer);
                    tapTimer = setTimeout(() => {
                        // Single tap - do nothing (just move)
                        tapCount = 0;
                    }, 300);
                }
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
        
        // Keyboard functions
        function sendKey(key) {
            sendCommand({ type: 'key', key: key });
        }
        
        function sendCombo(keys) {
            sendCommand({ type: 'combo', keys: keys });
        }
        
        // Prevent default touch behaviors
        document.addEventListener('touchmove', (e) => {
            if (e.target.closest('.touchpad')) {
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
    print(f"[+] Phone connected")
    
    try:
        async for message in websocket:
            try:
                data = json.loads(message)
                
                if data['type'] == 'mouse_move':
                    pyautogui.moveRel(data['dx'], data['dy'])
                
                elif data['type'] == 'click':
                    button = data.get('button', 'left')
                    pyautogui.click(button=button)
                
                elif data['type'] == 'key':
                    pyautogui.press(data['key'])
                
                elif data['type'] == 'combo':
                    pyautogui.hotkey(*data['keys'])
                
            except Exception as e:
                print(f"[ERROR] {e}")
                
    except websockets.exceptions.ConnectionClosed:
        pass
    finally:
        print(f"[-] Phone disconnected")

async def serve_html(request):
    """Serve the HTML interface"""
    return web.Response(text=HTML_INTERFACE, content_type='text/html')

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

async def main():
    """Main server function"""
    local_ip = get_local_ip()
    http_port = 8080
    ws_port = 8765
    
    # Create HTTP server
    app = web.Application()
    app.router.add_get('/', serve_html)
    
    # Start WebSocket server
    ws_server = await websockets.serve(handle_websocket, '0.0.0.0', ws_port)
    
    print("\n" + "="*50)
    print("PHONE REMOTE CONTROL - SIMPLE VERSION")
    print("="*50)
    print(f"\nServer running at: http://{local_ip}:{http_port}")
    print(f"WebSocket port: {ws_port}")
    print("\nOpen this address on your phone's browser")
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