import os
import shutil
from automation.logger import logger

def create_file(file_name):
    try:
        with open(file_name, 'w') as f:
            f.write('')
        logger.info(f"Created file: {file_name}")
        print(f"✅ Created file: {file_name}")
    except Exception as e:
        logger.error(f"Failed to create file: {e}")
        print(f"❌ Error: {e}")

def delete_file(file_name):
    try:
        os.remove(file_name)
        logger.info(f"Deleted file: {file_name}")
        print(f"🗑 Deleted file: {file_name}")
    except Exception as e:
        logger.error(f"Failed to delete file: {e}")
        print(f"❌ Error: {e}")

def move_file(src, dst):
    try:
        shutil.move(src, dst)
        logger.info(f"Moved file from {src} to {dst}")
        print(f"📦 Moved file: {src} → {dst}")
    except Exception as e:
        logger.error(f"Failed to move file: {e}")
        print(f"❌ Error: {e}")