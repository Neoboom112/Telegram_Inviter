# utils.py

import json
import os
import csv
import requests
import time
import config # Import our settings file

# --- Progress and CSV Functions ---

def load_progress(progress_file):
    """
    Loads progress from a file.
    If the file exists and is valid, returns its contents.
    In case of an error or missing file, returns initial progress values
    from the settings.
    """
    if os.path.exists(progress_file):
        try:
            with open(progress_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except json.JSONDecodeError as e:
            print(f"⚠️ JSON decode error while loading progress: {e}. The file may be corrupted.")
        except Exception as e:
            print(f"⚠️ Unexpected error while loading progress: {e}")
    # Return initial values if the file is not found or an error occurs
    return {
        'processed': [], # List of users already processed
        'skipped': [],   # List of users already skipped
        'current_delay': config.INITIAL_DELAY_SECONDS, # Initial delay value
        'last_chunk': 0      # Index of the last processed batch
    }

def save_progress(processed, skipped, delay, last_chunk, progress_file):
    """
    Saves the current script progress to a file.
    :param processed: List of all users processed during the session.
    :param skipped: List of all users skipped during the session.
    :param delay: Current delay between invitations.
    :param last_chunk: Number of the last fully processed batch.
    :param progress_file: Path to the progress file.
    """
    progress = {
        'processed': processed,
        'skipped': skipped,
        'current_delay': delay,
        'last_chunk': last_chunk,
        'timestamp': int(time.time()) # Timestamp of the last save
    }
    try:
        with open(progress_file, 'w', encoding='utf-8') as f:
            json.dump(progress, f, indent=4) # Write to JSON with indentation for readability
    except Exception as e:
        print(f"⚠️ Error saving progress: {e}")

def get_usernames_from_csv(csv_url, processed_from_file_set):
    """
    Loads a list of usernames from a CSV file at the specified URL.
    Filters the list, excluding users that have already been processed.
    :param csv_url: URL of the CSV file.
    :param processed_from_file_set: Set of users already processed.
    :return: List of usernames to process.
    """
    try:
        print("🌐 Loading user list from CSV file...")
        if not csv_url or not csv_url.startswith("http"):
            raise ValueError("CSV file URL is not set or is not a valid HTTP link.")
        
        response = requests.get(csv_url)
        response.raise_for_status() # Raises an exception for HTTP errors (4xx, 5xx)
        
        print("🔍 Parsing CSV data...")
        csv_reader = csv.reader(response.text.splitlines())
        all_usernames = []
        
        for row in csv_reader:
            if row: # Check if the row is not empty
                username = row[0].strip().lstrip('@') # Remove spaces and '@' symbol
                if username and username.lower() != "username": # Skip the header row "username"
                    all_usernames.append(username)

        # Filter the list, keeping only those not yet processed
        usernames_to_process = [u for u in all_usernames if u not in processed_from_file_set]
        
        print(f"📊 Total users in CSV: {len(all_usernames)} | Previously processed: {len(processed_from_file_set)} | Remaining to process: {len(usernames_to_process)}")
        return usernames_to_process
        
    except requests.exceptions.RequestException as e:
        print(f"💥 Error loading CSV from URL '{csv_url}': {e}")
        return []
    except ValueError as e:
        print(f"💥 Configuration error: {e}")
        return []
    except Exception as e:
        print(f"💥 Unexpected error while reading CSV: {e}")
        return []