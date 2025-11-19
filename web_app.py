"""
Health AI Assistant - Web Application
A mobile-friendly web version accessible from any device
"""

from flask import Flask, render_template, request, jsonify, session, redirect, url_for, send_file
from flask_session import Session
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.utils import secure_filename
import os
from pathlib import Path
from datetime import datetime
import json
from openai import OpenAI
import secrets
import database as db
from PyPDF2 import PdfReader

app = Flask(__name__)
# Use environment variable for production, random for development
app.secret_key = os.environ.get('SECRET_KEY', secrets.token_hex(16))

# Data directory
BASE_DIR = Path(__file__).parent
USER_DATA_DIR = BASE_DIR / "user_data_web"
USER_DATA_DIR.mkdir(exist_ok=True)
CHATS_DIR = USER_DATA_DIR / "chats"
CHATS_DIR.mkdir(exist_ok=True)
PDFS_DIR = USER_DATA_DIR / "user_pdfs"
PDFS_DIR.mkdir(exist_ok=True)

# File upload configuration
ALLOWED_EXTENSIONS = {'pdf'}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_user_pdf_dir(user_id):
    """Get or create user's PDF directory"""
    user_dir = PDFS_DIR / str(user_id)
    user_dir.mkdir(exist_ok=True)
    return user_dir

# Configure server-side sessions (inside user_data_web)
SESSION_DIR = USER_DATA_DIR / 'sessions'
SESSION_DIR.mkdir(exist_ok=True)
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_FILE_DIR'] = SESSION_DIR
app.config['SESSION_PERMANENT'] = True
app.config['SESSION_USE_SIGNER'] = True
app.config['PERMANENT_SESSION_LIFETIME'] = 86400  # 24 hours
app.config['REMEMBER_COOKIE_DURATION'] = 86400  # 24 hours
app.config['SESSION_COOKIE_SECURE'] = True  # HTTPS only
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
Session(app)

# Configure Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.session_protection = "strong"

# Initialize database
db.init_db()

class User(UserMixin):
    def __init__(self, id, email, api_key=None, profile=None):
        self.id = id
        self.email = email
        self.api_key = api_key
        self.profile = profile


@login_manager.user_loader
def load_user(user_id):
    user_data = db.get_user(user_id)
    if user_data:
        return User(
            id=user_data['id'],
            email=user_data['email'],
            api_key=user_data['api_key'],
            profile=user_data['profile']
        )
    return None

# Prompt ID from your saved prompt
PROMPT_ID = "pmpt_691a13bdf574819486553f3f13926e8606a7ec11e234cf1f"
PROMPT_VERSION = "1"


@app.route('/')
def index():
    """Landing page"""
    if current_user.is_authenticated:
        return redirect(url_for('chat'))
    return render_template('index.html')


@app.route('/login')
def login():
    """Login page"""
    if current_user.is_authenticated:
        return redirect(url_for('chat'))
    return render_template('login.html')


@app.route('/signup')
def signup():
    """Signup page"""
    if current_user.is_authenticated:
        return redirect(url_for('chat'))
    return render_template('signup.html')


@app.route('/api/signup', methods=['POST'])
def api_signup():
    """Handle user signup"""
    data = request.json
    email = data.get('email', '').strip().lower()
    password = data.get('password', '')
    
    if not email or not password:
        return jsonify({'success': False, 'error': 'Email and password required'})
    
    if len(password) < 8:
        return jsonify({'success': False, 'error': 'Password must be at least 8 characters'})
    
    user_id = db.create_user(email, password)
    
    if not user_id:
        return jsonify({'success': False, 'error': 'Email already registered'})
    
    # Auto-login after signup
    user_data = db.get_user(user_id)
    user = User(
        id=user_data['id'],
        email=user_data['email'],
        api_key=user_data['api_key'],
        profile=user_data['profile']
    )
    login_user(user, remember=True)
    session.permanent = True
    
    return jsonify({'success': True})


@app.route('/api/login', methods=['POST'])
def api_login():
    """Handle user login"""
    data = request.json
    email = data.get('email', '').strip().lower()
    password = data.get('password', '')
    
    if not email or not password:
        return jsonify({'success': False, 'error': 'Email and password required'})
    
    user_id = db.verify_user(email, password)
    
    if not user_id:
        return jsonify({'success': False, 'error': 'Invalid email or password'})
    
    user_data = db.get_user(user_id)
    user = User(
        id=user_data['id'],
        email=user_data['email'],
        api_key=user_data['api_key'],
        profile=user_data['profile']
    )
    login_user(user, remember=True)
    session.permanent = True
    
    return jsonify({'success': True})


@app.route('/setup')
@login_required
def setup():
    """API key setup page"""
    if current_user.api_key:
        return redirect(url_for('survey'))
    return render_template('setup.html')


@app.route('/api/save-key', methods=['POST'])
@login_required
def save_api_key():
    """Save API key to user account"""
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
        
        # Save to database
        db.update_api_key(current_user.id, api_key)
        current_user.api_key = api_key
        
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': f'Invalid API key: {str(e)}'})


@app.route('/survey')
@login_required
def survey():
    """Health survey page"""
    if not current_user.api_key:
        return redirect(url_for('setup'))
    
    if current_user.profile:
        return redirect(url_for('chat'))
    
    return render_template('survey.html')


@app.route('/api/save-profile', methods=['POST'])
@login_required
def save_profile():
    """Save user health profile"""
    if not current_user.api_key:
        return jsonify({'success': False, 'error': 'No API key'})
    
    data = request.json
    
    # Save profile to database
    profile = {
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
    
    db.update_profile(current_user.id, profile)
    current_user.profile = profile
    
    # Initialize first chat
    session['current_chat_id'] = datetime.now().strftime("%Y%m%d_%H%M%S")
    session['chat_history'] = []
    
    return jsonify({'success': True})


@app.route('/chat')
@login_required
def chat():
    """Main chat interface"""
    if not current_user.api_key:
        return redirect(url_for('setup'))
    
    if not current_user.profile:
        return redirect(url_for('survey'))
    
    # Initialize chat if needed
    if 'current_chat_id' not in session:
        session['current_chat_id'] = datetime.now().strftime("%Y%m%d_%H%M%S")
        session['chat_history'] = []
    
    return render_template('chat.html', profile=current_user.profile)


@app.route('/api/chat', methods=['POST'])
@login_required
def chat_api():
    """Handle chat messages"""
    if not current_user.api_key:
        return jsonify({'success': False, 'error': 'No API key'})
    
    data = request.json
    user_message = data.get('message', '').strip()
    
    if not user_message:
        return jsonify({'success': False, 'error': 'Empty message'})
    
    try:
        # Build context from user profile
        profile = current_user.profile or {}
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
        
        # Add user's uploaded PDFs to context
        pdfs_context = get_user_pdfs_context(current_user.id)
        context += pdfs_context
        
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
        client = OpenAI(api_key=current_user.api_key)
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
        
        # Save chat to database
        save_chat_to_db(session, current_user.id)
        
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
@login_required
def get_profile():
    """Get user profile"""
    return jsonify({
        'success': True,
        'profile': current_user.profile or {}
    })


@app.route('/api/get-messages')
@login_required
def get_messages():
    """Get current chat messages"""
    return jsonify({
        'success': True,
        'messages': session.get('chat_history', [])
    })


def save_chat_to_db(session_obj, user_id):
    """Save current chat to database"""
    if not session_obj.get('current_chat_id') or not session_obj.get('chat_history'):
        return
    
    chat_id = session_obj['current_chat_id']
    
    # Generate title from first user message
    title = "New Chat"
    for msg in session_obj['chat_history']:
        if msg['role'] == 'user':
            title = msg['content'][:50]
            if len(msg['content']) > 50:
                title += "..."
            break
    
    db.save_chat(user_id, chat_id, title, session_obj['chat_history'])


@app.route('/api/new-chat', methods=['POST'])
@login_required
def new_chat():
    """Start a new chat"""
    # Save current chat before starting new one
    if session.get('chat_history'):
        save_chat_to_db(session, current_user.id)
    
    # Create new chat
    session['current_chat_id'] = datetime.now().strftime("%Y%m%d_%H%M%S")
    session['chat_history'] = []
    session.modified = True
    
    return jsonify({'success': True})


@app.route('/api/chat-history')
@login_required
def get_chat_history():
    """Get list of saved chats"""
    chats = db.get_user_chats(current_user.id)
    return jsonify({'success': True, 'chats': chats})


@app.route('/api/load-chat/<chat_id>')
@login_required
def load_chat(chat_id):
    """Load a specific chat"""
    chat_data = db.get_chat(chat_id, current_user.id)
    
    if not chat_data:
        return jsonify({'success': False, 'error': 'Chat not found'})
    
    # Load into session
    session['current_chat_id'] = chat_data['id']
    session['chat_history'] = chat_data['messages']
    session.modified = True
    
    return jsonify({'success': True, 'chat': chat_data})


@app.route('/api/clear-chat', methods=['POST'])
@login_required
def clear_chat():
    """Clear chat history"""
    # Save current chat before clearing
    if session.get('chat_history'):
        save_chat_to_db(session, current_user.id)
    
    # Start new chat
    session['current_chat_id'] = datetime.now().strftime("%Y%m%d_%H%M%S")
    session['chat_history'] = []
    session.modified = True
    return jsonify({'success': True})


@app.route('/logout')
@login_required
def logout_route():
    """Logout user"""
    logout_user()
    session.clear()
    return redirect(url_for('index'))


def extract_text_from_pdf(pdf_path):
    """Extract text from PDF file"""
    try:
        reader = PdfReader(pdf_path)
        text = ""
        for page in reader.pages:
            text += page.extract_text() + "\n"
        return text
    except Exception as e:
        return f"Error reading PDF: {str(e)}"


@app.route('/api/upload-pdf', methods=['POST'])
@login_required
def upload_pdf():
    """Upload a PDF file"""
    if 'file' not in request.files:
        return jsonify({'success': False, 'error': 'No file provided'})
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({'success': False, 'error': 'No file selected'})
    
    if not allowed_file(file.filename):
        return jsonify({'success': False, 'error': 'Only PDF files are allowed'})
    
    try:
        # Check file size
        file.seek(0, os.SEEK_END)
        file_size = file.tell()
        file.seek(0)
        
        if file_size > MAX_FILE_SIZE:
            return jsonify({'success': False, 'error': 'File too large (max 10MB)'})
        
        # Save file
        filename = secure_filename(file.filename)
        user_pdf_dir = get_user_pdf_dir(current_user.id)
        
        # Add timestamp to filename to avoid conflicts
        name, ext = os.path.splitext(filename)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        unique_filename = f"{name}_{timestamp}{ext}"
        
        filepath = user_pdf_dir / unique_filename
        file.save(filepath)
        
        # Extract text for preview
        text = extract_text_from_pdf(filepath)
        preview = text[:200] + "..." if len(text) > 200 else text
        
        return jsonify({
            'success': True,
            'filename': unique_filename,
            'original_name': file.filename,
            'preview': preview
        })
    
    except Exception as e:
        return jsonify({'success': False, 'error': f'Upload failed: {str(e)}'})


@app.route('/api/list-pdfs')
@login_required
def list_pdfs():
    """List user's uploaded PDFs"""
    try:
        user_pdf_dir = get_user_pdf_dir(current_user.id)
        pdfs = []
        
        for pdf_file in user_pdf_dir.glob("*.pdf"):
            pdfs.append({
                'filename': pdf_file.name,
                'size': pdf_file.stat().st_size,
                'uploaded': datetime.fromtimestamp(pdf_file.stat().st_mtime).isoformat()
            })
        
        # Sort by upload date (newest first)
        pdfs.sort(key=lambda x: x['uploaded'], reverse=True)
        
        return jsonify({'success': True, 'pdfs': pdfs})
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


@app.route('/api/delete-pdf/<filename>', methods=['DELETE'])
@login_required
def delete_pdf(filename):
    """Delete a PDF file"""
    try:
        # Security: ensure filename is safe
        safe_filename = secure_filename(filename)
        user_pdf_dir = get_user_pdf_dir(current_user.id)
        filepath = user_pdf_dir / safe_filename
        
        if not filepath.exists():
            return jsonify({'success': False, 'error': 'File not found'})
        
        filepath.unlink()
        return jsonify({'success': True})
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


def get_user_pdfs_context(user_id):
    """Get text content from all user's PDFs for AI context"""
    try:
        user_pdf_dir = get_user_pdf_dir(user_id)
        context = "\n\nUSER'S UPLOADED HEALTH DOCUMENTS:\n\n"
        
        pdf_files = list(user_pdf_dir.glob("*.pdf"))
        
        if not pdf_files:
            return ""
        
        for pdf_file in pdf_files:
            context += f"\n--- Document: {pdf_file.name} ---\n"
            text = extract_text_from_pdf(pdf_file)
            # Limit to first 2000 chars per PDF to avoid context overflow
            context += text[:2000]
            if len(text) > 2000:
                context += "\n[...document continues...]"
            context += "\n\n"
        
        return context
    
    except Exception as e:
        return f"\nError loading documents: {str(e)}\n"


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

