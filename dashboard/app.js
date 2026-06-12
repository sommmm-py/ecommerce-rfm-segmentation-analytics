// Apex Analytics Dashboard Controller

let appData = null;
let filteredCustomers = [];
let currentPage = 1;
const pageSize = 10;

// Chart references
let salesChartInstance = null;
let segmentChartInstance = null;

// Initialize on DOM load
document.addEventListener("DOMContentLoaded", () => {
    initTheme();
    loadDashboardData();
    setupEventListeners();
});

// Theme Management
function initTheme() {
    const savedTheme = localStorage.getItem("theme") || "dark";
    document.documentElement.setAttribute("data-theme", savedTheme);
    updateThemeToggleUI(savedTheme);
}

function updateThemeToggleUI(theme) {
    const btn = document.getElementById("theme-toggle");
    if (!btn) return;
    if (theme === "dark") {
        btn.querySelector(".icon-sun").style.display = "block";
        btn.querySelector(".icon-moon").style.display = "none";
    } else {
        btn.querySelector(".icon-sun").style.display = "none";
        btn.querySelector(".icon-moon").style.display = "block";
    }
}

function setupEventListeners() {
    // Theme toggle
    document.getElementById("theme-toggle").addEventListener("click", () => {
        const currentTheme = document.documentElement.getAttribute("data-theme");
        const newTheme = currentTheme === "dark" ? "light" : "dark";
        document.documentElement.setAttribute("data-theme", newTheme);
        localStorage.setItem("theme", newTheme);
        updateThemeToggleUI(newTheme);
        
        // Re-render charts with updated theme colors
        if (appData) {
            renderCharts();
        }
    });

    // Customer grid filters
    document.getElementById("customer-search").addEventListener("input", () => {
        currentPage = 1;
        applyFilters();
    });

    document.getElementById("segment-filter").addEventListener("change", () => {
        currentPage = 1;
        applyFilters();
    });
}

// Fetch dashboard data
async function loadDashboardData() {
    try {
        const response = await fetch("../data/dashboard_data.json");
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        appData = await response.json();
        
        // Populate dashboard components
        updateKPIs(appData.kpis);
        renderCharts();
        renderCohortHeatmap(appData.cohorts);
        
        filteredCustomers = [...appData.customers];
        renderCustomerTable();
        
    } catch (error) {
        console.error("Could not load dashboard data JSON:", error);
        // Display user friendly error in case of local CORS issues
        const main = document.querySelector(".main-content");
        const alertDiv = document.createElement("div");
        alertDiv.className = "kpi-card";
        alertDiv.style.borderColor = "var(--color-atrisk)";
        alertDiv.style.gridColumn = "1 / -1";
        alertDiv.innerHTML = `
            <div style="display:flex; align-items:center; gap:1rem;">
                <i class="fa-solid fa-circle-exclamation" style="font-size:2rem; color:var(--color-atrisk)"></i>
                <div>
                    <h3 style="color:var(--text-primary); margin-bottom:0.25rem;">Data Source Offline</h3>
                    <p style="color:var(--text-secondary); font-size:0.9rem;">
                        This dashboard loads its analytical metrics via a JSON file. Due to browser security (CORS) rules, 
                        opening this HTML file directly via <code>file://</code> double-click will block files loading.
                    </p>
                    <p style="color:var(--text-secondary); font-size:0.9rem; margin-top:0.5rem; font-weight:600;">
                        To run locally, run this command in terminal: <code style="background:rgba(0,0,0,0.2); padding:2px 6px; border-radius:4px;">npx serve dashboard</code> or upload to Github and run via Github Pages.
                    </p>
                </div>
            </div>
        `;
        main.insertBefore(alertDiv, main.firstChild);
    }
}

// Format numbers
function formatCurrency(num) {
    return new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' }).format(num);
}

function formatNumber(num) {
    return new Intl.NumberFormat('en-US').format(num);
}

// Update KPI cards
function updateKPIs(kpis) {
    document.getElementById("kpi-revenue").textContent = formatCurrency(kpis.totalRevenue);
    document.getElementById("kpi-customers").textContent = formatNumber(kpis.totalCustomers);
    document.getElementById("kpi-aov").textContent = formatCurrency(kpis.aov);
    document.getElementById("kpi-retention").textContent = `${kpis.retentionRate}%`;
}

// Render line and doughnut charts
function renderCharts() {
    const isDark = document.documentElement.getAttribute("data-theme") === "dark";
    const textSecondary = isDark ? '#94a3b8' : '#475569';
    const gridColor = isDark ? 'rgba(255, 255, 255, 0.08)' : 'rgba(0, 0, 0, 0.06)';

    // 1. Double Y-Axis Line/Bar Chart (Sales Trend)
    const salesCtx = document.getElementById("salesTrendChart").getContext("2d");
    if (salesChartInstance) {
        salesChartInstance.destroy();
    }

    const labels = appData.salesTrend.map(d => d.month);
    const revenueData = appData.salesTrend.map(d => d.revenue);
    const orderData = appData.salesTrend.map(d => d.orders);

    salesChartInstance = new Chart(salesCtx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [
                {
                    label: 'Monthly Revenue',
                    data: revenueData,
                    borderColor: '#3b82f6',
                    backgroundColor: 'rgba(59, 130, 246, 0.1)',
                    fill: true,
                    tension: 0.3,
                    borderWidth: 3,
                    yAxisID: 'y'
                },
                {
                    label: 'Orders (Invoices)',
                    data: orderData,
                    borderColor: '#10b981',
                    backgroundColor: 'transparent',
                    borderDash: [5, 5],
                    tension: 0.3,
                    borderWidth: 2,
                    yAxisID: 'y1'
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    labels: { color: textSecondary, font: { family: 'Outfit' } }
                },
                tooltip: {
                    mode: 'index',
                    intersect: false,
                }
            },
            scales: {
                x: {
                    grid: { color: gridColor },
                    ticks: { color: textSecondary, font: { family: 'Outfit' } }
                },
                y: {
                    type: 'linear',
                    display: true,
                    position: 'left',
                    grid: { color: gridColor },
                    ticks: {
                        color: textSecondary,
                        font: { family: 'Outfit' },
                        callback: function(value) { return '$' + formatNumber(value); }
                    }
                },
                y1: {
                    type: 'linear',
                    display: true,
                    position: 'right',
                    grid: { drawOnChartArea: false },
                    ticks: {
                        color: textSecondary,
                        font: { family: 'Outfit' }
                    }
                }
            }
        }
    });

    // 2. Customer Segmentation Doughnut Chart
    const segmentCtx = document.getElementById("segmentChart").getContext("2d");
    if (segmentChartInstance) {
        segmentChartInstance.destroy();
    }

    const segmentLabels = appData.segmentation.map(s => s.segment);
    const segmentCounts = appData.segmentation.map(s => s.count);
    
    // Segment specific colors
    const segmentColors = {
        'Champions': '#10b981',
        'Loyal Customers': '#3b82f6',
        'Promising/New': '#f59e0b',
        'At Risk': '#ef4444',
        'Lost/Hibernating': '#6b7280'
    };
    const bgColors = segmentLabels.map(label => segmentColors[label] || '#94a3b8');

    segmentChartInstance = new Chart(segmentCtx, {
        type: 'doughnut',
        data: {
            labels: segmentLabels,
            datasets: [{
                data: segmentCounts,
                backgroundColor: bgColors,
                borderWidth: isDark ? 2 : 1,
                borderColor: isDark ? '#0f172a' : '#ffffff'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: {
                        color: textSecondary,
                        font: { family: 'Outfit', size: 11 },
                        padding: 15
                    }
                }
            },
            cutout: '65%'
        }
    });
}

// Render Cohort Heatmap Table
function renderCohortHeatmap(cohorts) {
    const table = document.getElementById("cohort-heatmap");
    const thead = table.querySelector("thead");
    const tbody = table.querySelector("tbody");
    
    thead.innerHTML = "";
    tbody.innerHTML = "";

    // 1. Generate Headers
    let headerRow = "<tr><th>Cohort Month</th><th>Cohort Size</th>";
    for (let i = 1; i <= 12; i++) {
        headerRow += `<th>Month ${i}</th>`;
    }
    headerRow += "</tr>";
    thead.innerHTML = headerRow;

    // 2. Generate Rows
    cohorts.forEach(row => {
        let tr = document.createElement("tr");
        
        // Cohort Name & Size cells
        let tdCohort = `<td>${row.cohort}</td>`;
        let tdSize = `<td>${formatNumber(row.size)}</td>`;
        tr.innerHTML = tdCohort + tdSize;

        // Retention Cells
        row.retention.forEach((rate, idx) => {
            let td = document.createElement("td");
            if (rate === null) {
                td.textContent = "-";
                td.style.backgroundColor = "transparent";
            } else {
                td.textContent = `${rate}%`;
                td.className = "heatmap-cell";
                
                // Color scaling using CSS RGB variables
                const opacity = rate / 100;
                td.style.backgroundColor = `rgba(var(--heatmap-base), ${opacity})`;
                
                // Ensure proper text contrast
                if (rate > 55) {
                    td.style.color = "var(--heatmap-text-high)";
                } else {
                    td.style.color = "var(--heatmap-text-low)";
                }
            }
            tr.appendChild(td);
        });

        tbody.appendChild(tr);
    });
}

// Filter customer list based on inputs
function applyFilters() {
    const searchVal = document.getElementById("customer-search").value.toLowerCase().trim();
    const segmentVal = document.getElementById("segment-filter").value;

    filteredCustomers = appData.customers.filter(c => {
        const matchesSearch = c.id.toLowerCase().includes(searchVal);
        const matchesSegment = segmentVal === "All" || c.segment === segmentVal;
        return matchesSearch && matchesSegment;
    });

    renderCustomerTable();
}

// Render tabular customers list
function renderCustomerTable() {
    const tbody = document.getElementById("customers-table-body");
    tbody.innerHTML = "";

    const total = filteredCustomers.length;
    const startIdx = (currentPage - 1) * pageSize;
    const endIdx = Math.min(startIdx + pageSize, total);
    
    // Select correct slice
    const pageData = filteredCustomers.slice(startIdx, endIdx);

    if (pageData.length === 0) {
        tbody.innerHTML = `<tr><td colspan="6" class="text-center" style="padding: 3rem; color: var(--text-secondary);">No customers found matching the search criteria.</td></tr>`;
        document.getElementById("table-entries-info").textContent = "Showing 0 of 0 entries";
        renderPagination(0);
        return;
    }

    pageData.forEach(c => {
        const tr = document.createElement("tr");
        
        // Map segment string to badge class
        let badgeClass = "badge lost";
        if (c.segment === "Champions") badgeClass = "badge champions";
        else if (c.segment === "Loyal Customers") badgeClass = "badge loyal";
        else if (c.segment === "Promising/New") badgeClass = "badge promising";
        else if (c.segment === "At Risk") badgeClass = "badge atrisk";

        tr.innerHTML = `
            <td><strong>#${c.id}</strong></td>
            <td>${c.recency} days ago</td>
            <td>${c.frequency} orders</td>
            <td>${formatCurrency(c.monetary)}</td>
            <td class="text-center">
                <span style="font-family: monospace; font-size: 0.85rem; letter-spacing: 1px;">
                    R:${c.r_score} F:${c.f_score} M:${c.m_score}
                </span>
            </td>
            <td><span class="${badgeClass}">${c.segment}</span></td>
        `;
        tbody.appendChild(tr);
    });

    // Update paging status text
    document.getElementById("table-entries-info").textContent = `Showing ${startIdx + 1} to ${endIdx} of ${total} customers`;
    
    // Draw paging footer
    renderPagination(total);
}

// Render dynamic pagination buttons
function renderPagination(totalEntries) {
    const paginationContainer = document.getElementById("table-pagination");
    paginationContainer.innerHTML = "";

    const totalPages = Math.ceil(totalEntries / pageSize);
    if (totalPages <= 1) return;

    // Previous Button
    const prevBtn = document.createElement("button");
    prevBtn.className = "page-btn";
    prevBtn.innerHTML = '<i class="fa-solid fa-angle-left"></i>';
    prevBtn.disabled = currentPage === 1;
    prevBtn.addEventListener("click", () => {
        if (currentPage > 1) {
            currentPage--;
            renderCustomerTable();
        }
    });
    paginationContainer.appendChild(prevBtn);

    // Page number buttons (show max 5 pages around current page)
    let startPage = Math.max(1, currentPage - 2);
    let endPage = Math.min(totalPages, startPage + 4);
    
    if (endPage - startPage < 4) {
        startPage = Math.max(1, endPage - 4);
    }

    for (let i = startPage; i <= endPage; i++) {
        const pageBtn = document.createElement("button");
        pageBtn.className = `page-btn ${i === currentPage ? 'active' : ''}`;
        pageBtn.textContent = i;
        pageBtn.addEventListener("click", () => {
            currentPage = i;
            renderCustomerTable();
        });
        paginationContainer.appendChild(pageBtn);
    }

    // Next Button
    const nextBtn = document.createElement("button");
    nextBtn.className = "page-btn";
    nextBtn.innerHTML = '<i class="fa-solid fa-angle-right"></i>';
    nextBtn.disabled = currentPage === totalPages;
    nextBtn.addEventListener("click", () => {
        if (currentPage < totalPages) {
            currentPage++;
            renderCustomerTable();
        }
    });
    paginationContainer.appendChild(nextBtn);
}
