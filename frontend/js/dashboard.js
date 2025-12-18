/**
 * CalibraCore Lab - Dashboard Module
 */

document.addEventListener('DOMContentLoaded', () => {
    // Check authentication
    if (!requireAuth()) return;

    // Setup navbar
    setupNavbar();

    // Load dashboard data
    loadDashboard();
    loadEquipments();
    loadLaboratories();

    // Setup filters
    setupFilters();
    setupModalEvents();
});


// Current pagination state
let currentPage = 1;
const perPage = 15;


/**
 * Load dashboard summary
 */
async function loadDashboard() {
    try {
        const resumo = await API.getDashboardResumo();

        document.getElementById('stat-total').textContent = resumo.total;
        document.getElementById('stat-ok').textContent = resumo.em_dia;
        document.getElementById('stat-60').textContent = resumo.vence_60_dias;
        document.getElementById('stat-30').textContent = resumo.vence_30_dias;
        document.getElementById('stat-vencidos').textContent = resumo.vencidos;

        // Reset Alert Classes
        document.querySelector('.stat-card.danger').classList.remove('blink-critical');
        document.querySelector('.stat-card.warning-30').classList.remove('blink-warning');

        // Logic for Critical Alerts (Expired)
        if (resumo.vencidos > 0) {
            document.querySelector('.stat-card.danger').classList.add('blink-critical');

            // Setup Modal Data
            document.getElementById('critical-count').textContent = resumo.vencidos;
            document.getElementById('warning-count').textContent = resumo.vence_30_dias;

            if (resumo.vence_30_dias === 0) {
                document.getElementById('warning-msg').style.display = 'none';
            }

            // Show Modal
            const modal = document.getElementById('modal-critical');
            modal.classList.add('active');

            // Play Sound
            playAlertSound();
        }

        // Logic for Warnings (30 days)
        if (resumo.vence_30_dias > 0) {
            document.querySelector('.stat-card.warning-30').classList.add('blink-warning');
        }

        // Voice Greeting
        const user = await API.getMe();

        // Fetch expiring items for detailed alert if needed
        let expiringItems = [];
        if (resumo.vencidos > 0 || resumo.vence_30_dias > 0) {
            try {
                // Get critical/warning items. 
                // Priority: Vencidos -> Proximo 30
                let statusFilter = 'vencido';
                if (resumo.vencidos === 0 && resumo.vence_30_dias > 0) {
                    statusFilter = 'proximo_30';
                }

                // Fetch top 5 to have enough
                const response = await API.getEquipamentos({
                    status: statusFilter,
                    per_page: 5,
                    page: 1
                });
                expiringItems = response.items || [];
            } catch (e) {
                console.warn('Could not fetch items for voice', e);
            }
        }

        // Small delay to ensure voices are loaded
        setTimeout(() => {
            VoiceService.greetUser(user.nome, resumo, expiringItems);
        }, 1000);

    } catch (error) {
        console.error('Error loading dashboard:', error);
    }
}

function playAlertSound() {
    const audio = document.getElementById('alert-sound');
    if (audio) {
        audio.volume = 0.5;
        audio.play().catch(e => {
            console.warn('Autoplay blocked. Interaction required.', e);
            // Optional: Add a UI indication that sound was blocked if strict policy needed
        });
    }
}

function setupModalEvents() {
    const modal = document.getElementById('modal-critical');
    const closeBtn = document.getElementById('modal-critical-close');
    const resolveBtn = document.getElementById('btn-resolver');

    const closeModal = () => modal.classList.remove('active');

    if (closeBtn) closeBtn.addEventListener('click', closeModal);
    if (resolveBtn) {
        resolveBtn.addEventListener('click', () => {
            closeModal();
            // Scroll to table and filter by expired
            document.getElementById('filter-status').value = 'vencido';
            document.getElementById('filter-status').dispatchEvent(new Event('change'));
            document.querySelector('.table-container').scrollIntoView({ behavior: 'smooth' });
        });
    }
}


/**
 * Load laboratories for filter
 */
async function loadLaboratories() {
    try {
        const labs = await API.getLaboratorios();
        const select = document.getElementById('filter-lab');

        labs.forEach(lab => {
            const option = document.createElement('option');
            option.value = lab;
            option.textContent = lab;
            select.appendChild(option);
        });
    } catch (error) {
        console.error('Error loading laboratories:', error);
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
        const laboratorio = document.getElementById('filter-lab').value;
        const busca = document.getElementById('filter-search').value;

        const params = {
            page: currentPage,
            per_page: perPage
        };

        if (status) params.status = status;
        if (laboratorio) params.laboratorio = laboratorio;
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
        tbody.innerHTML = response.items.map(eq => {
            let rowClass = '';
            if (eq.status === 'vencido') rowClass = 'row-vencido';
            else if (eq.status === 'proximo_30') rowClass = 'row-proximo-30';
            else if (eq.status === 'proximo_60') rowClass = 'row-proximo-60';

            return `
            <tr class="${rowClass}">
                <td><strong>${eq.codigo_interno}</strong></td>
                <td>${eq.categoria || '-'}</td>
                <td>${eq.marca || '-'}</td>
                <td>${eq.numero_certificado || '-'}</td>
                <td>${eq.numero_serie || '-'}</td>
                <td>${Utils.formatDate(eq.data_ultima_calibracao)}</td>
                <td>${Utils.formatDate(eq.data_vencimento)}</td>
                <td>${eq.dias_para_vencer >= 0 ? eq.dias_para_vencer : Math.abs(eq.dias_para_vencer) + ' (atraso)'}</td>
                <td>${Utils.getStatusBadge(eq.status)}</td>
            </tr>
            `;
        }).join('');

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

    // Previous button
    html += `<button class="pagination-btn" ${current === 1 ? 'disabled' : ''} onclick="goToPage(${current - 1})">‹</button>`;

    // Page buttons
    for (let i = 1; i <= total; i++) {
        if (i === 1 || i === total || (i >= current - 1 && i <= current + 1)) {
            html += `<button class="pagination-btn ${i === current ? 'active' : ''}" onclick="goToPage(${i})">${i}</button>`;
        } else if (i === current - 2 || i === current + 2) {
            html += `<span style="color: var(--text-muted);">...</span>`;
        }
    }

    // Next button
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
    const filterLab = document.getElementById('filter-lab');
    const filterSearch = document.getElementById('filter-search');

    filterStatus.addEventListener('change', () => {
        currentPage = 1;
        loadEquipments();
    });

    filterLab.addEventListener('change', () => {
        currentPage = 1;
        loadEquipments();
    });

    // Debounce search input
    filterSearch.addEventListener('input', Utils.debounce(() => {
        currentPage = 1;
        loadEquipments();
    }, 300));
}
