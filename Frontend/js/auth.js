window.API_BASE = 'http://127.0.0.1:8000';

window.Auth = {
    // State
    get needsLogin() {
        return !localStorage.getItem('access_token');
    },

    // API Endpoints
    urls: {
        login: `${window.API_BASE}/auth/login/`,
        refresh: `${window.API_BASE}/auth/token/refresh/`,
        logout: `${window.API_BASE}/auth/logout/`,
        register: `${window.API_BASE}/auth/register/`
    },

    // Login
    async login(username, password) {
        try {
            const response = await fetch(this.urls.login, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ username, password })
            });

            const data = await response.json();

            if (response.ok) {
                this.setTokens(data.access, data.refresh);
                // Try to get user details if returned, or store username
                localStorage.setItem('username', username); 
                return { success: true };
            } else {
                return { success: false, error: data.detail || 'Login failed' };
            }
        } catch (error) {
            return { success: false, error: 'Network error' };
        }
    },

    // Register
    async register(username, email, password) {
        try {
            const response = await fetch(this.urls.register, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ username, email, password })
            });
            
            if (response.ok) {
                return { success: true };
            } else {
                const data = await response.json();
                // Format errors
                const errors = Object.values(data).flat().join(' ');
                return { success: false, error: errors || 'Registration failed' };
            }
        } catch (e) {
            return { success: false, error: 'Network error' };
        }
    },

    // Logout
    async logout() {
        // Optional: Call functionality to blacklist refresh token
        const refresh = localStorage.getItem('refresh_token');
        if (refresh) {
            try {
                await fetch(this.urls.logout, {
                    method: 'POST',
                    headers: { 
                        'Content-Type': 'application/json',
                        'Authorization': `Bearer ${localStorage.getItem('access_token')}`
                    },
                    body: JSON.stringify({ refresh })
                });
            } catch (e) {
                console.warn('Logout API call failed', e);
            }
        }
        
        this.clearTokens();
        window.location.href = 'login.html';
    },

    // Token Management
    setTokens(access, refresh) {
        localStorage.setItem('access_token', access);
        localStorage.setItem('refresh_token', refresh);
    },

    clearTokens() {
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        localStorage.removeItem('username');
    },

    // Authenticated Request Handler (Auto-Refresh)
    async request(url, options = {}) {
        let token = localStorage.getItem('access_token');

        // Add headers
        options.headers = options.headers || {};
        if (token) {
            options.headers['Authorization'] = `Bearer ${token}`;
        }

        let response = await fetch(url, options);

        // Handle 401 (Unauthorized) - Likely expired token
        if (response.status === 401 && token) {
            console.log("Access token expired, attempting refresh...");
            const newAccess = await this.refreshToken();
            
            if (newAccess) {
                // Retry request with new token
                options.headers['Authorization'] = `Bearer ${newAccess}`;
                response = await fetch(url, options);
            } else {
                // Refresh failed, force logout but DON'T REDIRECT silently
                this.clearTokens();
                // window.location.href = 'login.html?expired=1'; // Disabled to prevent refresh loop/confusion
                throw new Error('Session expired');
            }
        }

        return response;
    },

    async refreshToken() {
        const refresh = localStorage.getItem('refresh_token');
        if (!refresh) return null;

        try {
            const response = await fetch(this.urls.refresh, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ refresh })
            });

            if (response.ok) {
                const data = await response.json();
                localStorage.setItem('access_token', data.access);
                return data.access; // Some implementations also rotate refresh token
            }
        } catch (e) {
            console.error('Token refresh failed', e);
        }
        return null;
    },

    // UI Helpers
    checkAuthInUI() {
        const token = localStorage.getItem('access_token');
        const loginLink = document.getElementById('login-link');
        const logoutBtn = document.getElementById('logout-btn');
        const greeting = document.getElementById('user-greeting'); // Optional

        if (token) {
            if(loginLink) loginLink.classList.add('hidden');
            if(logoutBtn) logoutBtn.classList.remove('hidden');
            if(greeting) {
                const user = localStorage.getItem('username');
                if(user) {
                    greeting.textContent = `Hi, ${user}`;
                    greeting.classList.remove('hidden');
                }
            }
            
            // Attach logout handler
            if(logoutBtn) logoutBtn.onclick = () => this.logout();
        } else {
             if(loginLink) loginLink.classList.remove('hidden');
             if(logoutBtn) logoutBtn.classList.add('hidden');
             if(greeting) greeting.classList.add('hidden');
        }
    }
};

// Auto-run UI check on load
document.addEventListener('DOMContentLoaded', () => {
    Auth.checkAuthInUI();
});
