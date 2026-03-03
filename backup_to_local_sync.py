import shutil
import os
import datetime
import glob
import time

# Configuration
SOURCE_DB = "community_app.db"
# Using raw string for Windows path or double backslashes
DEST_FOLDER = r"C:\Users\Terry\Documents\Google Sync Folder"
RETENTION_HOURS = 24

def backup_database():
    # 1. Check if source database exists
    if not os.path.exists(SOURCE_DB):
        print(f"Error: Source database '{SOURCE_DB}' not found.")
        return

    # 2. Check if destination folder exists, create if not
    if not os.path.exists(DEST_FOLDER):
        try:
            os.makedirs(DEST_FOLDER)
            print(f"Created destination folder: {DEST_FOLDER}")
        except OSError as e:
            print(f"Error creating destination folder: {e}")
            return

    # 3. Create timestamped filename
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    dest_filename = f"backup_{timestamp}.db"
    dest_path = os.path.join(DEST_FOLDER, dest_filename)

    # 4. Copy the file
    try:
        shutil.copy2(SOURCE_DB, dest_path)
        print(f"Successfully backed up to: {dest_path}")
    except Exception as e:
        print(f"Error copying file: {e}")
        return

    # 5. Retention Policy: Delete files older than RETENTION_HOURS
    print(f"Checking for backups older than {RETENTION_HOURS} hours...")
    current_time = time.time()
    
    # List all .db files in the destination folder
    # We assume only backup files are .db files we want to manage, 
    # or we could match the pattern "backup_*.db"
    search_pattern = os.path.join(DEST_FOLDER, "backup_*.db")
    files = glob.glob(search_pattern)
    
    deleted_count = 0
    for file_path in files:
        try:
            # Get file modification time
            file_mod_time = os.path.getmtime(file_path)
            file_age_seconds = current_time - file_mod_time
            file_age_hours = file_age_seconds / 3600
            
            if file_age_hours > RETENTION_HOURS:
                os.remove(file_path)
                print(f"Deleted old backup: {os.path.basename(file_path)} ({file_age_hours:.1f} hours old)")
                deleted_count += 1
        except Exception as e:
            print(f"Error processing file {file_path}: {e}")

    if deleted_count == 0:
        print("No old backups found to delete.")
    else:
        print(f"Cleaned up {deleted_count} old backup file(s).")

if __name__ == "__main__":
    print(f"--- Starting Backup Process at {datetime.datetime.now()} ---")
    backup_database()
    print("--- Backup Process Completed ---")
