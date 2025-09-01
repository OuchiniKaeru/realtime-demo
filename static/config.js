const CONFIG = {
    API_ENDPOINTS: {
        session: 'http://localhost:8888/session',
        weather: 'http://localhost:8888/weather',
        search: 'http://localhost:8888/search',
        // realtime: 'https://api.openai.com/v1/realtime'
        realtime: 'https://swedencentral.realtimeapi-preview.ai.azure.com/v1/realtimertc'
    },
    MODEL: 'gpt-4o-realtime-preview-2024-12-17',
    VOICE: 'echo',
    VOICES: ['alloy', 'ash', 'ballad', 'coral', 'echo', 'sage', 'shimmer', 'verse'],
    INITIAL_MESSAGE: {
        text: 'My name is Geert and I live in Antwerp, Belgium.'
    },
    TOOLS: [], // ツールはtools_config.jsonから動的にロードされる
    WEATHER_ICONS: {
        0: "☀️", // Clear sky
        1: "🌤️", // Mainly clear
        2: "⛅", // Partly cloudy
        3: "☁️", // Overcast
        45: "🌫️", // Foggy
        48: "🌫️", // Depositing rime fog
        51: "🌦️", // Light drizzle
        53: "🌦️", // Moderate drizzle
        55: "🌧️", // Dense drizzle
        61: "🌧️", // Slight rain
        63: "🌧️", // Moderate rain
        65: "🌧️", // Heavy rain
        71: "🌨️", // Slight snow
        73: "🌨️", // Moderate snow
        75: "🌨️", // Heavy snow
        77: "🌨️", // Snow grains
        80: "🌦️", // Slight rain showers
        81: "🌧️", // Moderate rain showers
        82: "🌧️", // Violent rain showers
        85: "🌨️", // Slight snow showers
        86: "🌨️", // Heavy snow showers
        95: "⛈️", // Thunderstorm
        96: "⛈️", // Thunderstorm with slight hail
        99: "⛈️", // Thunderstorm with heavy hail
    },
};

window.CONFIG = CONFIG;

// tools_config.jsonを読み込む関数
async function loadToolsConfig() {
    try {
        const response = await fetch('/tools_config');
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        const config = await response.json();
        
        // CONFIG.TOOLSをクリアしてから再構築
        CONFIG.TOOLS = [];
        
        // ツール定義を動的に追加
        if (config.weather && config.weather.enabled) {
            CONFIG.TOOLS.push({
                type: 'function',
                name: 'get_weather',
                description: 'Get current weather and 7-day forecast for any location on Earth. Includes temperature, humidity, precipitation, and wind speed.',
                parameters: {
                    type: 'object',
                    description: 'The location to get the weather for in English',
                    properties: {
                        location: { 
                            type: 'string',
                            description: 'The city or location name to get weather for'
                        }
                    },
                    required: ['location']
                }
            });
        }
        if (config.search && config.search.enabled) {
            CONFIG.TOOLS.push({
                type: 'function',
                name: 'search_web',
                description: 'Search the web for current information about any topic',
                parameters: {
                    type: 'object',
                    properties: {
                        query: { type: 'string' }
                    },
                    required: ['query']
                }
            });
        }
        console.log('Tools config loaded:', CONFIG.TOOLS);
    } catch (error) {
        console.error('Failed to load tools config:', error);
    }
}

// DOMContentLoadedイベントで設定をロード
document.addEventListener('DOMContentLoaded', loadToolsConfig);
