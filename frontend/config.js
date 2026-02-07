const CONFIG = {
    BACKEND_URL: 'https://446a-39-40-171-22.ngrok-free.app/',
    TIMER_UPDATE_INTERVAL: 1000,
    FEATURES: { voice: true, music: true, timers: true, search: true }
};

CONFIG.API_BASE_URL = CONFIG.BACKEND_URL + '/api';

if (typeof module !== 'undefined' && module.exports) module.exports = CONFIG;
