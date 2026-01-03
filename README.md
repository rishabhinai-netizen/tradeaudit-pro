# 📊 TradeAudit Pro

India's First AI-Powered Trade Discipline Analyzer

## 🚀 Quick Start Guide

### Step 1: Install Python (if not already installed)

**Windows:**
1. Download Python 3.11+ from https://www.python.org/downloads/
2. During installation, CHECK ✅ "Add Python to PATH"
3. Click "Install Now"

**Mac:**
```bash
# Install Homebrew first (if not installed)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install Python
brew install python@3.11
```

**Verify Installation:**
```bash
python --version
# Should show Python 3.11.x or higher
```

### Step 2: Clone This Repository

```bash
# Navigate to where you want the project
cd Desktop  # or wherever you prefer

# Clone from GitHub (after you upload)
git clone https://github.com/YOUR_USERNAME/tradeaudit-pro.git
cd tradeaudit-pro
```

**OR Download ZIP:**
1. Click green "Code" button on GitHub
2. Click "Download ZIP"
3. Extract to Desktop/tradeaudit-pro

### Step 3: Install Dependencies

**Open Terminal/Command Prompt in project folder:**

**Windows (Command Prompt):**
```cmd
cd Desktop\tradeaudit-pro
python -m pip install --upgrade pip
pip install -r requirements.txt
```

**Mac/Linux:**
```bash
cd Desktop/tradeaudit-pro
python3 -m pip install --upgrade pip
pip3 install -r requirements.txt
```

**This will take 2-3 minutes.** You'll see packages downloading.

### Step 4: Run the App

```bash
# Windows
streamlit run app.py

# Mac/Linux
streamlit run app.py
```

**Your browser will automatically open to http://localhost:8501**

If it doesn't, manually go to that URL.

---

## 📁 Supported Broker Formats

### ✅ Currently Supported:
- **Zerodha** - Equity Tradebook CSV
- **Kotak Securities** - Equity Transaction Statement CSV
- **Kotak Securities** - Derivatives Transaction Statement CSV
- **ICICI Direct** - Equity Orderbook CSV

### 🔜 Coming Soon:
- Upstox
- Angel One
- Groww
- 5paisa

---

## 🎯 Features

### Current (MVP):
- ✅ Multi-broker CSV upload
- ✅ Automatic trade reconstruction
- ✅ P&L calculation with all charges
- ✅ Basic discipline scoring
- ✅ Interactive trade visualizations

### Roadmap:
- 🔜 Advanced strategy analysis (Momentum, Mean Reversion)
- 🔜 Behavioral pattern detection
- 🔜 Market data integration
- 🔜 PDF report generation
- 🔜 Custom strategy builder

---

## 🐛 Troubleshooting

### "Python not recognized"
- Reinstall Python with "Add to PATH" checked

### "No module named 'streamlit'"
- Run: `pip install -r requirements.txt` again

### "Port 8501 already in use"
- Close other Streamlit apps
- Or use: `streamlit run app.py --server.port 8502`

### Files not uploading
- Check CSV format matches broker examples
- File size should be < 200MB

---

## 📞 Support

- **Issues**: Open a GitHub issue
- **Email**: your-email@example.com
- **Documentation**: Check `/docs` folder

---

## 📄 License

MIT License - See LICENSE file

---

## 🙏 Acknowledgments

Built with:
- Streamlit (UI framework)
- Plotly (Charts)
- Pandas (Data processing)

Inspired by trading wisdom from:
- Mark Minervini (SEPA)
- William O'Neil (CANSLIM)
- Richard Dennis (Turtle Trading)

---

**Made with ❤️ for Indian Traders**
