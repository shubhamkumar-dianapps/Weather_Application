window.API_BASE = 'http://127.0.0.1:8000';

window.Auth = {
    isLoggedIn() {
        return !!localStorage.getItem('access_token');
    },

    getToken() {
        return localStorage.getItem('access_token');
    },

    setTokens(access, refresh) {
        localStorage.setItem('access_token', access);
        localStorage.setItem('refresh_token', refresh);
    },

    clearTokens() {
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        localStorage.removeItem('username');
    },

    async request(url, options = {}) {
        const token = this.getToken();
        options.headers = options.headers || {};

        if (token) {
            options.headers['Authorization'] = `Bearer ${token}`;
        }

        let response = await fetch(url, options);

        if (response.status === 401) {
            this.clearTokens();
            throw new Error('Session expired');
        }

        return response;
    },

    async login(username, password) {
        const res = await fetch(`${API_BASE}/auth/login/`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username, password })
        });

        const data = await res.json();

        if (res.ok) {
            this.setTokens(data.access, data.refresh);
            localStorage.setItem('username', username);
            return { success: true };
        }

        return { success: false, error: data.detail || 'Login failed' };
    },

    async register(username, email, password) {
        const res = await fetch(`${API_BASE}/auth/register/`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username, email, password })
        });

        const data = await res.json();
        if (res.ok) {
            return { success: true };
        }
        return { success: false, error: data.detail || 'Registration failed' };
    },

    logout() {
        this.clearTokens();
        window.location.href = 'login.html';
    },

    updateNavbar() {
        const loginLink = document.getElementById('login-link');
        const logoutBtn = document.getElementById('logout-btn');
        const greeting = document.getElementById('user-greeting');

        if (this.isLoggedIn()) {
            loginLink?.classList.add('hidden');
            logoutBtn?.classList.remove('hidden');

            if (greeting) {
                greeting.textContent = `Hi, ${localStorage.getItem('username')}`;
                greeting.classList.remove('hidden');
            }

            logoutBtn.onclick = () => this.logout();
        } else {
            loginLink?.classList.remove('hidden');
            logoutBtn?.classList.add('hidden');
            greeting?.classList.add('hidden');
        }
    }
};

document.addEventListener('DOMContentLoaded', () => {
    Auth.updateNavbar();
});
