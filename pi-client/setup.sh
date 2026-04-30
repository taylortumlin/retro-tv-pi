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

# [1/8] Install system dependencies
echo "[1/8] Installing system dependencies..."
sudo apt update -qq
sudo apt install -y mpv python3 python3-pip python3-flask python3-requests python3-evdev python3-venv libpq-dev

# [2/8] Install Python packages
echo "[2/8] Installing Python packages..."
pip3 install --user --break-system-packages -r "$SCRIPT_DIR/requirements.txt" 2>/dev/null \
  || pip3 install --user -r "$SCRIPT_DIR/requirements.txt" 2>/dev/null \
  || true

# [3/8] Copy application files
echo "[3/8] Copying application files..."
mkdir -p "$INSTALL_DIR/templates" "$INSTALL_DIR/static"

cp "$SCRIPT_DIR/tv_player.py" "$INSTALL_DIR/"
cp "$SCRIPT_DIR/tv_guide.py" "$INSTALL_DIR/"
cp "$SCRIPT_DIR/config.json" "$INSTALL_DIR/"
cp "$SCRIPT_DIR/requirements.txt" "$INSTALL_DIR/"

# Copy new modules if they exist
for f in models.py auth.py widgets.py integrations.py init_db.py; do
    [ -f "$SCRIPT_DIR/$f" ] && cp "$SCRIPT_DIR/$f" "$INSTALL_DIR/"
done

cp "$SCRIPT_DIR/templates/"*.html "$INSTALL_DIR/templates/"
cp -r "$SCRIPT_DIR/static/"* "$INSTALL_DIR/static/"

chmod +x "$INSTALL_DIR/tv_player.py" "$INSTALL_DIR/tv_guide.py"

# [4/8] Create .env if it doesn't exist
if [ ! -f "$INSTALL_DIR/.env" ]; then
    echo "[4/8] Creating .env from template..."
    cp "$SCRIPT_DIR/.env.example" "$INSTALL_DIR/.env"
    # Generate a random secret key
    SECRET=$(python3 -c "import secrets; print(secrets.token_hex(32))")
    sed -i "s/generate-a-random-key-here/$SECRET/" "$INSTALL_DIR/.env"
    echo "  --> Edit $INSTALL_DIR/.env with your settings"
else
    echo "[4/8] .env already exists, skipping..."
fi

# [5/8] Install systemd services
echo "[5/8] Installing systemd services..."
sudo cp "$SCRIPT_DIR/tv-player.service" /etc/systemd/system/
sudo cp "$SCRIPT_DIR/tv-guide.service" /etc/systemd/system/
sudo systemctl daemon-reload

# [6/8] Add user to required groups
echo "[6/8] Setting up permissions..."
sudo usermod -a -G video,render,input "$USER"

# [7/8] Enable services
echo "[7/8] Enabling services..."
sudo systemctl enable tv-player tv-guide

# [8/8] Install cloudflared (optional)
echo "[8/8] Cloudflare Tunnel setup..."
if ! command -v cloudflared &>/dev/null; then
    echo "  cloudflared not installed. To install:"
    echo "    curl -L https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-arm64.deb -o /tmp/cloudflared.deb"
    echo "    sudo dpkg -i /tmp/cloudflared.deb"
else
    echo "  cloudflared is installed: $(cloudflared --version)"
    echo "  To create tunnel: cloudflared tunnel create pitv"
    echo "  To add DNS:       cloudflared tunnel route dns pitv tv.ttumlinmedia.com"
fi

echo ""
echo "========================================"
echo "  Setup Complete!"
echo "========================================"
echo ""
echo "1. Edit your environment:"
echo "   nano $INSTALL_DIR/.env"
echo "   - Set ERSATZTV_URL, DB_URL, FLASK_SECRET_KEY, etc."
echo ""
echo "2. Test manually first:"
echo "   python3 $INSTALL_DIR/tv_player.py"
echo "   python3 $INSTALL_DIR/tv_guide.py"
echo ""
echo "3. Start the services:"
echo "   sudo systemctl start tv-player tv-guide"
echo ""
echo "4. Access:"
echo "   LAN Player:   http://$(hostname -I | awk '{print $1}'):5000"
echo "   LAN Guide:    http://$(hostname -I | awk '{print $1}'):5001"
echo "   Production:   https://tv.ttumlinmedia.com (after tunnel setup)"
echo ""
echo "5. View logs:"
echo "   journalctl -u tv-player -f"
echo "   journalctl -u tv-guide -f"
echo ""
echo "========================================"
