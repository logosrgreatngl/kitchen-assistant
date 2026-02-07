"""
Music Service — Direct song playback via yt-dlp
Extracts m4a audio URLs (Safari compatible)
"""
import time
import yt_dlp


class MusicService:
    RADIO_STATIONS = {
        'lofi': {
            'name': 'Lofi Hip Hop',
            'url': 'https://stream.zeno.fm/0r0xa792kwzuv',
        },
        'jazz': {
            'name': 'Smooth Jazz',
            'url': 'https://stream.zeno.fm/fyn8eh3h5f8uv',
        },
        'classical': {
            'name': 'Classical Radio',
            'url': 'https://stream.zeno.fm/4d6rh9h0qzzuv',
        },
    }

    def __init__(self):
        self.current_track = None
        self.is_playing = False
        self.queue = []
        self._url_cache = {}
        print("✅ Music Service initialized (yt-dlp)")

    # ------------------------------------------
    # Search & extract
    # ------------------------------------------

    def search_songs(self, query, max_results=5):
        """Search YouTube, return tracks with direct audio URLs."""
        try:
            print(f"🎵 Searching: {query}")
            ydl_opts = {
                'format': 'bestaudio[ext=m4a]/bestaudio/best',
                'noplaylist': True,
                'quiet': True,
                'no_warnings': True,
                'default_search': f'ytsearch{max_results}',
                'extract_flat': False,
            }
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                data = ydl.extract_info(
                    f"ytsearch{max_results}:{query}", download=False
                )

            tracks = []
            if data and 'entries' in data:
                for entry in data['entries']:
                    if entry is None:
                        continue
                    audio_url = self._best_audio_url(entry)
                    if audio_url:
                        vid = entry.get('id', '')
                        track = {
                            'title': entry.get('title', 'Unknown'),
                            'artist': entry.get('uploader', 'Unknown'),
                            'duration': entry.get('duration', 0),
                            'duration_str': self._fmt(entry.get('duration', 0)),
                            'thumbnail': entry.get('thumbnail', ''),
                            'audio_url': audio_url,
                            'video_id': vid,
                        }
                        tracks.append(track)
                        self._url_cache[vid] = {
                            'audio_url': audio_url,
                            'title': track['title'],
                            'expires': time.time() + 18000,
                        }
            print(f"✅ Found {len(tracks)} tracks")
            return tracks
        except Exception as e:
            print(f"❌ Search error: {e}")
            return []

    def get_audio_url(self, video_id):
        """Get (possibly cached) audio URL for a video ID."""
        if video_id in self._url_cache:
            c = self._url_cache[video_id]
            if time.time() < c['expires']:
                return {'status': 'success', **c}

        try:
            ydl_opts = {
                'format': 'bestaudio[ext=m4a]/bestaudio/best',
                'quiet': True,
                'no_warnings': True,
            }
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(
                    f"https://www.youtube.com/watch?v={video_id}",
                    download=False,
                )
            audio_url = self._best_audio_url(info)
            if audio_url:
                self._url_cache[video_id] = {
                    'audio_url': audio_url,
                    'title': info.get('title', ''),
                    'expires': time.time() + 18000,
                }
                return {
                    'status': 'success',
                    'audio_url': audio_url,
                    'title': info.get('title', ''),
                    'duration': info.get('duration', 0),
                }
            return {'status': 'error', 'message': 'No audio found'}
        except Exception as e:
            print(f"❌ Audio URL error: {e}")
            return {'status': 'error', 'message': str(e)}

    # ------------------------------------------
    # Playback helpers
    # ------------------------------------------

    def play_song(self, query):
        tracks = self.search_songs(query, max_results=1)
        if tracks:
            self.current_track = tracks[0]
            self.is_playing = True
            return {'status': 'playing', 'track': tracks[0]}
        return {'status': 'error', 'message': f'Nothing found for: {query}'}

    def add_to_queue(self, query):
        tracks = self.search_songs(query, max_results=1)
        if tracks:
            self.queue.append(tracks[0])
            return {
                'status': 'queued',
                'track': tracks[0],
                'position': len(self.queue),
            }
        return {'status': 'error', 'message': f'Nothing found for: {query}'}

    def skip(self):
        if self.queue:
            self.current_track = self.queue.pop(0)
            self.is_playing = True
            return {'status': 'playing', 'track': self.current_track}
        self.current_track = None
        self.is_playing = False
        return {'status': 'queue_empty'}

    def stop(self):
        self.is_playing = False
        self.current_track = None
        return {'status': 'stopped'}

    def get_queue(self):
        return {
            'queue': self.queue,
            'count': len(self.queue),
            'current': self.current_track,
        }

    def get_stations(self):
        return self.RADIO_STATIONS

    def play_station(self, name):
        name = name.lower()
        if name in self.RADIO_STATIONS:
            s = self.RADIO_STATIONS[name]
            self.current_track = s
            self.is_playing = True
            return {'status': 'playing', 'station': s}
        return {
            'status': 'error',
            'available': list(self.RADIO_STATIONS.keys()),
        }

    def get_status(self):
        return {
            'is_playing': self.is_playing,
            'current_track': self.current_track,
            'queue_length': len(self.queue),
        }

    # ------------------------------------------
    # Internal helpers
    # ------------------------------------------

    @staticmethod
    def _best_audio_url(entry):
        if not entry:
            return None
        if 'url' in entry and entry.get('acodec') != 'none':
            return entry['url']
        if 'formats' in entry:
            # prefer m4a for Safari
            m4a = [
                f for f in entry['formats']
                if f.get('ext') == 'm4a' and f.get('acodec') != 'none'
            ]
            if m4a:
                return m4a[-1]['url']
            audio = [
                f for f in entry['formats']
                if f.get('acodec') != 'none'
            ]
            if audio:
                return audio[-1]['url']
            return entry['formats'][-1].get('url')
        return entry.get('url')

    @staticmethod
    def _fmt(seconds):
        if not seconds:
            return '0:00'
        m, s = divmod(int(seconds), 60)
        h, m = divmod(m, 60)
        return f"{h}:{m:02d}:{s:02d}" if h else f"{m}:{s:02d}"