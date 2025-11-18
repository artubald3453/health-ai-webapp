"""
Health AI Assistant - Web Application
A mobile-friendly web version accessible from any device
"""

from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from flask_session import Session
import os
from pathlib import Path
from datetime import datetime
import json
from openai import OpenAI
import secrets

app = Flask(__name__)
# Use environment variable for production, random for development
app.secret_key = os.environ.get('SECRET_KEY', secrets.token_hex(16))

# Configure server-side sessions
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_FILE_DIR'] = Path(__file__).parent / 'flask_sessions'
app.config['SESSION_FILE_DIR'].mkdir(exist_ok=True)
Session(app)

# Data directory
BASE_DIR = Path(__file__).parent
USER_DATA_DIR = BASE_DIR / "user_data_web"
USER_DATA_DIR.mkdir(exist_ok=True)

# Prompt ID from your saved prompt
PROMPT_ID = "pmpt_691a13bdf574819486553f3f13926e8606a7ec11e234cf1f"
PROMPT_VERSION = "1"


@app.route('/')
def index():
    """Landing page"""
    return render_template('index.html')


@app.route('/setup')
def setup():
    """API key setup page"""
    if session.get('api_key'):
        return redirect(url_for('survey'))
    return render_template('setup.html')


@app.route('/api/save-key', methods=['POST'])
def save_api_key():
    """Save API key to session"""
    data = request.json
    api_key = data.get('api_key', '').strip()
    
    if not api_key:
        return jsonify({'success': False, 'error': 'API key is required'})
    
    if not api_key.startswith('sk-'):
        return jsonify({'success': False, 'error': 'Invalid API key format'})
    
    # Test the API key
    try:
        client = OpenAI(api_key=api_key)
        # Quick test call
        client.models.list()
        
        # Save to session
        session['api_key'] = api_key
        session['setup_complete'] = False
        
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': f'Invalid API key: {str(e)}'})


@app.route('/survey')
def survey():
    """Health survey page"""
    if not session.get('api_key'):
        return redirect(url_for('setup'))
    
    if session.get('setup_complete'):
        return redirect(url_for('chat'))
    
    return render_template('survey.html')


@app.route('/api/save-profile', methods=['POST'])
def save_profile():
    """Save user health profile"""
    if not session.get('api_key'):
        return jsonify({'success': False, 'error': 'No API key'})
    
    data = request.json
    
    # Save profile to session
    session['profile'] = {
        'height': data.get('height'),
        'weight': data.get('weight'),
        'age': data.get('age'),
        'gender': data.get('gender'),
        'sex': data.get('sex'),
        'vitamins': data.get('vitamins'),
        'medications': data.get('medications'),
        'injuries': data.get('injuries'),
        'abnormalities': data.get('abnormalities'),
        'goals': data.get('goals'),
        'other': data.get('other'),
        'created_at': datetime.now().isoformat()
    }
    
    session['setup_complete'] = True
    session['chat_history'] = []
    
    return jsonify({'success': True})


@app.route('/chat')
def chat():
    """Main chat interface"""
    if not session.get('api_key'):
        return redirect(url_for('setup'))
    
    if not session.get('setup_complete'):
        return redirect(url_for('survey'))
    
    return render_template('chat.html', profile=session.get('profile'))


@app.route('/api/chat', methods=['POST'])
def chat_api():
    """Handle chat messages"""
    if not session.get('api_key'):
        return jsonify({'success': False, 'error': 'Not authenticated'})
    
    data = request.json
    user_message = data.get('message', '').strip()
    
    if not user_message:
        return jsonify({'success': False, 'error': 'Empty message'})
    
    try:
        # Build context from user profile
        profile = session.get('profile', {})
        context = "USER HEALTH INFORMATION:\n\n"
        
        for key, value in profile.items():
            if key != 'created_at' and value:
                context += f"{key.replace('_', ' ').title()}: {value}\n"
        
        context += "\n\nAVAILABLE HEALTH REFERENCE MATERIALS:\n"
        context += "- How Not to Die (Michael Greger)\n"
        context += "- Lifespan: Why We Age and Why We Don't Have To\n"
        context += "- Outlive: The Science and Art of Longevity\n"
        context += "- The China Study\n"
        context += "- The Longevity Paradox\n"
        context += "- Blue Zones Study Guide\n"
        
        # Build full message with context
        full_message = f"{context}\n\nUser Question: {user_message}"
        
        # Add chat history
        chat_history = session.get('chat_history', [])
        if chat_history:
            history_text = "\n\nRecent Conversation:\n"
            for msg in chat_history[-10:]:
                role = "User" if msg["role"] == "user" else "Assistant"
                history_text += f"{role}: {msg['content']}\n"
            full_message = history_text + "\n" + full_message
        
        # Call OpenAI API
        client = OpenAI(api_key=session['api_key'])
        response = client.responses.create(
            prompt={
                "id": PROMPT_ID,
                "version": PROMPT_VERSION
            },
            input=full_message
        )
        
        # Extract AI response
        ai_message = None
        if hasattr(response, 'output'):
            output = response.output
            if isinstance(output, list):
                for item in output:
                    if hasattr(item, 'type') and item.type == 'message':
                        message = item
                    elif hasattr(item, 'content') and not hasattr(item, 'type'):
                        message = item
                    else:
                        continue
                    
                    if hasattr(message, 'content') and isinstance(message.content, list):
                        if len(message.content) > 0:
                            content_item = message.content[0]
                            if hasattr(content_item, 'text'):
                                ai_message = content_item.text
                                break
        
        if ai_message is None:
            ai_message = "I received your message but had trouble generating a response. Please try again."
        
        # Update chat history
        if 'chat_history' not in session:
            session['chat_history'] = []
        
        session['chat_history'].append({"role": "user", "content": user_message})
        session['chat_history'].append({"role": "assistant", "content": ai_message})
        
        # Keep only last 50 messages
        if len(session['chat_history']) > 50:
            session['chat_history'] = session['chat_history'][-50:]
        
        session.modified = True
        
        return jsonify({
            'success': True,
            'message': ai_message
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Error: {str(e)}'
        })


@app.route('/api/profile')
def get_profile():
    """Get user profile"""
    if not session.get('api_key'):
        return jsonify({'success': False, 'error': 'Not authenticated'})
    
    return jsonify({
        'success': True,
        'profile': session.get('profile', {})
    })


@app.route('/api/clear-chat', methods=['POST'])
def clear_chat():
    """Clear chat history"""
    session['chat_history'] = []
    session.modified = True
    return jsonify({'success': True})


@app.route('/logout')
def logout():
    """Clear session and logout"""
    session.clear()
    return redirect(url_for('index'))


if __name__ == '__main__':
    print("\n" + "="*50)
    print("🏥 Health AI Assistant - Web Server")
    print("="*50)
    print("\nServer starting...")
    print("Access at: http://localhost:5000")
    print("Or from your phone: http://YOUR_COMPUTER_IP:5000")
    print("\nPress Ctrl+C to stop")
    print("="*50 + "\n")
    
    app.run(host='0.0.0.0', port=5000, debug=True)

