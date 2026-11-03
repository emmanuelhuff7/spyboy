#!/bin/bash
# ═══════════════════════════════════════════════════════════════
# SPYBOY v2 — Oracle Cloud Always Free Setup Script
# Run this ONCE after SSH-ing into your new Oracle instance
# ═══════════════════════════════════════════════════════════════

set -e

echo "══════════════════════════════════════════"
echo "  SPYBOY v2 — Oracle Cloud Setup"
echo "══════════════════════════════════════════"

# Detect user (ubuntu for Ubuntu images, opc for Oracle Linux)
CURRENT_USER=$(whoami)
HOME_DIR=$(eval echo ~$CURRENT_USER)
echo "Running as: $CURRENT_USER"
echo "Home dir:   $HOME_DIR"

# Update system
echo ""
echo "[1/6] Updating system packages..."
sudo apt update && sudo apt upgrade -y

# Install Python and essentials
echo ""
echo "[2/6] Installing Python and dependencies..."
sudo apt install -y python3 python3-pip python3-venv curl iptables-persistent

# Create app directory
echo ""
echo "[3/6] Setting up app directory..."
mkdir -p $HOME_DIR/spyboy
cd $HOME_DIR/spyboy

# Create virtual environment
echo ""
echo "[4/6] Creating Python virtual environment..."
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install alpaca-py pandas numpy

# Get API credentials
echo ""
echo "[5/6] Configuring API credentials..."
echo "Enter your Alpaca paper trading credentials:"
echo "(These are stored locally in $HOME_DIR/spyboy/.env)"
echo ""
read -p "  API Key: " ALPACA_KEY
read -sp "  API Secret: " ALPACA_SECRET
echo ""

# Create secure environment file
cat > $HOME_DIR/spyboy/.env << EOF
ALPACA_API_KEY=${ALPACA_KEY}
ALPACA_API_SECRET=${ALPACA_SECRET}
ALPACA_PAPER=true
EOF
chmod 600 $HOME_DIR/spyboy/.env
echo "  Credentials saved securely."

# Create systemd service
echo ""
echo "[6/6] Creating systemd service..."
sudo tee /etc/systemd/system/spyboy.service > /dev/null << SERVICEFILE
[Unit]
Description=SPYBOY v2 — SPY Options Trading Bot
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
User=${CURRENT_USER}
WorkingDirectory=${HOME_DIR}/spyboy
EnvironmentFile=${HOME_DIR}/spyboy/.env
ExecStart=${HOME_DIR}/spyboy/venv/bin/python ${HOME_DIR}/spyboy/spyboy.py
Restart=always
RestartSec=30
StartLimitIntervalSec=300
StartLimitBurst=5

# Logging
StandardOutput=journal
StandardError=journal
SyslogIdentifier=spyboy

# Security
NoNewPrivileges=true

[Install]
WantedBy=multi-user.target
SERVICEFILE

# Make sure iptables allows outbound HTTPS (Alpaca API)
echo ""
echo "Configuring firewall for Alpaca API access..."
sudo iptables -F INPUT 2>/dev/null || true
sudo iptables -A INPUT -m state --state ESTABLISHED,RELATED -j ACCEPT
sudo iptables -A INPUT -p tcp --dport 22 -j ACCEPT
sudo iptables -A INPUT -i lo -j ACCEPT
sudo iptables -P OUTPUT ACCEPT
sudo netfilter-persistent save 2>/dev/null || true

# Test Alpaca connectivity
echo ""
echo "Testing Alpaca API connectivity..."
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" https://paper-api.alpaca.markets/v2/clock \
  -H "APCA-API-KEY-ID: ${ALPACA_KEY}" \
  -H "APCA-API-SECRET-KEY: ${ALPACA_SECRET}" 2>/dev/null || echo "000")

if [ "$HTTP_CODE" = "200" ]; then
    echo "  ✓ Alpaca API connection successful!"
elif [ "$HTTP_CODE" = "000" ]; then
    echo "  ✗ Could not reach Alpaca API. Check firewall settings."
    echo "    Try: sudo iptables -F && sudo netfilter-persistent save"
else
    echo "  ✗ Alpaca API returned HTTP $HTTP_CODE. Check your API keys."
fi

# Done
echo ""
echo "══════════════════════════════════════════════════════════"
echo "  Setup complete!"
echo ""
echo "  Next steps:"
echo "  1. Copy spyboy.py into ~/spyboy/"
echo "     mv ~/spyboy.py ~/spyboy/"
echo ""
echo "  2. Start the bot:"
echo "     sudo systemctl daemon-reload"
echo "     sudo systemctl enable spyboy"
echo "     sudo systemctl start spyboy"
echo ""
echo "  3. Watch it run:"
echo "     journalctl -u spyboy -f"
echo ""
echo "  Other commands:"
echo "     sudo systemctl status spyboy    # check status"
echo "     sudo systemctl restart spyboy   # restart"
echo "     sudo systemctl stop spyboy      # stop"
echo "     journalctl -u spyboy -n 50      # last 50 logs"
echo "     journalctl -u spyboy --since today  # today's logs"
echo "══════════════════════════════════════════════════════════"