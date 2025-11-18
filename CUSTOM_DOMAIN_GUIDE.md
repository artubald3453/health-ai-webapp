# 🌐 Custom Domain + HTTPS Setup Guide

## Get Your Website Online at `https://yourapp.com`

This guide will take you from local development to a live website with:
- ✅ Custom domain (yourapp.com)
- ✅ HTTPS (secure, that padlock 🔒)
- ✅ Accessible from anywhere
- ✅ Professional look

**Total Cost:** $10-15/year for domain + $0-7/month for hosting

---

## 📋 Overview: What You'll Do

1. Buy a domain name ($10-15/year)
2. Deploy your app to hosting service ($0-7/month)
3. Connect domain to hosting
4. Enable HTTPS (automatic, free!)
5. Done! 🎉

**Time:** 30-60 minutes

---

## Step 1: Buy a Domain Name (10 minutes)

### Option A: Namecheap (Recommended)
**Cost:** $10-13/year

1. Go to https://www.namecheap.com
2. Search for your desired domain:
   - `healthai.com`
   - `myhealthassistant.com`
   - `aihealth.app`
   - `wellness-ai.com`
3. Add to cart and checkout
4. **Important:** Turn OFF "WhoisGuard" auto-renewal (it's free first year)
5. Complete purchase

**Tips:**
- `.com` is most trusted ($13/year)
- `.app` looks modern ($15/year)
- `.io` is techy ($35/year)
- Shorter is better!

### Option B: Google Domains
**Cost:** $12/year

1. Go to https://domains.google
2. Search and purchase
3. Very simple, no upsells

### Option C: Cloudflare Registrar
**Cost:** $8-10/year (at-cost pricing!)

1. Create Cloudflare account
2. Register domain
3. Cheapest option, no markup

---

## Step 2: Deploy Your App (15 minutes)

### 🏆 RECOMMENDED: Render.com

**Why Render:**
- ✅ FREE plan available
- ✅ Automatic HTTPS
- ✅ Custom domain support
- ✅ Easy to use
- ✅ Auto-deploys on code changes

**Steps:**

#### 2.1: Prepare Your Code

First, push your code to GitHub:

```bash
cd /Users/finncullen/Desktop/CURSOR/filesforhealthbot

# Initialize git (if not already)
git init

# Create .gitignore
cat > .gitignore << 'EOF'
__pycache__/
*.pyc
*.pyo
flask_sessions/
user_data_web/
.DS_Store
*.spec
build/
dist/
venv/
venv_chatbot/
*.pdf
EOF

# Add all files
git add .

# Commit
git commit -m "Health AI Web App"

# Create GitHub repo and push
# (Create repo on github.com first, then:)
git remote add origin https://github.com/YOUR_USERNAME/health-ai-webapp.git
git push -u origin main
```

#### 2.2: Deploy to Render

1. **Create Account**
   - Go to https://render.com
   - Sign up with GitHub

2. **Create Web Service**
   - Click "New +" → "Web Service"
   - Connect your GitHub repo
   - Click "Connect" on your repo

3. **Configure Service**
   ```
   Name: health-ai-assistant
   Region: Oregon (or closest to you)
   Branch: main
   Runtime: Python 3
   Build Command: pip install -r requirements_web.txt
   Start Command: gunicorn web_app:app
   ```

4. **Environment Variables**
   Click "Advanced" → Add:
   ```
   Key: SECRET_KEY
   Value: (generate with: python3 -c "import secrets; print(secrets.token_hex(32))")
   ```

5. **Select Plan**
   - Free plan is fine to start!
   - Paid ($7/month) for always-on

6. **Click "Create Web Service"**

7. **Wait 2-3 minutes for deployment**

Your app is now live at: `https://health-ai-assistant.onrender.com`

---

## Step 3: Connect Your Domain (10 minutes)

### On Render:

1. **Go to your service**
2. **Click "Settings"**
3. **Scroll to "Custom Domain"**
4. **Click "Add Custom Domain"**
5. **Enter your domain:** `yourapp.com`
6. **Render will show you DNS settings** like:
   ```
   Type: CNAME
   Name: www
   Value: health-ai-assistant.onrender.com
   
   Type: A
   Name: @
   Value: 216.24.57.1
   ```

### On Namecheap (or your domain provider):

1. **Login to Namecheap**
2. **Go to Domain List**
3. **Click "Manage" on your domain**
4. **Click "Advanced DNS"**
5. **Add these records:**

   **For apex domain (yourapp.com):**
   ```
   Type: A Record
   Host: @
   Value: 216.24.57.1  (from Render)
   TTL: Automatic
   ```

   **For www subdomain (www.yourapp.com):**
   ```
   Type: CNAME Record
   Host: www
   Value: health-ai-assistant.onrender.com
   TTL: Automatic
   ```

6. **Save changes**

**Wait 10-60 minutes for DNS to propagate**

---

## Step 4: Enable HTTPS (Automatic!)

**Good news: Render does this automatically! 🎉**

Once your domain is connected:
1. Render detects it
2. Automatically provisions SSL certificate (via Let's Encrypt)
3. Enables HTTPS
4. Redirects HTTP → HTTPS

**Takes 5-10 minutes after DNS propagates.**

---

## Step 5: Test & Verify ✅

### Test Your Website:

```bash
# Test without www
curl -I https://yourapp.com

# Test with www
curl -I https://www.yourapp.com

# Should both show:
# HTTP/2 200
# (SSL certificate valid)
```

### Check in Browser:
1. Visit `https://yourapp.com`
2. Look for 🔒 padlock in address bar
3. Click padlock → "Connection is secure"
4. Test on phone!

---

## 🎉 You're Live!

Your app is now accessible at:
- ✅ `https://yourapp.com`
- ✅ `https://www.yourapp.com`
- ✅ Secure (HTTPS)
- ✅ Professional custom domain
- ✅ Works on all devices

---

## Alternative Hosting Options

### Option 2: Heroku ($7/month)

**Pros:**
- Very reliable
- Always-on
- Easy SSL

**Steps:**
1. Create Heroku account
2. Install Heroku CLI
3. Create `Procfile`:
   ```
   web: gunicorn web_app:app
   ```
4. Deploy:
   ```bash
   heroku login
   heroku create your-app-name
   git push heroku main
   ```
5. Add domain:
   ```bash
   heroku domains:add yourapp.com
   heroku domains:add www.yourapp.com
   ```
6. Follow DNS instructions
7. HTTPS is automatic!

**Cost:** $7/month

---

### Option 3: DigitalOcean ($5/month)

**Pros:**
- Full control
- Good performance
- Scalable

**Cons:**
- More technical
- Manual SSL setup

**Quick Setup:**
1. Create $5 Droplet (Ubuntu)
2. SSH in
3. Install Python, Nginx, Certbot
4. Deploy app
5. Configure Nginx
6. Get SSL with Certbot:
   ```bash
   sudo certbot --nginx -d yourapp.com -d www.yourapp.com
   ```

**Full Guide:** https://www.digitalocean.com/community/tutorials/how-to-serve-flask-applications-with-gunicorn-and-nginx-on-ubuntu-20-04

---

### Option 4: Vercel (Free!)

**Pros:**
- FREE
- Fast globally
- Easy custom domains
- Auto HTTPS

**Steps:**
1. Install Vercel CLI:
   ```bash
   npm install -g vercel
   ```

2. Create `vercel.json`:
   ```json
   {
     "version": 2,
     "builds": [
       {
         "src": "web_app.py",
         "use": "@vercel/python"
       }
     ],
     "routes": [
       {
         "src": "/(.*)",
         "dest": "web_app.py"
       }
     ]
   }
   ```

3. Deploy:
   ```bash
   vercel --prod
   ```

4. Add domain in Vercel dashboard
5. Update DNS (Vercel provides instructions)
6. HTTPS automatic!

**Cost:** FREE

---

## 🔒 SSL/HTTPS Details

### What is HTTPS?
- Encrypts data between user and server
- Shows padlock 🔒 in browser
- Required for:
  - Login forms
  - Payment processing
  - User trust
  - Google rankings

### How It Works:
1. Hosting provider provisions SSL certificate
2. Certificate is from Let's Encrypt (free, trusted)
3. Automatically renews every 90 days
4. Your site is secure!

### All Modern Hosts Do This Automatically:
- ✅ Render
- ✅ Vercel
- ✅ Heroku
- ✅ Netlify
- ⚠️ DigitalOcean (needs Certbot setup)

---

## 💰 Total Costs

### Minimum Setup (FREE):
- Domain: $10-13/year (Namecheap)
- Hosting: $0/month (Render free tier)
- SSL: $0 (Let's Encrypt)
- **Total: $10-13/year** (~$1/month!)

### Recommended Setup:
- Domain: $10-13/year
- Hosting: $7/month (Render paid or Heroku)
- SSL: $0
- **Total: $94-97/year** (~$8/month)

### Professional Setup:
- Domain: $10-13/year
- Hosting: $12+/month (better tier)
- CDN: $0-20/month (Cloudflare)
- **Total: $154+/year** (~$13/month)

---

## 📧 Professional Email (Optional)

Want `support@yourapp.com`?

### Option 1: Google Workspace
- $6/user/month
- Professional email
- Calendar, Drive, etc.

### Option 2: Zoho Mail
- FREE for 1 user
- Basic but functional
- Link: https://www.zoho.com/mail/

### Option 3: Cloudflare Email Routing
- FREE
- Forwards to your Gmail
- Link: https://developers.cloudflare.com/email-routing/

---

## 🚀 Quick Reference Card

### DNS Settings (Namecheap):

```
┌─────────────────────────────────────────┐
│ Type    │ Host  │ Value                │
├─────────────────────────────────────────┤
│ A       │ @     │ 216.24.57.1          │
│ CNAME   │ www   │ your-app.onrender.com│
└─────────────────────────────────────────┘
```

### Render Settings:

```
┌─────────────────────────────────────────┐
│ Build Command:                          │
│   pip install -r requirements_web.txt   │
│                                         │
│ Start Command:                          │
│   gunicorn web_app:app                  │
│                                         │
│ Environment Variables:                  │
│   SECRET_KEY=your-secret-key-here       │
└─────────────────────────────────────────┘
```

---

## 🐛 Troubleshooting

### "Site can't be reached"
- **Wait:** DNS takes 10-60 minutes
- **Check:** DNS records are correct
- **Clear cache:** `ipconfig /flushdns` (Windows) or `sudo dscacheutil -flushcache` (Mac)

### "Your connection is not private"
- **Wait:** SSL takes 5-10 minutes after DNS
- **Check:** Domain is fully connected
- **Try:** Visiting without www or vice versa

### "Application Error"
- **Check logs:** On Render dashboard
- **Verify:** `requirements_web.txt` has all dependencies
- **Check:** `gunicorn` is installed

### DNS Not Propagating
- **Check:** https://dnschecker.org
- **Enter:** Your domain
- **See:** If DNS has spread globally
- **Wait:** Can take up to 48 hours (usually 1 hour)

---

## ✅ Final Checklist

- [ ] Domain purchased
- [ ] GitHub repo created
- [ ] Code pushed to GitHub
- [ ] Render account created
- [ ] App deployed on Render
- [ ] Custom domain added on Render
- [ ] DNS records configured
- [ ] Waited 10-60 minutes
- [ ] HTTPS working (🔒 in browser)
- [ ] Tested on mobile
- [ ] Tested API key setup
- [ ] Tested chat functionality

---

## 🎯 Next Steps After Domain

1. **Set up analytics** (Google Analytics)
2. **Add privacy policy** (required for legal)
3. **Set up payment** (Stripe/Gumroad)
4. **Create landing page** (marketing)
5. **Start promoting!**

---

## 🎊 Congratulations!

You now have a professional web app at:
- `https://yourapp.com` ✅
- Secure with HTTPS 🔒
- Accessible worldwide 🌍
- Professional custom domain 💼

**Your Health AI Assistant is officially LIVE!** 🚀

---

## Quick Commands Reference

```bash
# Generate secret key
python3 -c "import secrets; print(secrets.token_hex(32))"

# Check DNS
nslookup yourapp.com

# Check SSL certificate
openssl s_client -connect yourapp.com:443

# Test website
curl -I https://yourapp.com
```

---

**Need help? Check the troubleshooting section or Render's excellent documentation!**

