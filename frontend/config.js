const CONFIG = {
    BACKEND_URL: 'http://192.168.10.11:5000',
    
    TIMER_UPDATE_INTERVAL: 1000,
    
    FEATURES: {
        voice: true,
        music: true,
        timers: true,
        search: true
    }
};

CONFIG.API_BASE_URL = CONFIG.BACKEND_URL + '/api';

if (typeof module !== 'undefined' && module.exports) {
    module.exports = CONFIG;
}