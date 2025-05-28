# config.py

# ✨✨✨✨✨✨✨✨✨✨✨✨✨✨✨✨✨✨✨✨
# ✨   Telegram Mass Inviter V3 Settings File   ✨
# ✨✨✨✨✨✨✨✨✨✨✨✨✨✨✨✨✨✨✨✨

# ==============================================================================
# 🔥🔥🔥🔥🔥🔥🔥 MAIN SETTINGS 🔥🔥🔥🔥🔥🔥🔥
# These parameters must be changed to your own data.
# ==============================================================================

# Get API_ID and API_HASH here: https://my.telegram.org/apps
# You must enter your own data, otherwise the bot won't be able to authorize!
API_ID = 1234567  # <--- YOUR API_ID (example: 1234567)
API_HASH = "" # <--- YOUR API_HASH (example: "abcdef1234567890abcdef1234567890")

# Session name. This is the filename where Pyrogram authorization data will be stored.
# You can use any name, e.g., "my_telegram_session".
SESSION_NAME = "my_account"

# Link to the CSV file with usernames. The file must be accessible via a direct URL.
# Example: "https://example.com/users.csv"
# Each line in the CSV should contain one username (with or without "@").
CSV_URL = ".csv" # <--- REPLACE WITH YOUR URL!

# Link to the chat or channel where users will be invited.
# This can be a public link (e.g., "https://t.me/my_chat")
# or a chat username (e.g., "my_chat").
# Important: The Pyrogram account must be an admin in this chat with the right to invite users.
INVITE_LINK = "TEST" # <--- REPLACE WITH YOUR URL/chat username! example: @yourgroup without @

# ==============================================================================
# ⚙️⚙️⚙️⚙️⚙️⚙️ ADDITIONAL SETTINGS ⚙️⚙️⚙️⚙️⚙️⚙️
# Usually, these don't need to be changed, but can be adjusted as needed.
# ==============================================================================

# Filename for saving progress.
PROGRESS_FILE = "inviter_progress.json"

# Initial delay between invitations in seconds.
# This delay can dynamically increase upon receiving a FloodWait.
INITIAL_DELAY_SECONDS = 15 

# How much to increase the delay (in seconds) upon receiving a FloodWait.
DELAY_INCREMENT_SECONDS = 5

# Maximum possible delay between invitations in seconds.
MAX_DELAY_SECONDS = 60

# Number of users to process in one batch (chunk).
# After processing each batch, the script takes a long pause.
CHUNK_SIZE = 50

# Pause between batches (chunks) in seconds.
# This helps reduce load on the Telegram API and lowers the risk of being blocked.
CHUNK_PAUSE_SECONDS = 300 # 300 seconds = 5 minutes