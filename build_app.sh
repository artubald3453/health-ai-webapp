#!/bin/bash

# Build script for Health AI Assistant
# This script compiles the Python app into a standalone executable

echo "================================================"
echo "  Health AI Assistant - Build Script"
echo "================================================"
echo ""

# Find pyinstaller (may be in user's local bin)
if command -v pyinstaller &> /dev/null; then
    PYINSTALLER="pyinstaller"
elif [ -f "$HOME/Library/Python/3.13/bin/pyinstaller" ]; then
    PYINSTALLER="$HOME/Library/Python/3.13/bin/pyinstaller"
elif [ -f "$HOME/Library/Python/3.12/bin/pyinstaller" ]; then
    PYINSTALLER="$HOME/Library/Python/3.12/bin/pyinstaller"
elif [ -f "$HOME/Library/Python/3.11/bin/pyinstaller" ]; then
    PYINSTALLER="$HOME/Library/Python/3.11/bin/pyinstaller"
else
    echo "❌ PyInstaller is not installed."
    echo "Installing PyInstaller..."
    pip3 install --user --break-system-packages pyinstaller
    PYINSTALLER="$HOME/Library/Python/3.13/bin/pyinstaller"
fi

echo "✓ PyInstaller is ready"
echo ""

# Detect OS
OS="$(uname -s)"
case "${OS}" in
    Linux*)     MACHINE=Linux;;
    Darwin*)    MACHINE=Mac;;
    CYGWIN*)    MACHINE=Windows;;
    MINGW*)     MACHINE=Windows;;
    *)          MACHINE="UNKNOWN:${OS}"
esac

echo "Detected OS: ${MACHINE}"
echo ""

# Clean previous builds
if [ -d "dist" ]; then
    echo "Cleaning previous builds..."
    rm -rf dist build *.spec
    echo "✓ Cleaned"
    echo ""
fi

# Build the app
echo "Building application..."
echo ""

if [ "$MACHINE" = "Mac" ]; then
    # macOS build
    $PYINSTALLER --name="Health AI Assistant" \
        --windowed \
        --onefile \
        --add-data "*.pdf:." \
        --hidden-import=PIL._tkinter_finder \
        --hidden-import=customtkinter \
        --hidden-import=openai \
        --hidden-import=PyPDF2 \
        --noconfirm \
        health_chatbot_gui.py
elif [ "$MACHINE" = "Linux" ]; then
    # Linux build
    $PYINSTALLER --name="Health AI Assistant" \
        --windowed \
        --onefile \
        --add-data "*.pdf:." \
        --hidden-import=PIL._tkinter_finder \
        --hidden-import=customtkinter \
        --hidden-import=openai \
        --hidden-import=PyPDF2 \
        --noconfirm \
        health_chatbot_gui.py
else
    echo "❌ Unsupported OS for this script. Please run PyInstaller manually."
    echo "See BUILD_APP_INSTRUCTIONS.md for details."
    exit 1
fi

# Check if build was successful
if [ $? -eq 0 ]; then
    echo ""
    echo "================================================"
    echo "  ✓ Build Successful!"
    echo "================================================"
    echo ""
    echo "Your app is ready at:"
    echo "  📦 dist/Health AI Assistant"
    echo ""
    echo "You can now run it directly or move it to your Applications folder."
    echo ""
    
    # Create a README in dist folder
    cat > dist/README.txt << EOF
Health AI Assistant
===================

To use this app:
1. Run the "Health AI Assistant" executable
2. On first launch, you'll be asked to enter your OpenAI API key
3. Complete the health survey
4. Start chatting with your AI health assistant!

Your data is stored in the 'user_data' folder next to this application.

For more information, see BUILD_APP_INSTRUCTIONS.md in the source folder.
EOF
    
    echo "A README.txt has been created in the dist folder."
    echo ""
else
    echo ""
    echo "❌ Build failed. Please check the error messages above."
    echo ""
    exit 1
fi

