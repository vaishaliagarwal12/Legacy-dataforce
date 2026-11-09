/**
 * Legacy DataForce - Clean Light Frontend Interactions
 * Handles sidebar toggles, delete confirmation modals, dynamic form validation with disabled buttons on save,
 * client-side table pagination and instant search, and Chart.js (strictly with NO animations).
 */

document.addEventListener('DOMContentLoaded', () => {
    // -------------------------------------------------------------------------
    // 1. Mobile Sidebar Toggle & Backdrop
    // -------------------------------------------------------------------------
    const sidebarToggle = document.getElementById('sidebarToggle');
    const appSidebar = document.getElementById('appSidebar');
    const sidebarBackdrop = document.getElementById('sidebarBackdrop');

    function closeSidebar() {
        if (appSidebar) appSidebar.classList.remove('show');
        if (sidebarBackdrop) sidebarBackdrop.classList.remove('show');
    }

    if (sidebarToggle && appSidebar) {
        sidebarToggle.addEventListener('click', () => {
            appSidebar.classList.toggle('show');
            if (sidebarBackdrop) sidebarBackdrop.classList.toggle('show');
        });
    }

    if (sidebarBackdrop) {
        sidebarBackdrop.addEventListener('click', closeSidebar);
    }

    // Close mobile sidebar when clicking a menu link
    const menuLinks = document.querySelectorAll('.menu-link');
    menuLinks.forEach(link => {
        link.addEventListener('click', () => {
            if (window.innerWidth < 992) {
                closeSidebar();
            }
        });
    });

    // Close sidebar or modals on Escape key
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape') {
            closeSidebar();
        }
    });

    // -------------------------------------------------------------------------
    // 2. Initialize Bootstrap Toasts & Auto-dismiss Flash Alerts
    // -------------------------------------------------------------------------
    const toastEls = document.querySelectorAll('.toast');
    toastEls.forEach(el => {
        try {
            const t = bootstrap.Toast.getOrCreateInstance(el);
            t.show();
        } catch (err) {
            console.error('Toast initialization error', err);
        }
    });

    const flashAlerts = document.querySelectorAll('.flash-alert');
    flashAlerts.forEach(alert => {
        setTimeout(() => {
            const bsAlert = bootstrap.Alert.getOrCreateInstance(alert);
            if (bsAlert) bsAlert.close();
        }, 6000);
    });

    // -------------------------------------------------------------------------
    // 2b. Live Asynchronous Database Health Verification
    // -------------------------------------------------------------------------
    const dbBadge = document.getElementById('dbHealthBadge');
    if (dbBadge) {
        fetch('/health', { headers: { 'Accept': 'application/json' }, cache: 'no-store' })
            .then(res => res.json())
            .then(data => {
                if (data && data.status === 'healthy' && data.database && data.database.connection === 'connected') {
                    dbBadge.className = 'badge badge-status-success px-2 py-1';
                    dbBadge.innerHTML = '<i class="bi bi-circle-fill text-success" style="font-size: 0.5rem; vertical-align: middle;"></i> MySQL Connected';
                    dbBadge.title = `MySQL ${data.database.version || '8.0'} Active (${data.database.active_database || 'Connected'})`;
                } else {
                    dbBadge.className = 'badge badge-status-danger px-2 py-1';
                    dbBadge.innerHTML = '<i class="bi bi-circle-fill text-danger" style="font-size: 0.5rem; vertical-align: middle;"></i> MySQL Disconnected';
                    dbBadge.title = 'MySQL Service Unavailable (Port 3306)';
                }
            })
            .catch(() => {
                dbBadge.className = 'badge badge-status-danger px-2 py-1';
                dbBadge.innerHTML = '<i class="bi bi-circle-fill text-danger" style="font-size: 0.5rem; vertical-align: middle;"></i> MySQL Disconnected';
                dbBadge.title = 'MySQL Connection Unreachable';
            });
    }

    // -------------------------------------------------------------------------
    // 3. Universal Delete Confirmation Modal
    // -------------------------------------------------------------------------
    const deleteModal = document.getElementById('deleteConfirmModal');
    if (deleteModal) {
        deleteModal.addEventListener('show.bs.modal', (event) => {
            const button = event.relatedTarget;
            if (!button) return;

            const deleteUrl = button.getAttribute('data-delete-url');
            const itemName = button.getAttribute('data-item-name') || 'this item';
            const extraWarning = button.getAttribute('data-warning') || '';

            const form = deleteModal.querySelector('#deleteConfirmForm');
            const nameSpan = deleteModal.querySelector('#deleteItemName');
            const warningP = deleteModal.querySelector('#deleteExtraWarning');
            const submitBtn = form ? form.querySelector('button[type="submit"]') : null;

            if (form && deleteUrl) {
                form.action = deleteUrl;
            }
            if (nameSpan) {
                nameSpan.textContent = itemName;
            }
            if (warningP) {
                if (extraWarning) {
                    warningP.textContent = extraWarning;
                    warningP.classList.remove('d-none');
                } else {
                    warningP.textContent = '';
                    warningP.classList.add('d-none');
                }
            }
            if (submitBtn) {
                submitBtn.disabled = false;
                submitBtn.innerHTML = '<i class="bi bi-trash3 me-1"></i> Delete Record';
            }
        });
    }

    // -------------------------------------------------------------------------
    // 4. Form Validation & Disabled Buttons While Saving
    // -------------------------------------------------------------------------
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', event => {
            // Check native HTML5 validity if requested
            if (form.classList.contains('needs-validation')) {
                if (!form.checkValidity()) {
                    event.preventDefault();
                    event.stopPropagation();
                    form.classList.add('was-validated');
                    return;
                }
                form.classList.add('was-validated');
            }

            // If valid, disable submit button and show saving indicator for POST/destructive forms
            const isGetMethod = form.getAttribute('method') && form.getAttribute('method').toLowerCase() === 'get';
            const submitBtn = form.querySelector('button[type="submit"]');
            if (submitBtn && !submitBtn.disabled && !isGetMethod) {
                submitBtn.disabled = true;
                const originalHtml = submitBtn.innerHTML;
                submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-1" role="status" aria-hidden="true"></span> Saving...';
                
                // Safety re-enable timeout if server response takes long or fails without page refresh
                setTimeout(() => {
                    if (submitBtn) {
                        submitBtn.disabled = false;
                        submitBtn.innerHTML = originalHtml;
                    }
                }, 8000);
            }
        });
    });

    // -------------------------------------------------------------------------
    // 5. Internship Form Dynamic Switcher (Mandatory vs Additional)
    // -------------------------------------------------------------------------
    const internshipTypeSelect = document.getElementById('internship_type_select');
    const requirementGroup = document.getElementById('requirement_group');
    const requirementSelect = document.getElementById('requirement_id_select');
    const internshipNoInput = document.getElementById('internship_no_input');

    if (internshipTypeSelect && requirementGroup && requirementSelect) {
        function updateInternshipFields() {
            const isMandatory = internshipTypeSelect.value === 'Mandatory';
            if (isMandatory) {
                requirementGroup.style.display = 'block';
                requirementSelect.required = true;
                requirementSelect.disabled = false;
                const selectedOpt = requirementSelect.options[requirementSelect.selectedIndex];
                if (selectedOpt && selectedOpt.dataset.reqNo && internshipNoInput) {
                    internshipNoInput.value = selectedOpt.dataset.reqNo;
                }
            } else {
                requirementGroup.style.display = 'none';
                requirementSelect.required = false;
                requirementSelect.disabled = true;
                requirementSelect.value = '';
                if (internshipNoInput && (!internshipNoInput.value || internshipNoInput.value <= 2)) {
                    internshipNoInput.value = '3';
                }
            }
        }

        internshipTypeSelect.addEventListener('change', updateInternshipFields);
        requirementSelect.addEventListener('change', () => {
            const selectedOpt = requirementSelect.options[requirementSelect.selectedIndex];
            if (selectedOpt && selectedOpt.dataset.reqNo && internshipNoInput) {
                internshipNoInput.value = selectedOpt.dataset.reqNo;
            }
        });
        updateInternshipFields();
    }

    // -------------------------------------------------------------------------
    // 6. Client-Side Table Pagination & Live Search Filter
    // -------------------------------------------------------------------------
    function initPaginatedTable(tableWrapper) {
        const table = tableWrapper.querySelector('table');
        if (!table) return;

        const tbody = table.querySelector('tbody');
        if (!tbody) return;

        const allRows = Array.from(tbody.querySelectorAll('tr:not(.no-filter)'));
        if (allRows.length === 0) return;

        const pageSize = parseInt(tableWrapper.getAttribute('data-page-size') || '10', 10);
        let currentPage = 1;
        let visibleRows = [...allRows];

        // Search input connector
        const searchInputId = tableWrapper.getAttribute('data-search-input');
        const searchInput = searchInputId ? document.getElementById(searchInputId) : null;

        // Create pagination footer if not already present
        let footer = tableWrapper.querySelector('.table-pagination-footer');
        if (!footer) {
            footer = document.createElement('div');
            footer.className = 'table-pagination-footer';
            tableWrapper.appendChild(footer);
        }

        function render() {
            const total = visibleRows.length;
            const totalPages = Math.max(1, Math.ceil(total / pageSize));
            if (currentPage > totalPages) currentPage = totalPages;
            if (currentPage < 1) currentPage = 1;

            const startIdx = (currentPage - 1) * pageSize;
            const endIdx = startIdx + pageSize;

            // Hide/show rows
            allRows.forEach(row => { row.style.display = 'none'; });
            visibleRows.forEach((row, idx) => {
                if (idx >= startIdx && idx < endIdx) {
                    row.style.display = '';
                }
            });

            // Footer content
            const showingStart = total === 0 ? 0 : startIdx + 1;
            const showingEnd = Math.min(total, endIdx);

            let paginationButtons = '';
            for (let i = 1; i <= totalPages; i++) {
                if (totalPages <= 7 || i === 1 || i === totalPages || (i >= currentPage - 1 && i <= currentPage + 1)) {
                    paginationButtons += `
                        <li class="page-item ${i === currentPage ? 'active' : ''}">
                            <button type="button" class="page-link" data-page="${i}">${i}</button>
                        </li>
                    `;
                } else if (i === currentPage - 2 || i === currentPage + 2) {
                    paginationButtons += `<li class="page-item disabled"><span class="page-link">...</span></li>`;
                }
            }

            footer.innerHTML = `
                <div>Showing <strong>${showingStart}-${showingEnd}</strong> of <strong>${total}</strong> records</div>
                <nav aria-label="Table pagination">
                    <ul class="pagination pagination-sm">
                        <li class="page-item ${currentPage === 1 ? 'disabled' : ''}">
                            <button type="button" class="page-link" data-page="${currentPage - 1}" aria-label="Previous">
                                <i class="bi bi-chevron-left"></i>
                            </button>
                        </li>
                        ${paginationButtons}
                        <li class="page-item ${currentPage === totalPages || total === 0 ? 'disabled' : ''}">
                            <button type="button" class="page-link" data-page="${currentPage + 1}" aria-label="Next">
                                <i class="bi bi-chevron-right"></i>
                            </button>
                        </li>
                    </ul>
                </nav>
            `;

            // Attach events
            footer.querySelectorAll('button[data-page]').forEach(btn => {
                btn.addEventListener('click', () => {
                    const page = parseInt(btn.getAttribute('data-page'), 10);
                    if (page >= 1 && page <= totalPages && page !== currentPage) {
                        currentPage = page;
                        render();
                    }
                });
            });
        }

        // Search filtering handler
        if (searchInput) {
            searchInput.addEventListener('input', () => {
                const query = searchInput.value.toLowerCase().trim();
                visibleRows = allRows.filter(row => {
                    return row.textContent.toLowerCase().includes(query);
                });
                currentPage = 1;
                render();
            });
        }

        render();
    }

    // Initialize all tables marked for pagination
    document.querySelectorAll('.table-card[data-paginate="true"]').forEach(wrapper => {
        initPaginatedTable(wrapper);
    });

    // Initialize fetch-based export download interceptors
    if (typeof window.initExportDownloadInterceptors === 'function') {
        window.initExportDownloadInterceptors();
    }
});

// -----------------------------------------------------------------------------
// Global Chart.js Initialization for Dashboard (Strictly NO animations)
// -----------------------------------------------------------------------------
window.initDashboardCharts = function(yearData, branchData, statusData, internData) {
    if (typeof Chart === 'undefined') return;

    // Global Chart.js defaults: Disable all animations and set clean typography
    Chart.defaults.animation = false;
    Chart.defaults.transitions = false;
    Chart.defaults.font.family = "'Inter', -apple-system, BlinkMacSystemFont, sans-serif";
    Chart.defaults.color = "#475569";

    const ACCENT_COLOR = '#059669';
    const ACCENT_LIGHT = 'rgba(5, 150, 105, 0.15)';
    const ACCENT_HOVER = '#047857';

    // -------------------------------------------------------------------------
    // Chart 1: Placements per Year (Bar Chart)
    // -------------------------------------------------------------------------
    const placementsPerYearCanvas = document.getElementById('yearwisePlacementChart');
    if (placementsPerYearCanvas && yearData && yearData.labels) {
        new Chart(placementsPerYearCanvas, {
            type: 'bar',
            data: {
                labels: yearData.labels,
                datasets: [
                    {
                        label: 'Total Offers',
                        data: yearData.offer_counts,
                        backgroundColor: 'rgba(37, 99, 235, 0.25)',
                        borderColor: ACCENT_COLOR,
                        borderWidth: 1.5,
                        borderRadius: 4,
                    },
                    {
                        label: 'Accepted Placements',
                        data: yearData.accepted_counts,
                        backgroundColor: ACCENT_COLOR,
                        borderColor: ACCENT_HOVER,
                        borderWidth: 1.5,
                        borderRadius: 4,
                    }
                ]
            },
            options: {
                animation: false,
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'top',
                        labels: { boxWidth: 12, padding: 12, font: { size: 12 } }
                    },
                    tooltip: { animation: false }
                },
                scales: {
                    x: { grid: { display: false } },
                    y: {
                        beginAtZero: true,
                        grid: { color: '#f1f5f9' },
                        title: { display: true, text: 'Placements & Offers', font: { size: 11 } }
                    }
                }
            }
        });
    }

    // -------------------------------------------------------------------------
    // Chart 2: Average Package per Year (Line Chart)
    // -------------------------------------------------------------------------
    const avgPackageCanvas = document.getElementById('avgPackagePerYearChart');
    if (avgPackageCanvas && yearData && yearData.labels) {
        new Chart(avgPackageCanvas, {
            type: 'line',
            data: {
                labels: yearData.labels,
                datasets: [
                    {
                        label: 'Average Package (LPA)',
                        data: yearData.avg_packages,
                        borderColor: ACCENT_COLOR,
                        backgroundColor: ACCENT_LIGHT,
                        fill: true,
                        pointBackgroundColor: ACCENT_COLOR,
                        pointBorderColor: '#ffffff',
                        pointBorderWidth: 2,
                        pointRadius: 4,
                        tension: 0, // Clean straight or crisp line without bouncy spline
                    }
                ]
            },
            options: {
                animation: false,
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'top',
                        labels: { boxWidth: 12, padding: 12, font: { size: 12 } }
                    },
                    tooltip: { animation: false }
                },
                scales: {
                    x: { grid: { display: false } },
                    y: {
                        beginAtZero: false,
                        grid: { color: '#f1f5f9' },
                        title: { display: true, text: 'Package (LPA)', font: { size: 11 } }
                    }
                }
            }
        });
    }

    // -------------------------------------------------------------------------
    // Chart 3: Placements by Branch (Bar Chart)
    // -------------------------------------------------------------------------
    const branchCanvas = document.getElementById('branchwiseChart');
    if (branchCanvas && branchData && branchData.labels) {
        new Chart(branchCanvas, {
            type: 'bar',
            data: {
                labels: branchData.labels,
                datasets: [
                    {
                        label: 'Placed Students',
                        data: branchData.placed_students,
                        backgroundColor: ACCENT_COLOR,
                        borderColor: ACCENT_HOVER,
                        borderWidth: 1.5,
                        borderRadius: 4,
                    },
                    {
                        label: 'Total Registered Students',
                        data: branchData.student_counts,
                        backgroundColor: 'rgba(148, 163, 184, 0.35)',
                        borderColor: '#94a3b8',
                        borderWidth: 1.5,
                        borderRadius: 4,
                    }
                ]
            },
            options: {
                animation: false,
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'top',
                        labels: { boxWidth: 12, padding: 12, font: { size: 12 } }
                    },
                    tooltip: { animation: false }
                },
                scales: {
                    x: { grid: { display: false } },
                    y: {
                        beginAtZero: true,
                        grid: { color: '#f1f5f9' },
                        title: { display: true, text: 'Student Count', font: { size: 11 } }
                    }
                }
            }
        });
    }

    // -------------------------------------------------------------------------
    // Chart 4: Mandatory vs Additional Internships (Doughnut Chart)
    // -------------------------------------------------------------------------
    const internCanvas = document.getElementById('internshipsBreakdownChart');
    if (internCanvas && internData && internData.labels) {
        // Organize counts into Mandatory vs Additional
        new Chart(internCanvas, {
            type: 'doughnut',
            data: {
                labels: internData.labels,
                datasets: [{
                    data: internData.counts,
                    backgroundColor: [
                        '#94a3b8', // Additional Internships (slate)
                        ACCENT_COLOR, // Mandatory #1 (accent blue)
                        '#60a5fa', // Mandatory #2 (light accent blue)
                    ],
                    borderWidth: 2,
                    borderColor: '#ffffff',
                }]
            },
            options: {
                animation: false,
                responsive: true,
                maintainAspectRatio: false,
                cutout: '68%',
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: { boxWidth: 12, padding: 10, font: { size: 11 } }
                    },
                    tooltip: { animation: false }
                }
            }
        });
    }
};

// -----------------------------------------------------------------------------
// Enterprise University Placement Dashboard (Dynamic Multi-Filter Interactive Visualizations)
// -----------------------------------------------------------------------------
window.initEnterpriseDashboard = function(initialPayload) {
    if (typeof Chart === 'undefined') {
        console.warn('Chart.js library is not available. Showing tabular fallback.');
        document.querySelectorAll('.chart-loading-overlay').forEach(overlay => overlay.style.display = 'none');
        document.querySelectorAll('.chart-empty-container').forEach(empty => {
            empty.style.display = 'flex';
            const title = empty.querySelector('.empty-state-title');
            if (title) title.textContent = 'Chart Visualization Standby';
            const text = empty.querySelector('.empty-state-text');
            if (text) text.textContent = 'Chart engine is in standby. Metric details are fully available in tabular view.';
        });
        return;
    }

    // Strict institutional rule: Absolutely NO animations
    Chart.defaults.animation = false;
    Chart.defaults.transitions = false;
    Chart.defaults.font.family = "'Inter', -apple-system, BlinkMacSystemFont, sans-serif";
    Chart.defaults.color = "#475569";

    const COLORS = {
        primary: '#059669',
        primaryLight: 'rgba(5, 150, 105, 0.25)',
        success: '#10b981',
        successLight: 'rgba(16, 185, 129, 0.25)',
        warning: '#f59e0b',
        warningLight: 'rgba(245, 158, 11, 0.25)',
        danger: '#ef4444',
        info: '#06b6d4',
        purple: '#8b5cf6',
        slate: '#94a3b8',
        slateLight: 'rgba(148, 163, 184, 0.25)',
    };

    window.enterpriseCharts = window.enterpriseCharts || {};

    function updateChartOrEmpty(chartKey, canvasId, emptyId, createChartFn, chartData) {
        const canvas = document.getElementById(canvasId);
        const emptyEl = document.getElementById(emptyId);
        if (!canvas) return;

        const isEmpty = !chartData || chartData.is_empty || !chartData.labels || chartData.labels.length === 0;

        if (isEmpty) {
            canvas.style.display = 'none';
            if (emptyEl) emptyEl.style.display = 'flex';
            if (window.enterpriseCharts[chartKey]) {
                window.enterpriseCharts[chartKey].destroy();
                delete window.enterpriseCharts[chartKey];
            }
            return;
        }

        canvas.style.display = 'block';
        if (emptyEl) emptyEl.style.display = 'none';

        if (window.enterpriseCharts[chartKey]) {
            window.enterpriseCharts[chartKey].destroy();
        }
        window.enterpriseCharts[chartKey] = createChartFn(canvas, chartData);
    }

    // Chart 1: Branch-wise Placement Distribution
    function createBranchwiseChart(canvas, data) {
        return new Chart(canvas, {
            type: 'bar',
            data: {
                labels: data.labels,
                datasets: [
                    {
                        label: 'Placed Students',
                        data: data.placed_students,
                        backgroundColor: COLORS.primary,
                        borderColor: COLORS.primary,
                        borderWidth: 1,
                        borderRadius: 4,
                    },
                    {
                        label: 'Eligible Students',
                        data: data.eligible_students,
                        backgroundColor: COLORS.successLight,
                        borderColor: COLORS.success,
                        borderWidth: 1,
                        borderRadius: 4,
                    },
                    {
                        label: 'Total Registered',
                        data: data.student_counts,
                        backgroundColor: COLORS.slateLight,
                        borderColor: COLORS.slate,
                        borderWidth: 1,
                        borderRadius: 4,
                    }
                ]
            },
            options: {
                animation: false,
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { position: 'top', labels: { boxWidth: 12, padding: 10, font: { size: 11 } } },
                    tooltip: { animation: false }
                },
                scales: {
                    x: { grid: { display: false } },
                    y: { beginAtZero: true, grid: { color: '#f1f5f9' }, title: { display: true, text: 'Student Count', font: { size: 11 } } }
                }
            }
        });
    }

    // Chart 2: Year-wise Placement Trends
    function createYearwiseChart(canvas, data) {
        return new Chart(canvas, {
            type: 'bar',
            data: {
                labels: data.labels,
                datasets: [
                    {
                        label: 'Total Offers',
                        data: data.offer_counts,
                        backgroundColor: COLORS.primaryLight,
                        borderColor: COLORS.primary,
                        borderWidth: 1.5,
                        borderRadius: 4,
                        order: 2,
                    },
                    {
                        label: 'Accepted Placements',
                        data: data.accepted_counts,
                        backgroundColor: COLORS.primary,
                        borderColor: COLORS.primary,
                        borderWidth: 1.5,
                        borderRadius: 4,
                        order: 2,
                    },
                    {
                        label: 'Avg Package (LPA)',
                        data: data.avg_packages,
                        type: 'line',
                        borderColor: COLORS.success,
                        backgroundColor: 'transparent',
                        borderWidth: 2,
                        pointBackgroundColor: COLORS.success,
                        pointBorderColor: '#fff',
                        pointRadius: 4,
                        tension: 0,
                        yAxisID: 'y1',
                        order: 1,
                    }
                ]
            },
            options: {
                animation: false,
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { position: 'top', labels: { boxWidth: 12, padding: 10, font: { size: 11 } } },
                    tooltip: { animation: false }
                },
                scales: {
                    x: { grid: { display: false } },
                    y: {
                        beginAtZero: true,
                        grid: { color: '#f1f5f9' },
                        title: { display: true, text: 'Offers / Placements', font: { size: 11 } }
                    },
                    y1: {
                        beginAtZero: true,
                        position: 'right',
                        grid: { display: false },
                        title: { display: true, text: 'Avg Package (LPA)', font: { size: 11 } }
                    }
                }
            }
        });
    }

    // Chart 3: CTC Package Distribution
    function createPackageDistChart(canvas, data) {
        return new Chart(canvas, {
            type: 'bar',
            data: {
                labels: data.labels,
                datasets: [{
                    label: 'Offers Count',
                    data: data.counts,
                    backgroundColor: [
                        COLORS.slate,
                        COLORS.primary,
                        COLORS.purple,
                        COLORS.success,
                    ],
                    borderRadius: 4,
                }]
            },
            options: {
                animation: false,
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: false },
                    tooltip: {
                        animation: false,
                        callbacks: {
                            label: function(context) {
                                const idx = context.dataIndex;
                                const pct = data.percentages ? data.percentages[idx] : 0;
                                return `${context.parsed.y} offers (${pct}%)`;
                            }
                        }
                    }
                },
                scales: {
                    x: { grid: { display: false } },
                    y: { beginAtZero: true, grid: { color: '#f1f5f9' }, title: { display: true, text: 'Offers Count', font: { size: 11 } } }
                }
            }
        });
    }

    // Chart 4: Placement vs Internship Statistics
    function createPlacementVsInternChart(canvas, data) {
        return new Chart(canvas, {
            type: 'bar',
            data: {
                labels: data.labels,
                datasets: [
                    {
                        label: 'Placement Offers',
                        data: data.placement_offers,
                        backgroundColor: COLORS.primary,
                        borderRadius: 4,
                    },
                    {
                        label: 'Total Internships',
                        data: data.total_internships,
                        backgroundColor: COLORS.info,
                        borderRadius: 4,
                    }
                ]
            },
            options: {
                animation: false,
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { position: 'top', labels: { boxWidth: 12, padding: 10, font: { size: 11 } } },
                    tooltip: { animation: false }
                },
                scales: {
                    x: { grid: { display: false } },
                    y: { beginAtZero: true, grid: { color: '#f1f5f9' }, title: { display: true, text: 'Count by Branch', font: { size: 11 } } }
                }
            }
        });
    }

    // Chart 5: Internship Completion Percentage
    function createInternshipCompletionChart(canvas, data) {
        return new Chart(canvas, {
            type: 'doughnut',
            data: {
                labels: data.labels,
                datasets: [{
                    data: data.counts,
                    backgroundColor: [
                        COLORS.success,  // Fully Completed (Both)
                        COLORS.warning,  // Partially Completed (1 of 2)
                        COLORS.danger,   // Incomplete / Pending
                    ],
                    borderColor: '#ffffff',
                    borderWidth: 2,
                }]
            },
            options: {
                animation: false,
                responsive: true,
                maintainAspectRatio: false,
                cutout: '68%',
                plugins: {
                    legend: { position: 'bottom', labels: { boxWidth: 12, padding: 10, font: { size: 11 } } },
                    tooltip: { animation: false }
                }
            }
        });
    }

    // Chart 6: Multiple-Offer Student Statistics
    function createMultipleOffersChart(canvas, data) {
        return new Chart(canvas, {
            type: 'doughnut',
            data: {
                labels: data.labels,
                datasets: [{
                    data: data.counts,
                    backgroundColor: [
                        COLORS.slate,   // 0 Offers
                        COLORS.primary, // 1 Offer
                        COLORS.purple,  // 2 Offers
                        COLORS.success, // 3+ Offers
                    ],
                    borderColor: '#ffffff',
                    borderWidth: 2,
                }]
            },
            options: {
                animation: false,
                responsive: true,
                maintainAspectRatio: false,
                cutout: '68%',
                plugins: {
                    legend: { position: 'bottom', labels: { boxWidth: 12, padding: 10, font: { size: 11 } } },
                    tooltip: { animation: false }
                }
            }
        });
    }

    function renderAllCharts(chartsData) {
        if (!chartsData) return;
        updateChartOrEmpty('branchwise', 'branchwisePlacementChart', 'emptyBranchwise', createBranchwiseChart, chartsData.branchwise);
        updateChartOrEmpty('yearwise', 'yearwisePlacementChart', 'emptyYearwise', createYearwiseChart, chartsData.yearwise);
        updateChartOrEmpty('packageDist', 'packageDistributionChart', 'emptyPackageDist', createPackageDistChart, chartsData.package_distribution);
        updateChartOrEmpty('placementVsIntern', 'placementVsInternshipChart', 'emptyPlacementVsIntern', createPlacementVsInternChart, chartsData.placement_vs_internship);
        updateChartOrEmpty('internCompletion', 'internshipCompletionChart', 'emptyInternshipCompletion', createInternshipCompletionChart, chartsData.internship_completion);
        updateChartOrEmpty('multipleOffers', 'multipleOffersChart', 'emptyMultipleOffers', createMultipleOffersChart, chartsData.multiple_offers);
    }

    // Initialize with initial data from server
    if (initialPayload && initialPayload.charts) {
        renderAllCharts(initialPayload.charts);
    }

    // -------------------------------------------------------------------------
    // Interactive Dynamic Filtering (AJAX & State Updates)
    // -------------------------------------------------------------------------
    const filterBatchYear = document.getElementById('filterBatchYear');
    const filterBranch = document.getElementById('filterBranch');
    const filterPlacementYear = document.getElementById('filterPlacementYear');
    const resetFiltersBtn = document.getElementById('resetFiltersBtn');
    const filterSpinner = document.getElementById('filterLoadingSpinner');
    const activeFilterBadge = document.getElementById('activeFilterBadge');

    function setLoading(isLoading) {
        if (filterSpinner) {
            if (isLoading) filterSpinner.classList.remove('d-none');
            else filterSpinner.classList.add('d-none');
        }
        document.querySelectorAll('.chart-loading-overlay').forEach(overlay => {
            overlay.style.display = isLoading ? 'flex' : 'none';
        });
    }

    async function applyDashboardFilters() {
        const batchYear = filterBatchYear ? filterBatchYear.value : '';
        const branch = filterBranch ? filterBranch.value : '';
        const placementYear = filterPlacementYear ? filterPlacementYear.value : '';

        const params = new URLSearchParams();
        if (batchYear) params.append('batch_year', batchYear);
        if (branch) params.append('branch', branch);
        if (placementYear) params.append('placement_year', placementYear);

        const hasActiveFilter = Boolean(batchYear || branch || placementYear);
        if (activeFilterBadge) {
            if (hasActiveFilter) activeFilterBadge.classList.remove('d-none');
            else activeFilterBadge.classList.add('d-none');
        }

        // Update browser URL without reloading
        const queryStr = params.toString();
        const newUrl = queryStr ? `/?${queryStr}` : '/';
        window.history.replaceState({ path: newUrl }, '', newUrl);

        setLoading(true);

        try {
            const endpoint = queryStr ? `/api/analytics/dashboard?${queryStr}` : '/api/analytics/dashboard';
            const response = await fetch(endpoint, {
                headers: { 'Accept': 'application/json' }
            });
            if (!response.ok) throw new Error(`HTTP Error ${response.status}`);
            const result = await response.json();
            if (result.status !== 'success' || !result.data) throw new Error('Invalid response structure');

            const data = result.data;
            const kpi = data.kpi || {};

            // Update KPI cards DOM
            const kpiMapping = {
                'kpiTotalStudents': kpi.total_students ?? 0,
                'kpiEligibleStudents': kpi.eligible_students ?? 0,
                'kpiTotalCompanies': kpi.total_companies ?? 0,
                'kpiActiveDrives': kpi.active_drives ?? 0,
                'kpiTotalOffers': kpi.total_offers ?? 0,
                'kpiPlacedStudents': kpi.placed_students ?? 0,
                'kpiAvgPackage': kpi.avg_package !== undefined ? kpi.avg_package : '0.0',
                'kpiHighestPackage': kpi.highest_package !== undefined ? kpi.highest_package : '0.0',
                'kpiPlacementRate': (kpi.placement_rate !== undefined ? kpi.placement_rate : 0) + '%',
            };

            for (const [id, val] of Object.entries(kpiMapping)) {
                const el = document.getElementById(id);
                if (el) el.textContent = val;
            }

            const pBar = document.getElementById('kpiPlacementProgressBar');
            if (pBar) {
                const rate = kpi.placement_rate || 0;
                pBar.style.width = `${rate}%`;
                pBar.setAttribute('aria-valuenow', rate);
            }

            // Update all 6 charts with new filtered payloads
            renderAllCharts(data.charts);

        } catch (err) {
            console.error('Failed to update dashboard filters:', err);
        } finally {
            setLoading(false);
        }
    }

    if (filterBatchYear) filterBatchYear.addEventListener('change', applyDashboardFilters);
    if (filterBranch) filterBranch.addEventListener('change', applyDashboardFilters);
    if (filterPlacementYear) filterPlacementYear.addEventListener('change', applyDashboardFilters);

    if (resetFiltersBtn) {
        resetFiltersBtn.addEventListener('click', () => {
            if (filterBatchYear) filterBatchYear.value = '';
            if (filterBranch) filterBranch.value = '';
            if (filterPlacementYear) filterPlacementYear.value = '';
            applyDashboardFilters();
        });
    }
};

// -----------------------------------------------------------------------------
// Export Truncation & Operational Alert Banner Utility
// -----------------------------------------------------------------------------
window.showExportAlert = function(message, type = 'warning') {
    let container = document.getElementById('exportAlertContainer') ||
                    document.querySelector('.flash-container') ||
                    document.querySelector('.page-container');
    if (!container) return;

    // Remove any previous export alert to prevent clutter
    const oldAlert = document.getElementById('exportTruncationAlert');
    if (oldAlert) {
        oldAlert.remove();
    }

    const alertDiv = document.createElement('div');
    alertDiv.id = 'exportTruncationAlert';
    const alertClass = type === 'warning' ? 'alert-warning' :
                       (type === 'danger' || type === 'error' ? 'alert-danger' :
                       (type === 'info' ? 'alert-info' : 'alert-success'));
    const iconClass = type === 'warning' ? 'bi-exclamation-triangle-fill text-warning' :
                      (type === 'danger' || type === 'error' ? 'bi-exclamation-octagon-fill text-danger' :
                      (type === 'info' ? 'bi-info-circle-fill text-info' : 'bi-check-circle-fill text-success'));
    const title = type === 'warning' ? 'Export Truncation Warning' :
                  (type === 'danger' || type === 'error' ? 'Export Failed' :
                  (type === 'info' ? 'Export Notice' : 'Export Complete'));

    alertDiv.className = `alert ${alertClass} alert-dismissible fade show shadow-sm d-flex align-items-center justify-content-between mb-3`;
    alertDiv.setAttribute('role', 'alert');
    alertDiv.innerHTML = `
        <div class="d-flex align-items-center gap-2">
            <i class="bi ${iconClass} fs-5 flex-shrink-0"></i>
            <div>
                <strong>${title}:</strong> <span>${message}</span>
            </div>
        </div>
        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
    `;

    container.prepend(alertDiv);
    try {
        alertDiv.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    } catch (_) {}
};

// -----------------------------------------------------------------------------
// Safe Fetch-Based File Download with Header Truncation Inspection
// -----------------------------------------------------------------------------
window.handleExportDownload = async function(linkEl, exportUrl) {
    if (!linkEl || !exportUrl || exportUrl === '#' || exportUrl.endsWith('#')) {
        return;
    }

    // Guard against repeated simultaneous clicks on the same export link
    if (linkEl.dataset.exporting === 'true') {
        return;
    }

    const originalHtml = linkEl.innerHTML;
    linkEl.dataset.exporting = 'true';
    linkEl.style.pointerEvents = 'none';
    linkEl.setAttribute('aria-busy', 'true');
    linkEl.innerHTML = '<span class="spinner-border spinner-border-sm me-1" role="status" aria-hidden="true"></span> Preparing download...';

    try {
        const response = await fetch(exportUrl, {
            method: 'GET',
            headers: {
                'X-Requested-With': 'XMLHttpRequest'
            }
        });

        if (!response.ok) {
            let errorMsg = `Failed to generate export (HTTP ${response.status}).`;
            try {
                const text = await response.text();
                if (text && text.length < 200 && !text.includes('<!DOCTYPE')) {
                    errorMsg = text;
                }
            } catch (_) {}
            window.showExportAlert(errorMsg, 'danger');
            if (window.showToast) {
                window.showToast(errorMsg, 'danger', 'Export Failed');
            }
            return;
        }

        // Determine filename from Content-Disposition header or fallback
        const disposition = response.headers.get('Content-Disposition') || '';
        let filename = 'export_data.csv';
        const filenameMatch = disposition.match(/filename[^;=\n]*=((['"]).*?\2|[^;\n]*)/);
        if (filenameMatch && filenameMatch[1]) {
            filename = filenameMatch[1].replace(/['"]/g, '').trim();
        } else if (exportUrl.includes('/reports/export-pdf')) {
            filename = 'placement_executive_report.pdf';
        } else if (exportUrl.includes('/students/export-csv')) {
            filename = 'students_directory.csv';
        } else if (exportUrl.includes('/placements/export-csv')) {
            filename = 'placement_offers_directory.csv';
        } else if (exportUrl.includes('/internships/export-csv')) {
            filename = 'internships_registry.csv';
        } else if (exportUrl.includes('/reports/export')) {
            filename = 'placement_internship_report.csv';
        }

        // Read truncation and metadata headers
        const isLimited = response.headers.get('X-Export-Limited') === 'true' ||
                          response.headers.get('X-Export-Status') === 'limited';
        const exportStatus = response.headers.get('X-Export-Status') || '';
        const exportWarning = response.headers.get('X-Export-Warning') || '';
        const exportCount = response.headers.get('X-Export-Count') || '';
        const exportTotal = response.headers.get('X-Export-Total-Count') || '';
        const exportLimit = response.headers.get('X-Export-Limit') || '';

        // Trigger safe Blob download using URL.createObjectURL
        const blob = await response.blob();
        const downloadUrl = window.URL.createObjectURL(blob);
        const tempLink = document.createElement('a');
        tempLink.style.display = 'none';
        tempLink.href = downloadUrl;
        tempLink.download = filename;
        tempLink.setAttribute('data-download-bypass', 'true');
        document.body.appendChild(tempLink);
        tempLink.click();

        setTimeout(() => {
            window.URL.revokeObjectURL(downloadUrl);
            tempLink.remove();
        }, 2000);

        // Feedback to user based on export status and limits
        if (isLimited) {
            const warningText = exportWarning ||
                `Export truncated: Only ${exportCount || 'limited'} records were downloaded because the dataset exceeds the system limit${exportLimit ? ' (' + exportLimit + ' records max)' : ''}. Total matching records: ${exportTotal || exportCount}.`;
            window.showExportAlert(warningText, 'warning');
            if (window.showToast) {
                window.showToast(warningText, 'warning', 'Export Limited');
            }
        } else if (exportStatus === 'empty' || exportCount === '0') {
            const emptyText = 'No matching records found for the active filter criteria. An empty export file was generated.';
            window.showExportAlert(emptyText, 'info');
            if (window.showToast) {
                window.showToast(emptyText, 'info', 'Empty Export');
            }
        } else {
            const countText = exportCount ? ` (${exportCount} records)` : '';
            const successText = `Export downloaded successfully${countText}: ${filename}`;
            if (window.showToast) {
                window.showToast(successText, 'success', 'Export Complete');
            }
        }
    } catch (err) {
        console.error('Export download error:', err);
        const errorText = 'Network or system error occurred while generating download. Please try again.';
        window.showExportAlert(errorText, 'danger');
        if (window.showToast) {
            window.showToast(errorText, 'danger', 'Export Error');
        }
    } finally {
        linkEl.dataset.exporting = 'false';
        linkEl.style.pointerEvents = '';
        linkEl.removeAttribute('aria-busy');
        linkEl.innerHTML = originalHtml;
    }
};

// -----------------------------------------------------------------------------
// Global Export Click Interceptor Setup
// -----------------------------------------------------------------------------
window.initExportDownloadInterceptors = function() {
    if (window._exportInterceptorsInitialized) return;
    window._exportInterceptorsInitialized = true;

    function getExportAnchor(element) {
        if (!element || element.nodeType !== Node.ELEMENT_NODE) return null;
        const anchor = element.closest('a');
        if (!anchor) return null;
        if (anchor.hasAttribute('data-download-bypass')) return null;

        if (anchor.id === 'btnDownloadSavedCsv' ||
            anchor.classList.contains('export-download-btn') ||
            anchor.hasAttribute('data-export-btn')) {
            return anchor;
        }

        const href = anchor.getAttribute('href') || '';
        if (
            href.includes('/students/export-csv') ||
            href.includes('/placements/export-csv') ||
            href.includes('/internships/export-csv') ||
            href.includes('/reports/export') ||
            href.includes('/reports/export-pdf') ||
            href.includes('/sql-reports/export-saved')
        ) {
            return anchor;
        }

        return null;
    }

    document.addEventListener('click', (e) => {
        const anchor = getExportAnchor(e.target);
        if (!anchor) {
            // Normal navigation or unrelated link - DO NOT intercept!
            return;
        }

        const href = anchor.getAttribute('href');
        if (!href || href === '#' || href.endsWith('#')) {
            if (anchor.id === 'btnDownloadSavedCsv') {
                e.preventDefault();
                if (window.showToast) {
                    window.showToast('Please select a saved report before downloading CSV.', 'warning', 'Export Notice');
                }
            }
            return;
        }

        e.preventDefault();
        e.stopPropagation();
        window.handleExportDownload(anchor, anchor.href);
    });
};

// Auto-run interceptor registration
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', window.initExportDownloadInterceptors);
} else {
    window.initExportDownloadInterceptors();
}

// -----------------------------------------------------------------------------
// Toast Notification Utility
// -----------------------------------------------------------------------------
window.showToast = function(message, type = 'info', title = '') {
    const container = document.getElementById('toastContainer');
    if (!container) return;

    const toastId = 'toast-' + Date.now();
    const bgClass = type === 'success' ? 'text-bg-success' :
                    type === 'danger' || type === 'error' ? 'text-bg-danger' :
                    type === 'warning' ? 'text-bg-warning' : 'text-bg-primary';

    const headerHtml = title ? `
        <div class="toast-header border-0 bg-transparent text-white">
            <strong class="me-auto">${title}</strong>
            <button type="button" class="btn-close btn-close-white" data-bs-dismiss="toast" aria-label="Close"></button>
        </div>` : '';

    const toastEl = document.createElement('div');
    toastEl.id = toastId;
    toastEl.className = `toast align-items-center ${bgClass} border-0 shadow-sm`;
    toastEl.setAttribute('role', 'alert');
    toastEl.setAttribute('aria-live', 'assertive');
    toastEl.setAttribute('aria-atomic', 'true');
    toastEl.setAttribute('data-bs-delay', '5000');

    toastEl.innerHTML = `
        ${headerHtml}
        <div class="d-flex">
            <div class="toast-body">
                ${message}
            </div>
            ${!title ? '<button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>' : ''}
        </div>
    `;

    container.appendChild(toastEl);
    const bsToast = new bootstrap.Toast(toastEl);
    bsToast.show();
    toastEl.addEventListener('hidden.bs.toast', () => {
        toastEl.remove();
    });
};
