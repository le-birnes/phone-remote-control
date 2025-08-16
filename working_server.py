#!/usr/bin/env python3
"""
Phone Remote Control Server - Working Version
With keyboard, sensitivity control, and improved tap gestures
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

# The HTML interface with all features
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
            -webkit-tap-highlight-color: transparent;
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
            display: flex;
            justify-content: space-between;
            align-items: center;
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
        }
        
        .status.connected {
            background: #4caf50;
        }
        
        .status.disconnected {
            background: #f44336;
        }
        
        .sensitivity-control {
            display: flex;
            align-items: center;
            gap: 10px;
            font-size: 12px;
        }
        
        .sensitivity-control input {
            width: 80px;
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
            font-size: 14px;
            pointer-events: none;
            text-align: center;
        }
        
        .gesture-indicator {
            position: fixed;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            background: rgba(76, 175, 80, 0.9);
            padding: 10px 20px;
            border-radius: 20px;
            font-size: 14px;
            display: none;
            z-index: 1000;
        }
        
        .mouse-buttons {
            display: flex;
            gap: 10px;
            height: 50px;
        }
        
        .mouse-btn {
            flex: 1;
            background: rgba(255, 255, 255, 0.2);
            border: 2px solid rgba(255, 255, 255, 0.3);
            border-radius: 10px;
            color: white;
            font-size: 14px;
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
        
        .mouse-btn.drag-active {
            background: #4caf50;
        }
        
        .scroll-area {
            height: 60px;
            background: rgba(255, 255, 255, 0.1);
            border-radius: 10px;
            display: flex;
            align-items: center;
            justify-content: center;
            touch-action: none;
            border: 2px solid rgba(255, 255, 255, 0.3);
            font-size: 14px;
        }
        
        .actions {
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 8px;
        }
        
        .action-btn {
            background: rgba(255, 255, 255, 0.2);
            border: 2px solid rgba(255, 255, 255, 0.3);
            border-radius: 8px;
            color: white;
            padding: 12px 5px;
            font-size: 12px;
            font-weight: bold;
            cursor: pointer;
            transition: all 0.2s;
        }
        
        .action-btn:active {
            background: rgba(255, 255, 255, 0.4);
            transform: scale(0.95);
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
            font-size: 24px;
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
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <span id="status" class="status disconnected">Connecting...</span>
            <div class="sensitivity-control">
                <span>Speed:</span>
                <input type="range" id="sensitivity" min="0.5" max="5" step="0.5" value="2">
                <span id="sensitivityValue">2.0</span>
            </div>
        </div>
        
        <div class="controls">
            <div class="touchpad" id="touchpad">
                <div class="touchpad-info">
                    TOUCHPAD<br>
                    Tap = Click<br>
                    Double-tap = Right-click<br>
                    Tap & Hold = Drag
                </div>
            </div>
            
            <div class="mouse-buttons">
                <div class="mouse-btn" id="leftClick">LEFT</div>
                <div class="mouse-btn" id="rightClick">RIGHT</div>
                <div class="mouse-btn" id="middleClick">MIDDLE</div>
                <div class="mouse-btn" id="dragToggle">DRAG</div>
            </div>
            
            <div class="scroll-area" id="scrollArea">
                SCROLL (Swipe up/down)
            </div>
            
            <div class="actions">
                <div class="action-btn" onclick="sendKey('escape')">ESC</div>
                <div class="action-btn" onclick="sendKey('enter')">ENTER</div>
                <div class="action-btn" onclick="sendKey('space')">SPACE</div>
                <div class="action-btn" onclick="sendKey('backspace')">BACK</div>
                <div class="action-btn" onclick="sendKey('tab')">TAB</div>
                <div class="action-btn" onclick="sendCombo(['alt', 'tab'])">ALT+TAB</div>
                <div class="action-btn" onclick="sendCombo(['ctrl', 'c'])">COPY</div>
                <div class="action-btn" onclick="sendCombo(['ctrl', 'v'])">PASTE</div>
                <div class="action-btn" onclick="sendCombo(['ctrl', 'z'])">UNDO</div>
                <div class="action-btn" onclick="sendCombo(['ctrl', 'a'])">ALL</div>
                <div class="action-btn" onclick="sendKey('delete')">DEL</div>
                <div class="action-btn" onclick="sendCombo(['win'])">WIN</div>
            </div>
        </div>
    </div>
    
    <div class="keyboard-toggle" onclick="toggleKeyboard()">⌨</div>
    <div class="gesture-indicator" id="gestureIndicator"></div>
    <input type="text" id="keyboardInput" class="keyboard-input" />
    
    <script>
        let ws = null;
        let touchpadActive = false;
        let lastX = 0;
        let lastY = 0;
        let lastTouchTime = 0;
        let tapCount = 0;
        let tapTimer = null;
        let holdTimer = null;
        let isDragging = false;
        let sensitivity = 2.0;
        
        // Gesture feedback
        function showGesture(text) {
            const indicator = document.getElementById('gestureIndicator');
            indicator.textContent = text;
            indicator.style.display = 'block';
            setTimeout(() => {
                indicator.style.display = 'none';
            }, 500);
        }
        
        // Sensitivity control
        document.getElementById('sensitivity').addEventListener('input', (e) => {
            sensitivity = parseFloat(e.target.value);
            document.getElementById('sensitivityValue').textContent = sensitivity.toFixed(1);
        });
        
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
        
        // Touchpad handling with new tap configuration
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
            
            // Handle tap counting
            const currentTime = Date.now();
            const tapInterval = currentTime - lastTouchTime;
            
            if (tapInterval < 300) {
                tapCount++;
            } else {
                tapCount = 1;
            }
            
            lastTouchTime = currentTime;
            
            // Clear existing timers
            if (tapTimer) clearTimeout(tapTimer);
            if (holdTimer) clearTimeout(holdTimer);
            
            // Set hold timer for drag detection
            holdTimer = setTimeout(() => {
                if (touchpadActive && !touchMoved) {
                    if (tapCount === 2) {
                        // Double tap and hold = start drag
                        isDragging = true;
                        sendCommand({ type: 'mousedown', button: 'left' });
                        showGesture('Drag Start');
                        document.getElementById('dragToggle').classList.add('drag-active');
                    }
                }
            }, 200);
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
            
            // Send mouse move command with sensitivity
            sendCommand({
                type: 'mouse_move',
                dx: deltaX * sensitivity,
                dy: deltaY * sensitivity
            });
            
            lastX = touch.clientX;
            lastY = touch.clientY;
        });
        
        touchpad.addEventListener('touchend', (e) => {
            e.preventDefault();
            
            // Clear hold timer
            if (holdTimer) clearTimeout(holdTimer);
            
            const touchDuration = Date.now() - touchStartTime;
            
            // Release drag if active
            if (isDragging) {
                sendCommand({ type: 'mouseup', button: 'left' });
                isDragging = false;
                document.getElementById('dragToggle').classList.remove('drag-active');
                showGesture('Drag End');
            } else if (!touchMoved && touchDuration < 300) {
                // Quick tap without movement
                if (tapCount >= 2) {
                    // Double tap = right click
                    clearTimeout(tapTimer);
                    sendCommand({ type: 'click', button: 'right' });
                    showGesture('Right Click');
                    tapCount = 0;
                } else {
                    // Single tap = left click
                    clearTimeout(tapTimer);
                    tapTimer = setTimeout(() => {
                        sendCommand({ type: 'click', button: 'left' });
                        showGesture('Click');
                        tapCount = 0;
                    }, 250);
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
        
        // Drag toggle
        document.getElementById('dragToggle').addEventListener('click', () => {
            isDragging = !isDragging;
            if (isDragging) {
                sendCommand({ type: 'mousedown', button: 'left' });
                document.getElementById('dragToggle').classList.add('drag-active');
                showGesture('Drag ON');
            } else {
                sendCommand({ type: 'mouseup', button: 'left' });
                document.getElementById('dragToggle').classList.remove('drag-active');
                showGesture('Drag OFF');
            }
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
            const deltaY = scrollStartY - e.touches[0].clientY;
            if (Math.abs(deltaY) > 10) {
                sendCommand({
                    type: 'scroll',
                    dy: Math.sign(deltaY) * 3
                });
                scrollStartY = e.touches[0].clientY;
            }
        });
        
        // Keyboard state management
        let keyboardOpen = false;
        
        // Keyboard toggle
        function toggleKeyboard() {
            const input = document.getElementById('keyboardInput');
            if (!keyboardOpen) {
                keyboardOpen = true;
                input.style.position = 'fixed';
                input.style.bottom = '0';
                input.style.opacity = '0.01';
                input.style.pointerEvents = 'auto';
                input.focus();
                // Prevent auto-reopening
                setTimeout(() => {
                    input.addEventListener('blur', handleKeyboardClose);
                }, 100);
            }
        }
        
        function handleKeyboardClose() {
            const input = document.getElementById('keyboardInput');
            keyboardOpen = false;
            input.style.bottom = '-100px';
            input.style.opacity = '0';
            input.style.pointerEvents = 'none';
            input.removeEventListener('blur', handleKeyboardClose);
            input.value = '';
        }
        
        // Keyboard input handling
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
        
        // Handle backspace and prevent reopening
        document.getElementById('keyboardInput').addEventListener('keydown', (e) => {
            if (e.key === 'Backspace' && e.target.value === '') {
                e.preventDefault();
                sendCommand({ type: 'key', key: 'backspace' });
            }
            // Close keyboard on Enter/Go
            if (e.key === 'Enter') {
                e.preventDefault();
                sendCommand({ type: 'key', key: 'enter' });
                handleKeyboardClose();
            }
        });
        
        // Prevent keyboard from auto-opening on page load or focus
        document.getElementById('keyboardInput').addEventListener('focus', (e) => {
            if (!keyboardOpen) {
                e.target.blur();
            }
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
            if (e.target.closest('.touchpad') || e.target.closest('.scroll-area')) {
                e.preventDefault();
            }
        }, { passive: false });
        
        // Prevent context menu
        document.addEventListener('contextmenu', (e) => {
            e.preventDefault();
        });
        
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
    print("PHONE REMOTE CONTROL - FULL VERSION")
    print("="*50)
    print(f"\nServer running at: http://{local_ip}:{http_port}")
    print(f"WebSocket port: {ws_port}")
    print("\nFeatures:")
    print("- Single tap = Left click")
    print("- Double tap = Right click")
    print("- Tap & hold after tap = Drag")
    print("- Adjustable sensitivity")
    print("- Keyboard button")
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