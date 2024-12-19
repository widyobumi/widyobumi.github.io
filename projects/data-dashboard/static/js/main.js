// Function to update the dashboard
async function updateDashboard() {
    console.log('Updating dashboard...');
    const startDate = document.getElementById('start-date').value;
    const endDate = document.getElementById('end-date').value;
    const category = document.getElementById('category').value;

    // Build query parameters
    const params = new URLSearchParams();
    if (startDate) params.append('start_date', startDate);
    if (endDate) params.append('end_date', endDate);
    if (category) params.append('category', category);

    try {
        console.log('Fetching data from /api/data...');
        const response = await fetch(`/api/data?${params.toString()}`);
        const data = await response.json();
        console.log('Received data:', data);

        if (data.error) {
            console.error('Error from server:', data.error);
            return;
        }

        // Update charts
        console.log('Updating charts...');
        if (data.charts.sales_over_time && data.charts.sales_over_time.data) {
            const lineChartLayout = {
                ...data.charts.sales_over_time.layout,
                title: 'Sales Over Time',
                xaxis: { title: 'Date' },
                yaxis: { title: 'Sales ($)' },
                height: 400,
                margin: { l: 50, r: 20, t: 40, b: 40 }
            };
            Plotly.newPlot('sales-over-time', data.charts.sales_over_time.data, lineChartLayout);
        }

        if (data.charts.sales_by_category && data.charts.sales_by_category.data) {
            const pieChartLayout = {
                ...data.charts.sales_by_category.layout,
                title: 'Sales by Category',
                height: 400,
                margin: { l: 20, r: 20, t: 40, b: 20 },
                showlegend: true,
                legend: {
                    orientation: 'h',
                    y: -0.1,
                    x: 0.5,
                    xanchor: 'center'
                }
            };
            Plotly.newPlot('sales-by-category', data.charts.sales_by_category.data, pieChartLayout);
        }

        // Update summary statistics
        console.log('Updating summary statistics...');
        if (data.summary) {
            document.getElementById('total-sales').textContent = 
                `$${data.summary.total_sales.toLocaleString('en-US', {minimumFractionDigits: 2, maximumFractionDigits: 2})}`;
            document.getElementById('avg-sales').textContent = 
                `$${data.summary.average_daily_sales.toLocaleString('en-US', {minimumFractionDigits: 2, maximumFractionDigits: 2})}`;
            document.getElementById('top-category').textContent = data.summary.top_category;
        }
    } catch (error) {
        console.error('Error updating dashboard:', error);
    }
}

// Function to handle window resize
function handleResize() {
    const width = window.innerWidth;
    Plotly.relayout('sales-over-time', {
        'width': document.getElementById('sales-over-time').offsetWidth
    });
    Plotly.relayout('sales-by-category', {
        'width': document.getElementById('sales-by-category').offsetWidth
    });
}

// Function to handle file upload
async function uploadFile() {
    console.log('Starting file upload...');
    const fileInput = document.getElementById('csv-file');
    const file = fileInput.files[0];

    if (!file) {
        alert('Please select a file to upload');
        return;
    }

    const formData = new FormData();
    formData.append('file', file);

    try {
        console.log('Uploading file...');
        const response = await fetch('/upload', {
            method: 'POST',
            body: formData
        });

        const result = await response.json();

        if (response.ok) {
            alert('File uploaded successfully');
            updateDashboard();
        } else {
            alert(result.error || 'Error uploading file');
        }
    } catch (error) {
        console.error('Error uploading file:', error);
        alert('Error uploading file. Please try again.');
    }
}

// Initialize dashboard on page load
document.addEventListener('DOMContentLoaded', () => {
    console.log('Page loaded, initializing dashboard...');
    updateDashboard();
    
    // Add resize handler
    window.addEventListener('resize', handleResize);
});
