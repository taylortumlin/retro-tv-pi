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

# [1/10] Install system dependencies
echo "[1/10] Installing system dependencies..."
sudo apt update -qq
sudo apt install -y mpv python3 python3-pip python3-flask python3-requests python3-evdev python3-venv libpq-dev

# [2/10] Install Python packages
echo "[2/10] Installing Python packages..."
pip3 install --user --break-system-packages -r "$SCRIPT_DIR/requirements.txt" 2>/dev/null \
  || pip3 install --user -r "$SCRIPT_DIR/requirements.txt" 2>/dev/null \
  || true

# [3/10] Install Node.js (if not present) and build frontend
echo "[3/10] Building frontend..."
if ! command -v node &>/dev/null; then
    echo "  Installing Node.js..."
    curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
    sudo apt install -y nodejs
fi
if [ -d "$SCRIPT_DIR/frontend" ]; then
    cd "$SCRIPT_DIR/frontend"
    npm ci --production=false
    npm run build
    cd "$SCRIPT_DIR"
    echo "  Frontend built → static/dist/"
fi

# [4/10] Copy application files
echo "[4/10] Copying application files..."
mkdir -p "$INSTALL_DIR/templates" "$INSTALL_DIR/static" "$INSTALL_DIR/frontend"

cp "$SCRIPT_DIR/tv_player.py" "$INSTALL_DIR/"
cp -r "$SCRIPT_DIR/tv_guide" "$INSTALL_DIR/"
cp "$SCRIPT_DIR/requirements.txt" "$INSTALL_DIR/"

# config.json is gitignored (it holds the PIN + LAN IP + coords). On a
# fresh install, seed it from the sanitized example so the service can
# start; the user must then edit it.
if [ -f "$SCRIPT_DIR/config.json" ]; then
    cp "$SCRIPT_DIR/config.json" "$INSTALL_DIR/config.json"
elif [ -f "$INSTALL_DIR/config.json" ]; then
    echo "  --> Keeping existing $INSTALL_DIR/config.json"
else
    cp "$SCRIPT_DIR/config.example.json" "$INSTALL_DIR/config.json"
    echo "  --> Seeded $INSTALL_DIR/config.json from config.example.json -- edit before starting"
fi

# Copy new modules if they exist
for f in models.py auth.py widgets.py integrations.py init_db.py; do
    [ -f "$SCRIPT_DIR/$f" ] && cp "$SCRIPT_DIR/$f" "$INSTALL_DIR/"
done

cp "$SCRIPT_DIR/templates/"*.html "$INSTALL_DIR/templates/" 2>/dev/null || true
cp -r "$SCRIPT_DIR/static/"* "$INSTALL_DIR/static/"

# Copy frontend source for builds
cp -r "$SCRIPT_DIR/frontend/src" "$INSTALL_DIR/frontend/"
cp "$SCRIPT_DIR/frontend/package.json" "$SCRIPT_DIR/frontend/package-lock.json" \
   "$SCRIPT_DIR/frontend/vite.config.ts" "$SCRIPT_DIR/frontend/svelte.config.js" \
   "$SCRIPT_DIR/frontend/tsconfig.json" "$SCRIPT_DIR/frontend/tsconfig.app.json" \
   "$SCRIPT_DIR/frontend/tsconfig.node.json" "$SCRIPT_DIR/frontend/index.html" \
   "$INSTALL_DIR/frontend/"

chmod +x "$INSTALL_DIR/tv_player.py"

# [5/10] Create .env if it doesn't exist
if [ ! -f "$INSTALL_DIR/.env" ]; then
    echo "[5/10] Creating .env from template..."
    cp "$SCRIPT_DIR/.env.example" "$INSTALL_DIR/.env"
    # Generate a random secret key
    SECRET=$(python3 -c "import secrets; print(secrets.token_hex(32))")
    sed -i "s/generate-a-random-key-here/$SECRET/" "$INSTALL_DIR/.env"
    echo "  --> Edit $INSTALL_DIR/.env with your settings"
else
    echo "[5/10] .env already exists, skipping..."
fi

# [6/10] Install systemd services
echo "[6/10] Installing systemd services..."
sudo cp "$SCRIPT_DIR/tv-player.service" /etc/systemd/system/
sudo cp "$SCRIPT_DIR/tv-guide.service" /etc/systemd/system/
sudo systemctl daemon-reload

# [7/10] Add user to required groups
echo "[7/10] Setting up permissions..."
sudo usermod -a -G video,render,input "$USER"

# [8/10] Enable services
echo "[8/10] Enabling services..."
sudo systemctl enable tv-player tv-guide

# [9/10] Install cloudflared (optional)
echo "[9/10] Cloudflare Tunnel setup..."
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
echo "   python3 -m tv_guide  (from $INSTALL_DIR)"
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
