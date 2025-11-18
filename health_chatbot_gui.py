"""
Health AI Chatbot GUI with animated background
Features:
- User onboarding with health questions
- PDF upload for medical data
- AI chatbot with access to uploaded PDFs and health books
- Beautiful animated pink/blue cloud background
"""

import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog, messagebox
import json
import os
from datetime import datetime
import threading
import math
import random
from PIL import Image, ImageDraw, ImageTk
from openai import OpenAI
from pathlib import Path
import PyPDF2
import base64

# Prompt ID and version from your saved prompt
PROMPT_ID = "pmpt_691a13bdf574819486553f3f13926e8606a7ec11e234cf1f"
PROMPT_VERSION = "1"

# Paths
BASE_DIR = Path(__file__).parent
BOOKS_DIR = BASE_DIR  # Health books are in the same directory
USER_DATA_DIR = BASE_DIR / "user_data"
USER_DATA_DIR.mkdir(exist_ok=True)

# OpenAI client (initialized after API key is set)
client = None


class AnimatedBackground(tk.Canvas):
    """Animated background with flowing pink and blue clouds"""
    
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs, highlightthickness=0)
        self.width = kwargs.get('width', 800)
        self.height = kwargs.get('height', 600)
        
        # Cloud particles
        self.clouds = []
        self.init_clouds()
        
        # Animation
        self.animate()
    
    def init_clouds(self):
        """Initialize cloud particles"""
        num_clouds = 15
        for _ in range(num_clouds):
            cloud = {
                'x': random.uniform(0, self.width),
                'y': random.uniform(0, self.height),
                'radius': random.uniform(80, 150),
                'vx': random.uniform(-0.3, 0.3),
                'vy': random.uniform(-0.2, 0.2),
                'color': random.choice(['pink', 'blue']),
                'opacity': random.uniform(0.1, 0.3)
            }
            self.clouds.append(cloud)
    
    def animate(self):
        """Animate cloud movements"""
        self.delete("all")
        
        # Draw background
        self.create_rectangle(0, 0, self.width, self.height, 
                            fill='#F5F5F0', outline='')
        
        # Update and draw clouds
        for cloud in self.clouds:
            # Update position
            cloud['x'] += cloud['vx']
            cloud['y'] += cloud['vy']
            
            # Wrap around edges
            if cloud['x'] < -cloud['radius']:
                cloud['x'] = self.width + cloud['radius']
            elif cloud['x'] > self.width + cloud['radius']:
                cloud['x'] = -cloud['radius']
            
            if cloud['y'] < -cloud['radius']:
                cloud['y'] = self.height + cloud['radius']
            elif cloud['y'] > self.height + cloud['radius']:
                cloud['y'] = -cloud['radius']
            
            # Draw cloud with gradient effect
            color = '#FFB6C1' if cloud['color'] == 'pink' else '#ADD8E6'
            opacity = int(cloud['opacity'] * 255)
            
            # Create multiple circles for soft cloud effect
            for i in range(3):
                r = cloud['radius'] - i * 15
                alpha = opacity - i * 30
                if alpha < 0:
                    alpha = 0
                
                # Convert hex to RGB and add alpha
                rgb = tuple(int(color[i:i+2], 16) for i in (1, 3, 5))
                fill_color = f'#{rgb[0]:02x}{rgb[1]:02x}{rgb[2]:02x}'
                
                self.create_oval(
                    cloud['x'] - r, cloud['y'] - r,
                    cloud['x'] + r, cloud['y'] + r,
                    fill=fill_color, outline='', stipple='gray50'
                )
        
        # Continue animation
        self.after(50, self.animate)


class HealthChatbotApp:
    """Main application class"""
    
    def __init__(self):
        global client
        
        self.app = ctk.CTk()
        self.app.title("Health AI Assistant")
        self.app.geometry("1200x800")
        
        # Set theme
        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("blue")
        
        # User data
        self.user_profile = {}
        self.uploaded_pdfs = []
        self.chat_history = []
        self.current_chat_id = None
        
        # Create chats directory
        self.chats_dir = USER_DATA_DIR / "chats"
        self.chats_dir.mkdir(exist_ok=True)
        
        # API key path
        self.api_key_path = USER_DATA_DIR / ".api_key"
        
        # Load or create user profile
        self.profile_path = USER_DATA_DIR / "user_profile.json"
        self.load_user_profile()
        
        # Check setup flow: API Key -> Onboarding -> Chat
        if not self.has_api_key():
            self.show_api_key_setup()
        elif not self.user_profile:
            # Initialize client with stored API key
            self.initialize_openai_client()
            self.show_onboarding()
        else:
            # Initialize client with stored API key
            self.initialize_openai_client()
            self.show_chat_interface()
    
    def has_api_key(self):
        """Check if API key is stored"""
        return self.api_key_path.exists()
    
    def save_api_key(self, api_key):
        """Save API key (with basic encoding for obfuscation)"""
        # Basic encoding (not encryption, just obfuscation)
        encoded = base64.b64encode(api_key.encode()).decode()
        with open(self.api_key_path, 'w') as f:
            f.write(encoded)
    
    def load_api_key(self):
        """Load API key"""
        if not self.api_key_path.exists():
            return None
        with open(self.api_key_path, 'r') as f:
            encoded = f.read().strip()
            return base64.b64decode(encoded).decode()
    
    def initialize_openai_client(self):
        """Initialize OpenAI client with stored API key"""
        global client
        api_key = self.load_api_key()
        if api_key:
            client = OpenAI(api_key=api_key)
            return True
        return False
    
    def load_user_profile(self):
        """Load existing user profile"""
        if self.profile_path.exists():
            with open(self.profile_path, 'r') as f:
                self.user_profile = json.load(f)
    
    def save_user_profile(self):
        """Save user profile"""
        with open(self.profile_path, 'w') as f:
            json.dump(self.user_profile, f, indent=2)
    
    def show_api_key_setup(self):
        """Show API key setup wizard"""
        # Create animated background
        self.bg_canvas = AnimatedBackground(self.app, width=1200, height=800)
        self.bg_canvas.place(x=0, y=0, relwidth=1, relheight=1)
        
        # Create main frame
        main_frame = ctk.CTkFrame(self.app, width=700, height=600, 
                                 corner_radius=20, fg_color="white")
        main_frame.place(relx=0.5, rely=0.5, anchor="center")
        
        # Content frame
        content_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        content_frame.pack(pady=40, padx=40, fill="both", expand=True)
        
        # Welcome title
        title = ctk.CTkLabel(content_frame, 
                            text="🏥 Welcome to Health AI Assistant",
                            font=("Helvetica", 32, "bold"))
        title.pack(pady=(20, 10))
        
        subtitle = ctk.CTkLabel(content_frame,
                               text="Your Personal AI Health Companion",
                               font=("Helvetica", 18),
                               text_color="gray")
        subtitle.pack(pady=(0, 30))
        
        # Instructions
        instructions = ctk.CTkLabel(
            content_frame,
            text="To get started, you'll need an OpenAI API key.\n"
                 "This key allows the app to connect to OpenAI's AI services.\n\n"
                 "Your API key will be stored securely on your computer\n"
                 "and never shared with anyone.",
            font=("Helvetica", 14),
            justify="center"
        )
        instructions.pack(pady=(0, 20))
        
        # Steps frame
        steps_frame = ctk.CTkFrame(content_frame, corner_radius=15, fg_color="#F0F0F0")
        steps_frame.pack(fill="x", pady=20, padx=20)
        
        steps_title = ctk.CTkLabel(steps_frame,
                                   text="How to Get Your API Key:",
                                   font=("Helvetica", 16, "bold"))
        steps_title.pack(pady=(15, 10))
        
        steps_text = (
            "1. Visit: https://platform.openai.com/api-keys\n"
            "2. Sign in or create an OpenAI account\n"
            "3. Click 'Create new secret key'\n"
            "4. Copy your API key\n"
            "5. Paste it below"
        )
        steps_label = ctk.CTkLabel(steps_frame, text=steps_text,
                                  font=("Helvetica", 13),
                                  justify="left")
        steps_label.pack(pady=(0, 15), padx=20)
        
        # API Key input
        api_key_label = ctk.CTkLabel(content_frame,
                                     text="Enter Your OpenAI API Key:",
                                     font=("Helvetica", 15, "bold"))
        api_key_label.pack(pady=(20, 5))
        
        self.api_key_entry = ctk.CTkEntry(content_frame,
                                         width=500,
                                         height=45,
                                         corner_radius=10,
                                         font=("Helvetica", 13),
                                         placeholder_text="sk-...",
                                         show="*")
        self.api_key_entry.pack(pady=(5, 20))
        
        # Show/hide password toggle
        self.show_key_var = ctk.BooleanVar(value=False)
        show_key_check = ctk.CTkCheckBox(content_frame,
                                        text="Show API key",
                                        variable=self.show_key_var,
                                        command=self.toggle_api_key_visibility)
        show_key_check.pack(pady=(0, 20))
        
        # Continue button
        continue_btn = ctk.CTkButton(content_frame,
                                    text="Continue",
                                    height=50,
                                    corner_radius=25,
                                    font=("Helvetica", 18, "bold"),
                                    command=self.validate_and_save_api_key)
        continue_btn.pack(pady=10)
    
    def toggle_api_key_visibility(self):
        """Toggle API key visibility"""
        if self.show_key_var.get():
            self.api_key_entry.configure(show="")
        else:
            self.api_key_entry.configure(show="*")
    
    def validate_and_save_api_key(self):
        """Validate and save the API key"""
        api_key = self.api_key_entry.get().strip()
        
        if not api_key:
            messagebox.showerror("Error", "Please enter your API key")
            return
        
        if not api_key.startswith("sk-"):
            messagebox.showerror("Error", "Invalid API key format. OpenAI API keys start with 'sk-'")
            return
        
        # Save the API key
        self.save_api_key(api_key)
        
        # Initialize OpenAI client
        if not self.initialize_openai_client():
            messagebox.showerror("Error", "Failed to initialize OpenAI client")
            return
        
        # Test the API key
        messagebox.showinfo("Success", "API key saved successfully!\n\nNow let's set up your health profile.")
        
        # Clear window and show onboarding
        for widget in self.app.winfo_children():
            widget.destroy()
        
        self.show_onboarding()
    
    def create_new_chat(self):
        """Create a new chat session"""
        self.current_chat_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.chat_history = []
        
        # Clear chat display
        if hasattr(self, 'chat_display'):
            self.chat_display.configure(state="normal")
            self.chat_display.delete("1.0", "end")
            self.chat_display.configure(state="disabled")
            
            # Add welcome message
            self.add_message_to_chat(
                "AI Assistant",
                f"Hello! I'm your personal health AI assistant. I have access to your health profile "
                f"and can help you with personalized workout recommendations, diet planning, and health advice. "
                f"\n\nHow can I help you today?"
            )
    
    def save_current_chat(self):
        """Save current chat to file"""
        if not self.current_chat_id or not self.chat_history:
            return
        
        chat_data = {
            'id': self.current_chat_id,
            'created_at': self.current_chat_id,
            'messages': self.chat_history,
            'title': self.generate_chat_title()
        }
        
        chat_file = self.chats_dir / f"{self.current_chat_id}.json"
        with open(chat_file, 'w') as f:
            json.dump(chat_data, f, indent=2)
    
    def generate_chat_title(self):
        """Generate a title for the chat based on first user message"""
        for msg in self.chat_history:
            if msg['role'] == 'user':
                title = msg['content'][:50]
                if len(msg['content']) > 50:
                    title += "..."
                return title
        return "New Chat"
    
    def load_chat(self, chat_id):
        """Load a saved chat"""
        chat_file = self.chats_dir / f"{chat_id}.json"
        
        if not chat_file.exists():
            return
        
        with open(chat_file, 'r') as f:
            chat_data = json.load(f)
        
        self.current_chat_id = chat_data['id']
        self.chat_history = chat_data['messages']
        
        # Clear and reload chat display
        self.chat_display.configure(state="normal")
        self.chat_display.delete("1.0", "end")
        self.chat_display.configure(state="disabled")
        
        # Display all messages
        for msg in self.chat_history:
            if msg['role'] == 'user':
                self.add_message_to_chat("You", msg['content'])
            else:
                self.add_message_to_chat("AI Assistant", msg['content'])
    
    def get_saved_chats(self):
        """Get list of saved chats"""
        chats = []
        for chat_file in sorted(self.chats_dir.glob("*.json"), reverse=True):
            try:
                with open(chat_file, 'r') as f:
                    chat_data = json.load(f)
                    chats.append({
                        'id': chat_data['id'],
                        'title': chat_data.get('title', 'Untitled Chat'),
                        'created_at': chat_data['created_at']
                    })
            except:
                pass
        return chats
    
    def show_chat_history_window(self):
        """Show window with saved chats"""
        history_window = ctk.CTkToplevel(self.app)
        history_window.title("Chat History")
        history_window.geometry("500x600")
        
        # Title
        ctk.CTkLabel(history_window, text="Your Previous Chats",
                    font=("Helvetica", 24, "bold")).pack(pady=20)
        
        # Scrollable frame for chats
        scroll = ctk.CTkScrollableFrame(history_window, width=460, height=500)
        scroll.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        # Get saved chats
        saved_chats = self.get_saved_chats()
        
        if not saved_chats:
            ctk.CTkLabel(scroll, text="No saved chats yet",
                        font=("Helvetica", 14)).pack(pady=20)
        else:
            for chat in saved_chats:
                chat_frame = ctk.CTkFrame(scroll, corner_radius=10)
                chat_frame.pack(fill="x", pady=5, padx=10)
                
                # Chat info
                title_label = ctk.CTkLabel(chat_frame, text=chat['title'],
                                          font=("Helvetica", 14, "bold"),
                                          anchor="w")
                title_label.pack(anchor="w", padx=10, pady=(10, 0))
                
                date_str = datetime.strptime(chat['created_at'], "%Y%m%d_%H%M%S").strftime("%B %d, %Y at %I:%M %p")
                date_label = ctk.CTkLabel(chat_frame, text=date_str,
                                         font=("Helvetica", 11),
                                         text_color="gray")
                date_label.pack(anchor="w", padx=10, pady=(0, 5))
                
                # Load button
                load_btn = ctk.CTkButton(chat_frame, text="Load Chat",
                                        command=lambda cid=chat['id']: [
                                            self.load_chat(cid),
                                            history_window.destroy()
                                        ],
                                        corner_radius=8, height=30)
                load_btn.pack(pady=(0, 10), padx=10)
    
    def show_onboarding(self):
        """Show onboarding screen with health questions"""
        # Create animated background
        self.bg_canvas = AnimatedBackground(self.app, width=1200, height=800)
        self.bg_canvas.place(x=0, y=0, relwidth=1, relheight=1)
        
        # Create main frame
        main_frame = ctk.CTkFrame(self.app, width=600, height=700, 
                                 corner_radius=20, fg_color="white")
        main_frame.place(relx=0.5, rely=0.5, anchor="center")
        
        # Scrollable frame for questions
        scroll = ctk.CTkScrollableFrame(main_frame, width=550, height=620,
                                       corner_radius=15)
        scroll.pack(pady=20, padx=20, fill="both", expand=True)
        
        # Title
        title = ctk.CTkLabel(scroll, text="Welcome to Your Health AI Assistant",
                           font=("Helvetica", 28, "bold"))
        title.pack(pady=20)
        
        subtitle = ctk.CTkLabel(scroll, 
                              text="Please provide some information to personalize your experience",
                              font=("Helvetica", 14))
        subtitle.pack(pady=(0, 20))
        
        # Question fields
        self.onboarding_fields = {}
        
        # Height
        self.add_spinbox(scroll, "Height (inches)", 36, 96, "height")
        
        # Weight
        self.add_spinbox(scroll, "Weight (lbs)", 50, 500, "weight")
        
        # Age
        self.add_spinbox(scroll, "Age", 5, 120, "age")
        
        # Gender
        self.add_radio_group(scroll, "Gender", ["Male", "Female", "Other"], "gender")
        
        # Sex
        self.add_radio_group(scroll, "Sex", ["Male", "Female", "Other"], "sex")
        
        # Text fields
        self.add_textbox(scroll, "Vitamins / Supplements", "vitamins")
        self.add_textbox(scroll, "Medications", "medications")
        self.add_textbox(scroll, "Medical Injuries", "injuries")
        self.add_textbox(scroll, "Medical Abnormalities", "abnormalities")
        self.add_textbox(scroll, "Health & Fitness Goals", "goals")
        self.add_textbox(scroll, "Anything else we should know?", "other")
        
        # Submit button
        submit_btn = ctk.CTkButton(scroll, text="Start Your Health Journey",
                                  height=50, corner_radius=25,
                                  font=("Helvetica", 18, "bold"),
                                  command=self.complete_onboarding)
        submit_btn.pack(pady=30)
    
    def add_spinbox(self, parent, label, start, end, key):
        """Add a spinbox field"""
        ctk.CTkLabel(parent, text=label, font=("Helvetica", 15, "bold")).pack(anchor="w", pady=(15, 5), padx=20)
        combo = ctk.CTkComboBox(parent, width=150, height=35, corner_radius=12,
                               values=[str(i) for i in range(start, end + 1)])
        combo.pack(anchor="w", padx=20)
        self.onboarding_fields[key] = combo
    
    def add_radio_group(self, parent, label, options, key):
        """Add a radio button group"""
        ctk.CTkLabel(parent, text=label, font=("Helvetica", 15, "bold")).pack(anchor="w", pady=(15, 5), padx=20)
        
        var = ctk.StringVar(value=options[0])
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.pack(anchor="w", padx=20, pady=5)
        
        for option in options:
            ctk.CTkRadioButton(frame, text=option, value=option, 
                             variable=var).pack(side="left", padx=10)
        
        self.onboarding_fields[key] = var
    
    def add_textbox(self, parent, label, key):
        """Add a textbox field"""
        ctk.CTkLabel(parent, text=label, font=("Helvetica", 15, "bold")).pack(anchor="w", pady=(15, 5), padx=20)
        textbox = ctk.CTkTextbox(parent, width=520, height=80, corner_radius=12)
        textbox.pack(padx=20, pady=5)
        self.onboarding_fields[key] = textbox
    
    def complete_onboarding(self):
        """Complete onboarding and save profile"""
        # Collect data
        self.user_profile = {
            'height': self.onboarding_fields['height'].get(),
            'weight': self.onboarding_fields['weight'].get(),
            'age': self.onboarding_fields['age'].get(),
            'gender': self.onboarding_fields['gender'].get(),
            'sex': self.onboarding_fields['sex'].get(),
            'vitamins': self.onboarding_fields['vitamins'].get("0.0", "end").strip(),
            'medications': self.onboarding_fields['medications'].get("0.0", "end").strip(),
            'injuries': self.onboarding_fields['injuries'].get("0.0", "end").strip(),
            'abnormalities': self.onboarding_fields['abnormalities'].get("0.0", "end").strip(),
            'goals': self.onboarding_fields['goals'].get("0.0", "end").strip(),
            'other': self.onboarding_fields['other'].get("0.0", "end").strip(),
            'created_at': datetime.now().isoformat()
        }
        
        self.save_user_profile()
        
        # Clear window and show chat interface
        for widget in self.app.winfo_children():
            widget.destroy()
        
        self.show_chat_interface()
    
    def show_chat_interface(self):
        """Show main chat interface"""
        # Create animated background
        self.bg_canvas = AnimatedBackground(self.app, width=1200, height=800)
        self.bg_canvas.place(x=0, y=0, relwidth=1, relheight=1)
        
        # Main container
        main_container = ctk.CTkFrame(self.app, fg_color="transparent")
        main_container.place(relx=0.5, rely=0.5, anchor="center", 
                           relwidth=0.9, relheight=0.9)
        
        # Top bar with controls
        top_bar = ctk.CTkFrame(main_container, height=60, corner_radius=15,
                             fg_color="white")
        top_bar.pack(fill="x", pady=(0, 10))
        
        # Title
        title = ctk.CTkLabel(top_bar, text="🏥 Health AI Assistant",
                           font=("Helvetica", 24, "bold"))
        title.pack(side="left", padx=20)
        
        # Chat History button
        history_btn = ctk.CTkButton(top_bar, text="💬 Chat History",
                                   command=self.show_chat_history_window,
                                   corner_radius=10, height=40)
        history_btn.pack(side="right", padx=10, pady=10)
        
        # New Chat button
        new_chat_btn = ctk.CTkButton(top_bar, text="➕ New Chat",
                                    command=self.create_new_chat,
                                    corner_radius=10, height=40)
        new_chat_btn.pack(side="right", padx=10, pady=10)
        
        # Upload PDF button
        upload_btn = ctk.CTkButton(top_bar, text="📄 Upload PDF",
                                  command=self.upload_pdf,
                                  corner_radius=10, height=40)
        upload_btn.pack(side="right", padx=10, pady=10)
        
        # View Profile button
        profile_btn = ctk.CTkButton(top_bar, text="👤 Profile",
                                   command=self.show_profile,
                                   corner_radius=10, height=40)
        profile_btn.pack(side="right", padx=10, pady=10)
        
        # Chat area
        chat_frame = ctk.CTkFrame(main_container, corner_radius=20,
                                 fg_color="white")
        chat_frame.pack(fill="both", expand=True, pady=(0, 10))
        
        # Chat display
        self.chat_display = ctk.CTkTextbox(chat_frame, corner_radius=15,
                                          font=("Helvetica", 14),
                                          wrap="word")
        self.chat_display.pack(fill="both", expand=True, padx=20, pady=20)
        self.chat_display.configure(state="disabled")
        
        # Input area
        input_frame = ctk.CTkFrame(main_container, height=80, corner_radius=25,
                                  fg_color="white")
        input_frame.pack(fill="x")
        
        # Message input
        self.message_input = ctk.CTkTextbox(input_frame, height=60,
                                           corner_radius=20,
                                           font=("Helvetica", 14))
        self.message_input.pack(side="left", fill="both", expand=True,
                               padx=(20, 10), pady=10)
        self.message_input.bind("<Return>", self.send_message)
        
        # Send button
        send_btn = ctk.CTkButton(input_frame, text="➤", width=60, height=60,
                                corner_radius=30, font=("Helvetica", 24),
                                command=self.send_message)
        send_btn.pack(side="right", padx=(0, 20), pady=10)
        
        # Create new chat if no chat is active
        if not self.current_chat_id:
            self.create_new_chat()
    
    def upload_pdf(self):
        """Upload a PDF file"""
        file_path = filedialog.askopenfilename(
            title="Select Medical PDF",
            filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")]
        )
        
        if file_path:
            # Copy to user data directory
            dest_path = USER_DATA_DIR / Path(file_path).name
            import shutil
            shutil.copy2(file_path, dest_path)
            
            self.uploaded_pdfs.append(str(dest_path))
            self.add_message_to_chat(
                "System",
                f"✓ Successfully uploaded: {Path(file_path).name}"
            )
    
    def show_profile(self):
        """Show user profile in a popup"""
        profile_window = ctk.CTkToplevel(self.app)
        profile_window.title("Your Health Profile")
        profile_window.geometry("600x700")
        
        # Scrollable frame
        scroll = ctk.CTkScrollableFrame(profile_window, width=560, height=660)
        scroll.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Title
        ctk.CTkLabel(scroll, text="Your Health Profile",
                    font=("Helvetica", 24, "bold")).pack(pady=20)
        
        # Display profile data
        for key, value in self.user_profile.items():
            if key != 'created_at':
                frame = ctk.CTkFrame(scroll, corner_radius=10)
                frame.pack(fill="x", pady=5, padx=10)
                
                ctk.CTkLabel(frame, text=f"{key.replace('_', ' ').title()}:",
                           font=("Helvetica", 12, "bold")).pack(anchor="w", padx=10, pady=5)
                ctk.CTkLabel(frame, text=str(value),
                           font=("Helvetica", 12)).pack(anchor="w", padx=10, pady=(0, 10))
    
    def add_message_to_chat(self, sender, message):
        """Add a message to the chat display"""
        self.chat_display.configure(state="normal")
        
        # Add timestamp
        timestamp = datetime.now().strftime("%H:%M")
        
        if sender == "You":
            self.chat_display.insert("end", f"\n{timestamp} - You:\n", "user_tag")
            self.chat_display.insert("end", f"{message}\n", "user_message")
        elif sender == "System":
            self.chat_display.insert("end", f"\n{timestamp} - {message}\n", "system_tag")
        else:
            self.chat_display.insert("end", f"\n{timestamp} - AI Assistant:\n", "ai_tag")
            self.chat_display.insert("end", f"{message}\n", "ai_message")
        
        # Configure tags (CustomTkinter doesn't support font in tags)
        self.chat_display.tag_config("user_tag", foreground="#0066CC")
        self.chat_display.tag_config("ai_tag", foreground="#CC0066")
        self.chat_display.tag_config("system_tag", foreground="#666666")
        self.chat_display.tag_config("user_message", foreground="#000000")
        self.chat_display.tag_config("ai_message", foreground="#000000")
        
        self.chat_display.configure(state="disabled")
        self.chat_display.see("end")
    
    def send_message(self, event=None):
        """Send a message to the AI"""
        message = self.message_input.get("1.0", "end").strip()
        
        if not message:
            return "break"  # Prevent default Enter behavior
        
        # Clear input
        self.message_input.delete("1.0", "end")
        
        # Add user message to chat
        self.add_message_to_chat("You", message)
        
        # Get AI response in a separate thread
        threading.Thread(target=self.get_ai_response, args=(message,), daemon=True).start()
        
        return "break"  # Prevent default Enter behavior
    
    def get_ai_response(self, user_message):
        """Get response from OpenAI API"""
        try:
            # Build context from user profile
            context = self.build_context()
            
            # Build the full user message with context
            full_message = f"{context}\n\nUser Question: {user_message}"
            
            # Add chat history context
            if self.chat_history:
                history_text = "\n\nRecent Conversation:\n"
                for msg in self.chat_history[-10:]:  # Last 10 messages
                    role = "User" if msg["role"] == "user" else "Assistant"
                    history_text += f"{role}: {msg['content']}\n"
                full_message = history_text + "\n" + full_message
            
            # Call OpenAI API with the prompt ID
            response = client.responses.create(
                prompt={
                    "id": PROMPT_ID,
                    "version": PROMPT_VERSION
                },
                input=full_message
            )
            
            # Extract the AI response - OpenAI Response object
            # Response.output is a list that may contain reasoning items and messages
            # We need to find the ResponseOutputMessage with type='message'
            ai_message = None
            
            try:
                # Response is a Response object with an 'output' attribute
                if hasattr(response, 'output'):
                    output = response.output
                    
                    # Output should be a list - find the message item
                    if isinstance(output, list):
                        for item in output:
                            # Look for item with type='message' or that has 'content'
                            if hasattr(item, 'type') and item.type == 'message':
                                message = item
                            elif hasattr(item, 'content') and not hasattr(item, 'type'):
                                message = item
                            else:
                                continue
                            
                            # Get content from message
                            if hasattr(message, 'content') and isinstance(message.content, list):
                                if len(message.content) > 0:
                                    content_item = message.content[0]
                                    
                                    # Extract text from content item
                                    if hasattr(content_item, 'text'):
                                        ai_message = content_item.text
                                        break  # Found it!
                
                # If extraction failed, use fallback
                if ai_message is None:
                    print(f"WARNING: Could not extract text from response")
                    print(f"Response type: {type(response)}")
                    print(f"Has output: {hasattr(response, 'output')}")
                    if hasattr(response, 'output'):
                        print(f"Output type: {type(response.output)}")
                        print(f"Output items: {[type(item).__name__ for item in response.output]}")
                    ai_message = str(response)
                    
            except Exception as extract_error:
                print(f"ERROR extracting response: {extract_error}")
                import traceback
                traceback.print_exc()
                ai_message = f"Error: {str(extract_error)}"
            
            # Update chat history - ensure strings only
            self.chat_history.append({"role": "user", "content": str(user_message)})
            self.chat_history.append({"role": "assistant", "content": str(ai_message)})
            
            # Save chat to disk
            self.save_current_chat()
            
            # Add AI response to chat (in main thread)
            self.app.after(0, self.add_message_to_chat, "AI Assistant", ai_message)
            
        except Exception as e:
            error_msg = f"Error: {str(e)}\n\nPlease check your API key and internet connection."
            self.app.after(0, self.add_message_to_chat, "System", error_msg)
    
    def build_context(self):
        """Build context from user profile and PDFs"""
        context = "USER HEALTH INFORMATION:\n\n"
        
        # Add profile
        for key, value in self.user_profile.items():
            if key != 'created_at' and value:
                context += f"{key.replace('_', ' ').title()}: {value}\n"
        
        # Add PDF information
        if self.uploaded_pdfs:
            context += "\n\nUPLOADED MEDICAL DOCUMENTS:\n"
            for pdf_path in self.uploaded_pdfs:
                context += f"\n- {Path(pdf_path).name}\n"
                # Extract text from PDF (basic extraction)
                try:
                    with open(pdf_path, 'rb') as file:
                        reader = PyPDF2.PdfReader(file)
                        text = ""
                        for page in reader.pages[:3]:  # First 3 pages only
                            text += page.extract_text()
                        context += f"Content preview: {text[:500]}...\n"
                except:
                    pass
        
        # Reference to available health books
        context += "\n\nAVAILABLE HEALTH REFERENCE MATERIALS:\n"
        context += "- How Not to Die (Michael Greger)\n"
        context += "- Lifespan: Why We Age and Why We Don't Have To\n"
        context += "- Outlive: The Science and Art of Longevity\n"
        context += "- The China Study\n"
        context += "- The Longevity Paradox\n"
        context += "- The Circadian Diabetes Code\n"
        context += "- Blue Zones Study Guide\n"
        context += "- Ageless: The New Science of Getting Older Without Getting Old\n"
        
        return context
    
    def run(self):
        """Run the application"""
        self.app.mainloop()


if __name__ == "__main__":
    app = HealthChatbotApp()
    app.run()

