# Phone Remote Control

Use your phone as a wireless mouse and keyboard for your PC via local WiFi.

## Features

- **Wireless Mouse Control**: Move cursor, click, and scroll from your phone
- **Double-tap Clicking**: Quick double-tap for easy clicking (Latest version)
- **Keyboard Input**: Type on your PC using your phone's keyboard
- **Gesture Support**: Long press for right-click, drag mode, and more
- **Two Versions**: Choose between Latest (enhanced) or Stable (original)
- **Local Network**: Works over WiFi - no internet required
- **Cross-Platform**: Works with any phone browser (Android, iOS)
- **No App Required**: Runs entirely in your phone's web browser

## Quick Start

### Installation

1. Install Python 3.7+ on your PC
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### Running the Server

**Option 1: Regular mode**
```bash
python server.py
```
Or double-click `start.bat`

**Option 2: Administrator mode** (recommended for full functionality)
```bash
# Run as administrator for terminal/system app access
start_admin.bat
```

### Connecting from Phone

1. Note the IP address shown in the server console (e.g., `192.168.1.100:8080`)
2. Open your phone's browser
3. Navigate to the server address
4. Choose your version:
   - **Latest** (`/latest`) - Enhanced with double-tap, better gestures
   - **Stable** (`/stable`) - Original simple interface

## Usage Guide

### Latest Version Features
- **Double-tap** - Single click (easier on mobile)
- **Single tap** - Also clicks
- **Long press** - Right-click
- **Double-tap and hold** - Start drag mode
- **Two-finger tap** - Right-click
- **Swipe on scroll area** - Scroll up/down

### Controls Available
- Full mouse movement and clicking
- Keyboard input with special keys
- Common shortcuts (Alt+Tab, Ctrl+C/V, etc.)
- ESC, Enter, Space, Backspace, Tab
- Windows key access

## Files Structure

```
phone-remote-control/
├── server.py           # Main server (serves both versions)
├── latest.html         # Enhanced interface with double-tap
├── stable.html         # Original stable interface
├── start.bat           # Quick launcher
├── start_admin.bat     # Admin launcher (for system access)
├── requirements.txt    # Python dependencies
└── README.md          # This file
```

## System Requirements

- **PC**: Windows/Mac/Linux with Python 3.7+
- **Phone**: Any modern smartphone with web browser
- **Network**: Both devices on same WiFi network

## Troubleshooting

### Can't click on certain windows?
Run the server as administrator using `start_admin.bat`

### Connection refused?
- Check firewall settings
- Ensure both devices are on same network
- Verify the IP address is correct

### Double-tap not working?
Make sure you're using the `/latest` version

## Security Note

This tool is designed for local network use only. The server binds to all network interfaces for convenience. Use only on trusted networks.

## License

Open source - Feel free to modify and extend!

## Contributing

Found a bug or have a feature request? Open an issue on GitHub:
https://github.com/le-birnes/phone-remote-control