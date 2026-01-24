
import os
from pathlib import Path
from dotenv import load_dotenv

def load_env_file():
    """Find and load .env file from current or parent directories"""
    current = Path(__file__).resolve().parent
    print(f"Starting search from: {current}")
    # Search up to 5 levels up
    for i in range(5):
        env_file = current / ".env"
        print(f"Checking: {env_file}")
        if env_file.exists():
            print(f"Found .env at: {env_file}")
            load_dotenv(env_file)
            return
        current = current.parent

load_env_file()

print(f"AWS_ACCESS_KEY_ID: {os.environ.get('AWS_ACCESS_KEY_ID')}")
print(f"AWS_SECRET_ACCESS_KEY: {os.environ.get('AWS_SECRET_ACCESS_KEY')}")
print(f"AWS_REGION: {os.environ.get('AWS_REGION')}")
print(f"S3_BUCKET_NAME: {os.environ.get('S3_BUCKET_NAME')}")
