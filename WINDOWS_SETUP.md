# 🪟 Windows Setup Guide

## Step-by-Step Installation

### 1. Install Python

1. Go to https://www.python.org/downloads/
2. Download Python 3.11 or later
3. **IMPORTANT**: During installation, check ✅ "Add Python to PATH"
4. Click "Install Now"
5. Wait for installation to complete

**Verify Installation:**
```cmd
python --version
```
Should show: `Python 3.11.x` or higher

### 2. Download Project Files

**Option A: Download ZIP from GitHub**
1. Go to your GitHub repository
2. Click green "Code" button
3. Click "Download ZIP"
4. Extract to `C:\Users\YourName\Desktop\tradeaudit-pro`

**Option B: Use Git (if installed)**
```cmd
cd Desktop
git clone https://github.com/YOUR_USERNAME/tradeaudit-pro.git
cd tradeaudit-pro
```

### 3. Open Command Prompt in Project Folder

1. Open File Explorer
2. Navigate to `Desktop\tradeaudit-pro`
3. Click in the address bar and type `cmd`
4. Press Enter

### 4. Install Dependencies

```cmd
python -m pip install --upgrade pip
pip install -r requirements.txt
```

**This will take 2-3 minutes.**

You'll see output like:
```
Collecting streamlit==1.31.0
Downloading streamlit-1.31.0-py2.py3-none-any.whl (8.4 MB)
Installing collected packages: ...
Successfully installed streamlit-1.31.0 pandas-2.1.4 ...
```

### 5. Run the App!

```cmd
streamlit run app.py
```

Your browser will automatically open to: http://localhost:8501

**If browser doesn't open automatically:**
- Manually go to http://localhost:8501 in Chrome/Edge

### 6. Upload Your Tradebook

1. Download tradebook CSV from your broker
2. Click "Browse files" in sidebar
3. Select your CSV
4. Click "Analyze Trades"

---

## 🐛 Troubleshooting

### "Python is not recognized..."

**Solution:**
1. Reinstall Python
2. Make sure to check ✅ "Add Python to PATH"
3. Restart Command Prompt

### "No module named 'streamlit'"

**Solution:**
```cmd
pip install -r requirements.txt
```

### "Port 8501 is already in use"

**Solution:**
```cmd
streamlit run app.py --server.port 8502
```

Then go to http://localhost:8502

### App won't load

**Solution:**
1. Close Command Prompt
2. Reopen in project folder
3. Run again: `streamlit run app.py`

---

## 🎓 Video Tutorial (Coming Soon)

We'll create a video walkthrough showing:
- Python installation
- Running the app
- Uploading tradebook
- Understanding the results

---

## 📞 Need Help?

- Create an issue on GitHub
- Email: your-email@example.com

**Made with ❤️ for Windows Users**
