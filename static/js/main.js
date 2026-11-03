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

    // -------------------------------------------------------------------------
    // 2. Auto-dismiss Flash Alerts
    // -------------------------------------------------------------------------
    const flashAlerts = document.querySelectorAll('.flash-alert');
    flashAlerts.forEach(alert => {
        setTimeout(() => {
            const bsAlert = bootstrap.Alert.getOrCreateInstance(alert);
            if (bsAlert) bsAlert.close();
        }, 6000);
    });

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

            // If valid, disable submit button and show saving indicator
            const submitBtn = form.querySelector('button[type="submit"]');
            if (submitBtn && !submitBtn.disabled) {
                submitBtn.disabled = true;
                const originalHtml = submitBtn.innerHTML;
                submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-1" role="status" aria-hidden="true"></span> Saving...';
                
                // Safety re-enable timeout if server response takes long or fails without page refresh
                setTimeout(() => {
                    if (submitBtn) {
                        submitBtn.disabled = false;
                        submitBtn.innerHTML = originalHtml;
                    }
                }, 10000);
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

    const ACCENT_COLOR = '#2563eb';
    const ACCENT_LIGHT = 'rgba(37, 99, 235, 0.15)';
    const ACCENT_HOVER = '#1d4ed8';

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
    if (typeof Chart === 'undefined') return;

    // Strict institutional rule: Absolutely NO animations
    Chart.defaults.animation = false;
    Chart.defaults.transitions = false;
    Chart.defaults.font.family = "'Inter', -apple-system, BlinkMacSystemFont, sans-serif";
    Chart.defaults.color = "#475569";

    const COLORS = {
        primary: '#2563eb',
        primaryLight: 'rgba(37, 99, 235, 0.25)',
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
