const App = {
    step: 0,
    searchParams: { city: '', state: '', country: '' },
    elements: {},
    
    init() {
        // Cache DOM Elements inside init to ensure they exist
        this.elements = {
            chatSection: document.getElementById('chat-section'),
            weatherDisplay: document.getElementById('weather-display'),
            botMessage: document.getElementById('bot-message'),
            userInput: document.getElementById('user-input'),
            chatForm: document.getElementById('chat-form'),
            errorDisplay: document.getElementById('error-display'),
            
            // Weather Fields
            wLocation: document.getElementById('w-location'),
            wDesc: document.getElementById('w-desc'),
            wTemp: document.getElementById('w-temp'),
            wFeelsLike: document.getElementById('w-feels-like'),
            wHumidity: document.getElementById('w-humidity'),
            wWind: document.getElementById('w-wind'),
            searchAgainBtn: document.getElementById('search-again-btn')
        };

        if (this.elements.chatForm) {
            this.elements.chatForm.addEventListener('submit', (e) => {
                e.preventDefault();
                this.handleInput();
            });
        } else {
            console.error("Chat Form not found!");
        }

        if (this.elements.searchAgainBtn) {
            this.elements.searchAgainBtn.addEventListener('click', () => {
                this.resetChat();
            });
        }
        
        // Set Default Background on Load
        this.updateBackground('default');
    },

    handleInput() {
        try {
            const val = this.elements.userInput.value.trim();
            if (!val) return;

            // Clear error
            this.elements.errorDisplay.style.display = 'none';
            this.elements.errorDisplay.textContent = '';
            
            // Store Value
            if (this.step === 0) {
                this.searchParams.city = val;
                this.transitionChat("Got it. Now, which <strong>State/Province</strong> is that in?", "Enter state code (e.g. NY, CA)...");
                this.step++;
            } else if (this.step === 1) {
                this.searchParams.state = val;
                this.transitionChat("Almost there. Finally, which <strong>Country</strong>?", "Enter country code (e.g. US, UK)...");
                this.step++;
            } else if (this.step === 2) {
                this.searchParams.country = val;
                this.elements.userInput.value = '';
                this.elements.userInput.blur();
                this.fetchWeather();
            }
            
            this.elements.userInput.value = '';
        } catch (e) {
            console.error("Input Error:", e);
            this.showError("An unexpected error occurred. Please try again.");
        }
    },

    transitionChat(newMessage, placeholder = "Enter details...") {
        // Simple animation effect
        this.elements.botMessage.style.opacity = '0';
        this.elements.userInput.placeholder = placeholder;
        
        setTimeout(() => {
            this.elements.botMessage.innerHTML = newMessage;
            this.elements.botMessage.style.opacity = '1';
        }, 300);
    },

    async fetchWeather() {
        // Show Loading
        this.elements.botMessage.innerHTML = "Fetching the latest weather data for you...";
        this.elements.chatForm.style.display = 'none';

        const { city, state, country } = this.searchParams;
        const query = `city=${encodeURIComponent(city)}&state=${encodeURIComponent(state)}&country=${encodeURIComponent(country)}`;
        const url = `${window.API_BASE}/api/weather/?${query}`;

        try {
            let response;
            
            if (Auth.needsLogin) {
                // Anonymous Request
                response = await fetch(url);
            } else {
                // Authenticated Request
                response = await Auth.request(url);
            }

            if (response.ok) {
                const data = await response.json();
                this.showWeather(data);
            } else {
                // Handle Errors
                if (response.status === 429) {
                    const data = await response.json();
                    if (Auth.needsLogin) {
                        // Anonymous Throttle -> Warn then Redirect
                        const msg = "You have reached the free limit (5 requests). Redirecting to Login...";
                        this.showError(msg);
                        setTimeout(() => {
                            window.location.href = 'login.html?reason=throttle';
                        }, 3000);
                    } else {
                        // Auth Throttle -> Show Message
                        this.showError(data.detail || "You have reached your request limit. Please try again later.");
                    }
                } else {
                    const data = await response.json();
                    this.showError(data.error || "Could not find weather data. Please try again.");
                }
            }
        } catch (e) {
            console.error(e);
            this.showError("Something went wrong. Please check your connection.");
        }
    },

    showWeather(data) {
        // Hide Chat, Show Weather
        this.elements.chatSection.classList.add('hidden');
        this.elements.weatherDisplay.style.display = 'block';

        // Parse Data (OpenWeatherMap format)
        // Name might be different if from cache or direct
        const name = this.searchParams.city; 
        const country = data.sys ? data.sys.country : this.searchParams.country;
        const temp = Math.round(data.main.temp);
        const desc = data.weather && data.weather[0] ? data.weather[0].description : '';
        const feels_like = Math.round(data.main.feels_like);
        const humidity = data.main.humidity;
        const wind = data.wind.speed;

        this.elements.wLocation.textContent = `${name}, ${country}`;
        this.elements.wDesc.textContent = desc.charAt(0).toUpperCase() + desc.slice(1);
        this.elements.wTemp.textContent = `${temp}°C`;
        this.elements.wFeelsLike.textContent = `${feels_like}°C`;
        this.elements.wHumidity.textContent = `${humidity}%`;
        this.elements.wWind.textContent = `${wind} m/s`;

        // Update Background
        if (data.weather && data.weather[0]) {
            this.updateBackground(data.weather[0].main);
        }
    },

    updateBackground(condition) {
        // GIPHY URLs provided by user
        const gifs = {
            clear: "https://media0.giphy.com/media/v1.Y2lkPTc5MGI3NjExeWxqNGJ4dm43b2lpb2g5aG5xOTlsemJtZ3o4Z2xiZTM1NG9hdHZ4cSZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/0Styincf6K2tvfjb5Q/giphy.gif",
            clouds: "https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExZW42eWsyemR6ZTBxMzF1NW9vN2Y3aGFtZmt3ejRpaHo1MDZxanF3cSZlcD12MV9naWZzX3NlYXJjaCZjdD1n/1TpGKApbHmkZa/giphy.gif",
            rain: "https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExYncwb3JjdmV1aWlmbjF0ZXU4bTIxcGwxbmF3NGJkbzh4dnFmbTBqbCZlcD12MV9naWZzX3NlYXJjaCZjdD1n/t7Qb8655Z1VfBGr5XB/giphy.gif",
            snow: "https://media.giphy.com/media/v1.Y2lkPWVjZjA1ZTQ3eW54amRqem16dmI1aHVtaDlpdTl0cHR1aGtrc3VhN3M4cXhsdGZ0OSZlcD12MV9naWZzX3NlYXJjaCZjdD1n/FoVi0LDjy1XS8/giphy.gif",
            mist: "https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExY3dmdzFra3FyejU1NGFlYWlvcnNndXRhdnF6enVoNzN6MGxhZDFucCZlcD12MV9naWZzX3NlYXJjaCZjdD1n/RI42LtoMA5mxi/giphy.gif",
            thunderstorm: "https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExOGwyMmI4MHcxdHlycm55cG50Zzl5NHRpOW9xMTBvMjRxNDBnNWJqMSZlcD12MV9naWZzX3NlYXJjaCZjdD1n/fAV73wP5H7xN6/giphy.gif",
            default: "https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExNWR4M2w4ZHg2bDlvcjhodnc5M3EyaWhpZmh1dG91b2ljbWR1ZTdxcCZlcD12MV9zdGlja2Vyc19zZWFyY2gmY3Q9cw/r3rHsiozh6noUHmJdq/giphy.gif"
        };
        
        let bgImage = gifs.default;
        const cond = condition.toLowerCase();

        if (cond.includes('clear')) bgImage = gifs.clear;
        else if (cond.includes('cloud')) bgImage = gifs.clouds;
        else if (cond.includes('rain') || cond.includes('drizzle')) bgImage = gifs.rain;
        else if (cond.includes('snow')) bgImage = gifs.snow;
        else if (cond.includes('thunder')) bgImage = gifs.thunderstorm;
        else if (cond.includes('mist') || cond.includes('fog') || cond.includes('haze') || cond.includes('smoke')) bgImage = gifs.mist;

        // Space Theme Gradient (Deep Dark Blue/Black)
        // This replaces the previous colorful gradient
        const gradient = 'radial-gradient(circle at bottom, #1b2735 0%, #090a0f 100%)';
        const body = document.body;
        
        body.style.backgroundImage = `url('${bgImage}'), ${gradient}`;
        // Fix Zoom: GIF gets 'cover', Gradient gets 'cover' too or stretched
        body.style.backgroundSize = "cover, cover"; 
        body.style.backgroundAttachment = "fixed, fixed";
    },

    showError(msg) {
        this.elements.chatForm.style.display = 'flex';
        this.elements.errorDisplay.textContent = msg;
        this.elements.errorDisplay.style.display = 'block';
        this.elements.botMessage.innerHTML = "Oops! Something happened.";
        
        // Reset state slightly to allow retry? or just stay
        // If it was a 429 on auth, we stay.
    },

    resetChat() {
        this.step = 0;
        this.searchParams = { city: '', state: '', country: '' };
        
        this.elements.weatherDisplay.style.display = 'none';
        this.elements.chatSection.classList.remove('hidden');
        this.elements.chatForm.style.display = 'flex';
        this.elements.botMessage.innerHTML = "Hello! Let's check the weather. First, what <strong>City</strong> is it?";
        this.elements.errorDisplay.style.display = 'none';
        this.elements.userInput.focus();
    }
};

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    App.init();
});
