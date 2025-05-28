# main.py

import asyncio
import os
import config # Import settings
import utils # Import utilities
from inviter_core import TelegramInviter # Import our TelegramInviter class

async def main():
    """
    Main function controlling the bot inviter's launch.
    """
    print("\n🚀 BOT LAUNCH 🚀")

    # 1. Load progress from file
    progress = utils.load_progress(config.PROGRESS_FILE)
    
    # 2. Get the list of users to process, considering already processed ones
    # Pass the set of processed users for quick filtering
    usernames_to_process = utils.get_usernames_from_csv(
        config.CSV_URL, 
        set(progress.get('processed', []))
    )
    
    # If the user list is empty, exit
    if not usernames_to_process:
        print("💢 User list is empty or all have been processed. Exiting.")
        if os.path.exists(config.PROGRESS_FILE):
            os.remove(config.PROGRESS_FILE)
            print(f"🗑 Progress file '{config.PROGRESS_FILE}' deleted.")
        return

    # 3. Initialize the inviter with all necessary settings
    inviter = TelegramInviter(
        api_id=config.API_ID,
        api_hash=config.API_HASH,
        session_name=config.SESSION_NAME,
        invite_link=config.INVITE_LINK,
        progress_file=config.PROGRESS_FILE
    )

    # 4. Start the invitation process
    await inviter.run_invitation(
        usernames_to_process,
        progress.get('last_chunk', 0), # Starting batch for resuming
        progress.get('processed', []), # Previously processed users
        progress.get('skipped', [])    # Previously skipped users
    )

    print("\n🎯 JOB COMPLETED 🎯")

if __name__ == "__main__":
    # Run the async main function
    asyncio.run(main())