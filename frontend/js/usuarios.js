/**
 * CalibraCore Lab - User Management Module
 */

document.addEventListener('DOMContentLoaded', () => {
    // Check authentication
    if (!requireAuth()) return;

    // Setup navbar
    setupNavbar();

    // Check admin access
    if (!requireAdmin()) {
        document.getElementById('users-container').style.display = 'none';
        document.getElementById('btn-novo').style.display = 'none';
        document.getElementById('access-denied').style.display = 'block';
        return;
    }

    // Load users
    loadUsers();

    // Setup modal
    setupModal();
});


/**
 * Load users list
 */
async function loadUsers() {
    const loading = document.getElementById('table-loading');
    const empty = document.getElementById('table-empty');
    const table = document.getElementById('users-table');
    const tbody = document.getElementById('users-tbody');

    loading.style.display = 'flex';
    empty.style.display = 'none';
    table.style.display = 'none';

    try {
        const users = await API.getUsuarios();

        loading.style.display = 'none';

        if (users.length === 0) {
            empty.style.display = 'block';
            return;
        }

        table.style.display = 'table';

        tbody.innerHTML = users.map(user => `
            <tr>
                <td><strong>${user.nome}</strong></td>
                <td>${user.email}</td>
                <td>
                    <span class="badge ${user.papel === 'admin' ? 'badge-ok' : 'badge-warning-60'}">
                        ${user.papel === 'admin' ? '👑 Admin' : '🔬 Laboratório'}
                    </span>
                </td>
                <td>${user.laboratorio || '-'}</td>
                <td>
                    <span class="badge ${user.ativo ? 'badge-ok' : 'badge-danger'}">
                        ${user.ativo ? '✓ Ativo' : '✕ Inativo'}
                    </span>
                </td>
                <td>
                    <div style="display: flex; gap: 0.5rem;">
                        <button class="btn btn-secondary btn-sm btn-icon" onclick="editUser(${user.id})" title="Editar">
                            ✏️
                        </button>
                        <button class="btn btn-danger btn-sm btn-icon" onclick="toggleUserStatus(${user.id}, ${user.ativo})" title="${user.ativo ? 'Desativar' : 'Ativar'}">
                            ${user.ativo ? '🔒' : '🔓'}
                        </button>
                    </div>
                </td>
            </tr>
        `).join('');

    } catch (error) {
        loading.style.display = 'none';
        empty.innerHTML = `
            <div class="icon">⚠️</div>
            <h3>Erro ao carregar usuários</h3>
            <p>${error.message}</p>
        `;
        empty.style.display = 'block';
    }
}


/**
 * Setup modal functionality
 */
function setupModal() {
    const modal = document.getElementById('modal-usuario');
    const btnNovo = document.getElementById('btn-novo');
    const btnClose = document.getElementById('modal-close');
    const btnCancelar = document.getElementById('btn-cancelar');
    const form = document.getElementById('form-usuario');
    const alertContainer = document.getElementById('alert-container');

    // Open modal for new user
    btnNovo.addEventListener('click', () => {
        document.getElementById('modal-title').textContent = 'Novo Usuário';
        form.reset();
        document.getElementById('user-id').value = '';
        document.getElementById('user-senha').required = true;
        document.getElementById('senha-hint').textContent = '*';
        document.getElementById('senha-edit-hint').style.display = 'none';
        modal.classList.add('active');
    });

    // Close modal
    const closeModal = () => {
        modal.classList.remove('active');
    };

    btnClose.addEventListener('click', closeModal);
    btnCancelar.addEventListener('click', closeModal);
    modal.addEventListener('click', (e) => {
        if (e.target === modal) closeModal();
    });

    // Form submission
    form.addEventListener('submit', async (e) => {
        e.preventDefault();

        const id = document.getElementById('user-id').value;
        const data = {
            nome: document.getElementById('user-nome').value,
            email: document.getElementById('user-email').value,
            papel: document.getElementById('user-papel').value,
            laboratorio: document.getElementById('user-laboratorio').value || null
        };

        const senha = document.getElementById('user-senha').value;
        if (senha) {
            data.senha = senha;
        }

        try {
            if (id) {
                await API.updateUsuario(id, data);
                Utils.showAlert(alertContainer, 'Usuário atualizado com sucesso!', 'success');
            } else {
                await API.createUsuario(data);
                Utils.showAlert(alertContainer, 'Usuário criado com sucesso!', 'success');
            }

            closeModal();
            loadUsers();
        } catch (error) {
            Utils.showAlert(alertContainer, error.message, 'error');
        }
    });
}


/**
 * Edit user
 */
async function editUser(id) {
    try {
        const user = await API.getUsuario(id);

        document.getElementById('modal-title').textContent = 'Editar Usuário';
        document.getElementById('user-id').value = user.id;
        document.getElementById('user-nome').value = user.nome;
        document.getElementById('user-email').value = user.email;
        document.getElementById('user-papel').value = user.papel;
        document.getElementById('user-laboratorio').value = user.laboratorio || '';
        document.getElementById('user-senha').value = '';
        document.getElementById('user-senha').required = false;
        document.getElementById('senha-hint').textContent = '';
        document.getElementById('senha-edit-hint').style.display = 'block';

        document.getElementById('modal-usuario').classList.add('active');
    } catch (error) {
        Utils.showAlert(document.getElementById('alert-container'), error.message, 'error');
    }
}


/**
 * Toggle user status (activate/deactivate)
 */
async function toggleUserStatus(id, currentStatus) {
    const action = currentStatus ? 'desativar' : 'ativar';

    if (!confirm(`Tem certeza que deseja ${action} este usuário?`)) {
        return;
    }

    try {
        if (currentStatus) {
            await API.deleteUsuario(id);
            Utils.showAlert(document.getElementById('alert-container'), 'Usuário desativado!', 'success');
        } else {
            await API.updateUsuario(id, { ativo: true });
            Utils.showAlert(document.getElementById('alert-container'), 'Usuário ativado!', 'success');
        }
        loadUsers();
    } catch (error) {
        Utils.showAlert(document.getElementById('alert-container'), error.message, 'error');
    }
}
