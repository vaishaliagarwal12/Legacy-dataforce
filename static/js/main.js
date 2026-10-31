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
