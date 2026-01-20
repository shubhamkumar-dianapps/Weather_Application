

const App = {
    step: 0,
    params: {
        city: '',
        state: '',
        country: ''
    },

    init() {
        this.cacheDOM();
        this.bindEvents();
        if (!this.loadState()) {
            this.updateBackground('homepage');
        }
    },


    cacheDOM() {
        this.chat = document.getElementById('chat-section');
        this.weather = document.getElementById('weather-display');
        this.container = document.getElementById('chat-form');

        this.input = document.getElementById('user-input');
        this.nextBtn = document.getElementById('next-btn');

        this.bot = document.getElementById('bot-message');
        this.error = document.getElementById('error-display');

        this.searchAgainBtn = document.getElementById('search-again-btn');

        this.wLocation = document.getElementById('w-location');
        this.wDesc = document.getElementById('w-desc');
        this.wTemp = document.getElementById('w-temp');
        this.wFeels = document.getElementById('w-feels-like');
        this.wHumidity = document.getElementById('w-humidity');
        this.wWind = document.getElementById('w-wind');

        // New Elements
        this.wHighLow = document.getElementById('w-high-low');
        this.wPressure = document.getElementById('w-pressure');
        this.wVisibility = document.getElementById('w-visibility');
        this.wSunrise = document.getElementById('w-sunrise');
        this.wSunset = document.getElementById('w-sunset');
        this.wClouds = document.getElementById('w-clouds');
        this.wCoords = document.getElementById('w-coords');
    },

    bindEvents() {
        // Button click
        this.nextBtn.addEventListener('click', () => {
            this.handleInput();
        });

        // Enter key (NO FORM)
        this.input.addEventListener('keydown', (e) => {
            if (e.key === 'Enter') {
                e.preventDefault();
                this.handleInput();
            }
        });

        // Reset search
        this.searchAgainBtn.addEventListener('click', () => {
            this.reset();
        });
    },

    handleInput() {
        const value = this.input.value.trim();
        if (!value) return;

        if (this.step === 0) {
            this.params.city = value;
            this.bot.innerHTML = 'Which <strong>State</strong>?';
            this.step++;
        }
        else if (this.step === 1) {
            this.params.state = value;
            this.bot.innerHTML = 'Which <strong>Country</strong>?';
            this.step++;
        }
        else {
            this.params.country = value;
            this.fetchWeather();
        }

        this.input.value = '';
    },

    async fetchWeather() {
        this.container.style.display = 'none';
        this.bot.innerHTML = 'Fetching weather...';

        const { city, state, country } = this.params;
        const url = `${API_BASE}/api/weather/?city=${city}&state=${state}&country=${country}`;

        try {
            const response = Auth.isLoggedIn()
                ? await Auth.request(url)
                : await fetch(url);

            const data = await response.json();

            if (!response.ok) {
                this.showError(data.error || 'Unable to fetch weather');
                return;
            }

            this.renderWeather(data);

        } catch (error) {
            this.showError(error.message);
        }
    },

    renderWeather(data) {
        // Save state on successful render
        this.saveState(data);

        this.chat.style.display = 'none';
        this.weather.style.display = 'block';

        const country = data.sys ? data.sys.country : this.params.country;
        this.wLocation.textContent = `${this.params.city}, ${country}`;

        const desc = data.weather[0].description;
        this.wDesc.textContent = desc.charAt(0).toUpperCase() + desc.slice(1);

        this.wTemp.textContent = `${Math.round(data.main.temp)}°C`;
        this.wFeels.textContent = `${Math.round(data.main.feels_like)}°C`;
        this.wHumidity.textContent = `${data.main.humidity}%`;
        this.wWind.textContent = `${data.wind.speed} m/s`;

        // Render New Data
        this.wHighLow.textContent = `${Math.round(data.main.temp_max)}°C / ${Math.round(data.main.temp_min)}°C`;
        this.wPressure.textContent = `${data.main.pressure} hPa`;
        this.wVisibility.textContent = `${(data.visibility / 1000).toFixed(1)} km`;
        this.wClouds.textContent = `${data.clouds.all}%`;

        this.wSunrise.textContent = this.formatTime(data.sys.sunrise, data.timezone);
        this.wSunset.textContent = this.formatTime(data.sys.sunset, data.timezone);

        this.wCoords.textContent = `Lat: ${data.coord.lat}, Lon: ${data.coord.lon}`;

        // Update Background
        if (data.weather && data.weather[0]) {
            this.updateBackground(data.weather[0].main);
        }
    },

    saveState(data) {
        sessionStorage.setItem('weather_data', JSON.stringify(data));
        sessionStorage.setItem('weather_params', JSON.stringify(this.params));
    },

    loadState() {
        const savedData = sessionStorage.getItem('weather_data');
        const savedParams = sessionStorage.getItem('weather_params');

        if (savedData && savedParams) {
            try {
                this.params = JSON.parse(savedParams);
                const data = JSON.parse(savedData);
                this.renderWeather(data);
                return true;
            } catch (e) {
                console.warn('Failed to load state', e);
                this.clearState();
            }
        }
        return false;
    },

    clearState() {
        sessionStorage.removeItem('weather_data');
        sessionStorage.removeItem('weather_params');
    },

    showError(message) {
        this.error.textContent = message;
        this.error.style.display = 'block';
        this.container.style.display = 'flex';

        // Provide a clear way to retry
        this.bot.innerHTML = `
            <div>Something went wrong.</div>
            <button id="retry-btn" class="send-btn" style="margin-top: 10px; padding: 0.5rem 1rem; font-size: 0.9rem;">Try Again</button>
        `;

        // Bind the retry button
        setTimeout(() => {
            const retryBtn = document.getElementById('retry-btn');
            if (retryBtn) {
                retryBtn.onclick = () => this.reset();
            }
        }, 0);
    },

    reset() {
        this.clearState();
        this.step = 0;
        this.params = { city: '', state: '', country: '' };

        this.weather.style.display = 'none';
        this.chat.style.display = 'block';
        this.container.style.display = 'flex';

        this.bot.innerHTML = 'What <strong>City</strong> are you checking?';
        this.error.style.display = 'none';
        this.input.value = '';

        // Reset background
        this.updateBackground('homepage');
    },

    updateBackground(condition) {
        const body = document.body;
        const gifMap = {
            'homepage': "assets/weather/space.jpg",
            'clear': "https://media0.giphy.com/media/v1.Y2lkPTc5MGI3NjExeWxqNGJ4dm43b2lpb2g5aG5xOTlsemJtZ3o4Z2xiZTM1NG9hdHZ4cSZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/0Styincf6K2tvfjb5Q/giphy.gif",
            'clouds': "https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExZW42eWsyemR6ZTBxMzF1NW9vN2Y3aGFtZmt3ejRpaHo1MDZxanF3cSZlcD12MV9naWZzX3NlYXJjaCZjdD1n/1TpGKApbHmkZa/giphy.gif",
            'rain': "https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExYncwb3JjdmV1aWlmbjF0ZXU4bTIxcGwxbmF3NGJkbzh4dnFmbTBqbCZlcD12MV9naWZzX3NlYXJjaCZjdD1n/t7Qb8655Z1VfBGr5XB/giphy.gif",
            'drizzle': "https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExYncwb3JjdmV1aWlmbjF0ZXU4bTIxcGwxbmF3NGJkbzh4dnFmbTBqbCZlcD12MV9naWZzX3NlYXJjaCZjdD1n/t7Qb8655Z1VfBGr5XB/giphy.gif",
            'snow': "https://media.giphy.com/media/v1.Y2lkPWVjZjA1ZTQ3eW54amRqem16dmI1aHVtaDlpdTl0cHR1aGtrc3VhN3M4cXhsdGZ0OSZlcD12MV9naWZzX3NlYXJjaCZjdD1n/FoVi0LDjy1XS8/giphy.gif",
            'thunderstorm': "https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExOGwyMmI4MHcxdHlycm55cG50Zzl5NHRpOW9xMTBvMjRxNDBnNWJqMSZlcD12MV9naWZzX3NlYXJjaCZjdD1n/fAV73wP5H7xN6/giphy.gif",
            'fog': "https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExY3dmdzFra3FyejU1NGFlYWlvcnNndXRhdnF6enVoNzN6MGxhZDFucCZlcD12MV9naWZzX3NlYXJjaCZjdD1n/RI42LtoMA5mxi/giphy.gif",
            'mist': "https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExY3dmdzFra3FyejU1NGFlYWlvcnNndXRhdnF6enVoNzN6MGxhZDFucCZlcD12MV9naWZzX3NlYXJjaCZjdD1n/RI42LtoMA5mxi/giphy.gif",
            'haze': "https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExY3dmdzFra3FyejU1NGFlYWlvcnNndXRhdnF6enVoNzN6MGxhZDFucCZlcD12MV9naWZzX3NlYXJjaCZjdD1n/RI42LtoMA5mxi/giphy.gif",
            'default': "https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExNWR4M2w4ZHg2bDlvcjhodnc5M3EyaWhpZmh1dG91b2ljbWR1ZTdxcCZlcD12MV9zdGlja2Vyc19zZWFyY2gmY3Q9cw/r3rHsiozh6noUHmJdq/giphy.gif"
        };

        const normalizedCondition = condition.toLowerCase();
        const gifUrl = gifMap[normalizedCondition] || gifMap['default'];

        // Apply background
        body.style.backgroundImage = `url('${gifUrl}')`;
        body.style.backgroundSize = 'cover';
        body.style.backgroundPosition = 'center';
        body.style.backgroundRepeat = 'no-repeat';
        body.style.backgroundAttachment = 'fixed';
    },

    formatTime(unixTimestamp, timezoneOffset) {
        // Create date object in UTC
        const date = new Date((unixTimestamp + timezoneOffset) * 1000);
        // Manual formatting to ensure we show "local" time of the city relative to UTC
        // But simply `new Date(unix * 1000)` gives browser local time. 
        // To show "City Time" we need to handle offset manually if we want absolute correctness, 
        // but typically just converting to locale string is enough if we ignore timezone or use UTC+offset.
        // Let's use a simple HH:MM format ignoring the offset for now to keep it standard per user locale 
        // OR better: use the browser's ability to offset.

        // Actually, easiest way to just show 12hr time:
        const d = new Date(unixTimestamp * 1000);
        return d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    }
};

document.addEventListener('DOMContentLoaded', () => {
    App.init();
});
