let currentData = [];
let sortDirection = {};

// Load data when page loads
window.onload = function() {
    fetchData();
};

function fetchData() {
    fetch('/api/data')
        .then(response => response.json())
        .then(data => {
            currentData = data;
            renderTable(data);
        })
        .catch(error => console.error('Error:', error));
}

function renderTable(data) {
    const tbody = document.getElementById('tableBody');
    tbody.innerHTML = '';
    
    data.forEach(row => {
        const tr = document.createElement('tr');
        
        const sentimentIcon = row.news_sentiment === 'favorable' 
            ? '<span class="favorable">👍 Favorable</span>' 
            : '<span class="unfavorable">👎 Unfavorable</span>';
        
        tr.innerHTML = `
            <td>${row.company}</td>
            <td><a href="https://${row.website}" target="_blank">${row.website}</a></td>
            <td class="number">${row.total_citations}</td>
            <td class="number">${row.research_reports}</td>
            <td class="number">${row.lab_reports}</td>
            <td class="number">${row.field_reports}</td>
            <td class="number">${row.testimonials}</td>
            <td class="number">${row.news_articles}</td>
            <td class="sentiment">${sentimentIcon}</td>
        `;
        
        tbody.appendChild(tr);
    });
}

function sortTable(column) {
    // Toggle sort direction
    sortDirection[column] = sortDirection[column] === 'asc' ? 'desc' : 'asc';
    
    // Sort the data
    currentData.sort((a, b) => {
        let aVal = a[column];
        let bVal = b[column];
        
        if (sortDirection[column] === 'asc') {
            return aVal > bVal ? 1 : -1;
        } else {
            return aVal < bVal ? 1 : -1;
        }
    });
    
    renderTable(currentData);
}