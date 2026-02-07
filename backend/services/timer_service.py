"""
Timer Service — Kitchen Timers
"""
import re
import time
import threading


class TimerService:
    def __init__(self):
        self.timers = []
        self._lock = threading.Lock()
        print("✅ Timer Service initialized")

    def parse_duration(self, text):
        text = text.lower()
        total = 0
        h = re.search(r'(\d+)\s*h', text)
        m = re.search(r'(\d+)\s*m', text)
        s = re.search(r'(\d+)\s*s', text)
        if h:
            total += int(h.group(1)) * 3600
        if m:
            total += int(m.group(1)) * 60
        if s:
            total += int(s.group(1))
        if total == 0:
            nums = re.findall(r'(\d+)', text)
            if nums:
                total = int(nums[0]) * 60
        if total > 0:
            parts = []
            hrs, rem = divmod(total, 3600)
            mins, secs = divmod(rem, 60)
            if hrs:
                parts.append(f"{hrs}h")
            if mins:
                parts.append(f"{mins}m")
            if secs:
                parts.append(f"{secs}s")
            return ' '.join(parts), total
        return None, 0

    def set_timer(self, label, seconds):
        timer_data = {
            'id': len(self.timers) + 1,
            'label': label,
            'seconds': seconds,
            'start_time': time.time(),
            'end_time': time.time() + seconds,
            'active': True,
        }
        with self._lock:
            self.timers.append(timer_data)
        return f"Timer set for {label}"

    def get_active_timers(self):
        now = time.time()
        active = []
        with self._lock:
            for t in self.timers:
                if t['active']:
                    remaining = max(0, t['end_time'] - now)
                    if remaining <= 0:
                        t['active'] = False
                    active.append({
                        'id': t['id'],
                        'label': t['label'],
                        'remaining': int(remaining),
                        'active': t['active'],
                    })
        return active

    def cancel_timer(self, timer_id):
        with self._lock:
            for t in self.timers:
                if t['id'] == timer_id:
                    t['active'] = False
                    return True
        return False