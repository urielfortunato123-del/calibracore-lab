/**
 * CalibraCore Lab - API Communication Module
 */

const API = {
    baseUrl: window.location.origin,

    /**
     * Get stored auth token
     */
    getToken() {
        return localStorage.getItem('calibracore_token');
    },

    /**
     * Set auth token
     */
    setToken(token) {
        localStorage.setItem('calibracore_token', token);
    },

    /**
     * Clear auth token
     */
    clearToken() {
        localStorage.removeItem('calibracore_token');
        localStorage.removeItem('calibracore_user');
    },

    /**
     * Get stored user
     */
    getUser() {
        const user = localStorage.getItem('calibracore_user');
        return user ? JSON.parse(user) : null;
    },

    /**
     * Set user data
     */
    setUser(user) {
        localStorage.setItem('calibracore_user', JSON.stringify(user));
    },

    /**
     * Check if user is authenticated
     */
    isAuthenticated() {
        return !!this.getToken();
    },

    /**
     * Make API request
     */
    async request(endpoint, options = {}) {
        const url = `${this.baseUrl}${endpoint}`;
        const token = this.getToken();

        const headers = {
            'Content-Type': 'application/json',
            ...options.headers
        };

        if (token) {
            headers['Authorization'] = `Bearer ${token}`;
        }

        try {
            const response = await fetch(url, {
                ...options,
                headers
            });

            // Handle 401 Unauthorized
            if (response.status === 401) {
                this.clearToken();
                window.location.href = '/';
                throw new Error('Sessão expirada');
            }

            // Parse response
            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.detail || 'Erro na requisição');
            }

            return data;
        } catch (error) {
            console.error('API Error:', error);
            throw error;
        }
    },

    /**
     * Login
     */
    async login(email, senha) {
        // Use form data for OAuth2 compatibility
        const formData = new URLSearchParams();
        formData.append('username', email);
        formData.append('password', senha);

        const response = await fetch(`${this.baseUrl}/api/auth/login`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded'
            },
            body: formData
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.detail || 'E-mail ou senha incorretos');
        }

        this.setToken(data.access_token);

        // Fetch user data
        const user = await this.request('/api/auth/me');
        this.setUser(user);

        return user;
    },

    /**
     * Logout
     */
    async logout() {
        try {
            await this.request('/api/auth/logout', { method: 'POST' });
        } catch (e) {
            // Ignore errors on logout
        }
        this.clearToken();
        window.location.href = '/';
    },

    /**
     * Get current user
     */
    async getMe() {
        return this.request('/api/auth/me');
    },

    // ============= Dashboard =============

    async getDashboardResumo() {
        return this.request('/api/dashboard/resumo');
    },

    async getLabsStats() {
        return this.request('/api/dashboard/laboratorios-stats');
    },

    // ============= Equipamentos =============

    async getEquipamentos(params = {}) {
        const query = new URLSearchParams(params).toString();
        return this.request(`/api/equipamentos${query ? '?' + query : ''}`);
    },

    async getEquipamento(id) {
        return this.request(`/api/equipamentos/${id}`);
    },

    async createEquipamento(data) {
        return this.request('/api/equipamentos', {
            method: 'POST',
            body: JSON.stringify(data)
        });
    },

    async updateEquipamento(id, data) {
        return this.request(`/api/equipamentos/${id}`, {
            method: 'PUT',
            body: JSON.stringify(data)
        });
    },

    async deleteEquipamento(id) {
        return this.request(`/api/equipamentos/${id}`, {
            method: 'DELETE'
        });
    },

    async getLaboratorios() {
        return this.request('/api/equipamentos/laboratorios');
    },

    async getCategorias() {
        return this.request('/api/equipamentos/categorias');
    },

    // ============= Usuários =============

    async getUsuarios(params = {}) {
        const query = new URLSearchParams(params).toString();
        return this.request(`/api/usuarios${query ? '?' + query : ''}`);
    },

    async getUsuario(id) {
        return this.request(`/api/usuarios/${id}`);
    },

    async createUsuario(data) {
        return this.request('/api/usuarios', {
            method: 'POST',
            body: JSON.stringify(data)
        });
    },

    async updateUsuario(id, data) {
        return this.request(`/api/usuarios/${id}`, {
            method: 'PUT',
            body: JSON.stringify(data)
        });
    },

    async deleteUsuario(id) {
        return this.request(`/api/usuarios/${id}`, {
            method: 'DELETE'
        });
    },

    // ============= Alertas =============

    async processarAlertas() {
        return this.request('/api/alertas/processar', {
            method: 'POST'
        });
    },

    async getHistoricoAlertas(params = {}) {
        const query = new URLSearchParams(params).toString();
        return this.request(`/api/alertas/historico${query ? '?' + query : ''}`);
    }
};


/**
 * Utility functions
 */
const Utils = {
    /**
     * Format date to DD/MM/YYYY
     */
    formatDate(dateStr) {
        if (!dateStr) return '-';
        const date = new Date(dateStr);
        return date.toLocaleDateString('pt-BR');
    },

    /**
     * Format datetime to DD/MM/YYYY HH:mm
     */
    formatDateTime(dateStr) {
        if (!dateStr) return '-';
        const date = new Date(dateStr);
        return date.toLocaleString('pt-BR');
    },

    /**
     * Get status badge HTML
     */
    getStatusBadge(status) {
        const statusMap = {
            'em_dia': { class: 'badge-ok', text: '✓ Em dia' },
            'proximo_60': { class: 'badge-warning-60', text: '⚠ 60 dias' },
            'proximo_30': { class: 'badge-warning-30', text: '⚠ 30 dias' },
            'vencido': { class: 'badge-danger', text: '✕ Vencido' }
        };
        const info = statusMap[status] || { class: '', text: status };
        return `<span class="badge ${info.class}">${info.text}</span>`;
    },

    /**
     * Show alert message
     */
    showAlert(container, message, type = 'error') {
        const alertEl = document.createElement('div');
        alertEl.className = `alert alert-${type}`;
        alertEl.innerHTML = `
            <span>${type === 'success' ? '✓' : type === 'warning' ? '⚠' : '✕'}</span>
            <span>${message}</span>
        `;
        container.innerHTML = '';
        container.appendChild(alertEl);

        // Auto-remove after 5 seconds
        setTimeout(() => {
            alertEl.remove();
        }, 5000);
    },

    /**
     * Debounce function
     */
    debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    }
};
