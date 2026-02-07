"""
Configuration
"""
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Server
    HOST = '0.0.0.0'
    PORT = 5000
    DEBUG = False  # Turn off for production
    USE_SSL = False
    SSL_CERT = 'cert.pem'
    SSL_KEY = 'key.pem'
    
    # API Keys
    GROQ_API_KEY = os.getenv('GROQ_API_KEY')
    
    # CORS - Add your Netlify domain
    ALLOWED_ORIGINS = os.getenv('ALLOWED_ORIGINS', '*')
    
    # AI Settings
    CHAT_MODEL = 'llama-3.1-70b-versatile'
    MAX_HISTORY_MESSAGES = 10
    
    # Search Settings
    MAX_SEARCH_RESULTS = 3
    SCRAPE_TIMEOUT = 10
    MAX_SCRAPE_CHARS = 5000