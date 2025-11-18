# 🚀 Quick Deploy: Get Your Domain + HTTPS in 30 Minutes

## TL;DR Steps

1. Buy domain ($10/year)
2. Push code to GitHub (free)
3. Deploy to Render (free)
4. Connect domain
5. Wait 10 minutes
6. Done! `https://yourapp.com` is live! 🎉

---

## Step-by-Step (Copy & Paste)

### 1. Buy a Domain (5 minutes)

Go to https://www.namecheap.com
- Search for domain (e.g., `myhealthai.com`)
- Add to cart, checkout
- **Cost:** ~$13/year

---

### 2. Push to GitHub (10 minutes)

```bash
cd /Users/finncullen/Desktop/CURSOR/filesforhealthbot

# Create .gitignore
cat > .gitignore << 'EOF'
__pycache__/
*.pyc
flask_sessions/
user_data_web/
.DS_Store
*.spec
build/
dist/
venv*/
*.pdf
EOF

# Initialize git
git init
git add .
git commit -m "Health AI Web App"

# Create repo on GitHub.com, then:
git remote add origin https://github.com/YOUR_USERNAME/your-repo.git
git branch -M main
git push -u origin main
```

---

### 3. Deploy to Render (10 minutes)

1. **Go to:** https://render.com
2. **Sign up** with GitHub
3. **Click:** "New +" → "Web Service"
4. **Select** your GitHub repo
5. **Fill in:**
   - **Name:** `health-ai`
   - **Build Command:** `pip install -r requirements_web.txt`
   - **Start Command:** `gunicorn web_app:app`
6. **Add Environment Variable:**
   - **Key:** `SECRET_KEY`
   - **Value:** Generate with:
     ```bash
     python3 -c "import secrets; print(secrets.token_hex(32))"
     ```
7. **Select:** Free plan
8. **Click:** "Create Web Service"

**Wait 2-3 minutes...** Your app is now at `https://your-app.onrender.com`

---

### 4. Connect Your Domain (5 minutes)

#### On Render:
1. **Click:** Settings
2. **Scroll to:** "Custom Domain"
3. **Click:** "Add Custom Domain"
4. **Enter:** `yourapp.com`
5. **Copy** the DNS settings Render shows you

#### On Namecheap:
1. **Login** to Namecheap
2. **Go to:** Domain List → Manage → Advanced DNS
3. **Delete** existing records
4. **Add these records:**

```
Type: A Record
Host: @
Value: 216.24.57.1  (from Render)

Type: CNAME Record  
Host: www
Value: your-app.onrender.com  (from Render)
```

5. **Save**

---

### 5. Wait & Test (10 minutes)

**Wait 10-60 minutes for:**
- DNS to propagate
- HTTPS to activate automatically

**Then test:**
- Visit `https://yourapp.com` 
- Look for 🔒 padlock
- Test on phone!

---

## ✅ Done!

Your app is now at:
- **`https://yourapp.com`** ✅
- **Secure (HTTPS)** 🔒
- **Worldwide access** 🌍
- **Professional domain** 💼

**Total Cost:** $13/year (just the domain!)

---

## What You Get

```
Before:  http://localhost:5000
         (only on your computer)

After:   https://yourapp.com
         ✅ Accessible from anywhere
         ✅ Secure (HTTPS)
         ✅ Professional domain
         ✅ Works on all devices
```

---

## Troubleshooting

**"Can't reach site"**
- Wait longer (DNS can take 60 minutes)
- Check DNS at https://dnschecker.org

**"Not secure" warning**
- Wait 5-10 minutes after DNS works
- HTTPS activates automatically

**"Application Error"**
- Check Render logs
- Verify all files pushed to GitHub

---

## Upgrade to Paid (Optional)

**Render Free Plan Limits:**
- Sleeps after 15 minutes of inactivity
- First request after sleep is slow (5-10 seconds)

**Render Paid ($7/month):**
- Always-on
- Fast responses
- Better for selling

**Upgrade:** Settings → "Instance Type" → Select paid plan

---

## Next Steps

1. ✅ Get domain
2. ✅ Deploy
3. ✅ Connect domain
4. ✅ HTTPS working
5. **→ Add payment system (Stripe/Gumroad)**
6. **→ Add privacy policy**
7. **→ Start selling!**

---

## Cost Summary

| Item | Free Plan | Paid Plan |
|------|-----------|-----------|
| Domain | $13/year | $13/year |
| Hosting | $0/month | $7/month |
| SSL/HTTPS | $0 | $0 |
| **Total** | **$13/year** | **$97/year** |

---

**Questions? Check `CUSTOM_DOMAIN_GUIDE.md` for detailed help!**

