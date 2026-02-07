"""
API Routes — Chat, Recipes, Timers, Music
"""
import re
from flask import Blueprint, request, jsonify, Response
from datetime import datetime
import requests as http_requests

api_bp = Blueprint('api', __name__, url_prefix='/api')

ai_service = None
search_service = None
timer_service = None
music_service = None


def init_services(ai, search, timer, music):
    global ai_service, search_service, timer_service, music_service
    ai_service = ai
    search_service = search
    timer_service = timer
    music_service = music


# ===================== HEALTH =====================

@api_bp.route('/health', methods=['GET'])
def health():
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
    })


# ===================== CHAT =====================

@api_bp.route('/chat', methods=['POST'])
def chat():
    try:
        data = request.get_json()
        message = data.get('message', '').strip()
        if not message:
            return jsonify({'error': 'No message'}), 400

        result = process_message(message)
        return jsonify({
            'response': result['text'],
            'type': result.get('type', 'general'),
            'data': result.get('data'),
            'timestamp': datetime.now().isoformat(),
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ===================== RECIPE =====================

@api_bp.route('/recipe', methods=['POST'])
def recipe():
    try:
        data = request.get_json()
        ingredients = data.get('ingredients', '').strip()
        if not ingredients:
            return jsonify({'error': 'No ingredients'}), 400

        ctx = search_service.get_context(f"recipe with {ingredients}")
        prompt = f"Suggest 2-3 recipes using: {ingredients}"
        resp = ai_service.chat(prompt, web_context=ctx)
        return jsonify({'response': resp, 'timestamp': datetime.now().isoformat()})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ===================== TIMER =====================

@api_bp.route('/timer', methods=['POST'])
def set_timer():
    try:
        data = request.get_json()
        duration_text = data.get('duration', '').strip()
        if not duration_text:
            return jsonify({'error': 'No duration'}), 400

        label, seconds = timer_service.parse_duration(duration_text)
        if not label:
            return jsonify({'error': 'Invalid duration'}), 400

        msg = timer_service.set_timer(label, seconds)
        return jsonify({
            'response': msg,
            'duration': label,
            'seconds': seconds,
            'timestamp': datetime.now().isoformat(),
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@api_bp.route('/timers', methods=['GET'])
def get_timers():
    try:
        timers = timer_service.get_active_timers()
        return jsonify({'timers': timers, 'count': len(timers)})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@api_bp.route('/timer/<int:timer_id>', methods=['DELETE'])
def cancel_timer(timer_id):
    try:
        ok = timer_service.cancel_timer(timer_id)
        return jsonify({'cancelled': ok})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ===================== ADVICE =====================

@api_bp.route('/advice', methods=['POST'])
def advice():
    try:
        data = request.get_json()
        question = data.get('question', '').strip()
        if not question:
            return jsonify({'error': 'No question'}), 400

        ctx = search_service.get_context(question)
        resp = ai_service.chat(question, web_context=ctx)
        return jsonify({'response': resp, 'timestamp': datetime.now().isoformat()})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ===================== MUSIC =====================

@api_bp.route('/music/search', methods=['POST'])
def search_songs():
    try:
        data = request.get_json()
        query = data.get('query', '').strip()
        if not query:
            return jsonify({'error': 'No query'}), 400
        max_r = data.get('max_results', 5)
        tracks = music_service.search_songs(query, max_r)
        return jsonify({'tracks': tracks, 'query': query})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@api_bp.route('/music/play', methods=['POST'])
def play_song():
    try:
        data = request.get_json()
        query = data.get('query', '').strip()
        if not query:
            return jsonify({'error': 'No query'}), 400
        result = music_service.play_song(query)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@api_bp.route('/music/audio/<video_id>', methods=['GET'])
def get_audio(video_id):
    """Get fresh audio URL for a video."""
    try:
        result = music_service.get_audio_url(video_id)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@api_bp.route('/music/stream/<video_id>', methods=['GET'])
def stream_audio(video_id):
    """
    Proxy audio stream — works on old Safari.
    The browser <audio> element points here.
    """
    try:
        result = music_service.get_audio_url(video_id)
        if result.get('status') != 'success':
            return jsonify({'error': 'Audio not found'}), 404

        headers = {
            'User-Agent': (
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                'AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36'
            )
        }

        range_header = request.headers.get('Range')
        if range_header:
            headers['Range'] = range_header

        r = http_requests.get(
            result['audio_url'], headers=headers, stream=True, timeout=30
        )

        resp_headers = {
            'Content-Type': r.headers.get('Content-Type', 'audio/mp4'),
            'Accept-Ranges': 'bytes',
        }
        if 'Content-Length' in r.headers:
            resp_headers['Content-Length'] = r.headers['Content-Length']
        if 'Content-Range' in r.headers:
            resp_headers['Content-Range'] = r.headers['Content-Range']

        def generate():
            for chunk in r.iter_content(chunk_size=8192):
                yield chunk

        return Response(generate(), status=r.status_code, headers=resp_headers)

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@api_bp.route('/music/queue', methods=['POST'])
def queue_song():
    try:
        data = request.get_json()
        query = data.get('query', '').strip()
        if not query:
            return jsonify({'error': 'No query'}), 400
        result = music_service.add_to_queue(query)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@api_bp.route('/music/queue', methods=['GET'])
def get_queue():
    try:
        return jsonify(music_service.get_queue())
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@api_bp.route('/music/skip', methods=['POST'])
def skip_song():
    try:
        return jsonify(music_service.skip())
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@api_bp.route('/music/stop', methods=['POST'])
def stop_music():
    try:
        return jsonify(music_service.stop())
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@api_bp.route('/music/stations', methods=['GET'])
def get_stations():
    try:
        return jsonify({'stations': music_service.get_stations()})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@api_bp.route('/music/station', methods=['POST'])
def play_station():
    try:
        data = request.get_json()
        name = data.get('station', 'lofi').strip()
        return jsonify(music_service.play_station(name))
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@api_bp.route('/music/status', methods=['GET'])
def music_status():
    try:
        return jsonify(music_service.get_status())
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ===================== MESSAGE ROUTER =====================

def process_message(message):
    msg = message.lower()

    # Play song
    if msg.startswith('play ') and 'radio' not in msg and 'station' not in msg:
        song = message[5:].strip()
        if song:
            result = music_service.play_song(song)
            if result['status'] == 'playing':
                t = result['track']
                return {
                    'text': f"🎵 Now playing: {t['title']} ({t['duration_str']})",
                    'type': 'music_play',
                    'data': result,
                }
            return {'text': f"Couldn't find '{song}'.", 'type': 'error'}

    # Stop
    if any(w in msg for w in ['stop music', 'stop playing']):
        music_service.stop()
        return {'text': '🔇 Music stopped.', 'type': 'music'}

    # Skip
    if msg in ['skip', 'next', 'next song']:
        r = music_service.skip()
        if r['status'] == 'playing':
            return {
                'text': f"⏭️ Now playing: {r['track']['title']}",
                'type': 'music_play',
                'data': r,
            }
        return {'text': '📭 Queue is empty.', 'type': 'music'}

        # Like current song
    if any(w in msg for w in ['like this', 'like song', 'love this', 'add to liked', 'save this song', 'favorite this']):
        if music_service.current_track:
            return {
                'text': f"❤️ Added '{music_service.current_track.get('title', 'Unknown')}' to your liked songs!",
                'type': 'music_like',
                'data': {'track': music_service.current_track},
            }
        return {'text': "No song is currently playing to like.", 'type': 'error'}

    # Unlike / remove from liked
    if any(w in msg for w in ['unlike', 'remove from liked', 'dislike this']):
        if music_service.current_track:
            return {
                'text': f"💔 Removed '{music_service.current_track.get('title', 'Unknown')}' from liked songs.",
                'type': 'music_unlike',
                'data': {'track': music_service.current_track},
            }
        return {'text': "No song is currently playing.", 'type': 'error'}

        # Timer
    if any(w in msg for w in ['timer', 'alarm', 'remind', 'countdown', 'set a', 'set for']):
        label, secs = timer_service.parse_duration(msg)
        if label:
            txt = timer_service.set_timer(label, secs)
            return {
                'text': f"⏲️ {txt}",
                'type': 'timer',
                'data': {'label': label, 'seconds': secs},
            }
        # If no duration found, ask AI but still mark as timer
        return {
            'text': "I couldn't understand the duration. Try saying 'set timer 5 minutes' or 'timer 30 seconds'.",
            'type': 'error',
        }

    # Direct time mentions like "10 minutes", "5 seconds" (without timer keyword)
    time_match = re.search(r'(\d+)\s*(seconds?|secs?|minutes?|mins?|hours?|hrs?)', msg)
    if time_match and any(w in msg for w in ['set', 'start', 'count', 'put']):
        label, secs = timer_service.parse_duration(msg)
        if label:
            txt = timer_service.set_timer(label, secs)
            return {
                'text': f"⏲️ {txt}",
                'type': 'timer',
                'data': {'label': label, 'seconds': secs},
            }

    # Recipe
    if any(w in msg for w in ['recipe', 'cook with', 'make with']):
        ctx = search_service.get_context(f"recipe {message}")
        resp = ai_service.chat(message, web_context=ctx)
        return {'text': resp, 'type': 'recipe'}

    # Cooking questions
    if any(w in msg for w in ['how', 'what', 'why', 'when', 'substitute', 'too much']):
        ctx = search_service.get_context(message)
        resp = ai_service.chat(message, web_context=ctx)
        return {'text': resp, 'type': 'advice'}

    # General
    resp = ai_service.chat(message)
    return {'text': resp, 'type': 'general'}

    