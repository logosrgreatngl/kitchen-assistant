"""
Kitchen Assistant Flask App
"""
from flask import Flask, jsonify
from flask_cors import CORS
from routes.api import api_bp, init_services
from services import AIService, SearchService, TimerService, MusicService
from config import Config

app = Flask(__name__)

# Update CORS to allow the ngrok header
CORS(app, resources={
    r"/api/*": {
        "origins": Config.ALLOWED_ORIGINS.split(",") if Config.ALLOWED_ORIGINS != '*' else '*',
        "methods": ["GET", "POST", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "ngrok-skip-browser-warning"],  # Added this!
    }
})


# Initialize services
print("🔧 Initializing services...")
ai_service = AIService()
search_service = SearchService()
timer_service = TimerService()
music_service = MusicService()

init_services(ai_service, search_service, timer_service, music_service)
app.register_blueprint(api_bp)

@app.route('/health')
def health():
    return jsonify({'status': 'ok', 'services': 'running'})

@app.route('/')
def index():
    return jsonify({'status': 'Kitchen Assistant API', 'version': '1.0'})

if __name__ == '__main__':
    print(f"""
╔════════════════════════════════════════╗
║   Kitchen Assistant API Server         ║
╠════════════════════════════════════════╣
║  🌐 URL: http://{Config.HOST}:{Config.PORT}         ║
║  🤖 AI: Groq (Llama 3.1)               ║
║  🎵 Music: YouTube (yt-dlp)            ║
║  🔍 Search: Google                     ║
╚════════════════════════════════════════╝
""")
    
    app.run(
        host=Config.HOST,
        port=Config.PORT,
        debug=Config.DEBUG,
    )