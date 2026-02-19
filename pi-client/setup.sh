#!/bin/bash
# Pi TV Setup Script — installs both Player and Guide services
# Run this on your Raspberry Pi (without sudo — it will prompt when needed)

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
INSTALL_DIR="$HOME/pi-tv"

echo "========================================"
echo "  Pi TV Setup"
echo "========================================"
echo ""
echo "Source:  $SCRIPT_DIR"
echo "Install: $INSTALL_DIR"
echo ""

# Check if running as root
if [ "$EUID" -eq 0 ]; then
    echo "Please run without sudo (script will ask for sudo when needed)"
    exit 1
fi

# [1/6] Install system dependencies
echo "[1/6] Installing system dependencies..."
sudo apt update -qq
sudo apt install -y mpv python3 python3-pip python3-flask python3-requests python3-evdev

# Install feedparser (not always in apt)
pip3 install --user --break-system-packages feedparser 2>/dev/null || pip3 install --user feedparser 2>/dev/null || true

# [2/6] Copy application files
echo "[2/6] Copying application files..."
mkdir -p "$INSTALL_DIR/templates" "$INSTALL_DIR/static"

cp "$SCRIPT_DIR/tv_player.py" "$INSTALL_DIR/"
cp "$SCRIPT_DIR/tv_guide.py" "$INSTALL_DIR/"
cp "$SCRIPT_DIR/config.json" "$INSTALL_DIR/"

cp "$SCRIPT_DIR/templates/"*.html "$INSTALL_DIR/templates/"
cp -r "$SCRIPT_DIR/static/"* "$INSTALL_DIR/static/"

chmod +x "$INSTALL_DIR/tv_player.py" "$INSTALL_DIR/tv_guide.py"

# [3/6] Install systemd services
echo "[3/6] Installing systemd services..."
sudo cp "$SCRIPT_DIR/tv-player.service" /etc/systemd/system/
sudo cp "$SCRIPT_DIR/tv-guide.service" /etc/systemd/system/
sudo systemctl daemon-reload

# [4/6] Add user to required groups
echo "[4/6] Setting up permissions..."
sudo usermod -a -G video,render,input "$USER"

# [5/6] Enable services
echo "[5/6] Enabling services..."
sudo systemctl enable tv-player tv-guide

# [6/6] Done
echo "[6/6] Setup complete!"
echo ""
echo "========================================"
echo "  Next Steps"
echo "========================================"
echo ""
echo "1. Edit the config file:"
echo "   nano $INSTALL_DIR/config.json"
echo "   - Set 'ersatztv_url' to your ErsatzTV server address"
echo "   - Adjust channels to match your ErsatzTV setup"
echo ""
echo "2. Test manually first:"
echo "   python3 $INSTALL_DIR/tv_player.py"
echo "   python3 $INSTALL_DIR/tv_guide.py"
echo ""
echo "3. Start the services:"
echo "   sudo systemctl start tv-player tv-guide"
echo ""
echo "4. Access from any device on your network:"
echo "   Player/Remote:  http://$(hostname -I | awk '{print $1}'):5000"
echo "   TV Guide:       http://$(hostname -I | awk '{print $1}'):5001"
echo ""
echo "5. View logs:"
echo "   journalctl -u tv-player -f"
echo "   journalctl -u tv-guide -f"
echo ""
echo "========================================"
