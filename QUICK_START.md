# 🚀 ROSE GUARD - Quick Start Guide

## ✅ Installation Complete!

Your ROSE GUARD application with the beautiful new UI is now running!

---

## 📦 What Was Installed

**Essential Packages:**
- ✅ `ttkbootstrap` - Modern themed Tkinter widgets
- ✅ `Pillow` - Image processing support
- ✅ `bcrypt` - Secure password hashing
- ✅ `argon2-cffi` - Modern password hashing
- ✅ `psutil` - System monitoring
- ✅ `PyYAML` - Configuration management

**Optional Packages** (install if needed):
```bash
pip install matplotlib pandas tqdm
```

---

## 🎯 How to Use the Enhanced UI

### 1. **Testing a Password**

#### Step 1: Enter Password
- Look for the **🔑 Password Configuration** card
- Enter your password in the text field
- Click the **👁️ Show Password** toggle to see what you're typing

#### Step 2: Select Hash Algorithm
- Choose from the dropdown:
  - **MD5** ⚠️ - Fast but insecure (for testing only)
  - **SHA-256** - Basic security
  - **bcrypt** 🔒 - Recommended
  - **Argon2** 🛡️ - Most secure
- Click **ℹ️ Info** to learn about each algorithm

#### Step 3: Choose Wordlist
- Click **📁 Browse** to select your wordlist file
- Default: `wordlists/demo_wordlist.txt`

#### Step 4: Select Attack Method
Choose one of three attack types:

**📚 Dictionary Attack** (Green Button)
- Tests password against wordlist
- Applies common mutations (1, 123, !, @, etc.)
- Fast and efficient

**💪 Brute Force** (Blue Button)
- Tries all possible combinations
- Configurable character set and length
- Slower but comprehensive

**🔀 Hybrid Attack** (Cyan Button)
- Combines dictionary + mutations
- Tests wordlist + number/symbol suffixes
- Best of both worlds

#### Step 5: Monitor Progress
- Watch the animated progress bar
- See real-time statistics:
  - Current attempts
  - Speed (attempts/second)
  - Estimated time remaining (ETA)
  - Elapsed time

#### Step 6: Stop if Needed
- Click **🛑 Stop Attack** to cancel anytime
- Results will show partial progress

---

### 2. **Viewing Results**

After an attack completes, you'll see:

**Success Message** 🔓
```
🎯 Attack Results
==================
🔓 SUCCESS: Password was cracked!
🔑 Found password: [password]
⚡ Total attempts: 1,234
⏱️ Time taken: 0.45 seconds
🚀 Average speed: 2,742 attempts/second
```

**Resistance Message** 🛡️
```
🎯 Attack Results
==================
🛡️ Password resisted the attack
⚡ Total attempts: 10,000
⏱️ Time taken: 3.67 seconds
🚀 Average speed: 2,725 attempts/second
```

---

### 3. **Generating Reports**

#### Beautiful HTML Report
1. Click **💾 Save Report** button
2. Choose where to save the file
3. Report opens automatically in your browser

**Report Features:**
- 📊 Executive summary with security alerts
- ⚡ Performance metrics dashboard
- 📝 Detailed attack history
- 💡 Personalized security recommendations
- 🎨 Professional gradient design
- 📱 Responsive layout (looks great on any device)
- 🖨️ Print-friendly styling

#### CSV Export
1. Go to **📈 Performance Metrics** tab
2. Click **📊 Export Results**
3. Save as CSV for Excel/analysis

---

### 4. **Viewing Metrics**

Switch to the **📈 Performance Metrics** tab to see:

**Overall Statistics:**
- Total attacks performed
- Success rate
- Total attempts
- Average speed
- Time statistics

**Per-Hash Analysis:**
- Success rate by algorithm
- Average time per algorithm
- Efficiency comparisons

**Per-Attack Analysis:**
- Success rate by method
- Efficiency scores
- Performance comparisons

---

## 🎨 Customizing Your Experience

### Change Theme
1. Click **View** in menu bar
2. Select **Theme**
3. Choose from 9 beautiful themes:
   - Darkly (default)
   - Cosmo
   - Flatly
   - Litera
   - Minty
   - Pulse
   - Sandstone
   - United
   - Yeti

### Menu Options

**File Menu:**
- **New Session** - Reset and start fresh
- **Open Wordlist** - Load new wordlist
- **Export Results** - Save as CSV
- **Save Report** - Generate HTML report
- **Exit** - Close application

**View Menu:**
- **Theme** - Change color scheme

**Help Menu:**
- **Documentation** - View online docs
- **About** - Version and credits

---

## 💡 Pro Tips

### Password Testing Tips
1. **Start with Dictionary Attack** - Fastest way to test
2. **Use Strong Hashing** - Test with bcrypt or Argon2 for realistic results
3. **Monitor Speed** - Compare performance across algorithms
4. **Check Recommendations** - Read report suggestions

### Performance Tips
1. **Use Smaller Wordlists** for quick tests
2. **Stop Long Attacks** early if needed
3. **Export Metrics** for comparison
4. **Save Reports** for documentation

### Security Best Practices
1. **Never test production passwords** - Only test in safe environments
2. **Use for education** - Learn about password security
3. **Follow recommendations** - Apply insights from reports
4. **Enable 2FA** - Always use two-factor authentication

---

## 🎯 Common Tasks

### Quick Password Test
```
1. Enter password
2. Keep default bcrypt hash
3. Click "Dictionary Attack"
4. Wait for results
5. Read recommendations
```

### Comprehensive Test
```
1. Enter password
2. Test with all hash algorithms
3. Try all three attack methods
4. Compare results in metrics
5. Generate full report
```

### Batch Testing
```
1. Create text file with passwords
2. Test each one individually
3. Export results after each test
4. Compare in spreadsheet
```

---

## ⚡ Keyboard Shortcuts

- **Ctrl+N** - New Session
- **Ctrl+O** - Open Wordlist
- **Ctrl+S** - Save Report
- **F1** - Help/About

---

## 🐛 Troubleshooting

### Issue: Application won't start
**Solution:**
```bash
pip install ttkbootstrap Pillow bcrypt argon2-cffi psutil pyyaml
python rose_guard_gui.py
```

### Issue: Wordlist not found
**Solution:**
- Check that `wordlists/demo_wordlist.txt` exists
- Or browse to select a different wordlist

### Issue: Attack is slow
**Solution:**
- Use smaller wordlist for testing
- Reduce max_length in config.yaml for brute force
- Use faster hash algorithm (MD5 for testing only)

### Issue: Report won't open
**Solution:**
- Check that `templates/report_template.html` exists
- Manually open the saved HTML file
- Check file permissions

---

## 📚 Additional Resources

- **IMPROVEMENTS_SUMMARY.md** - Overview of all UI enhancements
- **UI_IMPROVEMENTS_GUIDE.md** - Future feature recommendations
- **config.yaml** - Configuration options
- **README.md** - Full documentation

---

## 🌟 Features at a Glance

✨ **Beautiful Modern UI**
- Professional color scheme
- Card-based layout
- Icon-enhanced buttons
- Smooth animations

📊 **Comprehensive Testing**
- Multiple hash algorithms
- Three attack methods
- Real-time progress
- Detailed metrics

📈 **Professional Reports**
- Stunning HTML design
- Security recommendations
- Performance analytics
- Export options

🎨 **Customizable**
- 9 themes to choose from
- Configurable settings
- Flexible wordlists
- Adjustable parameters

---

## 🎉 Enjoy Your Enhanced ROSE GUARD!

You now have a **beautiful, professional, and powerful** password security testing tool!

**Key Features:**
- 💎 Modern design
- 🚀 Great user experience
- 📊 Comprehensive reporting
- 🛡️ Professional presentation

**Happy Testing! 🔐**

---

## 📞 Need Help?

1. Check this guide first
2. Review the error messages
3. Check the log files in `logs/roseguard.log`
4. Verify all dependencies are installed
5. Make sure config.yaml is valid

---

**Version:** 1.0.0 Enhanced Edition  
**Created by:** OGBODO ROSEMARY CHIAMAKA  
**Enhanced:** October 2025
