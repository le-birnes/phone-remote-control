# Phone Remote Control

Use your phone as a wireless mouse and keyboard for your PC via local WiFi.

## Features

- **Wireless Mouse Control**: Move cursor, click, and scroll from your phone
- **Keyboard Input**: Type on your PC using your phone's keyboard
- **Local Network**: Works over WiFi - no internet required
- **QR Code Connection**: Easy setup with QR code scanning
- **Cross-Platform**: Works with any phone browser (Android, iOS)
- **No App Required**: Runs entirely in your phone's web browser

## Installation

1. Install Python 3.x on your PC
2. Run the server:
   ```bash
   python remote_control_server.py
   ```
   Or double-click `start_remote_control.bat`

3. The script will auto-install required packages:
   - pyautogui
   - websockets
   - aiohttp
   - qrcode
   - pillow

## Usage

1. **Start the server** on your PC
2. **Note the IP address** displayed (e.g., `192.168.1.100:8080`)
3. **Open phone browser** and navigate to that address
4. **Use the interface**:
   - Touch and drag to move mouse
   - Tap to click
   - Use on-screen keyboard for typing
   - Swipe for scrolling

## System Requirements

- Python 3.7+
- Windows/Mac/Linux PC
- Phone with web browser
- Both devices on same WiFi network

## Files

- `remote_control_server.py` - Main server script
- `phone_remote_control.html` - Basic interface
- `phone_remote_control_v2.html` - Enhanced interface
- `start_remote_control.bat` - Windows launcher

## Security Note

This tool is designed for local network use only. The server binds to all network interfaces for convenience. Use only on trusted networks.

## Future Plans

- Camera streaming support
- Microphone audio capture
- File transfer capabilities
- Custom gestures
- Multi-device support

## License

Open source - Feel free to modify and extend!