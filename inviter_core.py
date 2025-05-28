# inviter_core.py
import os
import asyncio
from pyrogram import Client
from pyrogram.errors import (
    PeerIdInvalid, UsernameInvalid, UsernameNotOccupied,
    UserAlreadyParticipant, UserPrivacyRestricted, FloodWait
)
import config # Import settings
import utils # Import utilities

class TelegramInviter:
    def __init__(self, api_id, api_hash, session_name, invite_link, progress_file):
        """
        Initializes the TelegramInviter class.
        All main settings are taken from config.py.
        """
        self.app = Client(session_name, api_id, api_hash)
        self.invite_link = invite_link
        self.progress_file = progress_file
        
        # Delay and chunk size settings from config
        self.current_delay = config.INITIAL_DELAY_SECONDS
        self.delay_increment = config.DELAY_INCREMENT_SECONDS
        self.max_delay = config.MAX_DELAY_SECONDS
        self.chunk_size = config.CHUNK_SIZE
        self.chunk_pause = config.CHUNK_PAUSE_SECONDS

        # Variables for tracking progress within the current session
        self.skipped_users_current_session = [] # Users skipped in the current session
        self.total_processed_users_set = set() # All processed users in history (for saving)

    async def _get_chat_info(self):
        """
        Retrieves information about the target chat and checks the bot's invitation rights.
        :return: Pyrogram chat object.
        :raises ValueError: If INVITE_LINK is not set or the bot lacks permissions.
        """
        print(f"🔗 Connecting to chat: {self.invite_link}")
        if not self.invite_link:
            raise ValueError("Parameter 'INVITE_LINK' is not set.")
        
        chat = await self.app.get_chat(self.invite_link)
        
        me_in_chat = await self.app.get_chat_member(chat.id, "me")
        if not me_in_chat.privileges or not me_in_chat.privileges.can_invite_users:
            raise ValueError("💢 The bot does NOT have permission to invite users to this chat! Check admin settings.")
        
        print(f"✅ Bot successfully connected to chat '{chat.title}' and has invitation rights.")
        return chat

    async def _process_chunk(self, chat, usernames_chunk):
        """
        Processes invitations for one batch of users.
        Attempts to add each user to the chat, handles various errors.
        :param chat: Pyrogram chat object where users will be invited.
        :param usernames_chunk: List of usernames to process in the current batch.
        :return: Tuple: (success_count, skipped_count, failed_count, processed_in_this_chunk_list)
        """
        success = skipped = failed = 0
        processed_in_this_chunk = [] # Users processed in the current batch
        
        for idx, username in enumerate(usernames_chunk, 1):
            try:
                print(f"\n🔹 Processing {idx}/{len(usernames_chunk)}: @{username}")
                
                user = await self.app.get_users(username) # Get user object by username
                
                # Check if the user is already a chat member
                try:
                    member = await self.app.get_chat_member(chat.id, user.id)
                    if member.status in ["member", "administrator", "creator"]:
                        print(f"⏩ @{username} is already in the chat. Skipping.")
                        skipped += 1
                        self.skipped_users_current_session.append(username) # Add to skipped list
                        processed_in_this_chunk.append(username) # Mark as processed
                        continue # Move to the next user
                except Exception:
                    # If get_chat_member failed (e.g., user not found in chat),
                    # it means they're not in the chat, and we can try inviting them.
                    pass 
                
                await self.app.add_chat_members(chat.id, user.id) # Invite user to the chat
                success += 1
                processed_in_this_chunk.append(username) # Mark as successfully processed
                print(f"✅ SUCCESSFULLY invited @{username}")
                
                delay_to_use = self.current_delay 
                print(f"⏳ Waiting {delay_to_use} seconds before the next invitation...")
                await asyncio.sleep(delay_to_use) # Pause before the next action
                
            except FloodWait as e:
                # Handle FloodWait error: Telegram asks to wait for a specified time
                print(f"⚠️ FLOOD WAIT DETECTED! Waiting {e.value} seconds.")
                processed_in_this_chunk.append(username) # User is considered processed to avoid repetition
                await asyncio.sleep(e.value) # Wait for the time specified by Telegram
                self.current_delay = min(self.current_delay + self.delay_increment, self.max_delay) # Increase delay
                print(f"Delay increased to {self.current_delay} seconds.")
                # Progress will be saved after processing the entire batch in run_invitation
            except UserAlreadyParticipant:
                # User is already a chat participant (race condition or recheck)
                print(f"⏭ @{username} is already a chat participant.")
                skipped += 1
                self.skipped_users_current_session.append(username)
                processed_in_this_chunk.append(username)
            except UserPrivacyRestricted:
                # User has privacy restrictions and cannot be invited
                print(f"⏭ @{username} has privacy restrictions. Cannot invite.")
                skipped += 1
                self.skipped_users_current_session.append(username)
                processed_in_this_chunk.append(username)
            except (PeerIdInvalid, UsernameInvalid, UsernameNotOccupied):
                # Username is invalid, user not found, or does not exist
                print(f"❌ @{username}: Invalid user ID / username not found.")
                failed += 1
                processed_in_this_chunk.append(username)
            except Exception as e:
                # Any other unexpected error
                print(f"❌ Unexpected error processing @{username}: {type(e).__name__} - {e}")
                failed += 1
                processed_in_this_chunk.append(username)
        
        return success, skipped, failed, processed_in_this_chunk

    async def run_invitation(self, usernames_to_process, last_chunk_processed, initial_processed_users, initial_skipped_users):
        """
        Starts the main user invitation process.
        :param usernames_to_process: List of usernames to process.
        :param last_chunk_processed: Index of the last processed batch (for resuming).
        :param initial_processed_users: List of users already processed from the progress file.
        :param initial_skipped_users: List of users already skipped from the progress file.
        """
        # Initialize the total set of processed users and skipped list
        # with data from the progress file.
        self.total_processed_users_set.update(initial_processed_users)
        self.skipped_users_current_session.extend(initial_skipped_users)
        self.skipped_users_current_session = list(set(self.skipped_users_current_session)) # Unique values

        async with self.app: # Automatically close the client after completion
            try:
                chat = await self._get_chat_info() # Get chat info and verify bot permissions

                total_chunks = (len(usernames_to_process) + self.chunk_size - 1) // self.chunk_size
                print(f"Starting processing of {len(usernames_to_process)} users in {total_chunks} batches of {self.chunk_size} users each.")

                start_index_for_chunks = last_chunk_processed * self.chunk_size
                
                # Loop through user batches
                for i in range(start_index_for_chunks, len(usernames_to_process), self.chunk_size):
                    chunk = usernames_to_process[i:i+self.chunk_size]
                    current_chunk_number = (i // self.chunk_size) + 1 # Batch numbering starts at 1
                    
                    print(f"\n📦 Processing batch {current_chunk_number}/{total_chunks} (users {i+1}-{min(i+len(chunk), len(usernames_to_process))})")
                    
                    # Start processing invitations for the current batch
                    successes, skips, fails, processed_in_current_chunk = await self._process_chunk(chat, chunk)
                    
                    # Add users processed in this batch to the total set of processed users
                    self.total_processed_users_set.update(processed_in_current_chunk)
                    
                    # Save progress after each batch.
                    # Convert sets to lists for JSON storage.
                    utils.save_progress(
                        list(self.total_processed_users_set), 
                        list(set(self.skipped_users_current_session)), # Ensure skipped users are unique
                        self.current_delay, 
                        current_chunk_number, 
                        self.progress_file
                    )
                    
                    print(f"\n📊 Results for current batch: Successes: {successes}, Skipped: {skips}, Failures: {fails}")

                    # Pause between batches if this is not the last batch
                    if i + self.chunk_size < len(usernames_to_process):
                        print(f"⏸ Batch pause: {self.chunk_pause} seconds ({(self.chunk_pause / 60):.0f} minutes)...")
                        await asyncio.sleep(self.chunk_pause)
                
                print("\n🏁 ALL USERS PROCESSED! 🏁")
                if os.path.exists(self.progress_file):
                    os.remove(self.progress_file)
                    print(f"🗑 Progress file '{self.progress_file}' deleted as the job is complete.")
                    
            except ValueError as e:
                print(f"💥 Configuration or permission error: {e}")
            except Exception as e:
                print(f"💥 FATAL ERROR: {type(e).__name__} - {e}")
            finally:
                # Display the total number of skipped users at the end
                if self.skipped_users_current_session:
                    print(f"\n📝 Total users skipped during the session: {len(set(self.skipped_users_current_session))}")