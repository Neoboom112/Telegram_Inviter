
# Telegram Mass Inviter Bot 🤖

A powerful Python bot for automatically inviting users to Telegram groups/channels from a CSV list. Handles flood control, preserves progress, and skips already invited users.

## Features ✨

- 📊 Processes users from CSV files (local or URL)
- ⏳ Smart delay system with auto-increase during FloodWait
- 💾 Progress saving/resuming (even after bot restart)
- 🚫 Automatically skips:
  - Already invited users
  - Privacy-restricted accounts
  - Invalid usernames
- 📈 Batch processing with configurable chunk sizes
- 🔒 Secure session storage

## Requirements 📦

```bash
pip install pyrogram requests tgcrypto
```

## Configuration ⚙️

1. Edit `config.py` with your credentials:
```python
API_ID = 12345              # From https://my.telegram.org/apps
API_HASH = "abcdef123456"   # From https://my.telegram.org/apps
SESSION_NAME = "my_account" # Session filename
CSV_URL = "https://example.com/users.csv" # CSV with usernames
INVITE_LINK = "t.me/joinchat/ABC123"     # Target group/channel
```

2. CSV format (one username per line):
```
username1
username2
username3
```

## Usage 🚀

1. First run (will ask for Telegram login):
```bash
python main.py
```

2. For subsequent runs (resumes progress):
```bash
python main.py
```

## Advanced Settings 🛠

Configure in `config.py`:
```python
INITIAL_DELAY_SECONDS = 15   # Start delay between invites
DELAY_INCREMENT_SECONDS = 5  # FloodWait delay increase
MAX_DELAY_SECONDS = 60       # Maximum allowed delay
CHUNK_SIZE = 50              # Users per batch
CHUNK_PAUSE_SECONDS = 300    # Pause between batches (5 mins)
```

## Safety Tips 🔐

1. Start with small batches (CHUNK_SIZE = 10-20)
2. Use higher delays (30+ sec) for aged Telegram accounts
3. Monitor progress in `inviter_progress.json`
4. Bot must be admin with invite permissions

## Troubleshooting 🐛

| Error | Solution |
|-------|----------|
| `ApiIdInvalid` | Verify API_ID/HASH |
| `FloodWait` | Increase delays in config |
| `UserPrivacyRestricted` | These users can't be invited |
| `CSV download failed` | Check URL/Internet connection |

## License 📄
MIT License - Free for personal and commercial use

```

### Key Highlights:
1. **Clear Badges** - Shows Python version and dependencies at a glance
2. **Visual Emojis** - Makes each section easily scannable
3. **Table Format** - For troubleshooting common issues
4. **Safety Tips** - Important for avoiding account restrictions
5. **Configuration Examples** - Ready-to-copy code blocks
