/**
 * CalibraCore Lab - Equipment Management Module
 */

document.addEventListener('DOMContentLoaded', () => {
    // Check authentication
    if (!requireAuth()) return;

    // Setup navbar
    setupNavbar();

    // Load data
    loadEquipments();
    loadCategorias();

    // Setup event listeners
    setupFilters();
    setupModal();
});


// Current pagination state
let currentPage = 1;
const perPage = 20;
let deleteEquipmentId = null;


/**
 * Load categories for filter dropdown
 */
async function loadCategorias() {
    try {
        const cats = await API.getCategorias();
        const select = document.getElementById('filter-categoria');

        cats.forEach(cat => {
            const option = document.createElement('option');
            option.value = cat;
            option.textContent = cat;
            select.appendChild(option);
        });
    } catch (error) {
        console.error('Error loading categories:', error);
    }
}


/**
 * Load equipment list
 */
async function loadEquipments() {
    const loading = document.getElementById('table-loading');
    const empty = document.getElementById('table-empty');
    const table = document.getElementById('equipment-table');
    const tbody = document.getElementById('equipment-tbody');
    const pagination = document.getElementById('pagination');

    // Show loading
    loading.style.display = 'flex';
    empty.style.display = 'none';
    table.style.display = 'none';
    pagination.style.display = 'none';

    try {
        // Get filter values
        const status = document.getElementById('filter-status').value;
        const categoria = document.getElementById('filter-categoria').value;
        const busca = document.getElementById('filter-search').value;

        const params = {
            page: currentPage,
            per_page: perPage
        };

        if (status) params.status = status;
        if (categoria) params.categoria = categoria;
        if (busca) params.busca = busca;

        const response = await API.getEquipamentos(params);

        // Hide loading
        loading.style.display = 'none';

        if (response.items.length === 0) {
            empty.style.display = 'block';
            return;
        }

        // Show table
        table.style.display = 'table';

        // Build table rows
        tbody.innerHTML = response.items.map(eq => `
            <tr>
                <td><strong>${eq.codigo_interno}</strong></td>
                <td>${eq.categoria || '-'}</td>
                <td>${eq.marca || '-'}</td>
                <td>${eq.numero_certificado || '-'}</td>
                <td>${Utils.formatDate(eq.data_ultima_calibracao)}</td>
                <td>${Utils.formatDate(eq.data_vencimento)}</td>
                <td>${Utils.getStatusBadge(eq.status)}</td>
                <td>
                    <div style="display: flex; gap: 0.5rem;">
                        <button class="btn btn-secondary btn-sm btn-icon" onclick="editEquipment(${eq.id})" title="Editar">
                            ✏️
                        </button>
                        <button class="btn btn-danger btn-sm btn-icon" onclick="confirmDelete(${eq.id}, '${eq.codigo_interno}')" title="Excluir">
                            🗑️
                        </button>
                    </div>
                </td>
            </tr>
        `).join('');

        // Build pagination
        if (response.pages > 1) {
            pagination.style.display = 'flex';
            buildPagination(response.page, response.pages);
        }

    } catch (error) {
        console.error('Error loading equipment:', error);
        loading.style.display = 'none';
        empty.innerHTML = `
            <div class="icon">⚠️</div>
            <h3>Erro ao carregar equipamentos</h3>
            <p>${error.message}</p>
        `;
        empty.style.display = 'block';
    }
}


/**
 * Build pagination controls
 */
function buildPagination(current, total) {
    const pagination = document.getElementById('pagination');
    let html = '';

    html += `<button class="pagination-btn" ${current === 1 ? 'disabled' : ''} onclick="goToPage(${current - 1})">‹</button>`;

    for (let i = 1; i <= total; i++) {
        if (i === 1 || i === total || (i >= current - 1 && i <= current + 1)) {
            html += `<button class="pagination-btn ${i === current ? 'active' : ''}" onclick="goToPage(${i})">${i}</button>`;
        } else if (i === current - 2 || i === current + 2) {
            html += `<span style="color: var(--text-muted);">...</span>`;
        }
    }

    html += `<button class="pagination-btn" ${current === total ? 'disabled' : ''} onclick="goToPage(${current + 1})">›</button>`;

    pagination.innerHTML = html;
}


/**
 * Go to specific page
 */
function goToPage(page) {
    currentPage = page;
    loadEquipments();
}


/**
 * Setup filter event listeners
 */
function setupFilters() {
    const filterStatus = document.getElementById('filter-status');
    const filterCategoria = document.getElementById('filter-categoria');
    const filterSearch = document.getElementById('filter-search');

    filterStatus.addEventListener('change', () => {
        currentPage = 1;
        loadEquipments();
    });

    filterCategoria.addEventListener('change', () => {
        currentPage = 1;
        loadEquipments();
    });

    filterSearch.addEventListener('input', Utils.debounce(() => {
        currentPage = 1;
        loadEquipments();
    }, 300));
}


/**
 * Setup modal functionality
 */
function setupModal() {
    const modal = document.getElementById('modal-equipamento');
    const modalDelete = document.getElementById('modal-delete');
    const btnNovo = document.getElementById('btn-novo');
    const btnClose = document.getElementById('modal-close');
    const btnCancelar = document.getElementById('btn-cancelar');
    const form = document.getElementById('form-equipamento');
    const alertContainer = document.getElementById('alert-container');

    // Open modal for new equipment
    btnNovo.addEventListener('click', () => {
        document.getElementById('modal-title').textContent = 'Novo Equipamento';
        form.reset();
        document.getElementById('eq-id').value = '';
        document.getElementById('eq-laboratorio').value = 'Laboratório';
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

        const id = document.getElementById('eq-id').value;
        const codigo = document.getElementById('eq-codigo').value;
        const categoria = document.getElementById('eq-categoria').value;

        const data = {
            codigo_interno: codigo,
            descricao: document.getElementById('eq-descricao').value || codigo,
            categoria: categoria,
            marca: document.getElementById('eq-marca').value || null,
            numero_certificado: document.getElementById('eq-certificado').value || null,
            laboratorio: document.getElementById('eq-laboratorio').value,
            data_ultima_calibracao: document.getElementById('eq-ultima-cal').value || null,
            data_vencimento: document.getElementById('eq-vencimento').value,
            observacoes: document.getElementById('eq-observacoes').value || null
        };

        try {
            if (id) {
                await API.updateEquipamento(id, data);
                Utils.showAlert(alertContainer, 'Equipamento atualizado com sucesso!', 'success');
            } else {
                await API.createEquipamento(data);
                Utils.showAlert(alertContainer, 'Equipamento cadastrado com sucesso!', 'success');
            }

            closeModal();
            loadEquipments();
            loadCategorias(); // Reload categories in case new one was added
        } catch (error) {
            Utils.showAlert(alertContainer, error.message, 'error');
        }
    });

    // Delete modal
    const closeDeleteModal = () => {
        modalDelete.classList.remove('active');
        deleteEquipmentId = null;
    };

    document.getElementById('modal-delete-close').addEventListener('click', closeDeleteModal);
    document.getElementById('btn-delete-cancelar').addEventListener('click', closeDeleteModal);
    modalDelete.addEventListener('click', (e) => {
        if (e.target === modalDelete) closeDeleteModal();
    });

    document.getElementById('btn-delete-confirmar').addEventListener('click', async () => {
        if (!deleteEquipmentId) return;

        try {
            await API.deleteEquipamento(deleteEquipmentId);
            Utils.showAlert(alertContainer, 'Equipamento desativado com sucesso!', 'success');
            closeDeleteModal();
            loadEquipments();
        } catch (error) {
            Utils.showAlert(alertContainer, error.message, 'error');
        }
    });
}


/**
 * Edit equipment
 */
async function editEquipment(id) {
    try {
        const eq = await API.getEquipamento(id);

        document.getElementById('modal-title').textContent = 'Editar Equipamento';
        document.getElementById('eq-id').value = eq.id;
        document.getElementById('eq-codigo').value = eq.codigo_interno;
        document.getElementById('eq-categoria').value = eq.categoria || '';
        document.getElementById('eq-descricao').value = eq.descricao || '';
        document.getElementById('eq-marca').value = eq.marca || '';
        document.getElementById('eq-certificado').value = eq.numero_certificado || '';
        document.getElementById('eq-ultima-cal').value = eq.data_ultima_calibracao || '';
        document.getElementById('eq-vencimento').value = eq.data_vencimento;
        document.getElementById('eq-laboratorio').value = eq.laboratorio;
        document.getElementById('eq-observacoes').value = eq.observacoes || '';

        document.getElementById('modal-equipamento').classList.add('active');
    } catch (error) {
        Utils.showAlert(document.getElementById('alert-container'), error.message, 'error');
    }
}


/**
 * Confirm delete
 */
function confirmDelete(id, codigo) {
    deleteEquipmentId = id;
    document.getElementById('delete-eq-name').textContent = codigo;
    document.getElementById('modal-delete').classList.add('active');
}
