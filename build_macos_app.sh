#!/bin/bash

# Build script for Health AI Assistant - macOS App Bundle
# This creates a proper .app that looks like App Store apps

echo "================================================"
echo "  Health AI Assistant - macOS App Builder"
echo "================================================"
echo ""

# Check if pyinstaller is installed
if ! command -v pyinstaller &> /dev/null
then
    echo "Installing PyInstaller..."
    pip3 install pyinstaller
fi

echo "✓ PyInstaller is ready"
echo ""

# Clean previous builds
if [ -d "dist" ] || [ -d "build" ]; then
    echo "Cleaning previous builds..."
    rm -rf dist build *.spec
    echo "✓ Cleaned"
    echo ""
fi

# Check for icon file
if [ -f "app_icon.icns" ]; then
    echo "✓ Found app_icon.icns - building with custom icon"
    ICON_FLAG="--icon=app_icon.icns"
else
    echo "ℹ️  No app_icon.icns found - building with default icon"
    echo "   To add a custom icon, see: APP_STORE_GUIDE.md"
    ICON_FLAG=""
fi
echo ""

# Build the app as a proper macOS .app bundle
echo "Building macOS Application Bundle..."
echo ""

# Try to find pyinstaller (may be in user's local bin)
if command -v pyinstaller &> /dev/null; then
    PYINSTALLER="pyinstaller"
elif [ -f "$HOME/Library/Python/3.13/bin/pyinstaller" ]; then
    PYINSTALLER="$HOME/Library/Python/3.13/bin/pyinstaller"
elif [ -f "$HOME/Library/Python/3.12/bin/pyinstaller" ]; then
    PYINSTALLER="$HOME/Library/Python/3.12/bin/pyinstaller"
elif [ -f "$HOME/Library/Python/3.11/bin/pyinstaller" ]; then
    PYINSTALLER="$HOME/Library/Python/3.11/bin/pyinstaller"
else
    echo "❌ Error: Could not find pyinstaller"
    echo "Please run: pip3 install --user --break-system-packages pyinstaller"
    exit 1
fi

$PYINSTALLER --name="HealthAIAssistant" \
    --windowed \
    --onedir \
    $ICON_FLAG \
    --add-data "*.pdf:." \
    --hidden-import=PIL._tkinter_finder \
    --hidden-import=customtkinter \
    --hidden-import=openai \
    --hidden-import=PyPDF2 \
    --osx-bundle-identifier=com.healthai.assistant \
    --noconfirm \
    health_chatbot_gui.py

# Rename to proper name with spaces
if [ -d "dist/HealthAIAssistant.app" ]; then
    mv "dist/HealthAIAssistant.app" "dist/Health AI Assistant.app"
fi

# Check if build was successful
if [ $? -eq 0 ]; then
    echo ""
    echo "================================================"
    echo "  ✓ Build Successful!"
    echo "================================================"
    echo ""
    echo "Your app is ready at:"
    echo "  📦 dist/Health AI Assistant.app"
    echo ""
    echo "To use it:"
    echo "  1. Double-click to open"
    echo "  2. Or drag to Applications folder"
    echo ""
    echo "To install:"
    echo "  cp -r 'dist/Health AI Assistant.app' /Applications/"
    echo ""
    
    # Create a README
    cat > dist/README.txt << EOF
Health AI Assistant
===================

Installation:
1. Drag "Health AI Assistant.app" to your Applications folder
2. Double-click to launch
3. On first launch, enter your OpenAI API key
4. Complete the health survey
5. Start chatting!

Your data is stored in:
~/Library/Application Support/Health AI Assistant/

To uninstall:
1. Delete the app from Applications
2. Delete the data folder above (optional)
EOF
    
    echo "A README.txt has been created in the dist folder."
    echo ""
else
    echo ""
    echo "❌ Build failed. Please check the error messages above."
    echo ""
    exit 1
fi

