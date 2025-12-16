/**
 * CalibraCore Lab - Authentication Module
 */

document.addEventListener('DOMContentLoaded', () => {
    const loginForm = document.getElementById('login-form');
    const alertContainer = document.getElementById('alert-container');

    // Check if already logged in - ONLY on login page
    const isLoginPage = window.location.pathname === '/' || window.location.pathname === '/index.html';
    if (isLoginPage && API.isAuthenticated()) {
        window.location.href = '/dashboard';
        return;
    }

    // Handle login form submission
    if (loginForm) {
        loginForm.addEventListener('submit', async (e) => {
            e.preventDefault();

            const email = document.getElementById('email').value;
            const senha = document.getElementById('senha').value;
            const btnText = document.getElementById('btn-text');
            const btnLoading = document.getElementById('btn-loading');
            const btnLogin = document.getElementById('btn-login');

            // Show loading state
            btnText.style.display = 'none';
            btnLoading.style.display = 'inline-block';
            btnLogin.disabled = true;

            try {
                await API.login(email, senha);

                // Success - redirect to dashboard
                window.location.href = '/dashboard';
            } catch (error) {
                Utils.showAlert(alertContainer, error.message, 'error');

                // Reset button
                btnText.style.display = 'inline';
                btnLoading.style.display = 'none';
                btnLogin.disabled = false;
            }
        });
    }
});


/**
 * Require authentication - redirect to login if not authenticated
 */
function requireAuth() {
    if (!API.isAuthenticated()) {
        window.location.href = '/';
        return false;
    }
    return true;
}


/**
 * Require admin role
 */
function requireAdmin() {
    const user = API.getUser();
    if (!user || user.papel !== 'admin') {
        return false;
    }
    return true;
}


/**
 * Setup navbar with user info and logout
 */
function setupNavbar() {
    const user = API.getUser();
    if (!user) return;

    // Update user info in navbar
    const userName = document.getElementById('user-name');
    const userRole = document.getElementById('user-role');

    if (userName) userName.textContent = user.nome;
    if (userRole) userRole.textContent = user.papel === 'admin' ? 'Administrador' : 'Laboratório';

    // Setup logout button
    const logoutBtn = document.getElementById('btn-logout');
    if (logoutBtn) {
        logoutBtn.addEventListener('click', async () => {
            await API.logout();
        });
    }

    // Setup active menu item
    const currentPath = window.location.pathname;
    const menuLinks = document.querySelectorAll('.navbar-link');
    menuLinks.forEach(link => {
        if (link.getAttribute('href') === currentPath) {
            link.classList.add('active');
        }
    });

    // Hide admin-only menus for non-admin users
    if (user.papel !== 'admin') {
        const adminLinks = document.querySelectorAll('[data-admin-only]');
        adminLinks.forEach(el => el.style.display = 'none');
    }
}
