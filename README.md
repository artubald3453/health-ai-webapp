# 🏥 Health AI Assistant

A beautiful, personalized AI health chatbot with an intuitive setup wizard.

## ✨ Features

- **🔑 API Key Setup Wizard**: First-time users guided through API key setup
- **📊 Three-Step Onboarding**: API Key → Health Survey → Chat Interface
- **🔒 Secure Storage**: API keys stored locally with encoding
- **💬 Personalized Chat**: AI knows your health profile
- **📄 PDF Upload**: Upload medical documents
- **💾 Chat History**: All conversations saved

## 🚀 Quick Start

### Run from Source
```bash
cd filesforhealthbot
pip install -r requirements_chatbot.txt
python3 health_chatbot_gui.py
```

### Build Standalone App

**Quick executable:**
```bash
./build_app.sh
```

**Proper macOS .app bundle:**
```bash
./build_macos_app.sh
```

This creates `dist/Health AI Assistant.app` that you can drag to Applications!

## 🎨 Adding a Custom Icon

**Quick method:**
1. Create a 1024x1024 PNG (use ChatGPT, Canva, or Figma)
2. Convert at https://cloudconvert.com/png-to-icns
3. Save as `app_icon.icns` in project folder
4. Run `./build_macos_app.sh` (automatically uses icon!)

**Or use terminal:**
```bash
./create_icon.sh your_icon.png
```

See **`QUICK_REFERENCE.md`** for detailed steps!

## 📱 App Store Distribution

Want to publish to the Mac App Store?

See **`APP_STORE_GUIDE.md`** for complete instructions on:
- Creating professional icons
- Apple Developer account setup
- Code signing and notarization
- App Store submission process
- Alternative distribution methods

## 🎯 First-Time Setup

1. Launch the app
2. Enter your OpenAI API key (get one at platform.openai.com/api-keys)
3. Complete the health survey
4. Start chatting!

## 📁 File Structure

```
filesforhealthbot/
├── health_chatbot_gui.py        # Main application
├── requirements_chatbot.txt     # Dependencies
├── build_app.sh                 # Build script
├── user_data/                   # Created at runtime
│   ├── .api_key                # Your API key
│   ├── user_profile.json       # Your health profile
│   └── chats/                  # Saved conversations
└── *.pdf                       # Health reference books
```

## ⚠️ Disclaimer

This AI assistant is for informational purposes only and is not a substitute for professional medical advice.
