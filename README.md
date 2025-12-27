# UnfollowXBot - Intelligent Hybrid System for Twitter/X

**UnfollowXBot** is an intelligent automated bot designed to unfollow users who do not follow back on Twitter/X. It features a hybrid analysis system using AI (OpenRouter) to protect developers, researchers, and tech professionals.

**🆕 Hybrid Version:** Chrome Extension + Python AI Analysis!

## 🚀 Key Features

### 🆕 Hybrid System (RECOMMENDED)
- 🌐 **Chrome Extension** - Works seamlessly with current X UI changes.
- 🤖 **AI Analysis** - Uses OpenRouter to categorize and analyze profiles.
- 🛡️ **Immunity System** - Automatically protects devs, researchers, and academics.
- 📊 **CSV Analysis** - Organized, auditable data logs with complete bios.
- ⚡ **Auto Identification** - Detects non-followers automatically.
- ⏰ **Auto Execution** - Unfollows 15 users every 25 minutes (to respect rate limits).
- 🚫 **No API Required** - Does not require Twitter API credentials.

### 📜 Selenium System (LEGACY)
- 🌐 **Selenium Only** - Works strictly via browser automation (Chrome/Brave).
- 💾 **Saved Progress** - Can be paused and resumed.
- 🔄 **Smart Filters** - Multiple criteria for filtering users.
- 📈 **High Volume Support** - Optimized for thousands of users.

## 🎯 Workflow

### 🆕 Hybrid System:
1. **🌐 Chrome Extension** - Identifies non-followers automatically.
2. **📋 Data Collection** - Extracts username, bio, and location from profiles.
3. **🤖 AI Analysis** - AI analyzes profiles to determine immunity status.
4. **💾 Complete CSV** - Saves detailed analysis to CSV format.
5. **🛡️ Filtering** - Automatically removes immune users from the list.
6. **⚡ Intelligent Unfollow** - Executes selective unfollows via extension.

### 📜 Legacy System:
1. **🌐 Selenium Collection** - Extracts following/followers lists.
2. **📋 Bio Extraction** - Gathers bio, location, and profile data.
3. **🤖 AI Analysis** - Analyzes profiles for immunity.
4. **💾 CSV Export** - Saves data to CSV.
5. **🛡️ Filtering** - Removes protected profiles.
6. **⚡ Selenium Unfollow** - Executed via browser automation.

## 📦 Installation

bash
# Install dependencies
pip install -r requirements.txt --force-reinstall


## ⚙️ Configuration

### 1. Prerequisites

- **Browser**: Chrome or Brave installed.
- **Login**: Logged into Twitter/X in the browser.
- **OpenRouter**: API Key for AI analysis.

### 2. Configure Environment Variables

bash
# Copy example file
cp .env.example .env

# Edit with your credentials
nano .env


### 3. Fill Credentials in .env

bash
# OpenRouter is the ONLY requirement (No Twitter API needed!)
OPENROUTER_API_KEY=your_openrouter_key_here

# Optional settings
BROWSER=chrome
HEADLESS=false
MAX_FOLLOWING=5000
MAX_FOLLOWERS=5000


### 4. Obtain Credentials

- **OpenRouter API**: [openrouter.ai](https://openrouter.ai/) (Only requirement)

## 🚀 Quick Start

### 🆕 Hybrid System (Recommended)

#### Automatic Execution
bash
python twitter_hybrid_bot.py


#### Extension Setup
1. Open Chrome/Brave and go to `chrome://extensions/`
2. Enable "Developer Mode"
3. Click "Load Unpacked" and select the `extension` folder.
4. Pin the extension to the toolbar.

### 📜 Selenium System (Legacy)

#### Unfollow Non-Followers
bash
python bot.py


#### Analyze User via AI (Command Line)
bash
python analyze.py --username @user


## 🛡️ Protection Logic

The AI analyzes the user's bio and metadata for keywords indicating they are:
- Developers (`dev`, `engineer`, `software`)
- Researchers (`research`, `PhD`, `science`)
- Academics (`professor`, `university`, `academic`)
- Tech professionals (`CTO`, `tech`, `AI`)

These profiles are automatically marked as **IMMUNE** and excluded from unfollowing.

## ⚠️ Important Notes

- **Rate Limits**: The bot respects X limits (approx 15 unfollows/hour).
- **Safety**: Use the AI analysis to avoid burning bridges with valuable connections.
- **Legality**: This bot complies with X's Terms of Service by using browser automation instead of unauthorized API access.

## 🤝 Contributing

Contributions are welcome! Please open an issue or pull request.

## 📜 License

MIT License. Use responsibly.
