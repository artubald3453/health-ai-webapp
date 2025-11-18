#!/bin/bash

# Health AI Chatbot Launcher Script

echo "🏥 Health AI Chatbot - Starting..."
echo ""

# Check if virtual environment exists
if [ ! -d "venv_chatbot" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv_chatbot
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv_chatbot/bin/activate

# Install requirements if needed
if ! python -c "import customtkinter" 2>/dev/null; then
    echo "Installing dependencies..."
    pip install -r requirements_chatbot.txt
fi

# Check if API key is set in environment
if [ -z "$OPENAI_API_KEY" ]; then
    echo ""
    echo "⚠️  WARNING: OPENAI_API_KEY environment variable not set!"
    echo "Set it with: export OPENAI_API_KEY='your-api-key'"
    echo ""
    read -p "Press Enter to continue anyway, or Ctrl+C to exit..."
fi

# Run the application
echo ""
echo "🚀 Launching Health AI Chatbot..."
python health_chatbot_gui.py

# Deactivate on exit
deactivate

