#!/bin/bash

echo "================================================"
echo "  🏥 Health AI Assistant - Web App"
echo "================================================"
echo ""
echo "Starting server..."
echo ""
echo "Access from:"
echo "  💻 Computer: http://localhost:5000"
echo ""
echo "  📱 Phone (same WiFi):"
IP=$(ipconfig getifaddr en0 2>/dev/null || hostname -I | awk '{print $1}')
if [ ! -z "$IP" ]; then
    echo "  http://$IP:5000"
else
    echo "  http://YOUR_IP_ADDRESS:5000"
    echo "  (Find your IP with: ifconfig getifaddr en0)"
fi
echo ""
echo "Press Ctrl+C to stop"
echo "================================================"
echo ""

python3 web_app.py

