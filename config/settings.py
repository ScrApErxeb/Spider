from dotenv import load_dotenv
import os

def load_env():
    load_dotenv()

def get(key, default=None):
    return os.getenv(key, default)
