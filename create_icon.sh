#!/bin/bash

# Simple script to convert a PNG to macOS .icns icon format
# Usage: ./create_icon.sh your_icon.png

echo "================================================"
echo "  Icon Creator for macOS"
echo "================================================"
echo ""

# Check if a file was provided
if [ $# -eq 0 ]; then
    echo "Usage: ./create_icon.sh your_icon.png"
    echo ""
    echo "First, create or download a 1024x1024 PNG icon, then run:"
    echo "  ./create_icon.sh icon.png"
    echo ""
    echo "Quick ways to get an icon:"
    echo "  1. AI Generation: Use ChatGPT, Midjourney, or Canva AI"
    echo "  2. Design yourself: Use Canva or Figma"
    echo "  3. Convert online: Go to cloudconvert.com/png-to-icns"
    echo "  4. Hire someone: Fiverr.com ($20-50)"
    echo ""
    exit 1
fi

INPUT_FILE="$1"

# Check if input file exists
if [ ! -f "$INPUT_FILE" ]; then
    echo "❌ Error: File '$INPUT_FILE' not found!"
    exit 1
fi

# Check if it's a PNG
if [[ ! "$INPUT_FILE" =~ \.png$ ]]; then
    echo "⚠️  Warning: File should be a PNG image"
fi

echo "Converting $INPUT_FILE to app_icon.icns..."
echo ""

# Create iconset folder
ICONSET="AppIcon.iconset"
rm -rf "$ICONSET"
mkdir "$ICONSET"

# Generate all required sizes
echo "Generating icon sizes..."
sips -z 16 16     "$INPUT_FILE" --out "$ICONSET/icon_16x16.png" > /dev/null 2>&1
sips -z 32 32     "$INPUT_FILE" --out "$ICONSET/icon_16x16@2x.png" > /dev/null 2>&1
sips -z 32 32     "$INPUT_FILE" --out "$ICONSET/icon_32x32.png" > /dev/null 2>&1
sips -z 64 64     "$INPUT_FILE" --out "$ICONSET/icon_32x32@2x.png" > /dev/null 2>&1
sips -z 128 128   "$INPUT_FILE" --out "$ICONSET/icon_128x128.png" > /dev/null 2>&1
sips -z 256 256   "$INPUT_FILE" --out "$ICONSET/icon_128x128@2x.png" > /dev/null 2>&1
sips -z 256 256   "$INPUT_FILE" --out "$ICONSET/icon_256x256.png" > /dev/null 2>&1
sips -z 512 512   "$INPUT_FILE" --out "$ICONSET/icon_256x256@2x.png" > /dev/null 2>&1
sips -z 512 512   "$INPUT_FILE" --out "$ICONSET/icon_512x512.png" > /dev/null 2>&1
sips -z 1024 1024 "$INPUT_FILE" --out "$ICONSET/icon_512x512@2x.png" > /dev/null 2>&1

# Convert to .icns
echo "Creating .icns file..."
iconutil -c icns "$ICONSET"

# Rename and move
mv AppIcon.icns app_icon.icns
rm -rf "$ICONSET"

echo ""
echo "================================================"
echo "  ✓ Success!"
echo "================================================"
echo ""
echo "Created: app_icon.icns"
echo ""
echo "Next steps:"
echo "  1. Build your app: ./build_macos_app.sh"
echo "  2. Your app will now have the custom icon!"
echo ""

