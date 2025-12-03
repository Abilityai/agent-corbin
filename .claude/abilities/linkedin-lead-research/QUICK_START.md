# LinkedIn Lead Research Skill - Quick Start

## ✅ Status: Self-Contained & Ready

This skill is **100% self-contained** and can be copied/moved anywhere without any external dependencies.

## 📦 What's Included

```
linkedin-lead-research/
├── .env                  # API key (RAPIDAPI_KEY)
├── .gitignore           # Git ignore rules
├── linkedin_api.py      # Main API wrapper
├── requirements.txt     # Python dependencies
├── setup.sh            # One-command setup script
├── venv/               # Python virtual environment
├── SKILL.md            # Skill definition for Claude
├── README.md           # Full documentation
├── INSTALLATION.md     # Setup guide
└── QUICK_START.md      # This file
```

## 🚀 Quick Test

Test that everything works:

```bash
cd /Users/eugene/Dropbox/Coding/N8N_Main_repos/Corbin20/.claude/skills/linkedin-lead-research

# Test username extraction
./venv/bin/python3 linkedin_api.py extract-username "https://linkedin.com/in/johndoe"

# Test profile fetch (will hit API)
./venv/bin/python3 linkedin_api.py profile eugenevy
```

## 💡 Usage with Claude

Just ask Claude natural language questions:

- "Research this LinkedIn profile: https://linkedin.com/in/jane-smith"
- "Get recent posts for LinkedIn user bob-jones"
- "What's alice-williams current position on LinkedIn?"
- "Is mike-brown active on LinkedIn?"

Claude will automatically invoke this skill!

## 🔑 API Key

Located in `.env` file:
```
RAPIDAPI_KEY=a45f6d315fmsh9421f84897ba7ddp15659fjsn3eb60906b0db
```

To use a different key:
1. Edit `.env` file
2. Update the `RAPIDAPI_KEY` value
3. No restart needed

## 📋 Available Commands

| Command | Example | Description |
|---------|---------|-------------|
| `extract-username` | `extract-username "url"` | Get username from LinkedIn URL |
| `profile` | `profile johndoe` | Basic profile info |
| `activity` | `activity johndoe` | Recent activity timestamp |
| `position` | `position johndoe` | Current job/company |
| `posts` | `posts johndoe 30` | Posts from last N days |
| `comments` | `comments johndoe` | Recent comments |
| `enrich` | `enrich johndoe 30` | Full profile data |

## 🔄 Portability

To move/copy this skill to another system:

1. **Copy entire directory**:
   ```bash
   cp -r linkedin-lead-research /path/to/new/location
   ```

2. **Run setup** (if moving to new machine):
   ```bash
   cd /path/to/new/location/linkedin-lead-research
   ./setup.sh
   ```

That's it! The skill includes:
- ✅ Python virtual environment
- ✅ All dependencies (requests, python-dateutil)
- ✅ API key configuration
- ✅ All Python code

**No external dependencies!**

## 🧪 Test Commands

```bash
# Navigate to skill directory
cd .claude/skills/linkedin-lead-research

# Test extraction
./venv/bin/python3 linkedin_api.py extract-username "https://linkedin.com/in/test"

# Test with your profile
./venv/bin/python3 linkedin_api.py profile eugenevy

# Full enrichment
./venv/bin/python3 linkedin_api.py enrich eugenevy 30
```

## 🐛 Troubleshooting

**"Module not found"**: Run `./setup.sh` to reinstall dependencies

**"API key error"**: Check `.env` file exists and has RAPIDAPI_KEY

**"Empty response"**: Profile may be private or username incorrect

**"Rate limit"**: Wait a few minutes, skill has auto-retry logic

## 📚 More Information

- **Full docs**: See `README.md`
- **Installation**: See `INSTALLATION.md`
- **Skill definition**: See `SKILL.md`

## ✨ That's It!

The skill is fully set up and ready to use. Claude will automatically invoke it when you ask LinkedIn-related questions!
