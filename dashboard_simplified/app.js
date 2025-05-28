// Global variables
let originalData = [];
let suspectData = [];
let comparisonData = [];
let filteredData = [];

// DOM elements
const loadingElement = document.getElementById('loading');
const centroFilter = document.getElementById('centro-filter');
const skuFilter = document.getElementById('sku-filter');
const fornecedorFilter = document.getElementById('fornecedor-filter');
const grupoFilter = document.getElementById('grupo-filter');
const produtoFilter = document.getElementById('produto-filter');
const startDateInput = document.getElementById('start-date');
const endDateInput = document.getElementById('end-date');
const onlySuspectsYes = document.getElementById('only-suspects-yes');
const onlySuspectsNo = document.getElementById('only-suspects-no');
const applyFiltersBtn = document.getElementById('apply-filters');
const clearFiltersBtn = document.getElementById('clear-filters');
const exportCsvBtn = document.getElementById('export-csv');

// Initialize the dashboard
document.addEventListener('DOMContentLoaded', function() {
    showLoading();
    
    // Initialize data
    originalData = processOriginalData(rawData);
    suspectData = processSuspectData(rawSuspectData);
    comparisonData = processComparisonData(rawComparisonData);
    
    // Set initial filtered data
    filteredData = [...originalData];
    
    // Populate filter options
    populateFilterOptions();
    
    // Set date range
    setDateRange();
    
    // Add event listeners
    applyFiltersBtn.addEventListener('click', applyFilters);
    clearFiltersBtn.addEventListener('click', clearFilters);
    exportCsvBtn.addEventListener('click', exportToCsv);
    
    // Initial render
    renderDashboard();
    
    hideLoading();
});

// Process original data
function processOriginalData(data) {
    return data.map(item => {
        return {
            ...item,
            'Data Doc.': new Date(item['Data Doc.']),
            'Preco_Unitario': item['Valor Liquido'] / item['Quantidade']
        };
    });
}

// Process suspect data
function processSuspectData(data) {
    return data;
}

// Process comparison data
function processComparisonData(data) {
    return data;
}

// Populate filter options
function populateFilterOptions() {
    // Get unique values
    const centros = [...new Set(originalData.map(item => item['Centro']))].sort();
    const skus = [...new Set(originalData.map(item => item['SKU']))].sort();
    const fornecedores = [...new Set(originalData.map(item => item['Fornecedor']))].sort();
    const grupos = [...new Set(originalData.map(item => item['Grp. Mercadoria']).filter(Boolean))].sort();
    const produtos = [...new Set(originalData.map(item => item['Descrição']).filter(Boolean))].sort();
    
    // Populate Centro filter
    centros.forEach(centro => {
        const option = document.createElement('option');
        option.value = centro;
        option.textContent = centro;
        centroFilter.appendChild(option);
    });
    
    // Populate SKU filter
    skus.forEach(sku => {
        const option = document.createElement('option');
        option.value = sku;
        option.textContent = sku;
        skuFilter.appendChild(option);
    });
    
    // Populate Fornecedor filter with checkboxes
    fornecedorFilter.innerHTML = ''; // Clear existing content
    fornecedores.forEach(fornecedor => {
        const checkboxDiv = document.createElement('div');
        checkboxDiv.className = 'form-check';
        
        const checkbox = document.createElement('input');
        checkbox.type = 'checkbox';
        checkbox.className = 'form-check-input fornecedor-checkbox';
        checkbox.id = 'fornecedor-' + fornecedor.replace(/\s+/g, '-').toLowerCase();
        checkbox.value = fornecedor;
        
        const label = document.createElement('label');
        label.className = 'form-check-label';
        label.htmlFor = checkbox.id;
        // Use the real name instead of code
        label.textContent = fornecedor;
        
        checkboxDiv.appendChild(checkbox);
        checkboxDiv.appendChild(label);
        fornecedorFilter.appendChild(checkboxDiv);
    });
    
    // Populate Grupo filter
    grupos.forEach(grupo => {
        const option = document.createElement('option');
        option.value = grupo;
        option.textContent = grupo;
        grupoFilter.appendChild(option);
    });
    
    // Populate Produto filter
    produtos.forEach(produto => {
        const option = document.createElement('option');
        option.value = produto;
        option.textContent = produto.length > 50 ? produto.substring(0, 50) + '...' : produto;
        produtoFilter.appendChild(option);
    });
}

// Set date range
function setDateRange() {
    const dates = originalData.map(item => item['Data Doc.']);
    const minDate = new Date(Math.min.apply(null, dates));
    const maxDate = new Date(Math.max.apply(null, dates));
    
    startDateInput.value = minDate.toISOString().split('T')[0];
    endDateInput.value = maxDate.toISOString().split('T')[0];
    
    startDateInput.min = minDate.toISOString().split('T')[0];
    startDateInput.max = maxDate.toISOString().split('T')[0];
    endDateInput.min = minDate.toISOString().split('T')[0];
    endDateInput.max = maxDate.toISOString().split('T')[0];
}

// Apply filters
function applyFilters() {
    showLoading();
    
    // Get selected values
    const selectedCentros = Array.from(centroFilter.selectedOptions).map(option => option.value);
    const selectedSkus = Array.from(skuFilter.selectedOptions).map(option => option.value);
    // Get selected fornecedores from checkboxes
    const selectedFornecedores = Array.from(document.querySelectorAll('.fornecedor-checkbox:checked')).map(checkbox => checkbox.value);
    const selectedGrupos = Array.from(grupoFilter.selectedOptions).map(option => option.value);
    const selectedProdutos = Array.from(produtoFilter.selectedOptions).map(option => option.value);
    const startDate = startDateInput.value ? new Date(startDateInput.value) : null;
    const endDate = endDateInput.value ? new Date(endDateInput.value) : null;
    const onlySuspects = false; // Sempre mostrar todos os produtos, não apenas suspeitos
    
    // Filter data
    filteredData = originalData.filter(item => {
        // Filter by Centro
        if (selectedCentros.length > 0 && !selectedCentros.includes(item['Centro'])) {
            return false;
        }
        
        // Filter by SKU
        if (selectedSkus.length > 0 && !selectedSkus.includes(item['SKU'])) {
            return false;
        }
        
        // Filter by Fornecedor
        if (selectedFornecedores.length > 0 && !selectedFornecedores.includes(item['Fornecedor'])) {
            return false;
        }
        
        // Filter by Grupo
        if (selectedGrupos.length > 0 && !selectedGrupos.includes(item['Grp. Mercadoria'])) {
            return false;
        }
        
        // Filter by Produto (Descrição)
        if (selectedProdutos.length > 0 && !selectedProdutos.includes(item['Descrição'])) {
            return false;
        }
        
        // Filter by date range
        if (startDate && item['Data Doc.'] < startDate) {
            return false;
        }
        if (endDate && item['Data Doc.'] > endDate) {
            return false;
        }
        
        // Filter by suspects
        if (onlySuspects) {
            const isSuspect = suspectData.some(suspect => 
                suspect['SKU'] === item['SKU'] && suspect['Centro'] === item['Centro']
            );
            if (!isSuspect) {
                return false;
            }
        }
        
        return true;
    });
    
    // Render dashboard with filtered data
    renderDashboard();
    
    hideLoading();
}

// Clear filters
function clearFilters() {
    // Clear selections
    centroFilter.selectedIndex = -1;
    skuFilter.selectedIndex = -1;
    // Clear fornecedor checkboxes
    document.querySelectorAll('.fornecedor-checkbox').forEach(checkbox => {
        checkbox.checked = false;
    });
    grupoFilter.selectedIndex = -1;
    produtoFilter.selectedIndex = -1;
    
    // Reset date range
    setDateRange();
    
    // Reset radio button
    onlySuspectsNo.checked = true;
    
    // Reset filtered data
    filteredData = [...originalData];
    
    // Render dashboard
    renderDashboard();
}

// Render dashboard
function renderDashboard() {
    // Render overview tab
    renderCentroSpendingChart();
    renderPriceDistributionChart();
    renderPriceTimeChart();
    
    // Render suspects tab
    renderSuspectTable();
    renderComparisonChart();
    renderOutlierDetails();
    
    // Render data tab
    renderFilteredDataTable();
}

// Render Centro Spending Chart
function renderCentroSpendingChart() {
    // Group by Centro and sum Valor Liquido
    const centroSpending = {};
    filteredData.forEach(item => {
        const centro = item['Centro'];
        if (!centroSpending[centro]) {
            centroSpending[centro] = 0;
        }
        centroSpending[centro] += item['Valor Liquido'];
    });
    
    // Convert to arrays for Plotly
    const centros = Object.keys(centroSpending);
    const valores = Object.values(centroSpending);
    
    // Sort by value (descending)
    const combined = centros.map((centro, i) => ({ centro, valor: valores[i] }));
    combined.sort((a, b) => b.valor - a.valor);
    
    const sortedCentros = combined.map(item => item.centro);
    const sortedValores = combined.map(item => item.valor);
    
    // Create chart
    const data = [{
        x: sortedCentros,
        y: sortedValores,
        type: 'bar',
        marker: {
            color: sortedValores,
            colorscale: 'Viridis'
        },
        text: sortedValores.map(valor => `R$ ${valor.toFixed(2)}`),
        textposition: 'auto'
    }];
    
    const layout = {
        title: 'Gasto Total por Centro',
        xaxis: { title: 'Centro' },
        yaxis: { 
            title: 'Valor Líquido Total (R$)',
            tickformat: ',.2f'
        },
        coloraxis: { showscale: false }
    };
    
    Plotly.newPlot('centro-spending-chart', data, layout);
}

// Render Price Distribution Chart
function renderPriceDistributionChart() {
    // Group by SKU and Centro
    const groups = {};
    filteredData.forEach(item => {
        const key = `${item['SKU']}_${item['Centro']}`;
        if (!groups[key]) {
            groups[key] = {
                sku: item['SKU'],
                centro: item['Centro'],
                descricao: item['Descrição'],
                precos: [],
                count: 0
            };
        }
        groups[key].precos.push(item['Preco_Unitario']);
        groups[key].count++;
    });
    
    // Convert to array and sort by count
    const groupsArray = Object.values(groups);
    groupsArray.sort((a, b) => b.count - a.count);
    
    // Take top 10
    const top10Groups = groupsArray.slice(0, 10);
    
    // Create box plots
    const data = top10Groups.map(group => {
        const shortDesc = group.descricao.length > 20 
            ? group.descricao.substring(0, 20) + '...' 
            : group.descricao;
        
        return {
            y: group.precos,
            type: 'box',
            name: `${group.sku} (${group.centro})<br>${shortDesc}`,
            boxpoints: 'outliers'
        };
    });
    
    const layout = {
        title: 'Distribuição de Preço Unitário (Top 10 SKU/Centro por volume)',
        yaxis: { title: 'Preço Unitário (R$)' },
        showlegend: false,
        height: 500
    };
    
    Plotly.newPlot('price-distribution-chart', data, layout);
}

// Render Price Time Chart
function renderPriceTimeChart() {
    // Group by SKU, Centro and Month
    const groups = {};
    filteredData.forEach(item => {
        const key = `${item['SKU']}_${item['Centro']}`;
        if (!groups[key]) {
            groups[key] = {
                sku: item['SKU'],
                centro: item['Centro'],
                descricao: item['Descrição'],
                months: {},
                count: 0
            };
        }
        
        const month = item['Data Doc.'].toISOString().substring(0, 7); // YYYY-MM
        if (!groups[key].months[month]) {
            groups[key].months[month] = {
                sum: 0,
                count: 0
            };
        }
        
        groups[key].months[month].sum += item['Preco_Unitario'];
        groups[key].months[month].count++;
        groups[key].count++;
    });
    
    // Convert to array and sort by count
    const groupsArray = Object.values(groups);
    groupsArray.sort((a, b) => b.count - a.count);
    
    // Take top 5
    const top5Groups = groupsArray.slice(0, 5);
    
    // Create line charts
    const data = top5Groups.map(group => {
        // Calculate monthly averages
        const months = Object.keys(group.months).sort();
        const averages = months.map(month => 
            group.months[month].sum / group.months[month].count
        );
        
        const shortDesc = group.descricao.length > 15 
            ? group.descricao.substring(0, 15) + '...' 
            : group.descricao;
        
        return {
            x: months,
            y: averages,
            type: 'scatter',
            mode: 'lines+markers',
            name: `${group.sku} (${group.centro}) - ${shortDesc}`
        };
    });
    
    const layout = {
        title: 'Evolução do Preço Unitário Médio Mensal (Top 5 SKU/Centro por volume)',
        xaxis: { title: 'Mês' },
        yaxis: { title: 'Preço Unitário Médio (R$)' },
        legend: { title: { text: 'SKU (Centro)' } },
        height: 500
    };
    
    Plotly.newPlot('price-time-chart', data, layout);
}

// Render Suspect Table
function renderSuspectTable() {
    const suspectTableBody = document.querySelector('#suspect-table tbody');
    suspectTableBody.innerHTML = '';
    
    // Get unique SKU/Centro combinations in filtered data
    const filteredSkuCentros = new Set();
    filteredData.forEach(item => {
        filteredSkuCentros.add(`${item['SKU']}_${item['Centro']}`);
    });
    
    // Filter suspect data to only show those in the filtered data
    const filteredSuspects = suspectData.filter(suspect => 
        filteredSkuCentros.has(`${suspect['SKU']}_${suspect['Centro']}`)
    );
    
    if (filteredSuspects.length === 0) {
        const row = document.createElement('tr');
        const cell = document.createElement('td');
        cell.colSpan = 10;
        cell.textContent = 'Nenhum SKU/Centro suspeito encontrado com os filtros atuais.';
        cell.className = 'text-center';
        row.appendChild(cell);
        suspectTableBody.appendChild(row);
        return;
    }
    
    // Add rows to table
    filteredSuspects.forEach(suspect => {
        const row = document.createElement('tr');
        
        // Add cells
        row.innerHTML = `
            <td>${suspect['SKU']}</td>
            <td>${suspect['Centro']}</td>
            <td>${suspect['Descrição']}</td>
            <td>${suspect['Num_Compras']}</td>
            <td>R$ ${suspect['Preco_Medio'].toFixed(2)}</td>
            <td>R$ ${suspect['Preco_Min'].toFixed(2)}</td>
            <td>R$ ${suspect['Preco_Max'].toFixed(2)}</td>
            <td>${suspect['CV_Percent'].toFixed(2)}%</td>
            <td>${suspect['Num_Outliers_IQR']}</td>
            <td><strong>${suspect['Motivo_Suspeita']}</strong></td>
        `;
        
        suspectTableBody.appendChild(row);
    });
}

// Render Comparison Chart
function renderComparisonChart() {
    const data = [
        {
            x: comparisonData.map(item => `${item['SKU']} - ${item['Descrição'].substring(0, 20)}`),
            y: comparisonData.map(item => item['Preço Médio Interno (R$)']),
            type: 'bar',
            name: 'Preço Médio Interno',
            text: comparisonData.map(item => `R$ ${item['Preço Médio Interno (R$)'].toFixed(2)}`),
            textposition: 'auto'
        },
        {
            x: comparisonData.map(item => `${item['SKU']} - ${item['Descrição'].substring(0, 20)}`),
            y: comparisonData.map(item => item['Referência Externa (R$)']),
            type: 'bar',
            name: 'Referência Externa',
            text: comparisonData.map(item => `R$ ${item['Referência Externa (R$)'].toFixed(2)}`),
            textposition: 'auto'
        }
    ];
    
    const layout = {
        barmode: 'group',
        title: 'Comparação: Preço Médio Interno vs. Referência Externa',
        xaxis: { title: 'SKU - Descrição' },
        yaxis: { title: 'Preço (R$)' },
        legend: { title: { text: 'Fonte do Preço' } },
        height: 500,
        annotations: comparisonData.map((item, i) => ({
            x: `${item['SKU']} - ${item['Descrição'].substring(0, 20)}`,
            y: -30,
            xref: 'x',
            yref: 'y',
            text: `Obs: ${item['Observação']}`,
            showarrow: false,
            font: { size: 10 },
            align: 'center'
        })),
        margin: { b: 150 }
    };
    
    Plotly.newPlot('internal-external-comparison', data, layout);
}

// Render Outlier Details
function renderOutlierDetails() {
    const outlierDetailsContainer = document.getElementById('outlier-details-container');
    outlierDetailsContainer.innerHTML = '';
    
    // Get unique SKU/Centro combinations in filtered data
    const filteredSkuCentros = new Set();
    filteredData.forEach(item => {
        filteredSkuCentros.add(`${item['SKU']}_${item['Centro']}`);
    });
    
    // Filter suspect data to only show those in the filtered data
    const filteredSuspects = suspectData.filter(suspect => 
        filteredSkuCentros.has(`${suspect['SKU']}_${suspect['Centro']}`)
    );
    
    if (filteredSuspects.length === 0) {
        outlierDetailsContainer.textContent = 'Nenhum SKU/Centro suspeito encontrado com os filtros atuais.';
        return;
    }
    
    // Sort by number of outliers (descending)
    filteredSuspects.sort((a, b) => b['Num_Outliers_IQR'] - a['Num_Outliers_IQR']);
    
    // Take top 3
    const top3Suspects = filteredSuspects.slice(0, 3);
    
    // Create sections for each suspect
    top3Suspects.forEach(suspect => {
        const sku = suspect['SKU'];
        const centro = suspect['Centro'];
        
        // Get data for this SKU/Centro
        const skuData = filteredData.filter(item => 
            item['SKU'] === sku && item['Centro'] === centro
        );
        
        if (skuData.length === 0) {
            return;
        }
        
        // Calculate IQR for outlier detection
        const precos = skuData.map(item => item['Preco_Unitario']).sort((a, b) => a - b);
        const q1Index = Math.floor(precos.length * 0.25);
        const q3Index = Math.floor(precos.length * 0.75);
        const q1 = precos[q1Index];
        const q3 = precos[q3Index];
        const iqr = q3 - q1;
        const lowerBound = q1 - 1.5 * iqr;
        const upperBound = q3 + 1.5 * iqr;
        
        // Identify outliers
        const outliers = skuData.filter(item => 
            item['Preco_Unitario'] < lowerBound || item['Preco_Unitario'] > upperBound
        );
        
        if (outliers.length === 0) {
            return;
        }
        
        // Create section
        const section = document.createElement('div');
        section.className = 'mb-4';
        
        // Add heading
        const heading = document.createElement('h5');
        heading.textContent = `SKU: ${sku} | Centro: ${centro} | ${suspect['Descrição'].substring(0, 30)}...`;
        section.appendChild(heading);
        
        // Add info
        const info = document.createElement('p');
        info.textContent = `Preço Médio: R$ ${suspect['Preco_Medio'].toFixed(2)} | Outliers: ${outliers.length} de ${skuData.length} transações`;
        section.appendChild(info);
        
        // Add table
        const table = document.createElement('table');
        table.className = 'table table-striped table-hover';
        
        // Add table header
        const thead = document.createElement('thead');
        thead.innerHTML = `
            <tr>
                <th>Nº Pedido</th>
                <th>Data</th>
                <th>Fornecedor</th>
                <th>Quantidade</th>
                <th>Valor Líquido</th>
                <th>Preço Unitário</th>
            </tr>
        `;
        table.appendChild(thead);
        
        // Add table body
        const tbody = document.createElement('tbody');
        outliers.forEach(outlier => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>${outlier['Nº Pedido']}</td>
                <td>${outlier['Data Doc.'].toLocaleDateString()}</td>
                <td>${outlier['Fornecedor']}</td>
                <td>${outlier['Quantidade']}</td>
                <td>R$ ${outlier['Valor Liquido'].toFixed(2)}</td>
                <td>R$ ${outlier['Preco_Unitario'].toFixed(2)}</td>
            `;
            tbody.appendChild(row);
        });
        table.appendChild(tbody);
        
        section.appendChild(table);
        
        // Add horizontal rule
        const hr = document.createElement('hr');
        section.appendChild(hr);
        
        outlierDetailsContainer.appendChild(section);
    });
    
    if (outlierDetailsContainer.children.length === 0) {
        outlierDetailsContainer.textContent = 'Nenhum outlier encontrado nos SKUs/Centros filtrados.';
    }
}

// Render Filtered Data Table
function renderFilteredDataTable() {
    const filteredDataNote = document.getElementById('filtered-data-note');
    const filteredDataTableBody = document.querySelector('#filtered-data-table tbody');
    filteredDataTableBody.innerHTML = '';
    
    // Limit to 1000 rows for performance
    let displayData = filteredData;
    if (filteredData.length > 1000) {
        // Take a random sample
        displayData = [];
        const indices = new Set();
        while (indices.size < 1000) {
            indices.add(Math.floor(Math.random() * filteredData.length));
        }
        indices.forEach(index => {
            displayData.push(filteredData[index]);
        });
        
        filteredDataNote.textContent = 'Nota: Mostrando uma amostra aleatória de 1000 linhas para melhor performance.';
    } else {
        filteredDataNote.textContent = `Mostrando ${filteredData.length} transações.`;
    }
    
    // Add rows to table
    displayData.forEach(item => {
        const row = document.createElement('tr');
        
        // Add cells with fornecedor highlighted in bold
        row.innerHTML = `
            <td>${item['Nº Pedido']}</td>
            <td>${item['Item']}</td>
            <td><strong>${item['Data Doc.'].toLocaleDateString()}</strong></td>
            <td>${item['SKU']}</td>
            <td>${item['Descrição']}</td>
            <td>${item['UN']}</td>
            <td>${item['Centro']}</td>
            <td>${item['Quantidade']}</td>
            <td>R$ ${item['Valor Liquido'].toFixed(2)}</td>
            <td>R$ ${item['Preco_Unitario'].toFixed(2)}</td>
            <td><strong>${item['Fornecedor']}</strong></td>
            <td>${item['Codigo_Fornecedor']}</td>
        `;
        
        filteredDataTableBody.appendChild(row);
    });
}

// Export to CSV
function exportToCsv() {
    // Create CSV content
    const headers = [
        'Nº Pedido', 'Item', 'Data Doc.', 'SKU', 'Descrição', 'UN', 'Centro',
        'Quantidade', 'Valor Liquido', 'Preco_Unitario', 'Fornecedor', 'Codigo_Fornecedor'
    ];
    
    let csvContent = headers.join(',') + '\n';
    
    filteredData.forEach(item => {
        const row = [
            `"${item['Nº Pedido']}"`,
            `"${item['Item']}"`,
            `"${item['Data Doc.'].toLocaleDateString()}"`,
            `"${item['SKU']}"`,
            `"${item['Descrição'].replace(/"/g, '""')}"`,
            `"${item['UN']}"`,
            `"${item['Centro']}"`,
            item['Quantidade'],
            item['Valor Liquido'],
            item['Preco_Unitario'],
            `"${item['Fornecedor'].replace(/"/g, '""')}"`,
            `"${item['Codigo_Fornecedor']}"`
        ];
        
        csvContent += row.join(',') + '\n';
    });
    
    // Create download link
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.setAttribute('href', url);
    link.setAttribute('download', 'dados_filtrados.csv');
    link.style.visibility = 'hidden';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    
    // Show notification
    const notification = document.getElementById('export-notification');
    notification.style.display = 'block';
    setTimeout(() => {
        notification.style.display = 'none';
    }, 3000);
}

// Show loading spinner
function showLoading() {
    loadingElement.style.display = 'flex';
}

// Hide loading spinner
function hideLoading() {
    loadingElement.style.display = 'none';
}
