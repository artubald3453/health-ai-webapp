# 🔐 User Accounts System

Your Health AI app now has a full user account system! Users can create accounts and access their data from anywhere.

## ✨ New Features

### 1. **User Accounts**
- Sign up with email and password
- Login from any device
- Secure password hashing (bcrypt-level security)

### 2. **Persistent Data Storage**
- ✅ **API Key** - Saved to your account (no need to re-enter!)
- ✅ **Health Profile** - Your survey answers stored securely
- ✅ **Chat History** - All conversations saved to your account
- ✅ **Access Anywhere** - Login from phone, tablet, or desktop

### 3. **SQLite Database**
- Lightweight database (single file)
- No external database server needed
- Easy to deploy anywhere
- Automatic backups possible

---

## 📱 User Flow

```
1. Visit homepage
2. Create Account (email + password)
3. Setup API Key (one time only!)
4. Complete Health Survey (one time only!)
5. Start Chatting
6. Logout anytime
7. Login from any device - everything is saved!
```

---

## 🔒 Security Features

### Password Security
- Passwords are **hashed** (never stored in plain text)
- Uses `werkzeug` security (same as Flask framework)
- Minimum 8 character requirement

### API Key Protection
- Stored encrypted in database
- Only accessible when logged in
- Never exposed in frontend

### Session Security
- Server-side sessions (not cookies)
- Secure session management with Flask-Login
- Auto-logout on browser close (optional)

---

## 🗄️ Database Structure

### **users** table
```
id              - Unique user ID
email           - User's email (unique)
password_hash   - Hashed password
api_key         - OpenAI API key
profile         - JSON health profile data
created_at      - Account creation date
```

### **chats** table
```
id              - Unique chat ID
user_id         - Owner of the chat
title           - Chat title (from first message)
messages        - JSON array of all messages
created_at      - Chat creation date
```

---

## 🚀 Deployment Changes

### Required Files
- `database.py` - Database functions
- `web_app.py` - Updated with user auth
- `templates/login.html` - Login page
- `templates/signup.html` - Signup page
- `requirements_web.txt` - Updated dependencies

### New Dependencies
```
flask-login>=0.6.3
werkzeug>=3.0.0
```

### Database Location
The database file (`users.db`) will be created automatically at:
```
user_data_web/users.db
```

This file contains ALL user data and should be:
- ✅ Backed up regularly
- ✅ Excluded from Git (already in .gitignore)
- ✅ Kept secure on your server

---

## 💾 Backup Strategy

### Local Development
```bash
# Backup database
cp user_data_web/users.db user_data_web/users.db.backup

# Restore from backup
cp user_data_web/users.db.backup user_data_web/users.db
```

### Production (Render/Heroku)
- Use Render's persistent disk feature
- Or store in cloud database (PostgreSQL upgrade possible)
- Regular automated backups recommended

---

## 🎯 Testing Locally

### 1. Install dependencies
```bash
cd /Users/finncullen/Desktop/CURSOR/filesforhealthbot
pip3 install -r requirements_web.txt
```

### 2. Run the server
```bash
python3 web_app.py
```

### 3. Test account flow
1. Visit http://localhost:5000
2. Click "Create Account"
3. Sign up with test email
4. Add your OpenAI API key
5. Complete health survey
6. Start chatting
7. Logout and login again - everything saved!

---

## 🌐 Production Deployment

### On Render
1. Push code to GitHub
2. Render will auto-detect changes
3. **Important**: Enable persistent disk storage
   - Dashboard → Your Service → Disk
   - Mount Path: `/opt/render/project/src/user_data_web`
   - Size: 1GB (free tier)

Without persistent disk, users will lose data on each deploy!

### Environment Variables
```
SECRET_KEY=(generate with: python3 -c "import secrets; print(secrets.token_hex(32))")
```

---

## 🔄 Upgrading to PostgreSQL (Optional)

For production at scale, you can upgrade to PostgreSQL:

### Why?
- Better for multiple servers
- Built-in backups
- Higher concurrent users
- Free tier on Render

### How?
1. Create Render PostgreSQL database
2. Install `psycopg2-binary`
3. Update `database.py` to use PostgreSQL
4. Migrate existing data

SQLite is fine for hundreds of users, but PostgreSQL is better for thousands.

---

## 🎨 Customization Ideas

### Add "Remember Me"
```python
login_user(user, remember=True)  # Stays logged in for 30 days
```

### Add Email Verification
- Send confirmation email on signup
- Verify email before allowing chat

### Add Password Reset
- "Forgot password" feature
- Email reset link

### Add User Settings
- Change password
- Update health profile
- Delete account

---

## 🐛 Troubleshooting

### "No module named 'flask_login'"
```bash
pip3 install flask-login
```

### "Database is locked"
SQLite has limited concurrent access. Upgrade to PostgreSQL for production.

### "User not logged in" errors
Check that `@login_required` decorator is on protected routes.

### Lost user data
Database file was deleted or not persisted. Enable persistent disk on Render.

---

## 📊 Database Management

### View users
```bash
sqlite3 user_data_web/users.db "SELECT id, email, created_at FROM users;"
```

### View chats
```bash
sqlite3 user_data_web/users.db "SELECT id, title, user_id FROM chats;"
```

### Reset database (DANGER!)
```bash
rm user_data_web/users.db
# Will be recreated on next run
```

---

## 🎉 Benefits

### For Users
- ✅ No setup friction (login once!)
- ✅ Access from any device
- ✅ Never lose chat history
- ✅ Professional experience

### For You
- ✅ Track user growth
- ✅ Enable paid features later
- ✅ Better analytics
- ✅ Email marketing possible

---

## 🚀 Next Steps

1. Test locally
2. Deploy to Render
3. Enable persistent disk
4. Test signup/login flow
5. Share with users!

Your app is now production-ready! 🎊

