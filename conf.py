from dotenv import load_dotenv
import os

load_dotenv('env_file')
REDIS_HOST = os.getenv("REDIS_HOST", "0.0.0.0")  
REDIS_PORT = os.getenv("REDIS_PORT", 6379)
API_KEY = os.getenv("API_KEY")
MAX_PROMPT_LENGTH=os.getenv("MAX_PROMPT_LENGTH", 10000)