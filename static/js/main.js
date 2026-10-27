/**
 * Legacy DataForce - Phase 8 Frontend Interactive Utilities
 * Handles sidebar toggles, delete confirmation modals, dynamic forms, and Chart.js initialization.
 */

document.addEventListener('DOMContentLoaded', () => {
    // -------------------------------------------------------------------------
    // 1. Mobile Sidebar Toggle & Backdrop
    // -------------------------------------------------------------------------
    const sidebarToggle = document.getElementById('sidebarToggle');
    const appSidebar = document.getElementById('appSidebar');
    const sidebarBackdrop = document.getElementById('sidebarBackdrop');

    if (sidebarToggle && appSidebar) {
        sidebarToggle.addEventListener('click', () => {
            appSidebar.classList.toggle('show');
            if (sidebarBackdrop) sidebarBackdrop.classList.toggle('show');
        });
    }

    if (sidebarBackdrop) {
        sidebarBackdrop.addEventListener('click', () => {
            if (appSidebar) appSidebar.classList.remove('show');
            sidebarBackdrop.classList.remove('show');
        });
    }

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
        });
    }

    // -------------------------------------------------------------------------
    // 4. Client-side Bootstrap Form Validation
    // -------------------------------------------------------------------------
    const forms = document.querySelectorAll('.needs-validation');
    Array.from(forms).forEach(form => {
        form.addEventListener('submit', event => {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            form.classList.add('was-validated');
        }, false);
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
                
                // Set default internship no to requirement selected if available
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

        // Initialize state on load
        updateInternshipFields();
    }

    // -------------------------------------------------------------------------
    // 6. Live Table Quick-Search Filter
    // -------------------------------------------------------------------------
    const quickSearchInputs = document.querySelectorAll('[data-table-search]');
    quickSearchInputs.forEach(input => {
        const targetTableId = input.getAttribute('data-table-search');
        const targetTable = document.getElementById(targetTableId);
        if (!targetTable) return;

        input.addEventListener('input', () => {
            const filter = input.value.toLowerCase().trim();
            const rows = targetTable.querySelectorAll('tbody tr');
            rows.forEach(row => {
                const text = row.textContent.toLowerCase();
                if (text.includes(filter)) {
                    row.style.display = '';
                } else {
                    row.style.display = 'none';
                }
            });
        });
    });
});

// -----------------------------------------------------------------------------
// Global Chart.js Initialization Helper for Dashboard
// -----------------------------------------------------------------------------
window.initDashboardCharts = function(yearData, branchData, statusData, internData) {
    // 1. Year-wise Placement Offers & Package Trend (Bar + Line)
    const yearCtx = document.getElementById('yearwisePlacementChart');
    if (yearCtx && yearData && yearData.labels) {
        new Chart(yearCtx, {
            type: 'bar',
            data: {
                labels: yearData.labels,
                datasets: [
                    {
                        label: 'Total Offers',
                        data: yearData.offer_counts,
                        backgroundColor: 'rgba(37, 99, 235, 0.75)',
                        borderColor: '#2563eb',
                        borderWidth: 1,
                        borderRadius: 6,
                        yAxisID: 'y',
                    },
                    {
                        label: 'Accepted Placements',
                        data: yearData.accepted_counts,
                        backgroundColor: 'rgba(16, 185, 129, 0.75)',
                        borderColor: '#10b981',
                        borderWidth: 1,
                        borderRadius: 6,
                        yAxisID: 'y',
                    },
                    {
                        type: 'line',
                        label: 'Average Package (LPA)',
                        data: yearData.avg_packages,
                        borderColor: '#d97706',
                        backgroundColor: 'rgba(217, 119, 6, 0.15)',
                        pointBackgroundColor: '#d97706',
                        pointBorderColor: '#ffffff',
                        pointHoverRadius: 6,
                        tension: 0.3,
                        yAxisID: 'y1',
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                interaction: { mode: 'index', intersect: false },
                plugins: {
                    legend: { position: 'top', labels: { boxWidth: 12, font: { family: 'Inter', size: 12 } } },
                    tooltip: { padding: 10, cornerRadius: 8 }
                },
                scales: {
                    x: { grid: { display: false } },
                    y: {
                        type: 'linear',
                        display: true,
                        position: 'left',
                        title: { display: true, text: 'Number of Offers' },
                        grid: { color: '#f1f5f9' },
                    },
                    y1: {
                        type: 'linear',
                        display: true,
                        position: 'right',
                        title: { display: true, text: 'Package (LPA)' },
                        grid: { drawOnChartArea: false },
                    }
                }
            }
        });
    }

    // 2. Branch-wise Placement & Internship Performance (Grouped Bar)
    const branchCtx = document.getElementById('branchwiseChart');
    if (branchCtx && branchData && branchData.labels) {
        new Chart(branchCtx, {
            type: 'bar',
            data: {
                labels: branchData.labels,
                datasets: [
                    {
                        label: 'Total Active Students',
                        data: branchData.student_counts,
                        backgroundColor: 'rgba(100, 116, 139, 0.65)',
                        borderRadius: 6,
                    },
                    {
                        label: 'Placed Students',
                        data: branchData.placed_students,
                        backgroundColor: 'rgba(37, 99, 235, 0.85)',
                        borderRadius: 6,
                    },
                    {
                        label: 'Completed Internships',
                        data: branchData.internship_counts,
                        backgroundColor: 'rgba(13, 148, 136, 0.85)',
                        borderRadius: 6,
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { position: 'top', labels: { boxWidth: 12, font: { family: 'Inter', size: 12 } } },
                },
                scales: {
                    x: { grid: { display: false } },
                    y: { beginAtZero: true, grid: { color: '#f1f5f9' }, title: { display: true, text: 'Count' } }
                }
            }
        });
    }

    // 3. Placement Offer Status Distribution (Doughnut)
    const statusCtx = document.getElementById('offerStatusChart');
    if (statusCtx && statusData && statusData.labels) {
        new Chart(statusCtx, {
            type: 'doughnut',
            data: {
                labels: statusData.labels,
                datasets: [{
                    data: statusData.counts,
                    backgroundColor: [
                        '#3b82f6', // Offered (blue)
                        '#10b981', // Accepted (emerald)
                        '#059669', // Joined (dark green)
                        '#ef4444'  // Declined (red)
                    ],
                    borderWidth: 2,
                    borderColor: '#ffffff'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { position: 'bottom', labels: { boxWidth: 12, padding: 12 } }
                },
                cutout: '65%'
            }
        });
    }

    // 4. Internship Breakdown (Doughnut)
    const internCtx = document.getElementById('internshipBreakdownChart');
    if (internCtx && internData && internData.labels) {
        new Chart(internCtx, {
            type: 'doughnut',
            data: {
                labels: internData.labels,
                datasets: [{
                    data: internData.counts,
                    backgroundColor: [
                        '#6366f1', // Mandatory 1 (Indigo)
                        '#8b5cf6', // Mandatory 2 (Purple)
                        '#0ea5e9'  // Additional (Sky blue)
                    ],
                    borderWidth: 2,
                    borderColor: '#ffffff'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { position: 'bottom', labels: { boxWidth: 12, padding: 12 } }
                },
                cutout: '65%'
            }
        });
    }
};
