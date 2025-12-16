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
    // Setup event listeners
    setupFilters();
    setupExports();
    setupModal();

    // Global event delegation for delete buttons
    document.addEventListener('click', (e) => {
        const btn = e.target.closest('.btn-delete');
        if (btn) {
            const id = btn.getAttribute('data-id');
            const codigo = btn.getAttribute('data-codigo');
            confirmDelete(id, codigo);
        }
    });
});


// Current pagination state
let currentPage = 1;
const perPage = 20;
// deleteEquipmentId removed to avoid duplication


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

        // Helper to escape simple quotes for the function call
        const escapeStr = (str) => str ? str.replace(/'/g, "\\'").replace(/"/g, '&quot;') : '';

        // Build table rows
        tbody.innerHTML = response.items.map(eq => `
            <tr>
                <td><strong>${eq.codigo_interno}</strong></td>
                <td>${eq.categoria || '-'}</td>
                <td>${eq.marca || '-'}</td>
                <td>
                    ${eq.caminho_certificado ? `
                        <a href="${API.baseUrl}/api/equipamentos/${eq.id}/comprovante" target="_blank" title="Abrir Certificado" style="color: var(--primary-color); text-decoration: underline; font-weight: 500;">
                            ${eq.numero_certificado || 'Ver Arquivo'} 📎
                        </a>
                    ` : (eq.numero_certificado || '-')}
                </td>
                <td>${Utils.formatDate(eq.data_ultima_calibracao)}</td>
                <td>${Utils.formatDate(eq.data_vencimento)}</td>
                <td>${Utils.getStatusBadge(eq.status)}</td>
                <td>
                    <div style="display: flex; gap: 0.5rem;">
                        <button class="btn btn-secondary btn-sm btn-icon" onclick="editEquipment(${eq.id})" title="Editar">
                            ✏️
                        </button>
                        <button class="btn btn-danger btn-sm btn-icon" onclick="window.confirmDelete(${eq.id}, '${escapeStr(eq.codigo_interno)}')" title="Excluir">
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
    const fileStatus = document.getElementById('file-status');
    const linkFile = fileStatus.querySelector('a');

    // Open modal for new equipment
    btnNovo.addEventListener('click', () => {
        document.getElementById('modal-title').textContent = 'Novo Equipamento';
        form.reset();
        document.getElementById('eq-id').value = '';
        document.getElementById('eq-laboratorio').value = 'Laboratório';
        fileStatus.style.display = 'none';
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

    // Button Save Click Handler
    const btnSalvar = document.getElementById('btn-salvar');
    btnSalvar.type = "button"; // Change to normal button to prevent default submit behavior issues

    // Setup Delete Modal Listeners
    if (modalDelete) {
        // Cancel button
        document.getElementById('btn-delete-cancelar').addEventListener('click', () => {
            modalDelete.classList.remove('active');
            deleteEquipmentId = null;
        });

        // Click outside
        modalDelete.addEventListener('click', (e) => {
            if (e.target === modalDelete) {
                modalDelete.classList.remove('active');
                deleteEquipmentId = null;
            }
        });

        // Confirm button (remove old listeners to be safe? actually adding one is fine if init runs once)
        const btnConfirmDelete = document.getElementById('btn-delete-confirmar');
        // Clone to remove old listeners (optional but safer if setupModal runs multiple times, though it shouldn't)
        // For now, standard addEventListener is fine as setupModal is called once per page load.

        btnConfirmDelete.addEventListener('click', async () => {
            if (!deleteEquipmentId) return;

            const originalText = btnConfirmDelete.textContent;

            try {
                btnConfirmDelete.disabled = true;
                btnConfirmDelete.textContent = '...';

                await API.deleteEquipamento(deleteEquipmentId);

                Utils.showAlert(alertContainer, 'Equipamento excluído com sucesso!', 'success');
                modalDelete.classList.remove('active');
                loadEquipments();
            } catch (error) {
                Utils.showAlert(alertContainer, error.message, 'error');
            } finally {
                btnConfirmDelete.disabled = false;
                btnConfirmDelete.textContent = originalText;
                deleteEquipmentId = null;
            }
        });
    }

    btnSalvar.addEventListener('click', async (e) => {
        e.preventDefault();

        if (!form.checkValidity()) {
            form.reportValidity();
            return;
        }

        const id = document.getElementById('eq-id').value;
        const codigo = document.getElementById('eq-codigo').value;
        const categoria = document.getElementById('eq-categoria').value;
        const fileInput = document.getElementById('eq-arquivo-certificado');

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
            // Disable button
            btnSalvar.disabled = true;
            btnSalvar.innerHTML = '<span>⏳ Salvando...</span>';

            let eqId = id;
            if (id) {
                await API.updateEquipamento(id, data);
            } else {
                const newEq = await API.createEquipamento(data);
                eqId = newEq.id;
            }

            // Upload certificate if selected
            if (fileInput.files.length > 0) {
                const file = fileInput.files[0];

                // 50MB limit check
                if (file.size > 52428800) {
                    throw new Error('O arquivo excede o limite de 50MB.');
                }

                await API.uploadCertificado(eqId, file);
                Utils.showAlert(alertContainer, 'Equipamento e certificado salvos!', 'success');
            } else {
                Utils.showAlert(alertContainer, 'Equipamento salvo com sucesso!', 'success');
            }

            closeModal();
            loadEquipments();
            loadCategorias();
        } catch (error) {
            console.error('Save error:', error);
            Utils.showAlert(alertContainer, error.message, 'error');
        } finally {
            btnSalvar.disabled = false;
            btnSalvar.innerHTML = 'Salvar'; // Restore button text (simplified, assuming original was 'Salvar')
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

        // Show current file if exists
        const fileStatus = document.getElementById('file-status');
        const linkFile = fileStatus.querySelector('a');
        if (eq.caminho_certificado) {
            fileStatus.style.display = 'block';
            linkFile.href = `${API.baseUrl}/api/equipamentos/${eq.id}/comprovante`;
        } else {
            fileStatus.style.display = 'none';
        }

        document.getElementById('modal-equipamento').classList.add('active');
    } catch (error) {
        Utils.showAlert(document.getElementById('alert-container'), error.message, 'error');
    }
}


/**
 * Confirm delete
 */
// Global variable for deletion logic
let deleteEquipmentId = null;

// Attach deletion logic to modal buttons once



/**
 * Open Delete Modal
 */
/**
 * Confirm delete (Native Browser Dialog for reliability)
 */
window.confirmDelete = async function (id, codigo) {
    if (confirm('Deseja realmente excluir o registro?')) {
        try {
            await API.deleteEquipamento(id);
            Utils.showAlert(document.getElementById('alert-container'), 'Equipamento excluído com sucesso!', 'success');
            loadEquipments();
        } catch (error) {
            Utils.showAlert(document.getElementById('alert-container'), error.message, 'error');
        }
    }
};


/**
 * Setup export buttons
 */
function setupExports() {
    const btnExcel = document.getElementById('btn-export-excel');
    const btnPdf = document.getElementById('btn-export-pdf');

    if (btnExcel) {
        btnExcel.addEventListener('click', () => downloadReport('excel'));
    }

    if (btnPdf) {
        btnPdf.addEventListener('click', () => downloadReport('pdf'));
    }
}


/**
 * Download report
 */
async function downloadReport(format) {
    const status = document.getElementById('filter-status').value;
    const categoria = document.getElementById('filter-categoria').value;
    const busca = document.getElementById('filter-search').value;
    const alertContainer = document.getElementById('alert-container');

    const params = new URLSearchParams();
    if (status) params.append('status', status);
    if (categoria) params.append('categoria', categoria);
    if (busca) params.append('busca', busca);

    const url = `${API.baseUrl}/api/equipamentos/export/${format}?${params.toString()}`;
    const token = API.getToken();

    let btn; // Declare btn here to be available in catch block

    try {
        btn = document.getElementById(`btn-export-${format}`);
        const originalText = btn.innerHTML;
        // Store original text on button to restore it later if needed, though closure captures it

        btn.innerHTML = '<span>⏳ ...</span>';
        btn.disabled = true;

        const response = await fetch(url, {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });

        if (!response.ok) throw new Error('Falha no download.');

        const blob = await response.blob();
        const downloadUrl = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = downloadUrl;
        a.download = `equipamentos.${format === 'excel' ? 'xlsx' : 'pdf'}`;
        document.body.appendChild(a);
        a.click();
        a.remove();
        window.URL.revokeObjectURL(downloadUrl);

        Utils.showAlert(alertContainer, 'Relatório gerado com sucesso!', 'success');

        btn.innerHTML = originalText;
        btn.disabled = false;
    } catch (error) {
        console.error('Download error:', error);
        Utils.showAlert(alertContainer, 'Erro ao baixar relatório.', 'error');

        if (btn) {
            // Need to restore original text, but it's lost if we didn't save it on the element or rely on closure.
            // Simplified restoration:
            btn.innerHTML = format === 'excel' ? '<span>📊 Excel</span>' : '<span>📄 PDF</span>';
            btn.disabled = false;
        }
    }
}
